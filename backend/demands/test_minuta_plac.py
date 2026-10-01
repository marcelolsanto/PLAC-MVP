"""
Testes unitários para as regras, fórmulas e tabelas da Minuta da Diretriz do PLAC v2
(services_minuta_plac.py)
"""

from datetime import date
from django.test import TestCase
from demands.services_minuta_plac import (
    calcular_prioridade_minuta,
    calcular_calendario_anexo_iii,
    calcular_indicadores_anexo_iv,
    subtrair_dias_uteis,
    somar_dias_uteis,
    PRAZOS_ANEXO_III,
)


class MinutaPlacServicesTestCase(TestCase):

    def test_dias_uteis_subtracao_e_soma(self):
        # Sexta-feira: 2026-10-02
        sexta = date(2026, 10, 2)
        # Subtrair 1 dia útil -> Quinta (2026-10-01)
        self.assertEqual(subtrair_dias_uteis(sexta, 1), date(2026, 10, 1))
        # Segunda-feira: 2026-10-05
        segunda = date(2026, 10, 5)
        # Subtrair 1 dia útil da segunda -> Sexta anterior (2026-10-02)
        self.assertEqual(subtrair_dias_uteis(segunda, 1), date(2026, 10, 2))
        # Somar 1 dia útil da sexta -> Segunda-feira (2026-10-05)
        self.assertEqual(somar_dias_uteis(sexta, 1), date(2026, 10, 5))

    def test_anexo_ii_pontuacao_e_grau(self):
        # Caso 1: Todos 5 -> 5*30 + 5*30 + 5*25 + 5*15 = 150 + 150 + 125 + 75 = 500 (ALTO, 1Q)
        res = calcular_prioridade_minuta(5, 5, 5, 5)
        self.assertEqual(res["pontuacao"], 500)
        self.assertEqual(res["grau_prioridade"], "ALTO")
        self.assertEqual(res["quadrimestre_id"], "1Q")

        # Caso 2: Todos 1 -> 1*30 + 1*30 + 1*25 + 1*15 = 100 (BAIXO, 3Q)
        res_baixo = calcular_prioridade_minuta(1, 1, 1, 1)
        self.assertEqual(res_baixo["pontuacao"], 100)
        self.assertEqual(res_baixo["grau_prioridade"], "BAIXO")
        self.assertEqual(res_baixo["quadrimestre_id"], "3Q")

        # Caso 3: Todos 3 -> 3*30 + 3*30 + 3*25 + 3*15 = 90 + 90 + 75 + 45 = 300 (MEDIO, 2Q)
        res_medio = calcular_prioridade_minuta(3, 3, 3, 3)
        self.assertEqual(res_medio["pontuacao"], 300)
        self.assertEqual(res_medio["grau_prioridade"], "MEDIO")
        self.assertEqual(res_medio["quadrimestre_id"], "2Q")

    def test_anexo_ii_enquadramento_obrigatorio_e_vedacao(self):
        # Item 6: F2=5 (contrato expira no exercício sem prorrogação) -> Obrigatoriamente ALTO
        res_expira = calcular_prioridade_minuta(1, 5, 1, 1)
        self.assertEqual(res_expira["grau_prioridade"], "ALTO")
        self.assertTrue(res_expira["enquadramento_obrigatorio"])

        # Item 6: F3=5 (obrigação legal com prazo fatal) -> Obrigatoriamente ALTO
        res_legal = calcular_prioridade_minuta(1, 1, 5, 1)
        self.assertEqual(res_legal["grau_prioridade"], "ALTO")
        self.assertTrue(res_legal["enquadramento_obrigatorio"])

        # Item 7: Vedação de BAIXO para substituição de contrato que expira
        res_vedado = calcular_prioridade_minuta(1, 1, 1, 1, substitui_contrato_expirando=True)
        self.assertNotEqual(res_vedado["grau_prioridade"], "BAIXO")
        self.assertEqual(res_vedado["grau_prioridade"], "MEDIO")

    def test_anexo_iii_calculo_calendario(self):
        # Assinatura pretendida em 15/12/2026 para Pregão Eletrônico (140 dias úteis até assinatura)
        data_pretendida = date(2026, 12, 15)
        res_pregao = calcular_calendario_anexo_iii(data_pretendida, "PREGAO_ELETRONICO")
        self.assertEqual(res_pregao["dias_uteis_ate_assinatura"], 140)
        self.assertFalse(res_pregao["alerta_antecipacao"])

        # Assinatura pretendida em 10/02/2027 para Pregão Eletrônico: 140 dias úteis recai em 2026!
        data_inicio_2027 = date(2027, 2, 10)
        res_antecipado = calcular_calendario_anexo_iii(data_inicio_2027, "PREGAO_ELETRONICO")
        self.assertTrue(res_antecipado["alerta_antecipacao"])
        self.assertLess(res_antecipado["ano_envio_gcc"], 2027)

    def test_anexo_iv_indicadores_desempenho(self):
        res = calcular_indicadores_anexo_iv(
            contratacoes_planejadas=100,
            contratacoes_concluidas=88,
            processos_encaminhados_no_prazo=92,
            processos_encaminhados_total=100,
            itens_incluidos_no_curso=8,
            total_itens_plac_vigente=108,
            alteracoes_aprovadas=15,
            soma_dias_uteis_reais=1200,
            concluidas_com_tempo=10,
            processos_devolvidos_incompletude=5,
            soma_dias_saneamento=40,
        )

        # TEP: 88% -> Adequado
        self.assertEqual(res["tep"]["valor"], 88.0)
        self.assertEqual(res["tep"]["status"], "Adequado")

        # IAC: 92% -> Adequado
        self.assertEqual(res["iac"]["valor"], 92.0)
        self.assertEqual(res["iac"]["status"], "Adequado")

        # ICNP: 8/108 = 7.4% -> Adequado (<= 10%)
        self.assertEqual(res["icnp"]["valor"], 7.4)
        self.assertEqual(res["icnp"]["status"], "Adequado")

        # IAP: 15/108 = 13.9% -> Adequado (<= 25%)
        self.assertEqual(res["iap"]["valor"], 13.9)
        self.assertEqual(res["iap"]["status"], "Adequado")

        # TMP: 1200 / 10 = 120 dias úteis
        self.assertEqual(res["tmp"]["valor_dias_uteis"], 120.0)

    def test_api_indicadores_minuta_view(self):
        from rest_framework.test import APIRequestFactory
        from demands.views import IndicadoresMinutaPlacView
        factory = APIRequestFactory()
        view = IndicadoresMinutaPlacView.as_view()
        request = factory.get('/api/planejamento/indicadores-minuta/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("tep", response.data)
        self.assertIn("iac", response.data)
        self.assertIn("icnp", response.data)
        self.assertIn("iap", response.data)
        self.assertIn("tmp", response.data)
        self.assertIn("marcos_regimentais", response.data)

    def test_api_calcular_prioridade_minuta_view(self):
        from rest_framework.test import APIRequestFactory
        from demands.views import CalcularPrioridadeMinutaView
        factory = APIRequestFactory()
        view = CalcularPrioridadeMinutaView.as_view()
        payload = {
            "f1": 5, "f2": 5, "f3": 5, "f4": 5,
            "tipo_contratacao": "PREGAO_ELETRONICO",
            "data_pretendida_assinatura": "2026-11-30"
        }
        request = factory.post('/api/planejamento/calcular-prioridade-minuta/', payload, format='json')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["prioridade"]["pontuacao"], 500)
        self.assertEqual(response.data["prioridade"]["grau_prioridade"], "ALTO")
        self.assertIsNotNone(response.data["calendario"])
        self.assertEqual(response.data["calendario"]["dias_uteis_ate_assinatura"], 140)

    def test_api_prazos_anexo_iii_view(self):
        from rest_framework.test import APIRequestFactory
        from demands.views import PrazosAnexoIIIView
        factory = APIRequestFactory()
        view = PrazosAnexoIIIView.as_view()
        request = factory.get('/api/planejamento/prazos-anexo-iii/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 10)

    def test_api_pncp_precos_consulta_view(self):
        from rest_framework.test import APIRequestFactory
        from demands.views import PNCPPrecosConsultaView
        factory = APIRequestFactory()
        view = PNCPPrecosConsultaView.as_view()
        request = factory.get('/api/planejamento/pncp-precos/?termo=DWDM')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("estatisticas", response.data)
        self.assertIn("amostras_mercado", response.data)
        self.assertGreater(len(response.data["amostras_mercado"]), 0)

