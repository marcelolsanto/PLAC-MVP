import urllib.request
import urllib.error
import json

for ano in ["2026", "2025", "2024"]:
    url = f"https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial={ano}0101&dataFinal={ano}1231&cnpj=00336701000104&codigoModalidadeContratacao=6&pagina=1&tamanhoPagina=50"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
        print(f"[{ano}] Total: {data.get('totalRegistros')}")
        for d in data.get('data', []):
            num = d.get('numeroCompra')
            ano_c = d.get('anoCompra')
            objeto = d.get('objeto', '')
            print(f"   -> Pregão {num}/{ano_c}: {objeto[:100]}")
    except urllib.error.HTTPError as e:
        print(f"[{ano}] Err {e.code}: {e.read().decode('utf-8')[:200]}")
    except Exception as e:
        print(f"[{ano}] Err: {e}")
