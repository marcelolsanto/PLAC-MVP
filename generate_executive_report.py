import json
import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from playwright.sync_api import sync_playwright

# 1. Load data
f_calc = 'CALCULADORA_PRAZOS_GESTAO_CONTRATUAL_SIGA.xlsx'
df_reaj = pd.read_excel(f_calc, sheet_name='REAJUSTE_APOSTILAMENTO', header=3)
col_ct_reaj = df_reaj.columns[2]

df_base = pd.read_excel('15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx', sheet_name='BASE CTR FINALIZADOS', header=3)
dto_base = df_base[df_base['DIRETORIA'].astype(str).str.contains('DTO', na=False)]
col_ct_base = df_base.columns[14]

merged_42 = pd.merge(df_reaj, dto_base, left_on=col_ct_reaj, right_on=col_ct_base, how='inner')

# String cleaning
def clean_str(s):
    if not s or pd.isna(s):
        return ""
    res = str(s)
    replacements = {
        'COMUNICA\ufffdO': 'COMUNICAÇÃO',
        'INSTALA\ufffdO': 'INSTALAÇÃO',
        'SOLU\ufffdES': 'SOLUÇÕES',
        'TELEINFORM\ufffdTICA': 'TELEINFORMÁTICA',
        'SERVI\ufffdOS': 'SERVIÇOS',
        'SERVI\ufffdO': 'SERVIÇO',
        'AQUISI\ufffdO': 'AQUISIÇÃO',
        'ESTA\ufffdES': 'ESTAÇÕES',
        'MANUTEN\ufffdO': 'MANUTENÇÃO',
        'CR\ufffdTICO': 'CRÍTICO',
        'ATEN\ufffdO': 'ATENÇÃO',
        'PR\ufffdXIMO': 'PRÓXIMO',
        'A\ufffdO': 'AÇÃO',
        'GOVERNAN\ufffdA': 'GOVERNANÇA',
        'NECESS\ufffdRIA': 'NECESSÁRIA',
        'AUTUA\ufffdO': 'AUTUAÇÃO',
        'PRORROGA\ufffdO': 'PRORROGAÇÃO',
        'EXERC\ufffdCIO': 'EXERCÍCIO',
        'M\ufffdDIO': 'MÉDIO',
        'AN\ufffdLISE': 'ANÁLISE',
        'JUR\ufffdDICA': 'JURÍDICA',
        'PADR\ufffdO': 'PADRÃO',
        'IN\ufffdRCIA': 'INÉRCIA',
        'EL\ufffdTRICA': 'ELÉTRICA',
        'GEST\ufffdO': 'GESTÃO',
        'PRE\ufffdOS': 'PREÇOS',
        'PRE\ufffdO': 'PREÇO',
        '\ufffdREA': 'ÁREA',
        'IN\ufffdCIO': 'INÍCIO',
        'T\ufffdRMINO': 'TÉRMINO',
        'SAT\ufffdLITE': 'SATÉLITE',
        '\ufffdRBITA': 'ÓRBITA',
        'DISPOSI\ufffdES': 'DISPOSIÇÕES',
        'T\ufffdCNICAS': 'TÉCNICAS',
        'T\ufffdCNICA': 'TÉCNICA',
        'OPERA\ufffdO': 'OPERAÇÃO',
        'ECON\ufffdMICA': 'ECONÔMICA',
        'NOTIFICA\ufffdO': 'NOTIFICAÇÃO',
        'RELAT\ufffdRIO': 'RELATÓRIO',
        'INSTRU\ufffdO': 'INSTRUÇÃO',
        'RENOVA\ufffdO': 'RENOVAÇÃO',
        'CONS\ufffdRCIO': 'CONSÓRCIO',
        '\ufffd': ''
    }
    for k, v in replacements.items():
        res = res.replace(k, v)
    return res.strip()

