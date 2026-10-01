from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from demands.services_contratos_fluxo import ContratosFluxoService, AREAS_TELEBRAS

class ContratosFluxoTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_carregar_contratos_vigentes(self):
        """Testa o carregamento dos contratos vigentes do PNCP e enriquecimento de dados"""
        contratos = ContratosFluxoService.carregar_contratos_vigentes()
        self.assertGreater(len(contratos), 0)
        
        primeiro = contratos[0]
        self.assertIn("numero_contrato", primeiro)
        self.assertIn("numero_processo_siga", primeiro)
        self.assertIn("dias_restantes", primeiro)
        self.assertIn("status_vigencia", primeiro)
        self.assertIn("area_atual_tramitacao", primeiro)
        self.assertIn("fornecedor", primeiro)

    def test_inferencia_preditiva_ia_fluxo(self):
        """Testa a inferência de próximo caminho lógico pelas áreas da Telebras"""
        # Contrato 3 (Oracle - está na GCC, com fim próximo)
        inferencia = ContratosFluxoService.inferir_caminho_e_fluxo(3)
        self.assertNotIn("erro", inferencia)
        self.assertEqual(inferencia["onde_esta"], "2. GCC - Compras & Contratações")
        self.assertIn("proxima_area_inferida", inferencia)
        self.assertIn("caminho_restante_completo", inferencia)
        self.assertGreater(len(inferencia["caminho_restante_completo"]), 0)
        self.assertIn("checklist_documentos_necessarios", inferencia)
        self.assertIn("acao_imediata_recomendada", inferencia)
        self.assertIn("status_sla", inferencia)

    def test_resumo_areas_telebras(self):
        """Testa o mapa das 7 macro-áreas da Telebras no Fluxo Lógico"""
        resumo = ContratosFluxoService.obter_resumo_fluxo_areas()
        self.assertIn("total_contratos_vigentes", resumo)
        self.assertIn("areas_fluxo", resumo)
        self.assertEqual(len(resumo["areas_fluxo"]), 7)

        siglas = [a["sigla"] for a in resumo["areas_fluxo"]]
        self.assertIn("REQUISITANTE", siglas)
        self.assertIn("GCC", siglas)
        self.assertIn("GEFIN", siglas)
        self.assertIn("CONJUR", siglas)
        self.assertIn("DIRETORIA", siglas)
        self.assertIn("PNCP/DOU", siglas)
        self.assertIn("GECAD", siglas)

    def test_api_endpoints_contratos_fluxo(self):
        """Testa as chamadas HTTP dos endpoints de Contratos PNCP e Fluxo Telebras"""
        # 1. Lista de Contratos
        res_lista = self.client.get('/api/contratos/pncp-vigentes/')
        self.assertEqual(res_lista.status_code, status.HTTP_200_OK)
        self.assertIn("contratos", res_lista.data)
        self.assertIn("areas_telebras", res_lista.data)

        # 2. Resumo das Áreas
        res_areas = self.client.get('/api/contratos/fluxo-areas-telebras/')
        self.assertEqual(res_areas.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_areas.data["areas_fluxo"]), 7)

        # 3. Inferência de Contrato Específico
        res_inf = self.client.get('/api/contratos/1/inferir-tramitacao/')
        self.assertEqual(res_inf.status_code, status.HTTP_200_OK)
        self.assertIn("proxima_area_inferida", res_inf.data)

        # 4. Tempo Médio por Área (Amostras de Processos)
        res_tempo = self.client.get('/api/contratos/tempo-medio-areas/')
        self.assertEqual(res_tempo.status_code, status.HTTP_200_OK)
        self.assertIn("distribuicao_tempo_areas", res_tempo.data)
        self.assertGreater(res_tempo.data["amostras_analisadas"], 0)

        # 5. Processo Paradigma Completo Encerrado no SIGA
        res_paradigma = self.client.get('/api/contratos/processo-paradigma/')
        self.assertEqual(res_paradigma.status_code, status.HTTP_200_OK)
        self.assertEqual(res_paradigma.data["numero_processo"], "53000.002814/2026-31")
        self.assertEqual(len(res_paradigma.data["fases_percorridas"]), 7)

        # 6. Kanban Multi-Áreas Telebras
        res_kanban = self.client.get('/api/contratos/kanban-areas/')
        self.assertEqual(res_kanban.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_kanban.data), 7)

