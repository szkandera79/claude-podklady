#!/usr/bin/env python3
"""Generuje mobilni-kotelna-tc/studie.html (studie proveditelnosti, fáze 1) z výpočtů ve studie_calc.py.

Spuštění z kořene repozitáře: python3 mobilni-kotelna-tc/src/build_studie.py
"""
from pathlib import Path
import studie_calc as C

OUT = Path(__file__).resolve().parent.parent / 'studie.html'


def f1(x):
    return f'{x:.1f}'.replace('.', ',')


def f0(x):
    return f'{x:,.0f}'.replace(',', ' ')


def tc(t):
    return f'{t:+d}'.replace('-', '−') if isinstance(t, int) else f1(t).replace('-', '−')


UNIT_NAME = {'RH050': 'RH050', 'RH060': 'RH060', 'RHX50': 'RH X50'}


def units_str(units):
    out, seen = [], []
    for u in units:
        if u not in seen:
            seen.append(u)
    for u in seen:
        n = units.count(u)
        out.append(f'{n}× {UNIT_NAME[u]}' if n > 1 else UNIT_NAME[u])
    return ' + '.join(out)


# ---------------------------------------------------------------- tabulky
def t_units():
    h = ''.join(f'<th>A{tc(t)}</th>' for t in C.T_SHOW)
    rows = ''
    for m, tw, vals in C.unit_table():
        first = tw == 35
        name = f'<th rowspan="3" scope="rowgroup">{UNIT_NAME[m]}<span class="sub">„nominál“ {f1(C.NOM[m])} kW</span></th>' if first else ''
        cells = ''.join(f'<td class="{ "warn" if (t <= -15) else "" }">{f1(v)}</td>' for t, v in zip(C.T_SHOW, vals))
        rows += f'<tr class="{ "grp" if first else "" }">{name}<td class="tw">W{tw}</td>{cells}</tr>'
    return f'''<div class="tbl"><table><thead><tr><th>Jednotka</th><th>Voda</th>{h}</tr></thead>
<tbody>{rows}</tbody></table></div>'''


def t_cascades():
    rows = ''
    r45 = {r['code']: r for r in C.cascade_rows(45)}
    for r in C.cascade_rows(55):
        a = r45[r['code']]
        p, i = C.electro(r['units'] + [r['tuv']])
        b = C.breaker(i)
        res = f' <span class="tag">z toho {UNIT_NAME[r["reserve"]]} rezerva</span>' if r['reserve'] else ''
        n1 = '—' if r['n1'][3] == 0 else f'{f1(r["n1"][3])} / {f1(r["n1"][4])}'
        rows += f'''<tr><th scope="row">{r["code"]}</th><td class="l">{units_str(r["units"])}{res}</td>
<td>{f1(r["nom"])}</td><td>{f1(a["caps"][3])}</td><td class="hl">{f1(r["caps"][3])}</td><td>{f1(r["caps"][4])}</td>
<td class="hl">{n1}</td><td>{len(r["units"]) + 1}</td><td>{f0(i)} A / {b} A</td></tr>'''
    return f'''<div class="tbl"><table><thead><tr><th>Kód</th><th class="l">Jednotky pro vytápění</th><th>Nominál A7/W35</th>
<th>−15 °C W45</th><th>−15 °C W55</th><th>−20 °C W55</th><th>Po výpadku největší jednotky −15/−20 °C W55</th>
<th>Jednotek celkem (+ TUV)</th><th>Proud / jistič</th></tr></thead><tbody>{rows}</tbody></table></div>'''


def t_balance():
    loads = (30, 40, 50, 70)
    head = ''.join(f'<th>ztráta {p} kW</th>' for p in loads)
    rows = ''
    for code, name, units, res, tuv in C.CASCADES:
        allu = units + ([res] if res else [])
        cells = ''
        for p in loads:
            t = C.balance_point(allu, p, 55)
            cls = 'ok' if t <= -15 else ('warn' if t <= -10 else 'bad')
            cells += f'<td class="{cls}">{tc(t)} °C</td>'
        rows += f'<tr><th scope="row">{code}</th><td class="l">{units_str(allu)}</td>{cells}</tr>'
    return f'''<div class="tbl"><table><thead><tr><th>Kód</th><th class="l">Sestava (všechny jednotky v provozu)</th>{head}</tr></thead>
<tbody>{rows}</tbody></table></div>'''


def t_supply():
    rows = ''
    for sys in ((90, 70), (80, 60), (75, 65), (70, 55), (55, 45)):
        cells = ''
        for tmax in (55, 60, 70):
            t = C.limit_temp(*sys, tmax)
            cls = 'ok' if t <= -15 else ('warn' if t <= -5 else 'bad')
            cells += f'<td class="{cls}">do {tc(t)} °C</td>'
        share = C.radiator_share(*sys, 55, 45)
        rows += f'<tr><th scope="row">{sys[0]}/{sys[1]} °C</th>{cells}<td>{f0(share * 100)} %</td></tr>'
    return f'''<div class="tbl"><table><thead><tr><th>Návrh otopné soustavy (při −15 °C)</th><th>TČ dodá max. 55 °C</th><th>max. 60 °C (RH050/060)</th>
<th>max. 70 °C (jen RH X50)</th><th>Výkon těles při 55/45 °C vůči návrhu</th></tr></thead><tbody>{rows}</tbody></table></div>'''


def t_tuv():
    rows = ''
    for code, name, vol, area in C.TUV_CONFIGS:
        cells = ''
        for ta in (7, -7, -15):
            hp = C.cap('RH050', 55, ta)
            h, pav, _ = C.tuv_heatup(vol, area, hp)
            cells += f'<td>{f1(h)} h <span class="sub">{f1(pav)} kW</span></td>'
        tmax = C.t_max_reachable(area)
        rows += f'<tr><th scope="row">{code}</th><td class="l">{name}</td><td>{f1(area)}</td>{cells}<td class="warn">{f1(tmax)} °C</td></tr>'
    return f'''<div class="tbl"><table><thead><tr><th>Konf.</th><th class="l">Zásobníky TUV</th><th>Plocha výměníků m²</th>
<th>A+7</th><th>A−7</th><th>A−15</th><th>Max. teplota zásobníku jen z TČ</th></tr></thead><tbody>{rows}</tbody></table></div>'''


def t_hoses():
    rows = ''
    for p, q, dn, v, vals in C.hose_table():
        cls = lambda x: 'bad' if x > 30 else ('warn' if x > 15 else 'ok')
        vcls = 'bad' if v > 1.5 else ('warn' if v > 1.0 else 'ok')
        cells = ''.join(f'<td class="{cls(x)}">{f1(x)}</td>' for x in vals)
        rows += f'<tr class="{ "grp" if dn == 40 else "" }"><th scope="row">{p} kW · {f1(q)} m³/h</th><td>DN{dn}</td><td class="{vcls}">{f1(v)}</td>{cells}</tr>'
    return f'''<div class="tbl"><table><thead><tr><th>Výkon · průtok (Δt 10 K)</th><th>Hadice</th><th>Rychlost m/s</th>
<th>2× 5 m</th><th>2× 10 m</th><th>2× 20 m</th><th>2× 30 m</th></tr></thead><tbody>{rows}</tbody></table></div>'''


