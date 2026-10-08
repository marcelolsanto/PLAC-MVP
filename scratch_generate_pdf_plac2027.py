import os
import sys
import io
import base64
import openpyxl
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

print("[1/5] Carregando bases de dados para o PDF...")

# 1. Carregar Dados do Kanban 2026
wb_k = openpyxl.load_workbook('Z:/PLAC-MVP/BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx', data_only=True)
ws_k = wb_k['INVENTARIO_GERAL']
processos = []
for r in list(ws_k.iter_rows(values_only=True))[1:]:
    if r[1]:
        processos.append({
            'proc': str(r[1]).strip(),
            'cod_plac': str(r[2]).strip() if r[2] else 'EXTRAORDINÁRIO',
            'origem': str(r[3]).strip() if r[3] else 'EXTRAORDINÁRIO',
            'dir': str(r[4]).strip() if r[4] else 'NÃO INFORMADA',
            'ger': str(r[5]).strip() if r[5] else 'NÃO INFORMADA',
            'objeto': str(r[6]).strip() if r[6] else '',
            'val': float(r[7]) if r[7] and isinstance(r[7], (int, float)) else 0.0,
            'fase': str(r[9]).strip() if r[9] else '',
            'setor': str(r[10]).strip() if r[10] else '',
            'custodiante': str(r[11]).strip() if r[11] else '',
            'dias': int(r[12]) if r[12] and isinstance(r[12], (int, float)) else 0,
            'sla': int(r[13]) if r[13] and isinstance(r[13], (int, float)) else 0,
            'desvio': int(r[14]) if r[14] and isinstance(r[14], (int, float)) else 0,
            'status': str(r[15]).strip() if r[15] else '',
            'acao': str(r[17]).strip() if len(r) > 17 and r[17] else '',
            'prox_doc': str(r[19]).strip() if len(r) > 19 and r[19] else ''
        })

# 2. Carregar Contratos Vigentes
wb_v = openpyxl.load_workbook('Z:/PLAC-MVP/AUDITORIA_CONTRATOS_VIGENTES_2026_SIGA.xlsx', data_only=True)
ws_v = wb_v['CONTRATOS_VIGENTES_2026']
contratos = []
for r in list(ws_v.iter_rows(values_only=True))[1:]:
    if r[1]:
        contratos.append({
            'ctr': str(r[1]).strip(),
            'proc': str(r[2]).strip() if r[2] else '',
            'dir': str(r[3]).strip() if r[3] else '',
            'area': str(r[4]).strip() if r[4] else '',
            'modalidade': str(r[5]).strip() if r[5] else '',
            'ini': str(r[6])[:10] if r[6] else '',
            'fim': str(r[7])[:10] if r[7] else '',
            'val': float(r[8]) if r[8] and isinstance(r[8], (int, float)) else 0.0,
            'forn': str(r[11]).strip() if r[11] else '',
            'objeto': str(r[12]).strip() if r[12] else ''
        })

# 3. Carregar Calculadora T-120
wb_c = openpyxl.load_workbook('Z:/PLAC-MVP/CALCULADORA_PRAZOS_GESTAO_CONTRATUAL_SIGA.xlsx', data_only=True)
ws_t120 = wb_c['CALCULADORA_T120_ALERTAS']
t120_dict = {}
for r in list(ws_t120.iter_rows(values_only=True))[8:]:
    if len(r) > 13 and r[2]:
        t120_dict[str(r[2]).strip()] = {
            'marco_t120': str(r[11])[:10] if r[11] else '',
            'dias_t120': int(r[12]) if r[12] is not None and isinstance(r[12], (int, float)) else 0,
            'status': str(r[13]).strip() if r[13] else '',
            'acao': str(r[14]).strip() if len(r) > 14 and r[14] else ''
        }

procs_gcc = [p for p in processos if '2600' in p['setor'] or 'GCC' in p['setor'].upper()]
procs_dem = [p for p in processos if p not in procs_gcc and not ('CONJUR' in p['setor'].upper() or '1600' in p['setor'])]
procs_jur = [p for p in processos if 'CONJUR' in p['setor'].upper() or '1600' in p['setor']]

contratos_2026 = [c for c in contratos if '2026' in c['fim']]
contratos_2027 = [c for c in contratos if '2027' in c['fim']]
contratos_pos = [c for c in contratos if not ('2026' in c['fim'] or '2027' in c['fim'])]

print(f"[+] Total Processos: {len(processos)} (GCC: {len(procs_gcc)}, Demandantes: {len(procs_dem)}, CONJUR: {len(procs_jur)})")
print(f"[+] Total Contratos Vigentes: {len(contratos)} (Venc. 2026: {len(contratos_2026)}, Venc. 2027: {len(contratos_2027)}, Pós-2027: {len(contratos_pos)})")

# -------------------------------------------------------------
# GERAÇÃO DE GRÁFICOS MATPLOTLIB
# -------------------------------------------------------------
print("[2/5] Gerando gráficos de suporte...")
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# Gráfico 1: Distribuição dos Processos em Planejamento por Macro-Localização no SIGA
fig1, ax1 = plt.subplots(figsize=(5.5, 2.5), dpi=200)
locais = ['GCC (Mesa 2600)', 'Demandantes (Fases 1-3)', 'CONJUR (Fase 4)']
qtds_locais = [len(procs_gcc), len(procs_dem), len(procs_jur)]
vals_locais_m = [sum(p['val'] for p in procs_gcc)/1e6, sum(p['val'] for p in procs_dem)/1e6, sum(p['val'] for p in procs_jur)/1e6]
colors_loc = ['#0284c7', '#0f766e', '#8b5cf6']

bars1 = ax1.bar(locais, vals_locais_m, color=colors_loc, width=0.45)
ax1.set_ylabel('Volume Financeiro (R$ Milhões)', fontsize=7.5, fontweight='bold', color='#1e293b')
ax1.set_title('Distribuição da Carteira de Planejamento (R$ 300,5M)', fontsize=8.5, fontweight='bold', pad=10, color='#0f172a')
ax1.tick_params(axis='x', labelsize=7.5)
ax1.tick_params(axis='y', labelsize=7)

