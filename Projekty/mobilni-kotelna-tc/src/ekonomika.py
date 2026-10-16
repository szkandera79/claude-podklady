#!/usr/bin/env python3
"""Ekonomika zakázky mobilní kotelny (fáze 5) — vstupy z rozpocet.py, výstup src/econ.html (kap. 15 studie).

Předpoklad: jedna šestiměsíční zakázka za rok (topná sezóna). Elektřinu hradí zákazník.
Přímé náklady zakázky jsou vlastní odhady [O], ceny dopravy vycházejí z rešerše (30–50 Kč/km).
"""
from pathlib import Path
import rozpocet as R
import studie_calc as C
import model as M

# --- celkové náklady zákazníka: nájem + energie (orientačně, bez DPH) ---
DESIGN_KW = 50
SEASON_SHARE = 0.80          # podíl říjen–březen na roční potřebě tepla [ODHAD]
Q6 = sum(DESIGN_KW * min(1, max(0, (20 - t) / 35)) * h for t, h in M.bins().items()) / 1000 * SEASON_SHARE  # MWh
SPF_HI, SPF_LO = M.SPF_CALC, M.SPF_W55                       # ekviterm 50/35 vs. trvale 55 °C
# Tržní ceny k 16. 10. 2026, bez DPH (zdroje v SOURCES):
#  nafta: ČSÚ 41. týden 47,74 Kč/l s DPH → 39,5 bez DPH
#  LTO: nafta − spotřební daň 8,01 + daň LTO po vrácení 0,66 ≈ 32 Kč/l (koncové ceny 32–38 s DPH, nedatované)
#  LPG pro vytápění (propan): 2,4–2,9 Kč/kWh s DPH → ≈ 2,2 bez DPH × 6,6 kWh/l ≈ 15 Kč/l (autoplyn 21,75 s DPH neplatí)
#  elektřina pro firmy: jednotarif 5,6–6,6 Kč/kWh s DPH (E.ON, PRE, ČEZ 2026) → ≈ 5,0 bez DPH; rozpětí 4,5–5,5
PRICES = dict(el=5.0, diesel=39.5, lto=32.0, lpg=15.0)  # Kč/kWh, Kč/l
SOURCES = [
    ('ČSÚ přes wattbox.cz: nafta 47,74 Kč/l s DPH, 41. týden 2026', 'https://wattbox.cz/ceny-paliv'),
    ('TZB-info: ceny elektřiny 2026 (E.ON, PRE, ČEZ)', 'https://www.tzb-info.cz/ceny-paliv-a-energii/14-ceny-elektriny'),
    ('CALPG: propan pro vytápění ≈ 2,90 Kč/kWh s DPH', 'https://calpg.cz/kolik-stoji-prechod-na-propanove-vytapeni/'),
    ('NRG: koncová cena LTO ≈ 38 Kč/l (nedatováno)', 'https://www.nrg.cz/nebojme-se-lehkych-topnych-oleju/'),
    ('e-genergie: spotřební daň a vratka u LTO', 'https://www.egenergie.com/ropne-produkty/extra-lehky-topny-olej/'),
]
ALTS = [  # (název, Kč za kWh paliva, kWh v litru, účinnost, nájem/měs nízký–vysoký, jednorázově)
    ('Nafta, mobilní kotelna', 39.5, M.OIL_KWH_L, M.OIL_EFF, (35_000, 60_000), 25_000),
    ('LTO, mobilní kotelna', 32.0, M.OIL_KWH_L, M.OIL_EFF, (35_000, 60_000), 25_000),
    ('LPG, kontejner + nádrž', 15.0, M.LPG_KWH_L, M.GAS_EFF, (35_000, 60_000), 35_000),
]

MONTHS = 6
INSTALL_FEE, REMOVAL_FEE = 50_000, 40_000     # zadavatel
RENTS = (50_000, 70_000, 90_000)
CAPITAL_RATE = 0.06                           # alternativní výnos vázaného kapitálu p. a. [ODHAD]