def t_buffer():
    rows = ''
    for m in ('RH050', 'RH060', 'RHX50'):
        pmin = C.cap(m, 35, 7, 'MIN')
        rows += f'<tr><th scope="row">{UNIT_NAME[m]}</th><td>{f1(pmin)}</td><td>{f0(C.min_buffer_l(pmin))} l</td></tr>'
    return f'''<div class="tbl narrow"><table><thead><tr><th>Nejmenší běžící jednotka</th><th>Min. výkon A7/W35 kW</th><th>Min. účinný objem AKU</th></tr></thead>
<tbody>{rows}</tbody></table></div>'''


# ---------------------------------------------------------------- obsah
RISKS = [
    ('kritické', 'Teplotní spád otopné soustavy zákazníka',
     'Objekt dosud vytápěla CZT nebo kotelna; tělesa a teplovzdušné jednotky bývají navržené na 90/70 nebo 80/60 °C. '
     'RH050/RH060 dávají max. 60 °C, RH X50 až 78 °C, ale za cenu výkonu i COP.',
     'Při soustavě 90/70 stačí 55 °C jen do +5,5 °C venku; 70 °C z RH X50 do −2,5 °C. Hrozí nedotápění administrativy v mrazech.',
     'Při obhlídce zjistit ekvitermní křivku a skutečné teploty přívodu (záznam předávací stanice). Hala jen temperovat. Návrh dělat na skutečně potřebnou teplotu, ne na nominál.'),
    ('kritické', 'Nominální výkon ≠ výkon v mrazu',
     'Zadání pracuje s kaskádami „50 a 70 kW nominálně“. Při −15 °C a W55 mají jednotky 51–55 % výkonu z A7/W35.',
     'Sestava 2× RH060 + 2× RH050 (73,6 kW nominálně) dá při −15 °C/W55 jen 38 kW, RH X50 jen 24,8 kW.',
     'Kaskádu dimenzovat na tepelnou ztrátu při výpočtové teplotě a požadované teplotě vody. Do smlouvy psát garantovaný výkon při −15 °C a W55.'),
    ('kritické', 'Provoz bez glykolu',
     'Návod RH X50 výslovně požaduje při teplotách pod 0 °C nemrznoucí směs. Mechanické protimrazové ventily při výpadku proudu vypustí vodu, a to i z části soustavy nad nimi.',
     'Riziko ztráty záruky, zamrznutí výměníků jednotek (oprava desítky tisíc Kč na jednotku) a vypuštění soustavy bez obsluhy na místě.',
     'Venkovní primární okruh plnit propylenglykolem 35 % a oddělit deskovým výměníkem v kontejneru. Varianta jen s vodou pouze s písemným souhlasem výrobce a s opatřeními v kap. 7.'),
    ('vysoké', 'Elektrický příkon u zákazníka',
     'Sestavy potřebují 47–79 A na fázi (s jednotkou TUV a pomocnými spotřebiči).',
     'Pokud objekt nemá volný příkon 3× 63–100 A, kotelnu nelze plně provozovat.',
     'Zjistit hlavní jistič, rezervovaný příkon a skutečné maximum odběru. Regulace s omezením příkonu (počet běžících jednotek) jako záloha.'),
    ('vysoké', 'Redundance N+1 platí jen do určité zátěže',
     'Rezervní jednotka je skutečnou rezervou jen tehdy, když zbývající jednotky pokryjí ztrátu při výpočtové teplotě.',
     'U 2× RH X50 a ztráty 50 kW jsou v mrazu potřeba obě jednotky; po poruše jedné zbývá 24,8 kW.',
     'Ve smlouvě a nabídce rozlišit „záložní výkon“ a „garantovaný výkon“. Menší jednotky dávají jemnější odstupňování výpadku (−15 až −30 % místo −50 %).'),
    ('vysoké', 'TUV z RH050 nedosáhne hygienické teploty',
     'RH050 má doporučenou max. teplotu vody 60 °C. Přes trubkový výměník lze zásobník ohřát jen na ≈ 52–53 °C.',
     'Trvalý provoz pod 55 °C zvyšuje riziko legionely; vyhláška 252/2004 Sb. požaduje TUV v místě odběru zpravidla 50–70 °C [OVĚŘIT aktuální znění].',
     'Topná vložka v zásobníku TUV pro týdenní sterilizaci 70 °C (regulace RH ji umí řídit, P17–P20). Malý elektrický dohřev pro TUV je tu oprávněný.'),
    ('vysoké', 'Řízení smíšené kaskády',
     'RH050/RH060 a RH X50 mají odlišné řídicí jednotky. Návody neuvádějí společnou kaskádu ani protokol pro nadřazenou regulaci.',
     'Bez ověřeného rozhraní nelze slíbit automatické převzetí výkonu při poruše.',
     'Nadřazený regulátor (PLC) v kontejneru: povolení chodu a žádaná teplota každé jednotky, čtení poruch. Od výrobce vyžádat Modbus/RS485 mapu a podporu IoT pro všechny tři modely.'),
    ('střední', 'Hydraulika jednotek s vlastním a bez vlastního čerpadla',
     'RH050/RH060 mají vestavěné oběhové čerpadlo (9 a 12 m max.), RH X50 vyžaduje externí čerpadlo řízené jednotkou.',
     'Paralelní čerpadla různých výšek na společném potrubí se navzájem ovlivňují; malá jednotka může mít nedostatečný průtok a hlásit poruchu.',
     'Každá jednotka ve vlastní smyčce k hydraulickému separátoru (rozdělovač s nulovou tlakovou diferencí), zpětná klapka a filtr v každé větvi.'),
    ('střední', 'Bezpečnost R290 a přeprava',
     'Jednotky obsahují propan (RH X50 4 kg). Kontejner obsahuje rozvaděč, tedy možné zdroje vznícení.',
     'Netěsnost u dveří nebo větracích otvorů kontejneru může vytvořit nebezpečnou koncentraci.',
     'Jednotky mimo bezpečnostní zónu otvorů kontejneru [OVĚŘIT vzdálenost v návodu]. Přeprava naplněných jednotek dle ADR (UN 3358) [OVĚŘIT výjimky].'),
    ('střední', 'Hluk',
     'RH X50 má LWA 66 dB při W55 a až 77 dB při max. výkonu; RH050/060 59–62 dB (protokoly TÜV SÜD).',
     'Pětice RH jednotek ≈ 69 dB LWA. U bytové zástavby do ~30 m hrozí překročení nočního limitu 40 dB.',
     'Na obhlídce zjistit vzdálenost chráněných prostor; umístění jednotek odvrátit od zástavby.'),
    ('střední', 'Ceny a stav skladových dílů',
     'AKU 1 000 l za ≈ 5 000 Kč je výrazně pod běžnou cenou nové nádrže s izolací. Použitá jednotka má nejasný stav.',
     'Rozpočet může být podhodnocen.',
     'Ověřit, zda jde o nádrž bez izolace / výprodej; použitou jednotku zkontrolovat a dát do role rezervy.'),
]

