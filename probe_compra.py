import urllib.request
import json

compra_id = "92515005000382026"
subpaths = [
    "",
    "/itens",
    "/itens/quadro-demonstrativo",
    "/eventos",
    "/mensagens",
    "/documentos",
    "/sessao-publica",
    "/termos",
    "/resultado",
    "/fase-externa",
    "/edital"
]

base = f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras/{compra_id}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

for sub in subpaths:
    url = base + sub
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode('utf-8')
            print(f"[{resp.status}] {url} -> {data[:300]}")
    except Exception as e:
        print(f"[ERR] {url} -> {e}")