# přímé náklady jedné zakázky do 100 km [O]
DIRECT = [
    ('Doprava tam: kontejner (ruka) + jednotky (valník s rukou)', 20_000),
    ('Instalace u zákazníka: 2 technici × 2 dny, elektrikář, revize', 43_000),
    ('Spotřební materiál instalace: přechody, těsnění, inhibitor', 8_000),
    ('Servis: 6 prohlídek po ≈ 4 h + cesta', 25_000),
    ('Vzdálený dohled, LTE, cloud (6 měsíců)', 3_000),
    ('Rezerva na poruchy a náhradní díly', 15_000),
    ('Pojištění zařízení (pokud ho nehradí nájemce)', 8_000),
    ('Demontáž, vypuštění, doprava zpět', 41_000),
    ('Příprava mezi nájmy: čištění, filtry, kontrola, revize', 15_000),
    ('Obhlídka, nabídka, smlouva', 8_000),
]
DIRECT_SUM = sum(v for _, v in DIRECT)

SETUPS = [('U', 'B-2'), ('U', 'A-50'), ('E', 'B-2')]


def guaranteed_kw(cfg):
    units = R.HP_CONFIGS[cfg][1][:-1]          # bez jednotky TUV
    return sum(C.cap(u, 55, -15) for u in units)


def calc(v, cfg, rent):
    t = R.totals(v, cfg)
    revenue = MONTHS * rent + INSTALL_FEE + REMOVAL_FEE
    gross = revenue - DIRECT_SUM
    capital = CAPITAL_RATE * (t['new'] + t['book'])
    econ = gross - t['wear'] - capital
    first = econ - t['opp']
    payback = t['new'] / gross if gross > 0 else float('inf')
    cum = [n * gross - t['new'] for n in (1, 2, 3)]
    return dict(t=t, revenue=revenue, gross=gross, capital=capital, econ=econ, first=first, payback=payback, cum=cum)


def breakeven(v, cfg):
    t = R.totals(v, cfg)
    capital = CAPITAL_RATE * (t['new'] + t['book'])
    base = DIRECT_SUM - INSTALL_FEE - REMOVAL_FEE
    return dict(
        cash=base / MONTHS,                                         # pokryje přímé náklady
        econ=(base + t['wear'] + capital) / MONTHS,                 # ekonomicky nulový výsledek
        pay3=(base + t['new'] / 3) / MONTHS,                        # nové výdaje zpět za 3 zakázky
        pay1=(base + t['new']) / MONTHS,                            # nové výdaje zpět za 1 zakázku
    )


def f0(x):
    return f'{x:,.0f}'.replace(',', ' ').replace('-', '−')


def f1(x):
    return f'{x:.1f}'.replace('.', ',')


def cls(x):
    return 'ok' if x >= 0 else 'bad'


