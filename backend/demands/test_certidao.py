from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from demands.models import Demand
from demands.services_certidao import (
    normalizar_numero_siga,
    validar_formato_siga,
    gerar_hash_autenticidade,
    gerar_certidao_pdf,
    vincular_processo_siga_demanda
)

User = get_user_model()

class TestCertidaoRastreioService(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.demanda = Demand.objects.create(
            description="Contratação de Serviços de Medicina do Trabalho e Saúde Ocupacional",
            directorate="3000 - Diretoria Técnico-Operacional",
            management_unit="3600 - GERÊNCIA DE OPERAÇÕES",
            responsible_name="Marcelo Santos",
            responsible_email="marcelo.santos@telebras.com.br",
            item_type="SERVICO",
            nature_type="NOVA",
            catmat_code="CATSER 3220",
            quantity=1,
            estimated_value=1200000.00,
            procurement_type="Pregão Eletrônico",
            intended_date=date(2027, 8, 15),
            f1=5, f2=5, f3=3, f4=3,
            created_by=self.user
        )

    def test_codigo_rastreio_gerado_automaticamente(self):
        self.demanda.refresh_from_db()
        self.assertIsNotNone(self.demanda.codigo_rastreio_plac)
        # Formato: PLAC2027-DTO0001
        self.assertTrue(self.demanda.codigo_rastreio_plac.startswith("PLAC2027-DTO"))

    def test_normalizar_numero_siga(self):
        self.assertEqual(normalizar_numero_siga("TLB-PRO-2026-002672"), "TLB-PRO-2026/002672")
        self.assertEqual(normalizar_numero_siga("tlb-pro-2024/03820"), "TLB-PRO-2024/03820")
        self.assertEqual(normalizar_numero_siga("2026/002672"), "TLB-PRO-2026/002672")

    def test_validar_formato_siga(self):
        self.assertTrue(validar_formato_siga("TLB-PRO-2026/002672"))
        self.assertTrue(validar_formato_siga("TLB-PRO-2026-002672"))
        self.assertFalse(validar_formato_siga("PROCESSO-INVALIDO"))
        self.assertFalse(validar_formato_siga("12345"))

    def test_gerar_hash_autenticidade(self):
        h = gerar_hash_autenticidade(self.demanda)
        self.assertEqual(len(h), 64)
        self.assertTrue(h.isalnum())

    def test_gerar_certidao_pdf_em_memoria(self):
        pdf_bytes = gerar_certidao_pdf(self.demanda)
        self.assertIsInstance(pdf_bytes, bytes)
        # Assinatura de cabeçalho PDF
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 1000)

    def test_vincular_processo_siga_demanda(self):
        res = vincular_processo_siga_demanda(self.demanda.id, "TLB-PRO-2026-002672")
        self.assertEqual(res["status"], "sucesso")
        self.assertEqual(res["siga_process_number"], "TLB-PRO-2026/002672")

        self.demanda.refresh_from_db()
        self.assertEqual(self.demanda.siga_process_number, "TLB-PRO-2026/002672")

    def test_api_emitir_certidao_pdf(self):
        url = f"/api/planejamento/demandas/{self.demanda.id}/emitir-certidao-pdf/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", resp["Content-Disposition"])

    def test_api_emitir_certidao_pdf_inline_abre_no_navegador(self):
        url = f"/api/planejamento/demandas/{self.demanda.id}/emitir-certidao-pdf/?inline=1"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp["Content-Disposition"].startswith("inline; filename="))
        self.assertTrue(resp.content.startswith(b"%PDF-"))

    def test_api_vincular_processo_siga(self):
        url = "/api/planejamento/vincular-processo-siga/"
        payload = {
            "demand_id": self.demanda.id,
            "numero_processo_siga": "TLB-PRO-2026/002672"
        }
        resp = self.client.post(url, data=payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "sucesso")
        self.assertEqual(data["siga_process_number"], "TLB-PRO-2026/002672")
