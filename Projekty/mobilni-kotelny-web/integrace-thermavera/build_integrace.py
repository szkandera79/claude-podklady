#!/usr/bin/env python3
"""Varianta 2: služba mobilních kotelen jako součást webu thermavera.cz.

Zdrojem obsahu je samostatný web mobilni-kotelny-web (texty, kalkulačka, obrázky); skript ho zabalí
do hlavičky a patičky ThermaVera a upraví homepage ThermaVera (menu, hero, karta, patička, TR překlady,
vizualizace v hero se štítkem, sitemap).

Použití (z kořene repozitáře):
  python3 mobilni-kotelny-web/integrace-thermavera/build_integrace.py --apply
      zapíše do thermavera-web/: podsložku mobilni-kotelny/ (vždy přegeneruje) a jednorázově upraví
      index.html a sitemap.xml (podruhé je přeskočí). Po změně obsahu webu služby stačí spustit znovu.
  python3 mobilni-kotelny-web/integrace-thermavera/build_integrace.py <výstupní složka>
      náhled: kopie thermavera-web s integrací, zdroje se nemění.
"""
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TV = ROOT / 'thermavera-web'
MK = ROOT / 'mobilni-kotelny-web'
SUB = 'mobilni-kotelny'

HERO_VIZ = ['strojirensky-zavod', 'hotel', 'logisticky-sklad', 'potravinarsky-zavod', 'strecha-hala', 'strecha-panelak']
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def replace_once(s, old, new, what):
    if s.count(old) != 1:
        sys.exit(f'Nenalezeno jednoznačně ({what}): {old[:70]}…')
    return s.replace(old, new)


# ---------- 1) homepage ThermaVera ----------
def patch_homepage(s):
    # hero: druhá výzva vedle ETS2 lišty (ta už na webu je) → odkaz pod tlačítky v hero
    s = replace_once(s, '<a href="#financovani" class="btn btn-outline">Prověřit řešení bez investice</a>',
        '<a href="#financovani" class="btn btn-outline">Prověřit řešení bez investice</a>'
        f'\n        <a href="{SUB}/" class="btn btn-outline">Pronájem mobilní kotelny</a>', 'hero')
    # položka menu
    s = replace_once(s, '<a class="link" href="#reseni">Řešení</a>',
        f'<a class="link" href="#reseni">Řešení</a>\n      <a class="link" href="{SUB}/">Mobilní kotelny</a>', 'menu')
    # karta „Mobilní kotelna“ v Naše řešení → podstránka
    i = s.index('<h3>Mobilní kotelna</h3>')
    j = s.index('<a href="#kontakt" class="arrowlink">Více informací', i)
    s = s[:j] + f'<a href="{SUB}/" class="arrowlink">Pronájem mobilní kotelny' + s[j + len('<a href="#kontakt" class="arrowlink">Více informací'):]
    k = s.index('</ul>', i)
    s = s[:k] + '  <li><svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>Pronájem i s tepelným čerpadlem</li>\n          ' + s[k:]
    # patička
    s = replace_once(s, '<a href="#financovani">Modely spolupráce</a>',
        f'<a href="#financovani">Modely spolupráce</a>\n        <a href="{SUB}/">Pronájem mobilní kotelny</a>', 'patička')
    # překlady nových textů (pravidlo i18n webu ThermaVera)
    tr = '''
  "Mobilní kotelny":["Mobile boiler rooms","Mobile Heizzentralen","Mobilne kotłownie"],
  "Pronájem i s tepelným čerpadlem":["Rental also with a heat pump","Miete auch mit Wärmepumpe","Wynajem także z pompą ciepła"],
  "Pronájem mobilní kotelny":["Mobile boiler room rental","Mobile Heizzentrale mieten","Wynajem mobilnej kotłowni"],
  "Vizualizace":["Visualisation","Visualisierung","Wizualizacja"],'''
    s = replace_once(s, '  const TR={', '  const TR={' + tr, 'TR')
    # hero: vizualizace mobilních kotelen mezi fotkami realizací + štítek „Vizualizace“
    viz = ''.join(f'\n    <div class="hero-slide" data-viz style="background-image:url(\'{SUB}/assets/img/hero-{n}.jpg\')"></div>' for n in HERO_VIZ)
    last = '<div class="hero-slide" style="background-image:url(\'assets/images/reference/r-arnhall-1.jpg\')"></div>'
    s = replace_once(s, last, last + viz, 'hero slides')
    s = replace_once(s, '  <div class="wrap hero-content">', '  <span class="hero-viz" id="heroViz">Vizualizace</span>\n  <div class="wrap hero-content">', 'hero badge')
    s = replace_once(s, '  .hero-slides{position:absolute;inset:0;z-index:0}',
        '  .hero-slides{position:absolute;inset:0;z-index:0}\n  .hero-viz{position:absolute;right:16px;bottom:14px;z-index:3;display:none;font-size:.74rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;background:rgba(0,0,0,.45);color:#fff;padding:4px 10px;border-radius:999px}\n  .hero-viz.show{display:block}', 'hero css')
    s = replace_once(s, '</body>', """<script>
/* Štítek „Vizualizace“ u snímků mobilních kotelen v hero (nejsou to realizace) */
(function(){
  var badge=document.getElementById('heroViz');
  var slides=[].slice.call(document.querySelectorAll('.hero-slide'));
  function upd(){var a=document.querySelector('.hero-slide.active');badge.classList.toggle('show',!!(a&&a.hasAttribute('data-viz')));}
  var mo=new MutationObserver(upd);slides.forEach(function(s){mo.observe(s,{attributes:true,attributeFilter:['class']});});upd();
})();
</script>
</body>""", 'body')
    return s


