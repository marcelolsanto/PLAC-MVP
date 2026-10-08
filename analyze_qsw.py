import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/chunk-QSWTPHHH.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

# Search for HttpClient calls (.get(, .post() or http)
http_calls = re.findall(r'\.get\([^\)]+\)|\.post\([^\)]+\)', content)
print("HTTP calls in chunk-QSWTPHHH.js:")
for h in set(http_calls):
    print("  ", h)

# Search for strings starting with / or http
urls = re.findall(r'[\'\"`](https?://[^\'\"`]+|/[a-zA-Z0-9_\-\./]+)[\'\"`]', content)
print("\nURLs in chunk-QSWTPHHH.js:")
for u in set(urls):
    if len(u) < 100:
        print("  ", u)
