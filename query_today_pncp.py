import urllib.request, json
import warnings
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0'}

# 1. Consulta PNCP Telebras
print("=== CONSULTA PNCP TELEBRAS (Set/Out 2026) ===")
url = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260901&dataFinal=20261006&cnpjOrgao=00336701000104&pagina=1&tamanhoPagina=20'
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('Total registros:', data.get('totalRegistros'))
        for item in data.get('data', []):
            num = item.get('numeroCompra')
            ano = item.get('anoCompra')
            mod = item.get('modalidadeNome')
            dt = item.get('dataPublicacaoPncp')
            obj = str(item.get('objeto', ''))[:100]
            print(f"- Compra {num}/{ano} | {mod} | Pub: {dt}")
            print(f"  Objeto: {obj}...")
except Exception as e:
    print('Erro PNCP:', e)

# 2. Consulta Comprasnet / Compras.gov.br para UASG 925150
print("\n=== CONSULTA COMPRASNET / SERPRO ===")
# Procura pregões em andamento da Telebras (UASG 925150)
url_cnet = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras?uasg=925150"
try:
    req = urllib.request.Request(url_cnet, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        cdata = json.loads(resp.read().decode('utf-8'))
        print("Comprasnet resposta:", cdata)
except Exception as e:
    print("Erro Comprasnet:", e)
