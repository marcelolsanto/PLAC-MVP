import urllib.request
import re

base = 'https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/'
html = urllib.request.urlopen(base).read().decode()
scripts = re.findall(r'href="(/comprasnet-web/[^"]+\.js)"|src="(/comprasnet-web/[^"]+\.js)"', html)
js_files = [s[0] or s[1] for s in scripts]
print('JS files:', js_files)

for js in js_files:
    content = urllib.request.urlopen('https://cnetmobile.estaleiro.serpro.gov.br' + js).read().decode(errors='ignore')
    if 'acompanhamento-compra' in content:
        print('Found acompanhamento-compra in:', js)
        for m in re.finditer(r'.{0,100}acompanhamento-compra.{0,100}', content):
            print('   -->', m.group(0))
