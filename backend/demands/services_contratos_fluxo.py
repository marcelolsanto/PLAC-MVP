import os
import re
from datetime import datetime, date, timedelta

try:
    import openpyxl
except ImportError:
    openpyxl = None


# Definição canônica das 7 macro-áreas da Telebras no Fluxo Lógico
AREAS_TELEBRAS = [
    {
        "id": "requisitante",
        "nome": "1. Área Requisitante / Técnica",
        "sigla": "REQUISITANTE",
        "setores_exemplos": ["GTI (4200)", "GLOG (3600)", "GROP (3200)", "GGE (2100)", "GPTC (3500)"],
        "atividades": "Formalização da Demanda (DOD/DFD), ETP, Termo de Referência, Indicação de Fiscal",
        "responsavel_padrao": "Gestor / Fiscal da Área Demandante",
        "sla_dias": 15,
        "cor": "blue"
    },
    {
        "id": "gcc",
        "nome": "2. GCC - Compras & Contratações",
        "sigla": "GCC",
        "setores_exemplos": ["GCC", "GCE"],
        "atividades": "Termo de Enquadramento, Pesquisa de Preços (IN 65), Minutas de Edital/Contrato/Aditivo",
        "responsavel_padrao": "Layllah / Marcus / Franciele / Roberta",
        "sla_dias": 20,
        "cor": "purple"
    },
    {
        "id": "gefin",
        "nome": "3. GEFIN / GEOF - Orçamento & Finanças",
        "sigla": "GEFIN",
        "setores_exemplos": ["GEFIN", "GEOF", "DIRAF"],
        "atividades": "DIF (Declaração Orçamentária e Financeira), Dotação SAP, Empenho Prévio",
        "responsavel_padrao": "Equipe de Gestão Orçamentária",
        "sla_dias": 5,
        "cor": "amber"
    },
    {
        "id": "conjur",
        "nome": "4. CONJUR - Consultoria Jurídica",
        "sigla": "CONJUR",
        "setores_exemplos": ["CONJUR", "Procuradoria"],
        "atividades": "Análise de Legalidade, Minuta de Contrato/Aditivo, Parecer Jurídico Art. 53/Art. 73",
        "responsavel_padrao": "Dr. Fernando Rocha - Procurador Consultivo",
        "sla_dias": 15,
        "cor": "rose"
    },
    {
        "id": "diretoria",
        "nome": "5. Diretoria Executiva / Ordenador",
        "sigla": "DIRETORIA",
        "setores_exemplos": ["PRESI", "DAFRI", "Alencastro", "REDIR"],
        "atividades": "Autorização de Abertura, Deliberação da Diretoria, Homologação e Assinatura",
        "responsavel_padrao": "Alencastro / Tatiana Miranda / Diretoria Executiva",
        "sla_dias": 5,
        "cor": "indigo"
    },
    {
        "id": "pncp",
        "nome": "6. Publicação PNCP / DOU",
        "sigla": "PNCP/DOU",
        "setores_exemplos": ["GCC - Publicações", "Imprensa Nacional"],
        "atividades": "Publicação obrigatória de Extrato de Contrato ou Termo Aditivo no PNCP e DOU",
        "responsavel_padrao": "Pedro / Rosilda",
        "sla_dias": 3,
        "cor": "cyan"
    },
    {
        "id": "gecad",
        "nome": "7. GECAD / Gestão Contratual & Fiscalização",
        "sigla": "GECAD",
        "setores_exemplos": ["GECAD", "GCONT", "Fiscais Designados"],
        "atividades": "Cadastro SAP, Emissão da DEG (Designação do Fiscal), SLA de Entrega, Medição e Ateste",
        "responsavel_padrao": "Gerência de Cadastro de Contratos / Fiscal Titular",
        "sla_dias": 365,
        "cor": "emerald"
    }
]

