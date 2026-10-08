import pandas as pd
import warnings
warnings.filterwarnings('ignore')

f_kanban = 'BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026_ATUALIZADA.xlsx'
df_kanban = pd.read_excel(f_kanban, sheet_name='INVENTARIO_GERAL')

# Check all 31 processes in Fase 5 (Triagem & Prontidão GCC)
fase5 = df_kanban[df_kanban['Fase Kanban'].str.contains('5. Triagem', na=False)]
print("=== PROCESSOS NA FASE 5 (TRIAGEM & PRONTIDÃO GCC) - PRESTES A PUBLICAR EDITAL NO PNCP ===")
print("Total:", len(fase5))
for idx, r in fase5.iterrows():
    proc = r['Processo SIGA']
    dir_dem = r['Diretoria']
    ger = r['Gerência Demandante']
    obj = r['Objeto Detalhado']
    val = r['Valor Estimado 2026 (R$)']
    dias = r['Dias no Setor']
    status_p = r['Status de Prazo']
    pecas = r['Peças Juntadas no SIGA']
    prox = r['Próximo Documento Obrigatório']
    acao = r['Ação em Andamento']
    print(f"\n[{dir_dem}/{ger}] {proc} | R$ {val:,.2f} | {dias} dias no setor | {status_p}")
    print(f"  Objeto: {obj}")
    print(f"  Peças no SIGA: {pecas}")
    print(f"  Próximo Passo / PNCP: {prox}")
    print(f"  Ação em Andamento: {acao}")

# Check CONJUR (Fase 4)
fase4 = df_kanban[df_kanban['Fase Kanban'].str.contains('4. Análise', na=False)]
print(f"\n=== PROCESSOS NA FASE 4 (CONJUR) - ANTECESSORES DO EDITAL: {len(fase4)} ===")
print("Top 5 maiores valores na CONJUR:")
for idx, r in fase4.sort_values(by='Valor Estimado 2026 (R$)', ascending=False).head(5).iterrows():
    print(f"* [{r['Diretoria']}/{r['Gerência Demandante']}] {r['Processo SIGA']} | R$ {r['Valor Estimado 2026 (R$)']:,.2f} | {r['Objeto Detalhado'][:70]} | Dias CONJUR: {r['Dias no Setor']}")