def html():
    name = {'E': 'Ekonomická', 'U': 'Univerzální'}
    # přímé náklady
    drows = ''.join(f'<tr><td class="l">{n}</td><td>{f0(v)}</td></tr>' for n, v in DIRECT)
    direct = f'''<div class="tbl narrow"><table class="mk"><thead><tr><th class="l">Přímé náklady jedné zakázky [O]</th><th>Kč</th></tr></thead>
<tbody>{drows}<tr class="sum"><th scope="row" class="l">Celkem</th><td class="hl">{f0(DIRECT_SUM)}</td></tr></tbody></table></div>'''

    # scénáře
    blocks = ''
    for v, cfg in SETUPS:
        head = ''.join(f'<th>{f0(r // 1000)} tis./měs.</th>' for r in RENTS)
        res = [calc(v, cfg, r) for r in RENTS]
        def row(label, fn, c=False, strong=False):
            cells = ''.join(f'<td class="{(cls(fn(x)) if c else "")} {"hl" if strong else ""}">{f0(fn(x))}</td>' for x in res)
            return f'<tr class="{"sum" if strong else ""}"><th scope="row" class="l">{label}</th>{cells}</tr>'
        t = res[0]['t']
        blocks += f'''<h3>{name[v]} kontejner · {cfg} ({R.HP_CONFIGS[cfg][0]}), {f1(guaranteed_kw(cfg))} kW při −15 °C / W55</h3>
<div class="tbl"><table><thead><tr><th class="l">Kč bez DPH na jednu zakázku</th>{head}</tr></thead><tbody>
{row('Tržby (6× nájem + 50 tis. instalace + 40 tis. demontáž)', lambda x: x['revenue'])}
{row('Přímé náklady zakázky', lambda x: -DIRECT_SUM)}
{row('Hrubý příspěvek zakázky', lambda x: x['gross'], True, True)}
{row(f'Opotřebení za sezónu', lambda x: -x['t']['wear'])}
{row(f'Kapitálový náklad {int(CAPITAL_RATE * 100)} % z vázaných {f0(t["new"] + t["book"])} Kč', lambda x: -x['capital'])}
{row('Ekonomický výsledek 2. a dalších zakázek', lambda x: x['econ'], True, True)}
{row(f'Ztráta prodejní hodnoty skladových dílů (jen 1. zakázka)', lambda x: -x['t']['opp'])}
{row('Ekonomický výsledek 1. zakázky', lambda x: x['first'], True, True)}
{row(f'Kumulovaná hotovost po 1. zakázce (nové výdaje {f0(t["new"])} Kč)', lambda x: x['cum'][0], True)}
{row('Kumulovaná hotovost po 2. zakázce', lambda x: x['cum'][1], True)}
{row('Kumulovaná hotovost po 3. zakázce', lambda x: x['cum'][2], True)}
{row('Návratnost nových výdajů (počet zakázek)', lambda x: x['payback'] * 1000)}
</tbody></table></div>'''
    blocks = blocks.replace('<td class=" ">', '<td>')
    # návratnost: zobrazit jako desetinné číslo
    import re
    blocks = re.sub(r'(<th scope="row" class="l">Návratnost nových výdajů \(počet zakázek\)</th>)((?:<td[^>]*>[^<]*</td>)+)',
                    lambda m: m.group(1) + re.sub(r'>(−?[\d ]+)<', lambda n: '>' + f'{int(n.group(1).replace(" ", "")) / 1000:.1f}'.replace('.', ',') + '<', m.group(2)), blocks)

    # body zvratu
    brows = ''
    for v, cfg in SETUPS:
        b = breakeven(v, cfg)
        kw = guaranteed_kw(cfg)
        brows += (f'<tr><th scope="row" class="l">{name[v]} · {cfg}</th><td>{f0(b["cash"])}</td><td>{f0(b["econ"])}</td>'
                  f'<td>{f0(b["pay3"])}</td><td>{f0(b["pay1"])}</td><td>{f0(70_000 / kw)}</td></tr>')
    be = f'''<div class="tbl"><table><thead><tr><th class="l">Měsíční nájem (Kč) potřebný, aby…</th><th>pokryl přímé náklady</th>
<th>dal ekonomickou nulu (vč. opotřebení a kapitálu)</th><th>vrátil nové výdaje za 3 zakázky</th><th>vrátil nové výdaje za 1 zakázku</th>
<th>70 tis. Kč na garantovaný kW</th></tr></thead><tbody>{brows}</tbody></table></div>'''

    ub = calc('U', 'B-2', 70_000)
    ua = calc('U', 'A-50', 70_000)
    b2 = breakeven('U', 'B-2')
    return f'''<h2><span class="no">15</span>Ekonomika zakázky</h2>
<p>Jedna zakázka = šestiměsíční pronájem v topné sezóně, tedy zpravidla jedna zakázka za rok. Elektřinu hradí zákazník. Rozpočet a opotřebení z kap. 14 (hydraulika bez separátoru a výměníku), přímé náklady zakázky jsou vlastní odhad do 100 km. Kladná čísla zeleně, záporná červeně.</p>
{tco_html()}
<h3>Ekonomika pro REO HEATING</h3>
{direct}
{blocks}
<h3>Bod zvratu</h3>
{be}
<p class="note">Srovnání s trhem (kap. 13): ENERENT pronajímá TČ 105 kW nominálně za ≈ 46–51 tis. Kč/měs. Při −15 °C bude jeho výkon zhruba poloviční (≈ 50 kW, [ODHAD]), tedy ≈ 950 Kč za garantovaný kW. Olejové a plynové kotelny 50–110 kW stojí 35–67 tis. Kč/měs. a jejich výkon na teplotě nezávisí.</p>
<div class="cols">
<div><h3>Závěry</h3><ul class="plain">
<li><b>První zakázka investici nezaplatí při žádném z nájmů.</b> Při 70 tis. Kč/měs. dá hrubý příspěvek ≈ {f0(ub["gross"])} Kč proti novým výdajům ≈ {f0(ub["t"]["new"])} Kč. Nové výdaje se vrátí za ≈ {f1(ub["payback"])} zakázky, tedy zhruba {f1(ub["payback"])} roku při jedné zakázce ročně.</li>
<li>Při 50 tis. Kč/měs. je návratnost ≈ {f1(calc("U", "B-2", 50_000)["payback"])} zakázky, při 90 tis. ≈ {f1(calc("U", "B-2", 90_000)["payback"])}. Ekonomicky nulový výsledek (vč. opotřebení a kapitálu) dává nájem ≈ {f0(b2["econ"])} Kč/měs.</li>
<li>Každá další zakázka přinese ≈ {f0(ub["gross"])} Kč hrubého příspěvku, ale po třech zakázkách při 70 tis. Kč/měs. zbývá ještě ≈ {f0(ub["cum"][2])} Kč nesplacených nových výdajů. <b>Při jedné zakázce ročně je podnikatelský případ slabý</b>; vyžaduje druhé nasazení v roce, delší pronájmy, nebo levnější provedení (ekonomická varianta: návratnost ≈ {f1(calc("E", "B-2", 70_000)["payback"])} zakázky).</li>
<li>Ztráta prodejní hodnoty dvou RH X50 (≈ {f0(ub["t"]["opp"])} Kč) je skutečný náklad jen tehdy, když by se jednotky jinak prodaly. Pokud leží na skladu bez kupce, je lepší je pronajímat.</li>
<li>Sestava A-50 má podobné náklady, ale menší garantovaný výkon ({f1(guaranteed_kw("A-50"))} kW proti {f1(guaranteed_kw("B-2"))} kW), takže za stejné nájemné nabízí zákazníkovi méně.</li>
</ul></div>
<div><h3>Je cena 70 tis. Kč/měs. konkurenceschopná?</h3><ul class="plain">
<li>Pro zakázku ≈ 50 kW při −15 °C (2× RH X50) vychází ≈ {f0(70_000 / guaranteed_kw("B-2"))} Kč za garantovaný kW, tedy ≈ 1,5× nad ENERENT a na horní hranici olejových kotelen. Obhajitelné u zákazníka, který chce bezemisní zdroj bez paliva a obsluhy; jinak vyjednávací prostor dolů k ≈ 55–60 tis.</li>
<li>Pro malou zakázku do ≈ 25 kW (jedna RH X50) je 70 tis. Kč/měs. výrazně nad trhem. Vhodnější je cena podle garantovaného výkonu, např. 40–45 tis. Kč/měs.</li>
<li>Poplatky 50 + 40 tis. Kč za instalaci a demontáž kryjí přímé náklady na dopravu, instalaci a demontáž (≈ {f0(20_000 + 43_000 + 8_000 + 41_000)} Kč) jen částečně.</li>
<li>Ekonomiku nejvíc zlepší druhé nasazení v roce (jaro/léto: TUV, technologické teplo, chlazení u RH X50) nebo delší pronájem; každý další měsíc nájmu přináší ≈ 65 tis. Kč příspěvku při 70 tis. nájmu.</li>
</ul></div>
</div>
'''


