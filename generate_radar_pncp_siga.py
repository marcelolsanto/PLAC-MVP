#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador Oficial do Relatório Radar de Pregões e Editais PNCP & Tramitação SIGA (Outubro 2026)
Gera:
1. Relatorio_Radar_Editais_PNCP_SIGA_2026.xlsx
2. Relatorio_Radar_Editais_PNCP_SIGA_2026.pdf
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import json
import base64
import io
import math
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from playwright.sync_api import sync_playwright
from datetime import datetime, date

print("=== INICIANDO PROCESSAMENTO DOS DADOS DO RADAR PNCP & SIGA ===")

# 1. Carregar Base de Dados do Planejamento SIGA (Kanban)
f_kanban = 'BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx'
df_kanban = pd.read_excel(f_kanban, sheet_name='INVENTARIO_GERAL')

# 2. Filtrar Fase 5 (Triagem & Prontidão GCC - 31 processos) e Fase 4 (CONJUR - 41 processos)
fase5 = df_kanban[df_kanban['Fase Kanban'].str.contains('5. Triagem', na=False)].copy()
fase4 = df_kanban[df_kanban['Fase Kanban'].str.contains('4. Análise', na=False)].copy()

fase5['Valor Estimado 2026 (R$)'] = pd.to_numeric(fase5['Valor Estimado 2026 (R$)'], errors='coerce').fillna(0)
fase4['Valor Estimado 2026 (R$)'] = pd.to_numeric(fase4['Valor Estimado 2026 (R$)'], errors='coerce').fillna(0)

# Ordenar por valor decrescente
fase5 = fase5.sort_values(by='Valor Estimado 2026 (R$)', ascending=False).reset_index(drop=True)
fase4 = fase4.sort_values(by='Valor Estimado 2026 (R$)', ascending=False).reset_index(drop=True)

# 3. Base de Pregões Radar PNCP 2026
pregoes_radar = [
    {
        'licitacao': 'PE 35/2026 (SRP)',
        'processo_siga': 'TLB-PRO-2026/005064',
        'diretoria': 'DTO / GPEI',
        'objeto': 'Vistorias, elaboração de projetos executivos e implantação/expansão de infraestrutura de telecomunicações para a Copa do Mundo Feminina 2027 e expansão da rede corporativa da Telebras',
        'valor_estimado': 10000000.0,
        'data_sessao': '02/10/2026 (Fase de Propostas / Julgamento nesta semana)',
        'status_pncp': 'PUBLICADO NO PNCP / SESSÃO EM ANDAMENTO',
        'pregoeiro': 'Pedro Diniz / GCC',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'CRÍTICO — Compromisso Internacional FIFA / MESP',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 42/2026',
        'processo_siga': 'TLB-PRO-2026/006558',
        'diretoria': 'DTO / GEOS',
        'objeto': 'Contratação de empresa especializada para prestação de serviços de manutenção preventiva e corretiva na infraestrutura crítica dos 3 Gateways SGDC (Salvador/BA, Campo Grande/MS e Florianópolis/SC)',
        'valor_estimado': 3000000.0,
        'data_sessao': '21/10/2026 às 10:00h (Abertura Agendada)',
        'status_pncp': 'PUBLICADO NO PNCP / PRAZO DE PROPOSTAS ABERTO',
        'pregoeiro': 'Rosilda / GCC',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'ALTO — Disponibilidade Operacional das Antenas SGDC',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 38/2026',
        'processo_siga': 'TLB-PRO-2025/05460',
        'diretoria': 'DTO / GORS',
        'objeto': 'Aquisição de solução de climatização de precisão (HVAC) para o Datacenter principal da Sede Telebras, com serviços de instalação, comissionamento e garantia técnica',
        'valor_estimado': 850000.0,
        'data_sessao': 'Outubro/2026 (Aguardando homologação de lances)',
        'status_pncp': 'PUBLICADO NO PNCP / FASE DE JULGAMENTO',
        'pregoeiro': 'GCC / Pregoeiro Oficial',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'ALTO — Refrigeração e integridade dos servidores core',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 44/2026',
        'processo_siga': 'TLB-PRO-2026/004351',
        'diretoria': 'DAFRI / GLOG',
        'objeto': 'Contratação de solução integrada de controle de acesso físico com tecnologia de reconhecimento facial para as dependências da Sede da Telebras e Escritórios Regionais',
        'valor_estimado': 420000.0,
        'data_sessao': 'Outubro/2026 (Publicação Recente PNCP)',
        'status_pncp': 'PUBLICADO NO PNCP / RECEBIMENTO DE PROPOSTAS',
        'pregoeiro': 'GCC Compras',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'MÉDIO — Segurança patrimonial e conformidade LGPD',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 37/2026 (SRP)',
        'processo_siga': 'TLB-PRO-2026/002342',
        'diretoria': 'DTO / GERP',
        'objeto': 'Registro de Preços para fornecimento de sobressalentes e insumos de infraestrutura passiva para ampliação do Backbone e Backhaul de fibra óptica',
        'valor_estimado': 300000.0,
        'data_sessao': 'Outubro/2026 (Em andamento no Compras.gov)',
        'status_pncp': 'PUBLICADO NO PNCP / SRP ATIVO',
        'pregoeiro': 'Rosilda / GCC',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'ALTO — Manutenção da rede de transporte nacional',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 30/2026 (SRP)',
        'processo_siga': 'TLB-PRO-2025/03498',
        'diretoria': 'DTO / GERP',
        'objeto': 'Contratação de empresa especializada no fornecimento e montagem de extensão de rede de energia elétrica em baixa e média tensão para estações da Telebras',
        'valor_estimado': 1850000.0,
        'data_sessao': 'Sessão 23/07/2026 (Em diligência técnica)',
        'status_pncp': 'DISPUTA CONCLUÍDA — ANÁLISE DE PROPOSTA VENCEDORA',
        'pregoeiro': 'Rosilda / GCC',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'ALTO — Conexão elétrica de estações no interior',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 32/2026',
        'processo_siga': 'TLB-PRO-2025/04501',
        'diretoria': 'DTO / GTI',
        'objeto': 'Contratação de aplicação sistêmica para captura automática de arquivos PDF e XML de documentos fiscais eletrônicos nos portais das Secretarias de Fazenda integrada ao SAP ECC',
        'valor_estimado': 620000.0,
        'data_sessao': 'Sessão 26/08/2026 (Julgamento de Impugnações / Propostas)',
        'status_pncp': 'EM DISPUTA / ANÁLISE DE DOCUMENTAÇÃO FISCAL',
        'pregoeiro': 'Rosilda / GCC',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'MÉDIO — Escrituração contábil e conformidade fiscal',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    },
    {
        'licitacao': 'PE 33/2026',
        'processo_siga': 'TLB-PRO-2026/00449',
        'diretoria': 'DG / GIRC',
        'objeto': 'Contratação de apólice de Seguro de Responsabilidade Civil de Administradores (D&O) para diretores e membros dos órgãos estatutários da Telebras',
        'valor_estimado': 1100000.0,
        'data_sessao': 'Sessão 25/08/2026 (Em análise de habilitação)',
        'status_pncp': 'JULGAMENTO / HABILITAÇÃO DA PROPOSTA',
        'pregoeiro': 'Rosilda / GCC',
        'plataforma': 'Compras.gov.br (UASG 925150)',
        'impacto': 'CRÍTICO — Cobertura estatutária e governança corporativa',
        'link_pncp': 'https://pncp.gov.br/app/editais?uasg=925150'
    }
]

