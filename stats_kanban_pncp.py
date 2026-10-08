import pandas as pd
import json

f_kanban = 'BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx'
df_kanban = pd.read_excel(f_kanban, sheet_name='INVENTARIO_GERAL')

# Fase 5: Triagem & Prontidão GCC
fase5 = df_kanban[df_kanban['Fase Kanban'].str.contains('5. Triagem', na=False)].copy()
fase4 = df_kanban[df_kanban['Fase Kanban'].str.contains('4. Análise', na=False)].copy()

print(f"Fase 5 (GCC): {len(fase5)} processos | R$ {fase5['Valor Estimado 2026 (R$)'].sum():,.2f}")
print(f"Fase 4 (CONJUR): {len(fase4)} processos | R$ {fase4['Valor Estimado 2026 (R$)'].sum():,.2f}")

# Group by Directorate for Fase 5
print("\nFase 5 por Diretoria:")
for d, sub in fase5.groupby('Diretoria'):
    print(f"  {d}: {len(sub)} processos | R$ {sub['Valor Estimado 2026 (R$)'].sum():,.2f}")

# Check status de prazo in Fase 5
print("\nStatus de Prazo Fase 5:")
print(fase5['Status de Prazo'].value_counts())
