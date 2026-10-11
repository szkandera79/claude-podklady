#!/usr/bin/env python3
"""Build katalogu RH X50: katalog.html (CZ, zdroj) → verze 1 a 2 (v2 = obálka z obalka-v2.html),\nkaždá CZ + EN → 4 PDF.

    python3 build.py

Anglická verze vzniká náhradou textů podle slovníku EN (klíč = přesný český text
v katalog.html). Když se změní český text, je potřeba upravit i klíč zde — skript
spadne, pokud klíč v HTML nenajde, a na konci ověří, že v EN nezůstala čeština.
"""
import os
import re
import subprocess

import fitz

DIR = os.path.dirname(os.path.abspath(__file__))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

EN = [
    ('<html lang="cs">', '<html lang="en">'),
    ('<title>REO HEATING — RH X50, komerční tepelné čerpadlo R290</title>',
     '<title>REO HEATING — RH X50, commercial R290 heat pump</title>'),
    # 1 · obálka
    ('Komerční řada · Chladivo R290', 'Commercial series · R290 refrigerant'),
    ('Plně invertorové tepelné čerpadlo<br>vzduch–voda', 'Full DC inverter<br>air-to-water heat pump'),
    ('''Dva chladicí okruhy, velký výkon a stabilní provoz. Vytápění,
      chlazení i ohřev teplé vody pro bytové domy, obce, firmy a komerční objekty.''',
     '''Two refrigerant circuits, large capacity and stable operation. Heating,
      cooling and domestic hot water for apartment buildings, municipalities, businesses and commercial sites.'''),
    ('<span>Vytápění</span><span>Chlazení</span><span>Teplá voda</span>',
     '<span>Heating</span><span>Cooling</span><span>Hot water</span>'),
    ('alt="Tepelné čerpadlo RH X50"', 'alt="RH X50 heat pump"'),
    ('<span>výstupní teplota<br>vody</span>', '<span>water outlet<br>temperature</span>'),
    ('<b>49 kW</b><span>topný výkon<br>při A7/W35</span>', '<b>49 kW</b><span>heating capacity<br>at A7/W35</span>'),
    ('<b>5,62</b><span>max. COP<br>(ohřev TV)</span>', '<b>5.62</b><span>max. COP<br>(hot water)</span>'),
    ('<span>třída ErP<br>při 35 °C</span>', '<span>ErP class<br>at 35 °C</span>'),
    ('<span>provoz do venkovní<br>teploty</span>', '<span>minimum ambient<br>operating temp.</span>'),
    ('<span>jednotek<br>v kaskádě</span>', '<span>units<br>in cascade</span>'),
    # 2 · vlastnosti
    ('<div class="eyebrow">Vlastnosti</div>', '<div class="eyebrow">Features</div>'),
    ('Řešení navržené pro<br><em>komerční provoz</em>', 'Designed for<br><em>commercial applications</em>'),
    ('''RH X50 spojuje vysokou účinnost a všestrannost. Pokryje vytápění,
      chlazení i ohřev teplé vody a díky kaskádě roste s potřebou objektu.''',
     '''RH X50 combines maximum efficiency with versatility. It covers heating,
      cooling and hot water, and cascade control lets it grow with the building's demand.'''),
    ('Chladivo <b>R290</b> (propan) — ODP = 0, nízké GWP = 3.', '<b>R290</b> refrigerant (propane) — ODP = 0, low GWP = 3.'),
    ('''<b>Dvojitá invertorová technologie:</b> přesné a úsporné vytápění
          s výstupní teplotou vody až 78 °C.''',
     '''<b>Dual DC inverter technology:</b> precise and efficient heating
          with a water outlet temperature of up to 78 °C.'''),
    ('<b>Nejvyšší energetická třída:</b> ErP A+++ (při 35 °C), COP až 5,62.',
     '<b>Top efficiency rating:</b> ErP A+++ (at 35 °C), COP up to 5.62.'),
    ('<b>Vestavěný Wi‑Fi modul</b> pro připojení a vzdálené ovládání.',
     '<b>Built-in Wi‑Fi module</b> for connectivity and remote control.'),
    ('<b>Vícejazyčné ovládání</b> — snadná obsluha v řadě jazyků.',
     '<b>Multilingual interface</b> — easy operation in many languages.'),
    ('''<b>SG Ready (Smart Grid):</b> lepší řízení energie a napojení
          na chytrou síť.''',
     '''<b>SG Ready (Smart Grid):</b> better energy management and
          smart grid integration.'''),
    ('<b>Automatická regulace teploty</b> pro optimální provoz.',
     '<b>Automatic temperature control</b> for optimal performance.'),
    ('<b>Noční režim</b> se sníženou hlučností mimo pracovní dobu.',
     '<b>Night mode</b> with reduced noise during off-hours.'),
    ('<b>Kaskádové řízení</b> až 8 jednotek pro flexibilní navýšení výkonu.',
     '<b>Cascade control</b> of up to 8 units for flexible scaling.'),
    ('<b>Časovaná tepelná dezinfekce</b> pro bezpečný a hygienický provoz teplé vody.',
     '<b>Timed high-temperature disinfection</b> for safe and hygienic hot water.'),
    ('<b>Cloudová platforma</b> pro vzdálený dohled a správu.',
     '<b>IoT cloud platform</b> for remote monitoring and management.'),
    ('''<b>Volitelná výbava:</b> vestavěná oběhová čerpadla, snímač úniku chladiva,
          řízení externího zdroje tepla a zásobníku teplé vody.''',
     '''<b>Options:</b> built-in circulation pumps, refrigerant leak sensor,
          control of an external heat source and hot water tank.'''),
    ('alt="RH X50 — pohled zboku"', 'alt="RH X50 — side view"'),
    ('alt="RH X50 — pohled zepředu"', 'alt="RH X50 — front view"'),
    ('<span>přírodní chladivo<br>GWP = 3</span>', '<span>natural refrigerant<br>GWP = 3</span>'),
    ('<span>energetická třída<br>při 35 °C</span>', '<span>energy class<br>at 35 °C</span>'),
    ('<span>max. výstupní<br>teplota vody</span>', '<span>max. water<br>outlet temp.</span>'),
    ('<span>vzdálené ovládání<br>a dohled</span>', '<span>remote control<br>and monitoring</span>'),
    ('<b>Dva chladicí okruhy,<br>velký výkon, stabilní provoz</b>',
     '<b>Two-circuit configuration,<br>large capacity, superior stability</b>'),
    ('''<span>Dvouokruhová konstrukce s dvojicí invertorových kompresorů pokrývá
        velký výkon v jediné jednotce a podle potřeby ho plynule reguluje.</span>''',
     '''<span>A two-circuit design with a pair of inverter compressors delivers
        large capacity in a single unit and modulates it smoothly to demand.</span>'''),
    # 3 · konstrukce
    ('<div class="eyebrow">Konstrukce a výbava</div>', '<div class="eyebrow">Design and equipment</div>'),
    ('Prémiová výbava,<br><em>spolehlivá kvalita</em>', 'Premium configuration,<br><em>reliable quality</em>'),
    ('alt="Barevný dotykový ovladač"', 'alt="Colour touchscreen controller"'),
    ('''<b style="color:var(--ink)">Velký barevný dotykový ovladač</b> s vestavěným Wi‑Fi
          modulem. Na jedné obrazovce je vidět stav vytápění i teplé vody.''',
     '''<b style="color:var(--ink)">Large colour touchscreen controller</b> with a built-in
          Wi‑Fi module. Heating and hot water status on a single screen.'''),
    ('<dt>Režimy</dt><dd>vytápění · teplá voda · chlazení · automatický</dd>',
     '<dt>Modes</dt><dd>heating · hot water · cooling · automatic</dd>'),
    ('<dt>Teploty</dt><dd>požadovaná a aktuální teplota vody pro ÚT i TV</dd>',
     '<dt>Temperatures</dt><dd>target and current water temperature for heating and hot water</dd>'),
    ('<dt>Stav</dt><dd>provozní stav, Wi‑Fi, hlášení poruch</dd>',
     '<dt>Status</dt><dd>operating state, Wi‑Fi, error messages</dd>'),
    ('<dt>Funkce</dt><dd>časové programy, dotazy na provozní hodnoty, zámek obrazovky</dd>',
     '<dt>Functions</dt><dd>timers, operating data query, screen lock</dd>'),
    ('<dt>Nastavení</dt><dd>volba režimu a parametrů jednotky</dd>',
     '<dt>Settings</dt><dd>mode selection and unit parameters</dd>'),
    ('<b>Snímač úniku chladiva R290</b>', '<b>R290 refrigerant leak sensor</b>'),
    ('<span>Při dosažení koncentrace 15 % spustí alarm.</span>',
     '<span>Triggers an alarm when the concentration reaches 15 %.</span>'),
    ('<b>Barevný dotykový ovladač</b>', '<b>Colour touchscreen controller</b>'),
    ('<span>Vestavěný Wi‑Fi modul, ovládání jednotky i koncových zařízení.</span>',
     '<span>Built-in Wi‑Fi module, control of the unit and end devices.</span>'),
    ('<li>Manometry</li>', '<li>Pressure gauges</li>'),
    ('<li>Elektrický rozvaděč</li>', '<li>Electrical control box</li>'),
    ('<li>Sběrač chladiva</li>', '<li>Liquid receiver</li>'),
    ('<li>Deskový výměník</li>', '<li>Plate heat exchanger</li>'),
    ('<b>Lamelový výměník s plochými lamelami</b>', '<b>Flat-panel louvered fin heat exchanger</b>'),
    ('''<span>Hydrofilní povrch odolný proti korozi, solné mlze a oxidaci.
            Ploché lamely méně zachytávají vodu, led i prach, snadno se čistí
            a kladou menší odpor vzduchu.</span>''',
     '''<span>Hydrophilic coating resistant to corrosion, salt spray and oxidation.
            The flat design minimises water, ice and dust build-up, is easy to clean
            and reduces air resistance.</span>'''),
    ('<b>Nízká hlučnost</b>', '<b>Low noise</b>'),
    ('''<span>Konstrukce s řadou protihlukových opatření — akustický tlak
            62 dB(A) ve vzdálenosti 1 m.</span>''',
     '''<span>Multiple noise reduction measures — sound pressure level
            of 62 dB(A) at 1 m.</span>'''),
    ('<b>Velký DC invertorový ventilátor 14 000 m³/h</b>', '<b>Large DC inverter fan, 14,000 m³/h</b>'),
    ('''<span>Plynulá regulace otáček, tichý chod, méně pohyblivých dílů
            a vyšší účinnost.</span>''',
     '''<span>Stepless speed control, quiet operation, fewer moving parts
            and higher efficiency.</span>'''),
    ('alt="Odvod kondenzátu v podstavě"', 'alt="Chassis condensate drainage"'),
    ('<b>Odvod kondenzátu v podstavě</b>', '<b>Chassis drainage holes</b>'),
    ('<span>Otvory v šasi odvádějí kondenzát přímo ven a brání tvorbě ledu.</span>',
     '<span>Condensate drains straight out of the chassis, preventing ice build-up.</span>'),
    ('alt="Invertorové kompresory"', 'alt="Inverter compressors"'),
    ('<b>Invertorové kompresory HIGHLY<br>(dva okruhy)</b>', '<b>HIGHLY full DC inverter<br>compressors (two circuits)</b>'),
    ('<span>Nízké vibrace, tichý chod a vysoká účinnost i v mrazu do −25 °C.</span>',
     '<span>Low vibration, quiet operation and high efficiency even at −25&nbsp;°C.</span>'),
    # 4 · parametry
    ('<div class="eyebrow">Technické parametry</div>', '<div class="eyebrow">Technical data</div>'),
    ('Invertorové tepelné čerpadlo R290<br>pro vytápění, chlazení a teplou vodu',
     'DC inverter R290 heat pump<br>for heating, cooling and hot water'),
    ('Ohřev teplé vody <small>venkovní 20/15 °C (DB/WB), voda 15/55 °C</small>',
     'Domestic hot water <small>ambient 20/15 °C (DB/WB), water 15/55 °C</small>'),
    ('Vytápění <small>venkovní 7/6 °C (DB/WB), voda 30/35 °C</small>',
     'Heating <small>ambient 7/6 °C (DB/WB), water 30/35 °C</small>'),
    ('Chlazení <small>venkovní 35/24 °C (DB/WB), voda 12/7 °C</small>',
     'Cooling <small>ambient 35/24 °C (DB/WB), water 12/7 °C</small>'),
    ('<th>Topný výkon (kW)</th><td>23,8–68</td>', '<th>Heating capacity (kW)</th><td>23.8–68</td>'),
    ('<th>Příkon (kW)</th><td>4,23–15,46</td>', '<th>Power input (kW)</th><td>4.23–15.46</td>'),
    ('<th>COP</th><td>4,39–5,62</td>', '<th>COP</th><td>4.39–5.62</td>'),
    ('<th>Množství ohřáté vody (l/h)</th><td>1 462</td>', '<th>Heated water output (l/h)</th><td>1,462</td>'),
    ('<th>Topný výkon (kW)</th><td>18,4–49,25</td>', '<th>Heating capacity (kW)</th><td>18.4–49.25</td>'),
    ('<th>Příkon (kW)</th><td>4,23–12,96</td>', '<th>Power input (kW)</th><td>4.23–12.96</td>'),
    ('<th>COP</th><td>3,8–4,3</td>', '<th>COP</th><td>3.8–4.3</td>'),
    ('<th>Chladicí výkon (kW)</th><td>13,8–34,5</td>', '<th>Cooling capacity (kW)</th><td>13.8–34.5</td>'),
    ('<th>Příkon (kW)</th><td>5,2–16,2</td>', '<th>Power input (kW)</th><td>5.2–16.2</td>'),
    ('<th>EER</th><td>2,12–2,65</td>', '<th>EER</th><td>2.12–2.65</td>'),
    ('Elektro a hydraulika', 'Electrical and hydraulic'),
    ('<th>Energetická třída ErP (35 °C / 55 °C)</th>', '<th>ErP energy class (35 °C / 55 °C)</th>'),
    ('<th>Napájení</th><td>380 V / 3f / 50–60 Hz</td>', '<th>Power supply</th><td>380 V / 3 Ph / 50–60 Hz</td>'),
    ('<th>Max. příkon (kW) / max. proud (A)</th>', '<th>Max. power input (kW) / max. current (A)</th>'),
    ('<th>Jistič (A) / průřez přívodu (mm²)</th>', '<th>Fuse or circuit breaker (A) / cable cross-section (mm²)</th>'),
    ('<th>Připojení vody</th>', '<th>Water connection</th>'),
    ('<th>Průtok vody (m³/h) / max. tlaková ztráta (kPa)</th><td>5,8 / 80</td>',
     '<th>Water flow (m³/h) / max. pressure drop (kPa)</th><td>5.8 / 80</td>'),
    ('<th>Akustický výkon / akustický tlak v 1 m (dB(A))</th>', '<th>Sound power / sound pressure at 1 m (dB(A))</th>'),
    ('Provoz a konstrukce', 'Operation and construction'),
    ('<th>Chladivo / kompresor</th><td>R290 / HIGHLY, invertorový</td>',
     '<th>Refrigerant / compressor</th><td>R290 / HIGHLY, DC inverter</td>'),
    ('<th>Rozsah venkovních teplot (°C)</th><td>−25 až 43</td>',
     '<th>Operating ambient temperature (°C)</th><td>−25 to 43</td>'),
    ('<th>Výstupní teplota vody — vytápění / TV (°C)</th>', '<th>Water outlet temperature — heating / DHW (°C)</th>'),
    ('<th>Výstupní teplota vody — chlazení (°C)</th>', '<th>Water outlet temperature — cooling (°C)</th>'),
    ('<th>Krytí / třída ochrany před úrazem</th>', '<th>IP rating / electric shock protection class</th>'),
    ('<th>Rozměry jednotky Š × H × V (mm)</th><td>1 195 × 980 × 1 900</td>',
     '<th>Unit dimensions W × D × H (mm)</th><td>1,195 × 980 × 1,900</td>'),
    ('<th>Rozměry balení Š × H × V (mm)</th><td>1 275 × 1 060 × 2 100</td>',
     '<th>Packing dimensions W × D × H (mm)</th><td>1,275 × 1,060 × 2,100</td>'),
    ('<th>Hmotnost netto (kg)</th>', '<th>Net weight (kg)</th>'),
    ('''Parametry se mohou v rámci průběžného vývoje produktu měnit.
      Rozhodující jsou údaje na výrobním štítku dodané jednotky. Podrobné výkonové
      křivky viz protokol výkonových charakteristik RH X50.''',
     '''Specifications may change as part of continuous product development.
      The data on the rating plate of the delivered unit are binding. For detailed
      performance curves, see the RH X50 performance data sheet.'''),
    ('<span>Telefon</span>', '<span>Phone</span>'),
]

