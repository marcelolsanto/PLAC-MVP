import urllib.request
import json

# Query PNCP for Telebras (00336701000104)
# PNCP consulta contratacoes publicacao endpoint
url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20240101&dataFinal=20241231&cnpjOrgao=00336701000104&pagina=1&tamanhoPagina=10"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Total 2024:", data.get('totalRegistros'))
        for item in data.get('data', []):
            print("  Item:", item.get('numeroCompra'), item.get('anoCompra'), item.get('modalidadeNome'), item.get('objeto')[:80])
except Exception as e:
    print("Err 2024:", e)

url2 = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260101&dataFinal=20261231&cnpjOrgao=00336701000104&pagina=1&tamanhoPagina=10"
try:
    req = urllib.request.Request(url2, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Total 2026:", data.get('totalRegistros'))
        for item in data.get('data', []):
            print("  Item 2026:", item.get('numeroCompra'), item.get('anoCompra'), item.get('modalidadeNome'), item.get('objeto')[:80])
except Exception as e:
    print("Err 2026:", e)
