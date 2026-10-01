import os
import sys
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# -------------------------------------------------------------
# 1. SETUP & CONFIGURATION
# -------------------------------------------------------------
PLAC_FILE = r"Z:\PLAC-MVP\ANEXOS_PLAC 2026 1.xlsx"
CTR_FILE = r"Z:\PLAC-MVP\15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx"

OUTPUT_EXCEL = r"Z:\PLAC-MVP\AUDITORIA_ADESAO_PLAC_2026_SIGA.xlsx"
OUTPUT_JSON = r"Z:\PLAC-MVP\AUDITORIA_ADESAO_PLAC_2026_SIGA.json"
OUTPUT_PDF = r"Z:\PLAC-MVP\RELATORIO_EXECUTIVO_AUDITORIA_ADESAO_PLAC_SIGA.pdf"

SIGA_LOGIN_URL = "https://intranet2.telebras.com.br/siga/public/app/login"
SIGA_DOC_URL = "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla={sigla}"
SIGA_ANTIGO_URL = "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibirAntigo?sigla={sigla}&"

SIGA_USER = "TB53137"
SIGA_PASS = "#Mr321456"

# -------------------------------------------------------------
# 2. DATA EXTRACTION: PLAC 2026 DEMANDS
# -------------------------------------------------------------
def load_plac_demands(filepath):
    print(f"[*] Carregando demandas do PLAC 2026 de {filepath}...")
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb['BASE_PLAC_2026']
    
    plac_items = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 4:  # header row is index 3 (Row 4)
            continue
        cod = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        if not cod or cod.lower() in ["none", "-", ""]:
            continue
            
        obj = str(row[8]).strip() if len(row) > 8 and row[8] else ""
        ger = str(row[3]).strip() if len(row) > 3 and row[3] else ""
        dir_nome = str(row[4]).strip() if len(row) > 4 and row[4] else ""
        val_2026 = float(row[12]) if len(row) > 12 and isinstance(row[12], (int, float)) else 0.0
        
        plac_items.append({
            "cod_verif": cod,
            "seq": row[2],
            "gerencia": ger,
            "diretoria": dir_nome,
            "objeto": obj,
            "justificativa": str(row[9]).strip() if len(row) > 9 and row[9] else "",
            "data_prevista": str(row[10]) if len(row) > 10 and row[10] else "",
            "valor_2026": val_2026
        })
    wb.close()
    print(f"[+] Total de {len(plac_items)} demandas carregadas do PLAC 2026.")
    return plac_items

# -------------------------------------------------------------
# 3. DATA EXTRACTION: CONTRATOS FINALIZADOS (PLANILHA 15)
# -------------------------------------------------------------
def load_contracts(filepath):
    print(f"[*] Carregando contratos finalizados de {filepath}...")
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb['BASE CTR FINALIZADOS']
    
    contracts = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 4:
            continue
            
        # Col 6: Nº PROCESSO SIGA (Col G in Excel)
        proc_siga = str(row[6]).strip() if len(row) > 6 and row[6] is not None else ""
        # Col 14: Nº CONTRATO (Col O in Excel)
        num_ctr = str(row[14]).strip() if len(row) > 14 and row[14] is not None else ""
        
        if not proc_siga and not num_ctr:
            continue
            
        # Parse contract value
        val_ctr = 0.0
        if len(row) > 29 and row[29] is not None:
            raw_v = row[29]
            if isinstance(raw_v, (int, float)):
                val_ctr = float(raw_v)
            else:
                try:
                    val_ctr = float(str(raw_v).replace("R$", "").replace(".", "").replace(",", ".").strip())
                except:
                    val_ctr = 0.0
                    
        # Parse Dates
        dt_formalizacao = ""
        if len(row) > 20 and row[20]: # Início vigência
            dt_formalizacao = str(row[20])[:10]
        elif len(row) > 19 and row[19]: # Mês assinatura / data
            dt_formalizacao = str(row[19])[:10]
        elif len(row) > 2 and row[2]: # Data início processo
            dt_formalizacao = str(row[2])[:10]

        cod_verif_col = str(row[3]).strip() if len(row) > 3 and row[3] is not None else ""
        if cod_verif_col.lower() in ["none", "-", ""]:
            cod_verif_col = ""
            
        obj = str(row[23]).strip() if len(row) > 23 and row[23] else (str(row[9]).strip() if len(row) > 9 and row[9] else "")

        contracts.append({
            "idx": i + 1,
            "numero_contrato": num_ctr,
            "processo_siga": proc_siga,
            "cod_verif_planilha": cod_verif_col,
            "diretoria": str(row[4]).strip() if len(row) > 4 and row[4] else "N/D",
            "area_requisitante": str(row[5]).strip() if len(row) > 5 and row[5] else "N/D",
            "modalidade": str(row[7]).strip() if len(row) > 7 and row[7] else "N/D",
            "tipo_contrato": str(row[12]).strip() if len(row) > 12 and row[12] else "",
            "fornecedor": str(row[25]).strip() if len(row) > 25 and row[25] else "",
            "data_formalizacao": dt_formalizacao,
            "objeto": obj,
            "valor_contrato": val_ctr
        })
    wb.close()
    print(f"[+] Total de {len(contracts)} contratos carregados da planilha 15.")
    return contracts

