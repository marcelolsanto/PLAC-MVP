import io
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from demands.models import Demand
from demands.services_governanca import obter_resumo_esteira, gerar_minuta_consolidada_pdf

User = get_user_model()


class GovernancaEsteiraTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='diretor_dto',
            password='password123',
            email='diretor.dto@telebras.com.br'
        )
        self.client.force_authenticate(user=self.user)

        self.demand = Demand.objects.create(
            directorate='Diretoria Técnica e Operacional - DTO',
            management_unit='GTI - Gerência de Tecnologia da Informação',
            responsible_name='Carlos Ferreira',
            responsible_email='carlos.ferreira@telebras.com.br',
            description='Aquisição de Switches de Borda 10Gbps para Estações de Telecomunicações',
            item_type='TI',
            catmat_code='CATMAT-89421',
            quantity=10,
            unit='UN',
            strategic_alignment='Objetivo 3 - Conectividade Nacional e Expansão SGDC',
            estimated_value=350000.00,
            intended_date=date(2026, 8, 20),  # Q2
            f1=5,
            f2=5,
            f3=3,
            f4=3,
            status='AGUARDANDO_VALIDACAO',
            created_by=self.user
        )

    def test_auto_atribuicao_quadrimestre(self):
        """Demanda com intended_date em agosto deve ser automaticamente atribuída ao Q2."""
        self.assertEqual(self.demand.quadrimestre_alvo, 'Q2')
        self.assertTrue(self.demand.codigo_rastreio_plac.startswith('PLAC2026-DTO'))

    def test_aprovacao_diretor_bloqueada_sem_processo_siga(self):
        """O Diretor NÃO pode aprovar demanda que não tenha o número do processo SIGA autuado."""
        self.assertFalse(self.demand.siga_process_number)
        url = f'/api/demands/{self.demand.id}/approve/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data.get('bloqueio_siga'))
        self.assertIn('Aprovação bloqueada', response.data.get('error', ''))
        
        # O status permanece inalterado
        self.demand.refresh_from_db()
        self.assertEqual(self.demand.status, 'AGUARDANDO_VALIDACAO')

    def test_aprovacao_diretor_sucesso_com_processo_siga(self):
        """Com o processo SIGA vinculado, o Diretor aprova e a demanda avança para VALIDADO_DIRETOR."""
        self.demand.siga_process_number = 'TLB-PRO-2026/00142'
        self.demand.save()

        url = f'/api/demands/{self.demand.id}/approve/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.demand.refresh_from_db()
        self.assertEqual(self.demand.status, 'VALIDADO_DIRETOR')

    def test_avancar_fase_governance_gate(self):
        """Action avancar_fase respeita a trava de processo SIGA e avança as etapas sequenciais."""
        url = f'/api/demands/{self.demand.id}/avancar_fase/'
        
        # Sem SIGA -> Bloqueado
        res_bloq = self.client.post(url)
        self.assertEqual(res_bloq.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(res_bloq.data.get('bloqueio_siga'))

        # Com SIGA -> Avança
        self.demand.siga_process_number = 'TLB-PRO-2026/00999'
        self.demand.save()

        # 1. Levantamento -> Validação do Diretor
        res1 = self.client.post(url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.demand.refresh_from_db()
        self.assertEqual(self.demand.status, 'VALIDADO_DIRETOR')

        # 2. Validação do Diretor -> Consolidação GCC
        res2 = self.client.post(url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.demand.refresh_from_db()
        self.assertEqual(self.demand.status, 'CONSOLIDADO')

        # 3. Consolidação GCC -> Deliberação REDIR
        res3 = self.client.post(url)
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.demand.refresh_from_db()
        self.assertEqual(self.demand.status, 'DELIBERACAO_REDIR')

    def test_retroceder_fase_com_motivo(self):
        """A demanda pode retroceder de fase registrando o motivo de rejeição/ajuste."""
        self.demand.status = 'VALIDADO_DIRETOR'
        self.demand.siga_process_number = 'TLB-PRO-2026/00142'
        self.demand.save()

        url = f'/api/demands/{self.demand.id}/retroceder_fase/'
        response = self.client.post(url, {
            'motivo': 'Necessário complementar termo de justificativa do quantitativo.'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.demand.refresh_from_db()
        self.assertEqual(self.demand.status, 'AGUARDANDO_VALIDACAO')
        self.assertIn('justificativa', self.demand.rejection_reason)

    def test_esteira_kanban_endpoint_e_filtro_quadrimestre(self):
        """Endpoint esteira_kanban agrupa demandas por fases e filtra por quadrimestre."""
        # Criar uma segunda demanda no Q1
        Demand.objects.create(
            directorate='DAFRI',
            description='Serviço de Auditoria Contábil Independente',
            item_type='SERVICO',
            catmat_code='CATSER-1234',
            quantity=1,
            estimated_value=120000.00,
            intended_date=date(2026, 3, 15),  # Q1
            f1=3, f2=3, f3=5, f4=3,
            status='CONSOLIDADO',
            created_by=self.user
        )

        # Filtro Q2
        res_q2 = self.client.get('/api/demands/esteira_kanban/?quadrimestre=Q2')
        self.assertEqual(res_q2.status_code, status.HTTP_200_OK)
        data_q2 = res_q2.data
        self.assertIn('resumo', data_q2)
        self.assertIn('colunas', data_q2)
        self.assertEqual(data_q2['resumo']['quadrimestre'], 'Q2')
        self.assertEqual(len(data_q2['colunas']['levantamento']), 1)
        self.assertEqual(len(data_q2['colunas']['consolidacao_gcc']), 0)

        # Filtro Q1
        res_q1 = self.client.get('/api/demands/esteira_kanban/?quadrimestre=Q1')
        self.assertEqual(res_q1.status_code, status.HTTP_200_OK)
        data_q1 = res_q1.data
        self.assertEqual(len(data_q1['colunas']['consolidacao_gcc']), 1)
        self.assertEqual(len(data_q1['colunas']['levantamento']), 0)

    def test_gerar_minuta_consolidada_pdf(self):
        """A geração da minuta consolidada em PDF via ReportLab deve produzir bytes válidos de PDF."""
        pdf_bytes = gerar_minuta_consolidada_pdf(quadrimestre='Q2', ano=2026)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))
        self.assertGreater(len(pdf_bytes), 1500)

    def test_minuta_consolidada_pdf_endpoint(self):
        """Endpoint de download da Minuta Consolidada retorna status 200 e tipo application/pdf."""
        res = self.client.get('/api/planejamento/minuta-consolidada-pdf/?quadrimestre=Q2&ano=2026')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertTrue(res.content.startswith(b'%PDF-'))
