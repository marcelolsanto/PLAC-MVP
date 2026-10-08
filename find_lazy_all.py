import urllib.request
import re

url = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/main-ASI6JQ73.js'
content = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')

# Match chunk-*.js
chunks = set(re.findall(r'chunk-[A-Za-z0-9_-]+\.js', content))
print("Found chunks in main:", len(chunks))

for c in chunks:
    try:
        c_url = f"https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/{c}"
        c_text = urllib.request.urlopen(urllib.request.Request(c_url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode(errors='ignore')
        if 'acompanhamento' in c_text:
            print(f"MATCH in {c}!")
            matches = re.findall(r'.{0,60}acompanhamento.{0,60}', c_text)
            for m in matches[:5]:
                print("   ", m)
            # Look for api endpoints in this chunk
            api_calls = re.findall(r'[\'\"`](https?://[^\'\"`]+|/[a-zA-Z0-9_/-]+(?:compra|fase|item|evento)[a-zA-Z0-9_/-]*)[\'\"`]', c_text)
            print("    APIs in this chunk:", set(api_calls))
    except Exception as e:
        print("ERR in chunk", c, e)
