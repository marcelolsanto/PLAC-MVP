import json
from datetime import date, timedelta
from django.test import TestCase
from rest_framework.test import APIClient

from demands.services_capacidade import (
    eh_dia_util,
    subtrair_dias_uteis,
    somar_dias_uteis,
    calcular_cronograma_reverso,
    verificar_capacidade_gcc,
    obter_janelas_cabiveis,
    determinar_quadrimestre,
    identificar_config_modalidade
)

class TestGestaoCapacidadeService(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_dias_uteis_e_feriados(self):
        # 01/01/2026 é Confraternização Universal (quinta-feira) -> não deve ser dia útil
        d_feriado = date(2026, 1, 1)
        self.assertFalse(eh_dia_util(d_feriado))
        
        # Sábado e Domingo não são dias úteis
        d_sabado = date(2026, 1, 3)
        d_domingo = date(2026, 1, 4)
        self.assertFalse(eh_dia_util(d_sabado))
        self.assertFalse(eh_dia_util(d_domingo))
        
        # 05/01/2026 é segunda-feira regular -> dia útil
        d_segunda = date(2026, 1, 5)
        self.assertTrue(eh_dia_util(d_segunda))

    def test_subtrair_e_somar_dias_uteis(self):
        # 09/01/2026 (sexta-feira). Subtraindo 5 dias úteis deve voltar para 02/01/2026 (pulando 01/01 feriado)
        ref = date(2026, 1, 9)
        resultado_sub = subtrair_dias_uteis(ref, 5)
        self.assertTrue(eh_dia_util(resultado_sub))
        self.assertLess(resultado_sub, ref)

        # Somando 5 dias úteis a partir de 02/01 deve retornar 09/01
        resultado_soma = somar_dias_uteis(resultado_sub, 5)
        self.assertEqual(resultado_soma, ref)

    def test_cronograma_reverso_pregao_viavel(self):
        hoje = date(2026, 1, 10)
        # Data pretendida de assinatura 10 meses à frente (viável)
        data_assinatura = date(2026, 11, 20)
        
        cronograma = calcular_cronograma_reverso(
            modalidade="PREGAO",
            data_pretendida_assinatura=data_assinatura,
            data_hoje=hoje
        )
        
        self.assertEqual(cronograma['modalidade_codigo'], 'PREGAO')
        self.assertEqual(cronograma['sla_regimental_gcc_dias_uteis'], 31)
        self.assertEqual(cronograma['prazo_planilha_antigo_gcc'], 144)
        self.assertEqual(cronograma['responsaveis_gcc'], 'Marcus / Layllah')
        self.assertEqual(cronograma['grau_confianca_pct'], 99.0)
        self.assertLessEqual(cronograma['margem_erro_pct'], 2.0)
        self.assertIn('cenarios', cronograma)
        self.assertIn('previsao_entrega_local', cronograma)
        self.assertFalse(cronograma['eh_retroativo'])
        self.assertEqual(cronograma['cor_semaforo'], 'VERDE')
        self.assertEqual(cronograma['status_viabilidade'], 'VIÁVEL')
        self.assertEqual(cronograma['quadrimestre_alvo'], 'Q3/2026')

    def test_cronograma_reverso_urgencia_retroativa(self):
        hoje = date(2026, 5, 1)
        # Data pretendida de assinatura em apenas 15 dias para um pregão de 144 dias!
        data_assinatura = date(2026, 5, 16)
        
        cronograma = calcular_cronograma_reverso(
            modalidade="PREGAO",
            data_pretendida_assinatura=data_assinatura,
            data_hoje=hoje
        )
        
        self.assertTrue(cronograma['eh_retroativo'])
        self.assertEqual(cronograma['cor_semaforo'], 'VERMELHO')
        self.assertEqual(cronograma['status_viabilidade'], 'INVIÁVEL')
        self.assertIn('URGÊNCIA FABRICADA', cronograma['classificacao_risco'])
        self.assertGreater(cronograma['dias_em_atraso'], 0)

    def test_determinar_quadrimestre(self):
        q1 = determinar_quadrimestre(date(2026, 3, 15))
        self.assertEqual(q1['quadrimestre_codigo'], 'Q1/2026')
        self.assertEqual(q1['quadrimestre_numero'], 1)

        q2 = determinar_quadrimestre(date(2026, 7, 20))
        self.assertEqual(q2['quadrimestre_codigo'], 'Q2/2026')
        self.assertEqual(q2['quadrimestre_numero'], 2)

        q3 = determinar_quadrimestre(date(2026, 11, 10))
        self.assertEqual(q3['quadrimestre_codigo'], 'Q3/2026')
        self.assertEqual(q3['quadrimestre_numero'], 3)

    def test_janelas_cabiveis_sugestoes(self):
        hoje = date(2026, 2, 1)
        sugestoes = obter_janelas_cabiveis(modalidade="PREGAO", quantidade_sugestoes=3, data_base=hoje)
        
        self.assertEqual(len(sugestoes), 3)
        for s in sugestoes:
            self.assertIn('data_sugerida_assinatura', s)
            self.assertIn('data_fatal_abertura_siga', s)
            self.assertIn('quadrimestre', s)
            # A data de abertura deve ser no futuro em relação à data base
            d_siga = date.fromisoformat(s['data_fatal_abertura_siga'])
            self.assertGreaterEqual(d_siga, hoje)

    def test_api_verificar_capacidade(self):
        resp = self.client.get('/api/planejamento/verificar-capacidade/?data=2026-08-15&modalidade=PREGAO')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('status_capacidade', data)
        self.assertIn('vagas_restantes', data)
        self.assertIn('quadrimestre', data)

    def test_api_cronograma_reverso(self):
        payload = {
            "modalidade": "PREGAO",
            "data_pretendida_assinatura": "2026-11-30"
        }
        resp = self.client.post('/api/planejamento/cronograma-reverso/', data=payload, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['modalidade_codigo'], 'PREGAO')
        self.assertIn('data_fatal_abertura_siga', data)
        self.assertIn('status_viabilidade', data)

    def test_api_janelas_cabiveis(self):
        resp = self.client.get('/api/planejamento/janelas-cabiveis/?modalidade=PREGAO&quantidade=3')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['janelas_cabiveis']), 3)
