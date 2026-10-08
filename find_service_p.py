import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-QSWTPHHH.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

# Search for obterCompra( in the entire file
for m in re.finditer(r'obterCompra\([^\)]*\)\s*\{[^\}]+\}', content):
    print("Found definition:", m.group(0))

# Or where .get( or .post( is used with /compras/
for m in re.finditer(r'.{0,60}comprasnet-fase-externa.{0,100}', content):
    print("fase-externa:", m.group(0))