# -------------------------------------------------------------
# 4. SIGA CRAWLER & AUDITOR ENGINE
# -------------------------------------------------------------
class SigaAuditor:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False
        self.authenticated = False
        self.cache = {}
        
    def login(self):
        print(f"[*] Autenticando no SIGA da intranet com usuário {self.username}...")
        try:
            r = self.session.post(
                SIGA_LOGIN_URL,
                data={"username": self.username, "password": self.password},
                timeout=15,
                allow_redirects=False
            )
            if "siga-jwt-auth" in self.session.cookies or "JSESSIONID" in self.session.cookies:
                self.authenticated = True
                print("[+] Autenticação no SIGA concluída com sucesso!")
                return True
            else:
                print(f"[-] Falha ao autenticar no SIGA: cookies não emitidos.")
                return False
        except Exception as e:
            print(f"[-] Erro ao conectar ao SIGA: {e}")
            return False

    def inspect_process(self, proc_sigla):
        if not proc_sigla or not proc_sigla.startswith("TLB-PRO-"):
            return {
                "encontrado": False,
                "cod_verif": None,
                "mencao_plac": False,
                "documentos_encontrados": [],
                "resumo": "Processo não informado ou em formato não SIGA"
            }
            
        if proc_sigla in self.cache:
            return self.cache[proc_sigla]
            
        url_doc = SIGA_DOC_URL.format(sigla=proc_sigla)
        result = {
            "encontrado": False,
            "cod_verif": None,
            "mencao_plac": False,
            "documentos_encontrados": [],
            "resumo": ""
        }
        
        try:
            r = self.session.get(url_doc, timeout=12)
            if r.status_code == 200:
                result["encontrado"] = True
                text = r.text
                
                # 1. Regex search for COD VERIF: e.g. 1100-GAB PR_01, 2200-GLOG_05, 3200-GPTC_10, etc.
                matches_cod = re.findall(r'\b\d{4}-[A-Z0-9\s_]+_\d{2}\b', text)
                if matches_cod:
                    result["cod_verif"] = matches_cod[0]
                    
                # 2. Check mentions of PLAC
                if re.search(r'\bplac\b', text, re.IGNORECASE):
                    result["mencao_plac"] = True
                    
                # 3. Parse subdocuments in juntadas table
                soup = BeautifulSoup(text, 'html.parser')
                docs_list = []
                for tr in soup.find_all('tr'):
                    c_text = tr.get_text(separator=' ', strip=True)
                    if any(k in c_text.upper() for k in ['DFD', 'ETP', 'CERTID', 'PLAC', 'TERMO DE REF', 'PARECER']):
                        docs_list.append(c_text[:100])
                result["documentos_encontrados"] = docs_list[:5]
                
                # If not found COD VERIF in main page, check exibirAntigo if process has more history
                if not result["cod_verif"]:
                    sigla_clean = proc_sigla.replace("-", "").replace("/", "")
                    url_antigo = SIGA_ANTIGO_URL.format(sigla=sigla_clean)
                    try:
                        r_antigo = self.session.get(url_antigo, timeout=10)
                        if r_antigo.status_code == 200:
                            m_antigo = re.findall(r'\b\d{4}-[A-Z0-9\s_]+_\d{2}\b', r_antigo.text)
                            if m_antigo:
                                result["cod_verif"] = m_antigo[0]
                            if re.search(r'\bplac\b', r_antigo.text, re.IGNORECASE):
                                result["mencao_plac"] = True
                    except:
                        pass
        except Exception as e:
            result["resumo"] = f"Erro na requisição: {str(e)}"
            
        self.cache[proc_sigla] = result
        return result

# -------------------------------------------------------------
# 5. SEMANTIC MATCHING LOGIC
# -------------------------------------------------------------
STOPWORDS = {
    'para', 'com', 'que', 'dos', 'das', 'uma', 'por', 'sobre', 'sob', 'como', 'mais', 'pelo',
    'pela', 'objeto', 'contratacao', 'prestacao', 'servicos', 'servico', 'aquisicao', 'empresa',
    'especializada', 'atender', 'demandas', 'telebras', 'presente', 'contrato', 'termo', 'aditivo'
}