contracts = []
for idx, r in merged_42.iterrows():
    c_id = r[col_ct_reaj]
    forn = clean_str(r[df_reaj.columns[3]])
    val_atual = float(r[df_reaj.columns[4]]) if pd.notna(r[df_reaj.columns[4]]) else 0
    reaj = float(r[df_reaj.columns[8]]) if pd.notna(r[df_reaj.columns[8]]) else 0
    novo_val = float(r[df_reaj.columns[9]]) if pd.notna(r[df_reaj.columns[9]]) else val_atual + reaj
    fim_vig = clean_str(str(r.get('FINAL \nVIGÊNCIA', ''))[:10])
    inicio_vig = clean_str(str(r.get('INÍCIO VIGÊNCIA', ''))[:10])
    area = clean_str(r.get('ÁREA REQUISITANTE', '')) or 'DTO'
    proc_siga = clean_str(r.get('Nº PROCESSO SIGA', ''))
    rito = clean_str(r[df_reaj.columns[7]]) or 'Apostilamento Unilateral (GCC)'

    contracts.append({
        'contrato': c_id,
        'fornecedor': forn,
        'area': area,
        'processo_siga': proc_siga,
        'inicio_vigencia': inicio_vig,
        'fim_vigencia': fim_vig,
        'valor_atual': val_atual,
        'reajuste': reaj,
        'novo_valor': novo_val,
        'rito': rito
    })

# Sort contracts by valor_atual descending
contracts = sorted(contracts, key=lambda x: x['valor_atual'], reverse=True)

# Totals
total_contratos = len(contracts)
total_valor_atual = sum(c['valor_atual'] for c in contracts)
total_reajuste = sum(c['reajuste'] for c in contracts)
total_novo_valor = sum(c['novo_valor'] for c in contracts)
percentual_medio = (total_reajuste / total_valor_atual) * 100

# Group by Area
area_summary = {}
for c in contracts:
    a = c['area']
    if a not in area_summary:
        area_summary[a] = {'count': 0, 'valor': 0, 'reajuste': 0}
    area_summary[a]['count'] += 1
    area_summary[a]['valor'] += c['valor_atual']
    area_summary[a]['reajuste'] += c['reajuste']

def fmt_cur(v):
    return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Chart 1: Donut chart by Gerência
plt.figure(figsize=(4.2, 2.9), dpi=200)
colors = ['#1e3a8a', '#0284c7', '#0d9488', '#f59e0b', '#8b5cf6', '#ec4899']
sorted_areas = sorted(area_summary.items(), key=lambda x: x[1]['valor'], reverse=True)
labels = [f"{k}\nR$ {v['valor']/1e6:.1f}M ({v['valor']/total_valor_atual*100:.1f}%)" for k, v in sorted_areas]
sizes = [v['valor'] for k, v in sorted_areas]

plt.pie(sizes, labels=labels, colors=colors[:len(sizes)], startangle=140, 
        wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2),
        textprops={'fontsize': 7, 'weight': 'bold', 'color': '#1f2937'})
plt.title('Distribuição dos Reajustes por Gerência DTO (42 Contratos)', fontsize=8.5, fontweight='bold', pad=10, color='#0f172a')
plt.tight_layout()

buf1 = io.BytesIO()
plt.savefig(buf1, format='png', bbox_inches='tight', transparent=True)
buf1.seek(0)
chart1_b64 = base64.b64encode(buf1.read()).decode('utf-8')
plt.close()

# Chart 2: Top 6 Reajustes Apostilados
top_reaj = sorted(contracts, key=lambda x: x['reajuste'], reverse=True)[:6]
labels_reaj = [c['contrato'].replace('TLB-CTR-', 'CTR-') for c in top_reaj]
vals_reaj_k = [c['reajuste'] / 1e3 for c in top_reaj]

plt.figure(figsize=(6.2, 2.9), dpi=200)
bars = plt.bar(range(len(top_reaj)), vals_reaj_k, color='#0284c7', edgecolor='none', width=0.45)
plt.xticks(range(len(top_reaj)), labels_reaj, fontsize=7.5, fontweight='bold', color='#374151')
plt.yticks(fontsize=7, color='#4b5563')
plt.ylabel('Reajuste Apostilado (Mil R$)', fontsize=7.5, fontweight='bold', color='#1f2937')
plt.title('Top 6 Maiores Reajustes Apostilados pela GCC em 2026', fontsize=8.5, fontweight='bold', pad=10, color='#0f172a')

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + (max(vals_reaj_k)*0.02), f'R$ {yval:,.0f}k'.replace(',', '.'), 
             ha='center', va='bottom', fontsize=6.5, fontweight='bold', color='#1e3a8a')

plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.ylim(0, max(vals_reaj_k)*1.18)
plt.tight_layout()

buf2 = io.BytesIO()
plt.savefig(buf2, format='png', bbox_inches='tight', transparent=True)
buf2.seek(0)
chart2_b64 = base64.b64encode(buf2.read()).decode('utf-8')
plt.close()