for b, q, v in zip(bars1, qtds_locais, vals_locais_m):
    h = b.get_height()
    ax1.text(b.get_x() + b.get_width()/2, h + 2, f"{q} procs\nR$ {v:.1f}M", ha='center', va='bottom', fontsize=6.8, fontweight='bold', color='#0f172a')

plt.tight_layout()
buf1 = io.BytesIO()
plt.savefig(buf1, format='png', bbox_inches='tight', transparent=True)
buf1.seek(0)
chart1_b64 = base64.b64encode(buf1.read()).decode('utf-8')
plt.close()

# Gráfico 2: Vigência dos Contratos Ativos e Transição para o PLAC 2027
fig2, ax2 = plt.subplots(figsize=(5.5, 2.5), dpi=200)
sizes_vig = [len(contratos_2026), len(contratos_2027), len(contratos_pos)]
labels_vig = [
    f"Vencem em 2026\n({len(contratos_2026)} CTRs | R${sum(c['val'] for c in contratos_2026)/1e6:.1f}M)",
    f"Vencem em 2027\n({len(contratos_2027)} CTRs | R${sum(c['val'] for c in contratos_2027)/1e6:.1f}M)",
    f"Plurianuais Pós-2027\n({len(contratos_pos)} CTRs)"
]
colors_vig = ['#ef4444', '#f59e0b', '#10b981']

wedges, texts, autotexts = ax2.pie(
    sizes_vig, labels=labels_vig, colors=colors_vig, autopct='%1.1f%%', startangle=140,
    wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
    textprops={'fontsize': 6.8, 'color': '#0f172a'},
    pctdistance=0.75
)
for at in autotexts:
    at.set_fontsize(6.8)
    at.set_weight('bold')
    at.set_color('#ffffff')

ax2.set_title('Contratos Vigentes: Calendário de Expiração e PLAC 2027', fontsize=8.5, fontweight='bold', pad=10, color='#0f172a')
plt.tight_layout()
buf2 = io.BytesIO()
plt.savefig(buf2, format='png', bbox_inches='tight', transparent=True)
buf2.seek(0)
chart2_b64 = base64.b64encode(buf2.read()).decode('utf-8')
plt.close()

print("[+] Gráficos gerados com sucesso!")

# -------------------------------------------------------------
# MONTAGEM DO HTML COM 5 PÁGINAS A4 LANDSCAPE
# -------------------------------------------------------------
print("[3/5] Construindo HTML diagramado...")

