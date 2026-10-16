#!/usr/bin/env python3
"""Položkový investiční rozpočet univerzální mobilní kotelny (fáze 4).

Výstup: src/budget.html (vkládá ho build_studie.py jako kap. 14). Spuštění samostatně vypíše souhrn.
Zdroj ceny u každé položky:
  T = tržní cena z rešerše 16. 10. 2026 (kap. 13; ✓ = ověřeno přímo na webu prodejce)
  Z = cena sdělená zadavatelem
  O = vlastní odborný odhad (k poptání)
Všechny ceny bez DPH. Varianty kontejneru: E = ekonomická, U = univerzální.
"""
from pathlib import Path

FX_USD = 21.369          # ČNB 23. 9. 2026 (porovnani-x50-rh060)
LANDED = 1.12            # doprava + clo na EXW cenu [ODHAD]
RESERVE = 0.10

# (skupina, položka, množství E, množství U, jedn. cena E, jedn. cena U, zdroj, poznámka)
CORE = [
    ('Kontejner', 'Kontejner 20′ použitý, cargo-worthy', 1, 0, 40_000, 0, 'T', 'Locont 38–42 tis., NOVAK od 38 500'),
    ('Kontejner', 'Kontejner 20′ nový one-trip, CSC', 0, 1, 0, 62_500, 'T✓', 'kontik; HC +22 500 Kč'),
    ('Kontejner', 'Doprava kontejneru do dílny', 1, 1, 4_000, 4_000, 'T', 'HZ 3 500, Kontejnery Ostrava 3 719'),
    ('Kontejner', 'Zateplení stěn a stropu (≈ 53 m²)', 1, 1, 32_000, 32_000, 'O', 'stříkaný PUR / minerální vata'),
    ('Kontejner', 'Prostupy: panel rychlospojek, kabelové vývodky, větrací mřížky', 1, 1, 18_000, 18_000, 'O', ''),
    ('Kontejner', 'Podlaha: protiskluzová úprava, záchytná vana pod nádržemi', 1, 1, 8_000, 15_000, 'O', ''),
    ('Kontejner', 'Nátěr, značení, tabulky R290', 1, 1, 8_000, 8_000, 'O', ''),
    ('Konstrukce', 'Hutní materiál nosného rámu (≈ 550 kg)', 1, 1, 25_000, 25_000, 'O', '≈ 45 Kč/kg'),
    ('Konstrukce', 'Výroba a montáž rámu, šroubované držáky, kotvení (≈ 90 h)', 1, 1, 58_000, 58_000, 'O', '650 Kč/h'),
    ('Konstrukce', 'Povrchová úprava rámu (zinek / nátěr)', 1, 1, 12_000, 12_000, 'O', ''),
    ('Konstrukce', 'Statické posouzení kotvení a přepravy', 1, 1, 25_000, 25_000, 'O', 'autorizovaný konstruktér'),
    ('Nádrže', 'Akumulační nádrž 1 000 l nová', 0, 1, 0, 5_000, 'Z', 'podezřele nízká cena, ověřit'),
    ('Nádrže', 'Izolace k AKU 1 000 l (pokud není v ceně)', 0, 1, 0, 9_000, 'O', ''),
    ('Nádrže', 'Topná vložka TUV 6 kW + termostat (sterilizace)', 1, 1, 6_000, 6_000, 'O', ''),
    ('Hydraulika', 'Sběrač a rozdělovač větví jednotek na AKU (AKU = hydraulický separátor)', 1, 1, 12_000, 8_000, 'O', 'E: propojení 3 nádrží'),
    ('Hydraulika', 'Čerpadlo sekundáru EC (U zdvojené)', 1, 1, 30_000, 55_000, 'O', ''),
    ('Hydraulika', 'Expanzní nádoby soustavy (≈ 150 l), pojistné ventily', 1, 1, 9_000, 9_000, 'O', ''),
    ('Ochrana proti zamrznutí', 'UPS pro oběhová čerpadla a regulaci (≈ 2 kWh)', 1, 1, 35_000, 35_000, 'O', 'cirkulace při výpadku proudu'),
    ('Ochrana proti zamrznutí', 'Hlídání tlaku a teploty vratné vody, poplach přes GSM', 1, 1, 6_000, 6_000, 'O', ''),
    ('Hydraulika', 'Filtr a magnetický odkalovač sekundáru', 1, 1, 14_000, 14_000, 'O', ''),
    ('Hydraulika', 'Plnicí a doplňovací sestava s oddělovačem EN 1717', 1, 1, 9_000, 9_000, 'O', ''),
    ('Hydraulika', 'TUV: pojistná sestava, expanzomat 25 l, cirkulační čerpadlo', 1, 1, 15_000, 15_000, 'O', ''),
    ('Hydraulika', 'Armatury DN25–65 (≈ 35 ks kohoutů, klapek, filtrů)', 1, 1, 38_000, 38_000, 'O', 'kohout 2″ 1 264 Kč (T)'),
    ('Hydraulika', 'Potrubí a tvarovky v kontejneru (≈ 35 m)', 1, 1, 32_000, 32_000, 'O', ''),
    ('Hydraulika', 'Izolace potrubí, teploměry, manometry, odvzdušnění', 1, 1, 15_000, 15_000, 'O', 'K-Flex 207 Kč/m (T)'),
    ('Připojení', 'Sada hadic DN50 2× 20 m (CALORTEC, Camlock EPDM, spony, kohouty, izolace)', 1, 1, 47_500, 47_500, 'T', 'sestaveno z cen rešerše'),
    ('Připojení', 'Sada hadic DN65 2× 20 m pro 100 kW', 0, 1, 0, 65_000, 'T', 'sestaveno z cen rešerše'),
    ('Připojení', 'Přechodové kusy na různá hrdla (redukce, příruby)', 1, 1, 6_000, 12_000, 'O', ''),
    ('Připojení', 'Přípojky studené vody, TUV a cirkulace', 1, 1, 12_000, 12_000, 'O', 'hadice pro pitnou vodu na dotaz'),
    ('Elektro', 'Rozvaděč (E 80 A, U 100 A): vypínač, SPD T1+T2, hlídač fází', 1, 1, 38_000, 45_000, 'O', ''),
    ('Elektro', 'Přívodní kabel s CEE (E 5×25 / 25 m, U 4×35+PE / 30 m, 125 A)', 1, 1, 26_000, 32_000, 'O', ''),
    ('Elektro', 'Elektroinstalace kontejneru, osvětlení, temperace 2 kW', 1, 1, 18_000, 18_000, 'O', ''),
    ('Elektro', 'Příprava na podružné měření elektřiny a tepla', 1, 1, 4_000, 4_000, 'O', 'měřidla volitelně'),
    ('Regulace', 'PLC, HMI, čidla, LTE router, GSM poplach s baterií', 1, 1, 45_000, 75_000, 'O', ''),
    ('Regulace', 'Programování kaskády, vzdálený přístup, oživení', 1, 1, 25_000, 45_000, 'O', ''),
    ('Práce', 'Montáž technologie (≈ 180 h instalatér + elektrikář)', 1, 1, 117_000, 117_000, 'O', '650 Kč/h'),
    ('Práce', 'Tlakové zkoušky, proplach, plnění, uvedení do provozu', 1, 1, 12_000, 12_000, 'O', ''),
    ('Práce', 'Dokumentace, výchozí revize elektro, posouzení R290 (EN 378)', 1, 1, 35_000, 35_000, 'O', ''),
]

