#!/usr/bin/env python3
"""Podklady REO HEATING pro projektanty a partnery — stránka ke stažení dokumentů (artefakt).

Použití (z kořene repozitáře):
    python3 podklady-partneri/build.py <výstupní_složka>

Do výstupní složky zkopíruje všechny PDF (soubory/…) a vygeneruje index.html.
ZIP datových listů / štítků skládá až prohlížeč (JSZip) — artefakt .zip soubory neservíruje. Složka se pak publikuje jako artefakt
(index.html + soubory/*). PDF se do gitu nekopírují — zdroje jsou v projektech níže.
"""
import base64, html, os, shutil, sys, zipfile
from datetime import date

import fitz  # PyMuPDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Projekty/
REO = os.path.join(ROOT, 'REO')
SMART = os.path.join(REO, 'PW Helios', 'REO R290 Smart')
DL = os.path.join(REO, 'R290-datove-listy', 'pdf')
STITKY = os.path.join(SMART, 'registrace', 'A_REO-HEATING', 'energeticke-stitky')
POKYNY = os.path.join(ROOT, 'reo-schemata-zapojeni', 'pokyny')
CENIK = os.path.join(SMART, 'cenik', 'cenik.pdf')

MODELY = ['RH06-1F', 'RH08-3F', 'RH10-3F', 'RH12-3F', 'RH14-3F', 'RH16-3F', 'RHX20-Pro', 'RHX30-Pro']
NAZEV = {m: m.replace('-1F', ' 1F').replace('-3F', ' 3F').replace('-Pro', ' Pro') for m in MODELY}

# (sekce, název, popis, zdroj, publikovaný název souboru)
DOCS = [
    ('cenik', 'Ceník REO R290 Smart a RHX Pro',
     'Ceny tepelných čerpadel 6–40 kW a nerezových zásobníků REO v Kč bez DPH, u každého modelu výkon, SCOP a hluk.',
     CENIK, 'REO-HEATING_Cenik_R290-Smart-RHX-Pro.pdf'),
    ('tc', 'Katalog REO R290 Smart',
     'Přehled řady: topí přímo ze sluníčka, SCOP až 5,29, kompresor Mitsubishi Electric, modelová řada, zásobníky.',
     os.path.join(SMART, 'katalog', 'REO-R290-Smart_katalog.pdf'), 'REO-R290-Smart_katalog.pdf'),
    ('tc', 'Technický list pro projektanty a partnery',
     'Parametry všech modelů, limity FV vstupu (MPPT), výbava jednotky, regulace, SG Ready, Modbus, kaskáda.',
     os.path.join(SMART, 'letaky', 'REO-R290-Smart_letak-partneri.pdf'), 'REO-R290-Smart_technicky-list.pdf'),
    ('tc', 'Technická prezentace Smart a RHX Pro',
     'Výbava, odhlučnění, ochrana R290, SG Ready / PV Ready, kaskády, ovladač, Modbus/BMS, zapojení přídavného zdroje a ventilů.',
     os.path.join(SMART, 'prezentace-komercni', 'REO-R290-Smart_RHX20-RHX30-Pro_prezentace-CZ.pdf'),
     'REO-R290-Smart-RHX-Pro_prezentace.pdf'),
    ('tc', 'Instalační a provozní návod CZ',
     'Rozměry, hydraulická a elektrická schémata, připojení FV, parametry regulace, chybové kódy.',
     os.path.join(SMART, 'REO-R290-Smart_navod-CZ.pdf'), 'REO-R290-Smart_navod-CZ.pdf'),
    ('nadrze', 'Katalog nerezových nádrží REO',
     'Akumulační nádrže, zásobníky TV, kombinované 2 v 1 a solární; objemy 30–1 000 l, zakázkové provedení.',
     os.path.join(REO, 'REO-letak-nadrze', 'REO_HEATING_Katalog_nadrzi.pdf'), 'REO-HEATING_Katalog-nadrzi.pdf'),
    ('pokyny', 'Vytápění s AKU nádrží a ohřev TUV',
     'Schéma zapojení, osazení venkovní jednotky, armatury, pojistná výbava, uvedení do provozu.',
     os.path.join(POKYNY, 'REO-pokyny-instalace-V2-AKU-TUV.pdf'), 'REO-pokyny-instalace_AKU-TUV.pdf'),
    ('pokyny', 'Varianta s hydroboxem, AKU nádrží a ohřevem TUV',
     'Totéž zapojení s vnitřním hydroboxem REO v technické místnosti.',
     os.path.join(POKYNY, 'REO-pokyny-instalace-H2-hydrobox-AKU-TUV.pdf'), 'REO-pokyny-instalace_hydrobox-AKU-TUV.pdf'),
]
for m in MODELY:
    DOCS.append(('dl', NAZEV[m], 'Výkon, příkon a COP', os.path.join(DL, f'{m}_Heating_REO-HEATING.pdf'),
                 f'datove-listy/{m}_datovy-list.pdf'))
