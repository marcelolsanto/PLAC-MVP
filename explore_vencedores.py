import pandas as pd, warnings, json, os
from datetime import datetime
warnings.filterwarnings('ignore')

fname = [f for f in os.listdir('.') if 'PREG' in f.upper() and f.endswith('.xlsx')][0]
df_raw = pd.read_excel(fname, sheet_name='CONTROLE PEs e DEs', header=None)

def cs(s):
    if not s or pd.isna(s): return ''
    r = str(s)
    for k, v in [
        ('PREG\ufffdO','PREGÃO'),('CONTRATA\ufffdO','CONTRATAÇÃO'),('AQUISI\ufffdO','AQUISIÇÃO'),
        ('LICITA\ufffdO','LICITAÇÃO'),('DISPENSA ELETR\ufffdNICA','DISPENSA ELETRÔNICA'),
        ('TRADI\ufffdO','TRADIÇÃO'),('INSTRU\ufffdO','INSTRUÇÃO'),('SOLU\ufffdES','SOLUÇÕES'),
        ('\ufffdREA','ÁREA'),('SERVI\ufffdO','SERVIÇO'),('MODALIDADE DA LICITA','MODALIDADE DA LICITA'),
        ('SESS\ufffdO','SESSÃO'),('PUBLICA\ufffdO','PUBLICAÇÃO'),('ADJUDICA\ufffdO','ADJUDICAÇÃO'),
        ('INSTALA\ufffdO','INSTALAÇÃO'),('SA\ufffdDE','SAÚDE'),('REVIS\ufffdO','REVISÃO'),
        ('MONITORAMENTO','MONITORAMENTO'),('MEDI\ufffdO','MEDIÇÃO'),('CLIMATIZA\ufffdO','CLIMATIZAÇÃO'),
        ('ESPECIALI','ESPECIALI'),('\ufffd','')
    ]:
        r = r.replace(k, v)
    return r.strip()

def fmt_val(v):
    if not v or pd.isna(v) or str(v) in ('0', '0.0', '-', 'nan'): return '—'
    try:
        fv = float(v)
        if fv == 0: return '—'
        return f"R$ {fv:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    except:
        return str(v)

def fmt_date(v):
    if not v or pd.isna(v) or str(v) in ('nan','-',''): return '—'
    try:
        if isinstance(v, datetime): return v.strftime('%d/%m/%Y')
        return str(v)[:10]
    except:
        return str(v)