src = open(os.path.join(DIR, 'katalog.html'), encoding='utf-8').read()

# Verze 2 = stejný katalog, jen obálka se scénou z originálu (obalka-v2.html).
COVER = re.compile(r'<!-- ═+ 1 · OBÁLKA ═+ -->.*?</section>', re.S)
assert len(COVER.findall(src)) == 1, 'v katalog.html nenalezena obálka'
cover2 = open(os.path.join(DIR, 'obalka-v2.html'), encoding='utf-8').read()
open(os.path.join(DIR, 'katalog-v2.html'), 'w', encoding='utf-8').write(COVER.sub(lambda m: cover2, src))


def translate(cz_html, name):
    en = cz_html
    for cz, tr in EN:
        assert cz in en, f'klíč nenalezen v {name}:\n{cz}'
        en = en.replace(cz, tr)
    # komentáře a CSS nechat, kontrolovat jen viditelný obsah
    body = re.sub(r'<!--.*?-->|<style>.*?</style>', '', en.split('<body>')[1], flags=re.S)
    left = sorted(set(re.findall(r'[^\x00-\x7F°±×–—²³½‑·−≤→]+', re.sub(r'<[^>]+>', ' ', body))))
    assert not left, f'{name}: v EN zůstala čeština: {left}'
    return en


