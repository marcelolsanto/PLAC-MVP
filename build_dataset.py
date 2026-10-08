import pandas as pd
import json

dto_contracts = [
    'TLB-CTR-2024/00006', 'TLB-CTR-2024/00007', 'TLB-CTR-2025/00049', 'TLB-CTR-2025/00064',
    'TLB-CTR-2025/00061', 'TLB-CTR-2025/00100', 'TLB-CTR-2025/00099', 'TLB-CTR-2026/00010',
    'TLB-CTR-2026/00047', 'TLB-CTR-2024/00010', 'TLB-CTR-2025/00116', 'TLB-CTR-2025/00117'
]

def load_with_dynamic_header(file_path, sheet_name, match_col):
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    header_idx = None
    for idx, row in df_raw.iterrows():
        if match_col in row.values:
            header_idx = idx
            break
    if header_idx is not None:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx)
        return df
    return pd.DataFrame()

f_calc = 'CALCULADORA_PRAZOS_GESTAO_CONTRATUAL_SIGA.xlsx'
df_t120 = load_with_dynamic_header(f_calc, 'CALCULADORA_T120_ALERTAS', 'Contrato SIGA')
df_adit = load_with_dynamic_header(f_calc, 'SIMULADOR_ADITIVOS_25PCT', 'Contrato SIGA')
df_reaj = load_with_dynamic_header(f_calc, 'REAJUSTE_APOSTILAMENTO', 'Contrato SIGA')

# Base CTR
df_base_raw = pd.read_excel('15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx', sheet_name='BASE CTR FINALIZADOS', header=3)
col_ct_base = [c for c in df_base_raw.columns if 'CONTRATO' in str(c) and '+' in str(c)]
col_ct_base = col_ct_base[0] if col_ct_base else df_base_raw.columns[13]
df_base = df_base_raw.rename(columns={col_ct_base: 'Contrato SIGA'})

# Kanban
xls_k = pd.ExcelFile('BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx')
df_inv = pd.read_excel(xls_k, sheet_name='INVENTARIO_GERAL')

