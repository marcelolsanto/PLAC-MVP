from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from demands.services_stats import (
    PREGOES_AMOSTRAS_DIAS_UTEIS,
    DISPENSAS_AMOSTRAS_DIAS_UTEIS,
    calcular_metricas_amostrais,
    calcular_modelo_pert,
    obter_diagnostico_completo_fluxos,
    prever_tempo_restante_processo,
    adicionar_dias_uteis
)

class TestInferenciaEstatisticaService(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_calcular_metricas_amostrais_pregao(self):
        stats = calcular_metricas_amostrais(PREGOES_AMOSTRAS_DIAS_UTEIS)
        self.assertEqual(stats["tamanho_amostra_n"], 61)
        self.assertAlmostEqual(stats["media_dias_uteis"], 31.13, places=1)
        self.assertAlmostEqual(stats["mediana_dias"], 28.0, places=1)
        self.assertGreater(stats["desvio_padrao_dias"], 10.0)
        self.assertIn("ic_95", stats)
        self.assertLess(stats["ic_95"]["limite_inferior"], stats["media_dias_uteis"])
        self.assertGreater(stats["ic_95"]["limite_superior"], stats["media_dias_uteis"])

    def test_calcular_metricas_amostrais_dispensa(self):
        stats = calcular_metricas_amostrais(DISPENSAS_AMOSTRAS_DIAS_UTEIS)
        self.assertEqual(stats["tamanho_amostra_n"], 28)
        self.assertAlmostEqual(stats["media_dias_uteis"], 15.96, places=1)
        self.assertAlmostEqual(stats["mediana_dias"], 13.5, places=1)

    def test_modelo_pert(self):
        pert = calcular_modelo_pert(otimista=18, mais_provavel=27, pessimista=60)
        # mu = (18 + 4*27 + 60)/6 = 186/6 = 31.0
        self.assertEqual(pert["duracao_esperada_pert_mu"], 31.0)
        # sigma = (60 - 18)/6 = 42/6 = 7.0
        self.assertEqual(pert["desvio_padrao_pert_sigma"], 7.0)
        # Percentis: P50 < P80 < P95
        p50 = pert["percentis"]["p50_certeza_50pct"]
        p80 = pert["percentis"]["p80_certeza_80pct"]
        p95 = pert["percentis"]["p95_certeza_95pct"]
        self.assertTrue(p50 < p80 < p95)
        self.assertEqual(p50, 31.0)

    def test_obter_diagnostico_completo_fluxos(self):
        diag = obter_diagnostico_completo_fluxos()
        self.assertEqual(diag["status"], "sucesso")
        self.assertIn("pregao_eletronico", diag)
        self.assertIn("dispensa_licitacao", diag)
        self.assertEqual(diag["pregao_eletronico"]["prazo_teorico_planilha_gcc"], 144)
        self.assertEqual(diag["dispensa_licitacao"]["prazo_teorico_planilha_gcc"], 117)
        self.assertIn("calibracao_gcc", diag["pregao_eletronico"])

    def test_prever_tempo_restante_processo(self):
        # Pregão na etapa 18 de 36 (50% concluído conforme planilha oficial da GCC)
        previsao = prever_tempo_restante_processo(tipo_processo="pregao", etapa_atual=18, nivel_confianca=80)
        self.assertIn("PREG", previsao["tipo_processo"].upper())
        self.assertEqual(previsao["total_etapas"], 36)
        self.assertEqual(previsao["progresso_pct"], 50.0)
        self.assertIn("data_projetada_conclusao_pert", previsao)
        self.assertIn("ganho_eficiencia_dias_uteis", previsao)

        # Inexigibilidade de Cursos (15 etapas - fluxo ágil)
        prev_curso = prever_tempo_restante_processo(tipo_processo="INEXIGIBILIDADE_CURSOS", etapa_atual=5, nivel_confianca=80)
        self.assertEqual(prev_curso["total_etapas"], 15)
        self.assertLess(prev_curso["duracao_total_modelo_pert_dias"], 25)

    def test_adicionar_dias_uteis(self):
        # Segunda-feira: 2026-09-28 -> somar 5 dias úteis deve dar a próxima segunda 2026-10-05
        d_segunda = date(2026, 9, 28) # 2026-09-28 é segunda
        d_result = adicionar_dias_uteis(d_segunda, 5)
        self.assertEqual(d_result, date(2026, 10, 5))

    def test_api_inferencia_fluxos(self):
        resp = self.client.get('/api/estatisticas/inferencia-fluxos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertIn("pregao_eletronico", data)
        self.assertIn("dispensa_licitacao", data)
        self.assertEqual(data["pregao_eletronico"]["estatistica_amostral"]["tamanho_amostra_n"], 61)

    def test_api_previsao_processo(self):
        resp = self.client.get('/api/estatisticas/previsao/?tipo=pregao&etapa=10&confianca=95')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIn("PREG", data["tipo_processo"].upper())
        self.assertEqual(data["etapa_atual"], 10)
        self.assertEqual(data["nivel_confianca_escolhido"], 95)
        self.assertIn("dias_uteis_restantes_pert", data)

    def test_api_catalogo_fluxos_gcc(self):
        resp = self.client.get('/api/contratos/catalogo-fluxos-gcc/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertEqual(data["total_modalidades"], 10)


