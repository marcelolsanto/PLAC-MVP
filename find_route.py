import urllib.request
import re

base_url = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/"
chunks = [
    "main-ASI6JQ73.js",
    "chunk-YXPFDLL2.js",
    "chunk-OQXCLFSG.js",
    "chunk-BXG5DYID.js",
    "chunk-BMYEID36.js",
    "chunk-EDTSXHGU.js",
    "chunk-ABDG4XZY.js",
    "chunk-Y6NI6Z7N.js",
    "chunk-45KLBJCN.js",
    "chunk-H5JFCYGZ.js"
]

for chunk in chunks:
    try:
        url = base_url + chunk
        content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
        if 'acompanhamento-compra' in content or 'acompanhamento' in content:
            print(f"FOUND IN {chunk}!")
            for m in re.finditer(r'.{0,70}acompanhamento.{0,70}', content):
                print("  -->", m.group(0))
    except Exception as e:
        pass