# Extrair TODOS os processos de 2026 (finalizados + em andamento)
registros_2026 = []
for row_i in range(4, len(df_raw)):
    row = df_raw.iloc[row_i].tolist()
    ano = row[3] if len(row) > 3 else None
    if not ano or pd.isna(ano): continue
    try:
        if int(float(str(ano))) != 2026: continue
    except:
        continue

    status = cs(str(row[4])) if len(row) > 4 else ''
    etapa = cs(str(row[5])) if len(row) > 5 else ''
    diretoria = str(row[6]).replace('3000-DTO','DTO').replace('2000-DAFRI','DAFRI').replace('4000-DC','DC').replace('5000-DG','DG').replace('1000-PRES','PRES') if len(row) > 6 else ''
    area = cs(str(row[7])) if len(row) > 7 else ''
    responsavel = cs(str(row[8])) if len(row) > 8 else ''
    modalidade = cs(str(row[9])) if len(row) > 9 else ''
    processo = str(row[10]) if len(row) > 10 and str(row[10]) not in ('nan','') else ''
    aviso = str(row[11]) if len(row) > 11 and str(row[11]) not in ('nan','') else ''
    licitacao = str(row[12]) if len(row) > 12 and str(row[12]) not in ('nan','') else ''
    objeto = cs(str(row[13])) if len(row) > 13 else ''
    observacoes = cs(str(row[14])) if len(row) > 14 else ''
    data_sessao = fmt_date(row[17]) if len(row) > 17 else '—'
    npart = row[22] if len(row) > 22 and str(row[22]) not in ('nan','') else 0
    empresa = cs(str(row[23])) if len(row) > 23 and str(row[23]) not in ('nan','-','') else '—'
    cnpj = str(row[24]).strip() if len(row) > 24 and str(row[24]) not in ('nan','-','') else '—'
    estimado = fmt_val(row[27]) if len(row) > 27 else '—'
    lance = fmt_val(row[28]) if len(row) > 28 else '—'
    negociado = fmt_val(row[29]) if len(row) > 29 else '—'
    homologado = fmt_val(row[30]) if len(row) > 30 else '—'
    economia = fmt_val(row[31]) if len(row) > 31 else '—'
    pct_desc = row[32] if len(row) > 32 and str(row[32]) not in ('nan','') else None
    pct_desc_str = f"{float(pct_desc)*100:.1f}%" if pct_desc and str(pct_desc) not in ('nan','') else '—'
    data_sessao_pub = fmt_date(row[17]) if len(row) > 17 else '—'
    data_adjudic = fmt_date(row[35]) if len(row) > 35 else '—'
    mes_hom = cs(str(row[36])) if len(row) > 36 and str(row[36]) not in ('nan','') else '—'
    data_dou = fmt_date(row[37]) if len(row) > 37 else '—'
    tempo_total = row[38] if len(row) > 38 and str(row[38]) not in ('nan','') else '—'

    # Classificar
    if etapa in ('EM ANDAMENTO','DISPUTA','PROPOSTAS/ ESCLAREC/ IMPUGN'):
        fase = 'EM DISPUTA'
    elif etapa in ('EM INSTRUÇÃO','EDIÇÃO','EM INSTRUCAO'):
        fase = 'EM INSTRUÇÃO'
    elif status == 'HOMOLOGADO':
        fase = 'HOMOLOGADO (FINALIZADO)'
    elif status == 'FRACASSADO':
        fase = 'FRACASSADO'
    elif status == 'REVOGADO':
        fase = 'REVOGADO'
    else:
        fase = status

    # Objeto resumo (60 chars)
    objeto_short = objeto[:65] + ('...' if len(objeto) > 65 else '')

    registros_2026.append({
        'ano': 2026,
        'status': status,
        'etapa': etapa,
        'fase': fase,
        'diretoria': diretoria,
        'area': area,
        'responsavel': responsavel,
        'modalidade': modalidade,
        'processo': processo,
        'licitacao': licitacao,
        'objeto': objeto,
        'objeto_short': objeto_short,
        'observacoes': observacoes,
        'data_sessao': data_sessao_pub,
        'n_participantes': int(float(str(npart))) if str(npart) not in ('nan','','-') else 0,
        'empresa_vencedora': empresa,
        'cnpj': cnpj,
        'valor_estimado': estimado,
        'lance_final': lance,
        'negociado': negociado,
        'homologado_val': homologado,
        'economia': economia,
        'pct_desconto': pct_desc_str,
        'data_adjudicacao': data_adjudic,
        'mes_homologacao': mes_hom,
        'data_dou': data_dou,
        'tempo_total_dias': str(tempo_total) if str(tempo_total) != 'nan' else '—',
    })

print(f"Total processos 2026: {len(registros_2026)}")
print()

# Estatísticas
from collections import Counter
fases = Counter(r['fase'] for r in registros_2026)
print("Por fase:")
for f, c in fases.most_common():
    print(f"  {f}: {c}")

print()
dto_procs = [r for r in registros_2026 if 'DTO' in r['diretoria']]
print(f"DTO: {len(dto_procs)}")
for r in dto_procs:
    print(f"  [{r['fase']}] {r['area']} | {r['empresa_vencedora'][:30]} | {r['objeto_short']}")
    print(f"    Processo: {r['processo']} | Valor Est: {r['valor_estimado']} | Hom: {r['homologado_val']}")

# Salva JSON
with open('vencedores_2026_data.json', 'w', encoding='utf-8') as f:
    json.dump(registros_2026, f, ensure_ascii=False, indent=2)
print(f"\nDados salvos em vencedores_2026_data.json")