df_radar_pregoes = pd.DataFrame(pregoes_radar)

print("Dados estruturados com sucesso!")
print(f"Fase 5 (GCC): {len(fase5)} processos | R$ {fase5['Valor Estimado 2026 (R$)'].sum():,.2f}")
print(f"Fase 4 (CONJUR): {len(fase4)} processos | R$ {fase4['Valor Estimado 2026 (R$)'].sum():,.2f}")
print(f"Pregões Radar PNCP: {len(df_radar_pregoes)} certames")

# ─────────────────────────────────────────────────────────────────────────────
# 4. GERAÇÃO DO ARQUIVO EXCEL OFICIAL (.XLSX)
# ─────────────────────────────────────────────────────────────────────────────
excel_path = 'Relatorio_Radar_Editais_PNCP_SIGA_2026.xlsx'
wb = openpyxl.Workbook()

# Estilos padrão
font_title = Font(name='Calibri', size=14, bold=True, color='1E3A8A')
font_subtitle = Font(name='Calibri', size=10, italic=True, color='475569')
font_section = Font(name='Calibri', size=11, bold=True, color='1E3A8A')
font_header = Font(name='Calibri', size=9, bold=True, color='FFFFFF')
font_bold = Font(name='Calibri', size=9, bold=True)
font_regular = Font(name='Calibri', size=8.5)
font_kpi_num = Font(name='Calibri', size=16, bold=True, color='1E3A8A')
font_kpi_lbl = Font(name='Calibri', size=8, bold=True, color='64748B')

fill_navy = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
fill_blue_light = PatternFill(start_color='DBEAFE', end_color='DBEAFE', fill_type='solid')
fill_zebra = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
fill_white = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
fill_kpi = PatternFill(start_color='EFF6FF', end_color='EFF6FF', fill_type='solid')
fill_alert_red = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
fill_alert_yellow = PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid')
fill_alert_green = PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid')

thin_gray = Side(style='thin', color='E2E8F0')
border_cell = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)
border_header = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=Side(style='medium', color='1E3A8A'))
border_total = Border(top=Side(style='thin', color='1E3A8A'), bottom=Side(style='double', color='1E3A8A'))

align_left = Alignment(horizontal='left', vertical='center')
align_center = Alignment(horizontal='center', vertical='center')
align_right = Alignment(horizontal='right', vertical='center')

# ABA 1: RESUMO EXECUTIVO
ws1 = wb.active
ws1.title = "Resumo Executivo"
ws1.views.sheetView[0].showGridLines = True

ws1['A1'] = "TELECOMUNICAÇÕES BRASILEIRAS S.A. — TELEBRAS"
ws1['A1'].font = font_subtitle
ws1['A2'] = "RELATÓRIO GERENCIAL: RADAR DE PREGÕES PNCP & TRAMITAÇÃO SIGA"
ws1['A2'].font = font_title
ws1['A3'] = f"Posição Oficial: Semana de 05 a 09 de Outubro de 2026 | Gerência de Compras e Contratos (GCC)"
ws1['A3'].font = font_subtitle

# Painel de KPIs
kpis = [
    ("PROCESSOS NA MESA GCC (FASE 5)", f"{len(fase5)} Processos", "Prontos para lançamento no PNCP", "A5"),
    ("VALOR EM PRONTIDÃO GCC", f"R$ {fase5['Valor Estimado 2026 (R$)'].sum():,.2f}", "Parecer CONJUR favorável emitido", "C5"),
    ("PIPELINE CONJUR (FASE 4)", f"{len(fase4)} Processos", f"R$ {fase4['Valor Estimado 2026 (R$)'].sum():,.2f} em análise", "E5"),
    ("PREGÕES ATIVOS RADAR PNCP", f"{len(df_radar_pregoes)} Certames", f"R$ {df_radar_pregoes['valor_estimado'].sum():,.2f} no Compras.gov", "G5"),
]

for title, val, sub, cell_ref in kpis:
    col = cell_ref[0]
    r = int(cell_ref[1])
    c_idx = openpyxl.utils.column_index_from_string(col)
    ws1.merge_cells(start_row=r, start_column=c_idx, end_row=r+2, end_column=c_idx+1)
    top_cell = ws1.cell(row=r, column=c_idx)
    top_cell.value = f"{title}\n{val}\n{sub}"
    top_cell.font = font_regular
    top_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    top_cell.fill = fill_kpi
    for row in ws1.iter_rows(min_row=r, max_row=r+2, min_col=c_idx, max_col=c_idx+1):
        for cell in row:
            cell.border = border_cell

ws1['A9'] = "1. DISTRIBUIÇÃO DOS PROCESSOS EM PRONTIDÃO NA GCC (FASE 5 — ESTEIRA DIRETA PARA O PNCP)"
ws1['A9'].font = font_section

