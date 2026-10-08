import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-QSWTPHHH.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

# Find 'carregarCompraAcessoPublicoResolver'
for m in re.finditer(r'.{0,100}carregarCompraAcessoPublicoResolver.{0,300}', content):
    print("RESOLVER:", m.group(0))

# Find 'we=' or function we
for m in re.finditer(r'var we\s*=.{0,300}|let we\s*=.{0,300}|const we\s*=.{0,300}|function we\(.{0,300}', content):
    print("DEF we:", m.group(0))