for m in MODELY:
    DOCS.append(('stitky', NAZEV[m], 'Energetický štítek ErP', os.path.join(STITKY, f'{m}_energeticky-stitek.pdf'),
                 f'energeticke-stitky/{m}_energeticky-stitek.pdf'))

ZIPS = {'dl': ('REO-R290-Smart_datove-listy.zip', 'Všechny datové listy (ZIP)'),
        'stitky': ('REO-R290-Smart_energeticke-stitky.zip', 'Všechny štítky (ZIP)')}

ZAKAZANE = ['power world', 'powerworld', 'helios', 'dkxlre', 'wk-', 'wk1', 'wk2', 'wk3', 'wk5']


def velikost(b):
    return f'{b / 1048576:.1f} MB'.replace('.', ',') if b >= 1048576 else f'{round(b / 1024)} kB'


def main(out):
    soub = os.path.join(out, 'soubory')
    if os.path.isdir(soub):
        shutil.rmtree(soub)
    os.makedirs(soub)
    info = []
    for sek, nazev, popis, src, pub in DOCS:
        dst = os.path.join(soub, pub)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        d = fitz.open(dst)
        text = (''.join(p.get_text() for p in d) + str(d.metadata)).lower()
        bad = [z for z in ZAKAZANE if z in text]
        if bad:
            sys.exit(f'STOP: {pub} obsahuje odkaz na výrobce: {bad}')
        info.append(dict(sek=sek, nazev=nazev, popis=popis, pub='soubory/' + pub,
                         stran=len(d), vel=os.path.getsize(dst)))
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(stranka(info, out))
    print(len(info), 'dokumentů;', 'celkem', velikost(sum(os.path.getsize(os.path.join(dp, f))
          for dp, _, fs in os.walk(soub) for f in fs)))


def logo(nazev):
    p = os.path.join(REO, 'logo', nazev)
    return 'data:image/svg+xml;base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def tlacitko(pub, text='Stáhnout PDF'):
    return f'<button type="button" class="dl" data-file="{pub}">{text}</button>'


def karta(i):
    meta = f'PDF · {i["stran"]} {"strana" if i["stran"] == 1 else "strany" if i["stran"] < 5 else "stran"} · {velikost(i["vel"])}'
    return f'''<article class="doc">
  <div class="doc-t"><h3>{html.escape(i["nazev"])}</h3><p>{html.escape(i["popis"])}</p></div>
  <div class="doc-a"><span class="meta">{meta}</span>{tlacitko(i["pub"])}</div>
</article>'''


