import urllib.request
import re

for ano in ["2023", "2024", "2025", "2026"]:
    for mod in [5]: # pregao
        url = f"http://comprasnet.gov.br/ConsultaLicitacoes/download/download_editais_detalhe.asp?coduasg=925150&modprp={mod}&numprp=38{ano}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = urllib.request.urlopen(req, timeout=5).read().decode('latin1', errors='ignore')
            clean = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
            clean = re.sub(r'<[^>]+>', ' ', clean)
            lines = [l.strip() for l in clean.splitlines() if l.strip()]
            txt = " ".join(lines)
            if "não cadastrada" not in txt.lower():
                print(f"FOUND for {ano}: {txt[:400]}")
            else:
                print(f"38/{ano} -> Não cadastrada")
        except Exception as e:
            print(f"Err {ano}: {e}")