def fmt_cur(v):
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    size: A4 landscape;
    margin: 8mm 9mm 8mm 9mm;
  }}
  * {{
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  body {{
    margin: 0;
    padding: 0;
    color: #0f172a;
    background-color: #ffffff;
    font-size: 8pt;
    line-height: 1.3;
  }}
  .page {{
    width: 100%;
    height: 190mm;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}
  .page:last-child {{
    page-break-after: avoid;
  }}
  .header {{
    border-bottom: 2px solid #0f172a;
    padding-bottom: 4px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}
  .header-left h1 {{
    margin: 0;
    font-size: 12pt;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #0f172a;
    text-transform: uppercase;
  }}
  .header-left h2 {{
    margin: 2px 0 0 0;
    font-size: 8.5pt;
    font-weight: 600;
    color: #0284c7;
    text-transform: uppercase;
  }}
  .header-right {{
    text-align: right;
    font-size: 7.2pt;
    color: #64748b;
    font-weight: 500;
  }}
  .footer {{
    border-top: 1px solid #cbd5e1;
    padding-top: 4px;
    margin-top: 5px;
    display: flex;
    justify-content: space-between;
    font-size: 6.8pt;
    color: #64748b;
  }}
  .kpi-row {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
    margin-bottom: 6px;
  }}
  .kpi-card {{
    background: #0f172a;
    color: #ffffff;
    border-radius: 4px;
    padding: 6px 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06);
  }}
  .kpi-card.alert-blue {{ background: #1e3a8a; }}
  .kpi-card.alert-teal {{ background: #0f766e; }}
  .kpi-card.alert-red {{ background: #991b1b; }}
  .kpi-card.alert-amber {{ background: #d97706; }}
  .kpi-card-title {{
    font-size: 6.5pt;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    opacity: 0.85;
    font-weight: 700;
  }}
  .kpi-card-val {{
    font-size: 11.5pt;
    font-weight: 800;
    margin: 1.5px 0;
    letter-spacing: -0.3px;
  }}
  .kpi-card-desc {{
    font-size: 6.5pt;
    opacity: 0.85;
  }}
  .section-title {{
    font-size: 8.5pt;
    font-weight: 800;
    color: #0f172a;
    margin: 4px 0 3px 0;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .section-title span {{ color: #0284c7; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 6.8pt;
    margin-bottom: 4px;
  }}
  th {{
    background: #1e293b;
    color: #ffffff;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 6.3pt;
    letter-spacing: 0.3px;
    padding: 3.5px 4px;
    text-align: left;
    border: 1px solid #334155;
  }}
  th.center, td.center {{ text-align: center; }}
  th.right, td.right {{ text-align: right; }}
  td {{
    padding: 3px 4px;
    border: 1px solid #e2e8f0;
    color: #1e293b;
  }}
  tr:nth-child(even) td {{
    background-color: #f8fafc;
  }}
  .badge {{
    display: inline-block;
    padding: 1.5px 4px;
    border-radius: 3px;
    font-size: 6pt;
    font-weight: 700;
    text-align: center;
    text-transform: uppercase;
  }}
  .badge-red {{ background: #fee2e2; color: #991b1b; }}
  .badge-yellow {{ background: #fef3c7; color: #92400e; }}
  .badge-green {{ background: #dcfce7; color: #166534; }}
  .badge-blue {{ background: #e0f2fe; color: #0369a1; }}
  .callout {{
    background: #f8fafc;
    border-left: 3px solid #0284c7;
    padding: 4px 7px;
    font-size: 6.8pt;
    color: #334155;
    margin: 3px 0;
    border-radius: 0 3px 3px 0;
  }}
  .callout-alert {{
    background: #fff1f2;
    border-left: 3px solid #e11d48;
    color: #881337;
  }}
  .box-container {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    margin-bottom: 5px;
  }}
  .box-info {{
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 5px 7px;
  }}
  .box-info-title {{
    font-weight: 800;
    font-size: 7.2pt;
    color: #1e3a8a;
    margin-bottom: 2px;
  }}
</style>
</head>
<body>

<!-- PÁGINA 1: VISÃO EXECUTIVA E ESTEIRA DO PLAC 2027 -->
<div class="page">
  <div>
    <div class="header">
      <div class="header-left">
        <h1>Telecomunicações Brasileiras S.A. — Telebras</h1>
        <h2>Relatório Integrado: Esteira PLAC 2027, Processos no SIGA e Gestão Contratual</h2>
      </div>
      <div class="header-right">
        Gerência de Compras e Contratos (GCC / DAFRI)<br>
        Referência: 08/10/2026 | Universo: PLAC 2026 & PLAC 2027
      </div>
    </div>

    <div class="kpi-row">
      <div class="kpi-card alert-blue">
        <div class="kpi-card-title">Mesa da GCC (Setor 2600)</div>
        <div class="kpi-card-val">34 processos</div>
        <div class="kpi-card-desc">R$ 53,95M (31 na Fase 5 prontos)</div>
      </div>
      <div class="kpi-card alert-teal">
        <div class="kpi-card-title">Setores Demandantes</div>
        <div class="kpi-card-val">111 processos</div>
        <div class="kpi-card-desc">R$ 201,31M em elaboração</div>
      </div>
      <div class="kpi-card alert-blue">
        <div class="kpi-card-title">Assessoria Jurídica CONJUR</div>
        <div class="kpi-card-val">41 processos</div>
        <div class="kpi-card-desc">R$ 45,21M em exame de legalidade</div>
      </div>
      <div class="kpi-card alert-red">
        <div class="kpi-card-title">Vigentes: Fim em 2026</div>
        <div class="kpi-card-val">18 contratos</div>
        <div class="kpi-card-desc">R$ 25,28M (Ação Imediata T-120)</div>
      </div>
      <div class="kpi-card alert-amber">
        <div class="kpi-card-title">Vigentes: Fim em 2027</div>
        <div class="kpi-card-val">14 contratos</div>
        <div class="kpi-card-desc">R$ 21,85M (Mandatório no PLAC 2027)</div>
      </div>
    </div>

    <div class="section-title">1. Arquitetura Operacional da Esteira de Fluxo do PLAC 2027</div>
    <div class="callout">
      A <b>Esteira de Planejamento do PLAC 2027</b> da Telebras estabelece o padrão em <b>6 Blocos Normativos</b> para levantamento, priorização e sincronização de demandas no SIGA. Seu núcleo reside no <b>Cronograma Reverso Regimental</b>: toda contratação tem sua <i>Data-Limite de Envio à GCC</i> calculada retroativamente a partir da <i>Data Pretendida de Assinatura</i>, descontando o SLA operacional da modalidade licitatória.
    </div>

    <div class="box-container">
      <div class="box-info">
        <div class="box-info-title">1. BLOCOS DE IDENTIFICAÇÃO & OBJETO</div>
        <div style="font-size:6.6pt; color:#334155;">
          • <b>Bloco 1:</b> Área demandante, gerente e fiscal do registro.<br>
          • <b>Bloco 2:</b> Natureza (Nova vs. Renovação de Vigente), código CATMAT/CATSER, vinculação com processo SIGA e metas do PEI.<br>
          • <i>Regra de Ouro:</i> Contratos vigentes que expiram em 2027 devem ser amarrados no campo de histórico.
        </div>
      </div>
      <div class="box-info">
        <div class="box-info-title">2. CRONOGRAMA REVERSO & ALERTA</div>
        <div style="font-size:6.6pt; color:#334155;">
          • <b>Data Fatal Abertura SIGA:</b> Limite para a área formalizar o DFD.<br>
          • <b>SLA GCC:</b> Pregão Eletrônico (31 d.u.), Dispensa (15 d.u.), Inexigibilidade (20 d.u.).<br>
          • <b>Alerta de Antecipação:</b> Célula vermelha quando a data-limite recai ainda em 2026, exigindo autuação imediata.
        </div>
      </div>
      <div class="box-info">
        <div class="box-info-title">3. MATRIZ DE PRIORIZAÇÃO (ANEXO II)</div>
        <div style="font-size:6.6pt; color:#334155;">
          • <b>Fórmula:</b> (F1 × 30) + (F2 × 30) + (F3 × 25) + (F4 × 15).<br>
          • <b>F1:</b> Criticidade atividade-fim | <b>F2:</b> Risco descontinuidade (nota 5 se vence em 2027).<br>
          • <b>F3:</b> Obrigação legal | <b>F4:</b> Materialidade financeira.<br>
          • <b>Classificação:</b> Alto (380-500), Médio (240-379), Baixo (100-239).
        </div>
      </div>
    </div>

    <div class="section-title">2. Gráficos Comparativos: Esteira no SIGA e Calendário de Contratos</div>
    <div style="display:flex; gap:8px; margin-top:2px;">
      <div style="flex:1; border:1px solid #e2e8f0; border-radius:4px; padding:4px; text-align:center;">
        <img src="data:image/png;base64,{chart1_b64}" style="width:100%; max-height:135px; object-fit:contain;">
      </div>
      <div style="flex:1; border:1px solid #e2e8f0; border-radius:4px; padding:4px; text-align:center;">
        <img src="data:image/png;base64,{chart2_b64}" style="width:100%; max-height:135px; object-fit:contain;">
      </div>
    </div>
  </div>

  <div class="footer">
    <span>TELEBRAS — Gerência de Compras e Contratos (GCC / DAFRI)</span>
    <span>Relatório Integrado PLAC 2026/2027 | Página 1 de 5</span>
  </div>
</div>

<!-- PÁGINA 2: PROCESSOS EM PLANEJAMENTO NA GCC (SETOR 2600) -->
<div class="page">
  <div>
    <div class="header">
      <div class="header-left">
        <h1>Telecomunicações Brasileiras S.A. — Telebras</h1>
        <h2>Fase de Planejamento: Processos Tramitando na Mesa da GCC (Setor 2600)</h2>
      </div>
      <div class="header-right">
        Lotação: 2600 (GCC / Licitações)<br>
        Total na Mesa: 34 Processos (R$ 53.947.230,87)
      </div>
    </div>

    <div class="section-title">1. Diagnóstico da Mesa da GCC: Prontidão para Publicação no PNCP</div>
    <div class="callout">
      A GCC custodia atualmente <b>34 processos de planejamento</b>. Destes, <b>31 processos pertencem à Fase 5 (Triagem & Prontidão)</b>, já tendo superado a análise jurídica da CONJUR e a instrução técnica preparatória. O valor total represado na mesa aguardando minuta de edital e publicação é de <b>R$ 53,63 milhões</b>, sendo que 91% pertencem à Diretoria Técnico-Operacional (DTO).
    </div>

    <div class="section-title">2. Rol Analítico dos Processos em Tramitação na GCC (Setor 2600)</div>
    <table>
      <thead>
        <tr>
          <th>Processo SIGA</th>
          <th>Código PLAC</th>
          <th>Diretoria</th>
          <th>Gerência</th>
          <th>Objeto Resumido</th>
          <th class="right">Valor Estimado (R$)</th>
          <th class="center">Fase Kanban</th>
          <th class="center">Dias GCC</th>
          <th class="center">SLA</th>
          <th class="center">Status</th>
          <th>Próxima Ação / Pendência</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>TLB-PRO-2026/005064</b></td>
          <td>3200-GPTC_01</td>
          <td>DTO</td>
          <td>GPTC</td>
          <td>Expansão e Suporte Rede Móvel Privativa RMSDF...</td>
          <td class="right"><b>R$ 10.000.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">18d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-yellow">ATENÇÃO</span></td>
          <td>Elaborar Minuta de Edital / Lançar no PNCP</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/002172</b></td>
          <td>3100-GEOP_02</td>
          <td>DTO</td>
          <td>GEOP</td>
          <td>Manutenção de Torres e Infraestrutura Física...</td>
          <td class="right"><b>R$ 9.600.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">22d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-yellow">ATENÇÃO</span></td>
          <td>Publicação Imediata do Edital de Licitação</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/004664</b></td>
          <td>3500-GORS_01</td>
          <td>DTO</td>
          <td>GORS</td>
          <td>Enlaces e Conectividade Amazônia Conectada...</td>
          <td class="right"><b>R$ 8.000.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">14d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-green">NO PRAZO</span></td>
          <td>Conferência Final de Conformidade GCC</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/003102</b></td>
          <td>3700-GTI_01</td>
          <td>DTO</td>
          <td>GTI</td>
          <td>Licenciamento Nuvem Híbrida e Virtualização...</td>
          <td class="right"><b>R$ 4.500.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">11d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-green">NO PRAZO</span></td>
          <td>Publicar no PNCP e Marcar Sessão</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/001890</b></td>
          <td>3600-GINF_02</td>
          <td>DTO</td>
          <td>GINF</td>
          <td>Energia Crítica e Nobreaks para Datacenters...</td>
          <td class="right"><b>R$ 3.800.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">19d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-yellow">ATENÇÃO</span></td>
          <td>Ajustar Minuta de Edital com Pregoeiro</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/006120</b></td>
          <td>2200-GLOG_03</td>
          <td>DAF</td>
          <td>GLOG</td>
          <td>Vigilância Armada e Segurança Patrimonial...</td>
          <td class="right"><b>R$ 2.400.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">9d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-green">NO PRAZO</span></td>
          <td>Publicar Aviso de Licitação no DOU/PNCP</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/007412</b></td>
          <td>3200-GPTC_03</td>
          <td>DTO</td>
          <td>GPTC</td>
          <td>Roteadores de Borda e Switches Core IP/MPLS...</td>
          <td class="right"><b>R$ 2.100.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">26d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-yellow">ATENÇÃO</span></td>
          <td>Pauta Prioritária GCC / Agendar Sessão</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/004210</b></td>
          <td>3400-GERP_02</td>
          <td>DTO</td>
          <td>GERP</td>
          <td>Cabos Ópticos e Acessórios de Rede Terrestre...</td>
          <td class="right"><b>R$ 1.850.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">8d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-green">NO PRAZO</span></td>
          <td>Minuta de Edital em Elaboração</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/002890</b></td>
          <td>1100-GAB_PR</td>
          <td>PR</td>
          <td>GAB PR</td>
          <td>Consultoria em Governança Corporativa e ESG...</td>
          <td class="right"><b>R$ 950.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">8d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-green">NO PRAZO</span></td>
          <td>Publicar no PNCP</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/003880</b></td>
          <td>3300-GEC_01</td>
          <td>DTO</td>
          <td>GEC</td>
          <td>Aparelhos de Medição e Certificação de Fibra...</td>
          <td class="right"><b>R$ 820.000,00</b></td>
          <td class="center">5. Prontidão GCC</td>
          <td class="center">12d</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-yellow">ATENÇÃO</span></td>
          <td>Homologar Calendário da GCC</td>
        </tr>
        <tr>
          <td><b>Demais 24 Processos na GCC</b></td>
          <td>Vários</td>
          <td>Mistas</td>
          <td>Várias</td>
          <td>Serviços de TI, Licenças, Infraestrutura e Apoio...</td>
          <td class="right">R$ 9.927.230,87</td>
          <td class="center">Fases 1, 2 e 5</td>
          <td class="center">Var.</td>
          <td class="center">10d</td>
          <td class="center"><span class="badge badge-blue">REGULAR</span></td>
          <td>Conferência, Triagem e Lançamento</td>
        </tr>
        <tr style="background:#f1f5f9; font-weight:bold;">
          <td>TOTAL NA GCC (SETOR 2600)</td>
          <td colspan="4">34 Processos sob custódia da GCC</td>
          <td class="right">R$ 53.947.230,87</td>
          <td class="center">—</td>
          <td class="center">10,5d média</td>
          <td class="center">—</td>
          <td class="center"><span class="badge badge-yellow">15 EM ATENÇÃO</span></td>
          <td>Meta: Lançar editais até 20/10/2026</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="footer">
    <span>TELEBRAS — Gerência de Compras e Contratos (GCC / DAFRI)</span>
    <span>Relatório Integrado PLAC 2026/2027 | Página 2 de 5</span>
  </div>
</div>

<!-- PÁGINA 3: PROCESSOS NOS SETORES DEMANDANTES E RESPONSÁVEIS -->
<div class="page">
  <div>
    <div class="header">
      <div class="header-left">
        <h1>Telecomunicações Brasileiras S.A. — Telebras</h1>
        <h2>Fase de Planejamento: Processos nos Setores Demandantes e Responsáveis</h2>
      </div>
      <div class="header-right">
        Localização: Áreas Técnicas Requisitantes<br>
        Total nos Demandantes: 111 Processos (R$ 201.308.524,20)
      </div>
    </div>

    <div class="section-title">1. Distribuição da Carga de Planejamento por Diretoria Demandante</div>
    <table>
      <thead>
        <tr>
          <th>Diretoria Requisitante</th>
          <th class="center">Qtd Processos</th>
          <th class="right">Volume Estimado (R$)</th>
          <th class="center">% Volume</th>
          <th class="center">Processos Críticos</th>
          <th>Gerências Demandantes Atuantes</th>
          <th>Diagnóstico do Represamento</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>3000 — Diretoria Técnico-Operacional (DTO)</b></td>
          <td class="center"><b>63</b></td>
          <td class="right"><b>R$ 152.383.943,76</b></td>
          <td class="center"><b>75,7%</b></td>
          <td class="center"><span class="badge badge-red">16</span></td>
          <td>3100-GPEI, 3400-GERP, 3700-GTI, 3820-GEOS, 3200-GPTC</td>
          <td>Maior gargalo em ETP, matriz de riscos e cotações IN 65.</td>
        </tr>
        <tr>
          <td><b>1000 — Presidência (PR)</b></td>
          <td class="center"><b>9</b></td>
          <td class="right">R$ 20.276.721,60</td>
          <td class="center">10,1%</td>
          <td class="center"><span class="badge badge-red">3</span></td>
          <td>1100-GAB PR, ASCOM, OUVID</td>
          <td>Destaque: Publicidade Institucional (R$ 15,0M com 55d no setor).</td>
        </tr>
        <tr>
          <td><b>2000 — Diretoria Administrativo-Financeira (DAF)</b></td>
          <td class="center"><b>14</b></td>
          <td class="right">R$ 13.315.388,83</td>
          <td class="center">6,6%</td>
          <td class="center"><span class="badge badge-yellow">3</span></td>
          <td>2500-GGP, 2200-GLOG, 2100-GCL, 2300-GAF</td>
          <td>Demandas de RH, medicina ocupacional e facilities prediais.</td>
        </tr>
        <tr>
          <td><b>4000 — Diretoria Comercial (DC)</b></td>
          <td class="center"><b>18</b></td>
          <td class="right">R$ 9.851.460,21</td>
          <td class="center">4,9%</td>
          <td class="center"><span class="badge badge-yellow">3</span></td>
          <td>4500-GROP, 4200-GCOM, 4100-GPAR</td>
          <td>Serviços de apoio à comercialização e canais de atendimento.</td>
        </tr>
        <tr>
          <td><b>4000 — Infraestrutura Corporativa DAF</b></td>
          <td class="center"><b>1</b></td>
          <td class="right">R$ 4.200.000,00</td>
          <td class="center">2,1%</td>
          <td class="center"><span class="badge badge-green">1</span></td>
          <td>2200-GLOG / Infraestrutura</td>
          <td>Obras civis e adequação de subestações regionais.</td>
        </tr>
        <tr>
          <td><b>5000 — Diretoria de Governança (DG)</b></td>
          <td class="center"><b>6</b></td>
          <td class="right">R$ 1.285.716,67</td>
          <td class="center">0,6%</td>
          <td class="center"><span class="badge badge-green">1</span></td>
          <td>5100-GAUD, 5200-GCOV, GECAD</td>
          <td>Auditoria independente, software de compliance e consultoria.</td>
        </tr>
      </tbody>
    </table>

    <div class="section-title">2. Top 8 Processos com Gargalos Severos nas Gerências Técnicas</div>
    <table>
      <thead>
        <tr>
          <th>Processo SIGA</th>
          <th>Gerência Demandante</th>
          <th>Objeto da Demanda</th>
          <th class="right">Valor Estimado (R$)</th>
          <th class="center">Fase Atual</th>
          <th class="center">Dias no Setor</th>
          <th class="center">SLA Meta</th>
          <th class="center">Desvio</th>
          <th>Gargalo Apurado & Diretriz de Desbloqueio</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>TLB-PRO-2026/002407</b></td>
          <td>3100-GPEI</td>
          <td>Projeto RPCAPF — Rede Fixa (RAAPF)...</td>
          <td class="right"><b>R$ 27.986.994,12</b></td>
          <td class="center">3. Pesquisa/TR</td>
          <td class="center">37d</td>
          <td class="center">20d</td>
          <td class="center"><span class="badge badge-red">+17d</span></td>
          <td>Falta de 3 cotações. Utilizar compras similares do PNCP.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2025/006752</b></td>
          <td>1100-GAB PR</td>
          <td>Serviço de Publicidade e Comunicação...</td>
          <td class="right"><b>R$ 15.000.000,00</b></td>
          <td class="center">2. ETP & Riscos</td>
          <td class="center">55d</td>
          <td class="center">35d</td>
          <td class="center"><span class="badge badge-red">+20d</span></td>
          <td>Ajuste na Matriz de Riscos e Despacho da Presidência.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2025/007412</b></td>
          <td>4100-GSI</td>
          <td>Serviços Continuados SOC Cibernético...</td>
          <td class="right"><b>R$ 4.200.000,00</b></td>
          <td class="center">3. Pesquisa/TR</td>
          <td class="center">34d</td>
          <td class="center">20d</td>
          <td class="center"><span class="badge badge-red">+14d</span></td>
          <td>Finalizar mapa de cotações com o apoio da GCC.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2026/009528</b></td>
          <td>3400-GERP</td>
          <td>Extensão e Infraestrutura Elétrica...</td>
          <td class="right"><b>R$ 3.000.000,00</b></td>
          <td class="center">3. Pesquisa/TR</td>
          <td class="center">37d</td>
          <td class="center">20d</td>
          <td class="center"><span class="badge badge-red">+17d</span></td>
          <td>Concluir TR e enviar para análise jurídica CONJUR.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2025/002330</b></td>
          <td>3200-GPTC</td>
          <td>Aquisição de Sistema DCIM Datacenter...</td>
          <td class="right"><b>R$ 2.000.000,00</b></td>
          <td class="center">3. Pesquisa/TR</td>
          <td class="center">32d</td>
          <td class="center">20d</td>
          <td class="center"><span class="badge badge-red">+12d</span></td>
          <td>Emitir despacho de encerramento da fase de cotação.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2025/008942</b></td>
          <td>3500-GORS</td>
          <td>Peças de Reposição RF e Amplificadores SSPA...</td>
          <td class="right"><b>R$ 1.850.000,00</b></td>
          <td class="center">2. ETP & Riscos</td>
          <td class="center">48d</td>
          <td class="center">35d</td>
          <td class="center"><span class="badge badge-red">+13d</span></td>
          <td>Validação técnica de especificação internacional.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2025/005090</b></td>
          <td>3100-GPEI</td>
          <td>Projeto RPCAPF Meios de Comunicação...</td>
          <td class="right"><b>R$ 1.729.808,17</b></td>
          <td class="center">3. Pesquisa/TR</td>
          <td class="center">32d</td>
          <td class="center">20d</td>
          <td class="center"><span class="badge badge-red">+12d</span></td>
          <td>Remeter autos à CONJUR.</td>
        </tr>
        <tr>
          <td><b>TLB-PRO-2025/008293</b></td>
          <td>3700-GTI</td>
          <td>Solução de Visibilidade e Segurança...</td>
          <td class="right"><b>R$ 1.090.005,50</b></td>
          <td class="center">2. ETP & Riscos</td>
          <td class="center">51d</td>
          <td class="center">35d</td>
          <td class="center"><span class="badge badge-red">+16d</span></td>
          <td>Aprovação interna do Gerente da GTI pendente.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="footer">
    <span>TELEBRAS — Gerência de Compras e Contratos (GCC / DAFRI)</span>
    <span>Relatório Integrado PLAC 2026/2027 | Página 3 de 5</span>
  </div>
</div>

<!-- PÁGINA 4: GESTÃO CONTRATUAL: CONTRATOS VIGENTES E TRANSIÇÃO PLAC 2027 -->
<div class="page">
  <div>
    <div class="header">
      <div class="header-left">
        <h1>Telecomunicações Brasileiras S.A. — Telebras</h1>
        <h2>Gestão Contratual: Contratos Vigentes e Alimentação do PLAC 2027</h2>
      </div>
      <div class="header-right">
        Base: 87 Contratos Ativos Auditados<br>
        Vigência: 2026, 2027 e Plurianuais Pós-2027
      </div>
    </div>

    <div class="section-title">1. Cruzamento Estratégico: Gestão de Vigência vs. Planejamento 2027</div>
    <div class="callout">
      A gestão dos contratos vigentes é o elo direto que alimenta a esteira do PLAC 2027. Dos <b>87 contratos auditados</b>, exatamente <b>14 contratos expiram ao longo de 2027 (R$ 21,85M)</b> e devem ser obrigatoriamente incluídos no <i>Levantamento de Necessidades do PLAC 2027</i> com nota máxima no <b>Fator F2 (Risco de Descontinuidade)</b>. Outros <b>18 contratos vencem ainda em 2026 (R$ 25,28M)</b> e requerem prorrogação imediata via aditivo no SIGA.
    </div>

    <div class="section-title">2. Contratos com Término em 2027 (Inclusão Mandatória no PLAC 2027)</div>
    <table>
      <thead>
        <tr>
          <th>Nº Contrato</th>
          <th>Processo SIGA</th>
          <th>Diretoria / Área</th>
          <th>Fornecedor</th>
          <th>Objeto Contratado</th>
          <th class="right">Valor Anual (R$)</th>
          <th class="center">Término</th>
          <th class="center">Status Fator F2</th>
          <th>Diretriz Obrigatória no PLAC 2027</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>TLB-CTR-2025/00089</b></td>
          <td>TLB-PRO-2025/00142</td>
          <td>DG / GIRC</td>
          <td>IMPAKT CONSULTORIA SS LTDA</td>
          <td>Consultoria especializada em auditoria contábil...</td>
          <td class="right">R$ 1.840.000,00</td>
          <td class="center">05/01/2027</td>
          <td class="center"><span class="badge badge-red">F2 = NOTA 5</span></td>
          <td>Cadastrar no Bloco 2 como Renovação de Vigente no PLAC 2027.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2026/00036</b></td>
          <td>TLB-PRO-2025/00881</td>
          <td>DAF / GCONT</td>
          <td>METRÓPOLE AUDITORES INDEPENDENTES</td>
          <td>Auditoria independente das demonstrações financeiras...</td>
          <td class="right">R$ 1.450.000,00</td>
          <td class="center">02/01/2027</td>
          <td class="center"><span class="badge badge-red">F2 = NOTA 5</span></td>
          <td>Exigência legal CVM. Abrir processo no SIGA em nov/2026.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2026/00010</b></td>
          <td>TLB-PRO-2025/00412</td>
          <td>DTO / GEOS</td>
          <td>ROLLS ROYCE SOLUTIONS BRASIL</td>
          <td>Manutenção de geradores e sistemas de força crítica...</td>
          <td class="right">R$ 2.890.000,00</td>
          <td class="center">22/01/2027</td>
          <td class="center"><span class="badge badge-red">F2 = NOTA 5</span></td>
          <td>Indispensável à estação satelital. Prioridade Alta (P500).</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2026/00047</b></td>
          <td>TLB-PRO-2025/00912</td>
          <td>DTO / GINF</td>
          <td>MAUFE TELAS COMÉRCIO E SERVIÇOS</td>
          <td>Proteção física e cercamento perimetral de estações...</td>
          <td class="right">R$ 680.000,00</td>
          <td class="center">23/01/2027</td>
          <td class="center"><span class="badge badge-red">F2 = NOTA 5</span></td>
          <td>Avaliar vantajabilidade de prorrogação ou nova licitação.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2025/00072</b></td>
          <td>TLB-PRO-2024/00551</td>
          <td>DTO / GTI</td>
          <td>ORACLE DO BRASIL SISTEMAS LTDA</td>
          <td>Suporte técnico e licenças corporativas de banco de dados...</td>
          <td class="right">R$ 4.250.000,00</td>
          <td class="center">15/04/2027</td>
          <td class="center"><span class="badge badge-red">F2 = NOTA 5</span></td>
          <td>Inexigibilidade de renovação. Envio à GCC até fev/2027.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2025/00095</b></td>
          <td>TLB-PRO-2024/00788</td>
          <td>DAF / GLOG</td>
          <td>ALGAR TELECOM S/A</td>
          <td>Links de conectividade e redundância dos prédios...</td>
          <td class="right">R$ 3.120.000,00</td>
          <td class="center">30/05/2027</td>
          <td class="center"><span class="badge badge-red">F2 = NOTA 5</span></td>
          <td>Pregão Eletrônico SRP. Lançar no cronograma reverso do Q2/2027.</td>
        </tr>
        <tr>
          <td><b>Demais 8 Contratos de 2027</b></td>
          <td>Vários</td>
          <td>DTO / DAF</td>
          <td>Fornecedores homologados</td>
          <td>Serviços contínuos prediais, links e apoio operacional...</td>
          <td class="right">R$ 7.621.487,17</td>
          <td class="center">2027</td>
          <td class="center"><span class="badge badge-yellow">ALTO RISCO</span></td>
          <td>Inclusão compulsória no Levantamento de Necessidades 2027.</td>
        </tr>
        <tr style="background:#f1f5f9; font-weight:bold;">
          <td>TOTAL VENCIMENTO EM 2027</td>
          <td colspan="4">14 Contratos que impactam a esteira do PLAC 2027</td>
          <td class="right">R$ 21.851.487,17</td>
          <td class="center">—</td>
          <td class="center"><span class="badge badge-red">MANDATÓRIO</span></td>
          <td>Meta: 100% cadastrados no PLAC 2027 pelas áreas</td>
        </tr>
      </tbody>
    </table>

    <div class="section-title">3. Contratos com Término em 2026 (Transição Emergencial / Q1 2027)</div>
    <div class="callout callout-alert">
      <b>Atenção Gestores:</b> Os <b>18 contratos que vencem em 2026 (R$ 25,28M)</b> estão com o limite temporal exíguo. Aqueles que não admitirem mais prorrogação (limite de 5 anos do art. 71 da Lei 13.303) devem ter nova licitação inserida imediatamente no <b>Q1/2027 do PLAC</b> com regime de fast-track para evitar descontinuidade operacional nos serviços da Telebras.
    </div>
  </div>

  <div class="footer">
    <span>TELEBRAS — Gerência de Compras e Contratos (GCC / DAFRI)</span>
    <span>Relatório Integrado PLAC 2026/2027 | Página 4 de 5</span>
  </div>
</div>

<!-- PÁGINA 5: ALERTAS T-120 E DIRETRIZES DE GOVERNANÇA -->
<div class="page">
  <div>
    <div class="header">
      <div class="header-left">
        <h1>Telecomunicações Brasileiras S.A. — Telebras</h1>
        <h2>Alertas do Marco Legal T-120 e Plano de Desbloqueio da Governança</h2>
      </div>
      <div class="header-right">
        Conformidade: Lei 13.303/2016 e RILC Telebras<br>
        Ações Imediatas para Fiscais e Gestores
      </div>
    </div>

    <div class="section-title">1. Matriz Crítica: Contratos com Marco T-120 Dias Vencido no SIGA</div>
    <table>
      <thead>
        <tr>
          <th>Contrato SIGA</th>
          <th>Processo SIGA</th>
          <th>Fornecedor Contratado</th>
          <th class="center">Término</th>
          <th class="center">Marco T-120</th>
          <th class="center">Dias de Estouro</th>
          <th class="center">Status Operacional</th>
          <th>Ação Emergencial de Governança</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><b>TLB-CTR-2026/00009</b></td>
          <td>TLB-PRO-2025/05495</td>
          <td>ROL SOLUÇÕES PREDIAIS LTDA</td>
          <td class="center">03/02/2026</td>
          <td class="center">06/10/2025</td>
          <td class="center">-358 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Autuação imediata de prorrogação ou contratação emergencial.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2025/00007</b></td>
          <td>TLB-PRO-2024/02695</td>
          <td>EXEMPLUS COMUNICAÇÃO E MKT</td>
          <td class="center">07/02/2026</td>
          <td class="center">10/10/2025</td>
          <td class="center">-354 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Relatório de fiscalização técnica e minuta de termo aditivo.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2026/00015</b></td>
          <td>TLB-PRO-2024/02695</td>
          <td>VIVER EVENTOS LTDA</td>
          <td class="center">13/02/2026</td>
          <td class="center">16/10/2025</td>
          <td class="center">-348 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Auditoria de vantajabilidade econômica frente aos preços de mercado.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2024/00006</b></td>
          <td>TLB-PRO-2023/06316</td>
          <td>HC COMUNICAÇÃO DE DADOS LTDA</td>
          <td class="center">01/03/2026</td>
          <td class="center">01/11/2025</td>
          <td class="center">-332 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Serviço contínuo de rede. Remeter minuta de aditivo à CONJUR.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2024/00007</b></td>
          <td>TLB-PRO-2023/06327</td>
          <td>HC COMUNICAÇÃO DE DADOS LTDA</td>
          <td class="center">01/03/2026</td>
          <td class="center">01/11/2025</td>
          <td class="center">-332 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Certidão trabalhista e instrução de termo aditivo tempestivo.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2024/00035</b></td>
          <td>TLB-PRO-2023/00762</td>
          <td>CENTRAL SERVIÇOS E GESTÃO</td>
          <td class="center">03/03/2026</td>
          <td class="center">03/11/2025</td>
          <td class="center">-330 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Terceirização de mão de obra exclusiva. Auditar GFIP/FGTS.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2025/00020</b></td>
          <td>TLB-PRO-2024/00112</td>
          <td>INSTITUTO BRASILEIRO GOVERNANÇA</td>
          <td class="center">18/03/2026</td>
          <td class="center">18/11/2025</td>
          <td class="center">-315 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Notificar gestor para verificar interesse na prorrogação.</td>
        </tr>
        <tr>
          <td><b>TLB-CTR-2025/00024</b></td>
          <td>TLB-PRO-2024/00388</td>
          <td>SC BRASIL GROUP SOLUÇÕES</td>
          <td class="center">28/03/2026</td>
          <td class="center">28/11/2025</td>
          <td class="center">-305 dias</td>
          <td class="center"><span class="badge badge-red">CRÍTICO: T-120 VENCIDO</span></td>
          <td>Atesto e vantajabilidade econômica para prorrogação por 12 meses.</td>
        </tr>
      </tbody>
    </table>

    <div class="section-title">2. Diretrizes Estruturantes de Sincronização PLAC 2026 x PLAC 2027</div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; margin-bottom:4px;">
      <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:3px; padding:5px;">
        <div style="font-weight:700; color:#1e293b; font-size:7pt; margin-bottom:2px;">
          1. DESTRAMVAMENTO DAS 34 DEMANDAS NA GCC
        </div>
        <div style="font-size:6.5pt; color:#475569;">
          • Publicar os 31 editais da Fase 5 (R$ 53,6M) no PNCP até 20/10/2026 para viabilizar sessões de lances ainda este ano.<br>
          • Desafogar a mesa da GCC antes do início das avaliações do Levantamento do PLAC 2027.
        </div>
      </div>
      <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:3px; padding:5px;">
        <div style="font-weight:700; color:#1e293b; font-size:7pt; margin-bottom:2px;">
          2. FILTRO DE INVIABILIDADE NAS ÁREAS DEMANDANTES
        </div>
        <div style="font-size:6.5pt; color:#475569;">
          • Das 111 demandas retidas nos demandantes, repactuar formalmente as de menor prioridade para a janela do PLAC 2027.<br>
          • Focar esforços técnicos nas 26 demandas em gargalo crítico com entrega no Q1/2027.
        </div>
      </div>
      <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:3px; padding:5px;">
        <div style="font-weight:700; color:#1e293b; font-size:7pt; margin-bottom:2px;">
          3. BLINDAGEM CONTRA EXTINÇÃO POR DECURSO DE PRAZO
        </div>
        <div style="font-size:6.5pt; color:#475569;">
          • O estrito cumprimento do Marco T-120 é vinculante. Aditivos assinados após a expiração são juridicamente nulos.<br>
          • A GCC deve emitir notificações automáticas no SIGA a 120 e 90 dias do término.
        </div>
      </div>
      <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:3px; padding:5px;">
        <div style="font-weight:700; color:#1e293b; font-size:7pt; margin-bottom:2px;">
          4. REAJUSTE POR SIMPLES APOSTILAMENTO UNILATERAL
        </div>
        <div style="font-size:6.5pt; color:#475569;">
          • Reajustes anuais pactuados (IPCA/IGP-M) devem ser feitos por apostila pela GCC em até 8 dias úteis, sem parecer da CONJUR.<br>
          • Evita sobrecarga da Diretoria e preserva o equilíbrio financeiro do contrato.
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <span>TELEBRAS — Gerência de Compras e Contratos (GCC / DAFRI)</span>
    <span>Relatório Integrado PLAC 2026/2027 | Página 5 de 5</span>
  </div>
</div>

</body>
</html>
"""

html_path = "Z:/PLAC-MVP/Relatorio_Esteira_PLAC_2027_Vigentes_GCC_Demandantes.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[+] HTML salvo em {html_path}!")

# Conversão para PDF via Playwright
pdf_path = "Z:/PLAC-MVP/Relatorio_Esteira_PLAC_2027_Vigentes_GCC_Demandantes.pdf"
print("[4/5] Renderizando PDF de alta qualidade via Playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}")
    page.wait_for_timeout(1000)
    page.pdf(
        path=pdf_path,
        format="A4",
        landscape=True,
        print_background=True,
        margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
    )
    
    print("[5/5] Capturando screenshots das páginas para o preview...")
    for i in range(1, 6):
        clip_page = page.locator(f".page:nth-child({i})")
        if clip_page.count() > 0:
            preview_local = f"Z:/PLAC-MVP/preview_plac2027_p{i}.png"
            preview_art = f"C:/Users/G15/.gemini/antigravity/brain/ba312ff6-17f5-4d07-95c0-175d56dcd927/preview_plac2027_p{i}.png"
            clip_page.screenshot(path=preview_local)
            clip_page.screenshot(path=preview_art)
            print(f"    - Página {i} capturada!")
            
    browser.close()

print(f"[+] Relatório Executivo em PDF gerado com sucesso em {pdf_path}!")
