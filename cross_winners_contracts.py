import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

fname = [f for f in os.listdir('.') if 'PREG' in f.upper() and f.endswith('.xlsx')][0]
df_preg = pd.read_excel(fname, sheet_name='CONTROLE PEs e DEs', header=3)

# Load contracts
df_ctr = pd.read_excel('15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx', sheet_name='BASE CTR FINALIZADOS', header=3)
col_proc_ctr = [c for c in df_ctr.columns if 'PROCESSO' in str(c).upper()][0]
contratos_processos = set(df_ctr[col_proc_ctr].dropna().astype(str).str.strip())
print(f"Contratos finalizados com processos: {len(contratos_processos)}")

# Check pregões
print("\n=== PREGÕES / PROCESSOS LICITATÓRIOS 2026 ===")
for idx, r in df_preg.iterrows():
    ano = r.get('ANO')
    try:
        if int(float(str(ano))) == 2026:
            proc = str(r.get('Nº PROCESSO SIGA', r.get('N° PROCESSO SIGA', r.iloc[10]))).strip()
            status = str(r.get('STATUS', r.iloc[4])).strip()
            etapa = str(r.get('ETAPA', r.iloc[5])).strip()
            dir_dem = str(r.get('DIR', r.iloc[6])).strip()
            area = str(r.get('ÁREA DEMANDANTE', r.iloc[7])).strip()
            empresa = str(r.get('EMPRESA VENCEDORA', r.iloc[23])).strip()
            obj = str(r.get('OBJETO', r.iloc[13]))[:60].strip()
            homol = r.get('HOMOLOGADO', r.iloc[30])
            estimado = r.get(' ESTIMADO', r.iloc[27])
            ja_tem_contrato = proc in contratos_processos
            
            print(f"Proc: {proc} | Dir: {dir_dem}/{area} | Status: {status} ({etapa})")
            print(f"   Vencedor: {empresa}")
            print(f"   Objeto: {obj}...")
            print(f"   Valor Homol: {homol} | Est: {estimado} | Já formalizou CTR? {ja_tem_contrato}")
            print()
    except Exception as e:
        pass