# nové výdaje navázané na každou venkovní jednotku
PER_UNIT = {
    'RHX50': [('Rám s kapsami VZV a silentbloky', 15_000, 'O'), ('Externí oběhové čerpadlo (návod)', 18_000, 'O'),
              ('Vývod v rozvaděči: jistič 40 A + chránič typ B', 9_000, 'O'), ('Kabel 5×10 mm², 10 m, komunikace', 4_500, 'O'),
              ('Pár hadic DN50 2× 4 m, rychlospojky, izolace', 10_500, 'T'), ('Filtr, zpětná klapka, uzávěry větve', 4_000, 'O'),
              ('2× protimrazový ventil + zavzdušňovací ventil', 6_000, 'O'), ('2× uzávěr s pružinovým návratem (bez proudu zavře)', 12_000, 'O')],
    'RH': [('Rám s kapsami VZV a silentbloky', 7_000, 'O'),
           ('Vývod v rozvaděči: jistič 16–20 A + chránič typ B', 6_000, 'O'), ('Kabel 5×4 mm², 10 m, komunikace', 2_000, 'O'),
           ('Pár hadic DN32 2× 4 m, rychlospojky, izolace', 6_500, 'T'), ('Filtr, zpětná klapka, uzávěry větve', 3_000, 'O'),
           ('2× protimrazový ventil + zavzdušňovací ventil', 5_000, 'O'), ('2× uzávěr s pružinovým návratem (bez proudu zavře)', 9_000, 'O')],
}