CORRECTIONS = [
    ('Kaskády dimenzovat na „50 a 70 kW nominálně“.',
     'Nominál A7/W35 je v mrazu k ničemu. RH060 má 22 kW při A7/W35, ale 11,4 kW při −15/W55.',
     'Navrhovat podle ztráty při −15 °C a skutečné teploty vody. Prodávat výkonové třídy podle garantovaného výkonu (např. „M40 = 40 kW při −15 °C/W55“).'),
    ('RH05 má „přibližně 15 kW“.',
     'Platí jen při A7/W35 (14,8 kW). Při −15 °C/W55 je to 7,6 kW, při −20 °C 6,4 kW.',
     'Pro TUV stačí; jako topný modul počítat 7,6 kW.'),
    ('RH X50 má v mrazu ≈ 25 kW.',
     'Potvrzeno pro −15 °C/W55 (24,8 kW, COP 1,50). Při −20 °C/W55 je to 20,8 kW, při W45 27,3 kW.',
     'Počítat 25 kW při −15 °C/W55 a 21 kW při −20 °C.'),
    ('Voda bez glykolu, ochrana mechanickými protimrazovými ventily.',
     'V rozporu s návodem RH X50. Ventily chrání jen místo, kde jsou osazeny, a při aktivaci vypouštějí soustavu.',
     'Glykol ve venkovním primárním okruhu + deskový výměník. Objem glykolu je malý (≈ 100–200 l směsi), protože AKU zůstává na vodě.'),
    ('Společný venkovní rozdělovač, do kontejneru jen dvě trubky.',
     'Venkovní rozdělovač je velký objem vody v mrazu, další izolovaný díl k přepravě a místo, kde se mísí průtoky jednotek mimo dohled čidel.',
     'Rozdělovač (hydraulický separátor) dát dovnitř kontejneru. Na stěně kontejneru panel rychlospojek, ke každé jednotce krátký pár izolovaných hadic.'),
    ('Rezervní jednotka zajistí redundanci N+1.',
     'Platí jen do zátěže, kterou pokryjí zbývající jednotky. V mrazu je „rezerva“ obvykle potřeba pro základní výkon.',
     'Uvádět dvě čísla: výkon všech jednotek a výkon po výpadku největší jednotky.'),
    ('RH05 ohřeje 1 000 l TUV.',
     'Ohřeje (≈ 3,4–6,1 h z 10 na 50 °C), ale jen na ≈ 52 °C. Omezením je teplota, ne výkon.',
     'Zásobník s topnou vložkou pro sterilizaci, případně ohřev TUV z RH X50 (až 78 °C).'),
    ('Desetistopý kontejner jako levnější alternativa.',
     'Vnitřní půdorys 2,83 × 2,35 m pojme AKU 1 000 l a jeden zásobník TUV, ale ne obsluhovací uličku, rozvaděč a budoucí záměnu 3× 300 l → 1 000 l.',
     'Výchozí řešení 20′. 10′ jen pro nejmenší sestavu (1 jednotka ÚT, 1 zásobník TUV).'),
]

CHECKLIST = [
    ('Tepelná ztráta a spotřeba', [
        'Projektová tepelná ztráta (PENB, projekt ÚT) zvlášť pro administrativu a halu; výpočtová teplota lokality.',
        'Fakturace tepla za 2–3 roky (GJ/měsíc), zvlášť ÚT a TUV, pokud jde. Odhad výkonu: P ≈ Q<sub>ÚT</sub> [kWh] / (D × 24) × (t<sub>i</sub> − t<sub>e</sub>), D = denostupně lokality.',
        'Požadované vnitřní teploty: kanceláře, hala (temperování 10–15 °C?), sklady, šatny.',
        'Provozní doba: směny, víkendy, noční útlum; je přípustný ranní náběh?',
    ]),
    ('Otopná soustava', [
        'Návrhový teplotní spád (90/70, 80/60, 75/65…) a skutečná ekvitermní křivka; foto regulátoru a záznam teplot přívodu při známé venkovní teplotě.',
        'Typ otopných ploch: radiátory, konvektory, teplovzdušné jednotky v hale (typ, výkon, návrhová teplota vody), podlahové topení.',
        'Objem soustavy (odhad), materiál potrubí, stav vody (kal, magnetit), přítomnost glykolu.',
        'Statický tlak a výška objektu, provozní tlak, pojistné ventily a expanze stávající soustavy.',
        'Oběhová čerpadla stávajících okruhů (typ, dopravní výška), směšovací uzly, rozdělovač / hydraulický vyrovnávač.',
        'Místo připojení: sekundár předávací stanice (výměník), rozdělovač, dimenze a závity hrdel, uzavírací armatury, vzdálenost od kontejneru.',
    ]),
    ('Teplá voda', [
        'Počet osob ve směně, sprchy (počet, souběžnost na konci směny), kuchyňky, technologické odběry.',
        'Stávající příprava TUV (v předávací stanici? zásobník, objem), cirkulace (délka, teplota, čerpadlo).',
        'Tlak a kvalita studené vody (tvrdost), místo napojení studené vody, možnost odpadu pro pojistný ventil.',
    ]),
    ('Elektro', [
        'Hlavní jistič objektu, rezervovaný příkon, skutečné čtvrthodinové maximum (faktura / měření).',
        'Volný vývod v rozvaděči: jistič, průřez, vzdálenost ke kontejneru, typ sítě (TN-C-S), zásuvka CEE 63/125 A.',
        'Kdo provede připojení a revizi na straně zákazníka; možnost podružného měření.',
    ]),
    ('Umístění a doprava', [
        'Plocha pro kontejner 20′ (6,1 × 2,4 m) + jednotky s odstupy (sání ≥ 0,5–1 m, výfuk nahoru ≥ 2 m volno); únosnost a rovinnost podkladu.',
        'Příjezd nákladního auta s hydraulickou rukou, nosnost a dosah ruky, sklony, průjezdné výšky, nadzemní vedení.',
        'Odvod kondenzátu z jednotek (v mrazu nesmí tvořit led na komunikaci).',
        'Vzdálenost od oken, dveří, šachet a kanálových vpustí (zóna R290), od hranice pozemku a chráněných prostor (hluk).',
        'Oplocení, zabezpečení, přístup servisu 24/7, mobilní signál pro vzdálený dohled.',
    ]),
    ('Smluvní a provozní', [
        'Důvod a předpokládaná délka odstávky, termín zahájení, kdo je kontaktní osoba pro provoz.',
        'Kdo hradí elektřinu, jak se bude odečítat; pojištění objektu a cizích věcí.',
        'Požadavky BOZP, povolení vjezdu a práce, požadavky hasičů nebo pojišťovny na R290.',
    ]),
]

DOCS_NEEDED = [
    'RH050 a RH060: typové štítky (max. proud, rozběhový proud), zda máte RH050 v 1f nebo 3f provedení, křivky vestavěných čerpadel, min. průtok a nastavení průtokového spínače, vodní objem jednotky.',
    'RH050/RH060: význam parametrů „Jednotky online“ a „Řídicí adresa“ (vestavěná kaskáda?), počet propojitelných jednotek, protokol (RS485/Modbus) a mapa registrů, vstup pro externí povolení chodu, výstup poruchy.',
    'RH X50: tlaková ztráta deskového výměníku při jmenovitém průtoku, min./max. průtok, vodní objem, kaskádní řízení „modulů“ (počet, propojení), Modbus mapa, řízení externího čerpadla.',
    'Pro všechny modely: podpora IoT platformy výrobce, víceuživatelský přístup a poruchová hlášení; povolená koncentrace propylenglykolu a korekce výkonu; zda výkonové mapy zahrnují odtávání.',
    'Hluk při max. výkonu a při nízkých venkovních teplotách (u RH050/060 chybí, viz audit akustiky).',
    'Zásobníky TUV 300 l: výkres (rozměry, hrdla, nátrubek pro topnou vložku, kotevní body), max. tlak, hmotnost, údaje výměníku (objem, tlaková ztráta, výkon dle výrobce).',
    'AKU 300/500 l a nabízená 1 000 l: rozměry s izolací, klopná výška, max. tlak, hrdla, cena a co zahrnuje.',
]

