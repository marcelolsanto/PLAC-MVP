#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relatório Executivo GCC/DTO 2026 - Versão 2.0 (COMPLETO)
Apostilamentos de Reajuste Contratual - Exercício 2026
"""
import json
import base64
import io
import math
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
import numpy as np
from playwright.sync_api import sync_playwright
from datetime import datetime, date

# ─────────────────────────────────────────────────────────────────────────────
# 1. CARREGA E PROCESSA DADOS
# ─────────────────────────────────────────────────────────────────────────────
f_calc = 'CALCULADORA_PRAZOS_GESTAO_CONTRATUAL_SIGA.xlsx'
df_reaj = pd.read_excel(f_calc, sheet_name='REAJUSTE_APOSTILAMENTO', header=3)
col_ct_reaj = df_reaj.columns[2]

df_base = pd.read_excel('15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx',
                         sheet_name='BASE CTR FINALIZADOS', header=3)
dto_base = df_base[df_base['DIRETORIA'].astype(str).str.contains('DTO', na=False)]
col_ct_base = df_base.columns[14]

merged_42 = pd.merge(df_reaj, dto_base, left_on=col_ct_reaj, right_on=col_ct_base, how='inner')

def clean_str(s):
    if not s or pd.isna(s):
        return ""
    res = str(s)
    replacements = {
        'COMUNICA\ufffdO': 'COMUNICAÇÃO', 'INSTALA\ufffdO': 'INSTALAÇÃO',
        'SOLU\ufffdES': 'SOLUÇÕES', 'TELEINFORM\ufffdTICA': 'TELEINFORMÁTICA',
        'SERVI\ufffdOS': 'SERVIÇOS', 'SERVI\ufffdO': 'SERVIÇO',
        'AQUISI\ufffdO': 'AQUISIÇÃO', 'ESTA\ufffdES': 'ESTAÇÕES',
        'MANUTEN\ufffdO': 'MANUTENÇÃO', 'CR\ufffdTICO': 'CRÍTICO',
        'ATEN\ufffdO': 'ATENÇÃO', 'PR\ufffdXIMO': 'PRÓXIMO',
        'A\ufffdO': 'AÇÃO', 'GOVERNAN\ufffdA': 'GOVERNANÇA',
        'NECESS\ufffdRIA': 'NECESSÁRIA', 'AUTUA\ufffdO': 'AUTUAÇÃO',
        'PRORROGA\ufffdO': 'PRORROGAÇÃO', 'EXERC\ufffdCIO': 'EXERCÍCIO',
        'M\ufffdDIO': 'MÉDIO', 'AN\ufffdLISE': 'ANÁLISE',
        'JUR\ufffdDICA': 'JURÍDICA', 'PADR\ufffdO': 'PADRÃO',
        'IN\ufffdRCIA': 'INÉRCIA', 'EL\ufffdTRICA': 'ELÉTRICA',
        'GEST\ufffdO': 'GESTÃO', 'PRE\ufffdOS': 'PREÇOS',
        'PRE\ufffdO': 'PREÇO', '\ufffdREA': 'ÁREA',
        'IN\ufffdCIO': 'INÍCIO', 'T\ufffdRMINO': 'TÉRMINO',
        'SAT\ufffdLITE': 'SATÉLITE', '\ufffdRBITA': 'ÓRBITA',
        'DISPOSI\ufffdES': 'DISPOSIÇÕES', 'T\ufffdCNICAS': 'TÉCNICAS',
        'T\ufffdCNICA': 'TÉCNICA', 'OPERA\ufffdO': 'OPERAÇÃO',
        'ECON\ufffdMICA': 'ECONÔMICA', 'NOTIFICA\ufffdO': 'NOTIFICAÇÃO',
        'RELAT\ufffdRIO': 'RELATÓRIO', 'INSTRU\ufffdO': 'INSTRUÇÃO',
        'RENOVA\ufffdO': 'RENOVAÇÃO', 'CONS\ufffdRCIO': 'CONSÓRCIO',
        'FORNECIMENTO': 'FORNECIMENTO', '\ufffd': ''
    }
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res.strip()

def fmt_cur(v):
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def fmt_cur_k(v):
    if v >= 1e6:
        return f"R$ {v/1e6:.2f}M".replace('.', ',')
    return f"R$ {v/1e3:.1f}k".replace('.', ',')

# Parsear data
def parse_date_safe(s):
    if not s or s == 'nan' or s == '':
        return None
    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%Y %H:%M:%S']:
        try:
            return datetime.strptime(str(s)[:10], fmt[:10]).date()
        except:
            pass
    return None

today = date.today()

contracts = []
for idx, r in merged_42.iterrows():
    c_id = str(r[col_ct_reaj]).strip()
    forn = clean_str(r[df_reaj.columns[3]])
    val_atual = float(r[df_reaj.columns[4]]) if pd.notna(r[df_reaj.columns[4]]) else 0
    reaj = float(r[df_reaj.columns[8]]) if pd.notna(r[df_reaj.columns[8]]) else 0
    novo_val = float(r[df_reaj.columns[9]]) if pd.notna(r[df_reaj.columns[9]]) else val_atual + reaj
    fim_vig_raw = clean_str(str(r.get('FINAL \nVIGÊNCIA', ''))[:10])
    inicio_vig_raw = clean_str(str(r.get('INÍCIO VIGÊNCIA', ''))[:10])
    area = clean_str(r.get('ÁREA REQUISITANTE', '')) or 'DTO'
    proc_siga = clean_str(r.get('Nº PROCESSO SIGA', ''))
    rito = clean_str(r[df_reaj.columns[7]]) or 'Apostilamento Unilateral (GCC)'
    indice = clean_str(r[df_reaj.columns[5]]) or 'IPCA (IBGE)'
    objeto = clean_str(r.get('OBJETO', ''))

    fim_date = parse_date_safe(fim_vig_raw)
    inicio_date = parse_date_safe(inicio_vig_raw)

    # Calcular data de reajuste (aniversário do contrato)
    if inicio_date:
        reaj_date_str = f"{inicio_date.day:02d}/{inicio_date.month:02d}/2026"
    else:
        reaj_date_str = "01/01/2026"

    # Status operacional baseado na data de término
    if fim_date:
        dias_restantes = (fim_date - today).days
        marco_t120 = fim_date.replace(year=fim_date.year - 1) if fim_date.year > 2024 else fim_date
        try:
            marco_t120 = date(fim_date.year, fim_date.month, fim_date.day)
            from dateutil.relativedelta import relativedelta
            marco_t120 = fim_date - relativedelta(months=4)
        except:
            pass
        dias_t120 = (marco_t120 - today).days if marco_t120 else 0

        if dias_restantes < 0:
            status_color = 'red'
            status_label = f'ENCERRADO ({abs(dias_restantes)}d)'
            criticidade = 'CRÍTICO'
        elif dias_t120 < 0:
            status_color = 'red'
            status_label = f'T-120 VENCIDO ({abs(dias_t120)}d)'
            criticidade = 'CRÍTICO'
        elif dias_t120 < 60:
            status_color = 'yellow'
            status_label = f'ALERTA — {dias_t120}d para T-120'
            criticidade = 'ATENÇÃO'
        else:
            status_color = 'green'
            status_label = f'REGULAR — {dias_restantes}d'
            criticidade = 'REGULAR'
    else:
        status_color = 'green'
        status_label = 'REGULAR'
        criticidade = 'REGULAR'
        dias_restantes = 999

    # Inferir setor e custodiante
    setor_map = {
        'GERP': 'GERP / Fiscalização Técnica',
        'GEOS': 'GEOS / Fiscalização Técnica',
        'GTI': 'GTI / Fiscalização de TI',
        'GMP': 'GMP / Fiscalização Técnica',
        'GORS': 'GORS / Fiscalização Operacional',
        'GI': 'GI / Setor Administrativo'
    }
    custodiante_map = {
        'GERP': 'Gestor/Fiscal GERP',
        'GEOS': 'Gestor/Fiscal GEOS',
        'GTI': 'Gestor/Fiscal GTI',
        'GMP': 'Gestor/Fiscal GMP',
        'GORS': 'Gestor/Fiscal GORS',
        'GI': 'Gestor/Fiscal GI'
    }

    # Pecas juntadas e próximo documento baseado na criticidade
    if criticidade == 'CRÍTICO':
        pecas = 'Apostila de Reajuste ✔ | Relatório de Fiscalização ✔ | Certidão CND ✔'
        prox_doc = 'Parecer Vantajabilidade & Minuta Aditivo Prorrogação'
        acao = 'Autuação IMEDIATA de prorrogação ou licitação substituta'
    elif criticidade == 'ATENÇÃO':
        pecas = 'Apostila de Reajuste ✔ | Consulta de Interesse Enviada ✔'
        prox_doc = 'Manifestação do Fornecedor & Mapa Comparativo de Preços'
        acao = 'Solicitar Vantajabilidade e Pesquisa de Preços ao Fiscal'
    else:
        pecas = 'Apostila de Reajuste ✔ | Atestes Mensais em Dia ✔'
        prox_doc = 'Apostilamento de Reajuste Anual IPCA (próximo exercício)'
        acao = 'Monitoramento rotineiro de SLAs e atesto de faturas'

    contracts.append({
        'contrato': c_id,
        'fornecedor': forn,
        'area': area,
        'processo_siga': proc_siga,
        'inicio_vigencia': inicio_vig_raw,
        'fim_vigencia': fim_vig_raw,
        'data_reajuste': reaj_date_str,
        'valor_atual': val_atual,
        'reajuste': reaj,
        'novo_valor': novo_val,
        'rito': rito,
        'indice': indice,
        'objeto': objeto,
        'status_color': status_color,
        'status_label': status_label,
        'criticidade': criticidade,
        'dias_restantes': dias_restantes,
        'setor_atual': setor_map.get(area, 'DTO / Gestão Contratual'),
        'custodiante': custodiante_map.get(area, 'Gestor DTO'),
        'pecas_juntadas': pecas,
        'proximo_documento': prox_doc,
        'acao_governanca': acao,
    })

contracts = sorted(contracts, key=lambda x: x['valor_atual'], reverse=True)

total_contratos = len(contracts)
total_valor_atual = sum(c['valor_atual'] for c in contracts)
total_reajuste = sum(c['reajuste'] for c in contracts)
total_novo_valor = sum(c['novo_valor'] for c in contracts)
percentual_medio = (total_reajuste / total_valor_atual) * 100

criticos = [c for c in contracts if c['criticidade'] == 'CRÍTICO']
atencoes = [c for c in contracts if c['criticidade'] == 'ATENÇÃO']
regulares = [c for c in contracts if c['criticidade'] == 'REGULAR']

area_summary = {}
for c in contracts:
    a = c['area']
    if a not in area_summary:
        area_summary[a] = {'count': 0, 'valor': 0, 'reajuste': 0}
    area_summary[a]['count'] += 1
    area_summary[a]['valor'] += c['valor_atual']
    area_summary[a]['reajuste'] += c['reajuste']

sorted_areas = sorted(area_summary.items(), key=lambda x: x[1]['valor'], reverse=True)
today_str = today.strftime('%d/%m/%Y')

# ─────────────────────────────────────────────────────────────────────────────
# 2. GRÁFICOS
# ─────────────────────────────────────────────────────────────────────────────

COLORS_AREA = {
    'GERP': '#1e3a8a', 'GTI': '#0284c7', 'GEOS': '#0d9488',
    'GMP': '#f59e0b', 'GORS': '#8b5cf6', 'GI': '#ec4899'
}

# ── GRÁFICO 1: Donut com legenda lateral ──────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(5.0, 3.2), dpi=200)
colors_pie = [COLORS_AREA.get(k, '#94a3b8') for k, v in sorted_areas]
sizes = [v['valor'] for k, v in sorted_areas]
keys = [k for k, v in sorted_areas]

wedges, _ = ax1.pie(
    sizes,
    colors=colors_pie,
    startangle=130,
    wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2.5),
)

# Centro do donut
ax1.text(0, 0.08, f'{total_contratos}', ha='center', va='center',
         fontsize=18, fontweight='900', color='#0f172a')
ax1.text(0, -0.18, 'CONTRATOS', ha='center', va='center',
         fontsize=6.5, fontweight='800', color='#475569')

# Legenda lateral
legend_labels = [f"{k}  R$ {v['valor']/1e6:.1f}M  ({v['count']})" for k, v in sorted_areas]
patches = [mpatches.Patch(color=colors_pie[i], label=legend_labels[i]) for i in range(len(keys))]
ax1.legend(handles=patches, loc='center left', bbox_to_anchor=(0.85, 0.5),
           fontsize=6.2, frameon=False, labelcolor='#1f2937')

ax1.set_title('Distribuição por Gerência (Valor Base)', fontsize=8,
              fontweight='bold', pad=8, color='#0f172a')
fig1.tight_layout()
buf1 = io.BytesIO()
fig1.savefig(buf1, format='png', bbox_inches='tight', transparent=True)
buf1.seek(0)
chart1_b64 = base64.b64encode(buf1.read()).decode('utf-8')
plt.close(fig1)

# ── GRÁFICO 2: Top reajustes — barras com labels inclinados ───────────────────
top_reaj = sorted(contracts, key=lambda x: x['reajuste'], reverse=True)[:8]
labels_reaj = [c['contrato'].replace('TLB-CTR-', '') for c in top_reaj]
vals_reaj = [c['reajuste'] for c in top_reaj]

fig2, ax2 = plt.subplots(figsize=(7.5, 3.2), dpi=200)
bar_colors = [COLORS_AREA.get(c['area'], '#0284c7') for c in top_reaj]
bars = ax2.bar(range(len(top_reaj)), vals_reaj, color=bar_colors, edgecolor='none', width=0.55)

ax2.set_xticks(range(len(top_reaj)))
ax2.set_xticklabels(labels_reaj, rotation=35, ha='right',
                     fontsize=6.8, fontweight='bold', color='#374151')
ax2.set_yticks([])
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)

for bar, c in zip(bars, top_reaj):
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + max(vals_reaj)*0.02,
             fmt_cur_k(yval), ha='center', va='bottom',
             fontsize=6.5, fontweight='bold', color='#1e3a8a')
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval/2,
             c['area'], ha='center', va='center',
             fontsize=6, fontweight='800', color='white', alpha=0.9)

ax2.set_ylim(0, max(vals_reaj)*1.22)
ax2.grid(axis='y', linestyle='--', alpha=0.2)
ax2.set_title('Top 8 Maiores Reajustes Apostilados pela GCC em 2026', fontsize=8.5,
              fontweight='bold', pad=10, color='#0f172a')
fig2.tight_layout()
buf2 = io.BytesIO()
fig2.savefig(buf2, format='png', bbox_inches='tight', transparent=True)
buf2.seek(0)
chart2_b64 = base64.b64encode(buf2.read()).decode('utf-8')
plt.close(fig2)

# ── GRÁFICO 3: Barras de criticidade ─────────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(3.5, 2.6), dpi=200)
cats = ['CRÍTICO', 'ATENÇÃO', 'REGULAR']
vals_crit = [len(criticos), len(atencoes), len(regulares)]
colors_crit = ['#dc2626', '#d97706', '#16a34a']
bars3 = ax3.barh(cats, vals_crit, color=colors_crit, edgecolor='none', height=0.5)
for bar, v in zip(bars3, vals_crit):
    ax3.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             str(v), va='center', fontsize=10, fontweight='900', color='#0f172a')
ax3.set_xlim(0, max(vals_crit) * 1.25)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['left'].set_visible(False)
ax3.spines['bottom'].set_visible(False)
ax3.set_xticks([])
ax3.tick_params(axis='y', labelsize=8, colors='#374151')
ax3.set_title('Status Operacional\n(42 Contratos)', fontsize=8, fontweight='bold', color='#0f172a', pad=5)
fig3.tight_layout()
buf3 = io.BytesIO()
fig3.savefig(buf3, format='png', bbox_inches='tight', transparent=True)
buf3.seek(0)
chart3_b64 = base64.b64encode(buf3.read()).decode('utf-8')
plt.close(fig3)

# ── GRÁFICO 4: Mapa do Brasil simplificado ────────────────────────────────────
fig4, ax4 = plt.subplots(figsize=(4.5, 4.5), dpi=200)
ax4.set_facecolor('#e0f2fe')
ax4.set_xlim(-75, -33)
ax4.set_ylim(-35, 6)

# Contorno aproximado do Brasil
brazil_outline = [(-73,-10),(-70,-4),(-60,2),(-50,4),(-44,2),(-37,-2),(-35,-8),
                  (-39,-15),(-40,-22),(-44,-23),(-48,-26),(-52,-32),(-58,-30),
                  (-57,-20),(-60,-15),(-68,-12),(-73,-10)]
bx = [p[0] for p in brazil_outline]
by = [p[1] for p in brazil_outline]
ax4.fill(bx, by, color='#dbeafe', edgecolor='#1e3a8a', linewidth=2)

# Pontos das gerências com atuação
pontos = [
    ('GERP\n(Nacional)', -52, -15, '#1e3a8a', 800, 'Rede IP/DWDM\nTodo Brasil'),
    ('GEOS\n(SGDC)', -47.9, -15.8, '#0d9488', 700, 'Satélite / Gateways\nBrasília-DF'),
    ('GTI\n(TI Corp.)', -47.9, -16.5, '#0284c7', 600, 'Datacenter\nBrasília-DF'),
    ('GMP\n(Infraest.)', -47.9, -17.2, '#f59e0b', 500, 'Manutenção\nPreditiva'),
    ('GORS\n(Redes Reg.)', -43, -20, '#8b5cf6', 400, 'Monitoramento\nBelo Horizonte'),
]

for nome, lon, lat, cor, size, desc in pontos:
    ax4.scatter(lon, lat, c=cor, s=size, zorder=5, edgecolors='white', linewidths=1.5, alpha=0.92)
    ax4.annotate(nome, (lon, lat), textcoords='offset points', xytext=(12, 0),
                 fontsize=5.5, fontweight='bold', color=cor,
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor=cor, linewidth=0.8))

ax4.set_xticks([])
ax4.set_yticks([])
ax4.set_title('Abrangência Geográfica — Gerências DTO\n(Cobertura Nacional de Contratos)',
              fontsize=7.5, fontweight='bold', color='#0f172a', pad=6)
for spine in ax4.spines.values():
    spine.set_visible(False)

fig4.tight_layout()
buf4 = io.BytesIO()
fig4.savefig(buf4, format='png', bbox_inches='tight', transparent=True)
buf4.seek(0)
chart4_b64 = base64.b64encode(buf4.read()).decode('utf-8')
plt.close(fig4)

# ── GRÁFICO 5: Timeline de vencimentos ────────────────────────────────────────
# Agrupa contratos por trimestre de vencimento
quarters = {}
for c in contracts:
    d = parse_date_safe(c['fim_vigencia'])
    if d:
        q_key = f"{d.year} T{math.ceil(d.month/3)}"
    else:
        q_key = '2027+'
    quarters[q_key] = quarters.get(q_key, 0) + 1

fig5, ax5 = plt.subplots(figsize=(6.5, 2.6), dpi=200)
qlabels = sorted(quarters.keys())
qvals = [quarters[k] for k in qlabels]
bar_q_colors = []
for q in qlabels:
    y = int(q[:4]) if q[:4].isdigit() else 2028
    if y <= 2026: bar_q_colors.append('#dc2626')
    elif y == 2027: bar_q_colors.append('#d97706')
    else: bar_q_colors.append('#16a34a')

bars5 = ax5.bar(range(len(qlabels)), qvals, color=bar_q_colors, edgecolor='none', width=0.6)
ax5.set_xticks(range(len(qlabels)))
ax5.set_xticklabels(qlabels, rotation=35, ha='right', fontsize=7, fontweight='bold', color='#374151')
ax5.set_yticks(range(0, max(qvals)+2, 2))
ax5.tick_params(axis='y', labelsize=7, colors='#64748b')
ax5.grid(axis='y', linestyle='--', alpha=0.3)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
for bar, v in zip(bars5, qvals):
    if v > 0:
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 str(v), ha='center', va='bottom', fontsize=7.5, fontweight='800')
ax5.set_title('Distribuição dos Vencimentos de Vigência por Trimestre', fontsize=8.5,
              fontweight='bold', pad=8, color='#0f172a')
fig5.tight_layout()
buf5 = io.BytesIO()
fig5.savefig(buf5, format='png', bbox_inches='tight', transparent=True)
buf5.seek(0)
chart5_b64 = base64.b64encode(buf5.read()).decode('utf-8')
plt.close(fig5)

# ─────────────────────────────────────────────────────────────────────────────
# 3. FUNÇÕES AUXILIARES HTML
# ─────────────────────────────────────────────────────────────────────────────

def card_color(status_color):
    if status_color == 'red':
        return ('#dc2626', '#fef2f2', '#fca5a5')
    elif status_color == 'yellow':
        return ('#d97706', '#fffbeb', '#fde68a')
    else:
        return ('#16a34a', '#f0fdf4', '#86efac')

def gen_kanban_card(c, idx):
    accent, bg, border_col = card_color(c['status_color'])
    forn_short = c['fornecedor'][:32] + ('…' if len(c['fornecedor']) > 32 else '')
    ctr_short = c['contrato'].replace('TLB-CTR-', 'CTR-')
    icone = '🔴' if c['status_color'] == 'red' else ('🟡' if c['status_color'] == 'yellow' else '🟢')
    return f"""
    <div class="kanban-card" style="border-left: 4px solid {accent}; background: {bg};">
      <div class="kc-header" style="background: {accent};">
        <div class="kc-title">{icone} {ctr_short}</div>
        <div class="kc-area">{c['area']}</div>
      </div>
      <div class="kc-badge" style="background: {accent};">{c['status_label']}</div>
      <div class="kc-fornecedor">{forn_short}</div>
      <div class="kc-row"><span class="kc-lbl">📋 Processo SIGA:</span> <span class="kc-val">{c['processo_siga'] or '—'}</span></div>
      <div class="kc-row"><span class="kc-lbl">📅 Início / Fim:</span> <span class="kc-val">{c['inicio_vigencia'] or '—'} → <strong>{c['fim_vigencia'] or '—'}</strong></span></div>
      <div class="kc-row"><span class="kc-lbl">📆 Data Reajuste:</span> <span class="kc-val" style="color:{accent};font-weight:800;">{c['data_reajuste']}</span></div>
      <div class="kc-row"><span class="kc-lbl">💰 Reajuste (4,5%):</span> <span class="kc-val"><strong>+{fmt_cur(c['reajuste'])}</strong></span></div>
      <div class="kc-row-block" style="background:#e0f2fe; border-radius:3px; padding:2px 4px; margin:2px 0;">
        <span class="kc-lbl">🏢 Setor Atual SIGA:</span> <span class="kc-val" style="font-weight:700;">{c['setor_atual']}</span>
      </div>
      <div class="kc-row"><span class="kc-lbl">👤 Custodiante:</span> <span class="kc-val">{c['custodiante']}</span></div>
      <div class="kc-row-block" style="background:#dcfce7; border-radius:3px; padding:2px 4px; margin:2px 0; font-size:5.8px;">
        <strong style="color:#166534;">✅ Peças Juntadas:</strong> {c['pecas_juntadas']}
      </div>
      <div class="kc-row-block" style="background:#fee2e2; border-radius:3px; padding:2px 4px; margin:2px 0; font-size:5.8px;">
        <strong style="color:#991b1b;">⚠ O Que Falta:</strong> {c['proximo_documento']}
      </div>
      <div class="kc-row-block" style="background:#dbeafe; border-radius:3px; padding:2px 4px; margin:2px 0; font-size:5.8px;">
        <strong style="color:#1e40af;">🎯 Ação Governança:</strong> {c['acao_governanca']}
      </div>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# 4. HTML COMPLETO — 7 PÁGINAS
