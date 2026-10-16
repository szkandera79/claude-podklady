#!/usr/bin/env python3
"""Ekonomika zakázky mobilní kotelny (fáze 5) — vstupy z rozpocet.py, výstup src/econ.html (kap. 15 studie).

Předpoklad: jedna šestiměsíční zakázka za rok (topná sezóna). Elektřinu hradí zákazník.
Přímé náklady zakázky jsou vlastní odhady [O], ceny dopravy vycházejí z rešerše (30–50 Kč/km).
"""
from pathlib import Path
import rozpocet as R
import studie_calc as C

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
