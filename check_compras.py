import urllib.request
import json
import re

compra_id = "92515005000382026"

# Let's search inside the JS chunks for API endpoints
urls_to_check = [
    f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras/{compra_id}",
    f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/api/compras/{compra_id}",
    f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/api/v1/compras/{compra_id}",
    f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/v1/compras/{compra_id}",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

for u in urls_to_check:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            print("SUCCESS:", u, resp.status)
            print(resp.read().decode('utf-8')[:500])
    except Exception as e:
        print("FAIL:", u, e)