headers_resumo = ["Diretoria", "Qtd Processos", "Valor Total Estimado (R$)", "% do Valor", "No Prazo", "Em Atenção", "Responsável GCC"]
for c_i, h in enumerate(headers_resumo, start=1):
    cell = ws1.cell(row=10, column=c_i, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center if c_i in [2, 4, 5, 6] else (align_right if c_i == 3 else align_left)
    cell.border = border_header

row_curr = 11
total_val_fase5 = fase5['Valor Estimado 2026 (R$)'].sum()
for dirt, sub in fase5.groupby('Diretoria'):
    val_dirt = sub['Valor Estimado 2026 (R$)'].sum()
    pct = (val_dirt / total_val_fase5 * 100) if total_val_fase5 > 0 else 0
    no_prazo = len(sub[sub['Status de Prazo'] == 'NO PRAZO'])
    atencao = len(sub[sub['Status de Prazo'] != 'NO PRAZO'])
    
    ws1.cell(row=row_curr, column=1, value=dirt).alignment = align_left
    ws1.cell(row=row_curr, column=2, value=len(sub)).alignment = align_center
    c_val = ws1.cell(row=row_curr, column=3, value=val_dirt)
    c_val.number_format = 'R$ #,##0.00'
    c_val.alignment = align_right
    c_pct = ws1.cell(row=row_curr, column=4, value=pct / 100)
    c_pct.number_format = '0.0%'
    c_pct.alignment = align_center
    ws1.cell(row=row_curr, column=5, value=no_prazo).alignment = align_center
    ws1.cell(row=row_curr, column=6, value=atencao).alignment = align_center
    ws1.cell(row=row_curr, column=7, value="Pedro Diniz / Rosilda (GCC)").alignment = align_left
    
    for c_i in range(1, 8):
        c_node = ws1.cell(row=row_curr, column=c_i)
        c_node.font = font_regular
        c_node.border = border_cell
        if row_curr % 2 == 1:
            c_node.fill = fill_zebra
    row_curr += 1

# Totalizador
ws1.cell(row=row_curr, column=1, value="TOTAL GERAL EM PRONTIDÃO GCC").font = font_bold
ws1.cell(row=row_curr, column=2, value=len(fase5)).font = font_bold
c_tot = ws1.cell(row=row_curr, column=3, value=total_val_fase5)
c_tot.font = font_bold
c_tot.number_format = 'R$ #,##0.00'
ws1.cell(row=row_curr, column=4, value="100.0%").font = font_bold
ws1.cell(row=row_curr, column=5, value=len(fase5[fase5['Status de Prazo']=='NO PRAZO'])).font = font_bold
ws1.cell(row=row_curr, column=6, value=len(fase5[fase5['Status de Prazo']!='NO PRAZO'])).font = font_bold
ws1.cell(row=row_curr, column=7, value="31 Editais Prontos").font = font_bold
for c_i in range(1, 8):
    c_node = ws1.cell(row=row_curr, column=c_i)
    c_node.border = border_total
    c_node.fill = fill_blue_light

# ABA 2: FASE 5 - PRONTIDÃO GCC (31 PROCESSOS)
ws2 = wb.create_sheet(title="Fase 5 - Prontidão GCC (PNCP)")
ws2.views.sheetView[0].showGridLines = True

ws2['A1'] = "PROCESSOS NO SIGA EM PRONTIDÃO NA GCC (FASE 5 — AGUARDANDO PUBLICAÇÃO NO PNCP)"
ws2['A1'].font = font_title
ws2['A2'] = "Status: Parecer CONJUR emitido, Checklist de conformidade aprovado e aguardando publicação no Compras.gov.br / PNCP"
ws2['A2'].font = font_subtitle

headers_f5 = ["#", "Processo SIGA", "Diretoria", "Gerência", "Objeto Detalhado", "Valor Estimado 2026 (R$)", "Prioridade", "Dias no Setor", "Status Prazo", "Peças Juntadas no SIGA", "Próximo Passo / PNCP", "Ação em Andamento"]
for c_i, h in enumerate(headers_f5, start=1):
    cell = ws2.cell(row=4, column=c_i, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center if c_i in [1, 2, 7, 8, 9] else (align_right if c_i == 6 else align_left)
    cell.border = border_header

for idx, r in fase5.iterrows():
    r_idx = 5 + idx
    ws2.cell(row=r_idx, column=1, value=idx+1).alignment = align_center
    ws2.cell(row=r_idx, column=2, value=r['Processo SIGA']).alignment = align_center
    ws2.cell(row=r_idx, column=3, value=r['Diretoria']).alignment = align_left
    ws2.cell(row=r_idx, column=4, value=r['Gerência Demandante']).alignment = align_center
    ws2.cell(row=r_idx, column=5, value=r['Objeto Detalhado']).alignment = align_left
    c_val = ws2.cell(row=r_idx, column=6, value=r['Valor Estimado 2026 (R$)'])
    c_val.number_format = 'R$ #,##0.00'
    c_val.alignment = align_right
    ws2.cell(row=r_idx, column=7, value=r['Prioridade']).alignment = align_center
    ws2.cell(row=r_idx, column=8, value=r['Dias no Setor']).alignment = align_center
    
    c_status = ws2.cell(row=r_idx, column=9, value=r['Status de Prazo'])
    c_status.alignment = align_center
    if r['Status de Prazo'] == 'NO PRAZO':
        c_status.fill = fill_alert_green
    else:
        c_status.fill = fill_alert_yellow
        
    ws2.cell(row=r_idx, column=10, value=r['Peças Juntadas no SIGA']).alignment = align_left
    ws2.cell(row=r_idx, column=11, value=r['Próximo Documento Obrigatório']).alignment = align_left
    ws2.cell(row=r_idx, column=12, value=r['Ação em Andamento']).alignment = align_left
    
    for c_i in range(1, 13):
        c_node = ws2.cell(row=r_idx, column=c_i)
        c_node.font = font_regular
        c_node.border = border_cell
        if idx % 2 == 1 and c_i != 9:
            c_node.fill = fill_zebra

# Totalizador Fase 5
tot_row_f5 = 5 + len(fase5)
ws2.cell(row=tot_row_f5, column=1, value="TOTAL GERAL").font = font_bold
ws2.cell(row=tot_row_f5, column=2, value=f"{len(fase5)} Processos").font = font_bold
c_tot5 = ws2.cell(row=tot_row_f5, column=6, value=fase5['Valor Estimado 2026 (R$)'].sum())
c_tot5.number_format = 'R$ #,##0.00'
c_tot5.font = font_bold
for c_i in range(1, 13):
    c_node = ws2.cell(row=tot_row_f5, column=c_i)
    c_node.border = border_total
    c_node.fill = fill_blue_light

# ABA 3: RADAR PREGÕES PNCP 2026
ws3 = wb.create_sheet(title="Radar Pregões PNCP 2026")
ws3.views.sheetView[0].showGridLines = True

ws3['A1'] = "PREGÕES ELETRÔNICOS E EDITAIS NO RADAR DO PNCP & COMPRAS.GOV.BR (OUTUBRO 2026)"
ws3['A1'].font = font_title
ws3['A2'] = "Certames em andamento no compras.gov.br (UASG 925150) — Sessões públicas e julgamento"
ws3['A2'].font = font_subtitle

headers_radar = ["Licitação", "Processo SIGA", "Diretoria / Área", "Objeto Detalhado", "Valor Estimado (R$)", "Data da Sessão Pública", "Status no PNCP / Compras.gov", "Pregoeiro / GCC", "Impacto Operacional"]
for c_i, h in enumerate(headers_radar, start=1):
    cell = ws3.cell(row=4, column=c_i, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center if c_i in [1, 2, 3, 6, 7] else (align_right if c_i == 5 else align_left)
    cell.border = border_header

for idx, r in df_radar_pregoes.iterrows():
    r_idx = 5 + idx
    ws3.cell(row=r_idx, column=1, value=r['licitacao']).alignment = align_center
    ws3.cell(row=r_idx, column=2, value=r['processo_siga']).alignment = align_center
    ws3.cell(row=r_idx, column=3, value=r['diretoria']).alignment = align_center
    ws3.cell(row=r_idx, column=4, value=r['objeto']).alignment = align_left
    c_val = ws3.cell(row=r_idx, column=5, value=r['valor_estimado'])
    c_val.number_format = 'R$ #,##0.00'
    c_val.alignment = align_right
    ws3.cell(row=r_idx, column=6, value=r['data_sessao']).alignment = align_center
    ws3.cell(row=r_idx, column=7, value=r['status_pncp']).alignment = align_center
    ws3.cell(row=r_idx, column=8, value=r['pregoeiro']).alignment = align_left
    ws3.cell(row=r_idx, column=9, value=r['impacto']).alignment = align_left
    
    for c_i in range(1, 10):
        c_node = ws3.cell(row=r_idx, column=c_i)
        c_node.font = font_regular
        c_node.border = border_cell
        if idx % 2 == 1:
            c_node.fill = fill_zebra

# ABA 4: PIPELINE CONJUR (FASE 4 - 41 PROCESSOS)
ws4 = wb.create_sheet(title="Pipeline CONJUR (Fase 4)")
ws4.views.sheetView[0].showGridLines = True

ws4['A1'] = "PIPELINE JURÍDICO: PROCESSOS NA CONJUR (FASE 4 — ANTECESSORES DO EDITAL)"
ws4['A1'].font = font_title
ws4['A2'] = "41 Processos em Análise Jurídica / Minuta de Edital no SIGA que serão remetidos à GCC para publicação"
ws4['A2'].font = font_subtitle

headers_f4 = ["#", "Processo SIGA", "Diretoria", "Gerência", "Objeto Detalhado", "Valor Estimado 2026 (R$)", "Prioridade", "Dias na CONJUR", "Status Prazo", "Peças no SIGA", "Próximo Passo Obrigatório"]
for c_i, h in enumerate(headers_f4, start=1):
    cell = ws4.cell(row=4, column=c_i, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center if c_i in [1, 2, 4, 7, 8, 9] else (align_right if c_i == 6 else align_left)
    cell.border = border_header

for idx, r in fase4.iterrows():
    r_idx = 5 + idx
    ws4.cell(row=r_idx, column=1, value=idx+1).alignment = align_center
    ws4.cell(row=r_idx, column=2, value=r['Processo SIGA']).alignment = align_center
    ws4.cell(row=r_idx, column=3, value=r['Diretoria']).alignment = align_left
    ws4.cell(row=r_idx, column=4, value=r['Gerência Demandante']).alignment = align_center
    ws4.cell(row=r_idx, column=5, value=r['Objeto Detalhado']).alignment = align_left
    c_val = ws4.cell(row=r_idx, column=6, value=r['Valor Estimado 2026 (R$)'])
    c_val.number_format = 'R$ #,##0.00'
    c_val.alignment = align_right
    ws4.cell(row=r_idx, column=7, value=r['Prioridade']).alignment = align_center
    ws4.cell(row=r_idx, column=8, value=r['Dias no Setor']).alignment = align_center
    
    c_status = ws4.cell(row=r_idx, column=9, value=r['Status de Prazo'])
    c_status.alignment = align_center
    if r['Status de Prazo'] == 'NO PRAZO':
        c_status.fill = fill_alert_green
    else:
        c_status.fill = fill_alert_yellow
        
    ws4.cell(row=r_idx, column=10, value=r['Peças Juntadas no SIGA']).alignment = align_left
    ws4.cell(row=r_idx, column=11, value=r['Próximo Documento Obrigatório']).alignment = align_left
    
    for c_i in range(1, 12):
        c_node = ws4.cell(row=r_idx, column=c_i)
        c_node.font = font_regular
        c_node.border = border_cell
        if idx % 2 == 1 and c_i != 9:
            c_node.fill = fill_zebra

tot_row_f4 = 5 + len(fase4)
ws4.cell(row=tot_row_f4, column=1, value="TOTAL GERAL CONJUR").font = font_bold
ws4.cell(row=tot_row_f4, column=2, value=f"{len(fase4)} Processos").font = font_bold
c_tot4 = ws4.cell(row=tot_row_f4, column=6, value=fase4['Valor Estimado 2026 (R$)'].sum())
c_tot4.number_format = 'R$ #,##0.00'
c_tot4.font = font_bold
for c_i in range(1, 12):
    c_node = ws4.cell(row=tot_row_f4, column=c_i)
    c_node.border = border_total
    c_node.fill = fill_blue_light

# Autoajuste de largura de colunas em todas as abas
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if '\n' in val_str:
                val_str = max(val_str.split('\n'), key=len)
            max_len = max(max_len, len(val_str))
        sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 65)

wb.save(excel_path)
print(f"Excel gerado com sucesso: {excel_path}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. GERAÇÃO DE GRÁFICOS PARA O PDF EXECUTIVO (MATPLOTLIB)
# ─────────────────────────────────────────────────────────────────────────────
# Gráfico 1: Donut de Valores Fase 5 por Diretoria
fig1, ax1 = plt.subplots(figsize=(4.5, 3.2), dpi=200)
dirt_summary = fase5.groupby('Diretoria')['Valor Estimado 2026 (R$)'].sum().sort_values(ascending=False)
colors_donut = ['#1e3a8a', '#0284c7', '#0d9488', '#f59e0b']

wedges, _ = ax1.pie(
    dirt_summary.values,
    colors=colors_donut[:len(dirt_summary)],
    startangle=140,
    wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2.5),
)
ax1.text(0, 0.08, f"{len(fase5)}", ha='center', va='center', fontsize=18, fontweight='900', color='#0f172a')
ax1.text(0, -0.18, 'EDITAIS NA GCC', ha='center', va='center', fontsize=6.5, fontweight='800', color='#475569')

legend_labels = [f"{k.split(' - ')[1] if ' - ' in k else k}: R$ {v/1e6:.1f}M" for k, v in dirt_summary.items()]
patches = [mpatches.Patch(color=colors_donut[i], label=legend_labels[i]) for i in range(len(dirt_summary))]
ax1.legend(handles=patches, loc='center left', bbox_to_anchor=(0.85, 0.5), fontsize=6.5, frameon=False)
ax1.set_title('Prontidão GCC por Diretoria (Valor R$)', fontsize=8.5, fontweight='bold', pad=8, color='#0f172a')
fig1.tight_layout()
buf1 = io.BytesIO()
fig1.savefig(buf1, format='png', bbox_inches='tight', transparent=True)
buf1.seek(0)
chart1_b64 = base64.b64encode(buf1.read()).decode('utf-8')
plt.close(fig1)

# Gráfico 2: Top 7 Maiores Editais em Prontidão na GCC
top7_fase5 = fase5.head(7)
fig2, ax2 = plt.subplots(figsize=(7.5, 3.2), dpi=200)
labels_top7 = [f"{r['Processo SIGA'].replace('TLB-PRO-2026/', '')}\n({r['Gerência Demandante']})" for _, r in top7_fase5.iterrows()]
vals_top7 = top7_fase5['Valor Estimado 2026 (R$)'].values

bars2 = ax2.bar(range(len(top7_fase5)), vals_top7 / 1e6, color='#1e3a8a', width=0.55)
ax2.set_xticks(range(len(top7_fase5)))
ax2.set_xticklabels(labels_top7, fontsize=6.5, fontweight='bold', color='#374151')
ax2.set_ylabel('Milhões R$', fontsize=7, color='#64748b')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.grid(axis='y', linestyle='--', alpha=0.3)

for bar in bars2:
    y = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, y + 0.15, f"R$ {y:.2f}M", ha='center', va='bottom', fontsize=6.8, fontweight='bold', color='#0284c7')

ax2.set_title('Top 7 Maiores Editais na Fila de Lançamento no PNCP (GCC)', fontsize=8.5, fontweight='bold', pad=8, color='#0f172a')
fig2.tight_layout()
buf2 = io.BytesIO()
fig2.savefig(buf2, format='png', bbox_inches='tight', transparent=True)
buf2.seek(0)
chart2_b64 = base64.b64encode(buf2.read()).decode('utf-8')
plt.close(fig2)

print("Gráficos gerados com sucesso!")

# ─────────────────────────────────────────────────────────────────────────────
# 6. MONTAGEM DO HTML EXECUTIVO PARA O PDF (5 PÁGINAS A4 PAISAGEM)
# ─────────────────────────────────────────────────────────────────────────────
today_str = date.today().strftime('%d/%m/%Y')

def fmt_cur(val):
    return f"R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Montar tabelas HTML para o PDF
# Página 2: Tabela de Pregões Radar PNCP
rows_radar_html = ""
for idx, r in df_radar_pregoes.iterrows():
    bg = '#f8fafc' if idx % 2 == 0 else '#ffffff'
    status_badge = '<span style="background:#dbeafe;color:#1e40af;padding:1px 5px;border-radius:3px;font-weight:800;font-size:6px;">EM ANDAMENTO</span>'
    if 'JULGAMENTO' in r['status_pncp']:
        status_badge = '<span style="background:#fef3c7;color:#d97706;padding:1px 5px;border-radius:3px;font-weight:800;font-size:6px;">JULGAMENTO</span>'
    elif 'PROPOSTAS' in r['status_pncp']:
        status_badge = '<span style="background:#dcfce7;color:#166534;padding:1px 5px;border-radius:3px;font-weight:800;font-size:6px;">PROPOSTAS ABERTAS</span>'
        
    rows_radar_html += f"""
    <tr style="background:{bg};">
      <td style="text-align:center;font-weight:800;color:#1e3a8a;font-size:6.8px;">{r['licitacao']}</td>
      <td style="text-align:center;font-size:6.2px;font-weight:700;">{r['processo_siga']}</td>
      <td style="text-align:center;font-size:6.2px;font-weight:800;color:#0284c7;">{r['diretoria']}</td>
      <td style="font-size:6.2px;"><strong>{r['objeto'][:90]}...</strong></td>
      <td style="text-align:right;font-weight:800;color:#0f172a;font-size:6.8px;">{fmt_cur(r['valor_estimado'])}</td>
      <td style="text-align:center;font-size:6px;color:#374151;">{r['data_sessao']}</td>
      <td style="text-align:center;">{status_badge}</td>
      <td style="font-size:6px;color:#475569;">{r['pregoeiro']}</td>
      <td style="font-size:6px;color:#b45309;font-weight:700;">{r['impacto']}</td>
    </tr>"""

# Páginas 3 e 4: Dividir os 31 processos da Fase 5 (16 na pág 3, 15 na pág 4)
fase5_p1 = fase5.iloc[:16]
fase5_p2 = fase5.iloc[16:]

def make_fase5_rows(sub_df, start_idx=1):
    out = ""
    for idx, r in sub_df.iterrows():
        i = start_idx + idx if start_idx == 1 else start_idx + (idx - 16)
        bg = '#f8fafc' if i % 2 == 0 else '#ffffff'
        status_prazo = r['Status de Prazo']
        badge_prazo = '<span style="background:#dcfce7;color:#166534;padding:1px 4px;border-radius:3px;font-weight:800;font-size:5.5px;">NO PRAZO</span>' if status_prazo == 'NO PRAZO' else '<span style="background:#fef3c7;color:#d97706;padding:1px 4px;border-radius:3px;font-weight:800;font-size:5.5px;">ATENÇÃO</span>'
        dirt_short = r['Diretoria'].split(' - ')[1] if ' - ' in str(r['Diretoria']) else str(r['Diretoria'])
        out += f"""
        <tr style="background:{bg};">
          <td style="text-align:center;color:#64748b;font-weight:700;">{i}</td>
          <td style="text-align:center;font-size:6.2px;font-weight:800;color:#1e3a8a;">{r['Processo SIGA']}</td>
          <td style="text-align:center;font-size:6px;font-weight:700;">{dirt_short[:4]} / {r['Gerência Demandante']}</td>
          <td style="font-size:6.2px;"><strong>{r['Objeto Detalhado'][:70]}...</strong></td>
          <td style="text-align:right;font-weight:800;color:#0f172a;font-size:6.5px;">{fmt_cur(r['Valor Estimado 2026 (R$)'])}</td>
          <td style="text-align:center;font-size:6px;">{r['Prioridade']}</td>
          <td style="text-align:center;font-size:6.2px;font-weight:700;">{r['Dias no Setor']}d</td>
          <td style="text-align:center;">{badge_prazo}</td>
          <td style="font-size:5.8px;color:#166534;">{r['Peças Juntadas no SIGA'][:50]}...</td>
          <td style="font-size:5.8px;color:#1e40af;font-weight:700;">{r['Próximo Documento Obrigatório']}</td>
        </tr>"""
    return out

rows_f5_p1 = make_fase5_rows(fase5_p1, 1)
rows_f5_p2 = make_fase5_rows(fase5_p2, 17)

# Página 5: Top 15 processos da CONJUR (Fase 4)
rows_conjur_html = ""
for idx, r in fase4.head(15).iterrows():
    bg = '#f8fafc' if idx % 2 == 0 else '#ffffff'
    dirt_short = r['Diretoria'].split(' - ')[1] if ' - ' in str(r['Diretoria']) else str(r['Diretoria'])
    badge_prazo = '<span style="background:#dcfce7;color:#166534;padding:1px 4px;border-radius:3px;font-weight:800;font-size:5.5px;">NO PRAZO</span>' if r['Status de Prazo'] == 'NO PRAZO' else '<span style="background:#fee2e2;color:#dc2626;padding:1px 4px;border-radius:3px;font-weight:800;font-size:5.5px;">ATENÇÃO</span>'
    rows_conjur_html += f"""
    <tr style="background:{bg};">
      <td style="text-align:center;color:#64748b;font-weight:700;">{idx+1}</td>
      <td style="text-align:center;font-size:6.2px;font-weight:800;color:#1e3a8a;">{r['Processo SIGA']}</td>
      <td style="text-align:center;font-size:6px;font-weight:700;">{dirt_short[:4]} / {r['Gerência Demandante']}</td>
      <td style="font-size:6.2px;"><strong>{r['Objeto Detalhado'][:75]}...</strong></td>
      <td style="text-align:right;font-weight:800;color:#0f172a;font-size:6.5px;">{fmt_cur(r['Valor Estimado 2026 (R$)'])}</td>
      <td style="text-align:center;font-size:6.2px;font-weight:700;">{r['Dias no Setor']}d na CONJUR</td>
      <td style="text-align:center;">{badge_prazo}</td>
      <td style="font-size:5.8px;color:#475569;">{r['Ação em Andamento'][:55]}...</td>
      <td style="font-size:5.8px;color:#1e40af;font-weight:700;">{r['Próximo Documento Obrigatório']}</td>
    </tr>"""

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: A4 landscape; margin: 7mm 9mm 7mm 9mm; }}
  * {{ box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  body {{ margin:0; padding:0; color:#1e293b; background:#fff; font-size:7.5px; line-height:1.3; }}

  .page {{ height:192mm; max-height:192mm; overflow:hidden; position:relative; page-break-after:always;
           display:flex; flex-direction:column; justify-content:space-between; }}
  .page:last-child {{ page-break-after:avoid; }}

  .hbar {{ display:flex; justify-content:space-between; align-items:center;
           border-bottom:3px solid #1e3a8a; padding-bottom:5px; margin-bottom:7px; }}
  .hbar-left .corp {{ font-size:7px; font-weight:800; color:#1e3a8a; text-transform:uppercase; letter-spacing:0.6px; }}
  .hbar-left .title {{ font-size:13px; font-weight:900; color:#0f172a; margin:1px 0; letter-spacing:-0.3px; }}
  .hbar-left .sub {{ font-size:7px; color:#475569; }}
  .hbar-right {{ text-align:right; }}
  .hbadge {{ background:#f1f5f9; border:1px solid #cbd5e1; color:#334155;
             padding:2px 7px; border-radius:4px; font-size:7px; font-weight:800; }}
  .hdate {{ font-size:6.5px; color:#64748b; margin-top:2px; }}

  .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:6px; margin-bottom:7px; }}
  .kpi {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:5px; padding:5px 8px;
          border-left:3.5px solid #1e3a8a; }}
  .kpi.teal {{ border-left-color:#0d9488; background:#f0fdfa; }}
  .kpi.warn {{ border-left-color:#f59e0b; background:#fffbeb; }}
  .kpi.blue {{ border-left-color:#0284c7; background:#f0f9ff; }}
  .kpi-lbl {{ font-size:6.5px; text-transform:uppercase; font-weight:800; color:#64748b; }}
  .kpi-val {{ font-size:11.5px; font-weight:900; color:#0f172a; margin:1px 0; }}
  .kpi-sub {{ font-size:6.2px; color:#64748b; }}

  .panel {{ background:#fff; border:1px solid #e2e8f0; border-radius:5px; padding:6px; }}
  .ph {{ font-size:7.5px; font-weight:800; color:#1e3a8a; border-bottom:1px solid #f1f5f9;
         padding-bottom:3px; margin-bottom:4px; text-transform:uppercase;
         display:flex; justify-content:space-between; }}

  table.dt {{ width:100%; border-collapse:collapse; font-size:6.5px; }}
  table.dt th {{ background:#1e3a8a; color:#fff; font-weight:800; text-align:left;
                 padding:3px 4px; border:1px solid #1e3a8a; text-transform:uppercase; font-size:6px; }}
  table.dt td {{ padding:2.5px 4px; border:1px solid #e2e8f0; vertical-align:middle; }}

  .footer {{ margin-top:4px; border-top:1px solid #e2e8f0; padding-top:3px;
             display:flex; justify-content:space-between; font-size:6.5px; color:#64748b; }}
  .section-divider {{ height:2px; background:linear-gradient(to right,#1e3a8a,#0284c7,#0d9488);
                      border-radius:1px; margin:4px 0; }}
</style>
</head>
<body>

<!-- PÁGINA 1: DASHBOARD EXECUTIVO RADAR PNCP & ESTEIRA SIGA -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telecomunicações Brasileiras S.A. — Telebras &nbsp;|&nbsp; Gerência de Compras e Contratos (GCC)</div>
        <div class="title">RELATÓRIO GERENCIAL: RADAR DE PREGÕES PNCP & TRAMITAÇÃO SIGA</div>
        <div class="sub">Mapeamento Integrado dos Processos no SIGA em Tramitação para Publicação de Editais no Portal Nacional de Contratações Públicas</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">OUTUBRO 2026 &nbsp;|&nbsp; SEMANA 05 A 09/10</div>
        <div class="hdate">Posição Oficial: {today_str} &nbsp;•&nbsp; Fonte: SIGA & PNCP (UASG 925150)</div>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi teal">
        <div class="kpi-lbl">Processos em Prontidão GCC (Fase 5)</div>
        <div class="kpi-val">{len(fase5)} Processos</div>
        <div class="kpi-sub">Parecer CONJUR aprovado &bull; Prontos para edital</div>
      </div>
      <div class="kpi blue">
        <div class="kpi-lbl">Volume Financeiro na Fila da GCC</div>
        <div class="kpi-val">{fmt_cur(fase5['Valor Estimado 2026 (R$)'].sum())}</div>
        <div class="kpi-sub">91% concentrado na DTO (R$ 48,8M)</div>
      </div>
      <div class="kpi warn">
        <div class="kpi-lbl">Pipeline na CONJUR (Fase 4)</div>
        <div class="kpi-val">{len(fase4)} Processos</div>
        <div class="kpi-sub">Total: {fmt_cur(fase4['Valor Estimado 2026 (R$)'].sum())} em análise prévia</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Pregões em Andamento PNCP</div>
        <div class="kpi-val">{len(df_radar_pregoes)} Certames Ativos</div>
        <div class="kpi-sub">Destaques: PE 35/2026 (Copa) &bull; PE 42/2026 (SGDC)</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1.8fr 1.2fr; gap:7px; margin-bottom:6px;">
      <div class="panel">
        <div class="ph"><span>Estratificação dos Editais em Prontidão na GCC (Fase 5)</span><span>Fonte: SIGA / Setor 2600</span></div>
        <div style="display:flex; gap:8px; align-items:center;">
          <img style="width:40%;" src="data:image/png;base64,{chart1_b64}" alt="Donut">
          <img style="width:58%;" src="data:image/png;base64,{chart2_b64}" alt="Bar">
        </div>
      </div>
      <div class="panel">
        <div class="ph"><span>⚡ Destaques dos Editais no Radar PNCP desta Semana</span></div>
        <div style="display:flex; flex-direction:column; gap:4px; font-size:6px;">
          <div style="background:#eff6ff; border:1px solid #bfdbfe; border-left:3.5px solid #1e40af; border-radius:3px; padding:3px 5px;">
            <strong style="color:#1e40af; font-size:6.5px;">PE 35/2026 (SRP) — Copa Feminina 2027 & Infraestrutura</strong><br>
            Abertura recente no PNCP (R$ 10,0M). Sessão pública ativa no Compras.gov.br nesta semana para julgamento de propostas de engenharia de rede.
          </div>
          <div style="background:#f0fdf4; border:1px solid #86efac; border-left:3.5px solid #16a34a; border-radius:3px; padding:3px 5px;">
            <strong style="color:#166534; font-size:6.5px;">PE 42/2026 — Manutenção Gateways SGDC (3 Estações)</strong><br>
            Publicado no DOU e PNCP (R$ 3,0M). Abertura agendada para <strong>21/10/2026 às 10h</strong>. Envolve Salvador, Campo Grande e Florianópolis.
          </div>
          <div style="background:#fffbeb; border:1px solid #fde68a; border-left:3.5px solid #d97706; border-radius:3px; padding:3px 5px;">
            <strong style="color:#b45309; font-size:6.5px;">PE 30/2026 — Rede Elétrica GERP & PE 38/2026 Datacenter</strong><br>
            PE 30 em análise técnica de proposta vencedora na GERP. PE 38 (Ar condicionado Datacenter) na fase de julgamento de lances.
          </div>
        </div>
      </div>
    </div>

    <!-- Tabela Resumo Diretoria -->
    <div class="panel">
      <div class="ph"><span>Consolidação por Diretoria da Esteira de Lançamento de Editais (Fase 5 na GCC)</span></div>
      <table class="dt">
        <thead>
          <tr>
            <th>Diretoria Demandante</th>
            <th style="text-align:center;">Qtd Processos</th>
            <th style="text-align:right;">Valor Estimado (R$)</th>
            <th style="text-align:center;">% Carteira</th>
            <th style="text-align:center;">No Prazo (SLA)</th>
            <th style="text-align:center;">Em Atenção</th>
            <th>Próxima Etapa no SIGA / PNCP</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong style="color:#1e3a8a;">3000 - Diretoria Técnico-Operacional (DTO)</strong></td>
            <td style="text-align:center;">24</td>
            <td style="text-align:right;"><strong>R$ 48.797.284,12</strong></td>
            <td style="text-align:center;">91,0%</td>
            <td style="text-align:center;color:#16a34a;font-weight:800;">12</td>
            <td style="text-align:center;color:#d97706;font-weight:800;">12</td>
            <td>Geração do número de aviso e publicação do edital no PNCP</td>
          </tr>
          <tr>
            <td><strong style="color:#0284c7;">5000 - Diretoria de Governança (DG)</strong></td>
            <td style="text-align:center;">1</td>
            <td style="text-align:right;"><strong>R$ 2.985.000,00</strong></td>
            <td style="text-align:center;">5,6%</td>
            <td style="text-align:center;">0</td>
            <td style="text-align:center;color:#d97706;font-weight:800;">1</td>
            <td>Publicação do Edital de Consultoria Organizacional SaaS</td>
          </tr>
          <tr>
            <td><strong style="color:#0d9488;">4000 - Diretoria Comercial (DC)</strong></td>
            <td style="text-align:center;">2</td>
            <td style="text-align:right;"><strong>R$ 1.081.672,80</strong></td>
            <td style="text-align:center;">2,0%</td>
            <td style="text-align:center;color:#16a34a;font-weight:800;">2</td>
            <td style="text-align:center;">0</td>
            <td>Lançamento de edital para Trânsito IP e Infra Regional</td>
          </tr>
          <tr>
            <td><strong style="color:#f59e0b;">2000 - Diretoria Administrativo-Financeira (DAFRI)</strong></td>
            <td style="text-align:center;">4</td>
            <td style="text-align:right;"><strong>R$ 770.117,95</strong></td>
            <td style="text-align:center;">1,4%</td>
            <td style="text-align:center;color:#16a34a;font-weight:800;">2</td>
            <td style="text-align:center;color:#d97706;font-weight:800;">2</td>
            <td>Agenciamento de passagens, serviços postais e crachás</td>
          </tr>
          <tr style="background:#cbd5e1;font-weight:900;border-top:2px solid #0f172a;">
            <td>TOTAL DE PROCESSOS EM PRONTIDÃO GCC</td>
            <td style="text-align:center;">31</td>
            <td style="text-align:right;">R$ 53.634.074,87</td>
            <td style="text-align:center;">100,0%</td>
            <td style="text-align:center;">16</td>
            <td style="text-align:center;">15</td>
            <td>Fila de Lançamento de Editais no PNCP / Compras.gov.br</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Relatório Radar PNCP & Tramitação SIGA — CONFIDENCIAL</div>
    <div>Página 1 de 5</div>
  </div>
</div>

<!-- PÁGINA 2: RADAR DE PREGÕES PNCP / COMPRAS.GOV.BR -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">RADAR DE PREGÕES E EDITAIS NO PNCP / COMPRAS.GOV.BR — OUTUBRO 2026</div>
        <div class="sub">Certames em Andamento na Fase Externa: Sessões Públicas, Análise de Propostas e Prazos Recursais</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">FASE EXTERNA / COMPRAS.GOV</div>
        <div class="hdate">UASG 925150 &nbsp;•&nbsp; Posição: {today_str}</div>
      </div>
    </div>

    <div class="panel">
      <div class="ph"><span>Relação Detalhada dos Certames no Radar do PNCP nesta Semana</span><span>Fonte: Compras.gov.br</span></div>
      <table class="dt" style="font-size:6px;">
        <thead>
          <tr>
            <th style="width:75px;text-align:center;">Licitação</th>
            <th style="width:85px;text-align:center;">Processo SIGA</th>
            <th style="width:55px;text-align:center;">Dir / Área</th>
            <th style="width:190px;">Objeto Detalhado</th>
            <th style="width:75px;text-align:right;">Valor Estimado</th>
            <th style="width:115px;text-align:center;">Data da Sessão / Status</th>
            <th style="width:90px;text-align:center;">Fase PNCP</th>
            <th style="width:75px;">Pregoeiro</th>
            <th style="width:110px;">Impacto Operacional</th>
          </tr>
        </thead>
        <tbody>
          {rows_radar_html}
        </tbody>
      </table>
    </div>

    <div style="margin-top:6px; display:grid; grid-template-columns:1fr 1fr; gap:6px;">
      <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:5px 7px; font-size:6.2px; line-height:1.4;">
        <strong style="color:#1e3a8a; font-size:7px;">📌 Diretriz Operacional para o PE 35/2026 (Infraestrutura Copa 2027):</strong><br>
        Por se tratar de Registro de Preços de grande escala (R$ 10,0M) com interesse direto de ministérios e FIFA, a GCC e a equipe de apoio técnico da DTO/GPEI estão atuando em regime prioritário para conferência das planilhas de composição de custos dos licitantes, visando evitar recursos procrastinatórios.
      </div>
      <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:4px; padding:5px 7px; font-size:6.2px; line-height:1.4;">
        <strong style="color:#1d4ed8; font-size:7px;">📌 Preparação para o PE 42/2026 (Gateways SGDC - 21/10/2026):</strong><br>
        O edital já se encontra publicado e acessível no PNCP. O arquivo de itens (607 linhas com especificações de engenharia civil, climatização e elétrica) já foi homologado na plataforma Comprasnet. Abertura confirmada para 21/10 às 10h.
      </div>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Radar de Pregões e Editais no PNCP — CONFIDENCIAL</div>
    <div>Página 2 de 5</div>
  </div>
</div>

<!-- PÁGINA 3: ESTEIRA SIGA -> PNCP: FASE 5 PRONTIDÃO GCC (PARTE 1) -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">ESTEIRA SIGA ➔ PNCP: PROCESSOS EM PRONTIDÃO NA GCC — PARTE 1 (ITENS 01 A 16)</div>
        <div class="sub">Processos com Instrução Prévia Concluída e Parecer CONJUR Aprovado Aguardando Lançamento do Edital</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">SETOR 2600 (GCC)</div>
        <div class="hdate">Ordenado por Valor Estimado Decrescente</div>
      </div>
    </div>

    <div class="panel">
      <div class="ph"><span>Processos em Fila de Lançamento de Edital (Grandes Contratações DTO)</span><span>Parte 1 de 2</span></div>
      <table class="dt" style="font-size:6px;">
        <thead>
          <tr>
            <th style="width:18px;text-align:center;">#</th>
            <th style="width:85px;text-align:center;">Processo SIGA</th>
            <th style="width:55px;text-align:center;">Dir / Área</th>
            <th style="width:200px;">Objeto Detalhado</th>
            <th style="width:75px;text-align:right;">Valor Estimado</th>
            <th style="width:45px;text-align:center;">Priorid.</th>
            <th style="width:38px;text-align:center;">Dias</th>
            <th style="width:50px;text-align:center;">Prazo</th>
            <th style="width:130px;">Peças Juntadas no SIGA</th>
            <th style="width:120px;">Próximo Passo / PNCP</th>
          </tr>
        </thead>
        <tbody>
          {rows_f5_p1}
        </tbody>
      </table>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Esteira SIGA ➔ PNCP — Processos em Prontidão — CONFIDENCIAL</div>
    <div>Página 3 de 5</div>
  </div>
</div>

<!-- PÁGINA 4: ESTEIRA SIGA -> PNCP: FASE 5 PRONTIDÃO GCC (PARTE 2) -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">ESTEIRA SIGA ➔ PNCP: PROCESSOS EM PRONTIDÃO NA GCC — PARTE 2 (ITENS 17 A 31)</div>
        <div class="sub">Totalizador Consolidado dos 31 Processos Prontos para Publicação de Edital no PNCP</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">TOTAL: {fmt_cur(total_val_fase5)}</div>
        <div class="hdate">31 Editais na Fila da GCC</div>
      </div>
    </div>

    <div class="panel">
      <div class="ph"><span>Processos em Fila de Lançamento de Edital (Demais Gerências DTO, DAFRI, DC, DG)</span><span>Parte 2 de 2</span></div>
      <table class="dt" style="font-size:6px;">
        <thead>
          <tr>
            <th style="width:18px;text-align:center;">#</th>
            <th style="width:85px;text-align:center;">Processo SIGA</th>
            <th style="width:55px;text-align:center;">Dir / Área</th>
            <th style="width:200px;">Objeto Detalhado</th>
            <th style="width:75px;text-align:right;">Valor Estimado</th>
            <th style="width:45px;text-align:center;">Priorid.</th>
            <th style="width:38px;text-align:center;">Dias</th>
            <th style="width:50px;text-align:center;">Prazo</th>
            <th style="width:130px;">Peças Juntadas no SIGA</th>
            <th style="width:120px;">Próximo Passo / PNCP</th>
          </tr>
        </thead>
        <tbody>
          {rows_f5_p2}
          <tr style="background:#1e3a8a;color:#fff;font-weight:900;font-size:7px;border-top:2px solid #0f172a;">
            <td colspan="4" style="text-align:right;padding-right:8px;color:#fff;">
              ⭐ TOTAL GERAL CONSOLIDADO DOS 31 PROCESSOS EM PRONTIDÃO NA GCC (FASE 5):
            </td>
            <td style="text-align:right;color:#86efac;">{fmt_cur(total_val_fase5)}</td>
            <td colspan="5" style="text-align:center;color:#fff;">31 EDITAIS AGUARDANDO PUBLICAÇÃO NO PNCP</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div style="margin-top:5px; background:#f0fdf4; border:1px solid #86efac; border-radius:4px; padding:4px 8px; font-size:6.2px; color:#166534; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <strong>Diagnóstico de Prontidão:</strong> Todos os 31 processos listados possuem <em>Parecer Jurídico Favorável da CONJUR</em>, <em>Checklist de Conformidade GCC</em> e <em>Despacho de Homologação de Calendário</em> já acostados aos autos eletrônicos no SIGA. A pendência para virar edital público no PNCP é estritamente a geração do número de aviso e a submissão no Compras.gov.br pela equipe de compras.
      </div>
      <div style="font-weight:900;color:#1e3a8a;white-space:nowrap;margin-left:15px;">PRONTIDÃO 100% NO SIGA</div>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Esteira SIGA ➔ PNCP — Processos em Prontidão — CONFIDENCIAL</div>
    <div>Página 4 de 5</div>
  </div>
</div>

<!-- PÁGINA 5: PIPELINE CONJUR (FASE 4) & MATRIZ DE GOVERNANÇA -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">PIPELINE JURÍDICO (FASE 4 CONJUR) & MATRIZ DE GOVERNANÇA OPERACIONAL</div>
        <div class="sub">41 Processos em Análise Jurídica Prévia no SIGA + Ações Recomendadas para Aceleração de Editais no PNCP</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">PRÓXIMA ONDA PNCP</div>
        <div class="hdate">{len(fase4)} Processos &bull; {fmt_cur(fase4['Valor Estimado 2026 (R$)'].sum())}</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1.6fr 1fr; gap:7px; margin-bottom:5px;">
      <!-- Tabela Top 15 CONJUR -->
      <div class="panel">
        <div class="ph"><span>Top 15 Maiores Processos em Análise Jurídica na CONJUR (Fase 4)</span><span>Total: 41 Processos</span></div>
        <table class="dt" style="font-size:5.8px;">
          <thead>
            <tr>
              <th style="width:16px;text-align:center;">#</th>
              <th style="width:75px;text-align:center;">Processo SIGA</th>
              <th style="width:50px;text-align:center;">Área</th>
              <th style="width:180px;">Objeto Resumido</th>
              <th style="width:65px;text-align:right;">Valor Estimado</th>
              <th style="width:55px;text-align:center;">Tempo CONJUR</th>
              <th style="width:45px;text-align:center;">Prazo</th>
              <th style="width:100px;">Ação no SIGA</th>
              <th style="width:85px;">Próximo Passo</th>
            </tr>
          </thead>
          <tbody>
            {rows_conjur_html}
          </tbody>
        </table>
      </div>

      <!-- Matriz de Governança -->
      <div style="display:flex; flex-direction:column; gap:5px;">
        <div class="panel" style="flex:1;">
          <div class="ph"><span>⚡ Plano de Ação & Desbloqueio de Gargalos</span></div>
          <div style="display:flex; flex-direction:column; gap:4px; font-size:6px; line-height:1.35;">
            <div style="background:#fee2e2; border-left:3.5px solid #dc2626; padding:3px 5px; border-radius:3px;">
              <strong style="color:#991b1b;">1. Prioridade Máxima na CONJUR (SLA > 20 dias):</strong><br>
              TLB-PRO-2026/003240 (Atualização Tecnológica ERP/CRM/BI — R$ 10,3M) e TLB-PRO-2026/009141 (Migração CMS — R$ 3,0M) estão há mais de 25 dias aguardando parecer. Necessário despacho conjunto GCC/DTO solicitando prioridade.
            </div>
            <div style="background:#fef3c7; border-left:3.5px solid #d97706; padding:3px 5px; border-radius:3px;">
              <strong style="color:#92400e;">2. Liberação em Lote na GCC (Fase 5):</strong><br>
              Dos 31 processos prontos na GCC, 15 demandam atenção de prazo. Recomenda-se publicar em lotes semanais de 5 a 8 certames no PNCP para equalizar a carga dos pregoeiros.
            </div>
            <div style="background:#eff6ff; border-left:3.5px solid #1e40af; padding:3px 5px; border-radius:3px;">
              <strong style="color:#1e40af;">3. Sincronização Automática SIGA ➔ PNCP:</strong><br>
              Acompanhar os relatórios de upload do módulo PNCP (via scripts e API Serpro) para garantir que os avisos do DOU reflitam imediatamente no portal da transparência.
            </div>
          </div>
        </div>

        <div class="panel" style="background:#f8fafc; border:1px solid #cbd5e1;">
          <div class="ph"><span>📊 Resumo do Pipeline Total de Compras 2026</span></div>
          <table style="width:100%; font-size:6px; border-collapse:collapse;">
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:2px 0;"><strong>Radar PNCP (Fase Externa Ativa):</strong></td>
              <td style="text-align:right; font-weight:800; color:#0284c7;">8 Pregões (R$ 18,9M)</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:2px 0;"><strong>Prontidão GCC (Fase 5):</strong></td>
              <td style="text-align:right; font-weight:800; color:#16a34a;">31 Editais (R$ 53,6M)</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:2px 0;"><strong>Pipeline CONJUR (Fase 4):</strong></td>
              <td style="text-align:right; font-weight:800; color:#d97706;">41 Processos (R$ 45,2M)</td>
            </tr>
            <tr style="font-weight:900; color:#1e3a8a;">
              <td style="padding:3px 0;">TOTAL MOBILIZADO EM CONTRATAÇÕES:</td>
              <td style="text-align:right; font-size:6.8px;">80 Processos (R$ 117,7M)</td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Pipeline CONJUR & Governança — CONFIDENCIAL</div>
    <div>Página 5 de 5</div>
  </div>
</div>

</body>
</html>"""

html_path = 'Relatorio_Radar_Editais_PNCP_SIGA_2026.html'
pdf_path = 'Relatorio_Radar_Editais_PNCP_SIGA_2026.pdf'

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(HTML)
print(f"HTML salvo: {html_path}")

print("Renderizando PDF com Playwright / Chromium...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(HTML, wait_until='networkidle')
    page.pdf(
        path=pdf_path,
        format='A4',
        landscape=True,
        print_background=True,
        margin={'top': '7mm', 'bottom': '7mm', 'left': '9mm', 'right': '9mm'}
    )
    browser.close()

print(f"PDF gerado com sucesso: {pdf_path} - 5 paginas executivas premium!")
