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

headers = {'User-Agent': 'Mozilla/5.0'}

for chunk in chunks:
    try:
        url = base_url + chunk
        req = urllib.request.Request(url, headers=headers)
        content = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        # Find urls or endpoints
        endpoints = re.findall(r'https?://[^\s"\'`]+|/[a-zA-Z0-9_\-\./]+compras[a-zA-Z0-9_\-\./]*', content)
        filtered = [e for e in endpoints if 'compras' in e or 'acompanhamento' in e or 'fase' in e]
        if filtered:
            print(f"--- {chunk} ---")
            for f in set(filtered):
                if len(f) < 120:
                    print(f)
    except Exception as e:
        print(chunk, e)