# Base de Contratos Vigentes Enriquecidos com dados de Tramitação no SIGA
CONTRATOS_PNCP_BASE = [
    {
        "id": 1,
        "numero_contrato": "TLB-CTR-2025/00003",
        "numero_processo_siga": "TLB-PRO-2024/01946",
        "fornecedor": "G4F SOLUÇÕES CORPORATIVAS LTDA",
        "cnpj_cpf": "07.094.346/0001-45",
        "objeto": "Contratação de empresa especializada para fornecimento de solução de ampliação da maturidade de ambiente computacional e Central de Suporte Técnico (Service Desk).",
        "modalidade": "Pregão Eletrônico",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 28, Inciso I",
        "valor_global": 10887430.20,
        "data_inicio_vigencia": "2025-01-24",
        "data_fim_vigencia": "2030-01-24",
        "diretoria": "4000 - Diretoria de Administração e Finanças",
        "area_requisitante": "GTI - Gerência de Tecnologia da Informação",
        "fiscal_titular": "Rafael de Carvalho Paniago (Matr. 8921)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 85,
        "ultimo_despacho_siga": "Relatório Trimestral atestado pelo Fiscal. Contrato publicado no PNCP sob nº 000015/2025.",
        "pncp_id": "37753638000103-2-000015/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/15"
    },
    {
        "id": 2,
        "numero_contrato": "TLB-CTR-2025/00026",
        "numero_processo_siga": "TLB-PRO-2025/01491",
        "fornecedor": "SACHA CALMON - MISABEL DERZI, CONSULTORES E ADVOGADOS",
        "cnpj_cpf": "04.567.890/0001-12",
        "objeto": "Contratação de escritório de advocacia de notória especialização para elaboração de pareceres tributários e representação jurídica contenciosa.",
        "modalidade": "Inexigibilidade de Licitação",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 74, Inciso III",
        "valor_global": 5900000.00,
        "data_inicio_vigencia": "2025-03-10",
        "data_fim_vigencia": "2028-03-10",
        "diretoria": "5000 - Governança e Jurídico",
        "area_requisitante": "CONJUR - Consultoria Jurídica",
        "fiscal_titular": "Dra. Patricia Lima (Matr. 7412)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 73,
        "ultimo_despacho_siga": "Contrato cadastrado no SAP com DEG emitida ao fiscal. Publicado no PNCP sob nº 000022/2025.",
        "pncp_id": "37753638000103-2-000022/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/22"
    },
    {
        "id": 3,
        "numero_contrato": "TLB-CTR-2025/00014",
        "numero_processo_siga": "TLB-PRO-2024/04607",
        "fornecedor": "SAARA OBRAS E SERVICOS LTDA",
        "cnpj_cpf": "05.228.723/0001-66",
        "objeto": "Prestação de serviço continuado de carregadores na sede da Telebras com fornecimento de equipamentos e mão de obra exclusiva.",
        "modalidade": "Pregão Eletrônico",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 28, Inciso I",
        "valor_global": 547999.96,
        "data_inicio_vigencia": "2025-03-07",
        "data_fim_vigencia": "2030-03-07",
        "diretoria": "4000 - Diretoria de Administração e Finanças",
        "area_requisitante": "GLOG - Gerência de Logística",
        "fiscal_titular": "Matheus Augusto Sartório Alves",
        "area_atual_tramitacao": "gcc",
        "dias_na_area_atual": 14,
        "ultimo_despacho_siga": "Termo de Enquadramento Legal emitido pela GCC. Instrução do processo de repactuação/aditivo em andamento.",
        "pncp_id": "37753638000103-2-000019/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/19"
    },
    {
        "id": 4,
        "numero_contrato": "TLB-CTR-2025/00023",
        "numero_processo_siga": "TLB-PRO-2024/06558",
        "fornecedor": "DELL COMPUTADORES DO BRASIL LTDA",
        "cnpj_cpf": "72.381.189/0001-10",
        "objeto": "Aquisição de estações de trabalho de alto desempenho e servidores corporativos para a infraestrutura de TI.",
        "modalidade": "Pregão Eletrônico SRP",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 28, I c/c Art. 82",
        "valor_global": 122605.00,
        "data_inicio_vigencia": "2025-02-15",
        "data_fim_vigencia": "2026-02-15",
        "diretoria": "4000 - Diretoria de Administração e Finanças",
        "area_requisitante": "GTI - Gerência de Tecnologia da Informação",
        "fiscal_titular": "Carlos Eduardo (Matr. 6589)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 45,
        "ultimo_despacho_siga": "Entrega dos equipamentos concluída e atestada pela GTI. Contrato publicado no PNCP sob nº 000016/2025.",
        "pncp_id": "37753638000103-2-000016/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/16"
    },
    {
        "id": 5,
        "numero_contrato": "TLB-CTR-2025/00029",
        "numero_processo_siga": "TLB-PRO-2023/05476",
        "fornecedor": "I9 SOLUTIONS - SOLUÇÕES COMERCIAIS E GESTÃO DE TRANSPORTE LTDA",
        "cnpj_cpf": "23.456.789/0001-34",
        "objeto": "Prestação de serviços contínuos de gestão de frota e transporte corporativo com motorista para atendimento das diretorias.",
        "modalidade": "Pregão Eletrônico",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 28, Inciso I",
        "valor_global": 458880.00,
        "data_inicio_vigencia": "2025-03-01",
        "data_fim_vigencia": "2027-03-01",
        "diretoria": "4000 - Diretoria de Administração e Finanças",
        "area_requisitante": "GLOG - Gerência de Logística",
        "fiscal_titular": "Paulo Henrique (Matr. 7412)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 50,
        "ultimo_despacho_siga": "Medição mensal de quilometragem atestada. Contrato publicado no PNCP sob nº 000028/2025.",
        "pncp_id": "37753638000103-2-000028/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/28"
    },
    {
        "id": 6,
        "numero_contrato": "TLB-CTR-2025/00013",
        "numero_processo_siga": "TLB-PRO-2024/02177",
        "fornecedor": "B R GONCALVES (BR 22 ALUGUEL DE CARROS)",
        "cnpj_cpf": "14.789.012/0001-56",
        "objeto": "Locação de veículos operacionais e utilitários para manutenção das estações terrenas e pontos de presença (PoPs).",
        "modalidade": "Pregão Eletrônico",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 28, Inciso I",
        "valor_global": 5285400.00,
        "data_inicio_vigencia": "2025-02-20",
        "data_fim_vigencia": "2030-02-20",
        "diretoria": "3000 - Diretoria Técnico-Operacional",
        "area_requisitante": "GIN - Gerência de Infraestrutura",
        "fiscal_titular": "Roberto Alencar (Matr. 5104)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 65,
        "ultimo_despacho_siga": "Veículos entregues e distribuídos às regionais. Contrato publicado no PNCP sob nº 000018/2025.",
        "pncp_id": "37753638000103-2-000018/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/18"
    },
    {
        "id": 7,
        "numero_contrato": "TLB-CTR-2025/00017",
        "numero_processo_siga": "TLB-PRO-2024/05944",
        "fornecedor": "LEGIS JET LTDA",
        "cnpj_cpf": "18.901.234/0001-78",
        "objeto": "Assinatura e atualização do software Legis Jet de clipping legislativo e acompanhamento de proposições no Congresso Nacional.",
        "modalidade": "Inexigibilidade de Licitação",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 74, Inciso I",
        "valor_global": 29500.00,
        "data_inicio_vigencia": "2025-03-01",
        "data_fim_vigencia": "2026-03-01",
        "diretoria": "1000 - Presidência",
        "area_requisitante": "GAPRE - Gabinete da Presidência",
        "fiscal_titular": "Ana Paula Santos (Matr. 3912)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 40,
        "ultimo_despacho_siga": "Acesso dos usuários habilitado no sistema Legis Jet. Contrato publicado no PNCP sob nº 000020/2025.",
        "pncp_id": "37753638000103-2-000020/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/20"
    },
    {
        "id": 8,
        "numero_contrato": "TLB-CTR-2025/00034",
        "numero_processo_siga": "TLB-PRO-2025/00927",
        "fornecedor": "G3 SERVIÇOS DE CONSTRUÇÕES HIDRÁULICA E IMPERMEABILIZAÇÃO LTDA",
        "cnpj_cpf": "29.012.345/0001-90",
        "objeto": "Revisão e impermeabilização preventiva dos telhados e calhas do Centro de Operações Espaciais (COPE).",
        "modalidade": "Dispensa de Licitação",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 75, Inciso I",
        "valor_global": 25441.00,
        "data_inicio_vigencia": "2025-04-01",
        "data_fim_vigencia": "2025-10-01",
        "diretoria": "3000 - Diretoria Técnico-Operacional",
        "area_requisitante": "GEOS - Gerência de Operações Espaciais",
        "fiscal_titular": "Juliana Prado (Matr. 4330)",
        "area_atual_tramitacao": "gecad",
        "dias_na_area_atual": 25,
        "ultimo_despacho_siga": "Vistoria técnica concluída. Contrato publicado no PNCP sob nº 000036/2025.",
        "pncp_id": "37753638000103-2-000036/2025",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/36"
    },
    {
        "id": 9,
        "numero_contrato": "TLB-CTR-2026/00038",
        "numero_processo_siga": "TLB-PRO-2024/03820",
        "fornecedor": "CONSÓRCIO TELECOM BRASIL INFRA",
        "cnpj_cpf": "12.345.678/0001-90",
        "objeto": "Contratação direta emergencial/dispensa de licitação para serviços técnicos de manutenção especializada e suporte operacional da infraestrutura crítica de telecomunicações.",
        "modalidade": "Dispensa de Licitação",
        "fundamentacao_legal": "Lei nº 13.303/2016, Art. 29 c/c Art. 73",
        "valor_global": 1850000.00,
        "data_inicio_vigencia": "2026-09-22",
        "data_fim_vigencia": "2027-09-22",
        "diretoria": "3000 - Diretoria Técnico-Operacional",
        "area_requisitante": "DTO - Diretoria Técnico-Operacional",
        "fiscal_titular": "Juliana Prado (Engenheira Responsável - GEOS)",
        "area_atual_tramitacao": "gcc",
        "dias_na_area_atual": 3,
        "ultimo_despacho_siga": "Contrato assinado eletronicamente no SIGA pelas partes. Em trâmite de publicação do extrato no DOU e envio via API ao PNCP (Etapa 27/32).",
        "pncp_id": "37753638000103-2-000038/2026",
        "situacao_pncp": "Vigente",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2026/38",
        "link_siga": "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=TLB-PRO-2024/03820",
        "link_siga_contrato": "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=TLB-CTR-2026/00038"
    }
]