# ---------- 2) podstránky služby v rámu ThermaVera ----------
HEADER = f'''<header>
  <div class="nav">
    <a href="../index.html" class="logo" aria-label="ThermaVera Energy — domů">
      <svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><rect x="1" y="1" width="30" height="30" rx="9" fill="#2E6B33"/><path d="M9.8 10.6H21.6L14 23.4" stroke="#FCC83C" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span><span class="b">Therma</span><span class="t">Vera</span> Energy</span>
    </a>
    <nav class="menu" aria-label="Hlavní navigace">
      <a href="../index.html#reseni">Řešení</a>
      <a href="index.html" class="on">Mobilní kotelny</a>
      <a href="../index.html#ekonomika">Ekonomika</a>
      <a href="../index.html#financovani">Financování</a>
      <a href="../index.html#prokoho">Pro koho</a>
      <a href="../index.html#reference">Realizace</a>
      <a href="../index.html#kontakt">Kontakt</a>
    </nav>
    <div class="navright">
      <a class="tel" href="tel:+420774872467">+420 774 872 467</a>
      <a class="btn btn-amber" href="index.html#poptavka">Poptat kotelnu</a>
      <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="subnav" aria-label="Mobilní kotelny">
    <div class="subnav-in">
      <span class="crumb"><a href="../index.html">ThermaVera</a> › Mobilní kotelny</span>
      <a href="index.html" data-p="index">Přehled</a>
      <a href="kalkulacka.html" data-p="kalkulacka">Kalkulačka ceny tepla</a>
      <a href="cena-tepla.html" data-p="cena-tepla">Proč nerozhoduje jen nájem</a>
      <a href="index.html#pronajem">Ceník a odkup</a>
      <a href="index.html#faq">Časté dotazy</a>
    </div>
  </nav>
</header>'''

SUBNAV_CSS = '''<style>
  .subnav{border-top:1px solid var(--line);background:var(--bg-alt)}
  .subnav-in{max-width:1360px;margin:0 auto;padding:0 24px;display:flex;gap:22px;align-items:center;height:44px;overflow-x:auto;white-space:nowrap;font-size:.86rem}
  .subnav a{color:var(--muted);font-weight:500}
  .subnav a.on,.subnav a:hover{color:var(--green);font-weight:600}
  .subnav .crumb{color:var(--muted);font-size:.8rem;margin-right:8px}
  .subnav .crumb a{color:var(--green-bright)}
  html{scroll-padding-top:130px}
</style>
</head>'''

