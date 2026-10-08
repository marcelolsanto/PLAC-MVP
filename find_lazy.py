import urllib.request
import re

url = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/main-ASI6JQ73.js"
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
# Find lazy loaded chunks
lazy_chunks = re.findall(r'\"([a-zA-Z0-9_\-]+\.js)\"', content)
print("Lazy chunks:", set(lazy_chunks))