def mrizka(info, sek, out):
    zname, ztext = ZIPS[sek]
    zsize = velikost(sum(i['vel'] for i in info if i['sek'] == sek))
    polozky = ''.join(
        f'<li data-sek="{sek}" data-file="{i["pub"]}"><span class="m">{html.escape(i["nazev"])}</span><span class="meta">{i["stran"]} str. · {velikost(i["vel"])}</span>'
        f'{tlacitko(i["pub"], "PDF")}</li>' for i in info if i['sek'] == sek)
    return f'<ul class="mini">{polozky}</ul><div class="zip"><button type="button" class="dl" data-zip="{sek}" data-name="{zname}">{ztext}</button><span class="meta">ZIP · cca {zsize}</span></div>'


def stranka(info, out):
    sek = lambda s: ''.join(karta(i) for i in info if i['sek'] == s)
    dnes = date.today()
    return f'''<title>Podklady REO HEATING</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap">
<style>
/* Layout: knihovna podkladů — úzký sloupec, sekce podle toho, co projektant hledá (cena → TČ → listy → nádrže → instalace) */
:root{{
  --bg:#FFFFFF; --soft:#F5FBF7; --tint:#E9F6EE; --line:#D9E8DE;
  --ink:#16231B; --body:#4A5A50; --muted:#6F7F75;
  --brand:#34A263; --brand-ink:#1E6A3D; --btn:#26804B; --btn-ink:#FFFFFF;
  --display:"Space Grotesk","Inter","Helvetica Neue",Arial,sans-serif;
  --text:"Inter","Helvetica Neue",Arial,sans-serif;
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{
  --bg:#101713; --soft:#141E18; --tint:#17281E; --line:#26382D;
  --ink:#E8F1EB; --body:#B5C4BA; --muted:#8C9C92;
  --brand:#4CBC7A; --brand-ink:#7FD3A2; --btn:#34A263; --btn-ink:#FFFFFF; color-scheme:dark }} }}
:root[data-theme="dark"]{{
  --bg:#101713; --soft:#141E18; --tint:#17281E; --line:#26382D;
  --ink:#E8F1EB; --body:#B5C4BA; --muted:#8C9C92;
  --brand:#4CBC7A; --brand-ink:#7FD3A2; --btn:#34A263; --btn-ink:#FFFFFF; color-scheme:dark }}
body{{ background:var(--bg); color:var(--ink); font-family:var(--text); font-size:15.5px; line-height:1.55; -webkit-font-smoothing:antialiased }}
.wrap{{ max-width:980px; margin:0 auto; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)) }}
h1,h2,h3{{ font-family:var(--display); text-wrap:balance; margin:0 }}
p{{ margin:0 }}
.logo-d{{ display:none }}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]) .logo-l{{display:none}} :root:not([data-theme="light"]) .logo-d{{display:block}} }}
:root[data-theme="dark"] .logo-l{{display:none}} :root[data-theme="dark"] .logo-d{{display:block}}

header{{ padding-block:36px 28px; border-bottom:1px solid var(--line) }}
header .top{{ display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap }}
header img{{ height:52px; width:auto }}
.kicker{{ font-size:12px; letter-spacing:.16em; text-transform:uppercase; font-weight:700; color:var(--brand-ink) }}
h1{{ font-size:clamp(28px,4.4vw,40px); line-height:1.1; margin-top:22px; letter-spacing:-.01em }}
.lead{{ color:var(--body); max-width:66ch; margin-top:12px; font-size:16.5px }}
.facts{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:10px; margin-top:24px }}
.fact{{ background:var(--tint); border-radius:10px; padding:12px 14px }}
.fact b{{ display:block; font-family:var(--display); font-size:20px; color:var(--brand-ink); font-variant-numeric:tabular-nums }}
.fact span{{ font-size:13px; color:var(--body) }}

nav.toc{{ display:flex; flex-wrap:wrap; gap:8px; padding-block:18px }}
nav.toc a{{ font-size:13.5px; font-weight:600; color:var(--brand-ink); text-decoration:none; border:1px solid var(--line); border-radius:999px; padding:5px 12px }}
nav.toc a:hover{{ background:var(--tint) }}

section{{ padding-block:26px; border-top:1px solid var(--line) }}
section h2{{ font-size:22px; color:var(--ink) }}
section .sub{{ color:var(--muted); font-size:14px; margin-top:4px; max-width:70ch }}
.docs{{ display:flex; flex-direction:column; gap:10px; margin-top:16px }}
.doc{{ display:flex; gap:16px; align-items:center; justify-content:space-between; border:1px solid var(--line); border-radius:10px; padding:14px 16px; background:var(--bg) }}
.doc-t{{ min-width:0 }}
.doc h3{{ font-size:16.5px; font-weight:600 }}
.doc p{{ color:var(--body); font-size:14px; margin-top:3px }}
.doc-a{{ display:flex; align-items:center; gap:12px; flex:none }}
.meta{{ font-size:12.5px; color:var(--muted); white-space:nowrap; font-variant-numeric:tabular-nums }}
@media (max-width:620px){{ .doc{{ flex-direction:column; align-items:flex-start }} .doc-a{{ width:100%; justify-content:space-between }} }}

button.dl{{ font:600 14px var(--text); background:var(--btn); color:var(--btn-ink); border:0; border-radius:8px; padding:9px 16px; cursor:pointer; white-space:nowrap }}
button.dl:hover{{ filter:brightness(1.08) }}
button.dl:focus-visible{{ outline:2px solid var(--brand); outline-offset:2px }}
button.dl[aria-busy="true"]{{ opacity:.6; cursor:progress }}
button.dl:disabled{{ background:var(--line); color:var(--muted); cursor:not-allowed }}

.cols{{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:22px; margin-top:16px }}
@media (max-width:760px){{ .cols{{ grid-template-columns:1fr }} }}
.cols h3{{ font-size:15px; font-weight:600; margin-bottom:8px }}
ul.mini{{ list-style:none; margin:0; padding:0; border:1px solid var(--line); border-radius:10px; overflow:hidden }}
ul.mini li[data-sek]{{}}
ul.mini li{{ display:flex; align-items:center; gap:10px; padding:8px 12px; border-top:1px solid var(--line) }}
ul.mini li:first-child{{ border-top:0 }}
ul.mini li:nth-child(even){{ background:var(--soft) }}
ul.mini .m{{ font-weight:600; flex:1; min-width:0 }}
ul.mini button.dl{{ padding:6px 12px; font-size:13px }}
.zip{{ display:flex; align-items:center; gap:12px; margin-top:10px }}
.zip button.dl{{ background:transparent; color:var(--brand-ink); border:1.5px solid var(--brand) }}

.note{{ margin-top:14px; font-size:13.5px; color:var(--body); border-left:3px solid var(--brand); padding-left:12px; max-width:75ch }}
#stav{{ position:fixed; left:50%; transform:translateX(-50%); bottom:calc(16px + env(safe-area-inset-bottom,0px)); background:var(--ink); color:var(--bg); font-size:14px; padding:10px 16px; border-radius:8px; max-width:calc(100% - 32px) }}
#nedostupne{{ background:var(--tint); border-radius:10px; padding:12px 16px; margin-top:16px; font-size:14.5px }}

footer{{ border-top:1px solid var(--line); padding-block:26px 40px; color:var(--body); font-size:14px }}
footer .k{{ display:flex; flex-wrap:wrap; gap:8px 28px; margin-top:10px }}
footer .k span{{ display:block; font-size:11.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); font-weight:700 }}
footer .k b{{ font-weight:600; color:var(--ink); user-select:all }}
footer .fine{{ margin-top:18px; font-size:12.5px; color:var(--muted); max-width:90ch }}
@media (prefers-reduced-motion:reduce){{ *{{ transition:none!important }} }}
</style>

<div class="wrap">
<header>
  <div class="top">
    <img class="logo-l" src="{logo('logo-reo-heating.svg')}" alt="REO HEATING">
    <img class="logo-d" src="{logo('logo-reo-heating-white.svg')}" alt="REO HEATING">
    <span class="kicker">Pro projektanty a partnery</span>
  </div>
  <h1>Podklady k tepelným čerpadlům REO R290 Smart a RHX Pro</h1>
  <p class="lead">Ceník, katalogy, datové listy, energetické štítky, nádrže a pokyny k instalaci na jednom místě.
  Monobloky vzduch–voda s přírodním chladivem R290 pro rodinné domy (6–16 kW) i bytové domy a provozovny (RHX Pro 20/30 kW, kaskáda až 8 jednotek).</p>
  <div class="facts">
    <div class="fact"><b>FV bez střídače</b><span>panely přímo do kompresoru přes desku MPPT</span></div>
    <div class="fact"><b>SCOP až 5,29</b><span>A+++ pro 35 i 55 °C (EN 14825)</span></div>
    <div class="fact"><b>Mitsubishi Electric</b><span>invertorový kompresor v celé řadě</span></div>
    <div class="fact"><b>75 °C · −25 °C</b><span>výstupní voda · spodní mez provozu</span></div>
  </div>
  <div id="nedostupne" hidden>V tomto zobrazení nelze soubory stahovat. Otevřete stránku přihlášení v claude.ai, nebo si podklady vyžádejte na <b>info@reoheating.cz</b>.</div>
</header>

<nav class="toc" aria-label="Sekce">
  <a href="#cenik">Ceník</a><a href="#tc">Tepelná čerpadla</a><a href="#listy">Datové listy a štítky</a><a href="#nadrze">Nádrže</a><a href="#pokyny">Pokyny k instalaci</a><a href="#kontakt">Kontakt</a>
</nav>

<section id="cenik">
  <h2>Ceník</h2>
  <p class="sub">Ceny za zařízení bez montáže v Kč bez DPH, platné od 11/2026. Podmínky pro partnery na vyžádání.</p>
  <div class="docs">{sek('cenik')}</div>
</section>

<section id="tc">
  <h2>Tepelná čerpadla REO R290 Smart a RHX Pro</h2>
  <p class="sub">Od přehledového katalogu po instalační návod se schématy pro projekt.</p>
  <div class="docs">{sek('tc')}</div>
</section>

<section id="listy">
  <h2>Datové listy a energetické štítky</h2>
  <p class="sub">Datové listy: výkon, příkon a COP pro výstupní vodu 35–55 °C a venkovní teploty −25 až +21 °C, u RHX Pro i 60–75 °C. Štítky ErP podle nařízení EU 811/2013.</p>
  <div class="cols">
    <div><h3>Datové listy</h3>{mrizka(info, 'dl', out)}</div>
    <div><h3>Energetické štítky ErP</h3>{mrizka(info, 'stitky', out)}</div>
  </div>
</section>

<section id="nadrze">
  <h2>Nerezové nádrže REO</h2>
  <p class="sub">Akumulace, zásobníky TV a kombinované nádrže k tepelným čerpadlům, nerez SUS 304.</p>
  <div class="docs">{sek('nadrze')}</div>
</section>

<section id="pokyny">
  <h2>Pokyny k instalaci</h2>
  <p class="sub">Ověřená zapojení s akumulační nádrží 100 l a zásobníkem TUV, krok za krokem s číslovanými schématy.</p>
  <div class="docs">{sek('pokyny')}</div>
  <p class="note">Pokyny vycházejí z realizací s jednotkami REO R290 RH030–RH060. Hydraulický princip (AKU, trojcestný ventil TUV, pojistná výbava) platí i pro REO R290 Smart; parametry regulace a připojení se řídí instalačním návodem Smart.</p>
</section>

<footer id="kontakt">
  <h2 style="font-size:20px">Pomůžeme s návrhem</h2>
  <p style="margin-top:6px;max-width:70ch">Navrhneme výkon nebo kaskádu, dimenzování FV stringu a hydraulické zapojení ke konkrétnímu projektu. Certifikáty KEYMARK a další dokumentaci doložíme na vyžádání.</p>
  <div class="k">
    <div><span>E-mail</span><b>info@reoheating.cz</b></div>
    <div><span>Telefon</span><b>+420 774 872 467</b></div>
    <div><span>Showroom</span><b>Smetanova 555, 739 61 Třinec</b></div>
    <div><span>Web</span><b><a href="https://reoheating.cz" target="_blank" rel="noopener" style="color:inherit">reoheating.cz</a></b></div>
  </div>
  <p class="fine">Údaje podle technické specifikace výrobce: COP podle EN 14511, SCOP a energetická třída podle EN 14825 (průměrné klima). Přímé napájení z FV vyžaduje volitelnou desku MPPT. Změny vyhrazeny. REO HEATING · Riva Trade s.r.o., IČ 08864811 · aktualizováno {dnes.day}. {dnes.month}. {dnes.year}</p>
</footer>
</div>
<div id="stav" role="status" hidden></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script>
(function(){{
  var stav = document.getElementById('stav'), t;
  function hlaska(s){{ stav.textContent = s; stav.hidden = false; clearTimeout(t); t = setTimeout(function(){{ stav.hidden = true; }}, 4000); }}
  var tlacitka = document.querySelectorAll('button.dl');
  function nedostupne(){{
    document.getElementById('nedostupne').hidden = false;
    tlacitka.forEach(function(b){{ b.disabled = true; b.title = 'Stahování není v tomto zobrazení dostupné'; }});
  }}
  if (!window.claude || !window.claude.use) {{ nedostupne(); return; }}
  window.claude.use('downloads').then(function(dl){{
    if (!dl) {{ nedostupne(); return; }}
    tlacitka.forEach(function(b){{
      b.addEventListener('click', function(){{
        if (b.getAttribute('aria-busy') === 'true') return;
        var f = b.getAttribute('data-file'), zsek = b.getAttribute('data-zip');
        function nacti(u){{ return fetch(u).then(function(r){{ if (!r.ok) throw {{code:'fetch'}}; return r.blob(); }}); }}
        var priprava;
        if (zsek) {{
          if (!window.JSZip) {{ hlaska('ZIP nelze vytvořit. Stáhněte soubory jednotlivě.'); return; }}
          var polozky = Array.prototype.map.call(document.querySelectorAll('li[data-sek="' + zsek + '"]'), function(li){{ return li.getAttribute('data-file'); }});
          var zip = new JSZip();
          priprava = Promise.all(polozky.map(function(u){{ return nacti(u).then(function(bl){{ zip.file(u.split('/').pop(), bl); }}); }}))
            .then(function(){{ return zip.generateAsync({{type:'blob'}}); }})
            .then(function(blob){{ return {{name: b.getAttribute('data-name'), blob: blob}}; }});
        }} else {{
          priprava = nacti(f).then(function(blob){{ return {{name: f.split('/').pop(), blob: blob}}; }});
        }}
        b.setAttribute('aria-busy','true');
        priprava
          .then(function(x){{ return dl.save({{filename: x.name, data: x.blob}}); }})
          .then(function(){{ hlaska('Soubor uložen.'); }})
          .catch(function(e){{
            var c = e && e.code;
            if (c === 'declined') return;
            if (c === 'rate_limited') {{ hlaska('Počkejte na předchozí stažení a zkuste to znovu.'); return; }}
            if (c === 'fetch') {{ hlaska('Soubor se nepodařilo načíst. Zkuste stránku obnovit.'); return; }}
            nedostupne();
          }})
          .then(function(){{ b.removeAttribute('aria-busy'); }});
      }});
    }});
  }});
}})();
</script>
'''


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(os.path.abspath(sys.argv[1]))