NEXT = [
    ('Fáze 2 · varianty a hydraulika', 'Po obhlídce nebo s modelovými daty: výběr sestavy, hydraulické schéma s dimenzemi, výběr čerpadel, separátoru, výměníku, expanze a pojistných prvků; regulační koncept a seznam signálů.'),
    ('Fáze 3 · konstrukce', 'Půdorys a 3D koncept, nosný rám z profilů, kotvení zásobníků (provozní vs. přepravní zatížení, EN 12195-1: 0,8 g vpřed, 0,5 g do stran), výpis hutního materiálu, rámy jednotek; seznam částí pro autorizovaného statika.'),
    ('Fáze 4 · trh a rozpočet', 'Rešerše kontejnerů 10′/20′, hadic, rychlospojek a armatur u českých dodavatelů s odkazy a cenami; položkový rozpočet A/B/C; cenová mapa pronájmů mobilních kotelen.'),
    ('Fáze 5 · ekonomika a smlouva', 'Ekonomika zakázky 50/70/90 tis. Kč/měsíc, bod zvratu, 2. a 3. pronájem; návrh nájemní smlouvy B2B s vypořádáním předčasného ukončení a jistotou.'),
]


def risks_html():
    out = ''
    for sev, title, why, impact, fix in RISKS:
        out += f'''<article class="risk sev-{ {"kritické": "crit", "vysoké": "high", "střední": "mid"}[sev] }">
<header><span class="pill">{sev}</span><h3>{title}</h3></header>
<dl><dt>Proč</dt><dd>{why}</dd><dt>Dopad</dt><dd>{impact}</dd><dt>Opatření</dt><dd>{fix}</dd></dl></article>'''
    return out


def corrections_html():
    rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in CORRECTIONS)
    return f'''<div class="tbl"><table class="text"><thead><tr><th>Předpoklad zadání</th><th>Zjištění</th><th>Doporučení</th></tr></thead>
<tbody>{rows}</tbody></table></div>'''


def checklist_html():
    out = ''
    for i, (title, items) in enumerate(CHECKLIST):
        lis = ''.join(f'<li><input type="checkbox" id="c{i}_{j}"><label for="c{i}_{j}">{it}</label></li>' for j, it in enumerate(items))
        out += f'<section class="check"><h3>{title}</h3><ul>{lis}</ul></section>'
    return out


SCHEMA = '''<svg viewBox="0 0 960 500" role="img" aria-label="Koncepční hydraulické schéma mobilní kotelny">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--ink-2)"/></marker></defs>
<rect x="250" y="20" width="560" height="460" rx="4" fill="var(--panel)" stroke="var(--ink-2)" stroke-width="1.5" stroke-dasharray="6 4"/>
<text x="262" y="42" class="lbl">KONTEJNER 20′ (technologie, rozvaděč, regulace)</text>
<text x="20" y="42" class="lbl">VENKU · glykol PG 35 %</text>
<text x="830" y="42" class="lbl">ZÁKAZNÍK · voda</text>
<!-- jednotky -->
<g class="unit"><rect x="20" y="70" width="120" height="54" rx="3"/><text x="80" y="93">RH X50</text><text x="80" y="111" class="s">+ ext. čerpadlo</text></g>
<g class="unit"><rect x="20" y="140" width="120" height="44" rx="3"/><text x="80" y="167">RH060</text></g>
<g class="unit"><rect x="20" y="200" width="120" height="44" rx="3"/><text x="80" y="227">RH050 / rezerva</text></g>
<g class="unit tuv"><rect x="20" y="330" width="120" height="54" rx="3"/><text x="80" y="353">RH050 · TUV</text><text x="80" y="371" class="s">samostatný okruh</text></g>
<!-- hadice jednotek -> panel -->
<g class="pipe hot"><path d="M140 85H250"/><path d="M140 152H250"/><path d="M140 212H250"/><path d="M140 345H250"/></g>
<g class="pipe cold"><path d="M140 112H250"/><path d="M140 174H250"/><path d="M140 234H250"/><path d="M140 372H250"/></g>
<text x="150" y="268" class="s l">páry izolovaných hadic,</text><text x="150" y="282" class="s l">rychlospojky, filtr, zpětná</text><text x="150" y="296" class="s l">klapka, uzávěry v každé větvi</text>
<rect x="244" y="70" width="12" height="320" fill="var(--accent)"/><text x="262" y="402" class="s l">panel rychlospojek na stěně</text>
<!-- separátor -->
<g class="pipe hot"><path d="M256 85H300"/><path d="M256 152H300"/><path d="M256 212H300"/></g>
<g class="pipe cold"><path d="M256 112H312"/><path d="M256 174H312"/><path d="M256 234H312"/></g>
<rect x="300" y="70" width="24" height="180" rx="10" class="dev"/><text x="312" y="268" class="s">hydraulický</text><text x="312" y="281" class="s">separátor</text>
<!-- primární čerpadlo + výměník -->
<g class="pipe hot"><path d="M324 95H400" marker-end="url(#ar)"/></g><g class="pipe cold"><path d="M400 215H324"/></g>
<circle cx="370" cy="215" r="11" class="dev"/><path d="M364 209L378 215L364 221z" fill="var(--ink-2)"/><text x="370" y="240" class="s">čerpadlo prim.</text>
<rect x="400" y="80" width="40" height="150" rx="3" class="hx"/><text x="420" y="250" class="s">deskový</text><text x="420" y="263" class="s">výměník</text>
<!-- AKU -->
<g class="pipe hot"><path d="M440 95H500"/></g><g class="pipe cold"><path d="M500 215H440"/></g>
<rect x="500" y="70" width="90" height="170" rx="40" class="tank"/><text x="545" y="150">AKU</text><text x="545" y="168" class="s">1 000 l · voda</text>
<!-- sekundár -->
<g class="pipe hot"><path d="M590 95H820" marker-end="url(#ar)"/></g><g class="pipe cold"><path d="M820 215H590"/></g>
<circle cx="650" cy="95" r="11" class="dev"/><path d="M644 89L658 95L644 101z" fill="var(--ink-2)"/><text x="650" y="76" class="s">čerpadlo sek. (EC)</text>
<rect x="700" y="205" width="26" height="20" class="dev"/><text x="713" y="245" class="s">filtr + odkalovač</text>
<rect x="804" y="70" width="12" height="160" fill="var(--accent)"/>
<text x="830" y="92" class="s l">přívod ÚT</text><text x="830" y="212" class="s l">zpátečka ÚT</text>
<text x="830" y="130" class="s l">hadice DN50 (DN65</text><text x="830" y="144" class="s l">nad ~80 kW),</text><text x="830" y="158" class="s l">připojení na sekundár</text><text x="830" y="172" class="s l">předávací stanice</text>
<!-- expanze -->
<path d="M470 215V280" class="pipe cold"/><ellipse cx="470" cy="294" rx="16" ry="14" class="dev"/><text x="470" y="322" class="s">EN prim. + PV</text>
<path d="M560 240V280" class="pipe cold"/><ellipse cx="560" cy="294" rx="16" ry="14" class="dev"/><text x="560" y="322" class="s">EN sek. + PV 3 bar</text>
<!-- TUV -->
<g class="pipe hot"><path d="M256 345H330V360H560"/></g><g class="pipe cold"><path d="M256 372H340V440H600"/></g>
<rect x="560" y="345" width="50" height="110" rx="22" class="tank"/><rect x="620" y="345" width="50" height="110" rx="22" class="tank"/><rect x="680" y="345" width="50" height="110" rx="22" class="tank"/>
<text x="645" y="475" class="s">TUV 3× 300 l (nebo 1× 1 000 l), výměníky paralelně, topná vložka</text>
<path d="M610 360H620M670 360H680" class="pipe hot"/><path d="M600 440H730" class="pipe cold"/>
<g class="pipe hot"><path d="M730 370H820" marker-end="url(#ar)"/></g><g class="pipe dhw"><path d="M820 420H730"/></g>
<text x="830" y="374" class="s l">TUV + cirkulace</text><text x="830" y="424" class="s l">studená voda (pojistná</text><text x="830" y="438" class="s l">sestava, zpětný ventil)</text>
</svg>'''

