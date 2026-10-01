import io
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from demands.models import Demand
from demands.services_monitor import (
    calcular_kpis_governanca_plac,
    calcular_ranking_areas_demandantes,
    executar_varredura_sentinela
)

User = get_user_model()


class SentinelaMonitorTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='auditor_telebras',
            password='password123',
            email='auditoria@telebras.com.br'
        )
        self.client.force_authenticate(user=self.user)

        # 1. Demanda Regular e Aderente
        self.d1 = Demand.objects.create(
            directorate='Diretoria Técnica e Operacional - DTO',
            management_unit='GTI - Tecnologia',
            responsible_name='Lucas Silva',
            description='Serviço de Nuvem Soberana',
            item_type='TI',
            catmat_code='CATSER-1001',
            quantity=1,
            estimated_value=200000.00,
            intended_date=date.today() + timedelta(days=200),
            f1=3, f2=3, f3=3, f4=3,
            status='CONTRATADO',
            siga_process_number='TLB-PRO-2026/00101',
            needs_anticipation=False,
            is_extraordinary=False,
            created_by=self.user
        )

        # 2. Demanda com Urgência Fabricada / Fora do Rito
        self.d2 = Demand.objects.create(
            directorate='Diretoria de Administração - DAFRI',
            management_unit='GLOG - Logística',
            responsible_name='Marcos Souza',
            description='Aquisição Emergencial de Nobreaks',
            item_type='BEM',
            catmat_code='CATMAT-2002',
            quantity=5,
            estimated_value=150000.00,
            intended_date=date.today() + timedelta(days=20),
            f1=5, f2=5, f3=5, f4=5,
            status='AGUARDANDO_VALIDACAO',
            siga_process_number=None,
            needs_anticipation=True,
            is_extraordinary=True,
            created_by=self.user
        )

    def test_calcular_kpis_governanca_plac(self):
        """Validação das fórmulas de IAC, ICNP, TEP e decomposição do TMP."""
        kpis = calcular_kpis_governanca_plac()
        self.assertEqual(kpis['total_demandas'], 2)
        
        # IAC: 1 aderente de 2 = 50.0% (Abaixo da meta de 85% -> DESVIO)
        self.assertEqual(kpis['iac']['valor'], 50.0)
        self.assertEqual(kpis['iac']['status'], 'DESVIO')

        # ICNP: 1 extraordinária de 2 = 50.0% (Acima da meta de 10% -> CRITICO)
        self.assertEqual(kpis['icnp']['valor'], 50.0)
        self.assertEqual(kpis['icnp']['status'], 'CRITICO')

        # TEP: 1 contratada de 2 = 50.0%
        self.assertEqual(kpis['tep']['valor'], 50.0)
        self.assertEqual(kpis['tep']['contratadas'], 1)

        # TMP: Decomposição analítica
        self.assertIn('dias_area_demandante', kpis['tmp'])
        self.assertIn('dias_gcc_compras', kpis['tmp'])
        self.assertIn('pct_tempo_area', kpis['tmp'])
        self.assertIn('pct_tempo_gcc', kpis['tmp'])

    def test_calcular_ranking_areas_demandantes(self):
        """Áreas com alta aderência ao SIGA e sem urgências fabricadas devem liderar o ranking."""
        ranking = calcular_ranking_areas_demandantes()
        self.assertEqual(len(ranking), 2)

        # O primeiro deve ser a DTO (com processo SIGA e sem urgência)
        top_area = ranking[0]
        self.assertIn('DTO', top_area['diretoria'])
        self.assertEqual(top_area['score_governanca'], 100)
        self.assertEqual(top_area['classificacao'], 'EXEMPLAR')

        # O segundo deve ser a DAFRI (sem processo SIGA e com urgência)
        bottom_area = ranking[1]
        self.assertIn('DAFRI', bottom_area['diretoria'])
        self.assertLess(bottom_area['score_governanca'], 60)
        self.assertEqual(bottom_area['classificacao'], 'CRITICO')

    def test_executar_varredura_sentinela(self):
        """A varredura autônoma deve identificar demandas em atraso fatal e incompatibilidade de SLA."""
        varredura = executar_varredura_sentinela()
        self.assertIn('alertas', varredura)
        self.assertIn('resumo_alertas', varredura)
        self.assertGreaterEqual(len(varredura['alertas']), 1)

        # Encontra alerta crítico ou de SLA na demanda d2
        alertas_d2 = [a for a in varredura['alertas'] if a['demand_id'] == self.d2.id]
        self.assertTrue(len(alertas_d2) > 0)
        self.assertIn(alertas_d2[0]['severidade'], ['CRITICO', 'ALERTA'])

    def test_endpoints_sentinela(self):
        """Endpoints REST expostos devem responder com HTTP 200 e payloads estruturados."""
        # 1. KPIs
        res_kpis = self.client.get('/api/planejamento/sentinela/kpis/')
        self.assertEqual(res_kpis.status_code, status.HTTP_200_OK)
        self.assertIn('iac', res_kpis.data)
        self.assertIn('icnp', res_kpis.data)
        self.assertIn('tep', res_kpis.data)
        self.assertIn('tmp', res_kpis.data)

        # 2. Ranking de Áreas
        res_rank = self.client.get('/api/planejamento/sentinela/ranking-areas/')
        self.assertEqual(res_rank.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res_rank.data, list)
        self.assertEqual(len(res_rank.data), 2)

        # 3. Varredura
        res_var = self.client.get('/api/planejamento/sentinela/varredura/')
        self.assertEqual(res_var.status_code, status.HTTP_200_OK)
        self.assertIn('alertas', res_var.data)
