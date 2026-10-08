import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-MAJZZURV.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

for m in re.finditer(r'.{0,50}baseUrlFaseExterna.{0,100}', content):
    print("-->", m.group(0))