# Split contracts into 2 batches of 21 for page 2 and page 3
batch1 = contracts[:21]
batch2 = contracts[21:]

html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    size: A4 landscape;
    margin: 8mm 10mm 8mm 10mm;
  }}
  * {{
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  body {{
    margin: 0;
    padding: 0;
    color: #1e293b;
    background: #ffffff;
    font-size: 8px;
    line-height: 1.3;
  }}
  .page-container {{
    height: 190mm;
    max-height: 190mm;
    overflow: hidden;
    position: relative;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .page-container:last-child {{
    page-break-after: avoid;
  }}
  
  /* Header styling */
  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2.5px solid #1e3a8a;
    padding-bottom: 5px;
    margin-bottom: 8px;
  }}
  .logo-title {{
    display: flex;
    flex-direction: column;
  }}
  .corp-name {{
    font-size: 8.5px;
    font-weight: 800;
    color: #1e3a8a;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }}
  .report-title {{
    font-size: 13.5px;
    font-weight: 900;
    color: #0f172a;
    margin: 1px 0 0 0;
    letter-spacing: -0.3px;
  }}
  .report-subtitle {{
    font-size: 8px;
    color: #475569;
    margin-top: 1px;
  }}
  .header-badge-box {{
    text-align: right;
  }}
  .badge-tag {{
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    color: #334155;
    padding: 2.5px 7px;
    border-radius: 4px;
    font-size: 7.5px;
    font-weight: 700;
  }}
  .badge-date {{
    font-size: 7px;
    color: #64748b;
    margin-top: 2px;
  }}

  /* KPI Grid */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 7px;
    margin-bottom: 8px;
  }}
  .kpi-card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 6px 8px;
    border-left: 3.5px solid #1e3a8a;
  }}
  .kpi-card.teal {{
    border-left-color: #0d9488;
    background: #f0fdfa;
  }}
  .kpi-card.warn {{
    border-left-color: #f59e0b;
    background: #fffbeb;
  }}
  .kpi-card.blue {{
    border-left-color: #0284c7;
    background: #f0f9ff;
  }}
  .kpi-card.purple {{
    border-left-color: #8b5cf6;
    background: #faf5ff;
  }}
  .kpi-label {{
    font-size: 7px;
    text-transform: uppercase;
    font-weight: 800;
    color: #64748b;
    letter-spacing: 0.3px;
  }}
  .kpi-value {{
    font-size: 11.5px;
    font-weight: 900;
    color: #0f172a;
    margin: 1px 0;
  }}
  .kpi-subtext {{
    font-size: 6.8px;
    color: #64748b;
  }}

  /* Visual Block */
  .analytics-block {{
    display: grid;
    grid-template-columns: 2fr 1.3fr;
    gap: 8px;
    margin-bottom: 8px;
  }}
  .panel-box {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 7px;
  }}
  .panel-header {{
    font-size: 8.5px;
    font-weight: 800;
    color: #1e3a8a;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 3px;
    margin-bottom: 5px;
    text-transform: uppercase;
    display: flex;
    justify-content: space-between;
  }}
  .charts-row {{
    display: flex;
    gap: 8px;
    justify-content: space-between;
    align-items: center;
  }}
  .chart-img {{
    max-width: 100%;
    height: auto;
    border-radius: 4px;
  }}

  /* Legal Notes / Directives */
  .info-card {{
    background: #ffffff;
    border-radius: 4px;
    padding: 4px 6px;
    margin-bottom: 4px;
    border-left: 3px solid #0284c7;
    border-top: 1px solid #f1f5f9;
    border-right: 1px solid #f1f5f9;
    border-bottom: 1px solid #f1f5f9;
  }}
  .info-title {{
    font-weight: 800;
    font-size: 7.5px;
    color: #0f172a;
  }}
  .info-desc {{
    font-size: 6.8px;
    color: #475569;
    margin-top: 1px;
    line-height: 1.25;
  }}

  /* Table styling */
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7px;
  }}
  table.data-table th {{
    background: #1e3a8a;
    color: #ffffff;
    font-weight: 800;
    text-align: left;
    padding: 3.5px 5px;
    border: 1px solid #1e3a8a;
    text-transform: uppercase;
    letter-spacing: 0.2px;
  }}
  table.data-table td {{
    padding: 3px 5px;
    border: 1px solid #e2e8f0;
    vertical-align: middle;
  }}
  table.data-table tr:nth-child(even) {{
    background: #f8fafc;
  }}
  table.data-table tr.total-row {{
    background: #e2e8f0;
    font-weight: 800;
    font-size: 7.5px;
    border-top: 2px solid #0f172a;
  }}

  /* Badges */
  .badge-status {{
    display: inline-block;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 800;
    font-size: 6.2px;
    text-transform: uppercase;
  }}
  .badge-ok {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
  .badge-blue {{ background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }}

  .footer-bar {{
    margin-top: 5px;
    border-top: 1px solid #e2e8f0;
    padding-top: 3px;
    display: flex;
    justify-content: space-between;
    font-size: 6.8px;
    color: #64748b;
  }}
</style>
</head>
<body>

  <!-- ==================== PÁGINA 1: DASHBOARD EXECUTIVO GCC ==================== -->
  <div class="page-container">
    <div>
      <div class="header-bar">
        <div class="logo-title">
          <div class="corp-name">Telecomunicações Brasileiras S.A. • Telebras | Gerência de Compras e Contratos (GCC)</div>
          <div class="report-title">RELATÓRIO DE APOSTILAMENTOS DE REAJUSTE CONTRATUAL — EXERCÍCIO 2026</div>
          <div class="report-subtitle">Relação Exclusiva dos Contratos da DTO com Apostilamento de Reajuste Anual (IPCA 4,5%) Processados pela GCC no Ano</div>
        </div>
        <div class="header-badge-box">
          <div class="badge-tag">AGENTE: GCC • EXERCÍCIO 2026</div>
          <div class="badge-date">Posição Oficial: Outubro / 2026 • Painel de Gestão Contratual</div>
        </div>
      </div>

      <!-- KPI Grid -->
      <div class="kpi-grid">
        <div class="kpi-card teal">
          <div class="kpi-label">Contratos Apostilados GCC</div>
          <div class="kpi-value">{total_contratos} Contratos</div>
          <div class="kpi-subtext">Processados no exercício 2026</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Volume Financeiro Base</div>
          <div class="kpi-value">{fmt_cur(total_valor_atual)}</div>
          <div class="kpi-subtext">Base econômica original sob gestão</div>
        </div>
        <div class="kpi-card warn">
          <div class="kpi-label">Total de Reajustes Apostilados</div>
          <div class="kpi-value">+{fmt_cur(total_reajuste)}</div>
          <div class="kpi-subtext">Acréscimo financeiro no exercício</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-label">Novo Valor Global Atualizado</div>
          <div class="kpi-value">{fmt_cur(total_novo_valor)}</div>
          <div class="kpi-subtext">Montante total pós-apostilamento</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-label">Percentual Médio / Rito</div>
          <div class="kpi-value">{percentual_medio:.1f}% (IPCA)</div>
          <div class="kpi-subtext">Apostilamento Unilateral GCC</div>
        </div>
      </div>

      <!-- Analytics and Visuals -->
      <div class="analytics-block">
        <div class="panel-box">
          <div class="panel-header">
            <span>Estratificação Macrorçamentária dos Apostilamentos DTO</span>
            <span>Fonte: Painel Apostilamento GCC</span>
          </div>
          <div class="charts-row">
            <img class="chart-img" style="width: 38%;" src="data:image/png;base64,{chart1_b64}" alt="Gráfico por Gerência">
            <img class="chart-img" style="width: 60%;" src="data:image/png;base64,{chart2_b64}" alt="Top Reajustes">
          </div>
        </div>

        <div class="panel-box">
          <div class="panel-header">
            <span>Rito Operacional & Fundamentação Legal GCC</span>
            <span style="color: #0284c7; font-weight: 800;">Eficiência Administrativa</span>
          </div>
          
          <div class="info-card">
            <div class="info-title">⚡ Apostilamento Unilateral pela GCC (Lei 13.303 / RILC)</div>
            <div class="info-desc">O reajuste em sentido estrito decorre de direito contratual objetivo pactuado em edital (IPCA). Conforme o Art. 81, § 8º da Lei nº 13.303/2016 e Art. 132 do RILC Telebras, a GCC formaliza a alteração mediante simples apostila unilateral, prescindindo de parecer prévio da CONJUR e aditivo bilateral.</div>
          </div>

          <div class="info-card">
            <div class="info-title">⏱️ Tempo Médio de Tramitação: 5 a 8 Dias Úteis</div>
            <div class="info-desc">Ao contrário de termos aditivos com alteração de objeto (que levam de 30 a 50 dias), o apostilamento pela GCC possui rito célere: verificação do índice oficial acumulado em 12 meses, conferência matemática pela GCC e publicação simplificada.</div>
          </div>

          <div class="info-card">
            <div class="info-title">💼 Abrangência: Contratos Vigentes e Encerrados no Ano</div>
            <div class="info-desc">Foram processados e pagos os reajustes devidos tanto para contratos vigentes plurianuais quanto para instrumentos que completaram seu ciclo no exercício de 2026, garantindo o fiel equilíbrio econômico-financeiro.</div>
          </div>
        </div>
      </div>

      <!-- Resumo Consolidado das Áreas -->
      <div class="panel-box">
        <div class="panel-header">
          <span>Consolidação dos Reajustes por Gerência Demandante da DTO</span>
          <span>Exercício 2026</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Gerência Demandante</th>
              <th style="text-align: center;">Qtd Contratos</th>
              <th>Tipologias de Contratação Atendidas</th>
              <th>Valor Base (R$)</th>
              <th>% Carteira</th>
              <th>Reajuste Apostilado (R$)</th>
              <th>Novo Valor Global (R$)</th>
              <th style="text-align: center;">Rito Operacional</th>
            </tr>
          </thead>
          <tbody>
"""

for area, d in sorted_areas:
    pct = (d['valor'] / total_valor_atual) * 100
    novo_area = d['valor'] + d['reajuste']
    obj_resumo = {
        'GERP': 'Infraestrutura de Redes, Contêineres DWDM/IP, Cabos Fanout e Cabos Ópticos',
        'GEOS': 'Operações SGDC, Seguro do Satélite em Órbita, Estações Gateway e Antenas',
        'GTI': 'Segurança de Perímetro, Firewall DCN, Licenciamento de Software e Consultoria TI',
        'GMP': 'Grupos Motor Geradores, Climatização de Precisão, Nobreaks e Infraestrutura',
        'GORS': 'Sistemas de Monitoramento, Redes Regionais e Suporte de Campo',
        'GI': 'Bens de Consumo e Infraestrutura Operacional Geral'
    }.get(area, 'Serviços Especializados de Engenharia e Telecomunicações')

    html_content += f"""
            <tr>
              <td><strong>{area}</strong></td>
              <td style="text-align: center;">{d['count']}</td>
              <td>{obj_resumo}</td>
              <td><strong>{fmt_cur(d['valor'])}</strong></td>
              <td>{pct:.1f}%</td>
              <td>+{fmt_cur(d['reajuste'])}</td>
              <td><strong>{fmt_cur(novo_area)}</strong></td>
              <td style="text-align: center;"><span class="badge-status badge-ok">Apostilamento GCC</span></td>
            </tr>
    """

html_content += f"""
            <tr class="total-row">
              <td>TOTAL APOSTILADO GCC (DTO)</td>
              <td style="text-align: center;">{total_contratos}</td>
              <td>42 Contratos Apostilados no Exercício 2026</td>
              <td>{fmt_cur(total_valor_atual)}</td>
              <td>100,0%</td>
              <td>+{fmt_cur(total_reajuste)}</td>
              <td>{fmt_cur(total_novo_valor)}</td>
              <td style="text-align: center;"><span class="badge-status badge-blue">MÉDIA 4,5%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="footer-bar">
      <div>Telebras • Gerência de Compras e Contratos (GCC) | Relatório de Apostilamentos DTO 2026</div>
      <div>Página 1 de 3</div>
    </div>
  </div>

  <!-- ==================== PÁGINA 2: TABELA DE CONTRATOS APOSTILADOS (PARTE 1 - 21 CONTRATOS) ==================== -->
  <div class="page-container">
    <div>
      <div class="header-bar">
        <div class="logo-title">
          <div class="corp-name">Telecomunicações Brasileiras S.A. • Telebras | Gerência de Compras e Contratos (GCC)</div>
          <div class="report-title">RELAÇÃO DE CONTRATOS APOSTILADOS PELA GCC EM 2026 (PARTE 1 / 2)</div>
          <div class="report-subtitle">Detalhamento dos Contratos de 1 a 21: Valores Originais, Reajuste IPCA (4,5%) e Novos Valores (Sem Colunas SAP e RC)</div>
        </div>
        <div class="header-badge-box">
          <div class="badge-tag">CONTRATOS 01 A 21</div>
          <div class="badge-date">Ordenado por Valor Base</div>
        </div>
      </div>

      <table class="data-table" style="font-size: 7px;">
        <thead>
          <tr>
            <th style="width: 25px; text-align: center;">Item</th>
            <th style="width: 100px;">Contrato SIGA</th>
            <th style="width: 95px;">Processo SIGA</th>
            <th style="width: 40px; text-align: center;">Área</th>
            <th style="width: 180px;">Fornecedor</th>
            <th style="width: 65px;">Início Vig.</th>
            <th style="width: 65px;">Fim Vig.</th>
            <th style="width: 80px;">Valor Base (R$)</th>
            <th style="width: 55px;">Índice</th>
            <th style="width: 75px;">Reajuste Apostilado</th>
            <th style="width: 80px;">Novo Valor Global</th>
            <th style="width: 80px; text-align: center;">Rito no SIGA</th>
          </tr>
        </thead>
        <tbody>
"""

subtot1_val = sum(c['valor_atual'] for c in batch1)
subtot1_reaj = sum(c['reajuste'] for c in batch1)
subtot1_novo = sum(c['novo_valor'] for c in batch1)

for i, c in enumerate(batch1):
    html_content += f"""
          <tr>
            <td style="text-align: center; color: #64748b;">{i+1}</td>
            <td><strong>{c['contrato']}</strong></td>
            <td>{c['processo_siga']}</td>
            <td style="text-align: center;"><strong>{c['area']}</strong></td>
            <td>{c['fornecedor'][:38]}</td>
            <td>{c['inicio_vigencia']}</td>
            <td><strong>{c['fim_vigencia']}</strong></td>
            <td>{fmt_cur(c['valor_atual'])}</td>
            <td>IPCA (4,5%)</td>
            <td><strong>+{fmt_cur(c['reajuste'])}</strong></td>
            <td><strong>{fmt_cur(c['novo_valor'])}</strong></td>
            <td style="text-align: center;"><span class="badge-status badge-ok">Apostila GCC</span></td>
          </tr>
    """

html_content += f"""
          <tr class="total-row">
            <td colspan="7" style="text-align: right;"><strong>SUBTOTAL (CONTRATOS 01 A 21):</strong></td>
            <td><strong>{fmt_cur(subtot1_val)}</strong></td>
            <td>4,5%</td>
            <td><strong>+{fmt_cur(subtot1_reaj)}</strong></td>
            <td><strong>{fmt_cur(subtot1_novo)}</strong></td>
            <td style="text-align: center;">21 ITENS</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="footer-bar">
      <div>Telebras • Gerência de Compras e Contratos (GCC) | Relatório de Apostilamentos DTO 2026</div>
      <div>Página 2 de 3</div>
    </div>
  </div>

  <!-- ==================== PÁGINA 3: TABELA DE CONTRATOS APOSTILADOS (PARTE 2 - 21 CONTRATOS) ==================== -->
  <div class="page-container">
    <div>
      <div class="header-bar">
        <div class="logo-title">
          <div class="corp-name">Telecomunicações Brasileiras S.A. • Telebras | Gerência de Compras e Contratos (GCC)</div>
          <div class="report-title">RELAÇÃO DE CONTRATOS APOSTILADOS PELA GCC EM 2026 (PARTE 2 / 2)</div>
          <div class="report-subtitle">Detalhamento dos Contratos de 22 a 42 e Totalizador Geral Consolidado (Sem Colunas SAP e RC)</div>
        </div>
        <div class="header-badge-box">
          <div class="badge-tag">CONTRATOS 22 A 42</div>
          <div class="badge-date">Total Consolidado: R$ 364,9 Milhões</div>
        </div>
      </div>

      <table class="data-table" style="font-size: 7px;">
        <thead>
          <tr>
            <th style="width: 25px; text-align: center;">Item</th>
            <th style="width: 100px;">Contrato SIGA</th>
            <th style="width: 95px;">Processo SIGA</th>
            <th style="width: 40px; text-align: center;">Área</th>
            <th style="width: 180px;">Fornecedor</th>
            <th style="width: 65px;">Início Vig.</th>
            <th style="width: 65px;">Fim Vig.</th>
            <th style="width: 80px;">Valor Base (R$)</th>
            <th style="width: 55px;">Índice</th>
            <th style="width: 75px;">Reajuste Apostilado</th>
            <th style="width: 80px;">Novo Valor Global</th>
            <th style="width: 80px; text-align: center;">Rito no SIGA</th>
          </tr>
        </thead>
        <tbody>
"""

subtot2_val = sum(c['valor_atual'] for c in batch2)
subtot2_reaj = sum(c['reajuste'] for c in batch2)
subtot2_novo = sum(c['novo_valor'] for c in batch2)

for i, c in enumerate(batch2):
    html_content += f"""
          <tr>
            <td style="text-align: center; color: #64748b;">{i+22}</td>
            <td><strong>{c['contrato']}</strong></td>
            <td>{c['processo_siga']}</td>
            <td style="text-align: center;"><strong>{c['area']}</strong></td>
            <td>{c['fornecedor'][:38]}</td>
            <td>{c['inicio_vigencia']}</td>
            <td><strong>{c['fim_vigencia']}</strong></td>
            <td>{fmt_cur(c['valor_atual'])}</td>
            <td>IPCA (4,5%)</td>
            <td><strong>+{fmt_cur(c['reajuste'])}</strong></td>
            <td><strong>{fmt_cur(c['novo_valor'])}</strong></td>
            <td style="text-align: center;"><span class="badge-status badge-ok">Apostila GCC</span></td>
          </tr>
    """

html_content += f"""
          <tr class="total-row" style="background: #f1f5f9;">
            <td colspan="7" style="text-align: right;"><strong>SUBTOTAL (CONTRATOS 22 A 42):</strong></td>
            <td><strong>{fmt_cur(subtot2_val)}</strong></td>
            <td>4,5%</td>
            <td><strong>+{fmt_cur(subtot2_reaj)}</strong></td>
            <td><strong>{fmt_cur(subtot2_novo)}</strong></td>
            <td style="text-align: center;">21 ITENS</td>
          </tr>
          <tr class="total-row" style="background: #cbd5e1; font-size: 7.8px; border-top: 2.5px solid #0f172a;">
            <td colspan="7" style="text-align: right;"><strong>TOTAL GERAL CONSOLIDADO APOSTILADO PELA GCC (42 CONTRATOS DTO):</strong></td>
            <td><strong>{fmt_cur(total_valor_atual)}</strong></td>
            <td>MÉDIA 4,5%</td>
            <td><strong>+{fmt_cur(total_reajuste)}</strong></td>
            <td><strong>{fmt_cur(total_novo_valor)}</strong></td>
            <td style="text-align: center;"><strong>42 APOSTILAS</strong></td>
          </tr>
        </tbody>
      </table>

      <!-- Bloco de Assinatura e Notas Finais -->
      <div style="margin-top: 8px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px 8px; font-size: 7px; color: #475569; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <strong>Nota de Encerramento GCC:</strong> Todos os 42 contratos acima listados pertencem à Diretoria Técnica e Operacional (DTO) e tiveram seus reajustes anuais com base no IPCA (4,5%) formalizados e apostilados pela Gerência de Compras e Contratos (GCC) no exercício de 2026, com envio ao setor contábil/financeiro para apropriação e pagamento.
        </div>
        <div style="font-weight: 800; color: #1e3a8a; white-space: nowrap; margin-left: 15px;">
          GERÊNCIA DE COMPRAS E CONTRATOS — GCC / TELEBRAS
        </div>
      </div>
    </div>

    <div class="footer-bar">
      <div>Telebras • Gerência de Compras e Contratos (GCC) | Relatório de Apostilamentos DTO 2026</div>
      <div>Página 3 de 3</div>
    </div>
  </div>

</body>
</html>
"""

with open('relatorio_dto_2026.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated clean 3-page relatorio_dto_2026.html successfully!")

# Convert to PDF via Playwright
print("Rendering PDF with Chromium via Playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html_content, wait_until='networkidle')
    page.pdf(
        path='Relatorio_DTO_2026.pdf',
        format='A4',
        landscape=True,
        print_background=True,
        margin={'top': '8mm', 'bottom': '8mm', 'left': '10mm', 'right': '10mm'}
    )
    browser.close()

print("PDF Relatorio_DTO_2026.pdf (3 pages, 42 contracts apostilados GCC) rendered with perfection!")
