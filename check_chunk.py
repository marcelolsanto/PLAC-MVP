import urllib.request
import re

url = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-Y6NI6Z7N.js"
headers = {'User-Agent': 'Mozilla/5.0'}
content = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read().decode('utf-8')

for m in re.finditer(r'(/public/v1/compras/[^"\'`\s,]+|/v1/compras/[^"\'`\s,]+)', content):
    print(m.group(0))

# Also search for 'acompanhamento' in this chunk
for m in re.finditer(r'.{0,50}acompanhamento.{0,50}', content):
    print("CTX:", m.group(0))