# skladové díly: (název, účetní hodnota/ks, zdroj, prodejní cena nového/ks, zdroj)
STOCK = {
    'RHX50': ('RH X50', 110_000, 'Z', 430_000, 'Z'),
    'RH060': ('RH060', round(2_398 * FX_USD * LANDED, -2), 'O', 160_000, 'Z'),
    'RH050': ('RH050', round(1_960 * FX_USD * LANDED, -2), 'O', 125_000, 'Z'),
    'TUV300': ('Zásobník TUV 300 l (vlastní výroba)', 12_000, 'O', 25_000, 'O'),
    'AKU300': ('Akumulační nádrž 300 l', 7_000, 'O', 12_000, 'O'),
    'AKU500': ('Akumulační nádrž 500 l', 10_000, 'O', 16_000, 'O'),
}
USED_SHARE = 0.55
# rozdíl proti glykolovému primáru (separátor 22k + výměník 38k + čerpadlo 32k + glykol 7k − ochrana vody 35k − 6k − ventily ≈ 3× 18k − rozdělovač 8k)
GLYCOL_DELTA = 22_000 + 38_000 + 32_000 + 7_000 - 35_000 - 6_000 - 3 * 18_000 - 8_000        # prodejní hodnota po 1. pronájmu jako podíl ceny nového [ODHAD]

HP_CONFIGS = {
    'B-2': ('2× RH X50 + RH050 pro TUV', ['RHX50', 'RHX50', 'RH050']),
    'A-50': ('2× RH060 + 2× RH050 + RH050 pro TUV', ['RH060', 'RH060', 'RH050', 'RH050', 'RH050']),
}
TANKS = {'E': ['AKU300', 'AKU300', 'AKU500', 'TUV300', 'TUV300', 'TUV300'],   # konfigurace nádrží A
         'U': ['TUV300', 'TUV300', 'TUV300']}                                  # konfigurace nádrží B

# životnost ve vytápěcích sezónách (6 měsíců) pro opotřebení [ODHAD]
LIFE = {'Ochrana proti zamrznutí': 8, 'Kontejner': 10, 'Konstrukce': 10, 'Nádrže': 10, 'Hydraulika': 8, 'Připojení': 4, 'Elektro': 8,
        'Regulace': 6, 'Práce': 10, 'jednotky': 8, 'TČ': 8, 'zásobníky': 10}


def core_items(v):
    out = []
    for g, name, qe, qu, pe, pu, src, note in CORE:
        q, p = (qe, pe) if v == 'E' else (qu, pu)
        if q:
            out.append((g, name, q, p, q * p, src, note))
    return out