PLAN = '''<svg viewBox="0 0 640 300" role="img" aria-label="Půdorys kontejneru 20 stop, předběžný">
<rect x="20" y="20" width="590" height="235" class="cont"/>
<text x="20" y="14" class="s l">vnitřní rozměr 5 898 × 2 352 mm · měřítko 1 : 100 (1 px = 10 mm)</text>
<rect x="20" y="20" width="590" height="155" class="zone"/>
<text x="26" y="196" class="s l">obsluhovací ulička 0,8 m · při přepravě: hadice, rámy, příslušenství</text>
<circle cx="75" cy="85" r="50" class="tank"/><text x="75" y="82">AKU</text><text x="75" y="98" class="s">1 000 l Ø1,0</text>
<circle cx="165" cy="58" r="33" class="tank"/><circle cx="240" cy="58" r="33" class="tank"/><circle cx="315" cy="58" r="33" class="tank"/>
<text x="240" y="118" class="s">3× TUV 300 l Ø≈0,65 [OVĚŘIT]</text>
<circle cx="190" cy="78" r="55" class="future"/><text x="190" y="150" class="s">rezerva pro TUV 1 000 l</text>
<rect x="365" y="24" width="120" height="70" class="dev"/><text x="425" y="55" class="s">separátor, výměník,</text><text x="425" y="69" class="s">čerpadla, expanze</text>
<rect x="495" y="24" width="90" height="34" class="elec"/><text x="540" y="45" class="s">rozvaděč + PLC</text>
<rect x="18" y="100" width="4" height="70" fill="var(--accent)"/><text x="30" y="166" class="s l">panel rychlospojek</text>
<path d="M610 24V251" stroke="var(--accent)" stroke-width="5"/><text x="600" y="275" class="s r">čelní dveře 2 343 × 2 280</text>
</svg>'''

CSS = '''
:root{--bg:#f6f8f6;--panel:#ffffff;--ink:#16211b;--ink-2:#4b5a51;--line:#d5ddd8;--accent:#2f8f58;--accent-bg:#e6f3eb;
--crit:#b3261e;--crit-bg:#fbe9e7;--high:#a35d00;--high-bg:#fdf1de;--mid:#5f6b2a;--mid-bg:#f1f3e3;--ok:#256c43;--ok-bg:#e3f2e8;
--hot:#c4512b;--cold:#2e6fa8;--dhw:#7a4ea3;
--f-head:"IBM Plex Sans Condensed","Arial Narrow",Arial,sans-serif;--f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#111714;--panel:#18201b;--ink:#e3ebe6;--ink-2:#9fb0a6;--line:#2c3831;--accent:#4cbc7a;--accent-bg:#1b2e22;
--crit:#ff8a7f;--crit-bg:#3a1c1a;--high:#f2b25c;--high-bg:#352816;--mid:#c3cf7d;--mid-bg:#272b18;--ok:#7fd3a0;--ok-bg:#183021;--hot:#f08a63;--cold:#6fa8de;--dhw:#b68ce0;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#111714;--panel:#18201b;--ink:#e3ebe6;--ink-2:#9fb0a6;--line:#2c3831;--accent:#4cbc7a;--accent-bg:#1b2e22;
--crit:#ff8a7f;--crit-bg:#3a1c1a;--high:#f2b25c;--high-bg:#352816;--mid:#c3cf7d;--mid-bg:#272b18;--ok:#7fd3a0;--ok-bg:#183021;--hot:#f08a63;--cold:#6fa8de;--dhw:#b68ce0;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.55}
.wrap{max-width:1080px;margin:0 auto;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-family:var(--f-head);text-wrap:balance;line-height:1.2;margin:0}
h1{font-size:2.1rem;font-weight:600}
h2{font-size:1.45rem;font-weight:600;margin-top:44px;padding-top:14px;border-top:2px solid var(--ink)}
h2 .no{font-family:var(--f-mono);font-size:.9rem;color:var(--accent);margin-right:10px;font-weight:500}
h3{font-size:1.08rem;font-weight:600}
p,li,dd{max-width:72ch}
.doc-head{display:grid;gap:10px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.eyebrow{font-family:var(--f-mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.meta{font-family:var(--f-mono);font-size:.8rem;color:var(--ink-2);display:flex;flex-wrap:wrap;gap:6px 18px}
.verdict{margin-top:22px;background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--accent);padding:16px 18px;display:grid;gap:8px}
.verdict p{margin:0}
.key{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:16px}
.key div{background:var(--panel);border:1px solid var(--line);padding:12px 14px;min-width:0}
.key b{display:block;font-family:var(--f-mono);font-size:1.35rem;font-weight:500;font-variant-numeric:tabular-nums}
.key span{font-size:.85rem;color:var(--ink-2)}
.tbl{overflow-x:auto;margin:14px 0;border:1px solid var(--line);background:var(--panel)}
.tbl.narrow{max-width:560px}
table{border-collapse:collapse;width:100%;font-size:.86rem;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}
thead th{font-family:var(--f-head);font-weight:600;background:var(--accent-bg);text-align:right;font-size:.82rem;line-height:1.25}
tbody th{text-align:left;font-weight:600;white-space:nowrap}
td.l,th.l{text-align:left}
td.tw{text-align:left;font-family:var(--f-mono);color:var(--ink-2)}
td{font-family:var(--f-mono)}
table.text td{font-family:var(--f-body);text-align:left;min-width:220px}
table.text thead th{text-align:left}
tr.grp th,tr.grp td{border-top:2px solid var(--line)}
.sub{display:block;font-size:.74rem;color:var(--ink-2);font-weight:400;font-family:var(--f-mono)}
td.hl{font-weight:600}
td.ok{color:var(--ok);background:var(--ok-bg)} td.warn{color:var(--high);background:var(--high-bg)} td.bad{color:var(--crit);background:var(--crit-bg)}
.tag{display:inline-block;font-family:var(--f-mono);font-size:.72rem;color:var(--ink-2);border:1px solid var(--line);padding:0 5px;margin-left:4px}
.note{font-size:.85rem;color:var(--ink-2)}
.risks{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:14px}
.risk{background:var(--panel);border:1px solid var(--line);padding:14px 16px;min-width:0}
.risk header{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;margin-bottom:8px}
.pill{font-family:var(--f-mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;padding:2px 7px}
.sev-crit .pill{background:var(--crit-bg);color:var(--crit)} .sev-high .pill{background:var(--high-bg);color:var(--high)} .sev-mid .pill{background:var(--mid-bg);color:var(--mid)}
.sev-crit{border-top:3px solid var(--crit)} .sev-high{border-top:3px solid var(--high)} .sev-mid{border-top:3px solid var(--mid)}
.risk dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:4px 10px;font-size:.86rem}
.risk dt{font-family:var(--f-mono);font-size:.72rem;text-transform:uppercase;color:var(--ink-2);padding-top:3px}
.risk dd{margin:0}
.fig{background:var(--panel);border:1px solid var(--line);padding:12px;overflow-x:auto;margin:14px 0}
.fig svg{display:block;width:100%;min-width:720px;height:auto}
.fig.plan svg{min-width:560px;max-width:760px}
svg text{font-family:var(--f-body);font-size:13px;fill:var(--ink);text-anchor:middle}
svg text.s{font-size:11px;fill:var(--ink-2)} svg text.l{text-anchor:start} svg text.r{text-anchor:end}
svg text.lbl{font-family:var(--f-mono);font-size:11px;letter-spacing:.06em;fill:var(--accent);text-anchor:start}
svg .unit rect{fill:var(--accent-bg);stroke:var(--accent);stroke-width:1.5}
svg .unit.tuv rect{stroke:var(--dhw)}
svg .pipe path,svg path.pipe{fill:none;stroke-width:2.5}
svg .hot path,svg path.hot{stroke:var(--hot)} svg .cold path,svg path.cold{stroke:var(--cold)} svg .dhw path{stroke:var(--dhw)}
svg .pipe.hot path{stroke:var(--hot)} svg .pipe.cold path{stroke:var(--cold)} svg .pipe.dhw path{stroke:var(--dhw)}
svg .dev{fill:var(--panel);stroke:var(--ink-2);stroke-width:1.5}
svg .hx{fill:var(--panel);stroke:var(--ink);stroke-width:1.5;stroke-dasharray:3 3}
svg .tank{fill:var(--panel);stroke:var(--ink);stroke-width:1.8}
svg .future{fill:none;stroke:var(--accent);stroke-width:1.5;stroke-dasharray:5 4}
svg .cont{fill:var(--panel);stroke:var(--ink);stroke-width:3}
svg .zone{fill:var(--accent-bg);stroke:none}
svg .elec{fill:var(--high-bg);stroke:var(--high);stroke-width:1.5}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
.cols>div{min-width:0}
ul.plain{padding-left:18px} ul.plain li{margin:4px 0}
.checks{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;margin-top:14px}
.check{background:var(--panel);border:1px solid var(--line);padding:14px 16px;min-width:0}
.check ul{list-style:none;padding:0;margin:8px 0 0;display:grid;gap:7px}
.check li{display:grid;grid-template-columns:20px 1fr;gap:6px;font-size:.88rem}
.check input{margin-top:4px;accent-color:var(--accent)}
.check input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.phases{display:grid;gap:10px;margin-top:14px;counter-reset:ph}
.phases div{background:var(--panel);border:1px solid var(--line);padding:12px 16px}
.phases b{font-family:var(--f-head)}
code,.mono{font-family:var(--f-mono);font-size:.88em}
.formula{font-family:var(--f-mono);font-size:.85rem;background:var(--panel);border:1px solid var(--line);padding:10px 12px;overflow-x:auto;white-space:pre}
footer{margin-top:48px;padding-top:14px;border-top:1px solid var(--line);font-size:.8rem;color:var(--ink-2)}
'''


