import urllib.request
import urllib.error

url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20240101&dataFinal=20241231&cnpjOrgao=00336701000104&codigoModalidadeContratacao=6&pagina=1&tamanhoPagina=10"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    print(resp.read().decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.read().decode('utf-8'))
except Exception as e:
    print("Other err:", e)