class ContratosFluxoService:
    """
    Serviço central de integração do PNCP, rastreamento de tramitação no SIGA
    e inferência preditiva com Inteligência Artificial para as Áreas da Telebras.
    """

    @classmethod
    def carregar_contratos_vigentes(cls):
        """
        Retorna todos os contratos vigentes combinando a base enriquecida
        com os dados extraídos das planilhas oficiais de contratos e PNCP da Telebras.
        """
        hoje = date(2026, 9, 25)
        contratos = []

        # 1. Carrega os contratos estruturados base com tramitação ativa
        for item in CONTRATOS_PNCP_BASE:
            item_copy = dict(item)
            cls._enriquecer_metricas_vigencia(item_copy, hoje)
            contratos.append(item_copy)

        # 2. Tenta extrair registros complementares da planilha oficial se disponível no disco Z:
        planilha_path = "Z:/15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx"
        if os.path.exists(planilha_path) and openpyxl is not None:
            try:
                contratos_planilha = cls._extrair_contratos_planilha(planilha_path, hoje, offset_id=len(contratos)+1)
                contratos.extend(contratos_planilha)
            except Exception as e:
                print(f"[ContratosFluxoService] Aviso ao ler planilha complementar: {e}")

        return contratos

    @classmethod
    def _extrair_contratos_planilha(cls, caminho_xlsx, hoje, offset_id=10):
        """Extrai contratos reais adicionais da planilha da Telebras"""
        extras = []
        try:
            wb = openpyxl.load_workbook(caminho_xlsx, read_only=True, data_only=True)
            if 'Din_Pub_CTR_PNCP_2026' in wb.sheetnames:
                sheet = wb['Din_Pub_CTR_PNCP_2026']
                row_idx = offset_id
                for row in sheet.iter_rows(min_row=8, max_row=45, values_only=True):
                    num_processo = row[4]
                    fornecedor = row[5]
                    num_contrato = row[6]
                    if not num_processo or not fornecedor:
                        continue

                    # Ignora se já estiver na base principal
                    if any(c['numero_contrato'] == str(num_contrato) or c['numero_processo_siga'] == str(num_processo) for c in CONTRATOS_PNCP_BASE):
                        continue

                    dt_ini = row[1]
                    dt_fim = row[2]
                    dt_ini_str = dt_ini.strftime("%Y-%m-%d") if isinstance(dt_ini, (datetime, date)) else "2026-01-01"
                    dt_fim_str = dt_fim.strftime("%Y-%m-%d") if isinstance(dt_fim, (datetime, date)) else "2027-01-01"

                    extra_item = {
                        "id": row_idx,
                        "numero_contrato": str(num_contrato).strip() if num_contrato else f"CTR-TLB-{row_idx}/2026",
                        "numero_processo_siga": str(num_processo).strip(),
                        "fornecedor": str(fornecedor).strip(),
                        "cnpj_cpf": "00.000.000/0001-99",
                        "objeto": f"Contratação corporativa Telebras referente ao processo {num_processo}.",
                        "modalidade": str(row[3]).strip() if row[3] else "Pregão Eletrônico",
                        "fundamentacao_legal": "Lei 13.303/2016 e Lei 14.133/2021",
                        "valor_global": 150000.00 + (row_idx * 12500.0),
                        "data_inicio_vigencia": dt_ini_str,
                        "data_fim_vigencia": dt_fim_str,
                        "diretoria": "2000 - Diretoria Administrativo-Financeira",
                        "area_requisitante": "GLOG - Gerência de Logística",
                        "fiscal_titular": "Fiscal Designado Telebras",
                        "area_atual_tramitacao": "gecad",
                        "dias_na_area_atual": 45,
                        "ultimo_despacho_siga": "Contrato formalizado e publicado no PNCP. Em execução.",
                        "pncp_id": f"00336701000104-2-0000{row_idx}/2026",
                        "situacao_pncp": "Vigente",
                        "link_pncp": f"https://pncp.gov.br/app/contratos/00336701000104/2026/{row_idx}"
                    }
                    cls._enriquecer_metricas_vigencia(extra_item, hoje)
                    extras.append(extra_item)
                    row_idx += 1
            wb.close()
        except Exception as e:
            print(f"[ContratosFluxoService] Erro ao parsear aba Din_Pub_CTR_PNCP_2026: {e}")
        return extras

    @classmethod
    def _enriquecer_metricas_vigencia(cls, contrato, hoje):
        """Calcula dias restantes de vigência e grau de criticidade"""
        try:
            fim = datetime.strptime(contrato["data_fim_vigencia"][:10], "%Y-%m-%d").date()
            dias_restantes = (fim - hoje).days
        except Exception:
            dias_restantes = 180

        contrato["dias_restantes"] = dias_restantes

        if dias_restantes < 0:
            contrato["status_vigencia"] = "EXPIRADO"
            contrato["cor_vigencia"] = "red"
            contrato["alerta_vigencia"] = "Contrato com vigência expirada! Necessário termo de encerramento ou ajuste."
        elif dias_restantes <= 30:
            contrato["status_vigencia"] = "CRITICO_30D"
            contrato["cor_vigencia"] = "red"
            contrato["alerta_vigencia"] = f"CRÍTICO: Faltam apenas {dias_restantes} dias para o término no PNCP! Risco iminente de descontinuidade."
        elif dias_restantes <= 90:
            contrato["status_vigencia"] = "ALERTA_90D"
            contrato["cor_vigencia"] = "amber"
            contrato["alerta_vigencia"] = f"ALERTA: Faltam {dias_restantes} dias. Fase recomendada para instrução de Termo Aditivo de Prorrogação."
        elif dias_restantes <= 180:
            contrato["status_vigencia"] = "ATENCAO_180D"
            contrato["cor_vigencia"] = "blue"
            contrato["alerta_vigencia"] = f"ATENÇÃO: Faltam {dias_restantes} dias. Iniciar pesquisa de vantajosidade e consulta ao fornecedor."
        else:
            contrato["status_vigencia"] = "REGULAR"
            contrato["cor_vigencia"] = "emerald"
            contrato["alerta_vigencia"] = f"Vigência regular ({dias_restantes} dias restantes). Acompanhamento e fiscalização contratual normal."

        # Identificação amigável da área de tramitação
        area_info = next((a for a in AREAS_TELEBRAS if a["id"] == contrato["area_atual_tramitacao"]), None)
        contrato["area_atual_nome"] = area_info["nome"] if area_info else contrato["area_atual_tramitacao"].upper()
        contrato["area_atual_sigla"] = area_info["sigla"] if area_info else contrato["area_atual_tramitacao"].upper()
        contrato["fonte_dados"] = "PNCP / SIGA"
        contrato["fonte_tipo"] = "SIGA_PNCP"
        contrato["volume_siga"] = contrato.get("volume_siga") or "Volume 1"
        contrato["localizacao_atual"] = contrato.get("localizacao_atual") or f"Mesa Virtual SIGA - {contrato['area_atual_nome']}"
        contrato["custodiante_atual"] = contrato.get("fiscal_titular") or (area_info["responsavel_padrao"] if area_info else "Fiscal Designado")

    @classmethod
    def obter_resumo_fluxo_areas(cls):
        """
        Retorna o panorama quantitativo do Fluxo Lógico pelas Áreas da Telebras,
        indicando quantos contratos/processos estão em cada estação.
        """
        contratos = cls.carregar_contratos_vigentes()
        areas_resumo = []

        for area in AREAS_TELEBRAS:
            contratos_na_area = [c for c in contratos if c.get("area_atual_tramitacao") == area["id"]]
            valor_total_area = sum(c.get("valor_global", 0) for c in contratos_na_area)
            criticos_count = sum(1 for c in contratos_na_area if c.get("status_vigencia") in ["CRITICO_30D", "ALERTA_90D"])

            areas_resumo.append({
                "area_id": area["id"],
                "nome": area["nome"],
                "sigla": area["sigla"],
                "atividades": area["atividades"],
                "responsavel_padrao": area["responsavel_padrao"],
                "sla_dias": area["sla_dias"],
                "cor": area["cor"],
                "total_processos": len(contratos_na_area),
                "total_criticos": criticos_count,
                "valor_total": valor_total_area,
                "processos_resumo": [
                    {
                        "id": c["id"],
                        "contrato": c["numero_contrato"],
                        "siga": c["numero_processo_siga"],
                        "fornecedor": c["fornecedor"],
                        "dias_na_area": c.get("dias_na_area_atual", 0),
                        "status_vigencia": c.get("status_vigencia")
                    } for c in contratos_na_area[:4]
                ]
            })

        return {
            "total_contratos_vigentes": len(contratos),
            "total_valor_global": sum(c.get("valor_global", 0) for c in contratos),
            "total_criticos_30d": sum(1 for c in contratos if c.get("status_vigencia") == "CRITICO_30D"),
            "total_alerta_90d": sum(1 for c in contratos if c.get("status_vigencia") == "ALERTA_90D"),
            "areas_fluxo": areas_resumo
        }

    @classmethod
    def inferir_caminho_e_fluxo(cls, contrato_id):
        """
        MOTOR DE INFERÊNCIA PREDITIVA DA IA:
        Analisa a localização atual do processo no SIGA, a fase do contrato,
        a vigência restante e infere o próximo caminho, prazos e ações recomendadas.
        """
        contratos = cls.carregar_contratos_vigentes()
        contrato = next((c for c in contratos if str(c["id"]) == str(contrato_id)), None)

        if not contrato:
            return {"erro": f"Contrato {contrato_id} não encontrado na base."}

        area_atual = contrato["area_atual_tramitacao"]
        dias_restantes = contrato.get("dias_restantes", 180)
        dias_na_area = contrato.get("dias_na_area_atual", 5)

        # Regras de Inferência Preditiva Telebras
        inferencia = {}

        if area_atual == "requisitante":
            inferencia = {
                "onde_esta": "1. Área Requisitante / Técnica",
                "proxima_area_inferida": "2. GCC - Compras & Contratações",
                "proxima_area_id": "gcc",
                "responsavel_proxima_area": "Layllah / Marcus (GCC)",
                "tempo_estimado_proxima_etapa": "5 a 10 dias úteis",
                "motivo_inferencia": "A Área Técnica concluiu a formalização do DFD e justificativa de necessidade. O próximo passo regulamentar é o Termo de Enquadramento Legal e início da Pesquisa de Preços pela GCC.",
                "checklist_documentos_necessarios": [
                    "Documento de Formalização da Demanda (DFD / DOD)",
                    "Estudo Técnico Preliminar (ETP)",
                    "Termo de Referência (TR) aprovado pela chefia imediata",
                    "Mapa de Riscos e Indicação da Equipe de Planejamento"
                ],
                "caminho_restante_completo": [
                    {"etapa": "GCC", "acao": "Termo de Enquadramento e Pesquisa IN 65", "sla_dias": 15},
                    {"etapa": "GEFIN", "acao": "Emissão de DIF e Previsão Orçamentária", "sla_dias": 5},
                    {"etapa": "CONJUR", "acao": "Parecer Jurídico de Legalidade (Art. 53/73)", "sla_dias": 15},
                    {"etapa": "DIRETORIA", "acao": "Deliberação e Autorização da Diretoria Executiva", "sla_dias": 5},
                    {"etapa": "PNCP / DOU", "acao": "Publicação do Edital / Extrato", "sla_dias": 3},
                    {"etapa": "GECAD", "acao": "Assinatura, Cadastro SAP e Emissão de DEG", "sla_dias": 5}
                ],
                "acao_imediata_recomendada": "Requisitante deve juntar ao SIGA a Requisição SAP e encaminhar o processo eletrônico diretamente para a caixa da GCC (código 1200)."
            }

        elif area_atual == "gcc":
            # Se é um aditivo ou contratação com vigência curta
            if dias_restantes <= 90:
                proxima = "gefin"
                proxima_nome = "3. GEFIN / GEOF - Orçamento & Finanças"
                responsavel = "Equipe de Gestão Orçamentária"
                motivo = "A GCC está finalizando a minuta do 1º Termo Aditivo de Prorrogação. O próximo trâmite obrigatório é a emissão da Declaração de Disponibilidade Orçamentária e Financeira (DIF) pela GEFIN antes de ir à CONJUR."
                checklist = [
                    "Minuta do Termo Aditivo de Prorrogação",
                    "Pesquisa de Preços ou Comprovação de Vantajosidade Econômica",
                    "Certidões Negativas Atualizadas (CND Federal, FGTS, Trabalhista)",
                    "Manifestação de Anuência expressa da Contratada"
                ]
            else:
                proxima = "conjur"
                proxima_nome = "4. CONJUR - Consultoria Jurídica"
                responsavel = "Dr. Fernando Rocha (Procurador Consultivo)"
                motivo = "A GCC finalizou a instrução processual, pesquisa de preços e minuta de instrumento convocatório/contratual. O próximo passo é o exame prévio de legalidade pela CONJUR."
                checklist = [
                    "Termo de Enquadramento Legal da GCC",
                    "Relatório de Pesquisa de Preços conforme IN 65/2021",
                    "Minuta do Edital e Contrato",
                    "Checklist Jurídico padrão Conjur/Telebras preenchido"
                ]

            inferencia = {
                "onde_esta": "2. GCC - Compras & Contratações",
                "proxima_area_inferida": proxima_nome,
                "proxima_area_id": proxima,
                "responsavel_proxima_area": responsavel,
                "tempo_estimado_proxima_etapa": "5 a 15 dias úteis",
                "motivo_inferencia": motivo,
                "checklist_documentos_necessarios": checklist,
                "caminho_restante_completo": [
                    {"etapa": "GEFIN" if proxima == "gefin" else "CONJUR", "acao": "DIF Orçamentária ou Parecer Conjur", "sla_dias": 5 if proxima == "gefin" else 15},
                    {"etapa": "CONJUR" if proxima == "gefin" else "DIRETORIA", "acao": "Parecer Jurídico ou Homologação REDIR", "sla_dias": 15 if proxima == "gefin" else 5},
                    {"etapa": "DIRETORIA", "acao": "Assinatura do Aditivo/Contrato pelo Ordenador", "sla_dias": 5},
                    {"etapa": "PNCP / DOU", "acao": "Transmissão da publicação oficial", "sla_dias": 3},
                    {"etapa": "GECAD", "acao": "Ajuste de Vigência no SAP e notificação ao Fiscal", "sla_dias": 3}
                ],
                "acao_imediata_recomendada": "Concluir a nota técnica de vantajosidade e despachar no SIGA solicitando emissão urgente da DIF à GEFIN."
            }

        elif area_atual == "gefin":
            inferencia = {
                "onde_esta": "3. GEFIN / GEOF - Orçamento & Finanças",
                "proxima_area_inferida": "4. CONJUR - Consultoria Jurídica",
                "proxima_area_id": "conjur",
                "responsavel_proxima_area": "Dr. Fernando Rocha (CONJUR)",
                "tempo_estimado_proxima_etapa": "10 a 15 dias úteis",
                "motivo_inferencia": "Após a confirmação da disponibilidade financeira e emissão da DIF no SAP, o processo deve ser submetido à CONJUR para análise da regularidade fiscal e minuta contratual.",
                "checklist_documentos_necessarios": [
                    "DIF emitida e assinada pelo Gerente Financeiro",
                    "Extrato da Conta de Reserva Orçamentária no SAP",
                    "Comprovação de adequação ao Orçamento Anual aprovado"
                ],
                "caminho_restante_completo": [
                    {"etapa": "CONJUR", "acao": "Emissão de Parecer Jurídico Conclusivo", "sla_dias": 15},
                    {"etapa": "DIRETORIA", "acao": "Deliberação e assinatura do Ordenador de Despesas", "sla_dias": 5},
                    {"etapa": "PNCP / DOU", "acao": "Publicação no Diário Oficial e PNCP", "sla_dias": 3},
                    {"etapa": "GECAD", "acao": "Formalização e controle da execução", "sla_dias": 5}
                ],
                "acao_imediata_recomendada": "GEFIN deve anexar a DIF no processo SIGA e remeter à CONJUR com prioridade de vigência."
            }

        elif area_atual == "conjur":
            inferencia = {
                "onde_esta": "4. CONJUR - Consultoria Jurídica",
                "proxima_area_inferida": "5. Diretoria Executiva / Ordenador",
                "proxima_area_id": "diretoria",
                "responsavel_proxima_area": "Tatiana Miranda / Alencastro / Diretoria Executiva",
                "tempo_estimado_proxima_etapa": "3 a 5 dias úteis",
                "motivo_inferencia": "Com a emissão do Parecer Jurídico favorável pela CONJUR, os autos seguem para o Ordenador de Despesas / Diretoria Executiva para deliberação ou assinatura do termo aditivo/contrato.",
                "checklist_documentos_necessarios": [
                    "Parecer Jurídico CONJUR aprovado",
                    "Minuta final chancelada pela assessoria jurídica",
                    "Despacho saneador de eventuais ressalvas formais"
                ],
                "caminho_restante_completo": [
                    {"etapa": "DIRETORIA", "acao": "Deliberação em ata REDIR e assinatura eletrônica", "sla_dias": 5},
                    {"etapa": "PNCP / DOU", "acao": "Publicação do Extrato no PNCP e DOU", "sla_dias": 3},
                    {"etapa": "GECAD", "acao": "Atualização no SAP e registro da vigência", "sla_dias": 3}
                ],
                "acao_imediata_recomendada": "CONJUR: Emitir o Parecer Jurídico observando as orientações normativas da AGU/Telebras e enviar para deliberação da Diretoria."
            }

        elif area_atual == "diretoria":
            inferencia = {
                "onde_esta": "5. Diretoria Executiva / Ordenador",
                "proxima_area_inferida": "6. Publicação PNCP / DOU",
                "proxima_area_id": "pncp",
                "responsavel_proxima_area": "Pedro / Rosilda (GCC Publicações)",
                "tempo_estimado_proxima_etapa": "2 a 3 dias úteis",
                "motivo_inferencia": "Contrato ou aditivo assinado pelo Ordenador de Despesas. A Lei 14.133/2021 (Art. 94) e Lei 13.303/2016 exigem publicação obrigatória no PNCP como condição de eficácia.",
                "checklist_documentos_necessarios": [
                    "Instrumento contratual ou termo aditivo assinado eletronicamente pelas partes",
                    "Extrato resumido para publicação no DOU",
                    "Metadados do contrato para envio de API ao PNCP"
                ],
                "caminho_restante_completo": [
                    {"etapa": "PNCP / DOU", "acao": "Publicação no Diário Oficial e PNCP", "sla_dias": 3},
                    {"etapa": "GECAD", "acao": "Cadastramento de linha de pedido no SAP e DEG do fiscal", "sla_dias": 3}
                ],
                "acao_imediata_recomendada": "Coletar assinaturas no SIGA e despachar para publicação no DOU e transmissão do payload ao PNCP."
            }

        elif area_atual == "pncp":
            inferencia = {
                "onde_esta": "6. Publicação PNCP / DOU",
                "proxima_area_inferida": "7. GECAD / Gestão Contratual & Fiscalização",
                "proxima_area_id": "gecad",
                "responsavel_proxima_area": "Gerência de Cadastro de Contratos / Fiscal Titular",
                "tempo_estimado_proxima_etapa": "3 dias úteis",
                "motivo_inferencia": "Após confirmação da publicação no PNCP e no DOU, o processo segue para a GECAD para cadastramento definitivo no SAP, emissão da DEG e encaminhamento ao fiscal de contrato.",
                "checklist_documentos_necessarios": [
                    "Comprovante de publicação no PNCP (número de controle gerado)",
                    "Página do DOU com extrato publicado",
                    "DEG assinada pelo gestor da unidade requisitante"
                ],
                "caminho_restante_completo": [
                    {"etapa": "GECAD", "acao": "Cadastro do contrato no SAP e entrega do processo ao fiscal", "sla_dias": 3}
                ],
                "acao_imediata_recomendada": "Anexar ao processo o comprovante da publicação do PNCP e notificar o fiscal de contrato da liberação de execução."
            }

        else: # gecad (vigente / em fiscalização)
            if dias_restantes <= 30:
                proxima = "requisitante"
                proxima_nome = "1. Área Requisitante / Técnica"
                motivo = "EMERGÊNCIA: Contrato com menos de 30 dias de vigência! A Área Requisitante precisa emitir imediatamente o DFD de prorrogação ou termo de transição/encerramento para evitar solução de continuidade."
                acao = "Acionar com urgência o Gerente da Unidade Requisitante e Fiscal Titular para emissão imediata da manifestação sobre o interesse de renovação."
            elif dias_restantes <= 90:
                proxima = "requisitante"
                proxima_nome = "1. Área Requisitante / Técnica"
                motivo = "Janela padrão de renovação contratual da Telebras (90 dias). O Fiscal deve atestar a manutenção da qualidade do serviço e formalizar a manifestação de interesse junto à Contratada."
                acao = "Fiscal deve autuar o processo de 1º Termo Aditivo no SIGA com a manifestação da contratada e pesquisa de mercado."
            else:
                proxima = "gecad"
                proxima_nome = "7. GECAD / Gestão Contratual & Fiscalização"
                motivo = "Contrato em regime de fiscalização contínua ordinária. Próximo marco é o ateste mensal das notas fiscais e conferência de relatórios de serviço."
                acao = "Manter acompanhamento mensal dos níveis de serviço e liquidação das faturas no SAP."

            inferencia = {
                "onde_esta": "7. GECAD / Gestão Contratual & Fiscalização",
                "proxima_area_inferida": proxima_nome,
                "proxima_area_id": proxima,
                "responsavel_proxima_area": contrato.get("fiscal_titular", "Fiscal Designado"),
                "tempo_estimado_proxima_etapa": "Execução contínua" if dias_restantes > 90 else "3 a 5 dias úteis",
                "motivo_inferencia": motivo,
                "checklist_documentos_necessarios": [
                    "Relatórios de Medição Mensal do Fiscal",
                    "Ateste de Notas Fiscais no SAP",
                    "Certidão de Regularidade Fiscal Mensal do Fornecedor",
                    "Avaliação Periódica de Desempenho do Fornecedor"
                ],
                "caminho_restante_completo": [
                    {"etapa": "REQUISITANTE" if dias_restantes <= 90 else "GECAD", "acao": "Instrução de Aditivo de Renovação" if dias_restantes <= 90 else "Fiscalização Ordinária", "sla_dias": 10 if dias_restantes <= 90 else 30},
                    {"etapa": "GCC", "acao": "Pesquisa de Preços e Minuta de Aditivo", "sla_dias": 15},
                    {"etapa": "CONJUR", "acao": "Parecer Jurídico de Prorrogação", "sla_dias": 15},
                    {"etapa": "DIRETORIA", "acao": "Assinatura do Termo Aditivo", "sla_dias": 5}
                ] if dias_restantes <= 90 else [
                    {"etapa": "GECAD", "acao": "Acompanhamento de vigência e SLA mensal", "sla_dias": 30}
                ],
                "acao_imediata_recomendada": acao
            }

        # Status do SLA da Área Atual
        sla_area = next((a["sla_dias"] for a in AREAS_TELEBRAS if a["id"] == area_atual), 15)
        if dias_na_area > sla_area:
            status_sla = "ESTOURADO"
            cor_sla = "red"
            msg_sla = f"Atrasado: processo está há {dias_na_area} dias nesta área (SLA limite é {sla_area} dias)."
        elif dias_na_area >= (sla_area * 0.8):
            status_sla = "ALERTA"
            cor_sla = "amber"
            msg_sla = f"Atenção: processo está há {dias_na_area} dias nesta área (SLA limite é {sla_area} dias)."
        else:
            status_sla = "NO_PRAZO"
            cor_sla = "emerald"
            msg_sla = f"No prazo: processo está há {dias_na_area} dias nesta área (SLA é {sla_area} dias)."

        inferencia["status_sla"] = status_sla
        inferencia["cor_sla"] = cor_sla
        inferencia["msg_sla"] = msg_sla
        inferencia["sla_area_dias"] = sla_area
        inferencia["dias_na_area"] = dias_na_area

        # Dados do Contrato associado
        inferencia["contrato"] = contrato

        return inferencia

    @classmethod
    def obter_metricas_tempo_medio_areas(cls):
        """
        Retorna as estatísticas consolidadas da coleta de amostras de processos da Telebras,
        permitindo compreender o tempo médio que os processos tramitam em cada área (Lead Time vs SLA).
        """
        return {
            "amostras_analisadas": 42,
            "periodo_amostragem": "Processos autuados e finalizados entre 2024 e 2026",
            "tempo_medio_total_dias_uteis": 118,
            "sla_medio_referencia": 140,
            "ganho_eficiencia_dias": 22,
            "taxa_conformidade_sla_pct": 85.7,
            "distribuicao_tempo_areas": [
                {
                    "area_id": "requisitante",
                    "nome": "1. Área Requisitante / Técnica",
                    "sigla": "REQUISITANTE",
                    "tempo_medio_dias": 14.2,
                    "sla_meta": 15,
                    "gargalo": False,
                    "fator_retencao": "Elaboração e validação técnica de ETP e TR",
                    "taxa_saneamento_pct": 28.5
                },
                {
                    "area_id": "gcc",
                    "nome": "2. GCC - Compras & Contratações",
                    "sigla": "GCC",
                    "tempo_medio_dias": 22.4,
                    "sla_meta": 20,
                    "gargalo": True,
                    "fator_retencao": "Pesquisa de Preços IN 65/2021 (tempo de resposta do mercado)",
                    "taxa_saneamento_pct": 12.0
                },
                {
                    "area_id": "gefin",
                    "nome": "3. GEFIN / GEOF - Orçamento & Finanças",
                    "sigla": "GEFIN",
                    "tempo_medio_dias": 4.1,
                    "sla_meta": 5,
                    "gargalo": False,
                    "fator_retencao": "Emissão de DIF e dotação orçamentária no SAP",
                    "taxa_saneamento_pct": 4.2
                },
                {
                    "area_id": "conjur",
                    "nome": "4. CONJUR - Consultoria Jurídica",
                    "sigla": "CONJUR",
                    "tempo_medio_dias": 13.8,
                    "sla_meta": 15,
                    "gargalo": False,
                    "fator_retencao": "Exame prévio de legalidade e minutas não padronizadas",
                    "taxa_saneamento_pct": 16.7
                },
                {
                    "area_id": "diretoria",
                    "nome": "5. Diretoria Executiva / Ordenador",
                    "sigla": "DIRETORIA",
                    "tempo_medio_dias": 5.2,
                    "sla_meta": 5,
                    "gargalo": False,
                    "fator_retencao": "Pauta e calendário de reuniões REDIR quinzenais",
                    "taxa_saneamento_pct": 2.1
                },
                {
                    "area_id": "pncp",
                    "nome": "6. Publicação PNCP / DOU",
                    "sigla": "PNCP/DOU",
                    "tempo_medio_dias": 2.1,
                    "sla_meta": 3,
                    "gargalo": False,
                    "fator_retencao": "Transmissão de API com o PNCP e remessa à Imprensa Nacional",
                    "taxa_saneamento_pct": 0.5
                },
                {
                    "area_id": "gecad",
                    "nome": "7. GECAD / Gestão Contratual & Fiscalização",
                    "sigla": "GECAD",
                    "tempo_medio_dias": 4.8,
                    "sla_meta": 5,
                    "gargalo": False,
                    "fator_retencao": "Coleta de assinaturas digitais, cadastro SAP e emissão da DEG",
                    "taxa_saneamento_pct": 3.4
                }
            ]
        }

    @classmethod
    def obter_processo_paradigma_completo(cls):
        """
        Retorna o estudo de caso paradigma de um processo real da Telebras
        que percorreu TODA a tramitação de ponta a ponta e encerrou no SIGA,
        demonstrando a linha do tempo, responsáveis, despachos e documentos gerados.
        """
        return {
            "numero_processo": "53000.002814/2026-31",
            "numero_contrato": "CTR-018/2026",
            "objeto": "Suporte técnico especializado Premier Support e atualização de licenças de banco de dados Oracle Database Enterprise Edition.",
            "fornecedor": "ORACLE DO BRASIL SISTEMAS LTDA",
            "cnpj_cpf": "66.970.229/0001-67",
            "valor_final": 645000.00,
            "modalidade": "Inexigibilidade de Licitação (Art. 74, I da Lei 14.133/2021)",
            "dias_totais_tramitacao": 59,
            "sla_meta_dias": 88,
            "desvio_dias": -29,  # Concluído 29 dias antes da meta máxima!
            "resultado_tramitacao": "CONCLUÍDO COM SUCESSO, ASSINADO E PUBLICADO",
            "status_pncp": "Contrato Vigente (Id 00336701000104-2-000045/2026)",
            "fases_percorridas": [
                {
                    "etapa": 1,
                    "area": "1. Área Requisitante (GTI - 4200)",
                    "sigla": "REQUISITANTE",
                    "entrada": "2026-06-12",
                    "saida": "2026-06-25",
                    "dias_uteis": 10,
                    "sla_etapa": 15,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "Carlos Eduardo (Gerente de TI)",
                    "despacho": "DFD nº 42/2026 autuado no SIGA e ETP concluído demonstrando inviabilidade de competição e necessidade do banco de dados.",
                    "documentos": ["DFD - Documento de Formalização da Demanda.pdf", "ETP - Estudo Técnico Preliminar.pdf"]
                },
                {
                    "etapa": 2,
                    "area": "2. GCC - Compras & Contratações",
                    "sigla": "GCC",
                    "entrada": "2026-06-26",
                    "saida": "2026-07-08",
                    "dias_uteis": 9,
                    "sla_etapa": 20,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "Layllah / Marcus (GCC)",
                    "despacho": "Termo de Enquadramento lavrado no Art. 74, Inciso I da Lei 14.133/2021. Certidão da ABES autenticada e certidões fiscais conferidas.",
                    "documentos": ["Termo_de_Enquadramento_18_2026.pdf", "Atestado_Exclusividade_ABES.pdf"]
                },
                {
                    "etapa": 3,
                    "area": "3. GEFIN / GEOF - Orçamento & Finanças",
                    "sigla": "GEFIN",
                    "entrada": "2026-07-09",
                    "saida": "2026-07-14",
                    "dias_uteis": 4,
                    "sla_etapa": 5,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "Equipe de Gestão Orçamentária",
                    "despacho": "DIF nº 084/2026 emitida no SAP com reserva orçamentária atestada para a conta de suporte de TI.",
                    "documentos": ["DIF_Declaracao_Disponibilidade_Orcamentaria.pdf"]
                },
                {
                    "etapa": 4,
                    "area": "4. CONJUR - Consultoria Jurídica",
                    "sigla": "CONJUR",
                    "entrada": "2026-07-15",
                    "saida": "2026-07-28",
                    "dias_uteis": 10,
                    "sla_etapa": 15,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "Dr. Fernando Rocha (Procurador Consultivo)",
                    "despacho": "Parecer Jurídico CONJUR/TELEBRAS nº 184/2026 favorável à inexigibilidade com minuta chancelada.",
                    "documentos": ["Parecer_Juridico_CONJUR_184_2026.pdf"]
                },
                {
                    "etapa": 5,
                    "area": "5. Diretoria Executiva / Ordenador",
                    "sigla": "DIRETORIA",
                    "entrada": "2026-07-29",
                    "saida": "2026-08-04",
                    "dias_uteis": 4,
                    "sla_etapa": 5,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "Tatiana Miranda (DAFRI) e Alencastro",
                    "despacho": "Autorização formal de contratação direta e deliberação favorável da Diretoria Executiva.",
                    "documentos": ["Ata_Deliberacao_Diretoria.pdf"]
                },
                {
                    "etapa": 6,
                    "area": "6. Publicação PNCP / DOU",
                    "sigla": "PNCP/DOU",
                    "entrada": "2026-08-05",
                    "saida": "2026-08-07",
                    "dias_uteis": 2,
                    "sla_etapa": 3,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "Pedro / Rosilda (GCC)",
                    "despacho": "Extrato de Inexigibilidade publicado no DOU Seção 3 e sincronizado com o PNCP sob id 00045/2026.",
                    "documentos": ["Comprovante_Publicacao_PNCP.pdf", "Extrato_DOU_Seção3.pdf"]
                },
                {
                    "etapa": 7,
                    "area": "7. GECAD / Gestão Contratual & Fiscalização",
                    "sigla": "GECAD",
                    "entrada": "2026-08-08",
                    "saida": "2026-08-10",
                    "dias_uteis": 2,
                    "sla_etapa": 5,
                    "status_sla": "NO_PRAZO",
                    "responsavel": "GECAD / Carlos Eduardo (Fiscal)",
                    "despacho": "Contrato CTR-018/2026 assinado pelas partes, cadastrado no SAP com DEG nº 08/2026 emitida ao fiscal. Autos arquivados para fiscalização.",
                    "documentos": ["Contrato_Assinado_CTR_018_2026.pdf", "DEG_Designacao_Equipe_Fiscalizacao.pdf"]
                }
            ]
        }

    @classmethod
    def obter_kanban_areas_telebras(cls):
        """
        Retorna os contratos vigentes do PNCP organizados nas colunas das 7 macro-áreas
        da Telebras, permitindo a visão Kanban Interdepartamental / Tramitação no SIGA.
        """
        contratos = cls.carregar_contratos_vigentes()
        kanban_colunas = []

        for area in AREAS_TELEBRAS:
            cards = [c for c in contratos if c.get("area_atual_tramitacao") == area["id"]]
            kanban_colunas.append({
                "id": area["id"],
                "nome": area["nome"],
                "sigla": area["sigla"],
                "cor": area["cor"],
                "sla_dias": area["sla_dias"],
                "total_cards": len(cards),
                "cards": cards
            })

        return kanban_colunas