def build():
    r55 = {r['code']: r for r in C.cascade_rows(55)}
    b2 = r55['B-2']
    a50 = r55['A-50']
    html = f'''<title>Univerzální mobilní kotelna</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="doc-head">
<div class="eyebrow">REO HEATING · interní podklad · fáze 1 ze 5</div>
<h1>Univerzální mobilní kotelna s tepelnými čerpadly</h1>
<div class="meta"><span>Studie proveditelnosti a kritická rizika</span><span>16. 10. 2026</span><span>Data: výkonové mapy a návody výrobce, výpočty <code>studie_calc.py</code></span></div>
</header>

<section class="verdict">
<p><b>Závěr fáze 1:</b> mobilní kotelnu z vlastních jednotek a zásobníků postavit lze. Ve stávající podobě zadání ale má tři zásadní slabiny: dimenzování podle nominálního výkonu, provoz bez glykolu a neznámou teplotu otopné soustavy zákazníka. Všechny tři mohou způsobit, že kotelna v mrazu nedodá slíbené teplo.</p>
<p>Předběžně doporučuji kontejner 20′, venkovní primární okruh s glykolem a deskovým výměníkem, rozdělovač uvnitř kontejneru, nadřazenou regulaci (PLC) a samostatné TČ pro TUV s topnou vložkou pro sterilizaci. Definitivní sestavu vybrat až po obhlídce (kap. 11).</p>
</section>

<div class="key">
<div><b>{f1(C.cap("RHX50", 55, -15))} kW</b><span>RH X50 při −15 °C / W55 (nominál {f1(C.NOM["RHX50"])} kW)</span></div>
<div><b>{f1(C.cap("RH060", 55, -15))} kW</b><span>RH060 při −15 °C / W55 (nominál {f1(C.NOM["RH060"])} kW)</span></div>
<div><b>{f1(C.cap("RH050", 55, -15))} kW</b><span>RH050 při −15 °C / W55 (nominál {f1(C.NOM["RH050"])} kW)</span></div>
<div><b>{f1(b2["caps"][3])} / {f1(b2["n1"][3])} kW</b><span>2× RH X50 při −15 °C / W55: obě jednotky / po výpadku jedné</span></div>
</div>

<h2><span class="no">01</span>Kritická rizika</h2>
<p>Seřazeno podle dopadu na to, zda kotelna dodá teplo. Opatření jsou předběžná.</p>
<div class="risks">{risks_html()}</div>

<h2><span class="no">02</span>Předpoklady zadání, které nesedí</h2>
{corrections_html()}

<h2><span class="no">03</span>Skutečný výkon jednotek</h2>
<p>Topný výkon v kW při maximální frekvenci kompresoru podle výkonových map výrobce (lineární interpolace mezi body mapy). W35/45/55 = teplota výstupní vody. Zvýrazněny jsou mrazové body. Odtávání: zda je v mapách zahrnuto, je nutné ověřit u výrobce.</p>
{t_units()}
<p class="note">RH050/RH060: rozsah venkovní teploty −25 až 43 °C, voda pro vytápění 20–70 °C, doporučená max. teplota 60 °C, vestavěné čerpadlo (max. dopravní výška 9 / 12 m), přípojky DN25, hmotnost 160 / 165 kg. RH X50: voda až 78 °C, externí čerpadlo, přípojky G1½″, 370 kg, max. 20 kW / 32 A.</p>

<h2><span class="no">04</span>Kaskády pro vytápění</h2>
<p>Výkony v kW. „Nominál“ je součet A7/W35. Sloupec „po výpadku“ je skutečně garantovatelný výkon s redundancí: odečítá se největší jednotka v sestavě. Proud zahrnuje jednotku TUV a pomocné spotřebiče {f0(C.AUX_A)} A; proudy RH050/RH060 jsou odhad z max. příkonu map [OVĚŘIT typový štítek].</p>
{t_cascades()}
<h3>Do jaké venkovní teploty sestava pokryje ztrátu (W55)</h3>
<p>Modelová budova: ztráta lineárně s venkovní teplotou, vážená vnitřní teplota {f0(C.T_IN)} °C (administrativa 20 °C, hala temperovaná), výpočtová teplota −15 °C. Zelená = pokryje výpočtovou teplotu, oranžová = do −10 °C, červená = nedostačuje už nad −10 °C.</p>
{t_balance()}
<div class="cols">
<div><h3>Co z toho plyne</h3><ul class="plain">
<li>Jedna RH X50 sama pokryje jen budovu se ztrátou do ≈ 25 kW. Bez druhé jednotky nemá varianta B žádnou rezervu.</li>
<li>2× RH X50 kryje ztrátu do ≈ 50 kW při W55. Skutečná N+1 jen u ztráty do ≈ 25 kW.</li>
<li>Kaskáda malých jednotek (A) se lépe přizpůsobí malé zátěži a výpadek jedné jednotky ubere jen 15–30 % výkonu. Vyžaduje ale 5–6 venkovních jednotek, rámů a párů hadic.</li>
<li>Hybrid RH X50 + 2× RH060 má nejvíc výkonu na počet jednotek, ale po výpadku RH X50 zbude jen {f1(r55["H"]["n1"][3])} kW.</li>
</ul></div>
<div><h3>Redundance N+1: omezení</h3><ul class="plain">
<li>Rezerva funguje automaticky jen s nadřazenou regulací, která zná stav všech jednotek (porucha, blokace, odtávání) a přidá další stupeň.</li>
<li>Společné prvky nejsou redundantní: separátor, výměník, primární a sekundární čerpadlo, hlavní jistič, PLC. Doporučeno zdvojené sekundární čerpadlo (provozní + záložní) a náhradní čerpadlo ve výbavě.</li>
<li>Střídání podle motohodin a výkonový deficit jsou běžné funkce kaskádových regulátorů, u jednotek je ale nutné ověřit vstup „povolení chodu“ a výstup „porucha“.</li>
</ul></div>
</div>

<h2><span class="no">05</span>Teplota otopné soustavy zákazníka</h2>
<p>Nejdůležitější neznámá. Tabulka udává nejnižší venkovní teplotu, při které daná maximální teplota přívodu ještě stačí soustavě navržené na uvedený spád (exponent těles n = 1,3, vnitřní teplota 20 °C, výpočtová −15 °C, ekvitermní provoz).</p>
{t_supply()}
<p class="note">Skutečné soustavy bývají předimenzované a budovy po zateplení potřebují nižší teplotu, proto je zásadní změřit, jakou teplotu objekt opravdu potřebuje. U hal s teplovzdušnými jednotkami klesá výkon při nižší teplotě vody podobně.</p>

<h2><span class="no">06</span>Teplá voda</h2>
<p>Ohřev z 10 na 50 °C samostatnou RH050 přes trubkové výměníky zásobníků. Předpoklady: zásobník promíchaný, max. teplota vody z TČ {f0(C.T_FLOW_MAX)} °C, Δt na výměníku 5 K, součinitel prostupu výměníku {f0(C.U_COIL)} W/m²K [ODHAD]. Výkon TČ při W55 podle mapy. V buňce doba ohřevu a průměrný výkon.</p>
{t_tuv()}
<div class="cols">
<div><h3>Hodnocení</h3><ul class="plain">
<li>Výkonově RH050 stačí i na 1 000 l (v mrazu ≈ 6 h). Plocha 3,2–3,4 m² na zásobník není omezením výkonu, ale teploty: při přívodu 58 °C lze zásobník ohřát jen na ≈ {f1(C.t_max_reachable(3.3))} °C.</li>
<li>Pro 55 °C by bylo potřeba ≈ 62–63 °C z TČ, což je nad doporučením výrobce RH050.</li>
<li>Řešení: topná vložka (3–6 kW) v posledním zásobníku pro týdenní sterilizaci na 70 °C. Regulace RH ji řídí (parametry P17–P20). Alternativa: TUV z RH X50 (až 78 °C), ale za cenu ztráty nezávislosti okruhů.</li>
</ul></div>
<div><h3>Potřeba TUV (odhad pro 20 osob)</h3>
<div class="formula">bez sprch:   20 os. × 15–25 l (45 °C) ≈ 300–500 l/den
se sprchami: 20 × 40 l (40 °C) na konci směny
  ≈ 800 l při 40 °C ≈ 530 l uložených při 55 °C
→ 600–900 l zásobník, pokud se sprchuje najednou</div>
<p class="note">Tři skladové zásobníky 300 l zapojené za sebou (předehřev → dohřev) nebo paralelně pokryjí oba případy. Bez sprch stačí jeden až dva.</p></div>
</div>

<h2><span class="no">07</span>Hydraulika a ochrana proti zamrznutí</h2>
<div class="fig">{SCHEMA}</div>
<p class="note">Koncepční schéma bez armatur v detailu. V každé větvi jednotky: kulové kohouty, filtr (návod RH X50 požaduje filtr ve zpátečce), zpětná klapka, vypouštění a odvzdušnění v nejvyšším bodě.</p>
<div class="cols">
<div><h3>Proč rozdělovač dovnitř a separátor</h3><ul class="plain">
<li>RH050/RH060 tlačí vlastním čerpadlem, RH X50 potřebuje externí. Hydraulický separátor odděluje průtoky jednotek od průtoku k výměníku, takže si čerpadla nepřekážejí.</li>
<li>Předimenzovaný společný rozdělovač bez separace způsobí mísení a zkreslí čidla, malá jednotka může mít při běhu sama příliš nízký průtok. Se separátorem a zpětnou klapkou v každé větvi provoz jediné malé jednotky funguje.</li>
<li>Průtoky jednotek při Δt 5 K: RH050 {f1(C.flow_m3h(C.NOM["RH050"], 5))}, RH060 {f1(C.flow_m3h(C.NOM["RH060"], 5))}, RH X50 {f1(C.flow_m3h(C.NOM["RHX50"], 5))} m³/h (s glykolem ≈ +10 %). Hadice: RH050/060 DN32, RH X50 DN50, délky do 5 m.</li>
<li>Pokud trváte na dvou trubkách z venkovního rozdělovače: potrubí DN65 (2× RH X50 ≈ 17 m³/h, v ≈ 1,4 m/s), rozdělovač izolovaný a jen s glykolem.</li>
</ul></div>
<div><h3>Minimální objem akumulace</h3>
{t_buffer()}
<p class="note">V = P<sub>min</sub> × 10 min / (c × 5 K). RH X50 smí startovat max. 4× za hodinu. AKU 1 000 l stačí pro všechny sestavy; 2× 300 l + 500 l také, ale se třemi nádobami a více spoji.</p></div>
</div>
<h3>Ochrana proti zamrznutí: doporučené řešení</h3>
<div class="cols">
<div><ul class="plain">
<li><b>Primár s glykolem (doporučeno):</b> propylenglykol 35 % (bod tuhnutí ≈ −17 °C, ochrana proti roztržení níže) ve venkovních jednotkách, hadicích, separátoru a výměníku. Objem ≈ 100–200 l směsi. Penalizace ≈ 2–3 K na výměníku a 3–5 % výkonu. Glykol zůstává v okruhu i při přepravě (samouzavírací rychlospojky).</li>
<li><b>Okruh TUV:</b> glykol přímo do výměníků zásobníků, další výměník není nutný.</li>
<li><b>Hadice k zákazníkovi (voda):</b> bez průtoku při −15 °C vychladnou na 0 °C za ≈ {f1(C.freeze_hours(40))} h (DN40), {f1(C.freeze_hours(50))} h (DN50), {f1(C.freeze_hours(65))} h (DN65) při izolaci 30 mm. Vypouštěcí kohouty v nejnižších bodech, poplach při výpadku proudu (GSM s baterií).</li>
<li><b>Kontejner:</b> termostatický temperační ohřívač a poplach při teplotě pod +5 °C.</li>
</ul></div>
<div><ul class="plain">
<li><b>Varianta jen s vodou</b> (jen se souhlasem výrobce): protimrazové ventily u každé jednotky v nejnižším bodě, zavzdušňovací ventil nahoře, zpětné klapky a uzávěry s pružinovým návratem bez proudu, aby se vypustila jen venkovní část; automatické doplňování přes oddělovač dle EN 1717; UPS pro oběhová čerpadla.</li>
<li>Samotné protimrazové ventily <b>nejsou dostatečně bezpečné</b>: chrání jen místo osazení, při aktivaci vypouštějí i výše položené části soustavy (AKU je v kontejneru výš než venkovní připojení) a po výpadku proudu zůstane soustava bez tlaku až do příjezdu servisu.</li>
<li>Porucha čerpadla nebo regulace: hlídání průtoku a teploty vratné vody v PLC, poplach přes vzdálený dohled.</li>
</ul></div>
</div>

<h2><span class="no">08</span>Připojení k zákazníkovi</h2>
<p>Tlaková ztráta páru hadic (přívod + zpátečka) v kPa při Δt 10 K na straně zákazníka, vnitřní průměr = DN, drsnost 0,05 mm, místní odpory ζ = {f0(C.ZETA_HOSE_PAIR)} (rychlospojky, kohouty, oblouky). Při Δt 5 K je průtok dvojnásobný a ztráta zhruba čtyřnásobná.</p>
{t_hoses()}
<p class="note">Doporučení: DN50 pro 50–70 kW do 30 m, DN65 pro 100 kW nebo pro Δt 5 K. DN40 jen pro krátké propojení do 50 kW. Hadice EPDM pro topnou vodu do 90–110 °C a 6–10 bar, izolace ≥ 30 mm s UV ochranou, rychlospojky s uzávěrem na obou stranách. Konkrétní dodavatelé a ceny ve fázi 4. Pokud má objekt vlastní oběhová čerpadla za předávací stanicí, připojit se přes jejich vyrovnávač nebo do místa výměníku tak, aby čerpadlo kotelny a čerpadla objektu pracovala odděleně.</p>

<h2><span class="no">09</span>Kontejner 20′ nebo 10′</h2>
<div class="fig plan">{PLAN}</div>
<div class="cols">
<div><h3>20′ (doporučeno)</h3><ul class="plain">
<li>Vnitřně 5,90 × 2,35 × 2,39 m, dveře 2,34 × 2,28 m, vlastní hmotnost ≈ 2,2 t.</li>
<li>Pojme AKU 1 000 l, 3× TUV 300 l (později 1× 1 000 l), hydrauliku, rozvaděč a obslužnou uličku.</li>
<li>Při přepravě v uličce hadice, rámy jednotek a příslušenství, případně RH050/060 nastojato. Jedna souprava místo dvou.</li>
<li>Klopná výška nádrže 1 000 l s izolací (≈ Ø1,0 × 2,05 m) ≈ 2,28 m: vejde se pod strop 2,39 m, dveřmi jen těsně [OVĚŘIT rozměry nádrže].</li>
</ul></div>
<div><h3>10′</h3><ul class="plain">
<li>Vnitřně 2,83 × 2,35 m: AKU 1 000 l + 1 zásobník TUV + rozvaděč na dveřích, bez uličky.</li>
<li>Servis jen otevřenými dveřmi, záměna zásobníků TUV prakticky nemožná.</li>
<li>Úspora na kontejneru (řádově desítky tisíc Kč) se ztratí na méně univerzálním použití.</li>
</ul></div>
</div>

<h2><span class="no">10</span>Elektrické připojení</h2>
<p>Souběžný maximální proud z tabulky v kap. 04. Jistič navržen s rezervou 10 %, kabel pro délku do ≈ 30 m (Cu, uložení ve vzduchu) [OVĚŘIT úbytek napětí pro konkrétní délku].</p>
<div class="tbl narrow"><table><thead><tr><th>Sestava (vč. TUV)</th><th>Příkon max. kW</th><th>Proud A</th><th>Jistič</th><th>Kabel Cu</th></tr></thead><tbody>
{"".join(f'<tr><th scope="row">{code}</th><td>{f0(C.electro(u + ([r] if r else []) + [t])[0])}</td><td>{f0(C.electro(u + ([r] if r else []) + [t])[1])}</td><td>{C.breaker(C.electro(u + ([r] if r else []) + [t])[1])} A</td><td>{C.CABLE[C.breaker(C.electro(u + ([r] if r else []) + [t])[1])]}</td></tr>' for code, n, u, r, t in C.CASCADES)}
</tbody></table></div>
<p class="note">Rozvaděč: hlavní vypínač, přepěťová ochrana T1+T2, jištění a chrániče pro každou jednotku zvlášť (návod RH X50: 40 A s ochranou proti úniku proudu), hlídač fází, PLC, LTE router, GSM poplach na baterii, místo pro podružné elektroměry a měřič tepla. Jednofázová RH050 by zatížila jednu fázi ≈ 20 A, proto přednostně 3f jednotky.</p>

<h2><span class="no">11</span>Kontrolní seznam pro obhlídku</h2>
<p>Zaškrtávání funguje jen v tomto prohlížeči a neukládá se.</p>
<div class="checks">{checklist_html()}</div>

<h2><span class="no">12</span>Co potřebuji od výrobce a ze skladu</h2>
<ul class="plain">{"".join(f"<li>{d}</li>" for d in DOCS_NEEDED)}</ul>

<h2><span class="no">13</span>Další postup</h2>
<div class="phases">{"".join(f"<div><b>{t}</b><br>{d}</div>" for t, d in NEXT)}</div>

<footer>Výkony jednotek z výkonových map výrobce; elektro RH X50 z návodu k použití. Vše označené [OVĚŘIT] nebo [ODHAD] je předpoklad, ne údaj výrobce ani tržní cena. Konstrukční a statické části bude posuzovat autorizovaný projektant. Zdroj výpočtů: <code>Projekty/mobilni-kotelna-tc/src/studie_calc.py</code>.</footer>
</div>'''
    OUT.write_text(html, encoding='utf-8')
    print('zapsáno', OUT)


if __name__ == '__main__':
    build()
