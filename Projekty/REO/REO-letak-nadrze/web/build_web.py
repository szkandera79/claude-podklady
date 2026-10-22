import re, base64, io, sys
from PIL import Image
SRC = sys.argv[1]; OUT = sys.argv[2]
import os
os.chdir(SRC)
s = open('letak.html', encoding='utf-8').read()
body = s[s.find('<body>')+6 : s.find('</body>')]

cache = {}
def img_uri(path):
    if path in cache: return cache[path]
    if path.endswith('.svg'):
        uri = 'data:image/svg+xml;base64,' + base64.b64encode(open(path,'rb').read()).decode()
    else:
        im = Image.open(path).convert('RGB')
        h = 760
        if im.height > h: im = im.resize((round(im.width*h/im.height), h), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=84, optimize=True, progressive=True)
        uri = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    cache[path] = uri; return uri

body = re.sub(r'src="([^"]+)"', lambda m: f'src="{img_uri(m.group(1))}" loading="lazy"', body)
body = re.sub(r'\s+style="[^"]*"', '', body)
body = re.sub(r'<div class="foot">.*?</div>\s*', '', body)  # tiskové patičky
body = body.replace('<div class="spacer"></div>', '')
body = body.replace('<div class="strip"></div>', '')
# tabulky parametrů do scroll kontejneru
body = re.sub(r'(<table>.*?</table>)', r'<div class="tw">\1</div>', body, flags=re.S)
# kotvy sekcí
ids = ['uvod','prehled','an','zv','zh','zd','kn','zs','zakazka','kontakt']
it = iter(ids)
body = re.sub(r'<section class="page( [a-z]+)?">', lambda m: f'<section class="page{m.group(1) or ""}" id="{next(it)}">', body)
body = body.replace('class="tblhead">Proti dvěma', 'class="tblhead gap">Proti dvěma').replace('class="tblhead">Jak postupovat','class="tblhead gap">Jak postupovat')
body = body.replace('<div class="cta">Chci nezávaznou nabídku</div>', '<a class="cta" href="https://reoheating.cz" target="_blank" rel="noopener">Chci nezávaznou nabídku</a>')

nav = '''<nav class="nav" aria-label="Typy nádrží"><div class="in">
<a class="brand" href="#uvod"><img src="%s" alt="REO HEATING"></a>
<div class="links"><a href="#an">AN</a><a href="#zv">ZV</a><a href="#zh">ZH</a><a href="#zd">ZD</a><a href="#kn">KN</a><a href="#zs">ZS</a><a href="#zakazka">Na míru</a><a href="#kontakt" class="k">Kontakt</a></div>
</div></nav>''' % img_uri('logo-reo-heating.svg')

css = open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'web.css'), encoding='utf-8').read()
html = f'''<title>Katalog nádrží REO HEATING</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800&display=swap">
<style>
{css}
</style>
{nav}
<main>
{body}
</main>
'''
open(OUT,'w',encoding='utf-8').write(html)
print(len(html)//1024, 'KB')