for v in ('', '-v2'):
    cz = open(os.path.join(DIR, f'katalog{v}.html'), encoding='utf-8').read()
    open(os.path.join(DIR, f'katalog{v}-en.html'), 'w', encoding='utf-8').write(translate(cz, f'katalog{v}.html'))

TITLE = {'CZ': 'RH X50 — komerční tepelné čerpadlo R290', 'EN': 'RH X50 — commercial R290 heat pump'}
for v in ('', '-v2'):
    for lang, html in (('CZ', f'katalog{v}.html'), ('EN', f'katalog{v}-en.html')):
        title = TITLE[lang]
        out = os.path.join(DIR, f'RH-X50-katalog{v}-{lang}.pdf')
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={out}', '--virtual-time-budget=8000',
                        'file://' + os.path.join(DIR, html)], check=True, capture_output=True)
        doc = fitz.open(out)
        assert doc.page_count == 4, f'{out}: {doc.page_count} stran místo 4'
        text = ' '.join(p.get_text() for p in doc).upper()
        for bad in ('POWER WORLD', 'POWERWORLD', 'PW150', 'PW300', 'DKZLRS'):
            assert bad not in text, f'{out}: zůstala stopa výrobce „{bad}"'
        doc.set_metadata({'title': title, 'author': 'REO HEATING', 'creator': 'REO HEATING',
                          'producer': 'REO HEATING', 'subject': title, 'keywords': 'RH X50, REO HEATING, R290'})
        doc.save(out + '.tmp', garbage=3, deflate=True)
        os.replace(out + '.tmp', out)
        print('uloženo:', out)
