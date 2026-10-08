import pandas as pd
import warnings
import json, os
warnings.filterwarnings('ignore')

# 1. Inspect BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx
f_kanban = 'BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx'
df_kanban = pd.read_excel(f_kanban, sheet_name='INVENTARIO_GERAL')
print("=== KANBAN INVENTARIO GERAL ===")
print("Total processos:", len(df_kanban))
print("Colunas:", list(df_kanban.columns))
print("\nFases Kanban:")
print(df_kanban['Fase Kanban'].value_counts())
print("\nSetores no SIGA:")
print(df_kanban['Setor Atual no SIGA'].value_counts().head(10))

# 2. Inspect Controle_Execucao_PLAC_GCC.xlsx
f_exec = 'Controle_Execucao_PLAC_GCC.xlsx'
xls_exec = pd.ExcelFile(f_exec)
print("\n=== CONTROLE EXECUCAO PLAC GCC ===")
print("Sheets:", xls_exec.sheet_names)
for s in xls_exec.sheet_names:
    df_s = pd.read_excel(f_exec, sheet_name=s)
    print(f"Sheet [{s}] shape: {df_s.shape}")
    print(f"Sheet [{s}] cols: {list(df_s.columns[:10])}")

# 3. Check processes related to 'edital', 'pncp', 'publicação', 'pregao'
print("\n=== PROCESSOS EM FASE DE EDITAL / LICITAÇÃO / PNCP NO KANBAN ===")
edital_fases = df_kanban[df_kanban['Fase Kanban'].astype(str).str.contains('Edital|Licita|Public|CONJUR|GCC|Termo', case=False, na=False)]
print("Qtd:", len(edital_fases))
for idx, r in edital_fases.head(15).iterrows():
    proc = r.get('Processo SIGA')
    fase = r.get('Fase Kanban')
    setor = r.get('Setor Atual no SIGA')
    resp = r.get('Custodiante / Responsável')
    obj = str(r.get('Objeto Detalhado'))[:60]
    val = r.get('Valor Estimado 2026 (R$)')
    print(f"* {proc} | {fase} | {setor} | Resp: {resp} | Val: {val} | {obj}...")