def unit_items(cfg):
    out = {}
    for u in HP_CONFIGS[cfg][1]:
        key = 'RHX50' if u == 'RHX50' else 'RH'
        for name, p, src in PER_UNIT[key]:
            k = (key, name)
            q, _, s = out.get(k, (0, p, src))
            out[k] = (q + 1, p, s)
    return [(('RH X50: ' if k[0] == 'RHX50' else 'RH050/060: ') + k[1], q, p, q * p, s) for k, (q, p, s) in out.items()]


def stock_items(v, cfg):
    names = HP_CONFIGS[cfg][1] + TANKS[v]
    out = []
    for key in dict.fromkeys(names):
        n = names.count(key)
        name, book, bsrc, new, nsrc = STOCK[key]
        out.append((key, name, n, book, n * book, bsrc, new, n * new * (1 - USED_SHARE), nsrc))
    return out


def totals(v, cfg):
    core = sum(x[4] for x in core_items(v))
    units = sum(x[3] for x in unit_items(cfg))
    new = (core + units) * (1 + RESERVE)
    st = stock_items(v, cfg)
    book = sum(x[4] for x in st)
    opp = sum(x[7] for x in st)
    # opotřebení za sezónu
    wear = 0.0
    for g, name, q, p, tot, src, note in core_items(v):
        wear += tot * (1 + RESERVE) / LIFE[g]
    wear += units * (1 + RESERVE) / LIFE['jednotky']
    for key, name, n, b, btot, *_ in st:
        wear += btot / (LIFE['TČ'] if key.startswith('RH') else LIFE['zásobníky'])
    return dict(core=core, units=units, reserve=(core + units) * RESERVE, new=new, book=book, opp=opp,
                econ=new + book, econ_opp=new + book + opp, wear=wear)


TANK_CONFIGS = [
    ('A', 'Maximum skladových nádrží: AKU 2× 300 + 500 l, TUV 3× 300 l', 0, 'AKU300 AKU300 AKU500 TUV300 TUV300 TUV300',
     '6 nádob, ≈ 3,4 m² půdorysu; nejvíc spojů a odvzdušnění; AKU ve 3 nádobách hůř vrství', 'nižší: dvě nádoby AKU navíc'),
    ('B', 'Nová AKU 1 000 l + TUV 2–3× 300 l ze skladu', 14_000, 'TUV300 TUV300 TUV300',
     '4 nádoby, ≈ 2,1 m²; jednoduchá AKU; TUV v sérii nebo paralelně', 'dobrá: rám připraven na TUV 1 000 l'),
    ('C', 'Nová AKU 1 000 l + nový TUV 1 000 l', 14_000 + 65_000, '',
     '2 nádoby, ≈ 2,0 m²; nejjednodušší hydraulika; klopná výška obou nádrží ověřit', 'nejvyšší; zásobníky 300 l zůstanou prodejné jako nové'),
]


def tank_rows():
    out = []
    for code, name, new, stock, space, univ in TANK_CONFIGS:
        keys = stock.split()
        book = sum(STOCK[k][1] for k in keys)
        opp = sum(STOCK[k][3] * (1 - USED_SHARE) for k in keys)
        out.append((code, name, new, book, opp, new + book + opp, space, univ))
    return out


# ------------------------------------------------------------------ HTML
def f0(x):
    return f'{x:,.0f}'.replace(',', ' ')


SRC = {'T': '<span class="src t" title="tržní cena z rešerše">T</span>',
       'T✓': '<span class="src t" title="tržní cena ověřená na webu prodejce">T✓</span>',
       'Z': '<span class="src z" title="sděleno zadavatelem">Z</span>',
       'O': '<span class="src o" title="vlastní odhad">O</span>'}