def normalize_words(text):
    text = text.lower()
    text = re.sub(r'[àáâãä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[íìîï]', 'i', text)
    text = re.sub(r'[óòôõö]', 'o', text)
    text = re.sub(r'[úùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = [w for w in text.split() if len(w) > 3 and w not in STOPWORDS]
    return set(words)

def match_semantic_plac(ctr_obj, ctr_area, ctr_dir, plac_items):
    best_score = 0.0
    best_match = None
    ctr_words = normalize_words(ctr_obj)
    if not ctr_words:
        return None, 0.0
        
    for p in plac_items:
        p_words = normalize_words(p['objeto'])
        if not p_words:
            continue
        common = ctr_words.intersection(p_words)
        if not common:
            continue
            
        score = len(common) / max(len(ctr_words.union(p_words)), 1)
        
        # Boost if matching Area / Gerência
        area_clean = ctr_area.upper().replace("-", "").replace(" ", "")
        ger_clean = p['gerencia'].upper().replace("-", "").replace(" ", "")
        if area_clean and ger_clean and (area_clean in ger_clean or ger_clean in area_clean):
            score += 0.28
            
        # Boost if matching Diretoria
        dir_clean = ctr_dir.upper().replace("-", "").replace(" ", "")
        p_dir = p['diretoria'].upper().replace("-", "").replace(" ", "")
        if dir_clean and p_dir and (dir_clean in p_dir or p_dir in dir_clean):
            score += 0.12
            
        if score > best_score:
            best_score = score
            best_match = p
            
    return best_match, best_score

# -------------------------------------------------------------
# 6. PIPELINE AUDITORIA COMPLETA
# -------------------------------------------------------------
def run_audit():
    plac_demands = load_plac_demands(PLAC_FILE)
    contracts = load_contracts(CTR_FILE)
    
    auditor = SigaAuditor(SIGA_USER, SIGA_PASS)
    auditor.login()
    
    # Unique processes to audit in SIGA
    unique_procs = list(set([c['processo_siga'] for c in contracts if c['processo_siga'].startswith("TLB-PRO-")]))
    print(f"[*] Iniciando varredura no SIGA de {len(unique_procs)} processos únicos...")
    
    # Multi-threaded fetching
    completed_count = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_proc = {executor.submit(auditor.inspect_process, p): p for p in unique_procs}
        for future in as_completed(future_to_proc):
            completed_count += 1
            if completed_count % 20 == 0 or completed_count == len(unique_procs):
                print(f"  [>] Processos auditados no SIGA: {completed_count}/{len(unique_procs)}...")
                
    print("[+] Varredura de processos no SIGA finalizada!")
    
    # 7. Classification and Consolidation
    print("[*] Consolidando resultados e aplicando matriz de adesão ao PLAC...")
    audited_contracts = []
    
    for c in contracts:
        proc = c['processo_siga']
        ctr = c['numero_contrato']
        obj = c['objeto']
        area = c['area_requisitante']
        diretoria = c['diretoria']
        
        siga_res = auditor.cache.get(proc, {})
        cod_siga = siga_res.get("cod_verif")
        cod_planilha = c['cod_verif_planilha']
        
        cod_final = None
        status_plac = ""
        categoria_cod = ""
        evidencia = ""
        objeto_plac_ref = ""
        
        # Priority 1: COD VERIF found in SIGA process documents
        if cod_siga:
            cod_final = cod_siga
            status_plac = "PREVISTA (COM COD VERIF NO SIGA)"
            categoria_cod = "PREVISTA_REGULAR"
            evidencia = f"Código {cod_siga} comprovado nos autos/expedientes do SIGA."
            # Match item in PLAC 2026
            p_match = next((p for p in plac_demands if p['cod_verif'] == cod_siga), None)
            if p_match:
                objeto_plac_ref = f"{p_match['objeto']} (R$ {p_match['valor_2026']:,.2f})"
            else:
                objeto_plac_ref = "Item planejado em ciclo anterior do PLAC (2024-2025)."

        # Priority 2: COD VERIF registered in contract spreadsheet (Col 3)
        elif cod_planilha and cod_planilha.upper() != "NÃO PREVISTO":
            cod_final = cod_planilha
            status_plac = "PREVISTA (COM COD VERIF VINCULADO)"
            categoria_cod = "PREVISTA_REGULAR"
            evidencia = f"Código {cod_planilha} registrado no cadastro da GCC."
            p_match = next((p for p in plac_demands if p['cod_verif'] == cod_planilha), None)
            if p_match:
                objeto_plac_ref = f"{p_match['objeto']} (R$ {p_match['valor_2026']:,.2f})"
            else:
                objeto_plac_ref = "Item cadastrado no PLAC."

        # Priority 3: Semantic Match with PLAC 2026
        else:
            best_p, score = match_semantic_plac(obj, area, diretoria, plac_demands)
            if best_p and score >= 0.28:
                cod_final = best_p['cod_verif']
                status_plac = "PREVISTA (VINCULADA POR OBJETO NO PLAC)"
                categoria_cod = "PREVISTA_SEM_RITO"
                evidencia = f"Demanda compatível com {best_p['cod_verif']} ({best_p['gerencia']}), mas omitiu inserção formal do rito no SIGA (Similaridade: {score*100:.1f}%)."
                objeto_plac_ref = f"{best_p['objeto']} (Previsto: R$ {best_p['valor_2026']:,.2f})"
            else:
                status_plac = "NÃO PREVISTA (EXTRAORDINÁRIA)"
                categoria_cod = "NAO_PREVISTA"
                evidencia = "Contratação extraordinária sem lastro correspondente no PLAC 2026."
                objeto_plac_ref = "Sem correspondência no planejamento."

        audited_contracts.append({
            "idx": c['idx'],
            "numero_contrato": ctr,
            "processo_siga": proc,
            "diretoria": diretoria,
            "area_requisitante": area,
            "modalidade": c['modalidade'],
            "tipo_contrato": c['tipo_contrato'],
            "fornecedor": c['fornecedor'],
            "data_formalizacao": c['data_formalizacao'],
            "valor_contrato": c['valor_contrato'],
            "status_plac": status_plac,
            "categoria_cod": categoria_cod,
            "cod_verif": cod_final if cod_final else "N/D",
            "objeto_contratado": obj,
            "objeto_plac_ref": objeto_plac_ref,
            "evidencia_auditoria": evidencia,
            "siga_mencao_plac": siga_res.get("mencao_plac", False)
        })

    # Summary Statistics
    total_ctrs = len(audited_contracts)
    val_total = sum(c['valor_contrato'] for c in audited_contracts)
    
    prev_regular = [c for c in audited_contracts if c['categoria_cod'] == "PREVISTA_REGULAR"]
    prev_sem_rito = [c for c in audited_contracts if c['categoria_cod'] == "PREVISTA_SEM_RITO"]
    nao_prev = [c for c in audited_contracts if c['categoria_cod'] == "NAO_PREVISTA"]
    
    val_prev_regular = sum(c['valor_contrato'] for c in prev_regular)
    val_prev_sem_rito = sum(c['valor_contrato'] for c in prev_sem_rito)
    val_nao_prev = sum(c['valor_contrato'] for c in nao_prev)
    
    taxa_adesao_formal = (len(prev_regular) / total_ctrs * 100) if total_ctrs else 0.0
    taxa_adesao_global = ((len(prev_regular) + len(prev_sem_rito)) / total_ctrs * 100) if total_ctrs else 0.0
    taxa_nao_prevista = (len(nao_prev) / total_ctrs * 100) if total_ctrs else 0.0

    print("\n" + "="*70)
    print("RESUMO EXECUTIVO DA AUDITORIA DE ADESÃO AO PLAC")
    print("="*70)
    print(f"Total de Contratos Auditados: {total_ctrs}")
    print(f"Volume Financeiro Total Contratado: R$ {val_total:,.2f}")
    print(f"1. Previstas Regulares (com COD VERIF no SIGA/cadastro): {len(prev_regular)} ({taxa_adesao_formal:.1f}%) | R$ {val_prev_regular:,.2f}")
    print(f"2. Previstas por Objeto (Omitiram rito no SIGA): {len(prev_sem_rito)} ({len(prev_sem_rito)/total_ctrs*100:.1f}%) | R$ {val_prev_sem_rito:,.2f}")
    print(f"3. Não Previstas (Extraordinárias): {len(nao_prev)} ({taxa_nao_prevista:.1f}%) | R$ {val_nao_prev:,.2f}")
    print(f"TAXA GLOBAL DE CONTRATAÇÕES PLANEJADAS NO PLAC: {taxa_adesao_global:.1f}%")
    print("="*70)

    # -------------------------------------------------------------
    # 7. EXPORT TO JSON
    # -------------------------------------------------------------
    export_data = {
        "metadados": {
            "data_auditoria": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "responsavel_auditoria": "Robô SIGA / GCC - Gerência de Compras e Contratos",
            "base_contratos": CTR_FILE,
            "base_plac": PLAC_FILE,
            "total_contratos": total_ctrs,
            "valor_total_contratado": val_total,
            "indicadores": {
                "taxa_adesao_formal_pct": round(taxa_adesao_formal, 2),
                "taxa_aderencia_global_pct": round(taxa_adesao_global, 2),
                "taxa_extraordinarias_pct": round(taxa_nao_prevista, 2),
                "qtd_previstas_formal": len(prev_regular),
                "val_previstas_formal": val_prev_regular,
                "qtd_previstas_objeto": len(prev_sem_rito),
                "val_previstas_objeto": val_prev_sem_rito,
                "qtd_nao_previstas": len(nao_prev),
                "val_nao_previstas": val_nao_prev
            }
        },
        "contratos": audited_contracts
    }
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Dataset JSON exportado em: {OUTPUT_JSON}")

    # -------------------------------------------------------------
    # 8. EXPORT TO EXCEL COM FORMATAÇÃO INSTITUCIONAL
    # -------------------------------------------------------------
    export_to_excel(audited_contracts, export_data["metadados"])
    
    # -------------------------------------------------------------
    # 9. GENERATE EXECUTIVE PDF REPORT
    # -------------------------------------------------------------
    generate_pdf_report(audited_contracts, export_data["metadados"])

# -------------------------------------------------------------
# 8. EXCEL BUILDER
# -------------------------------------------------------------
def export_to_excel(contracts, meta):
    print(f"[*] Gerando pasta de trabalho estruturada em {OUTPUT_EXCEL}...")
    wb = openpyxl.Workbook()
    
    # Styles
    navy_header_fill = PatternFill(start_color="002B49", end_color="002B49", fill_type="solid")
    blue_sub_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    green_fill = PatternFill(start_color="E6F4EA", end_color="E6F4EA", fill_type="solid")
    yellow_fill = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
    red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_normal = Font(name="Calibri", size=10)
    
    thin_border = Border(
        left=Side(style='thin', color='CCCCCC'),
        right=Side(style='thin', color='CCCCCC'),
        top=Side(style='thin', color='CCCCCC'),
        bottom=Side(style='thin', color='CCCCCC')
    )
    
    # Sheet 1: RESUMO_EXECUTIVO
    ws_res = wb.active
    ws_res.title = "RESUMO_EXECUTIVO"
    ws_res.views.sheetView[0].showGridLines = True
    
    ws_res.cell(row=2, column=2, value="AUDITORIA EXECUTIVA DE ADESÃO AO PLAC VIA SIGA").font = Font(size=16, bold=True, color="002B49")
    ws_res.cell(row=3, column=2, value=f"Data da Auditoria: {meta['data_auditoria']} | Responsável: GCC / Governança Corporativa").font = Font(size=10, italic=True, color="555555")
    
    # KPIs Table
    headers_kpi = ["Indicador de Auditoria", "Quantidade de Contratos", "Participação (%)", "Volume Financeiro (R$)", "Impacto Orçamentário (%)"]
    for col_idx, h in enumerate(headers_kpi, start=2):
        c = ws_res.cell(row=5, column=col_idx, value=h)
        c.fill = navy_header_fill
        c.font = font_header
        c.alignment = Alignment(horizontal="center", vertical="center")
        
    kpis_data = [
        ("1. Contratações Previstas Regulares (Com COD VERIF no SIGA/Cadastro)", meta['indicadores']['qtd_previstas_formal'], f"{meta['indicadores']['taxa_adesao_formal_pct']}%", meta['indicadores']['val_previstas_formal'], f"{meta['indicadores']['val_previstas_formal']/meta['valor_total_contratado']*100:.1f}%"),
        ("2. Contratações Previstas por Objeto (Omitiram rito no SIGA)", meta['indicadores']['qtd_previstas_objeto'], f"{meta['indicadores']['qtd_previstas_objeto']/meta['total_contratos']*100:.1f}%", meta['indicadores']['val_previstas_objeto'], f"{meta['indicadores']['val_previstas_objeto']/meta['valor_total_contratado']*100:.1f}%"),
        ("3. Contratações Não Previstas (Extraordinárias / Fora do PLAC)", meta['indicadores']['qtd_nao_previstas'], f"{meta['indicadores']['taxa_extraordinarias_pct']}%", meta['indicadores']['val_nao_previstas'], f"{meta['indicadores']['val_nao_previstas']/meta['valor_total_contratado']*100:.1f}%"),
        ("TOTAL GERAL DE CONTRATAÇÕES AUDITADAS", meta['total_contratos'], "100.0%", meta['valor_total_contratado'], "100.0%")
    ]
    
    for r_idx, row_vals in enumerate(kpis_data, start=6):
        is_total = (r_idx == 9)
        for c_idx, val in enumerate(row_vals, start=2):
            cell = ws_res.cell(row=r_idx, column=c_idx, value=val)
            cell.font = font_bold if is_total else font_normal
            cell.border = thin_border
            if c_idx == 2:
                cell.alignment = Alignment(horizontal="left")
            elif c_idx in [3, 4, 6]:
                cell.alignment = Alignment(horizontal="center")
            elif c_idx == 5:
                cell.alignment = Alignment(horizontal="right")
                cell.number_format = '#,##0.00'
            if is_total:
                cell.fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    ws_res.column_dimensions['B'].width = 65
    ws_res.column_dimensions['C'].width = 25
    ws_res.column_dimensions['D'].width = 18
    ws_res.column_dimensions['E'].width = 25
    ws_res.column_dimensions['F'].width = 25

    # Sheet 2: BASE_CONTRATOS_AUDITADOS
    ws_base = wb.create_sheet(title="CONTRATOS_AUDITADOS")
    ws_base.views.sheetView[0].showGridLines = True
    
    headers_base = [
        "Item", "Nº Contrato", "Nº Processo SIGA", "Diretoria", "Área Demandante", 
        "Modalidade", "Data Formalização", "Valor Contrato (R$)", "Status no PLAC", 
        "Código Verificador (COD VERIF)", "Fornecedor", "Objeto Contratado", "Referência PLAC 2026", "Evidência / Diagnóstico SIGA"
    ]
    
    for col_idx, h in enumerate(headers_base, start=1):
        cell = ws_base.cell(row=1, column=col_idx, value=h)
        cell.fill = navy_header_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for r_idx, c in enumerate(contracts, start=2):
        row_data = [
            c['idx'], c['numero_contrato'], c['processo_siga'], c['diretoria'], c['area_requisitante'],
            c['modalidade'], c['data_formalizacao'], c['valor_contrato'], c['status_plac'],
            c['cod_verif'], c['fornecedor'], c['objeto_contratado'], c['objeto_plac_ref'], c['evidencia_auditoria']
        ]
        
        status_fill = None
        if c['categoria_cod'] == "PREVISTA_REGULAR":
            status_fill = green_fill
        elif c['categoria_cod'] == "PREVISTA_SEM_RITO":
            status_fill = yellow_fill
        else:
            status_fill = red_fill
            
        for col_idx, val in enumerate(row_data, start=1):
            cell = ws_base.cell(row=r_idx, column=col_idx, value=val)
            cell.font = font_normal
            cell.border = thin_border
            if col_idx == 8:
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx in [1, 6, 7]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx == 9:
                cell.fill = status_fill
                cell.alignment = Alignment(horizontal="center")
                cell.font = font_bold
            else:
                cell.alignment = Alignment(horizontal="left")

    col_widths = {
        'A': 8, 'B': 22, 'C': 22, 'D': 12, 'E': 18, 'F': 22, 'G': 18, 
        'H': 20, 'I': 38, 'J': 28, 'K': 32, 'L': 50, 'M': 50, 'N': 55
    }
    for col_letter, width in col_widths.items():
        ws_base.column_dimensions[col_letter].width = width

    # Sheet 3: ADESAO_POR_DIRETORIA
    ws_dir = wb.create_sheet(title="ADESAO_POR_DIRETORIA")
    ws_dir.views.sheetView[0].showGridLines = True
    
    headers_dir = ["Diretoria", "Total Contratos", "Previstas Regulares", "Previstas por Objeto", "Não Previstas", "Taxa Formal (%)", "Taxa Global Aderência (%)", "Valor Total (R$)"]
    for col_idx, h in enumerate(headers_dir, start=1):
        cell = ws_dir.cell(row=1, column=col_idx, value=h)
        cell.fill = blue_sub_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    # Group by Diretoria
    dirs = {}
    for c in contracts:
        d = c['diretoria'] if c['diretoria'] else "N/D"
        if d not in dirs:
            dirs[d] = {"total": 0, "regular": 0, "sem_rito": 0, "nao_prev": 0, "valor": 0.0}
        dirs[d]["total"] += 1
        dirs[d]["valor"] += c['valor_contrato']
        if c['categoria_cod'] == "PREVISTA_REGULAR":
            dirs[d]["regular"] += 1
        elif c['categoria_cod'] == "PREVISTA_SEM_RITO":
            dirs[d]["sem_rito"] += 1
        else:
            dirs[d]["nao_prev"] += 1

    for r_idx, (d_name, stats) in enumerate(sorted(dirs.items(), key=lambda x: -x[1]['valor']), start=2):
        tx_formal = (stats["regular"] / stats["total"] * 100) if stats["total"] else 0.0
        tx_global = ((stats["regular"] + stats["sem_rito"]) / stats["total"] * 100) if stats["total"] else 0.0
        row_vals = [
            d_name, stats["total"], stats["regular"], stats["sem_rito"], stats["nao_prev"],
            f"{tx_formal:.1f}%", f"{tx_global:.1f}%", stats["valor"]
        ]
        for col_idx, val in enumerate(row_vals, start=1):
            cell = ws_dir.cell(row=r_idx, column=col_idx, value=val)
            cell.font = font_normal
            cell.border = thin_border
            if col_idx == 8:
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx >= 2:
                cell.alignment = Alignment(horizontal="center")

    for col_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        ws_dir.column_dimensions[col_letter].width = 24

    # Sheet 4: ADESAO_POR_GERENCIA
    ws_ger = wb.create_sheet(title="ADESAO_POR_GERENCIA")
    ws_ger.views.sheetView[0].showGridLines = True
    
    headers_ger = ["Área Requisitante (Gerência)", "Diretoria", "Total Contratos", "Previstas Regulares", "Previstas por Objeto", "Não Previstas", "Taxa Aderência Global (%)", "Valor Total (R$)"]
    for col_idx, h in enumerate(headers_ger, start=1):
        cell = ws_ger.cell(row=1, column=col_idx, value=h)
        cell.fill = navy_header_fill
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    gers = {}
    for c in contracts:
        g = c['area_requisitante'] if c['area_requisitante'] else "N/D"
        if g not in gers:
            gers[g] = {"dir": c['diretoria'], "total": 0, "regular": 0, "sem_rito": 0, "nao_prev": 0, "valor": 0.0}
        gers[g]["total"] += 1
        gers[g]["valor"] += c['valor_contrato']
        if c['categoria_cod'] == "PREVISTA_REGULAR":
            gers[g]["regular"] += 1
        elif c['categoria_cod'] == "PREVISTA_SEM_RITO":
            gers[g]["sem_rito"] += 1
        else:
            gers[g]["nao_prev"] += 1

    for r_idx, (g_name, stats) in enumerate(sorted(gers.items(), key=lambda x: -x[1]['valor']), start=2):
        tx_global = ((stats["regular"] + stats["sem_rito"]) / stats["total"] * 100) if stats["total"] else 0.0
        row_vals = [
            g_name, stats["dir"], stats["total"], stats["regular"], stats["sem_rito"], stats["nao_prev"],
            f"{tx_global:.1f}%", stats["valor"]
        ]
        for col_idx, val in enumerate(row_vals, start=1):
            cell = ws_ger.cell(row=r_idx, column=col_idx, value=val)
            cell.font = font_normal
            cell.border = thin_border
            if col_idx == 8:
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal="right")
            elif col_idx >= 3:
                cell.alignment = Alignment(horizontal="center")

    for col_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        ws_ger.column_dimensions[col_letter].width = 24

    wb.save(OUTPUT_EXCEL)
    print(f"[+] Pasta de trabalho Excel salva em: {OUTPUT_EXCEL}")