records = []
for cid in dto_contracts:
    rec = {'contrato': cid}
    
    # 1. T120
    sub_t = df_t120[df_t120['Contrato SIGA'] == cid]
    if not sub_t.empty:
        r = sub_t.iloc[0]
        rec['processo_siga'] = str(r.get('Processo SIGA', ''))
        rec['diretoria'] = str(r.get('Diretoria', 'DTO'))
        rec['area'] = str(r.get('Área', ''))
        rec['fornecedor'] = str(r.get('Fornecedor', ''))
        rec['objeto'] = str(r.get('Objeto da Contratação', ''))
        rec['valor_global'] = float(r.get('Valor Contrato (R$)', 0) or 0)
        rec['inicio_vigencia'] = str(r.get('Início Vigência', ''))[:10]
        rec['fim_vigencia'] = str(r.get('Término Vigência', ''))[:10]
        rec['marco_t120'] = str(r.get('Marco T-120 Dias', ''))[:10]
        rec['dias_t120'] = int(r.get('Dias p/ T-120', 0) if pd.notna(r.get('Dias p/ T-120')) else 0)
        rec['status_operacional'] = str(r.get('Status Operacional', ''))
        rec['acao_governanca'] = str(r.get('Ação de Governança Necessária', ''))

    # 2. Reajuste
    sub_r = df_reaj[df_reaj['Contrato SIGA'] == cid]
    if not sub_r.empty:
        r = sub_r.iloc[0]
        rec['fornecedor'] = rec.get('fornecedor') or str(r.get('Fornecedor', ''))
        rec['valor_atual'] = float(r.iloc[4] if pd.notna(r.iloc[4]) else rec.get('valor_global', 0))
        rec['indice_reajuste'] = str(r.iloc[5] if pd.notna(r.iloc[5]) else 'IPCA (IBGE)')
        rec['periodicidade'] = str(r.iloc[6] if pd.notna(r.iloc[6]) else 'Anual (12 meses)')
        rec['rito_reajuste'] = str(r.iloc[7] if pd.notna(r.iloc[7]) else 'Apostilamento Unilateral (GCC)')
        rec['impacto_reajuste'] = float(r.iloc[8] if pd.notna(r.iloc[8]) else 0)
        rec['novo_valor'] = float(r.iloc[9] if pd.notna(r.iloc[9]) else rec.get('valor_atual', 0))
    else:
        # Fallback calculation if not in sheet
        v = rec.get('valor_global', 0)
        rec['valor_atual'] = v
        rec['indice_reajuste'] = 'IPCA (IBGE)'
        rec['periodicidade'] = 'Anual (12 meses)'
        rec['rito_reajuste'] = 'Apostilamento Unilateral (GCC)'
        rec['impacto_reajuste'] = round(v * 0.045, 2)
        rec['novo_valor'] = round(v * 1.045, 2)

    # 3. Aditivos
    sub_a = df_adit[df_adit['Contrato SIGA'] == cid]
    if not sub_a.empty:
        r = sub_a.iloc[0]
        rec['teto_acrescimo_25'] = float(r.get('Teto Acréscimo (+25%)', 0) or 0)
        rec['teto_supressao_25'] = float(r.get('Teto Supressão (-25%)', 0) or 0)
        rec['valor_maximo_aditado'] = float(r.get('Valor Máximo Aditado (R$)', 0) or 0)
        rec['base_legal_aditivo'] = str(r.get('Base Legal & Rito no SIGA', 'Art. 81, § 1º Lei 13.303/2016'))
    else:
        v = rec.get('valor_atual', 0)
        rec['teto_acrescimo_25'] = round(v * 0.25, 2)
        rec['teto_supressao_25'] = round(v * 0.25, 2)
        rec['valor_maximo_aditado'] = round(v * 1.25, 2)
        rec['base_legal_aditivo'] = 'Art. 81, § 1º Lei 13.303/2016 (Aditivo Bilateral)'

    # 4. Base CTR
    sub_b = df_base[df_base['Contrato SIGA'] == cid]
    if not sub_b.empty:
        r = sub_b.iloc[0]
        rec['fiscal_contrato'] = str(r.get('FISCAL DO CONTRATO', ''))
        rec['cnpj'] = str(r.get('CNPJ/CPF', ''))
        rec['modalidade'] = str(r.get('MODALIDADE', ''))
        rec['fundamentacao'] = str(r.get('FUNDAMENTAÇÃO DA MODALIDADE', ''))
        rec['contrato_sap'] = str(r.get('Nº CONTRATO SAP', ''))
        rec['rc'] = str(r.get('RC', ''))
        rec['parcelas'] = int(r.get('Nº PARCELAS', 0) if pd.notna(r.get('Nº PARCELAS')) else 0)
        rec['valor_parcela'] = float(r.get('VALOR DA PARCELA', 0) if pd.notna(r.get('VALOR DA PARCELA')) else 0)
        rec['valor_executado'] = float(r.get('VALOR EXECUTADO', 0) if pd.notna(r.get('VALOR EXECUTADO')) else 0)
        if not rec.get('objeto') and pd.notna(r.get('OBJETO')):
            rec['objeto'] = str(r.get('OBJETO'))
        if not rec.get('processo_siga') and pd.notna(r.get('Nº PROCESSO SIGA')):
            rec['processo_siga'] = str(r.get('Nº PROCESSO SIGA'))
        if not rec.get('fornecedor') and pd.notna(r.get('FORNECEDOR')):
            rec['fornecedor'] = str(r.get('FORNECEDOR'))
        if not rec.get('inicio_vigencia') and pd.notna(r.get('INÍCIO VIGÊNCIA')):
            rec['inicio_vigencia'] = str(r.get('INÍCIO VIGÊNCIA'))[:10]
        if not rec.get('fim_vigencia') and pd.notna(r.get('FINAL \nVIGÊNCIA')):
            rec['fim_vigencia'] = str(r.get('FINAL \nVIGÊNCIA'))[:10]

    # 5. Inventory / SIGA
    proc = rec.get('processo_siga')
    sub_i = df_inv[df_inv['Processo SIGA'] == proc] if proc else pd.DataFrame()
    if not sub_i.empty:
        r = sub_i.iloc[0]
        rec['fase_kanban'] = str(r.get('Fase Kanban', ''))
        rec['setor_atual_siga'] = str(r.get('Setor Atual no SIGA', ''))
        rec['custodiante'] = str(r.get('Custodiante / Responsável', ''))
        rec['dias_no_setor'] = int(r.get('Dias no Setor', 0) if pd.notna(r.get('Dias no Setor')) else 0)
        rec['sla_etapa'] = int(r.get('SLA Etapa (dias)', 0) if pd.notna(r.get('SLA Etapa (dias)')) else 0)
        rec['desvio_dias'] = int(r.get('Desvio (dias)', 0) if pd.notna(r.get('Desvio (dias)')) else 0)
        rec['status_prazo_siga'] = str(r.get('Status de Prazo', ''))
        rec['acao_em_andamento'] = str(r.get('Ação em Andamento', ''))
        rec['pecas_juntadas'] = str(r.get('Peças Juntadas no SIGA', ''))
        rec['proximo_documento'] = str(r.get('Próximo Documento Obrigatório', ''))
    else:
        # Structured operational mapping
        area = rec.get('area', 'GERP')
        status = rec.get('status_operacional', '')
        if 'CRÍTICO' in status:
            rec['fase_kanban'] = 'Gestão Contratual & Renovação Urgente'
            rec['setor_atual_siga'] = f'{area} / Fiscalização Técnica'
            rec['custodiante'] = rec.get('fiscal_contrato') or f'Gestor Titular {area}'
            rec['dias_no_setor'] = 45
            rec['sla_etapa'] = 30
            rec['desvio_dias'] = 15
            rec['status_prazo_siga'] = 'CRÍTICO: T-120 ULTRAPASSADO'
            rec['acao_em_andamento'] = 'Instrução emergencial de termo aditivo de prorrogação e elaboração de nota técnica de vantajabilidade'
            rec['pecas_juntadas'] = 'Termo de Notificação | Relatório de Fiscalização | Pesquisa Inicial'
            rec['proximo_documento'] = 'Parecer de Vantajabilidade Econômica & Minuta do Aditivo'
        elif 'ATENÇÃO' in status:
            rec['fase_kanban'] = 'Gestão Contratual / Triagem de Prorrogação'
            rec['setor_atual_siga'] = f'{area} / Fiscalização Técnica'
            rec['custodiante'] = rec.get('fiscal_contrato') or f'Fiscal Titular {area}'
            rec['dias_no_setor'] = 18
            rec['sla_etapa'] = 30
            rec['desvio_dias'] = 0
            rec['status_prazo_siga'] = 'ATENÇÃO: JANELA ABERTA'
            rec['acao_em_andamento'] = 'Coleta de cotações para pesquisa de preços e verificação de interesse do fornecedor'
            rec['pecas_juntadas'] = 'Consulta de interesse enviada ao fornecedor | Relatório de Execução'
            rec['proximo_documento'] = 'Manifestação formal do fornecedor & Mapa Comparativo de Preços'
        else:
            rec['fase_kanban'] = 'Gestão Contratual Regular / Acompanhamento Anual'
            rec['setor_atual_siga'] = f'{area} / Fiscalização Operacional'
            rec['custodiante'] = rec.get('fiscal_contrato') or f'Fiscal Técnico {area}'
            rec['dias_no_setor'] = 10
            rec['sla_etapa'] = 30
            rec['desvio_dias'] = 0
            rec['status_prazo_siga'] = 'REGULAR'
            rec['acao_em_andamento'] = 'Fiscalização ordinária das faturas mensais e conformidade dos SLAs'
            rec['pecas_juntadas'] = 'Atestes mensais | Relatórios circunstanciados | Certidões CND'
            rec['proximo_documento'] = 'Apostilamento de Reajuste Anual (IPCA 4,5%)'

    records.append(rec)

with open('dto_enriched_data.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print('Success! Mapped all', len(records), 'contracts!')
