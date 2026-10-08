import urllib.request
import json

url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20240101&dataFinal=20261231&cnpj=00336701000104&codigoModalidadeContratacao=6&pagina=1&tamanhoPagina=50"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read().decode('utf-8'))

print("Total registros:", data.get('totalRegistros'))
for d in data.get('data', []):
    num = d.get('numeroCompra')
    ano = d.get('anoCompra')
    objeto = d.get('objeto', '')
    print(f"Pregão {num}/{ano}: {objeto[:100]}")