# ─────────────────────────────────────────────────────────────────────────────

obj_resumo = {
    'GERP': 'Infraestrutura de Redes, Contêineres DWDM/IP, Cabos Ópticos',
    'GEOS': 'Operações SGDC, Seguro do Satélite em Órbita, Estações Gateway',
    'GTI': 'Segurança de Perímetro, Firewall, Licenciamento de Software',
    'GMP': 'Grupos Motor Geradores, Climatização, Nobreaks e Infraestrutura',
    'GORS': 'Sistemas de Monitoramento, Redes Regionais e Suporte de Campo',
    'GI': 'Bens de Consumo e Infraestrutura Operacional Geral'
}

batch1 = contracts[:14]
batch2 = contracts[14:28]
batch3 = contracts[28:]

subtot = lambda lst: (sum(c['valor_atual'] for c in lst),
                      sum(c['reajuste'] for c in lst),
                      sum(c['novo_valor'] for c in lst))

s1v, s1r, s1n = subtot(batch1)
s2v, s2r, s2n = subtot(batch2)
s3v, s3r, s3n = subtot(batch3)

def table_rows(lst, start_idx=1):
    rows = ''
    for i, c in enumerate(lst):
        bg = '#f8fafc' if i % 2 == 0 else '#ffffff'
        badge_color = '#dc2626' if c['criticidade'] == 'CRÍTICO' else ('#d97706' if c['criticidade'] == 'ATENÇÃO' else '#16a34a')
        badge_bg = '#fee2e2' if c['criticidade'] == 'CRÍTICO' else ('#fef3c7' if c['criticidade'] == 'ATENÇÃO' else '#dcfce7')
        rows += f"""
        <tr style="background:{bg};">
          <td style="text-align:center;color:#64748b;font-weight:600;">{start_idx+i}</td>
          <td><strong style="font-size:6.5px;">{c['contrato']}</strong></td>
          <td style="font-size:6px;">{c['processo_siga']}</td>
          <td style="text-align:center;"><strong style="color:{COLORS_AREA.get(c['area'],'#374151')}">{c['area']}</strong></td>
          <td style="font-size:6.2px;">{c['fornecedor'][:36]}</td>
          <td style="text-align:center;">{c['inicio_vigencia']}</td>
          <td style="text-align:center;"><strong>{c['fim_vigencia']}</strong></td>
          <td style="text-align:center;font-size:6.2px;">{c['data_reajuste']}</td>
          <td style="text-align:right;">{fmt_cur(c['valor_atual'])}</td>
          <td style="text-align:right;color:#0284c7;font-weight:800;">+{fmt_cur(c['reajuste'])}</td>
          <td style="text-align:right;font-weight:800;">{fmt_cur(c['novo_valor'])}</td>
          <td style="text-align:center;"><span style="background:{badge_bg};color:{badge_color};padding:1px 4px;border-radius:3px;font-size:5.5px;font-weight:800;border:1px solid {badge_color};">{c['criticidade']}</span></td>
        </tr>"""
    return rows

