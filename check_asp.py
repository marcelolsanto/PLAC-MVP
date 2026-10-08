import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-Y6NI6Z7N.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

for m in re.finditer(r'.{0,50}obterUrlBaseComprasnetAsp.{0,100}', content):
    print("ASP base:", m.group(0))

url2 = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-USTQWP3O.js'
content2 = urllib.request.urlopen(urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

for m in re.finditer(r'.{0,50}chaveCompraFormatoAsp.{0,100}', content2):
    print("Asp format:", m.group(0))
