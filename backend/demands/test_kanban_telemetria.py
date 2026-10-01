import os
import sys
import unittest
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from demands.services_kanban_planejamento import obter_dados_kanban_planejamento
from demands.views import PlanejamentoKanbanTelemetriaView

class KanbanPlanejamentoTests(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PlanejamentoKanbanTelemetriaView.as_view()

    def test_servico_kanban_retorna_estrutura_correta(self):
        dados = obter_dados_kanban_planejamento(ano=2026)
        self.assertIn("kpis", dados)
        self.assertIn("colunas_config", dados)
        self.assertIn("colunas", dados)
        
        # Verificar KPIs
        kpis = dados["kpis"]
        self.assertGreater(kpis["total_processos"], 150)
        self.assertGreater(kpis["valor_total_rs"], 200000000)
        self.assertIn("gargalos_criticos", kpis)
        self.assertIn("risco_apagao_2026", kpis)
        
        # Verificar as 5 colunas
        colunas = dados["colunas"]
        self.assertEqual(len(colunas), 5)
        for col_id in ["1_DFD", "2_ETP", "3_PESQUISA_TR", "4_JURIDICO", "5_GCC"]:
            self.assertIn(col_id, colunas)
            self.assertGreater(len(colunas[col_id]), 0)
            
            # Verificar campos do primeiro card de cada coluna
            item = colunas[col_id][0]
            self.assertIn("numero_processo_siga", item)
            self.assertIn("setor_atual_sigla", item)
            self.assertIn("custodiante_atual", item)
            self.assertIn("dias_no_setor", item)
            self.assertIn("diff_media_str", item)
            self.assertIn("status_prazo", item)
            self.assertIn("risco_nao_contratar_2026", item)
            self.assertIn("documentos_produzidos", item)
            self.assertIn("proximo_documento_pendente", item)

    def test_view_kanban_telemetria_execucao(self):
        request = self.factory.get('/api/planejamento/kanban-telemetria/?ano=2026')
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        json_data = response.data
        self.assertIn("kpis", json_data)
        self.assertIn("colunas", json_data)
        self.assertGreater(json_data["kpis"]["total_processos"], 150)

if __name__ == '__main__':
    unittest.main()