# -------------------------------------------------------------
# 9. NUMBERED CANVAS FOR REPORTLAB (PAGE X OF Y)
# -------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 565, "TELEBRAS — Relatório Executivo de Auditoria de Adesão das Contratações ao PLAC")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 558, 806, 558)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 40, 806, 40)
        
        self.drawString(36, 28, f"Documento Corporativo SIGA / GCC — Emitido eletronicamente em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(806, 28, page_text)
        self.restoreState()

# -------------------------------------------------------------
# 10. EXECUTIVE PDF REPORT BUILDER
# -------------------------------------------------------------
def generate_pdf_report(contracts, meta):
    print(f"[*] Gerando Relatório Executivo em PDF: {OUTPUT_PDF}...")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=landscape(A4),
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#002B49")
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569")
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#002B49"),
        spaceAfter=6,
        spaceBefore=12
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )
    status_reg = ParagraphStyle(
        'StatusReg',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#166534")
    )
    status_sem_rito = ParagraphStyle(
        'StatusSemRito',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#854D0E")
    )
    status_nao_prev = ParagraphStyle(
        'StatusNaoPrev',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#991B1B")
    )

    story = []

    # Title & Header
    story.append(Paragraph("TELECOMUNICAÇÕES BRASILEIRAS S.A. — TELEBRAS", subtitle_style))
    story.append(Paragraph("RELATÓRIO EXECUTIVO DE AUDITORIA DE ADESÃO AO PLAC", title_style))
    story.append(Paragraph(
        "Rastreamento de Conformidade dos Contratos Formalizados frente ao Plano Anual de Contratações (2024–2026) e Validação de Rito nos Processos do SIGA",
        subtitle_style
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#002B49"), spaceAfter=14))

    # Executive Overview
    story.append(Paragraph("1. Painel Executivo de Conformidade e Aderência Global", h1_style))
    
    kpis = meta['indicadores']
    card_data = [
        [
            Paragraph(f"<b>TOTAL CONTRATOS</b><br/><font size=14 color='#002B49'><b>{meta['total_contratos']}</b></font><br/><font size=7 color='#64748B'>100% Auditados no SIGA</font>", body_style),
            Paragraph(f"<b>VALOR TOTAL CONTRATADO</b><br/><font size=13 color='#002B49'><b>R$ {meta['valor_total_contratado']:,.2f}</b></font><br/><font size=7 color='#64748B'>Volume Financeiro</font>", body_style),
            Paragraph(f"<b>ADESÃO FORMAL (SIGA)</b><br/><font size=14 color='#16A34A'><b>{kpis['taxa_adesao_formal_pct']}%</b></font><br/><font size=7 color='#64748B'>{kpis['qtd_previstas_formal']} CTRs com COD VERIF</font>", body_style),
            Paragraph(f"<b>ADERÊNCIA GLOBAL (PLAC)</b><br/><font size=14 color='#2563EB'><b>{kpis['taxa_aderencia_global_pct']}%</b></font><br/><font size=7 color='#64748B'>{kpis['qtd_previstas_formal']+kpis['qtd_previstas_objeto']} CTRs Planejados</font>", body_style),
            Paragraph(f"<b>NÃO PREVISTAS (EXTRAORD.)</b><br/><font size=14 color='#DC2626'><b>{kpis['taxa_extraordinarias_pct']}%</b></font><br/><font size=7 color='#64748B'>{kpis['qtd_nao_previstas']} CTRs sem lastro PLAC</font>", body_style),
        ]
    ]
    t_cards = Table(card_data, colWidths=[150, 160, 150, 150, 160])
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 14))

    # Diagnóstico e Resumo das 3 Categorias
    story.append(Paragraph("2. Diagnóstico Estratégico por Categoria de Enquadramento", h1_style))
    cat_summary = [
        [
            Paragraph("<b>Categoria de Adesão ao PLAC</b>", table_cell_bold),
            Paragraph("<b>Qtd CTRs</b>", table_cell_bold),
            Paragraph("<b>Part. (%)</b>", table_cell_bold),
            Paragraph("<b>Volume Financeiro (R$)</b>", table_cell_bold),
            Paragraph("<b>Diagnóstico de Governança & Rito Processual</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>1. Previstas Regulares</b><br/><font color='#16A34A' size=6.5>Conforme com rito pleno</font>", table_cell),
            Paragraph(str(kpis['qtd_previstas_formal']), table_cell_bold),
            Paragraph(f"{kpis['taxa_adesao_formal_pct']}%", table_cell),
            Paragraph(f"R$ {kpis['val_previstas_formal']:,.2f}", table_cell),
            Paragraph("Contratações com <b>COD VERIF</b> expressamente registrado nos autos do SIGA (DFD/ETP) ou no cadastro da GCC. Rito 100% cumprido conforme Diretriz do PLAC e Art. 12 da Lei 13.303/2016.", table_cell)
        ],
        [
            Paragraph("<b>2. Previstas por Objeto</b><br/><font color='#854D0E' size=6.5>Falha de rito no SIGA</font>", table_cell),
            Paragraph(str(kpis['qtd_previstas_objeto']), table_cell_bold),
            Paragraph(f"{kpis['qtd_previstas_objeto']/meta['total_contratos']*100:.1f}%", table_cell),
            Paragraph(f"R$ {kpis['val_previstas_objeto']:,.2f}", table_cell),
            Paragraph("Demandas contempladas no orçamento e planejamento do PLAC 2026, porém as áreas demandantes <b>omitiram a vinculação formal do Código Verificador nos autos do SIGA</b>. Demonstra maturidade de planejamento, mas com necessidade de capacitação no rito operacional.", table_cell)
        ],
        [
            Paragraph("<b>3. Não Previstas</b><br/><font color='#991B1B' size=6.5>Extraordinárias / Fora do PLAC</font>", table_cell),
            Paragraph(str(kpis['qtd_nao_previstas']), table_cell_bold),
            Paragraph(f"{kpis['taxa_extraordinarias_pct']}%", table_cell),
            Paragraph(f"R$ {kpis['val_nao_previstas']:,.2f}", table_cell),
            Paragraph("Contratações não constantes no planejamento original do PLAC. Exigem monitoramento preventivo da GCC para mitigar custos de oportunidade e compras fragmentadas/emergenciais.", table_cell)
        ],
        [
            Paragraph("<b>TOTAL GERAL</b>", table_cell_bold),
            Paragraph(str(meta['total_contratos']), table_cell_bold),
            Paragraph("100.0%", table_cell_bold),
            Paragraph(f"R$ {meta['valor_total_contratado']:,.2f}", table_cell_bold),
            Paragraph("Base consolidada da totalidade dos contratos formalizados da Telebras.", table_cell_bold)
        ]
    ]
    t_cat = Table(cat_summary, colWidths=[150, 55, 60, 115, 390])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#002B49")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 14))

    # Aderência por Diretoria
    story.append(Paragraph("3. Desempenho e Taxa de Aderência por Diretoria Executiva", h1_style))
    dirs = {}
    for c in contracts:
        d = c['diretoria'] if c['diretoria'] else "N/D"
        if d not in dirs:
            dirs[d] = {"total": 0, "regular": 0, "sem_rito": 0, "nao_prev": 0, "valor": 0.0}
        dirs[d]["total"] += 1
        dirs[d]["valor"] += c['valor_contrato']
        if c['categoria_cod'] == "PREVISTA_REGULAR":
            dirs[d]["regular"] += 1
        elif c['categoria_cod'] == "PREVISTA_SEM_RITO":
            dirs[d]["sem_rito"] += 1
        else:
            dirs[d]["nao_prev"] += 1

    dir_rows = [
        [
            Paragraph("<b>Diretoria</b>", table_cell_bold),
            Paragraph("<b>Total CTRs</b>", table_cell_bold),
            Paragraph("<b>Previstas (Regulares)</b>", table_cell_bold),
            Paragraph("<b>Previstas (Por Objeto)</b>", table_cell_bold),
            Paragraph("<b>Não Previstas</b>", table_cell_bold),
            Paragraph("<b>Adesão Formal (%)</b>", table_cell_bold),
            Paragraph("<b>Aderência Global (%)</b>", table_cell_bold),
            Paragraph("<b>Volume Total (R$)</b>", table_cell_bold)
        ]
    ]
    for d_name, s in sorted(dirs.items(), key=lambda x: -x[1]['valor']):
        tx_f = (s["regular"] / s["total"] * 100) if s["total"] else 0.0
        tx_g = ((s["regular"] + s["sem_rito"]) / s["total"] * 100) if s["total"] else 0.0
        dir_rows.append([
            Paragraph(f"<b>{d_name}</b>", table_cell),
            Paragraph(str(s["total"]), table_cell),
            Paragraph(str(s["regular"]), table_cell),
            Paragraph(str(s["sem_rito"]), table_cell),
            Paragraph(str(s["nao_prev"]), table_cell),
            Paragraph(f"{tx_f:.1f}%", table_cell_bold if tx_f >= 50 else table_cell),
            Paragraph(f"<b>{tx_g:.1f}%</b>", table_cell_bold),
            Paragraph(f"R$ {s['valor']:,.2f}", table_cell)
        ])

    t_dir = Table(dir_rows, colWidths=[130, 65, 95, 95, 75, 85, 95, 130])
    t_dir.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_dir)
    story.append(PageBreak())

    # Detailed Table: All Contracts
    story.append(Paragraph("4. Relação Completa dos Contratos Auditados e Mapeamento de Processos SIGA", h1_style))
    story.append(Paragraph(
        "Demonstrativo analítico contendo o Número do Processo SIGA, Número do Contrato/Empenho, Área Demandante, Data de Formalização, Valor do Contrato, Código Verificador e Status no PLAC.",
        subtitle_style
    ))
    story.append(Spacer(1, 8))

    tbl_headers = [
        Paragraph("<b>Nº CTR / Empenho</b>", table_cell_bold),
        Paragraph("<b>Nº Processo SIGA</b>", table_cell_bold),
        Paragraph("<b>Área Demand.</b>", table_cell_bold),
        Paragraph("<b>Data Formaliz.</b>", table_cell_bold),
        Paragraph("<b>Valor Contrato (R$)</b>", table_cell_bold),
        Paragraph("<b>Status no PLAC</b>", table_cell_bold),
        Paragraph("<b>COD VERIF</b>", table_cell_bold),
        Paragraph("<b>Objeto Contratado (Resumo)</b>", table_cell_bold)
    ]
    
    table_rows = [tbl_headers]
    for c in contracts:
        st_p = table_cell
        if c['categoria_cod'] == "PREVISTA_REGULAR":
            st_p = status_reg
        elif c['categoria_cod'] == "PREVISTA_SEM_RITO":
            st_p = status_sem_rito
        else:
            st_p = status_nao_prev
            
        table_rows.append([
            Paragraph(f"<b>{c['numero_contrato']}</b>", table_cell),
            Paragraph(c['processo_siga'], table_cell),
            Paragraph(f"{c['area_requisitante']}<br/><font color='#64748B' size=6>{c['diretoria']}</font>", table_cell),
            Paragraph(c['data_formalizacao'], table_cell),
            Paragraph(f"R$ {c['valor_contrato']:,.2f}", table_cell),
            Paragraph(c['status_plac'], st_p),
            Paragraph(f"<b>{c['cod_verif']}</b>", table_cell),
            Paragraph(c['objeto_contratado'][:75] + ("..." if len(c['objeto_contratado']) > 75 else ""), table_cell)
        ])

    t_all = Table(table_rows, colWidths=[95, 95, 65, 65, 80, 130, 85, 155], repeatRows=1)
    t_all.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#002B49")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_all)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Relatório Executivo PDF gerado com sucesso em: {OUTPUT_PDF}")

# -------------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------------
if __name__ == '__main__':
    run_audit()