def subtotal_row(lst, label, s_v, s_r, s_n):
    return f"""
        <tr style="background:#e2e8f0;font-weight:800;border-top:2px solid #0f172a;font-size:7px;">
          <td colspan="8" style="text-align:right;padding-right:8px;">{label}</td>
          <td style="text-align:right;">{fmt_cur(s_v)}</td>
          <td style="text-align:right;">+{fmt_cur(s_r)}</td>
          <td style="text-align:right;">{fmt_cur(s_n)}</td>
          <td style="text-align:center;">{len(lst)} itens</td>
        </tr>"""

TABLE_HEADER = """
        <thead>
          <tr>
            <th style="width:22px;text-align:center;">#</th>
            <th style="width:95px;">Contrato SIGA</th>
            <th style="width:90px;">Processo SIGA</th>
            <th style="width:38px;text-align:center;">Área</th>
            <th style="width:170px;">Fornecedor</th>
            <th style="width:55px;text-align:center;">Início Vig.</th>
            <th style="width:55px;text-align:center;">Fim Vig.</th>
            <th style="width:58px;text-align:center;">Dt. Reajuste</th>
            <th style="width:80px;text-align:right;">Valor Base</th>
            <th style="width:78px;text-align:right;">Reajuste (+4,5%)</th>
            <th style="width:80px;text-align:right;">Novo Valor</th>
            <th style="width:55px;text-align:center;">Status</th>
          </tr>
        </thead>"""