def tco_html():
    q = Q6 * 1000                                   # kWh tepla za 6 měsíců
    hp_kwh = (q / SPF_HI, q / SPF_LO)
    hp_cost = tuple(x * PRICES['el'] for x in hp_kwh)
    ours = MONTHS * 70_000 + INSTALL_FEE + REMOVAL_FEE
    rows = (f'<tr class="grp"><th scope="row" class="l">TČ REO HEATING (nájem 70 tis.)</th><td>{f0(hp_kwh[0])}–{f0(hp_kwh[1])} kWh el.</td>'
            f'<td>{f1(1 / SPF_HI)}–{f1(1 / SPF_LO)}</td><td>{f0(hp_cost[0])}–{f0(hp_cost[1])}</td><td>{f0(ours)}</td>'
            f'<td class="hl">{f0(ours + hp_cost[0])}–{f0(ours + hp_cost[1])}</td></tr>')
    alt_lines = []
    for name, price, kwh_l, eff, (rlo, rhi), once in ALTS:
        litres = q / (kwh_l * eff)
        cost = litres * price
        rent = (MONTHS * rlo + once, MONTHS * rhi + once)
        save = (cost - hp_cost[1], cost - hp_cost[0])
        alt_lines.append((name, cost, save))
        rows += (f'<tr><th scope="row" class="l">{name}</th><td>{f0(litres)} l</td><td>{f1(1 / eff)}</td><td>{f0(cost)}</td>'
                 f'<td>{f0(rent[0])}–{f0(rent[1])}</td><td class="hl">{f0(rent[0] + cost)}–{f0(rent[1] + cost)}</td></tr>')
    d = alt_lines[0]
    be_rows = ''
    BE = {}
    for name, price, kwh_l, eff, (rlo, rhi), once in ALTS:
        cost = q / (kwh_l * eff) * price
        cells = ''
        for r in (rlo, rhi):
            alt_total = MONTHS * r + once + cost
            lo = (alt_total - INSTALL_FEE - REMOVAL_FEE - hp_cost[1]) / MONTHS
            hi = (alt_total - INSTALL_FEE - REMOVAL_FEE - hp_cost[0]) / MONTHS
            BE[(name.split(',')[0], r)] = (lo, hi)
            cells += f'<td class="{"ok" if hi >= 70_000 else ("warn" if hi >= 55_000 else "bad")}">{f0(lo)}–{f0(hi)}</td>'
        be_rows += f'<tr><th scope="row" class="l">{name}</th>{cells}</tr>'
    be = f'''<div class="tbl"><table><thead><tr><th class="l">Konkurence</th><th>její nájem 35 tis./měs.</th><th>její nájem 60 tis./měs.</th></tr></thead>
<tbody>{be_rows}</tbody></table></div>'''
    per_h_el = (DESIGN_KW / SPF_HI, DESIGN_KW / SPF_LO)
    per_h_l = DESIGN_KW / (M.OIL_KWH_L * M.OIL_EFF)
    return f'''<h3>Hlavní prodejní argument: celkové náklady zákazníka (nájem + energie)</h3>
<p>Olejovou nebo plynovou kotelnu nelze srovnávat jen nájmem: zákazník u ní platí i palivo, a to je největší položka. Modelový objekt se ztrátou {DESIGN_KW} kW při −15 °C potřebuje za 6 měsíců topné sezóny ≈ {f0(Q6)} MWh tepla [ODHAD]. Ceny bez DPH: elektřina {f1(PRICES["el"])} Kč/kWh, nafta {f1(PRICES["diesel"])} Kč/l (ČSÚ 47,74 Kč/l s DPH), LTO {f0(PRICES["lto"])} Kč/l, propan pro vytápění {f0(PRICES["lpg"])} Kč/l; tržní ceny k 16. 10. 2026, zdroje pod tabulkou. V nabídce vždy nahradit cenami z faktur zákazníka. Sezónní topný faktor TČ {f1(SPF_LO)} (trvale 55 °C) až {f1(SPF_HI)} (ekvitermně 50/35 °C), vypočtený z výkonových map RH X50.</p>
<div class="tbl"><table><thead><tr><th class="l">6 měsíců, Kč bez DPH</th><th>Spotřeba energie</th><th>kWh vstupu na 1 kWh tepla</th><th>Náklady na energii</th><th>Nájem + doprava a montáž</th><th>Celkem</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="note">Zdroje cen: {" · ".join(f'<a href="{u}">{t}</a>' for t, u in SOURCES)}.</p>
<h3>Do jakého nájmu jsme pro zákazníka celkově levnější</h3>
<p>Měsíční nájem TČ (Kč bez DPH, s poplatky 50 + 40 tis.), při kterém jsou celkové náklady zákazníka za 6 měsíců stejné jako u konkurenční kotelny včetně paliva. Rozpětí odpovídá topnému faktoru {f1(SPF_LO)}–{f1(SPF_HI)}. Zelená: 70 tis. Kč je pod hranicí, takže TČ vyjde levněji.</p>
{be}
<div class="cols">
<div><h3>Co říct zákazníkovi předem</h3><ul class="plain">
<li><b>Nájem je vyšší, provoz levnější.</b> Při výkonu {DESIGN_KW} kW spotřebuje TČ ≈ {f0(per_h_el[0])}–{f0(per_h_el[1])} kWh elektřiny za hodinu (≈ {f0(per_h_el[0] * PRICES["el"])}–{f0(per_h_el[1] * PRICES["el"])} Kč), naftová kotelna ≈ {f1(per_h_l)} l nafty (≈ {f0(per_h_l * PRICES['diesel'])} Kč).</li>
<li>Na 1 kWh tepla potřebuje TČ {f1(1 / SPF_HI)}–{f1(1 / SPF_LO)} kWh elektřiny, naftová kotelna {f1(1 / M.OIL_EFF)} kWh v naftě. <b>Energie spotřebuje 2–3× méně.</b></li>
<li>Protože kWh elektřiny je dražší než kWh v naftě, je úspora v penězích menší než úspora energie: za sezónu ≈ {f0(d[2][0])}–{f0(d[2][1])} Kč proti naftě, tedy o ≈ {f0((1 - hp_cost[1] / d[1]) * 100)}–{f0((1 - hp_cost[0] / d[1]) * 100)} % nižší náklady na energii.</li>
<li>Další výhody bez paliva: žádné dovozy nafty a hlídání nádrže, žádné spaliny a zápach u budovy, nižší hluk, žádné riziko úniku paliva.</li>
</ul></div>
<div><h3>Kde jsou meze argumentu</h3><ul class="plain">
<li>Proti <b>naftě</b> za 60 tis. Kč/měs. obstojí nájem 70 tis. Kč vždy (hranice {f0(BE[('Nafta', 60_000)][0])}–{f0(BE[('Nafta', 60_000)][1])} Kč). Proti levné naftové kotelně za 35 tis. Kč/měs. je hranice {f0(BE[('Nafta', 35_000)][0])}–{f0(BE[('Nafta', 35_000)][1])} Kč, tam je potřeba jít s nájmem k 55–65 tis.</li>
<li>Proti <b>LTO</b> jen proti dražší konkurenci ({f0(BE[('LTO', 60_000)][0])}–{f0(BE[('LTO', 60_000)][1])} Kč). Nejtěžším soupeřem je <b>propan</b> ve vlastní nádrži: hranice jen {f0(BE[('LPG', 35_000)][0])}–{f0(BE[('LPG', 60_000)][1])} Kč, tam úspora na energii vyšší nájem nevyrovná.</li>
<li>Úspora silně závisí na teplotě vody: při soustavě 90/70, kde TČ jede trvale na 55 °C a výš, se blíží spodní hranici.</li>
<li>Úsporu nabízet jen „orientačně, podle cen energie zákazníka“, ne jako garanci. Do každé nabídky dosadit skutečné ceny elektřiny a paliva zákazníka.</li>
</ul></div>
</div>'''


def build():
    out = Path(__file__).with_name('econ.html')
    out.write_text(html(), encoding='utf-8')
    return out


if __name__ == '__main__':
    build()
    for v, cfg in SETUPS:
        for r in RENTS:
            x = calc(v, cfg, r)
            print(v, cfg, r, {k: round(x[k]) for k in ('revenue', 'gross', 'econ', 'first')}, 'payback', round(x['payback'], 2), [round(c) for c in x['cum']])
        print('breakeven', {k: round(b) for k, b in breakeven(v, cfg).items()}, 'kW', round(guaranteed_kw(cfg), 1))
    print('direct', DIRECT_SUM)