FOOTER = f'''<footer>
  <div class="wrap">
    <div class="cols">
      <div><h4>ThermaVera Energy</h4><p>Zelené kotelny na klíč a pronájem mobilních kotelen s tepelnými čerpadly. Chytrá a hospodárná energetika — teplo levněji, čistěji a nezávisleji.</p></div>
      <div><h4>Mobilní kotelny</h4><ul><li><a href="index.html">Přehled služby</a></li><li><a href="kalkulacka.html">Kalkulačka ceny tepla</a></li><li><a href="cena-tepla.html">Proč nerozhoduje jen nájem</a></li><li><a href="../index.html">Zelené kotelny na klíč</a></li></ul></div>
      <div><h4>Kontakt</h4><ul><li><a href="tel:+420774872467">+420 774 872 467</a></li><li><a href="mailto:info@thermavera.cz">info@thermavera.cz</a></li><li>Riva Trade, s.r.o., IČ: 08864811<br>Korunní 2569/108, 110 00 Praha 10</li><li><a href="../ochrana-udaju.html">Ochrana osobních údajů</a></li></ul></div>
    </div>
    <p class="legal">Uvedené výpočty jsou orientační a nejsou závaznou nabídkou. Nezaručujeme výši úspor. © ThermaVera Energy — Riva Trade, s.r.o.</p>
  </div>
</footer>'''


def frame_subpage(s, page):
    s = re.sub(r'<header>.*?</header>', lambda m: HEADER.replace(f'data-p="{page}"', f'data-p="{page}" class="on"'), s, count=1, flags=re.S)
    s = re.sub(r'<footer>.*?</footer>', lambda m: FOOTER, s, count=1, flags=re.S)
    s = replace_once(s, '</head>', SUBNAV_CSS, f'{page}: head')
    s = s.replace('href="favicon.svg"', 'href="../favicon.svg"')
    s = s.replace('https://thermavera.cz/ochrana-udaju.html', '../ochrana-udaju.html')
    s = s.replace('<form id="poptavka-form" novalidate>', '<form id="poptavka-form" novalidate data-endpoint="../odeslat.php">')
    s = re.sub(r'\| ThermaVera</title>', '| ThermaVera Energy</title>', s)
    return s


def build_sub(dest):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(MK / 'assets', dest / 'assets')
    for page in ('index', 'kalkulacka', 'cena-tepla'):
        html = (MK / f'{page}.html').read_text(encoding='utf-8')
        (dest / f'{page}.html').write_text(frame_subpage(html, page), encoding='utf-8')


def patch_sitemap(s):
    urls = ''.join(f"""  <url>
    <loc>https://thermavera.cz/{SUB}/{p}</loc>
    <lastmod>{date.today()}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{prio}</priority>
  </url>
""" for p, prio in (('', '0.9'), ('kalkulacka.html', '0.7'), ('cena-tepla.html', '0.6')))
    return replace_once(s, '</urlset>', urls + '</urlset>', 'sitemap')


def main():
    if not sys.argv[1:]:
        sys.exit(__doc__)
    if sys.argv[1] == '--apply':
        home = (TV / 'index.html').read_text(encoding='utf-8')
        if f'href="{SUB}/"' in home:
            print('index.html už integraci obsahuje, přeskakuji')
        else:
            (TV / 'index.html').write_text(patch_homepage(home), encoding='utf-8')
            sm = TV / 'sitemap.xml'
            sm.write_text(patch_sitemap(sm.read_text(encoding='utf-8')), encoding='utf-8')
        build_sub(TV / SUB)
        print('Zapsáno do', TV)
        return
    out = Path(sys.argv[1])
    if out.exists():
        shutil.rmtree(out)
    top = {'dist', 'reference', 'thermavera-web-dist', 'CLAUDE.md', 'README.md', SUB}   # jen v kořeni webu
    shutil.copytree(TV, out, ignore=lambda d, names: [n for n in names if (Path(d) == TV and n in top) or n.endswith('.zip')])
    home = (TV / 'index.html').read_text(encoding='utf-8')
    if f'href="{SUB}/"' not in home:
        home = patch_homepage(home)
    (out / 'index.html').write_text(home, encoding='utf-8')
    build_sub(out / SUB)
    print('Náhled integrace:', out)


if __name__ == '__main__':
    main()
