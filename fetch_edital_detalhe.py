import urllib.request
import re

url = "http://comprasnet.gov.br/ConsultaLicitacoes/download/download_editais_detalhe.asp?coduasg=925150&modprp=5&numprp=382026"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
content = urllib.request.urlopen(req, timeout=10).read().decode('latin1', errors='ignore')

# Strip tags and show text
clean = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
clean = re.sub(r'<style.*?</style>', '', clean, flags=re.DOTALL)
clean = re.sub(r'<[^>]+>', ' ', clean)
lines = [l.strip() for l in clean.splitlines() if l.strip()]
print("\n".join(lines))