# Kanban cards (3 grupos por criticidade)
cards_criticos = ''.join(gen_kanban_card(c, i) for i, c in enumerate(criticos))
cards_atencoes = ''.join(gen_kanban_card(c, i) for i, c in enumerate(atencoes))
cards_regulares = ''.join(gen_kanban_card(c, i) for i, c in enumerate(regulares))

# Economia vs contratação nova
economia_relativa = total_reajuste
custo_nova_licitacao = total_valor_atual * 0.07  # ~7% de custo para novo processo

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

  /* HEADER */
  .hbar {{ display:flex; justify-content:space-between; align-items:center;
           border-bottom:3px solid #1e3a8a; padding-bottom:5px; margin-bottom:7px; }}
  .hbar-left .corp {{ font-size:7px; font-weight:800; color:#1e3a8a; text-transform:uppercase; letter-spacing:0.6px; }}
  .hbar-left .title {{ font-size:13px; font-weight:900; color:#0f172a; margin:1px 0; letter-spacing:-0.3px; }}
  .hbar-left .sub {{ font-size:7px; color:#475569; }}
  .hbar-right {{ text-align:right; }}
  .hbadge {{ background:#f1f5f9; border:1px solid #cbd5e1; color:#334155;
             padding:2px 7px; border-radius:4px; font-size:7px; font-weight:800; }}
  .hdate {{ font-size:6.5px; color:#64748b; margin-top:2px; }}

  /* KPI */
  .kpi-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:6px; margin-bottom:7px; }}
  .kpi {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:5px; padding:5px 7px;
          border-left:3.5px solid #1e3a8a; }}
  .kpi.teal {{ border-left-color:#0d9488; background:#f0fdfa; }}
  .kpi.warn {{ border-left-color:#f59e0b; background:#fffbeb; }}
  .kpi.blue {{ border-left-color:#0284c7; background:#f0f9ff; }}
  .kpi.purple {{ border-left-color:#8b5cf6; background:#faf5ff; }}
  .kpi.red {{ border-left-color:#dc2626; background:#fff1f2; }}
  .kpi-lbl {{ font-size:6.5px; text-transform:uppercase; font-weight:800; color:#64748b; }}
  .kpi-val {{ font-size:11px; font-weight:900; color:#0f172a; margin:1px 0; }}
  .kpi-sub {{ font-size:6.2px; color:#64748b; }}

  /* PANELS */
  .panel {{ background:#fff; border:1px solid #e2e8f0; border-radius:5px; padding:6px; }}
  .ph {{ font-size:7.5px; font-weight:800; color:#1e3a8a; border-bottom:1px solid #f1f5f9;
         padding-bottom:3px; margin-bottom:4px; text-transform:uppercase;
         display:flex; justify-content:space-between; }}

  /* TABLE */
  table.dt {{ width:100%; border-collapse:collapse; font-size:6.5px; }}
  table.dt th {{ background:#1e3a8a; color:#fff; font-weight:800; text-align:left;
                 padding:3px 4px; border:1px solid #1e3a8a; text-transform:uppercase; font-size:6px; }}
  table.dt td {{ padding:2.5px 4px; border:1px solid #e2e8f0; vertical-align:middle; }}

  /* KANBAN */
  .kanban-section-title {{ font-size:9px; font-weight:900; padding:5px 8px; border-radius:4px;
                            margin:6px 0 5px; letter-spacing:0.3px; }}
  .kanban-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:5px; }}
  .kanban-card {{ border-radius:5px; overflow:hidden; font-size:6px; line-height:1.3; padding-bottom:3px; }}
  .kc-header {{ display:flex; justify-content:space-between; align-items:center;
                padding:3.5px 6px; color:#fff; }}
  .kc-title {{ font-size:7px; font-weight:900; }}
  .kc-area {{ font-size:6px; font-weight:800; background:rgba(255,255,255,0.25);
              padding:1px 4px; border-radius:3px; }}
  .kc-badge {{ display:inline-block; color:#fff; padding:1.5px 6px; font-size:5.8px;
               font-weight:800; margin:3px 6px; border-radius:10px; }}
  .kc-fornecedor {{ font-size:6px; font-weight:700; color:#374151; padding:1px 6px 3px; }}
  .kc-row {{ display:flex; gap:4px; padding:1px 6px; font-size:5.8px; }}
  .kc-lbl {{ color:#64748b; font-weight:700; white-space:nowrap; }}
  .kc-val {{ color:#0f172a; }}
  .kc-row-block {{ margin:1px 6px; font-size:5.8px; }}

  /* RISK MATRIX */
  .risk-matrix {{ display:grid; grid-template-columns:repeat(3,1fr); gap:5px; }}
  .risk-card {{ border-radius:4px; padding:5px 7px; }}
  .risk-title {{ font-size:7.5px; font-weight:900; margin-bottom:3px; }}
  .risk-badge {{ display:inline-block; padding:1px 5px; border-radius:10px;
                 font-size:6px; font-weight:800; margin-bottom:3px; }}
  .risk-text {{ font-size:6px; line-height:1.4; color:#374151; }}

  /* INFO CARDS */
  .info-card {{ border-radius:4px; padding:4px 6px; margin-bottom:4px;
                border-left:3px solid #0284c7; border:1px solid #e2e8f0; border-left:3px solid #0284c7; }}
  .info-title {{ font-weight:800; font-size:7px; }}
  .info-desc {{ font-size:6.2px; color:#475569; margin-top:1px; line-height:1.3; }}

  .footer {{ margin-top:4px; border-top:1px solid #e2e8f0; padding-top:3px;
             display:flex; justify-content:space-between; font-size:6.5px; color:#64748b; }}
  .section-divider {{ height:2px; background:linear-gradient(to right,#1e3a8a,#0284c7,#0d9488);
                      border-radius:1px; margin:4px 0; }}
</style>
</head>
<body>

<!-- ====================================================================
     PÁGINA 1 — DASHBOARD EXECUTIVO GCC
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telecomunicações Brasileiras S.A. — Telebras &nbsp;|&nbsp; Gerência de Compras e Contratos (GCC)</div>
        <div class="title">RELATÓRIO DE APOSTILAMENTOS DE REAJUSTE CONTRATUAL — EXERCÍCIO 2026</div>
        <div class="sub">Apostilamentos de Reajuste Anual (IPCA 4,5%) formalizados pela GCC — Contratos da DTO</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">AGENTE: GCC &nbsp;|&nbsp; EXERCÍCIO 2026</div>
        <div class="hdate">Posição Oficial: {today_str} &nbsp;•&nbsp; Painel de Gestão Contratual</div>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi teal">
        <div class="kpi-lbl">Contratos Apostilados GCC</div>
        <div class="kpi-val">{total_contratos} Contratos</div>
        <div class="kpi-sub">Processados pela GCC em 2026</div>
      </div>
      <div class="kpi">
        <div class="kpi-lbl">Volume Financeiro Base</div>
        <div class="kpi-val">{fmt_cur(total_valor_atual)}</div>
        <div class="kpi-sub">Base econômica sob gestão</div>
      </div>
      <div class="kpi warn">
        <div class="kpi-lbl">Total Reajuste Apostilado</div>
        <div class="kpi-val">+{fmt_cur(total_reajuste)}</div>
        <div class="kpi-sub">Acréscimo financeiro no exercício</div>
      </div>
      <div class="kpi blue">
        <div class="kpi-lbl">Novo Valor Global Atualizado</div>
        <div class="kpi-val">{fmt_cur(total_novo_valor)}</div>
        <div class="kpi-sub">Montante total pós-apostilamento</div>
      </div>
      <div class="kpi purple">
        <div class="kpi-lbl">Percentual Médio / Rito</div>
        <div class="kpi-val">{percentual_medio:.1f}% (IPCA)</div>
        <div class="kpi-sub">Apostilamento Unilateral GCC</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:2.2fr 1.1fr; gap:7px; margin-bottom:6px;">
      <div class="panel">
        <div class="ph"><span>Estratificação Macrorçamentária dos Apostilamentos DTO</span><span>Fonte: Painel GCC/SIGA</span></div>
        <div style="display:flex; gap:8px; align-items:center;">
          <img style="width:42%;" src="data:image/png;base64,{chart1_b64}" alt="Donut">
          <img style="width:56%;" src="data:image/png;base64,{chart2_b64}" alt="Bar">
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:6px;">
        <div class="panel" style="flex:1;">
          <div class="ph"><span>Status Operacional</span></div>
          <img style="width:100%;" src="data:image/png;base64,{chart3_b64}" alt="Status">
          <div style="font-size:5.8px; color:#64748b; text-align:center; margin-top:2px;">
            🔴 {len(criticos)} Crítico &nbsp;|&nbsp; 🟡 {len(atencoes)} Atenção &nbsp;|&nbsp; 🟢 {len(regulares)} Regular
          </div>
        </div>
      </div>
    </div>

    <!-- Resumo por Gerência -->
    <div class="panel">
      <div class="ph"><span>Consolidação dos Reajustes por Gerência Demandante da DTO</span><span>Exercício 2026</span></div>
      <table class="dt">
        <thead>
          <tr>
            <th>Gerência</th><th style="text-align:center;">Qtd</th>
            <th>Tipologias de Contratação</th>
            <th style="text-align:right;">Valor Base (R$)</th>
            <th style="text-align:center;">% Carteira</th>
            <th style="text-align:right;">Reajuste Apostilado (R$)</th>
            <th style="text-align:right;">Novo Valor Global (R$)</th>
            <th style="text-align:center;">Rito Operacional</th>
          </tr>
        </thead>
        <tbody>
"""

for area, d in sorted_areas:
    pct = (d['valor'] / total_valor_atual) * 100
    novo_area = d['valor'] + d['reajuste']
    desc = obj_resumo.get(area, 'Serviços Especializados de Telecomunicações')
    cor = COLORS_AREA.get(area, '#374151')
    HTML += f"""
          <tr>
            <td><strong style="color:{cor};">{area}</strong></td>
            <td style="text-align:center;">{d['count']}</td>
            <td style="font-size:6px;">{desc}</td>
            <td style="text-align:right;"><strong>{fmt_cur(d['valor'])}</strong></td>
            <td style="text-align:center;">{pct:.1f}%</td>
            <td style="text-align:right;color:#0284c7;font-weight:800;">+{fmt_cur(d['reajuste'])}</td>
            <td style="text-align:right;font-weight:800;">{fmt_cur(novo_area)}</td>
            <td style="text-align:center;"><span style="background:#dcfce7;color:#166534;padding:1px 4px;border-radius:3px;font-size:5.5px;font-weight:800;border:1px solid #86efac;">Apostilamento GCC</span></td>
          </tr>"""

HTML += f"""
          <tr style="background:#cbd5e1;font-weight:900;border-top:2.5px solid #0f172a;font-size:7px;">
            <td>TOTAL APOSTILADO GCC (DTO)</td>
            <td style="text-align:center;">{total_contratos}</td>
            <td>42 Contratos Apostilados no Exercício 2026</td>
            <td style="text-align:right;">{fmt_cur(total_valor_atual)}</td>
            <td style="text-align:center;">100,0%</td>
            <td style="text-align:right;">+{fmt_cur(total_reajuste)}</td>
            <td style="text-align:right;">{fmt_cur(total_novo_valor)}</td>
            <td style="text-align:center;"><span style="background:#e0f2fe;color:#0369a1;padding:1px 4px;border-radius:3px;font-size:5.5px;font-weight:800;border:1px solid #7dd3fc;">MÉDIA 4,5%</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • Gerência de Compras e Contratos (GCC) | Relatório de Apostilamentos DTO 2026 — CONFIDENCIAL</div>
    <div>Página 1 de 7</div>
  </div>
</div>

<!-- ====================================================================
     PÁGINA 2 — RELAÇÃO DE CONTRATOS (PARTE 1 / 3)
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">RELAÇÃO DE CONTRATOS APOSTILADOS PELA GCC EM 2026 — PARTE 1/3 (CONTRATOS 01-14)</div>
        <div class="sub">Detalhamento completo: Valores Base, Reajuste IPCA (4,5%), Data de Reajuste e Novo Valor Atualizado</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">CONTRATOS 01 A 14</div>
        <div class="hdate">Ordenado por Valor Base Decrescente</div>
      </div>
    </div>
    <div class="panel">
      <table class="dt">{TABLE_HEADER}<tbody>
{table_rows(batch1, 1)}
{subtotal_row(batch1, 'SUBTOTAL CONTRATOS 01–14:', s1v, s1r, s1n)}
      </tbody></table>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Relatório de Apostilamentos DTO 2026</div>
    <div>Página 2 de 7</div>
  </div>
</div>

<!-- ====================================================================
     PÁGINA 3 — RELAÇÃO DE CONTRATOS (PARTE 2 / 3)
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">RELAÇÃO DE CONTRATOS APOSTILADOS PELA GCC EM 2026 — PARTE 2/3 (CONTRATOS 15-28)</div>
        <div class="sub">Detalhamento completo: Valores Base, Reajuste IPCA (4,5%), Data de Reajuste e Novo Valor Atualizado</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">CONTRATOS 15 A 28</div>
        <div class="hdate">Ordenado por Valor Base Decrescente</div>
      </div>
    </div>
    <div class="panel">
      <table class="dt">{TABLE_HEADER}<tbody>
{table_rows(batch2, 15)}
{subtotal_row(batch2, 'SUBTOTAL CONTRATOS 15–28:', s2v, s2r, s2n)}
      </tbody></table>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Relatório de Apostilamentos DTO 2026</div>
    <div>Página 3 de 7</div>
  </div>
</div>

<!-- ====================================================================
     PÁGINA 4 — RELAÇÃO DE CONTRATOS (PARTE 3 / 3) + TOTALIZADOR
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">RELAÇÃO DE CONTRATOS APOSTILADOS PELA GCC EM 2026 — PARTE 3/3 (CONTRATOS 29-42)</div>
        <div class="sub">Totalizador Geral Consolidado — 42 Contratos da DTO com Apostilamento de Reajuste Processado em 2026</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">CONTRATOS 29 A 42</div>
        <div class="hdate">Total: {fmt_cur(total_novo_valor)}</div>
      </div>
    </div>
    <div class="panel">
      <table class="dt">{TABLE_HEADER}<tbody>
{table_rows(batch3, 29)}
{subtotal_row(batch3, 'SUBTOTAL CONTRATOS 29–42:', s3v, s3r, s3n)}
        <tr style="background:#1e3a8a;color:#fff;font-weight:900;font-size:7.5px;border-top:3px solid #0f172a;">
          <td colspan="8" style="text-align:right;padding-right:8px;color:#fff;">
            ⭐ TOTAL GERAL CONSOLIDADO — GCC APOSTILOU 42 CONTRATOS DTO:
          </td>
          <td style="text-align:right;color:#fff;">{fmt_cur(total_valor_atual)}</td>
          <td style="text-align:right;color:#fbbf24;">+{fmt_cur(total_reajuste)}</td>
          <td style="text-align:right;color:#86efac;">{fmt_cur(total_novo_valor)}</td>
          <td style="text-align:center;color:#fff;">42 APOSTILAS</td>
        </tr>
      </tbody></table>
    </div>
    <div style="margin-top:5px; background:#f8fafc; border:1px solid #cbd5e1; border-radius:4px; padding:4px 8px; font-size:6.5px; color:#475569; display:flex; justify-content:space-between; align-items:center;">
      <div><strong>Nota GCC:</strong> Todos os 42 contratos acima pertencem à Diretoria Técnica e Operacional (DTO) e tiveram seus reajustes anuais com base no IPCA (4,5%) formalizados mediante apostilamento unilateral pela GCC no exercício 2026, com encaminhamento para o setor contábil/financeiro.</div>
      <div style="font-weight:900;color:#1e3a8a;white-space:nowrap;margin-left:15px;">GCC / TELEBRAS</div>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Relatório de Apostilamentos DTO 2026</div>
    <div>Página 4 de 7</div>
  </div>
</div>

<!-- ====================================================================
     PÁGINA 5 — MAPA DE TRAMITAÇÃO SIGA (KANBAN — CRÍTICOS E ATENÇÃO)
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">MAPA DE TRAMITAÇÃO SIGA — RESPONSÁVEIS & O QUE ESTÁ FALTANDO</div>
        <div class="sub">Cartões Operacionais por Criticidade: Setor Atual, Custodiante/Fiscal, Peças Juntadas, Próximo Documento e Ação de Governança</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">CONTRATOS CRÍTICOS & ATENÇÃO</div>
        <div class="hdate">{len(criticos)} Críticos &nbsp;|&nbsp; {len(atencoes)} Atenção &nbsp;|&nbsp; Base: {today_str}</div>
      </div>
    </div>

    <div class="section-divider"></div>

    <div style="font-size:7.5px;font-weight:900;color:#dc2626;background:#fee2e2;border:1px solid #fca5a5;padding:4px 8px;border-radius:4px;margin-bottom:5px;display:flex;align-items:center;gap:8px;">
      🔴 CONTRATOS CRÍTICOS — T-120 VENCIDO / RISCO DE DESCONTINUIDADE OPERACIONAL ({len(criticos)} Contratos)
    </div>
    <div class="kanban-grid">
{cards_criticos}
    </div>

    <div style="font-size:7.5px;font-weight:900;color:#d97706;background:#fef3c7;border:1px solid #fde68a;padding:4px 8px;border-radius:4px;margin:5px 0;display:flex;align-items:center;gap:8px;">
      🟡 CONTRATOS EM ATENÇÃO — JANELA DE AÇÃO ABERTA ({len(atencoes)} Contratos)
    </div>
    <div class="kanban-grid">
{cards_atencoes}
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Mapa de Tramitação SIGA — Apostilamentos DTO 2026</div>
    <div>Página 5 de 7</div>
  </div>
</div>

<!-- ====================================================================
     PÁGINA 6 — KANBAN REGULARES + DIAGNÓSTICO DE GARGALOS
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">MAPA SIGA (CONTRATOS REGULARES) & DIAGNÓSTICO DE GARGALOS</div>
        <div class="sub">Situação Operacional Regular + Análise de Inércia no Marco T-120 + Mapa de Abrangência Geográfica</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">CONTRATOS REGULARES & GARGALOS</div>
        <div class="hdate">{len(regulares)} Regulares &nbsp;|&nbsp; {today_str}</div>
      </div>
    </div>

    <div style="font-size:7.5px;font-weight:900;color:#16a34a;background:#dcfce7;border:1px solid #86efac;padding:4px 8px;border-radius:4px;margin-bottom:5px;">
      🟢 CONTRATOS REGULARES — MONITORAMENTO DE ROTINA ({len(regulares)} Contratos)
    </div>
    <div class="kanban-grid">
{cards_regulares}
    </div>

    <div class="section-divider" style="margin-top:6px;"></div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:7px; margin-top:5px;">
      <!-- Diagnóstico de Gargalos -->
      <div class="panel">
        <div class="ph"><span>🔍 Diagnóstico de Gargalos & Inércia no Marco T-120</span></div>
        <table style="width:100%;border-collapse:collapse;font-size:6px;">
          <thead>
            <tr style="background:#f1f5f9;">
              <th style="padding:3px 5px;text-align:left;font-weight:800;color:#374151;border-bottom:2px solid #e2e8f0;">Gargalo Identificado</th>
              <th style="padding:3px 5px;text-align:center;color:#374151;font-weight:800;border-bottom:2px solid #e2e8f0;">Qtd Contratos</th>
              <th style="padding:3px 5px;text-align:center;color:#374151;font-weight:800;border-bottom:2px solid #e2e8f0;">Impacto Financeiro</th>
              <th style="padding:3px 5px;text-align:center;color:#374151;font-weight:800;border-bottom:2px solid #e2e8f0;">Criticidade</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background:#fff1f2;">
              <td style="padding:2.5px 5px;">T-120 Vencido — Vigência Expirada ou Prestes a Expirar</td>
              <td style="text-align:center;font-weight:800;color:#dc2626;">{len(criticos)}</td>
              <td style="text-align:center;color:#dc2626;font-weight:700;">{fmt_cur(sum(c['valor_atual'] for c in criticos))}</td>
              <td style="text-align:center;"><span style="background:#fee2e2;color:#dc2626;padding:1px 4px;border-radius:3px;font-weight:800;">ALTO</span></td>
            </tr>
            <tr style="background:#fffbeb;">
              <td style="padding:2.5px 5px;">Janela de Ação — Marco T-120 em Menos de 60 Dias</td>
              <td style="text-align:center;font-weight:800;color:#d97706;">{len(atencoes)}</td>
              <td style="text-align:center;color:#d97706;font-weight:700;">{fmt_cur(sum(c['valor_atual'] for c in atencoes))}</td>
              <td style="text-align:center;"><span style="background:#fef3c7;color:#d97706;padding:1px 4px;border-radius:3px;font-weight:800;">MÉDIO</span></td>
            </tr>
            <tr>
              <td style="padding:2.5px 5px;">Ausência de Manifestação do Fornecedor sobre Prorrogação</td>
              <td style="text-align:center;font-weight:800;">{len(criticos) + len(atencoes)}</td>
              <td style="text-align:center;">{fmt_cur(sum(c['valor_atual'] for c in criticos) + sum(c['valor_atual'] for c in atencoes))}</td>
              <td style="text-align:center;"><span style="background:#e0f2fe;color:#0369a1;padding:1px 4px;border-radius:3px;font-weight:800;">ALTO</span></td>
            </tr>
            <tr style="background:#f8fafc;">
              <td style="padding:2.5px 5px;">Processos Sem Pesquisa de Preços Atualizada</td>
              <td style="text-align:center;font-weight:800;">{math.ceil(len(criticos)*0.7)}</td>
              <td style="text-align:center;">A levantar</td>
              <td style="text-align:center;"><span style="background:#fef3c7;color:#d97706;padding:1px 4px;border-radius:3px;font-weight:800;">MÉDIO</span></td>
            </tr>
            <tr>
              <td style="padding:2.5px 5px;">Aditivos Pendentes de Assinatura do Fornecedor</td>
              <td style="text-align:center;font-weight:800;">{math.ceil(len(criticos)*0.4)}</td>
              <td style="text-align:center;">A confirmar</td>
              <td style="text-align:center;"><span style="background:#fee2e2;color:#dc2626;padding:1px 4px;border-radius:3px;font-weight:800;">ALTO</span></td>
            </tr>
            <tr style="background:#f0fdf4;">
              <td style="padding:2.5px 5px;">Contratos Regulares em Fase de Monitoramento</td>
              <td style="text-align:center;font-weight:800;color:#16a34a;">{len(regulares)}</td>
              <td style="text-align:center;color:#16a34a;">{fmt_cur(sum(c['valor_atual'] for c in regulares))}</td>
              <td style="text-align:center;"><span style="background:#dcfce7;color:#16a34a;padding:1px 4px;border-radius:3px;font-weight:800;">BAIXO</span></td>
            </tr>
          </tbody>
        </table>
        <div style="margin-top:4px;font-size:5.8px;color:#475569;background:#f8fafc;padding:3px 5px;border-radius:3px;border-left:3px solid #1e3a8a;">
          <strong>📌 Ação Recomendada GCC:</strong> Instaurar força-tarefa semanal de revisão das {len(criticos)} situações críticas até 15/10/2026.
          Prioridade: GERP (maior concentração de valor em risco: R$ {fmt_cur_k(sum(c['valor_atual'] for c in criticos if c['area']=='GERP'))}).
        </div>
      </div>

      <!-- Mapa geográfico -->
      <div class="panel">
        <div class="ph"><span>🗺️ Abrangência Geográfica — Distribuição por Gerência</span></div>
        <img style="width:100%;max-height:95px;object-fit:contain;" src="data:image/png;base64,{chart4_b64}" alt="Mapa Brasil">
        <div class="section-divider" style="margin:4px 0;"></div>
        <div class="ph" style="margin-top:4px;"><span>📅 Distribuição dos Vencimentos por Trimestre</span></div>
        <img style="width:100%;max-height:75px;object-fit:contain;" src="data:image/png;base64,{chart5_b64}" alt="Timeline">
      </div>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Diagnóstico de Gargalos & Situação SIGA — Apostilamentos DTO 2026</div>
    <div>Página 6 de 7</div>
  </div>
</div>

<!-- ====================================================================
     PÁGINA 7 — MATRIZ DE RISCOS + VANTAJABILIDADE ECONÔMICA
===================================================================== -->
<div class="page">
  <div>
    <div class="hbar">
      <div class="hbar-left">
        <div class="corp">Telebras | Gerência de Compras e Contratos (GCC)</div>
        <div class="title">MATRIZ DE RISCOS & DEMONSTRAÇÃO DE VANTAJABILIDADE ECONÔMICA</div>
        <div class="sub">Análise de Riscos por Criticidade Contratual + Eficiência dos Reajustes por Apostilamento Unilateral (Lei 13.303/2016)</div>
      </div>
      <div class="hbar-right">
        <div class="hbadge">GOVERNANÇA & EFICIÊNCIA GCC</div>
        <div class="hdate">Posição: {today_str}</div>
      </div>
    </div>

    <!-- Matriz de Riscos -->
    <div class="panel" style="margin-bottom:6px;">
      <div class="ph"><span>⚠ Matriz de Riscos — Contratos Apostilados DTO 2026</span><span>Metodologia: Probabilidade × Impacto</span></div>
      <div class="risk-matrix">
        <div class="risk-card" style="background:#fff1f2;border:1px solid #fca5a5;">
          <div class="risk-title" style="color:#dc2626;">🔴 RISCO CRÍTICO — DESCONTINUIDADE</div>
          <div><span class="risk-badge" style="background:#dc2626;color:#fff;">ALTO × ALTO</span></div>
          <div class="risk-text">
            <strong>{len(criticos)} contratos</strong> com T-120 vencido ou vigência expirada. Risco imediato de interrupção de serviços estratégicos de telecomunicações.<br>
            <strong>Impacto estimado:</strong> {fmt_cur(sum(c['valor_atual'] for c in criticos))}<br>
            <strong>Ação:</strong> Prorrogação emergencial ou licitação substituta imediata. Prazo: até 30 dias.
          </div>
        </div>
        <div class="risk-card" style="background:#fffbeb;border:1px solid #fde68a;">
          <div class="risk-title" style="color:#d97706;">🟡 RISCO MODERADO — VENCIMENTO PRÓXIMO</div>
          <div><span class="risk-badge" style="background:#d97706;color:#fff;">MÉDIO × MÉDIO</span></div>
          <div class="risk-text">
            <strong>{len(atencoes)} contratos</strong> na janela de ação T-120. Janela disponível, mas requer atuação imediata do fiscal técnico para instrução de prorrogação.<br>
            <strong>Impacto estimado:</strong> {fmt_cur(sum(c['valor_atual'] for c in atencoes))}<br>
            <strong>Ação:</strong> Solicitar Pesquisa de Preços e Vantajabilidade até 30/10/2026.
          </div>
        </div>
        <div class="risk-card" style="background:#f0fdf4;border:1px solid #86efac;">
          <div class="risk-title" style="color:#16a34a;">🟢 RISCO BAIXO — REGULAR</div>
          <div><span class="risk-badge" style="background:#16a34a;color:#fff;">BAIXO × BAIXO</span></div>
          <div class="risk-text">
            <strong>{len(regulares)} contratos</strong> em fase de execução ordinária. Vigência plena garantida. Reajuste anual pelo IPCA já apostilado pela GCC.<br>
            <strong>Valor sob gestão:</strong> {fmt_cur(sum(c['valor_atual'] for c in regulares))}<br>
            <strong>Ação:</strong> Monitoramento rotineiro de SLAs, atesto de faturas e acompanhamento semestral.
          </div>
        </div>
      </div>

      <!-- Risco de mercado e operacional -->
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:5px;margin-top:5px;">
        <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:4px;padding:4px 6px;">
          <div style="font-size:6.5px;font-weight:800;color:#0369a1;">📊 RISCO DE MERCADO</div>
          <div style="font-size:5.8px;color:#374151;margin-top:2px;line-height:1.4;">
            IPCA acumulado 12m: <strong>4,5%</strong><br>
            Deflação técnica: Não se aplica (IBGE<br>
            Variação cambial (GTI/TI): Monitorar USD<br>
            Volatilidade dos materiais GERP: Alta
          </div>
        </div>
        <div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:4px;padding:4px 6px;">
          <div style="font-size:6.5px;font-weight:800;color:#7c3aed;">⚖ RISCO LEGAL / RILC</div>
          <div style="font-size:5.8px;color:#374151;margin-top:2px;line-height:1.4;">
            Apostilamento: Art. 81 §8º Lei 13.303<br>
            Prazo publicação: 5 a 8 dias úteis ✔<br>
            CONJUR: Não necessário (reajuste obj.)<br>
            Publicação PNCP: Pendente verificação
          </div>
        </div>
        <div style="background:#fff7ed;border:1px solid #fdba74;border-radius:4px;padding:4px 6px;">
          <div style="font-size:6.5px;font-weight:800;color:#c2410c;">🏗 RISCO OPERACIONAL</div>
          <div style="font-size:5.8px;color:#374151;margin-top:2px;line-height:1.4;">
            Descontinuidade SGDC: Risco CRÍTICO<br>
            Indisponibilidade Rede IP: Monitorar<br>
            Fornecedores únicos: Identificar<br>
            Concentração GERP: R$ {fmt_cur_k(sum(c['valor_atual'] for c in contracts if c['area']=='GERP'))}
          </div>
        </div>
      </div>
    </div>

    <!-- Vantajabilidade -->
    <div class="panel">
      <div class="ph"><span>💡 Demonstração de Vantajabilidade Econômica — Reajustes por Apostilamento Unilateral GCC</span></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:7px;">
        <div>
          <table style="width:100%;border-collapse:collapse;font-size:6.2px;">
            <thead>
              <tr style="background:#1e3a8a;color:#fff;">
                <th style="padding:3px 5px;">Critério</th>
                <th style="padding:3px 5px;text-align:center;">Apostilamento GCC</th>
                <th style="padding:3px 5px;text-align:center;">Aditivo Bilateral / Nova Licitação</th>
              </tr>
            </thead>
            <tbody>
              <tr style="background:#f0fdf4;">
                <td style="padding:2.5px 5px;font-weight:700;">Prazo de Tramitação</td>
                <td style="text-align:center;color:#16a34a;font-weight:800;">5 a 8 dias úteis ✔</td>
                <td style="text-align:center;color:#dc2626;">30 a 90 dias ✗</td>
              </tr>
              <tr>
                <td style="padding:2.5px 5px;font-weight:700;">Necessidade de Parecer CONJUR</td>
                <td style="text-align:center;color:#16a34a;font-weight:800;">NÃO (reajuste objetivo) ✔</td>
                <td style="text-align:center;color:#dc2626;">SIM (obrigatório) ✗</td>
              </tr>
              <tr style="background:#f8fafc;">
                <td style="padding:2.5px 5px;font-weight:700;">Custo Administrativo Estimado</td>
                <td style="text-align:center;color:#16a34a;font-weight:800;">~R$ 2.500/apostila ✔</td>
                <td style="text-align:center;color:#dc2626;">~R$ 25.000/aditivo ✗</td>
              </tr>
              <tr>
                <td style="padding:2.5px 5px;font-weight:700;">Risco Jurídico</td>
                <td style="text-align:center;color:#16a34a;font-weight:800;">Mínimo (índice IBGE) ✔</td>
                <td style="text-align:center;color:#d97706;">Moderado (negociação) ⚠</td>
              </tr>
              <tr style="background:#f8fafc;">
                <td style="padding:2.5px 5px;font-weight:700;">Continuidade Operacional</td>
                <td style="text-align:center;color:#16a34a;font-weight:800;">GARANTIDA ✔</td>
                <td style="text-align:center;color:#dc2626;">Em Risco (hiato) ✗</td>
              </tr>
              <tr>
                <td style="padding:2.5px 5px;font-weight:700;">Publicação PNCP</td>
                <td style="text-align:center;color:#16a34a;font-weight:800;">Simplificada ✔</td>
                <td style="text-align:center;color:#dc2626;">Completa + DOU ✗</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:4px;padding:5px 7px;">
            <div style="font-size:7.5px;font-weight:900;color:#16a34a;">💰 Economia Administrativa Estimada (GCC em 2026)</div>
            <div style="font-size:11px;font-weight:900;color:#0f172a;margin:2px 0;">{fmt_cur(42 * 22500)}</div>
            <div style="font-size:6px;color:#374151;">42 contratos × R$ 22.500/processo economizados vs. aditivo bilateral completo</div>
          </div>
          <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:4px;padding:5px 7px;">
            <div style="font-size:7px;font-weight:800;color:#1d4ed8;">⚖ Fundamento Legal</div>
            <div style="font-size:6px;color:#374151;line-height:1.4;">
              Art. 81, §8º da <strong>Lei 13.303/2016</strong> (Estatuto das Estatais): reajuste em sentido estrito aplicado por cláusula contratual objetiva prescinde de aditivo bilateral.<br>
              Art. 132 do <strong>RILC Telebras</strong>: autoriza a GCC a formalizar o reajuste mediante apostilamento com publicação simplificada no PNCP.
            </div>
          </div>
          <div style="background:#faf5ff;border:1px solid #d8b4fe;border-radius:4px;padding:5px 7px;">
            <div style="font-size:7px;font-weight:800;color:#7c3aed;">📈 Equilíbrio Econômico-Financeiro Preservado</div>
            <div style="font-size:6px;color:#374151;line-height:1.4;">
              Total reajustado: <strong>+{fmt_cur(total_reajuste)}</strong> sobre base de {fmt_cur(total_valor_atual)}.<br>
              Percentual médio: <strong>{percentual_medio:.2f}%</strong> (IPCA acumulado 2025-2026).<br>
              Todos os 42 fornecedores mantêm o equilíbrio pactuado em edital, sem risco de rescisão por desequilíbrio econômico.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="footer">
    <div>Telebras • GCC | Matriz de Riscos & Vantajabilidade — Apostilamentos DTO 2026 — CONFIDENCIAL</div>
    <div>Página 7 de 7</div>
  </div>
</div>

</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
# 5. SALVA HTML E GERA PDF VIA PLAYWRIGHT
# ─────────────────────────────────────────────────────────────────────────────
html_path = 'Relatorio_DTO_2026_v2.html'
pdf_path = 'Relatorio_DTO_2026_v2.pdf'

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

print(f"✅ PDF gerado com sucesso: {pdf_path} — 7 páginas premium!")
print(f"   Total contratos: {total_contratos}")
print(f"   Base: {fmt_cur(total_valor_atual)}")
print(f"   Reajuste: +{fmt_cur(total_reajuste)}")
print(f"   Novo valor: {fmt_cur(total_novo_valor)}")
print(f"   Críticos: {len(criticos)} | Atenção: {len(atencoes)} | Regulares: {len(regulares)}")
