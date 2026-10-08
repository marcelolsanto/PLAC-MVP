import json

with open('vencedores_2026_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

homologados = [d for d in data if d['fase'] == 'HOMOLOGADO (FINALIZADO)']
em_disputa = [d for d in data if d['fase'] == 'EM DISPUTA']
em_instrucao = [d for d in data if d['fase'] == 'EM INSTRUÇÃO']

print(f"Total homologados com vencedores: {len(homologados)}")

def parse_cur(s):
    if not s or s == '—': return 0.0
    clean = s.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try: return float(clean)
    except: return 0.0

total_est = sum(parse_cur(d['valor_estimado']) for d in homologados)
total_hom = sum(parse_cur(d['homologado_val']) for d in homologados)
total_eco = sum(parse_cur(d['economia']) for d in homologados)

print(f"Total Estimado: R$ {total_est:,.2f}")
print(f"Total Homologado: R$ {total_hom:,.2f}")
print(f"Total Economia: R$ {total_eco:,.2f}")
if total_est > 0:
    print(f"Desconto Médio Global: {(total_eco/total_est)*100:.1f}%")

print("\n--- HOMOLOGADOS POR DIRETORIA ---")
by_dir = {}
for d in homologados:
    diret = d['diretoria']
    if diret not in by_dir:
        by_dir[diret] = {'count': 0, 'homologado': 0, 'economia': 0}
    by_dir[diret]['count'] += 1
    by_dir[diret]['homologado'] += parse_cur(d['homologado_val'])
    by_dir[diret]['economia'] += parse_cur(d['economia'])

for k, v in sorted(by_dir.items(), key=lambda x: x[1]['homologado'], reverse=True):
    print(f"{k}: {v['count']} processos | Homologado: R$ {v['homologado']:,.2f} | Economia: R$ {v['economia']:,.2f}")

print("\n--- PROCESSOS DTO HOMOLOGADOS ---")
dto_h = [d for d in homologados if d['diretoria'] == 'DTO']
for d in dto_h:
    print(f"* {d['empresa_vencedora']} (CNPJ: {d['cnpj']})")
    print(f"  Processo: {d['processo']} | Pregão: {d['licitacao']} | Área: {d['area']}")
    print(f"  Objeto: {d['objeto'][:80]}")
    print(f"  Estimado: {d['valor_estimado']} -> Homologado: {d['homologado_val']} (Economia: {d['economia']} | {d['pct_desconto']})")
    print(f"  Adjudicado em: {d['data_adjudicacao']} | DOU: {d['data_dou']}")
    print()

print("\n--- PROCESSOS DTO EM DISPUTA / MANIFESTAÇÃO ---")
dto_d = [d for d in em_disputa if d['diretoria'] == 'DTO']
for d in dto_d:
    print(f"* {d['processo']} | {d['licitacao']} | Área: {d['area']}")
    print(f"  Objeto: {d['objeto'][:80]}")
    print(f"  Etapa: {d['etapa']} | Obs: {d['observacoes']}")
    print(f"  Sessão: {d['data_sessao']}")
    print()
