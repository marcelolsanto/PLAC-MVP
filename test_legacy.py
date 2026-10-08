import urllib.request

urls = [
    "http://comprasnet.gov.br/livre/Pregao/ata0.asp?co_no_uasg=925150&numprp=382026",
    "http://comprasnet.gov.br/livre/Pregao/ata0.asp?co_no_uasg=925150&numprp=000382026",
    "http://comprasnet.gov.br/ConsultaLicitacoes/download/download_editais_detalhe.asp?coduasg=925150&modprp=5&numprp=382026",
    "http://comprasnet.gov.br/ConsultaLicitacoes/download/download_editais_detalhe.asp?coduasg=925150&modprp=5&numprp=000382026",
    "http://comprasnet.gov.br/livre/Pregao/termohom.asp?prgCod=92515005000382026",
    "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras/92515005000382026/itens",
    "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras/92515005000382026/sessao-publica"
]

headers = {'User-Agent': 'Mozilla/5.0'}

for u in urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode('latin1', errors='ignore')
            print(f"[SUCCESS {resp.status}] {u}")
            # look for useful text
            lines = [line.strip() for line in content.split('\n') if len(line.strip()) > 0 and not line.strip().startswith('<')]
            print("   Content sample:", lines[:10])
    except Exception as e:
        print(f"[FAIL] {u} -> {e}")
