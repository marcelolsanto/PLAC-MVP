import pandas as pd
import warnings
warnings.filterwarnings('ignore')

fname = '6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx'
df = pd.read_excel(fname, sheet_name='CONTROLE PEs e DEs', header=3)

# Print columns and look for dates or recent items
print("Colunas:")
for i, c in enumerate(df.columns):
    print(f"[{i}] {c}")

print("\n--- PROCESSOS RECENTES OU COM SESSÃO EM SET/OUT/NOV 2026 ---")
for idx, r in df.iterrows():
    ano = r.get('ANO')
    try:
        if float(str(ano)) >= 2025:
            lic = str(r.get('Nº DA LICITAÇÃO', r.get('N° DA LICITAÇÃO', ''))).strip()
            proc = str(r.get('Nº PROCESSO SIGA', r.get('N° PROCESSO SIGA', ''))).strip()
            obj = str(r.get('OBJETO', ''))[:60].strip()
            sessao = str(r.get('DATA SESSÃO PÚBLICA', r.get('DATA SESSAO PUBLICA', ''))).strip()
            status = str(r.get('STATUS', '')).strip()
            etapa = str(r.get('ETAPA', '')).strip()
            obs = str(r.get('DEMANDAS E OBSERVAÇÕES', r.get('DEMANDAS E OBSERVACOES', ''))).strip()
            dir_area = f"{r.get('DIR', '')}/{r.get('ÁREA DEMANDANTE', '')}"
            venc = str(r.get('EMPRESA VENCEDORA', '')).strip()
            
            print(f"Ano: {ano} | Lic: {lic} | Proc: {proc} | {dir_area}")
            print(f"   Status: {status} ({etapa}) | Sessão: {sessao}")
            print(f"   Vencedor: {venc}")
            print(f"   Obj: {obj}...")
            print(f"   Obs: {obs}")
            print()
    except Exception as e:
        pass
