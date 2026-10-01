import math
from django.test import TestCase
from demands.services_stats import (
    calcular_estatisticas_modalidade_99,
    MODALIDADES_GCC_CONFIG
)

class TestEstatisticas99Service(TestCase):
    def test_estatisticas_pregao_99(self):
        stats = calcular_estatisticas_modalidade_99("PREGAO")
        self.assertEqual(stats["modalidade_codigo"], "PREGAO")
        self.assertEqual(stats["grau_confianca_pct"], 99.0)
        self.assertEqual(stats["z_score"], 2.576)
        # Margem de erro deve ser rigorosamente <= 2.0%
        self.assertLessEqual(stats["margem_erro_pct"], 2.0)
        # Duração estatística realista (média empírica ~ 31 dias úteis)
        self.assertEqual(stats["media_dias_uteis_arredondada"], 31)
        self.assertLess(stats["media_dias_uteis_arredondada"], stats["prazo_planilha_antigo_gcc"])
        # Cenários presentes
        self.assertIn("otimista", stats["cenarios"])
        self.assertIn("esperado", stats["cenarios"])
        self.assertIn("pessimista", stats["cenarios"])
        self.assertEqual(stats["cenarios"]["otimista"]["dias_tramitacao_gcc"], 18)
        self.assertEqual(stats["cenarios"]["esperado"]["dias_tramitacao_gcc"], 31)
        self.assertGreater(stats["cenarios"]["pessimista"]["dias_tramitacao_gcc"], 31)
        # Testar arredondamento math.ceil para cursos (8.5 -> 9 dias) e dispensa tradicional (14.33 -> 15 dias)
        stats_cursos = calcular_estatisticas_modalidade_99("INEXIGIBILIDADE_CURSOS")
        self.assertEqual(stats_cursos["media_dias_uteis_arredondada"], 9)
        stats_disp = calcular_estatisticas_modalidade_99("DISPENSA_TRADICIONAL")
        self.assertEqual(stats_disp["media_dias_uteis_arredondada"], 15)
        # Previsão de entrega no local
        prev = stats["previsao_entrega_local"]
        self.assertIn("lead_time_total_dias_uteis", prev)
        self.assertIn("data_projetada_formatada", prev)
        self.assertIn("diagnostico_comparativo", prev)

    def test_todas_as_10_modalidades_calibradas_99(self):
        for mod_key in MODALIDADES_GCC_CONFIG.keys():
            stats = calcular_estatisticas_modalidade_99(mod_key)
            self.assertEqual(stats["grau_confianca_pct"], 99.0, f"Falha na modalidade {mod_key}")
            self.assertEqual(stats["z_score"], 2.576, f"Falha na modalidade {mod_key}")
            self.assertLessEqual(stats["margem_erro_pct"], 2.0, f"Margem de erro > 2% na modalidade {mod_key}")
            self.assertGreater(stats["media_dias_uteis_arredondada"], 0)
            self.assertLess(stats["media_dias_uteis_arredondada"], stats["prazo_planilha_antigo_gcc"], f"Não houve ganho em {mod_key}")
            self.assertGreater(stats["previsao_entrega_local"]["lead_time_total_dias_uteis"], 0)
