#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pokyny k instalaci REO RH030–RH060 — schválená schémata zapojení, 2 varianty.

Varianta 1: vytápění s AKU 100 l (REO-SCH-K1, K1-E, K1-P)
Varianta 2: vytápění s AKU 100 l + ohřev TUV (REO-SCH-K2, K2-E, K1-P)

Vytváří ../pokyny/v1-aku/index.html, ../pokyny/v2-aku-tuv/index.html (stránky pro artefakt,
obrázky vedle nich) a PDF ../pokyny/REO-pokyny-instalace-V1-AKU.pdf a ...-V2-AKU-TUV.pdf.
Před spuštěním vygenerujte schémata (gen_schema_kuncice*.py, gen_patka_kuncice.py) a PNG.
Spuštění:  python3 reo-schemata-zapojeni/src/build_pokyny.py
"""
import html, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from soupis_kuncice import ITEMS, ITEMS_TUV, MATERIALS  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REV = "rev. 1 · 11/2026"
e = html.escape

VARIANTS = {
    "v1-aku": dict(
        tuv=False, pdf="REO-pokyny-instalace-V1-AKU.pdf",
        title="Pokyny k instalaci — vytápění s AKU",
        h1="Vytápění s akumulační nádrží 100 l",
        lead="Tepelné čerpadlo ohřívá topnou vodu v akumulační nádrži 100 l. Z ní ji sekundární oběhové čerpadlo "
             "dodává do radiátorů nebo podlahového topení; čerpadlo spíná bezdrátový pokojový termostat přes přijímač.",
        imgs={"hydraulika.png": "schema-kuncice-aku100.png", "elektro.png": "schema-kuncice-elektro.png",
              "patka.png": "schema-kuncice-patka.png"},
        codes="REO-SCH-K1 · K1-E · K1-P"),
    "v2-aku-tuv": dict(
        tuv=True, pdf="REO-pokyny-instalace-V2-AKU-TUV.pdf",
        title="Pokyny k instalaci — AKU a TUV",
        h1="Vytápění s AKU nádrží 100 l a ohřev TUV",
        lead="Tepelné čerpadlo ohřívá topnou vodu v akumulační nádrži 100 l a přes trojcestný ventil také teplou užitkovou "
             "vodu ve spirálovém zásobníku. TUV má přednost. Topení řídí bezdrátový pokojový termostat přes přijímač "
             "a sekundární oběhové čerpadlo.",
        imgs={"hydraulika.png": "schema-kuncice-tuv.png", "elektro.png": "schema-kuncice-elektro-tuv.png",
              "patka.png": "schema-kuncice-patka.png"},
        codes="REO-SCH-K2 · K2-E · K1-P"),
}

CSS = """
:root { --bg:#F7F9F8; --surface:#FFFFFF; --fg:#1F2624; --muted:#5B6764; --line:#DCE3E0;
  --accent:#26804B; --accent-soft:#E9F6EE; --warn:#A86B05; --warn-soft:#FFF4DA;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif; --body:"Source Sans 3","Segoe UI",Helvetica,Arial,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#141917; --surface:#1C2320; --fg:#E6ECE9;
  --muted:#9DAAA5; --line:#2F3934; --accent:#5CC488; --accent-soft:#1F3328; --warn:#E8B54A; --warn-soft:#3A3020; color-scheme:dark } }
:root[data-theme="dark"] { --bg:#141917; --surface:#1C2320; --fg:#E6ECE9; --muted:#9DAAA5; --line:#2F3934;
  --accent:#5CC488; --accent-soft:#1F3328; --warn:#E8B54A; --warn-soft:#3A3020; color-scheme:dark }
body { background:var(--bg); color:var(--fg); font:16.5px/1.55 var(--body);
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:28px 48px; }
.wrap { max-width:1040px; margin:0 auto; display:grid; gap:40px; }
h1,h2,h3 { font-family:var(--display); line-height:1.15; text-wrap:balance; margin:0; }
h1 { font-size:clamp(26px,4vw,38px); font-weight:800; }
h2 { font-size:24px; font-weight:700; display:flex; gap:12px; align-items:baseline; }
h2 .no { color:var(--accent); font-variant-numeric:tabular-nums; }
h3 { font-size:17px; font-weight:700; }
p { margin:0; max-width:72ch; }
.eyebrow { font:700 12.5px/1 var(--display); letter-spacing:.12em; text-transform:uppercase; color:var(--accent); }
header { display:grid; gap:12px; border-bottom:3px solid var(--accent); padding-bottom:22px; }
.meta { display:flex; flex-wrap:wrap; gap:6px 22px; color:var(--muted); font-size:14.5px; }
.meta b { color:var(--fg); font-weight:600; }
section { display:grid; gap:16px; }
figure { margin:0; }
.sheet { background:#fff; border:1px solid var(--line); border-radius:6px; overflow-x:auto; }
.sheet img { display:block; width:100%; min-width:680px; }
figcaption { color:var(--muted); font-size:13.5px; margin-top:6px; }
ul.list, ol.steps { margin:0; padding-left:22px; display:grid; gap:6px; max-width:80ch; }
.n { display:inline-block; min-width:21px; padding:0 5px; border-radius:11px; background:var(--accent-soft); color:var(--accent);
  font:700 12.5px/21px var(--display); text-align:center; font-variant-numeric:tabular-nums; }
.note { background:var(--warn-soft); border-left:4px solid var(--warn); padding:12px 16px; border-radius:0 4px 4px 0; display:grid; gap:6px; }
.note strong { color:var(--warn); }
.tbl { overflow-x:auto; border:1px solid var(--line); border-radius:6px; background:var(--surface); }
table { border-collapse:collapse; width:100%; min-width:640px; font-size:14.5px; }
th,td { text-align:left; vertical-align:top; padding:7px 12px; border-bottom:1px solid var(--line); }
th { font:700 11.5px/1.3 var(--display); letter-spacing:.08em; text-transform:uppercase; color:var(--muted); background:var(--bg); }
tr:last-child td { border-bottom:0; }
tr.grp td { background:var(--accent-soft); color:var(--accent); font:700 12px/1.3 var(--display); letter-spacing:.06em; text-transform:uppercase; }
td.q { white-space:nowrap; font-variant-numeric:tabular-nums; }
.cols { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px; }
.box { background:var(--accent-soft); border-radius:6px; padding:16px 18px; display:grid; gap:8px; min-width:0; }
footer { color:var(--muted); font-size:13.5px; border-top:1px solid var(--line); padding-top:14px; display:grid; gap:4px; }
@media (max-width:720px) { .cols { grid-template-columns:1fr; } }
@page { size:A4; margin:14mm 12mm; }
@media print {
  :root { --bg:#fff; --surface:#fff; }
  body { padding:0; font-size:11pt; }
  .wrap { max-width:none; gap:22px; }
  .sheet { border:0; overflow:visible; } .sheet img { min-width:0; }
  section.pb { break-before:page; }
  .wrap, section { display:block; }
  .wrap > * + * { margin-top:22px; }
  section > * + * { margin-top:12px; }
  h2, h3 { break-after:avoid; page-break-after:avoid; }
  .cols { display:block; } .cols > .box + .box { margin-top:12px; }
  figure, .note, .box, tr { break-inside:avoid; }
  .tbl { overflow:visible; border:0; } table { min-width:0; font-size:9.5pt; }
}
"""


def items_table(items):
    out = ['<div class="tbl"><table><thead><tr><th>Č.</th><th>Položka</th><th>Počet</th><th>Poznámka</th></tr></thead><tbody>']
    group = None
    for g, n, item, qty, unit, note in items:
        if g != group:
            out.append(f'<tr class="grp"><td colspan="4">{e(g)}</td></tr>')
            group = g
        num = " ".join(f'<span class="n">{e(k.strip())}</span>' for k in n.split(",")) if n != "—" else "—"
        out.append(f'<tr><td>{num}</td><td>{e(item)}</td><td class="q">{e(qty)} {e(unit)}</td><td>{e(note)}</td></tr>')
    out.append('</tbody></table></div>')
    return "\n".join(out)


def materials_table():
    rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in m) + "</tr>" for m in MATERIALS)
    return ('<div class="tbl"><table><thead><tr><th>Materiál</th><th>Spojování</th><th>Vlastnosti</th>'
            f'<th>Primár (orientačně)</th></tr></thead><tbody>{rows}</tbody></table></div>')


def page(v):
    tuv = v["tuv"]
    sec = []
    # 1 — umístění
    sec.append(f'''<section>
  <h2><span class="no">1</span> Umístění venkovní jednotky a betonová patka</h2>
  <ul class="list">
    <li>Jednotka stojí venku na betonové patce ze dvou ramen ze ztraceného bednění a na dvou antivibračních patkách (silentblocích), nad úrovní terénu a sněhu.</li>
    <li>Ramena: šířka 200 mm, délka min. 500 mm, výška min. 300 mm, kolmo ke stěně, osově 700 mm od sebe.</li>
    <li>Odstup ramen od stěny <strong>min. 400 mm, doporučujeme 500 mm</strong>. Návod uvádí na straně sání vzduchu více než 0,5 m, kolem jednotky 1 m volného prostoru, před výfukem a nad jednotkou 2 m.</li>
    <li>Mezi rameny štěrkový podsyp. Dno jednotky slouží jako vana na kondenzát, odtokové otvory musí zůstat volné.</li>
  </ul>
  <figure><div class="sheet"><img src="patka.png" alt="Výkres betonové patky: půdorys a pohled zepředu s kótami."></div>
    <figcaption>REO-SCH-K1-P — betonová patka venkovní jednotky.</figcaption></figure>
  <div class="note"><p><strong>Ochranná zóna R290.</strong> Okna, dveře a sklepní světlíky min. 1 m od půdorysu jednotky, nad horní hranou min. 0,5 m (okno nad jednotkou je přípustné). V zóně nesmí být šachty, vpusti a kanalizace, větrací otvory ani zdroje vznícení (zásuvky, vypínače, svítidla) a ani prohlubně — R290 je těžší než vzduch.</p>
    <p><strong>Doporučení:</strong> na straně výfuku vzduchu min. 3 m k oknům obytných místností, terasám a chodníkům a min. 3 m od sousedního pozemku (hluk, proudění). Pevnou vzdálenost norma neuvádí; ČSN EN 378 a ČSN EN IEC 60335-2-40 ji svěřují výrobci.</p></div>
</section>''')
    # 2 — hydraulika
    tuv_steps = ""
    if tuv:
        tuv_steps = '''
  <h3>Ohřev TUV</h3>
  <ol class="steps">
    <li><strong>Trojcestný ventil <span class="n">18</span></strong> hned za vstupem výstupu z TČ do technické místnosti. Bez napětí vede vodu do AKU (A), v režimu TUV do spirály zásobníku (B). TUV má přednost.</li>
    <li><strong>Zásobník TUV se spirálou <span class="n">19</span></strong>: spirála shora dolů, výkon spirály ≥ jmenovitý výkon TČ. Na přívodu i vratce spirály uzávěry <span class="n">2</span>. Čidlo TUV T2 <span class="n">20</span> v jímce zásobníku.</li>
    <li>Vratka ze spirály se spojí s vratkou z AKU <strong>před magnetickým filtrem <span class="n">16</span></strong> — filtr chrání TČ v obou režimech. Uzávěr na spodním hrdle AKU umožní odpojit AKU, zatímco ohřev TUV běží dál.</li>
    <li>Studená voda: uzávěr a zpětný ventil <span class="n">22</span>, expanzní nádoba pro pitnou vodu <span class="n">24</span>, pojistný ventil TUV <span class="n">23</span> bez uzávěru s výfukem do odpadu. Teplá voda odchází z horní části zásobníku; doporučujeme termostatický směšovač (voda nad 52 °C může opařit).</li>
    <li>Topná vložka <span class="n">21</span> volitelně — dohřev a antilegionella (1× za 7 dní ohřev na 70 °C).</li>
  </ol>'''
    sec.append(f'''<section class="pb">
  <h2><span class="no">2</span> Hydraulické zapojení</h2>
  <figure><div class="sheet"><img src="hydraulika.png" alt="Schéma hydraulického zapojení."></div>
    <figcaption>{"REO-SCH-K2 — vytápění s AKU 100 l a ohřev TUV; prvky 1–17 shodné s variantou 1." if tuv else "REO-SCH-K1 — pouze vytápění s AKU nádrží 100 l."}</figcaption></figure>
  <h3>Venkovní část</h3>
  <ol class="steps">
    <li>Na výstupu teplé vody z jednotky nejdřív kulový uzávěr <span class="n">2</span> co nejblíže hrdlu, za ním separátor <span class="n">4</span> s velkým bezpečnostním odvzdušňovacím ventilem a pojistným ventilem — nejvyšší bod venkovní části. Separátor zůstává venku: vzduch i případně uniklé R290 musí odejít do volného prostoru.</li>
    <li>Na vratce kulový uzávěr <span class="n">2</span> a protizámrazový ventil <span class="n">3</span> s výpustí dolů.</li>
    <li>Venkovní potrubí co nejkratší, v izolaci odolné UV; kabely samostatně v chráničce; prostup zdí utěsněný.</li>
  </ol>
  <h3>Technická místnost</h3>
  <ol class="steps">
    <li>Výstup z TČ do horního hrdla AKU <span class="n">5</span> přes uzávěr <span class="n">2</span>; vratka ze spodního hrdla přes uzávěr <span class="n">2</span>, magnetický filtr <span class="n">16</span> a další uzávěr <span class="n">2</span> zpět k TČ. Filtr je zároveň filtr na vstupu vody do TČ, který vyžaduje návod.</li>
    <li>Na AKU: automatický odvzdušňovací ventil <span class="n">6</span> nahoře, teploměr s pojistným ventilem <span class="n">8</span> na společném vývodu pláště (bez uzávěru, výfuk do odpadu), vypouštěcí kohout <span class="n">15</span> dole.</li>
    <li>TČ se řídí vlastním čidlem teploty vratné vody; vstup pro čidlo v AKU jednotky RH030–RH060 nemají.</li>
    <li>Výstup do topení: volitelně směšovací ventil <span class="n">17</span> s obtokem z vratky — u podlahového topení z bezpečnostních důvodů omezí teplotu na <strong>max. 40 °C, ideálně 35 °C</strong>. Dál uzávěr, sekundární oběhové čerpadlo <span class="n">10</span> a uzávěr.</li>
    <li>Napájení čerpadla <span class="n">10</span> spíná a rozpíná přijímač <span class="n">11</span> podle bezdrátového termostatu <span class="n">12</span> — tím se zapíná a vypíná dodávka tepla do topení.</li>
    <li>Za čerpadlem stoupačka s pojistnou skupinou <span class="n">7</span> (pojistný ventil + manometr) a nad ní expanzní nádoba <span class="n">9</span>, mezi nimi žádný uzávěr.</li>
    <li>Odvzdušnění v nejvyšším bodě rozvodu <span class="n">13</span> a ventilky radiátorů <span class="n">14</span>. Uzávěry zavírat jen při servisu.</li>
  </ol>{tuv_steps}
</section>''')
    # 3 — elektro
    tuv_el = ""
    if tuv:
        tuv_el = '''<li>TUV: trojcestný ventil na svorky 3 (L) + 4 (N) + PE; čidlo T2 do řídicí desky; topná vložka volitelně přes stykač ze svorek 1 + 4, s vlastním jističem.</li>'''
    sec.append(f'''<section class="pb">
  <h2><span class="no">3</span> Elektrické zapojení</h2>
  <figure><div class="sheet"><img src="elektro.png" alt="Schéma elektrického zapojení pro jednotky 1F i 3F."></div>
    <figcaption>{"REO-SCH-K2-E" if tuv else "REO-SCH-K1-E"} — podle zapojovacích schémat v návodu (str. 17–19).</figcaption></figure>
  <div class="tbl"><table><thead><tr><th>Modely</th><th>Napájení</th><th>Svorky</th><th>Chránič</th><th>Jistič TČ</th><th>Kabel</th></tr></thead><tbody>
    <tr><td>RH030, RH040, RH050-1F</td><td>230 V · 1F</td><td>L · N · PE</td><td>2pólový</td><td>1pólový</td><td>3 vodiče</td></tr>
    <tr><td>RH050-3F, RH060</td><td>400 V · 3F</td><td>R · S · T · N · PE</td><td>4pólový</td><td>3pólový + ochrana proti výpadku fáze</td><td>5 vodičů</td></tr>
  </tbody></table></div>
  <ul class="list">
    <li>Samostatný přívod do rozvaděče TČ; napětí ±10 %, při startu min. 90 % jmenovitého. Jistič (ne nožový vypínač) na 1,5násobek provozního proudu podle typového štítku.</li>
    <li>Hlavní vypínač s proudovým chráničem min. 1,4 m nad podlahou. Jednotka uzemněna, ochranný vodič se nesmí připojit na N.</li>
    <li>Kabelový ovladač připojen komunikačním kabelem k řídicí desce. Svorky 5–6 = vstup externího spínače (volitelně).</li>
    <li>Přijímač termostatu má vlastní jistič 230 V; jeho kontakt spíná fázi sekundárního čerpadla.</li>
    {tuv_el}
    <li>V zimě nevypínat napájení jednotky (ochrana proti zamrznutí). Zapojení provádí osoba s odbornou kvalifikací dle ČSN / EN.</li>
  </ul>
</section>''')
    # 4 — soupis
    items = ITEMS + (ITEMS_TUV if tuv else [])
    sec.append(f'''<section class="pb">
  <h2><span class="no">4</span> Soupis komponent</h2>
  <p>Čísla odpovídají schématům. Délky potrubí a počty fitinek se upřesní podle skutečné trasy.</p>
  {items_table(items)}
  <h3>Volba materiálu potrubí</h3>
  <p>Investor si může vybrat, zda bude hydraulické propojení v mědi, uhlíkové oceli nebo PPR. Vždy je třeba počítat i s fitinky — napojovacími a šroubovacími prvky (šroubení, kolena, T-kusy, přechodky). Návod doporučuje nerezové nebo PPR potrubí a každé zařízení připojit rozebíratelným šroubením.</p>
  {materials_table()}
</section>''')
    # 5 — uvedení do provozu
    tuv_fill = '<li>Nejdřív napustit a odvzdušnit zásobník TUV (otevřít kohout teplé vody), teprve pak zapnout topnou vložku.</li>' if tuv else ""
    tuv_chk = '<li>Vyvolat požadavek na TUV a ověřit přepnutí trojcestného ventilu na spirálu a zpět.</li>' if tuv else ""
    sec.append(f'''<section>
  <h2><span class="no">5</span> Uvedení do provozu</h2>
  <div class="cols">
    <div class="box"><h3>Napuštění a odvzdušnění</h3><ul class="list">
      <li>Zkontrolovat přednastavení expanzních nádob před napuštěním.</li>
      <li>Napouštět pomalu přes plnicí sestavu, uzávěry otevřené.</li>
      <li>Odvzdušnit od nejnižšího po nejvyšší bod: separátor, AKU, stoupačky, radiátory.</li>
      <li>Tlak ve studeném stavu typicky 1–1,5 bar (manometr pojistné skupiny).</li>{tuv_fill}
    </ul></div>
    <div class="box"><h3>Kontrola funkce</h3><ul class="list">
      <li>Jednotku nechat před prvním startem min. 12 h pod napětím (předehřev).</li>
      <li>Spustit TČ a ověřit, že se po dosažení nastavené teploty vypne.</li>
      <li>Zvýšit teplotu na termostatu: přijímač musí zapnout sekundární čerpadlo.</li>{tuv_chk}
      <li>Po zahřátí znovu odvzdušnit, doplnit tlak, vyčistit magnetický filtr.</li>
    </ul></div>
  </div>
</section>''')
    body = "\n\n".join(sec)
    return f'''<title>{e(v["title"])}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Source+Sans+3:wght@400;600;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <span class="eyebrow">REO HEATING · Pokyny k instalaci · varianta {"2" if tuv else "1"}</span>
  <h1>{e(v["h1"])}</h1>
  <p>{e(v["lead"])}</p>
  <div class="meta"><span><b>Jednotky:</b> REO RH030–RH060 (monoblok, R290), 1F i 3F</span><span><b>Schémata:</b> {e(v["codes"])}</span><span><b>Stav:</b> schválená schémata · {REV}</span></div>
</header>

{body}

<footer>
  <p>Zjednodušený orientační podklad. Dimenze potrubí, nastavení pojistných ventilů, velikost expanzních nádob, průřezy kabelů a hodnoty jističů určete podle návodu k TČ, typového štítku a konkrétního domu. Instalaci a elektrické zapojení provádí odborná firma.</p>
  <p>REO HEATING · podle návodu k instalaci RH030–RH060</p>
</footer>
</div>
'''


def main():
    out_root = os.path.join(ROOT, "pokyny")
    for key, v in VARIANTS.items():
        d = os.path.join(out_root, key)
        os.makedirs(d, exist_ok=True)
        for dst, src in v["imgs"].items():
            shutil.copyfile(os.path.join(ROOT, src), os.path.join(d, dst))
        p = os.path.join(d, "index.html")
        open(p, "w", encoding="utf-8").write(page(v))
        pdf = os.path.join(out_root, v["pdf"])
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", "file://" + p], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("zapsáno:", p, "|", pdf)


if __name__ == "__main__":
    main()