def html():
    T = {(v, c): totals(v, c) for v in 'EU' for c in HP_CONFIGS}
    # souhrn
    head = ''.join(f'<th>{"Ekonomická" if v == "E" else "Univerzální"}<span class="sub">{c}</span></th>' for v in 'EU' for c in HP_CONFIGS)
    def row(label, key, cls=''):
        return f'<tr class="{cls}"><th scope="row" class="l">{label}</th>' + ''.join(
            f'<td class="{"hl" if cls else ""}">{f0(T[(v, c)][key])}</td>' for v in 'EU' for c in HP_CONFIGS) + '</tr>'
    summary = f'''<div class="tbl"><table><thead><tr><th class="l">Kč bez DPH</th>{head}</tr></thead><tbody>
{row('Kontejner a technologie', 'core')}
{row('Výdaje navázané na jednotky (rámy, hadice, vývody)', 'units')}
{row(f'Rezerva {int(RESERVE * 100)} %', 'reserve')}
{row('A · Nové finanční výdaje', 'new', 'sum')}
{row('B · Skladové díly v účetní hodnotě', 'book')}
{row('C · Celková ekonomická hodnota (A + B)', 'econ', 'sum')}
{row('Ztráta prodejní hodnoty skladových dílů po 1. nasazení', 'opp')}
{row('C′ · Včetně alternativních nákladů', 'econ_opp', 'sum')}
{row('Opotřebení za jednu sezónu (6 měsíců)', 'wear')}
</tbody></table></div>'''

    # položky A
    rows = ''
    last = None
    for (g, name, qe, qu, pe, pu, src, note) in CORE:
        if g != last:
            rows += f'<tr class="grp"><th scope="row" colspan="5" class="l">{g}</th></tr>'
            last = g
        e = f0(qe * pe) if qe else '—'
        u = f0(qu * pu) if qu else '—'
        rows += f'<tr><td class="l">{name}</td><td>{SRC[src]}</td><td>{e}</td><td>{u}</td><td class="l note">{note}</td></tr>'
    E, U = T[('E', 'B-2')], T[('U', 'B-2')]
    items_a = f'''<div class="tbl"><table class="mk"><thead><tr><th class="l">Položka</th><th>Zdroj</th><th>Ekonomická</th><th>Univerzální</th><th class="l">Poznámka</th></tr></thead>
<tbody>{rows}<tr class="sum"><th scope="row" class="l">Součet bez rezervy</th><td></td><td class="hl">{f0(E["core"])}</td><td class="hl">{f0(U["core"])}</td><td></td></tr></tbody></table></div>'''

    # jednotky
    urows = ''
    for c, (name, _) in HP_CONFIGS.items():
        items = unit_items(c)
        urows += f'<tr class="grp"><th scope="row" colspan="5" class="l">{c} · {name}</th></tr>'
        for n, q, p, tot, s in items:
            urows += f'<tr><td class="l">{n}</td><td>{SRC[s]}</td><td>{q}×</td><td>{f0(p)}</td><td>{f0(tot)}</td></tr>'
        urows += f'<tr class="sum"><th scope="row" class="l" colspan="4">Součet {c}</th><td class="hl">{f0(sum(x[3] for x in items))}</td></tr>'
    items_u = f'''<div class="tbl"><table class="mk"><thead><tr><th class="l">Položka</th><th>Zdroj</th><th>Počet</th><th>Kč/ks</th><th>Celkem</th></tr></thead><tbody>{urows}</tbody></table></div>'''

    # skladové díly B
    srows = ''
    for key in ['RHX50', 'RH060', 'RH050', 'TUV300', 'AKU300', 'AKU500']:
        name, book, bsrc, new, nsrc = STOCK[key]
        srows += (f'<tr><td class="l">{name}</td><td>{SRC[bsrc]}</td><td>{f0(book)}</td><td>{SRC[nsrc]}</td><td>{f0(new)}</td>'
                  f'<td>{f0(new * USED_SHARE)}</td><td>{f0(new * (1 - USED_SHARE))}</td></tr>')
    items_b = f'''<div class="tbl"><table class="mk"><thead><tr><th class="l">Skladový díl</th><th>Zdroj</th><th>Účetní hodnota/ks</th>
<th>Zdroj</th><th>Prodejní cena nového</th><th>Hodnota po 1. nasazení ({int(USED_SHARE * 100)} %)</th><th>Ztráta prodejní hodnoty</th></tr></thead><tbody>{srows}</tbody></table></div>'''

    # nádrže A/B/C
    trows = ''.join(f'<tr><th scope="row">{c}</th><td class="l">{n}</td><td>{f0(new)}</td><td>{f0(book)}</td><td>{f0(opp)}</td>'
                    f'<td class="hl">{f0(tot)}</td><td class="l">{sp}</td><td class="l">{un}</td></tr>'
                    for c, n, new, book, opp, tot, sp, un in tank_rows())
    tanks = f'''<div class="tbl"><table class="mk"><thead><tr><th>Konf.</th><th class="l">Nádrže</th><th>Nové výdaje</th><th>Skladové díly (účetně)</th>
<th>Ztráta prodejní hodnoty</th><th>Ekonomická hodnota</th><th class="l">Prostor a hydraulika</th><th class="l">Univerzálnost</th></tr></thead><tbody>{trows}</tbody></table></div>'''

    hpb = T[('U', 'B-2')]
    return f'''<h2><span class="no">14</span>Investiční rozpočet</h2>
<p><b>Hydraulika podle rozhodnutí zadavatele (16. 10. 2026): bez hydraulického separátoru a deskového výměníku.</b> Jednotky jsou napojeny přímo na AKU, která slouží jako separátor. Celá soustava je na vodu, ochranu proti zamrznutí zajišťují protimrazové ventily, uzávěry s pružinovým návratem a UPS pro čerpadla. Návod RH X50 přesto pod 0 °C požaduje glykol (kap. 01); bez písemného souhlasu výrobce zůstává riziko záruky. Úspora za separátor, výměník, primární čerpadlo a glykol (≈ 99 tis. Kč) se ale spotřebuje na protimrazové jištění vody: u 3 jednotek vychází vodní varianta o ≈ {f0(-GLYCOL_DELTA)} Kč dráž než glykolová, u 5 jednotek o ≈ 40 tis. Kč. Finančně tedy vynechání výměníku nic nepřináší.</p>
<p>Položkový rozpočet kontejnerové kotelny ve dvou provedeních a pro dvě sestavy tepelných čerpadel. Vše bez DPH. Zdroj ceny: {SRC["T✓"]} ověřeno na webu prodejce, {SRC["T"]} z rešerše trhu (kap. 13), {SRC["Z"]} sděleno zadavatelem, {SRC["O"]} vlastní odhad k poptání. Většina položek technologie jsou odhady; přesnost rozpočtu je proto řádově ±20 %.</p>
<div class="cols">
<div><h3>Ekonomická varianta</h3><ul class="plain">
<li>Použitý kontejner 20′, skladové AKU 2× 300 + 500 l a TUV 3× 300 l (nádrže konfigurace A).</li>
<li>Výměník 70 kW, jedno sekundární čerpadlo, jednodušší PLC, jen hadice DN50.</li>
<li>Pokryje zakázky do ≈ 70 kW. Pro 100 kW nebo Δt 5 K by bylo nutné dokoupit DN65 a větší výměník.</li>
</ul></div>
<div><h3>Univerzální varianta</h3><ul class="plain">
<li>Nový kontejner 20′ s CSC, nová AKU 1 000 l, TUV 3× 300 l ze skladu (konfigurace B), rám připravený na TUV 1 000 l.</li>
<li>Výměník 100 kW, zdvojené sekundární čerpadlo, plná kaskádová regulace s dálkovým dohledem, hadice DN50 i DN65.</li>
<li>Zvládne všechny sestavy z kap. 04 až do 2× RH X50.</li>
</ul></div>
</div>

<h3>Souhrn</h3>
{summary}
<div class="cols">
<div><h3>Jak číst souhrn</h3><ul class="plain">
<li><b>A</b> jsou peníze, které je nutné skutečně zaplatit. Rozdíl mezi ekonomickou a univerzální variantou je ≈ {f0(T[("U", "B-2")]["new"] - T[("E", "B-2")]["new"])} Kč.</li>
<li><b>B</b> oceňuje vlastní tepelná čerpadla a nádrže nákupní cenou: RH X50 cenou sdělenou zadavatelem, RH050/060 cenou EXW × kurz {str(FX_USD).replace(".", ",")} Kč/USD × {str(LANDED).replace(".", ",")} na dopravu a clo.</li>
<li><b>C′</b> přičítá alternativní náklad: jednotky a zásobníky po prvním pronájmu nepůjdou prodat jako nové. Při odhadu prodejní hodnoty {int(USED_SHARE * 100)} % ceny nového je to u sestavy 2× RH X50 největší položka celé investice (≈ {f0(hpb["opp"])} Kč). Platí jen tehdy, když by se jednotky jinak skutečně prodaly.</li>
<li><b>Opotřebení za sezónu</b> rozkládá nové výdaje a účetní hodnotu skladových dílů do životnosti: kontejner, konstrukce a nádrže 10 sezón, hydraulika, elektro a TČ 8, regulace 6, hadice 4 [ODHAD]. Slouží jako vstup do ekonomiky zakázky (fáze 5).</li>
</ul></div>
<div><h3>Hlavní závěry</h3><ul class="plain">
<li>Nové výdaje na kontejner s technologií vycházejí na ≈ {f0(T[("E", "A-50")]["new"] // 1000 * 1000)}–{f0(T[("U", "B-2")]["new"] // 1000 * 1000)} Kč. Rozhodující jsou práce, regulace a hydraulika, ne kontejner a nádrže.</li>
<li>Sestava z malých jednotek (A-50) stojí v nových výdajích zhruba stejně jako 2× RH X50: víc jednotek znamená víc rámů, hadic a protimrazových armatur, RH X50 zase potřebuje externí čerpadla. Ztráta prodejní hodnoty jednotek je u A-50 nižší, výkon v mrazu ale také (kap. 04).</li>
<li>Nová AKU 1 000 l je levná i při realistické ceně 20–25 tis. Kč. Zjednoduší hydrauliku a uvolní 2–3 skladové nádrže k prodeji jako nové.</li>
<li>Nový TUV 1 000 l (65 000 Kč) vychází nejlépe jen při započtení ztráty prodejní hodnoty zásobníků 300 l, tedy když je opravdu jde prodat jako nové. Jinak stačí konfigurace B s rámem připraveným na pozdější záměnu.</li>
</ul></div>
</div>

<h3>A · Kontejner a technologie, položkově</h3>
{items_a}
<h3>A · Výdaje navázané na venkovní jednotky</h3>
{items_u}
<h3>B · Skladové díly</h3>
{items_b}
<p class="note">Účetní a prodejní hodnoty zásobníků vlastní výroby a skladových AKU jsou odhad. Doplňte prosím skutečné náklady a ceníkové ceny; rozpočet se přepočte (<code>src/rozpocet.py</code>).</p>
<h3>Konfigurace nádrží A / B / C</h3>
<p>Porovnání podle zadání (kap. 5): nové výdaje, vázaná skladová hodnota a ztráta prodejní hodnoty zásobníků. Nová AKU 1 000 l počítána za 5 000 Kč (Z) + izolace 9 000 Kč (O).</p>
{tanks}
'''


def build():
    out = Path(__file__).with_name('budget.html')
    out.write_text(html(), encoding='utf-8')
    return out


if __name__ == '__main__':
    print(build())
    for v in 'EU':
        for c in HP_CONFIGS:
            t = totals(v, c)
            print(v, c, {k: round(x) for k, x in t.items()})
    for r in tank_rows():
        print(r[:6])
