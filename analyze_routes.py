import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-QSWTPHHH.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

# Search for route definition
for m in re.finditer(r'path:\s*["\']acompanhamento-compra["\'].{0,300}', content):
    print("ROUTE:", m.group(0))

for m in re.finditer(r'loadComponent:\s*\(\)\s*=>\s*import\([^\)]+\)', content):
    print("LOAD COMPONENT:", m.group(0))
