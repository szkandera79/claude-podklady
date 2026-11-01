#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Soupis komponent — schéma 1 (pouze vytápění s AKU 100 l), realizace Kunčice.

Vytváří ../kuncice/soupis-komponent.csv a vkládá tabulky do ../kuncice/index.html
mezi značky <!-- SOUPIS:START --> a <!-- SOUPIS:END -->.
Spuštění:  python3 reo-schemata-zapojeni/src/soupis_kuncice.py
Čísla v hranatých závorkách odpovídají číslům ve schématu REO-SCH-K1.
"""
import csv, html, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "kuncice"))

# (skupina, č. ve schématu, položka, počet, jednotka, poznámka)
ITEMS = [
    ("Hlavní zařízení", "1", "Tepelné čerpadlo REO RH030–RH060 (monoblok R290)", "1", "ks", "včetně kabelového ovladače; model podle tepelné ztráty"),
    ("Hlavní zařízení", "5", "Akumulační nádrž 100 l (topná voda)", "1", "ks", "s jímkou, hrdly pro teploměr a pojistný ventil"),

    ("Venkovní část", "—", "Tvárnice ztraceného bednění + beton (2 ramena 200 × min. 500 mm, výška min. 300 mm)", "1", "sada", "dle výkresu REO-SCH-K1-P; štěrkový podsyp mezi rameny"),
    ("Venkovní část", "—", "Antivibrační patky (silentbloky) s kotvením", "2", "ks", "jedna na každé rameno patky; návod je vyžaduje"),
    ("Venkovní část", "2", "Kulový uzávěr DN25 s holendrem (výstup, vratka)", "2", "ks", "co nejblíže hrdlům jednotky"),
    ("Venkovní část", "4", "Separátor vzduchu a nečistot s automatickým odvzdušněním a pojistným ventilem", "1", "ks", "na výstupu venku, nejvyšší bod venkovní části"),
    ("Venkovní část", "3", "Protizámrazový ventil DN25", "1", "ks", "na vratce venku, výpustí dolů"),
    ("Venkovní část", "—", "Izolace potrubí venkovní, odolná UV (min. 19 mm)", "dle trasy", "m", "pro výstup i vratku"),
    ("Venkovní část", "—", "Prostup obvodovou zdí — chránička, těsnění, izolace", "1", "sada", "prostup utěsnit"),

    ("Technická místnost — primár", "2", "Kulový uzávěr DN25 (vstup AKU, a před i za filtrem 16)", "3", "ks", "AKU a filtr lze odpojit bez vypouštění"),
    ("Technická místnost — primár", "16", "Magnetický filtr DN25 (s vypouštěním)", "1", "ks", "na vratce do TČ = filtr na vstupu dle návodu"),
    ("Technická místnost — primár", "6", "Automatický odvzdušňovací ventil 3/8″–1/2″ (horní vývod AKU)", "1", "ks", "s uzavíracím ventilkem"),
    ("Technická místnost — primár", "8", "Teploměr + pojistný ventil (T-kus na plášti AKU)", "1", "sada", "pojistný ventil bez uzávěru, výfuk do odpadu"),
    ("Technická místnost — primár", "15", "Vypouštěcí kohout AKU", "1", "ks", "na dně nádrže"),
    ("Technická místnost — primár", "—", "Plnicí sestava topné vody (ventil + oddělovač dle ČSN EN 1717)", "1", "sada", "návod vyžaduje plnicí ventil; ve schématu nekresleno"),

    ("Technická místnost — sekundár (topení)", "10", "Oběhové čerpadlo (elektronické, 230 V) se šroubením", "1", "ks", "napájení spíná přijímač 11"),
    ("Technická místnost — sekundár (topení)", "2", "Kulový uzávěr (před a za čerpadlem, vratka z topení)", "3", "ks", "dimenze dle rozvodu"),
    ("Technická místnost — sekundár (topení)", "7", "Pojistná skupina: pojistný ventil 2,5–3 bar + manometr (+ odvzdušnění)", "1", "sada", "na stoupačce za čerpadlem, výfuk do odpadu"),
    ("Technická místnost — sekundár (topení)", "9", "Expanzní nádoba pro topení + držák a připojení", "1", "ks", "objem dle výpočtu objemu soustavy; bez uzávěru"),
    ("Technická místnost — sekundár (topení)", "13", "Automatický odvzdušňovací ventil (nejvyšší bod rozvodu)", "1", "ks", "další dle počtu horních bodů"),
    ("Technická místnost — sekundár (topení)", "17", "Trojcestný směšovací ventil + hlavice (volitelně)", "0–1", "ks", "jen pro podlahové topení: max. 40 °C, ideálně 35 °C"),
    ("Technická místnost — sekundár (topení)", "14", "Odvzdušňovací ventilky radiátorů", "dle počtu", "ks", "většinou stávající"),

    ("Regulace a elektro", "11, 12", "Bezdrátový pokojový termostat + přijímač (relé 230 V)", "1", "sada", "přijímač spíná napájení čerpadla 10"),
    ("Regulace a elektro", "—", "Rozvaděč TČ: proudový chránič, jistič TČ (1F/3F), jistič 230 V čerpadla", "1", "sada", "jistič 1,5× provozní proud dle štítku"),
    ("Regulace a elektro", "—", "Napájecí kabel TČ (3 nebo 5 vodičů) v chráničce", "dle trasy", "m", "průřez dle proudu a délky"),
    ("Regulace a elektro", "—", "Kabel 230 V k čerpadlu a přijímači (3 × 1,5 mm²)", "dle trasy", "m", ""),
    ("Regulace a elektro", "—", "Komunikační kabel ovladače TČ", "dle trasy", "m", "často součást dodávky TČ"),

    ("Potrubí a fitinky", "—", "Potrubí — měď / uhlíková ocel / PPR (dle volby investora)", "dle trasy", "m", "primár min. DN25 dle přípojek TČ"),
    ("Potrubí a fitinky", "—", "Šroubení (holendry) — rozebíratelné spoje u TČ, AKU, filtru, čerpadla, separátoru", "cca 16", "ks", "návod: každé zařízení připojit šroubením"),
    ("Potrubí a fitinky", "—", "Kolena 90° / 45°", "dle trasy", "ks", "počet kolen omezit (tlaková ztráta)"),
    ("Potrubí a fitinky", "—", "T-kusy (odbočky pro pojistnou skupinu, obtok směšovače, odvzdušnění)", "cca 6", "ks", ""),
    ("Potrubí a fitinky", "—", "Přechodky závit vnější / vnitřní, redukce, přechody plast–kov", "cca 12", "ks", "dle zvoleného materiálu"),
    ("Potrubí a fitinky", "—", "Objímky a kotvení potrubí", "dle trasy", "ks", "proti vibracím (návod)"),
    ("Potrubí a fitinky", "—", "Těsnicí materiál (konopí + pasta / těsnicí vlákno)", "1", "bal.", ""),
    ("Potrubí a fitinky", "—", "Izolace potrubí vnitřní (kaučuk min. 13 mm)", "dle trasy", "m", "celý primár i sekundár"),
]

# doplňky pro variantu 2 (vytápění + TUV), čísla dle REO-SCH-K2 / K2-E
ITEMS_TUV = [
    ("TUV — hydraulika", "18", "Trojcestný přepínací ventil DN25 s pohonem 230 V", "1", "ks", "A → AKU, B → spirála TUV; v režimu TUV pod napětím"),
    ("TUV — hydraulika", "19", "Zásobník TUV se spirálou", "1", "ks", "výkon spirály ≥ jmenovitý výkon TČ (návod)"),
    ("TUV — hydraulika", "2", "Kulový uzávěr (přívod a vratka spirály)", "2", "ks", "servis bez vypouštění"),
    ("TUV — hydraulika", "2", "Kulový uzávěr na spodním hrdle AKU", "1", "ks", "AKU lze odpojit, ohřev TUV běží dál"),
    ("TUV — hydraulika", "22", "Uzávěr + zpětný ventil na přívodu studené vody", "1", "sada", ""),
    ("TUV — hydraulika", "23", "Pojistný ventil TUV (obvykle 6 bar)", "1", "ks", "bez uzávěru, výfuk do odpadu; dle tlaku vodovodu"),
    ("TUV — hydraulika", "24", "Expanzní nádoba pro pitnou vodu + držák", "1", "ks", "objem dle objemu zásobníku"),
    ("TUV — hydraulika", "—", "Termostatický směšovač na výstupu teplé vody", "0–1", "ks", "doporučeno — voda nad 52 °C může opařit"),
    ("TUV — hydraulika", "21", "Elektrická topná vložka do zásobníku (volitelně)", "0–1", "ks", "dohřev a antilegionella"),
    ("TUV — elektro", "12", "Kabel k trojcestnému ventilu (3 × 0,75–1,5 mm²)", "dle trasy", "m", "svorky 3 (L) + 4 (N) + PE"),
    ("TUV — elektro", "14", "Čidlo TUV T2 + prodlužovací kabel", "1", "sada", "do jímky zásobníku; ověřit, zda je součástí dodávky TČ"),
    ("TUV — elektro", "13", "Stykač + jistič pro topnou vložku (volitelně)", "0–1", "sada", "ovládání ze svorky 1 + 4"),
    ("TUV — fitinky", "—", "Šroubení, T-kusy a přechodky navíc pro okruh TUV a spirálu", "cca 10", "ks", "dle zvoleného materiálu"),
]



def items_hydrobox(tuv=False):
    """Soupis pro verzi s hydroboxem (REO-SCH-H1 / H2): rozvaděč TČ nahrazuje hydrobox, přibývá kabeláž hydrobox ↔ jednotka."""
    out = []
    for it in ITEMS:
        g, n, item = it[0], it[1], it[2]
        if item.startswith("Rozvaděč TČ"):
            out.append(("Regulace a elektro", "—", "Přívod do hydroboxu z domovního rozvaděče (jištění dle typu hydroboxu)", "1", "okruh", "jistič Q s chráničem je v hydroboxu: 40 / 25 / 50 / 32 A"))
            continue
        if item.startswith("Napájecí kabel TČ"):
            out.append(("Regulace a elektro", "—", "Napájecí kabel hydrobox → venkovní jednotka (3 nebo 5 vodičů)", "dle trasy", "m", "v chráničce, průřez dle proudu"))
            out.append(("Regulace a elektro", "—", "Ovládací kabel hydrobox ↔ jednotka (E-ohřev, čerpadlo, 3c ventil, N + PE)", "dle trasy", "m", "230 V, svorky 1–4 hydroboxu"))
            out.append(("Regulace a elektro", "—", "Signální kabel čerpadla PWM / GND / FB", "dle trasy", "m", "0–12 V DC, vést odděleně od silových kabelů"))
            continue
        if item.startswith("Šroubení (holendry)"):
            it = (g, n, "Šroubení (holendry) — rozebíratelné spoje u TČ, hydroboxu, AKU, filtru, čerpadla, separátoru", "cca 20", "ks", "hydrobox: 2× DN25 zdola, 3× DN25 z boku (vnitřní závit)")
        out.append(it)
        if g == "Hlavní zařízení" and n == "5":
            out.append(("Hlavní zařízení", "18", "Hydrobox REO (RH-03H/S, RH-03H, RH-05H/S nebo RH-05H podle jednotky)", "1", "ks",
                        "čerpadlo primáru, dohřev 3 kW, 3c ventil, filtr, exp. nádoba 8 l, pojistný ventil 3 bar, jistič"))
            out.append(("Hlavní zařízení", "—", "Kotvení hydroboxu na nehořlavou stěnu", "1", "sada", "700 × 500 × 280 mm, 35 kg"))
    if tuv:
        for it in ITEMS_TUV:
            if it[1] in ("18",) or it[2].startswith("Kabel k trojcestnému"):
                continue            # trojcestný ventil je součástí hydroboxu
            out.append(it)
    else:
        out.append(("Technická místnost — primár", "—", "Zátka výstupu B hydroboxu (TUV nevyužito)", "1", "ks", "DN25"))
    return out


MATERIALS = [
    ("Měď", "tvrdé pájení nebo lisování", "odolná, malé průměry, snese vysoké teploty; vyšší cena materiálu", "28 × 1,5 mm (DN25)"),
    ("Uhlíková ocel (lisovací systém)", "lisování", "rychlá montáž, nižší cena než měď; jen uzavřené topné okruhy, chránit před vlhkostí zvenku", "28 mm (DN25)"),
    ("PPR", "polyfúzní svařování", "nejlevnější; pro topení trubka s vložkou (hliník / sklo) kvůli roztažnosti; větší vnější průměr; venku chránit před UV", "32 × 5,4 mm a víc"),
]


def write_csv():
    p = os.path.join(OUT, "soupis-komponent.csv")
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Skupina", "Č. ve schématu", "Položka", "Počet", "Jednotka", "Poznámka"])
        w.writerows(ITEMS)
    return p


def html_block():
    e = html.escape
    out = ['<!-- SOUPIS:START -->', '<section>', '  <span class="eyebrow">Soupis komponent</span>',
           '  <h2>Co budeme k instalaci potřebovat — schéma 1</h2>',
           '  <p>Soupis pro hydraulické zapojení pouze pro vytápění s AKU nádrží 100 l. Čísla odpovídají schématu REO-SCH-K1. '
           'Délky potrubí a počty fitinek se upřesní podle skutečné trasy na místě.</p>',
           '  <div class="tbl"><table>',
           '    <thead><tr><th>Č.</th><th>Položka</th><th>Počet</th><th>Poznámka</th></tr></thead>', '    <tbody>']
    group = None
    for g, n, item, qty, unit, note in ITEMS:
        if g != group:
            out.append(f'      <tr class="grp"><td colspan="4">{e(g)}</td></tr>')
            group = g
        num = "".join(f'<span class="n">{e(k.strip())}</span> ' for k in n.split(",")) if n != "—" else "—"
        out.append(f'      <tr><td>{num.strip()}</td><td>{e(item)}</td><td class="q">{e(qty)} {e(unit)}</td><td>{e(note)}</td></tr>')
    out += ['    </tbody>', '  </table></div>',
            '  <h3>Volba materiálu potrubí</h3>',
            '  <p>Investor si může vybrat, zda bude hydraulické propojení v mědi, uhlíkové oceli nebo PPR. '
            'Ke každé variantě je vždy třeba počítat s fitinky, tedy s napojovacími a šroubovacími prvky (kolena, T-kusy, přechodky a šroubení). '
            'Návod RH030–RH060 doporučuje pro rozvody TČ nerezové nebo PPR potrubí a připojení každého zařízení rozebíratelným šroubením.</p>',
            '  <div class="tbl"><table>',
            '    <thead><tr><th>Materiál</th><th>Spojování</th><th>Vlastnosti</th><th>Primár (orientačně)</th></tr></thead>', '    <tbody>']
    for m in MATERIALS:
        out.append('      <tr>' + "".join(f'<td>{e(c)}</td>' for c in m) + '</tr>')
    out += ['    </tbody>', '  </table></div>',
            '  <p class="small">Dimenze sekundárního okruhu podle stávajícího rozvodu. U výkonnějších jednotek (RH050, RH060) ověřit průtok '
            'a případně zvětšit dimenzi primáru. Návod dále doporučuje zpětný ventil na výstupu z jednotky; ve schématu zatím není. '
            'Seznam ke stažení jako tabulka: soupis-komponent.csv ve složce projektu.</p>',
            '</section>', '<!-- SOUPIS:END -->']
    return "\n".join(out)


def inject():
    p = os.path.join(OUT, "index.html")
    s = open(p, encoding="utf-8").read()
    block = html_block()
    if "<!-- SOUPIS:START -->" in s:
        s = re.sub(r"<!-- SOUPIS:START -->.*?<!-- SOUPIS:END -->", lambda m: block, s, flags=re.S)
    else:
        anchor = '<section>\n  <span class="eyebrow">Uvedení do provozu</span>'
        assert anchor in s
        s = s.replace(anchor, block + "\n\n" + anchor)
    open(p, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    print("zapsáno:", write_csv())
    inject()
    print("vloženo do index.html")
