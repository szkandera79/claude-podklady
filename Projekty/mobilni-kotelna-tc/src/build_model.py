#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vygeneruje model.html z čísel v model.py (žádná čísla se nepřepisují ručně).
    python3 mobilni-kotelna-tc/src/build_model.py
"""
import pathlib
import model as M

OUT = pathlib.Path(__file__).resolve().parent.parent / "model.html"
NB = " "
U = M.UNIT


def kc(x, dec=0):
    return f"{x:,.{dec}f}".replace(",", NB).replace(".", ",").replace("-", "−")


def czk(x):
    return f"{kc(x)}{NB}Kč"


def pct(x, dec=0):
    return f"{kc(x * 100, dec)}{NB}%"


def yrs(x):
    return "nezaplatí se" if x == float("inf") or x > 25 else f"{kc(x, 1)}{NB}roku"


def table(head, rows, cls="", num_from=1, caption=""):
    th = "".join(f'<th class="{"num" if i >= num_from else ""}">{h}</th>' for i, h in enumerate(head))
    body = ""
    for r in rows:
        rc = ""
        if isinstance(r, tuple) and len(r) == 2 and isinstance(r[1], str) and r[1].startswith("cls:"):
            r, rc = r[0], r[1][4:]
        tds = "".join(f'<td class="{"num" if i >= num_from else ""}">{c}</td>' for i, c in enumerate(r))
        body += f'<tr class="{rc}">{tds}</tr>'
    cap = f"<caption>{caption}</caption>" if caption else ""
    return f'<div class="tw"><table class="{cls}">{cap}<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


P = list(M.PRODUCTS)
cap = {p: M.capex(p) for p in P}
dep = {p: M.deploy_cost(p) for p in P}
mwh = M.mwh_table()
r10, r20, r30 = mwh
pb = {(p, t, m): M.payback(p, m, t) for p in P for t in ("market", "disc") for m in (3, 6, 9)}
sel, els = M.sens_el()
sfu, facs = M.sens_fuel()
cr = M.credit_example()
be_d, be_l, be_g = (M.breakeven_el(1, a) for a in ("diesel", "lto", "gas"))
cap50, pw50 = M.perf(-15, 50, "MAX")
I50 = pw50 * 1000 / (3 ** 0.5 * 400 * 0.95)
ALTN = M.ALT
kw = {p: M.PRODUCTS[p][0] * U["kw_15"] for p in P}
S = 100  # px na metr


def svg_container():
    L, W, H = 6.058, 2.438, 2.591
    ox, oy = 40, 40
    tech = 0.08 + M.TECH_LEN
    ux1 = tech + 0.1 + 0.5
    ux2 = ux1 + 0.98 + 1.0
    uy = (W - 1.195) / 2
    g = []
    a = g.append
    a(f'<text x="{ox}" y="{oy - 16}" class="t-h">Půdorys</text>')
    a(f'<rect x="{ox}" y="{oy}" width="{L * S}" height="{W * S}" class="c-wall"/>')
    a(f'<rect x="{ox + 8}" y="{oy + 8}" width="{tech * S - 8}" height="{W * S - 16}" class="c-tech"/>')
    a(f'<rect x="{ox + tech * S + 10}" y="{oy + 8}" width="{(L - tech) * S - 18}" height="{W * S - 16}" class="c-air"/>')
    a(f'<line x1="{ox + tech * S + 5}" y1="{oy}" x2="{ox + tech * S + 5}" y2="{oy + W * S}" class="c-part"/>')
    a(f'<circle cx="{ox + 0.62 * S}" cy="{oy + 0.62 * S}" r="{0.5 * S}" class="c-eq"/>')
    a(f'<text x="{ox + 0.62 * S}" y="{oy + 0.62 * S + 4}" class="t-s" text-anchor="middle">AKU 1 000 l</text>')
    a(f'<rect x="{ox + 1.3 * S}" y="{oy + 0.14 * S}" width="{0.5 * S}" height="{0.9 * S}" class="c-eq"/>')
    a(f'<text x="{ox + 1.55 * S}" y="{oy + 0.62 * S}" class="t-s" text-anchor="middle">RZ</text>')
    a(f'<rect x="{ox + 0.2 * S}" y="{oy + 1.45 * S}" width="{1.5 * S}" height="{0.6 * S}" class="c-eq"/>')
    a(f'<text x="{ox + 0.95 * S}" y="{oy + 1.72 * S}" class="t-s" text-anchor="middle">výměník,</text>')
    a(f'<text x="{ox + 0.95 * S}" y="{oy + 1.9 * S}" class="t-s" text-anchor="middle">čerpadla, měření</text>')
    a(f'<line x1="{ox - 6}" y1="{oy + 10}" x2="{ox - 6}" y2="{oy + W * S - 10}" class="c-door"/>')
    a(f'<text x="{ox - 14}" y="{oy + W * S / 2}" class="t-s" text-anchor="middle" transform="rotate(-90 {ox - 14} {oy + W * S / 2})">dveře se zámkem</text>')
    for x in (ux1, ux2):
        X, Y = ox + x * S, oy + uy * S
        a(f'<rect x="{X}" y="{Y}" width="{0.98 * S}" height="{1.195 * S}" class="c-unit"/>')
        a(f'<circle cx="{X + 0.49 * S}" cy="{Y + 0.6 * S}" r="{0.38 * S}" class="c-fan"/>')
        a(f'<text x="{X + 0.49 * S}" y="{Y + 0.64 * S}" class="t-s t-inv" text-anchor="middle">RH X50</text>')
    mid = ox + (tech + (L - tech) / 2) * S
    a(f'<text x="{mid}" y="{oy + 0.26 * S}" class="t-s" text-anchor="middle">mřížové panely · sání ≥ 0,5 m</text>')
    a(f'<text x="{mid}" y="{oy + (W - 0.12) * S}" class="t-s" text-anchor="middle">mřížové panely · sání ≥ 0,5 m</text>')
    a(f'<text x="{ox + tech * S / 2}" y="{oy + W * S + 20}" class="t-s" text-anchor="middle">technická místnost {kc(M.TECH_LEN, 2)} m</text>')
    a(f'<text x="{mid}" y="{oy + W * S + 20}" class="t-s" text-anchor="middle">vzduchová komora {kc(M.AIR_LEN, 2)} m · otevřená nahoru</text>')
    a(f'<text x="{ox + tech * S - 60}" y="{oy + W * S + 38}" class="t-s t-acc">plynotěsná přepážka</text>')
    sx = ox + L * S + 50
    a(f'<rect x="{sx}" y="{oy}" width="{4.0 * S}" height="{W * S}" class="c-skid"/>')
    for x in (0.5, 2.48):
        a(f'<rect x="{sx + x * S}" y="{oy + uy * S}" width="{0.98 * S}" height="{1.195 * S}" class="c-unit c-opt"/>')
    a(f'<text x="{sx + 2.0 * S}" y="{oy + W * S + 20}" class="t-s" text-anchor="middle">skid pro 3. a 4. jednotku</text>')
    a(f'<text x="{sx + 2.0 * S}" y="{oy + W * S + 36}" class="t-s" text-anchor="middle">(M75 / M100)</text>')

    ry = oy + W * S + 200
    base = ry + H * S
    a(f'<text x="{ox}" y="{ry - 128}" class="t-h">Podélný řez</text>')
    a(f'<line x1="{ox - 20}" y1="{base + 20}" x2="{sx + 4.0 * S + 10}" y2="{base + 20}" class="c-ground"/>')
    a(f'<rect x="{ox}" y="{ry}" width="{tech * S + 10}" height="{H * S}" class="c-wall"/>')
    a(f'<rect x="{ox + tech * S + 10}" y="{base - 0.16 * S}" width="{(L - tech) * S - 10}" height="{0.16 * S}" class="c-wall"/>')
    a(f'<line x1="{ox + L * S}" y1="{ry}" x2="{ox + L * S}" y2="{base}" class="c-post"/>')
    a(f'<line x1="{ox + tech * S + 10}" y1="{ry}" x2="{ox + L * S}" y2="{ry}" class="c-rail"/>')
    a(f'<rect x="{ox + 0.12 * S}" y="{base - 0.16 * S - 2.2 * S}" width="{1.0 * S}" height="{2.2 * S}" rx="10" class="c-eq"/>')
    a(f'<text x="{ox + 0.62 * S}" y="{base - 1.2 * S}" class="t-s" text-anchor="middle">AKU</text>')
    for x in (ux1, ux2):
        X = ox + x * S
        top = base - 0.16 * S - 0.2 * S - 1.9 * S
        a(f'<rect x="{X}" y="{top}" width="{0.98 * S}" height="{1.9 * S}" class="c-unit"/>')
        a(f'<rect x="{X + 0.19 * S}" y="{top - 0.45 * S}" width="{0.6 * S}" height="{0.45 * S}" class="c-duct"/>')
        cx = X + 0.49 * S
        a(f'<path d="M{cx} {top - 0.5 * S} v-{0.9 * S}" class="c-arrow" marker-end="url(#ah)"/>')
        for dx in (-0.3, 1.28):
            ax = X + dx * S
            a(f'<path d="M{ax - 12 if dx < 0 else ax + 12} {top + 1.2 * S} h{20 if dx < 0 else -20}" class="c-arrow-in" marker-end="url(#ahi)"/>')
    a(f'<text x="{ox + (ux1 + 0.49) * S + 14}" y="{ry - 0.95 * S}" class="t-s">výfuk nahoru, ≥ 2 m volno</text>')
    a(f'<text x="{ox + tech * S + 20}" y="{base + 42}" class="t-s">pororošt: kondenzát a případný únik R290 odchází dolů ven</text>')
    a(f'<text x="{ox + L * S + 8}" y="{ry + 12}" class="t-s">{kc(H, 2)} m</text>')
    a(f'<rect x="{sx}" y="{base - 0.3 * S}" width="{4.0 * S}" height="{0.3 * S}" class="c-skid"/>')
    for x in (0.5, 2.48):
        a(f'<rect x="{sx + x * S}" y="{base - 0.3 * S - 1.9 * S}" width="{0.98 * S}" height="{1.9 * S}" class="c-unit c-opt"/>')
    w = sx + 4.0 * S + 30
    h = base + 60
    defs = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5L0 10z" class="m-out"/></marker>'
            '<marker id="ahi" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0L10 5L0 10z" class="m-in"/></marker></defs>')
    return (f'<svg class="dwg" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Půdorys a řez kontejneru 20 stop '
            f's technickou místností a vzduchovou komorou pro dvě jednotky RH X50">{defs}{"".join(g)}</svg>')


unit_tbl = table(["Parametr (návod RH X50)", "Hodnota", "Důsledek pro mobilní kotelnu"], [
    ("Napájení", "3×380–400 V, 50 Hz, ±10 %", "Start vyžaduje ≥ 90 % jmenovitého napětí → pozor na dlouhé kabely a slabé staveništní přípojky"),
    ("Max. příkon / max. proud", f"{U['el_max_kw']} kW / {U['a_max']} A", f"Dimenzujeme na max. proud, ne na provozní (při −15 °C / W50 cca {kc(pw50, 1)} kW, {kc(I50)} A)"),
    ("Jistič jednotky", f"{U['breaker']} A, s ochranou proti úniku proudu", "Každá jednotka vlastní odbočka; chránič typ B (invertor)"),
    ("Průřez vodiče", f"{U['wire_mm2']} mm² (Cu)", "Pro vnitřní rozvod v kontejneru; přívod se dimenzuje na součet"),
    ("Uzemnění", "povinné", "Revize při každém nasazení (měření impedance smyčky)"),
    ("Napájení v zimě", "nevypínat; min. 12 h pod napětím před sezónou", "Po připojení 12 h předehřev kompresoru, teprve pak start → připojit den předem"),
    ("Spínání", "max. 4× za hodinu", "Kaskádu řídí regulace, nespínat stykačem ze vzdáleného povelu"),
    ("Chladivo", f"{U['refrigerant']}, {kc(U['charge_kg'], 1)} kg", "Hořlavé: jednotky jen ve volném prostoru, oddělené od technické místnosti"),
    ("Rozměry / hmotnost", "1 195 × 980 × 1 900 mm / 370 kg", "Do výšky kontejneru se vejde (vnitřní výška 2,39 m)"),
    ("Proudění vzduchu", "sání ze 4 stran ≥ 0,5 m, výfuk nahoru ≥ 2 m volno", "Nad jednotkou nesmí být střecha → otevřená vzduchová komora"),
    ("Výška nad terénem", "≥ 300 mm, při sněhu ≥ 500 mm", "Podlaha kontejneru + rám ≈ 0,5 m"),
    ("Voda", "filtr ve zpátečce povinný; glykol doporučen", "Magnetický filtr + oddělovací výměník s glykolem v primáru"),
    ("Hlučnost", f"≤ {U['lp_1m']} dB(A)", f"Předpoklad: akustický tlak v 1 m → akustický výkon ≈ {M.UNIT_LW} dB(A)"),
    ("Chlazení", "voda 7–30 °C, 34,5 kW při 35 °C venku", "Letní pronájem jako mobilní chladicí zdroj"),
], num_from=9)

elec_rows = []
for p in P:
    for e in M.electrical(p):
        elec_rows.append((f"{p} · {e['where']}", f"{e['units']}× RH X50", f"{kc(e['kw'])}{NB}kW", f"{e['a']}{NB}A",
                          f"3×{e['main']}{NB}A", e["cable"], e["plug"]))
elec_rows.append(("Pro srovnání: elektrokotel 50 kW", "—", "50 kW", "72 A", "3×80 A", "5×25 mm²", "CEE 125 A"))
elec_rows.append(("Pro srovnání: naftová kotelna 50 kW", "—", "0,5 kW", "2 A", "1×16 A", "3×2,5 mm²", "230 V"))
elec_tbl = table(["Sestava · přívod", "Jednotky", "Max. příkon", "Max. proud", "Hlavní jistič", "Přívodní kabel", "Připojení"],
                 elec_rows, num_from=2)

var_tbl = table(["", "A · Jednotky na střeše kontejneru", "B · Vzduchová komora v kontejneru (doporučeno)", "C · Jednotky na skidu vedle kontejneru"], [
    ("Přeprava", "<span class='bad'>Nad limitem 4,0 m</span> (souprava ≈ 6 m) → jednotky vozit zvlášť a na místě zvedat jeřábem",
     "<span class='good'>Vcelku</span>, výška soupravy ≈ 3,85 m, jedna jízda", "Druhá jízda nebo přívěs"),
    ("Montáž na místě", "Jeřáb + práce ve výšce při každém nasazení", "<span class='good'>Jen napojení</span>, vše předem zapojené", "Usazení skidu, propojení hadicemi a kabelem"),
    ("Proudění vzduchu", "<span class='good'>Výborné</span>", "Dobré; riziko recirkulace řeší výfukové nástavce nad střechu", "<span class='good'>Výborné</span>"),
    ("Zabezpečení", "Dobré (výška), ale bez zámku", "<span class='good'>Uzamykatelná komora</span>, jednotky přišroubované", "Mřížová klec, slabší"),
    ("R290", "Volný prostor", "Volný prostor nad i pod jednotkou, plynotěsná přepážka", "Volný prostor"),
    ("Hluk", "<span class='bad'>Nejhorší</span>: zdroj ve 4–5 m, nic nestíní", "Stěna kontejneru stíní jeden směr", "Podle natočení"),
    ("Statika", "Střecha ISO kontejneru není nosná → rám na rohové odlitky", "Výztužný rám místo vyřezaných stěn, statický posudek", "Bez problému"),
    ("Servis", "Ve výšce, nutné zábradlí", "Z podlahy kontejneru", "Z terénu"),
    ("Použití", "Spíš pro dlouhodobé nasazení", "<strong>Základ M25 a M50</strong>", "<strong>3. a 4. jednotka (M75, M100)</strong>"),
], num_from=9)

capex_rows = [(n, *[czk(v)] * len(P)) for n, v in M.CORE]
for n, v in M.PER_UNIT:
    capex_rows.append((f"{n} (za jednotku {czk(v)})", *[czk(v * M.PRODUCTS[p][0]) for p in P]))
for n, v in M.SKID:
    capex_rows.append((n, "—", "—", czk(v), czk(v)))
capex_rows.append((("Mezisoučet", *[czk(cap[p][0]) for p in P]), "cls:sub"))
capex_rows.append(((f"Rezerva {pct(M.RESERVE)}", *[czk(cap[p][1]) for p in P]), "cls:"))
capex_rows.append((("<strong>CAPEX sestavy</strong>", *[f"<strong>{czk(cap[p][2])}</strong>" for p in P]), "cls:tot"))
capex_rows.append(("První nasazení (doprava a montáž)", *[czk(dep[p]) for p in P]))
capex_rows.append((("<strong>CAPEX vč. prvního nasazení</strong>", *[f"<strong>{czk(cap[p][2] + dep[p])}</strong>" for p in P]), "cls:tot"))
capex_rows.append(("Kč na kW garantovaného výkonu (−15 °C)", *[czk(cap[p][2] / kw[p]) for p in P]))
capex_tbl = table(["Položka (Kč bez DPH)"] + P, capex_rows, cls="wide")

deploy_tbl = table(["Náklad jednoho nasazení (do 100 km)", "Kč"],
                   [(n, czk(v)) for n, v in M.DEPLOY_BASE] + [("Skid: doprava a napojení (jen M75/M100)", czk(M.DEPLOY_SKID))])
fleet = 3 * cap["M100"][2] + M.DEV_ONE_OFF
core_sum = sum(v for _, v in M.CORE)

price_rows = [(f"Nájem {p} · {kw[p]} kW / měsíc", czk(M.RENT[p]), czk(M.RENT[p] * (1 - M.DISC_RENT)), czk(M.RENT[p])) for p in P]
price_rows += [(f"Mobilizace {p} (do 100 km)", czk(M.MOBIL[p]), czk(M.MOBIL[p] * (1 - M.DISC_MOBIL)), czk(M.MOBIL[p])) for p in P]
price_rows.append(("Zápočet na trvalou kotelnu", "—", "—", f"{pct(M.CREDIT_SHARE)} zaplaceného nájmu, max {pct(M.CREDIT_CAP)} ceny kotelny"))
price_rows.append(("Kauce", "1 měsíční nájem", "bez kauce", "1 měsíční nájem"))
price_tbl = table(["Kč bez DPH", "A · Tržní", "B · Náš zákazník", "C · Se zápočtem"], price_rows)

hdr = ["Odběr v lednu", "Sestava TČ", "TČ celkem", "z toho nájem + mobilizace"] + [ALTN[t] for t in ALTN]
mwh_rows = []
for r in mwh:
    cells = [f"{r['mwh']} MWh/měsíc", r["set"], f"<strong>{czk(r['hp'])}</strong>", czk(r["hp_rent"])]
    for t in ALTN:
        diff = (r["hp"] - r[t]) / r[t]
        tag = "win" if diff < -0.03 else ("lose" if diff > 0.03 else "eq")
        cells.append(f'{czk(r[t])}<span class="d {tag}">TČ {"+" if diff > 0 else "−"}{pct(abs(diff))}</span>')
    mwh_rows.append(cells)
mwh_tbl = table(hdr, mwh_rows, cls="wide", num_from=2)

energy_tbl = table(["Zdroj", "Předpoklad (bez DPH)", "Energie na 1 MWh tepla"], [
    ("Tepelné čerpadlo RH X50", f"elektřina {czk(M.EL)}/MWh, SPF {kc(M.SPF, 1)} (z výkonových křivek)", czk(M.heat_price("hp"))),
    ("Nafta", f"{kc(M.DIESEL)} Kč/l, {kc(M.OIL_KWH_L)} kWh/l, účinnost {pct(M.OIL_EFF)}", czk(M.heat_price("diesel"))),
    ("Lehký topný olej", f"{kc(M.LTO)} Kč/l, účinnost {pct(M.OIL_EFF)}", czk(M.heat_price("lto"))),
    ("Propan (LPG)", f"{kc(M.LPG)} Kč/l, {kc(M.LPG_KWH_L, 1)} kWh/l, účinnost {pct(M.GAS_EFF)}", czk(M.heat_price("lpg"))),
    ("Zemní plyn", f"{czk(M.GAS)}/MWh vč. distribuce, účinnost {pct(M.GAS_EFF)}", czk(M.heat_price("gas"))),
    ("Elektrokotel", f"elektřina {czk(M.EL)}/MWh, účinnost {pct(M.EL_BOILER_EFF)}", czk(M.heat_price("elk"))),
], num_from=2)
rent_alt_tbl = table(["Alternativa", "25–30 kW", "50 kW", "75–80 kW", "Mobilizace"],
                     [(ALTN[t], *[czk(x) for x in M.ALT_RENT[t]], czk(M.ALT_MOBIL[t])) for t in ALTN])

spf_tbl = table(["Provoz soustavy", "SPF soustavy", "Energie na 1 MWh tepla (el. 4 500 Kč)"], [
    ("Pevně 55 °C (bez ekvitermu, staré radiátory)", kc(M.SPF_W55, 2), czk(M.EL / M.SPF_W55)),
    (("<strong>Ekviterm 50 °C při −15 °C → 35 °C při +15 °C (základ)</strong>", f"<strong>{kc(M.SPF_CALC, 2)}</strong>", f"<strong>{czk(M.EL / M.SPF_CALC)}</strong>"), "cls:tot"),
    ("Ekviterm 40 → 30 °C (podlahovka, vysoušení staveb)", kc(M.SPF_LOW, 2), czk(M.EL / M.SPF_LOW)),
])

sel_rows = [[f"SPF {kc(s, 1)}"] + [czk(v) for v in vals] for s, vals in sel.items()]
sel_rows.append((["<em>Nafta</em>"] + [f"<em>{czk(r20['diesel'])}</em>"] * len(els), "cls:ref"))
sel_rows.append((["<em>Lehký topný olej</em>"] + [f"<em>{czk(r20['lto'])}</em>"] * len(els), "cls:ref"))
sel_tbl = table(["M50 · 20 MWh/měsíc"] + [f"el. {kc(e)}" for e in els], sel_rows)
sfu_rows = [[ALTN[t]] + [czk(v) for v in vals] for t, vals in sfu.items()]
sfu_rows.append(([f"<strong>TČ M50 (el. {kc(M.EL)}, SPF {kc(M.SPF, 1)})</strong>"] + [f"<strong>{czk(r20['hp'])}</strong>"] * len(facs), "cls:tot"))
sfu_tbl = table(["M50 · 20 MWh/měsíc"] + [("palivo dnes" if f == 1 else f"palivo {'+' if f > 1 else ''}{pct(f - 1)}") for f in facs], sfu_rows)

pb_rows = []
for p in P:
    for t, tn in (("market", "A · tržní"), ("disc", "B · náš zákazník")):
        cells = [p, tn]
        for m in (3, 6, 9):
            x = pb[(p, t, m)]
            irr = "" if x["irr"] is None else " · IRR " + pct(x["irr"])
            cells.append(f'{czk(x["cf"])}<span class="d">{yrs(x["pb"])}{irr}</span>')
        pb_rows.append((cells, "cls:" + ("first" if t == "market" else "")))
pb_tbl = table(["Sestava", "Ceník", "3 měsíce obsazenosti", "6 měsíců", "9 měsíců"], pb_rows, num_from=2)

ex = M.payback("M50", 6)
pb_detail = table(["M50 · tržní ceník · 6 měsíců", "Kč/rok"], [
    (f"Nájem 6 × {czk(M.RENT['M50'])}", czk(M.RENT["M50"] * 6)),
    (f"Mobilizace {ex['deployments']} × {czk(M.MOBIL['M50'])}", czk(M.MOBIL["M50"] * ex["deployments"])),
    (f"Náklady nasazení {ex['deployments']} × {czk(dep['M50'])}", "−" + czk(dep["M50"] * ex["deployments"])),
    (f"Obchodní náklady {pct(M.SALES_COMM)} z nájmu", "−" + czk(M.RENT["M50"] * 6 * M.SALES_COMM)),
    (f"Pojištění a údržba ({pct(M.INSURANCE + M.MAINT, 1)} CAPEX), telemetrie, sklad", "−" + czk(ex["fixed"])),
    (("<strong>Provozní cash flow</strong>", f"<strong>{czk(ex['cf'])}</strong>"), "cls:tot"),
    (f"Návratnost CAPEX {czk(cap['M50'][2])}", yrs(ex["pb"])),
])

noise_rows = [(f"{r} m", *[f"{kc(M.noise(n, r))}{NB}dB(A)" for n in (1, 2, 4)]) for r in (5, 10, 15, 20, 30)]
noise_rows.append((("<strong>Odstup pro noční limit 40 dB(A)</strong>", *[f"<strong>{kc(M.dist_for(n, 40))}{NB}m</strong>" for n in (1, 2, 4)]), "cls:tot"))
noise_tbl = table(["Vzdálenost od okna chráněné stavby", "1 jednotka (M25)", "2 jednotky (M50)", "4 jednotky (M100)"], noise_rows)

sizes_tbl = table(["Sestava", "Jednotky", "Garantovaný výkon při −15 °C / W50", "Chlazení (35 °C venku, voda 7 °C)", "Odběr v lednu", "Umístění jednotek"], [
    ("M25", "1× RH X50", "25 kW", "34 kW", "do ~12 MWh/měsíc", "kontejner (1 místo volné)"),
    ("M50", "2× RH X50", "50 kW", "69 kW", "12–25 MWh/měsíc", "kontejner"),
    ("M75", "3× RH X50", "75 kW", "103 kW", "25–37 MWh/měsíc", "kontejner + skid"),
    ("M100", "4× RH X50", "100 kW", "138 kW", "37–50 MWh/měsíc", "kontejner + skid"),
], num_from=9)

risk_tbl = table(["Riziko", "Dopad", "Opatření"], [
    ("Nízká obsazenost mimo sezónu", "Návratnost nad 10 let", "Letní chlazení, vysoušení staveb, sleva mimo sezónu, spolupráce s půjčovnami"),
    ("Nedostatečná přípojka (3×80 A)", "Nasazení nelze realizovat", "Formulář požadavků v poptávce, kontrola jističe před nabídkou, M75/M100 na dva přívody"),
    ("Vysoká teplota soustavy", "SPF pod 2, zákazník neušetří", "Měření teplot při prohlídce, ekviterm povinně, jinak nenabízet"),
    ("Recirkulace studeného vzduchu v komoře", "Nižší výkon, častější odmrazování", "Výfukové nástavce, ověření na prototypu"),
    ("Únik R290", "Nebezpečí výbuchu", "Otevřená komora, plynotěsná přepážka, detektor s odpojením, školení"),
    ("Zamrznutí při výpadku proudu", "Škoda na jednotkách", "Glykol v primáru (návod doporučuje), alarm telemetrie"),
    ("Znečištěná voda soustavy", "Poškození výměníku", "Magnetický filtr, oddělovací výměník, proplach na náklady zákazníka"),
    ("Krádež, vandalismus", "Ztráta jednotek", "Uzamčený kontejner, GPS, pojištění, kauce"),
    ("Hluk, stížnosti", "Omezení provozu", "Výpočet odstupů, orientace kontejneru, tichý režim"),
    ("Platební morálka", "Cash flow", "Kauce, nájem měsíc dopředu, elektřina na odběr zákazníka"),
], num_from=9)

pitch_tbl = table(["", "Naftová kotelna 50 kW", "Tepelné čerpadlo M50"], [
    ("Nájem měsíčně", czk(M.ALT_RENT['diesel'][1]), czk(M.RENT['M50'])),
    ("Mobilizace (rozpuštěná do 4 měsíců)", czk(M.ALT_MOBIL['diesel'] / M.MONTHS), czk(M.MOBIL['M50'] / M.MONTHS)),
    ("Energie za 20 MWh tepla", czk(20 * M.heat_price('diesel')), czk(20 * M.heat_price('hp'))),
    (("<strong>Celkem za měsíc</strong>", f"<strong>{czk(20 * r20['diesel'])}</strong>", f"<strong>{czk(20 * r20['hp'])}</strong>"), "cls:tot"),
    ("Cena za 1 MWh tepla", czk(r20['diesel']), czk(r20['hp'])),
])

CSS = r"""
:root{
  --bg:#F4F8F5; --paper:#FFFFFF; --ink:#16201C; --muted:#5F6B64; --line:#DDE6E0; --soft:#F4F8F5;
  --green:#0F3D2E; --accent:#1E8F5B; --tint:#E7F3EC; --amber:#F2A33A; --amber-bg:#FFF4E2; --amber-ink:#7A4A0E;
  --win:#1E8F5B; --win-bg:#E7F3EC; --lose:#B4442E; --lose-bg:#FBEAE6; --eq:#6B6F5A; --eq-bg:#F1F0E6;
  --air:#DCEEF6; --air-ink:#2C6E8F; --unit:#0F3D2E; --unit-ink:#FFFFFF;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0E1512; --paper:#141E1A; --ink:#E4ECE7; --muted:#9AAAA1; --line:#2A3A33; --soft:#18241F;
  --green:#8FD3AE; --accent:#4CC08A; --tint:#1B3328; --amber-bg:#2E2413; --amber-ink:#F4C98A;
  --win:#5CCB95; --win-bg:#173026; --lose:#F08E78; --lose-bg:#35201B; --eq:#C9C6A8; --eq-bg:#29291F;
  --air:#16303B; --air-ink:#8CC8E3; --unit:#4CC08A; --unit-ink:#0E1512;
}}
:root[data-theme="dark"]{
  --bg:#0E1512; --paper:#141E1A; --ink:#E4ECE7; --muted:#9AAAA1; --line:#2A3A33; --soft:#18241F;
  --green:#8FD3AE; --accent:#4CC08A; --tint:#1B3328; --amber-bg:#2E2413; --amber-ink:#F4C98A;
  --win:#5CCB95; --win-bg:#173026; --lose:#F08E78; --lose-bg:#35201B; --eq:#C9C6A8; --eq-bg:#29291F;
  --air:#16303B; --air-ink:#8CC8E3; --unit:#4CC08A; --unit-ink:#0E1512;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.55 Inter,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;
  padding-inline:16px;padding-block:28px 60px;-webkit-font-smoothing:antialiased}
.doc{max-width:1080px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:44px clamp(18px,5vw,56px)}
h1,h2,h3{font-family:Poppins,system-ui,sans-serif;text-wrap:balance;color:var(--green)}
h1{font-size:clamp(24px,3.4vw,32px);line-height:1.18;margin:8px 0 10px;font-weight:600}
h2{font-size:21px;margin:46px 0 10px;font-weight:600;padding-top:22px;border-top:1px solid var(--line)}
h3{font-size:15.5px;margin:22px 0 6px;font-weight:600}
.eyebrow{font:600 11.5px/1 Inter,sans-serif;letter-spacing:2px;text-transform:uppercase;color:var(--accent)}
.sec{font:600 11px/1 Inter,sans-serif;letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:8px}
p,li{max-width:76ch}
.lead{font-size:16.5px}
.note,.small{font-size:13px;color:var(--muted)}
ul{padding-left:20px} li{margin:4px 0}
.meta{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--muted);margin-bottom:18px}
.internal{background:var(--amber-bg);color:var(--amber-ink);border-radius:12px;padding:14px 18px;font-size:13.5px;margin:18px 0}
.internal strong{display:block;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px;font-size:11.5px}
.internal ul{margin:4px 0 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:22px 0}
.kpi{background:var(--soft);border-radius:12px;padding:14px 16px}
.kpi .k{font-size:11.5px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);font-weight:600}
.kpi .v{font:600 23px/1.2 Poppins,sans-serif;color:var(--green);margin-top:6px;font-variant-numeric:tabular-nums}
.kpi .s{font-size:12.5px;color:var(--muted);margin-top:2px}
.tw{overflow-x:auto;margin:12px 0 8px;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:13.6px}
table.wide{min-width:980px}
caption{text-align:left;font-weight:600;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;padding:4px 0 8px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-weight:600;color:var(--muted);font-size:12.5px;background:var(--soft)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.sub td{background:var(--soft)} tr.first td{border-top:2px solid var(--line)}
tr.tot td{border-top:2px solid var(--accent);border-bottom:2px solid var(--accent)}
tr.ref td{color:var(--muted)}
.d{display:block;font-size:11.5px;color:var(--muted);font-weight:500;margin-top:1px}
.d.win,.d.lose,.d.eq{display:inline-block;border-radius:6px;padding:0 6px;margin-top:3px}
.d.win{background:var(--win-bg);color:var(--win)} .d.lose{background:var(--lose-bg);color:var(--lose)} .d.eq{background:var(--eq-bg);color:var(--eq)}
.good{color:var(--win);font-weight:600} .bad{color:var(--lose);font-weight:600}
.formula{background:var(--tint);border-radius:12px;padding:16px 18px;margin:14px 0}
.formula code{font:600 15px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--green)}
.pitch{border-left:3px solid var(--amber);padding:4px 0 4px 16px;margin:14px 0;font-size:15.5px}
.cols{columns:2 320px;column-gap:32px} .cols li{break-inside:avoid}
.fig{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:12px;padding:12px;background:var(--paper)}
.dwg{display:block;width:100%;min-width:760px;height:auto}
.dwg text{font:12px Inter,system-ui,sans-serif;fill:var(--ink)}
.dwg .t-h{font:600 13px Poppins,sans-serif;fill:var(--green)}
.dwg .t-s{fill:var(--muted)} .dwg .t-inv{fill:var(--unit-ink);font-weight:600} .dwg .t-acc{fill:var(--lose)}
.c-wall{fill:var(--soft);stroke:var(--muted);stroke-width:2}
.c-tech{fill:var(--paper);stroke:var(--line);stroke-width:1}
.c-air{fill:var(--air);stroke:var(--air-ink);stroke-width:1.5;stroke-dasharray:3 4}
.c-part{stroke:var(--lose);stroke-width:4}
.c-eq{fill:var(--tint);stroke:var(--accent);stroke-width:1.5}
.c-unit{fill:var(--unit);stroke:var(--unit);stroke-width:1}
.c-opt{opacity:.45}
.c-fan{fill:none;stroke:var(--unit-ink);stroke-width:1.5;opacity:.7}
.c-door{stroke:var(--accent);stroke-width:4}
.c-skid{fill:none;stroke:var(--muted);stroke-width:1.5;stroke-dasharray:6 4}
.c-ground{stroke:var(--muted);stroke-width:1.5}
.c-post,.c-rail{stroke:var(--muted);stroke-width:3}
.c-duct{fill:var(--soft);stroke:var(--unit);stroke-width:1.5}
.c-arrow{stroke:var(--air-ink);stroke-width:2.5;fill:none} .c-arrow-in{stroke:var(--air-ink);stroke-width:2;fill:none}
.m-out,.m-in{fill:var(--air-ink)}
a{color:var(--accent)}
@media print{body{background:#fff;padding:0}.doc{border:0;padding:0}.internal{display:none}h2{break-after:avoid}.tw,.fig{overflow:visible}table.wide{min-width:0;font-size:11px}.dwg{min-width:0}}
"""

html = f"""<meta charset="utf-8">
<title>Mobilní kotelny s TČ</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600&display=swap">
<style>{CSS}</style>
<main class="doc">
<div class="eyebrow">ThermaVera Energy · interní podnikatelský model</div>
<h1>Pronájem mobilních kotelen s tepelnými čerpadly RH X50 v kontejneru 20'</h1>
<div class="meta"><span>Sestavy M25 · M50 · M75 · M100</span><span>Česká republika · B2B</span><span>Všechny ceny bez DPH</span><span>Verze 2 · 21. 9. 2026</span></div>

<div class="internal"><strong>Před použitím navenek ověřit</strong><ul>
<li>U výrobce: zda „≤ 62 dB(A)" je akustický tlak v 1 m; zda lze omezit max. příkon (displej má režim „nízký výkon" a „špičkový odběr") a tím snížit jištění; souhlas s výfukovými nástavci a s provozem v otevřené komoře.</li>
<li>Posouzení umístění R290 podle EN 378 (otevřená komora, přepážka, detektor) a přepravy naplněných jednotek podle ADR.</li>
<li>Nabídka konverze kontejneru (výřez, výztuha, statika), ceny akumulace, výměníku, rozvaděče s chrániči typ B, pojištění flotily.</li>
<li>Průzkum trhu: nájmy mobilních naftových a plynových kotelen 25–100 kW v ČR (v modelu odhady).</li>
</ul></div>

<p class="lead">Kotelna je kontejner 20'. Technická místnost s akumulací, hydraulikou, rozvaděčem a regulací je zamčená a zateplená.
Jednotky RH X50 stojí ve vedlejší vzduchové komoře, která je otevřená nahoru a po stranách uzavřená mřížovými panely se zámkem. Kontejner
pojme 2 jednotky (M25, M50), 3. a 4. jednotku (M75, M100) nese skid vedle kontejneru. Podmínky elektrického připojení jsou z návodu RH X50,
topný faktor je spočítaný z výkonových křivek výrobce.</p>

<div class="kpis">
 <div class="kpi"><div class="k">CAPEX M50 / M100</div><div class="v">{kc(cap['M50'][2] / 1e6, 2)} / {kc(cap['M100'][2] / 1e6, 2)} mil.</div><div class="s">kontejner vč. rezervy {pct(M.RESERVE)}</div></div>
 <div class="kpi"><div class="k">Přívod M50</div><div class="v">3×80 A</div><div class="s">2 × 32 A max. dle návodu + pomocné okruhy</div></div>
 <div class="kpi"><div class="k">SPF z křivek RH X50</div><div class="v">{kc(M.SPF_CALC, 2)}</div><div class="s">ekviterm 50/35 °C; při pevných 55 °C jen {kc(M.SPF_W55, 2)}</div></div>
 <div class="kpi"><div class="k">Návratnost M100 · 6 / 9 měs.</div><div class="v">{kc(pb[('M100', 'market', 6)]['pb'], 1)} / {kc(pb[('M100', 'market', 9)]['pb'], 1)} roku</div><div class="s">tržní ceník; M50: {kc(pb[('M50', 'market', 6)]['pb'], 1)} / {kc(pb[('M50', 'market', 9)]['pb'], 1)} roku</div></div>
</div>

<h3>Hlavní závěry</h3>
<ul>
<li><strong>Jednotky na střechu nedávat.</strong> RH X50 je vysoká 1,9 m a fouká nahoru; na střeše by souprava na autě měřila kolem 6 m a nešla by převážet vcelku.
Lepší je <strong>vzduchová komora uvnitř kontejneru</strong>: otevřená nahoru, zamčená po stranách, převoz vcelku, na místě jen napojení.</li>
<li><strong>Přípojka je větší, než jsme čekali.</strong> Návod žádá na jednotku jistič 40 A (max. 32 A). M50 proto potřebuje přívod 3×80 A a konektor CEE 125 A, M100 dva takové přívody.
Tohle se musí prověřit jako první, je to nejčastější důvod, proč nasazení nepůjde.</li>
<li><strong>Teplota soustavy rozhoduje o všem.</strong> S ekvitermní křivkou 50/35 °C vychází SPF {kc(M.SPF_CALC, 2)}, při pevných 55 °C jen {kc(M.SPF_W55, 2)}, což už je jen o málo lepší než elektrokotel.
Objektům, které potřebují stále 55 °C a víc, mobilní TČ nenabízet.</li>
<li><strong>Kontejner zdražuje malé sestavy.</strong> Jádro kontejneru stojí kolem {czk(core_sum)} bez ohledu na počet jednotek.
M25 vychází na {czk(cap['M25'][2] / 25)}/kW, M100 na {czk(cap['M100'][2] / 100)}/kW. Flotilu stavět na M50–M100; M25 je kontejner M50 osazený jednou jednotkou.</li>
<li><strong>Proti naftě vyhrává TČ od 20 MWh měsíčně</strong>, ale jen o {pct((r20['diesel'] - r20['hp']) / r20['diesel'])} (M50) až {pct((r30['diesel'] - r30['hp']) / r30['diesel'])} (M75). Proti lehkému topnému oleji, LPG a zemnímu plynu
při elektřině {czk(M.EL)}/MWh nevyhrává. Při 10 MWh (M25) je dražší než nafta.</li>
<li><strong>Pro nás rozhoduje obsazenost.</strong> Při 3 měsících v roce se žádná sestava nezaplatí. M100 se vrací za {kc(pb[('M100', 'market', 6)]['pb'], 1)} roku při 6 měsících
a za {kc(pb[('M100', 'market', 9)]['pb'], 1)} roku při 9 měsících. <strong>RH X50 umí chladit</strong> (34,5 kW při 35 °C), takže letní pronájem jako mobilní chladicí zdroj je nejsilnější páka.</li>
<li><strong>Zvýhodněný ceník (B) se sám nezaplatí</strong>, jen spolu s marží trvalé kotelny nebo servisní smlouvy.</li>
</ul>

<h2><span class="sec">Umístění</span>Kde budou venkovní jednotky</h2>
<p>Podmínky z návodu: sání vzduchu ze všech čtyř stran s volným prostorem ≥ 0,5 m, výfuk ventilátorem nahoru s volným prostorem ≥ 2 m,
jednotka min. 300 mm (při sněhu 500 mm) nad terénem, na antivibračním uložení, s dobrým odvodem kondenzátu a mimo zdroje vznícení (R290).
Porovnání tří variant:</p>
{var_tbl}

<h3>Doporučená dispozice: varianta B</h3>
<div class="fig">{svg_container()}</div>
<ul>
<li><strong>Technická místnost</strong> ({kc(M.TECH_LEN, 2)} m u původních dveří kontejneru): akumulace 1 000 l (s izolací ⌀ ~1 m, výška do 2,2 m; vnitřní výška kontejneru 2,39 m),
deskový výměník, čerpadla, expanzomaty, rozvaděč, regulace, měření. Zamčená původními dveřmi kontejneru, zateplená, temperovaná.</li>
<li><strong>Vzduchová komora</strong> ({kc(M.AIR_LEN, 2)} m): 0,5 m + jednotka 0,98 m + 1,0 m mezi jednotkami + jednotka + 0,5 m. Jednotka stojí napříč (1,195 m),
k bočnicím zbývá po 0,62 m. Střecha vyřezaná, nahoře ochranná mříž s velkým volným průřezem; bočnice nahrazené uzamykatelnými mřížovými panely, které se pro servis otevírají.</li>
<li><strong>Výfukový nástavec</strong> vyvede studený vzduch nad úroveň střechy, aby se nenasával zpět bočnicemi. Nutný souhlas výrobce (tlaková rezerva ventilátoru).</li>
<li><strong>Výška:</strong> podlaha kontejneru a rám dávají ≈ 0,5 m nad terénem (splňuje i požadavek pro sníh), vršek jednotky je ≈ 2,1 m nad podlahou, pod horní hranou kontejneru.
Souprava na nákladním autě ≈ 3,85 m, pod limitem 4,0 m.</li>
<li><strong>R290:</strong> komora je volný prostor (otevřená nahoru, pororošt dole); propan je těžší než vzduch a odteče pod kontejner. Přepážka k technické místnosti je plynotěsná,
prostupy utěsněné, žádné otvory u podlahy; v technické místnosti detektor hořlavého plynu, který odpojí napájení. Uspořádání posoudit podle EN 378.</li>
<li><strong>Kondenzát a led</strong> padají pororoštem pod kontejner. Kontejner stojí na patkách ≥ 0,2 m nad terénem, pod komorou je štěrk nebo vyhřívaný žlab se svodem, aby led nevyrostl až k roštu.</li>
<li><strong>Statika:</strong> vyřezané stěny a střechu nahradí výztužný rám; zvedání za spodní rohové odlitky nebo na hákovém rámu. Volitelně <strong>hákový (abroll) rám</strong>
(+ ~35 tis. Kč): kontejner naloží a složí běžný hákový nosič bez jeřábu, mobilizace je levnější a rychlejší.</li>
</ul>

<h2><span class="sec">Elektro</span>Elektrické připojení podle návodu RH X50</h2>
{unit_tbl}
<h3>Přívod podle sestavy</h3>
<p>Hlavní jistič = součet max. proudů jednotek + pomocné okruhy (čerpadla, regulace, osvětlení, temperování ~{M.AUX_A} A) s rezervou pro selektivitu vůči jističům jednotek 40 A.
Patrony v akumulaci (2× 6 kW) se do přívodu nepočítají: regulace je pustí jen při odmrazování nebo výpadku kompresoru. Kabel H07RN-F do 25 m, u delších tras přepočítat úbytek napětí
(návod: start při ≥ 90 % jmenovitého napětí).</p>
{elec_tbl}
<ul>
<li><strong>Odbočka pro každou jednotku:</strong> jistič 40 A, proudový chránič typ B (invertorový kompresor; návod žádá ochranu proti úniku proudu), kabel 5×10 mm², uzemnění.</li>
<li><strong>M75 a M100</strong> mají dva přívody: kontejner 3×80 A a skid 3×50 A nebo 3×80 A. Často je to výhoda: dva menší vývody se najdou snáz než jeden 3×160 A.</li>
<li>Provozní proud při −15 °C / 50 °C je asi {kc(I50)} A na jednotku, tedy méně než 32 A. Jistit pod hodnoty z návodu jde jen s písemným souhlasem výrobce, např. s nastaveným omezením výkonu.</li>
<li>Bytový dům mívá hlavní jistič 3×80–160 A, M50 se tam vejde jen výjimečně. Typická místa pro M50 a větší jsou průmyslové a komerční objekty, staveniště s vlastní trafostanicí a kotelny s vlastním vývodem.</li>
<li><strong>Postup při nasazení:</strong> připojit napájení, 12 h předehřev kompresorů (podle návodu), teprve pak spustit. Napájení v zimě nevypínat, jinak nefunguje ochrana proti zamrznutí.</li>
<li>Navýšení rezervovaného příkonu u distributora trvá týdny až měsíce, na krátký pronájem se nevyplatí. U zápočtové varianty C je potřeba i pro trvalou kotelnu, takže ho uděláme dopředu.</li>
</ul>

<h2><span class="sec">Výkon</span>Sestavy a topný faktor</h2>
{sizes_tbl}
<p>Podle křivek výrobce dává jednotka při −15 °C a 50 °C {kc(cap50, 1)} kW při příkonu {kc(pw50, 1)} kW (COP {kc(cap50 / pw50, 2)}); garantujeme 25 kW.
Sezónní topný faktor je spočítaný binovou metodou: {kc(sum(M.bins().values()))} hodin topné sezóny podle venkovní teploty, lineární potřeba tepla s nulou při +15 °C,
modulace mezi křivkou MIN a MAX, pod výkonem MIN taktování (+5 %), odmrazování mezi −7 a +5 °C (+5 %), oběhová čerpadla (+3 %) a oddělovací výměník s glykolem (+3 %).</p>
{spf_tbl}
<p class="note">V dalších výpočtech je SPF {kc(M.SPF, 1)}. Ekvitermní regulace je v nabídce povinná: zákazník musí připustit nižší teplotu vody, když venku není mráz.</p>

<h2><span class="sec">Technika</span>Bivalence, hluk, logistika</h2>
<h3>Bivalence</h3>
<p>Sestava je dimenzovaná na −15 °C. Pod touto teplotou, při odmrazování a při poruše kompresoru kryje deficit tento zdroj (regulace RH X50 umí řídit pomocný zdroj; při odmrazování ho zapne, když výstupní voda klesne pod 16 °C):</p>
<ul>
<li><strong>Stávající zdroj objektu</strong>, pokud je funkční (zkouška před koupí, částečná rekonstrukce). Nejlevnější.</li>
<li><strong>Patrony v akumulaci</strong> 2× 6 kW, s blokací proti současnému chodu kompresorů na maximum.</li>
<li><strong>Záložní naftový modul</strong> (přinajímaný) pro kritické objekty bez vlastního zdroje.</li>
</ul>
<p>Smluvně garantujeme výkon při −15 °C, ne teplotu v objektu.</p>
<h3>Hluk</h3>
<p>Návod uvádí ≤ {U['lp_1m']} dB(A). Pokud jde o akustický tlak v 1 m, je akustický výkon asi {M.UNIT_LW} dB(A) na jednotku. Limit v chráněném venkovním prostoru staveb je 50 dB(A) ve dne a 40 dB(A) v noci.
Orientačně pro volné šíření nad odrazivou plochou:</p>
{noise_tbl}
<p class="note">Hluk je vedle jističe druhá hlavní překážka: M50 potřebuje v noci kolem {kc(M.dist_for(2, 40))} m od oken. Technická místnost stíní jeden směr, proto kontejner stavíme
technickou místností k nejbližší obytné budově. Dále: tichý noční režim s nižším výkonem, akustické lamely místo mřížových panelů (ověřit vliv na průtok vzduchu) a výpočet hluku jako příloha nabídky.</p>
<h3>Logistika</h3>
<ul>
<li>Kontejner M50 váží ≈ {kc((M.CONT['tare'] + 2 * U['mass'] + 1200) / 1000, 1)} t bez vody (akumulace se plní na místě). Veze ho auto s hydraulickou rukou 7,5–12 t nebo hákový nosič; skid druhou jízdou nebo na přívěsu.</li>
<li>Plocha 7 × 3,5 m (kontejner + obslužný prostor), zpevněná a rovná; pro M75/M100 dalších 4,5 × 3,5 m pro skid (4,0 × 2,4 m, jednotky se stejnými odstupy jako v kontejneru).</li>
<li>Montáž 1 den (napojení hadic DN50, kabel, plnění, odvzdušnění) + 12 h předehřev. Demontáž půl dne.</li>
<li>Sklad se 2–3 kontejnery připravenými k odjezdu je podmínka pro havarijní zakázky.</li>
</ul>

<h2><span class="sec">Investice</span>CAPEX</h2>
<p>Jádro kontejneru je společné pro všechny sestavy (připravené pro 2 jednotky). Ceny kromě RH X50 jsou odhady pro prvních 3–5 kusů.</p>
{capex_tbl}
<h3>Náklady jednoho nasazení</h3>
{deploy_tbl}
<p><strong>Doporučený start flotily:</strong> 3 kontejnery vybavené pro M100 (12 jednotek RH X50) = {czk(3 * cap['M100'][2])}, plus vývoj kontejneru
(projekt, statika, EN 378, prototyp, CE) {czk(M.DEV_ONE_OFF)}. Celkem <strong>{czk(fleet)}</strong>. Jednotky se dají přesouvat: flotila pokryje
např. 1× M100 + 2× M50 a 2 jednotky v záloze, nebo 3× M75 a 3 jednotky navíc.</p>
<p class="note">Cesty k nižšímu CAPEX: sériová výroba kontejneru (≥ 5 ks, −10–15 %), jednodušší rozvaděč u M25, sdílený skid. Proti skidu bez kontejneru je kontejner dražší asi o 300–400 tis. Kč, zato je zamčený, převáží se vcelku a má vyšší zůstatkovou hodnotu.</p>

<h2><span class="sec">Cenotvorba</span>Ceník pro tři typy zákazníků</h2>
{price_tbl}
<h3>A · Tržní pronájem</h3>
<ul>
<li>Minimální doba 1 měsíc; kratší nasazení denní sazbou 1/20 měsíčního nájmu. Mobilizace platí vždy.</li>
<li>V nájmu: sestava, telemetrie, servis, zásah do 24 h, pojištění. Elektřinu platí zákazník (vlastní odběr nebo podružný elektroměr).</li>
<li>Mimo topnou sezónu (duben–září) sleva 25 % pro stavby a technologii; chlazení zvláštním ceníkem.</li>
<li>Referenční cena ze zahraničí je 65 tis. Kč/měsíc za 100 kW. Náš M100 za {czk(M.RENT['M100'])} je nad ní, protože zahrnuje zamčený kontejner,
telemetrii a servis. Za 65 tis. Kč by se M100 při 6 měsících obsazenosti vracela asi 5,5 roku.</li>
</ul>
<h3>B · Zvýhodněný pronájem pro našeho zákazníka</h3>
<ul>
<li>Pro zákazníky s rozjednanou nebo podepsanou kotelnou, servisní smlouvou nebo teplem jako službou: nájem −{pct(M.DISC_RENT)}, mobilizace −{pct(M.DISC_MOBIL)}, bez kauce, přednost při havárii.</li>
<li>Sám se nezaplatí, proto B jen vázaně na zakázku a nejvýš na ~40 % obsazenosti flotily.</li>
</ul>
<h3>C · Pronájem se zápočtem na trvalou kotelnu</h3>
<ul>
<li>Zákazník platí tržní nájem. Když do 3 měsíců od vrácení objedná trvalou kotelnu, odečteme {pct(M.CREDIT_SHARE)} zaplaceného nájmu, max. {pct(M.CREDIT_CAP)} ceny kotelny.</li>
<li>Příklad: M50 na {cr['months']} měsíce = {czk(cr['paid'])} nájmu → zápočet {czk(cr['credit'])} (strop {czk(cr['cap'])} u kotelny za {czk(cr['perm'])}).
Z předpokládané marže kotelny {czk(cr['margin'])} zbývá {czk(cr['margin_after'])}.</li>
<li>Obchodně nejsilnější varianta: pronájem je placená zkouška. Kalorimetr a elektroměr změří skutečnou potřebu tepla a SPF na objektu, což je nejlepší podklad pro trvalou kotelnu.
Kontejnerová kotelna navíc může u zákazníka zůstat natrvalo (odkup).</li>
</ul>

<h2><span class="sec">Srovnání</span>Celková cena za 1 MWh tepla</h2>
<p>Cena tepla = (měsíční nájem + mobilizace rozpuštěná do {M.MONTHS} měsíců) ÷ odebrané MWh + energie na 1 MWh tepla. Alternativy ve srovnatelné velikosti.</p>
{mwh_tbl}
<h3>Předpoklady: energie</h3>
{energy_tbl}
<h3>Předpoklady: nájem alternativ</h3>
{rent_alt_tbl}
<p class="note">Nájmy alternativ jsou odhad k ověření. Od roku 2028 může ETS2 podle aktuálně uváděných informací zvýšit ceny fosilních paliv; povolenky nakupují dodavatelé paliv a náklady se mohou promítnout do cen. V tabulkách to není započteno.</p>

<h2><span class="sec">Citlivost</span>Cena elektřiny, teplota soustavy a paliva</h2>
<h3>TČ M50 podle ceny elektřiny a SPF (Kč/MWh tepla, 20 MWh/měsíc)</h3>
{sel_tbl}
<h3>Alternativy podle ceny paliva (Kč/MWh tepla)</h3>
{sfu_tbl}
<ul>
<li>Bod zvratu M50 při 20 MWh/měsíc: proti naftě při elektřině {czk(be_d)}/MWh, proti LTO {czk(be_l)}/MWh, proti zemnímu plynu {czk(be_g)}/MWh.</li>
<li>Víc než cena elektřiny rozhoduje teplota soustavy: přechod z pevných 55 °C na ekviterm sníží cenu energie z {czk(M.EL / M.SPF_W55)} na {czk(M.EL / M.SPF_CALC)} za MWh.</li>
<li>Nejlepší cílová skupina je zákazník s vlastní levnou elektřinou (průmysl, FVE, 3 000–3 500 Kč/MWh).</li>
</ul>

<h2><span class="sec">Návratnost</span>Ekonomika pro nás podle obsazenosti</h2>
<p>Provozní cash flow jedné sestavy za rok a prostá návratnost. Průměrné nasazení 3 měsíce (3 / 6 / 9 měsíců = 1 / 2 / 3 nasazení). IRR na {M.LIFETIME} let se zůstatkovou hodnotou {pct(M.RESIDUAL)}.</p>
{pb_tbl}
{pb_detail}
<ul>
<li><strong>Kontejnerová platforma potřebuje 6 a víc měsíců obsazenosti</strong> a větší sestavy. M25 se nevyplatí stavět samostatně.</li>
<li><strong>Letní chlazení</strong> (akce, stany, technologie, serverovny, výroba) dělá z kontejneru celoroční produkt. Jednotky dodávají vodu 7 °C, odběratel ji připojí přes fancoily nebo výměník.</li>
<li>Letní vysoušení staveb (nízká teplota vody, SPF přes 3) a ohřev vody pro bazény a sportoviště.</li>
</ul>

<h2><span class="sec">Hranice</span>Kdy TČ nedává smysl</h2>
<div class="cols"><ul>
<li><strong>Soustava potřebuje stále 55 °C a víc</strong> (90/70, poddimenzovaná tělesa, pára). SPF pod 2.</li>
<li><strong>Chybí přívod 3×80 A</strong> pro M50 (3×50 A pro M25) a navýšení nestihneme. Dieselagregát ekonomiku zruší.</li>
<li><strong>Krátké nasazení</strong> do ~3 týdnů: mobilizace převáží úsporu energie.</li>
<li><strong>Malý odběr</strong> pod ~12 MWh/měsíc: cenu tepla tvoří hlavně nájem, M25 je dražší než nafta.</li>
<li><strong>Funkční plynová přípojka</strong>, kde jde jen o náhradu kotle: mobilní plynový kotel je levnější.</li>
<li><strong>Kritický objekt bez zálohy</strong> v extrémních mrazech.</li>
<li><strong>Hlukově citlivé místo</strong> bez odstupu 15–25 m od oken.</li>
<li><strong>Nepřístupné místo</strong> pro kontejner (vnitroblok, průjezd pod 4 m) nebo bez možnosti splnit podmínky pro R290.</li>
</ul></div>

<h2><span class="sec">Rizika</span>Rizika a opatření</h2>
{risk_tbl}

<h2><span class="sec">Obchod</span>Struktura nabídky zákazníkovi</h2>
<ul>
<li><strong>Vaše situace</strong>: objekt, důvod (havárie, rekonstrukce, stavba, zkouška), termín a doba, teplota soustavy, měsíční odběr.</li>
<li><strong>Navržená sestava</strong>: M25–M100, garantovaný výkon při −15 °C, bivalence.</li>
<li><strong>Cena tepla za MWh</strong> nahoře jedním číslem, vedle ceny tepla ze srovnatelné naftové kotelny; pod tím rozpad na nájem, mobilizaci a elektřinu.</li>
<li><strong>Co je v ceně</strong>: kontejnerová kotelna, doprava, napojení, telemetrie, servis do 24 h, pojištění.</li>
<li><strong>Co zajistí zákazník</strong>: přívod s daným jištěním a konektorem, plochu 7 × 3,5 m, příjezd pro nákladní auto, napojovací místo na topné soustavě, elektřinu.</li>
<li><strong>Umístění a hluk</strong>: situační náčrt, orientace kontejneru, odstupy.</li>
<li><strong>Podmínky</strong>: minimální doba, kauce, fakturace, odpovědnost, pojištění.</li>
<li><strong>Zápočet na trvalou kotelnu</strong>: kolik z nájmu se vrátí.</li>
<li><strong>Další krok</strong>: prohlídka (jistič, teplota soustavy, místo), termín, kontakt.</li>
</ul>

<h2><span class="sec">Argumentace</span>Proč sledovat cenu za MWh, ne nájem</h2>
<div class="formula"><code>cena tepla = (nájem + mobilizace) ÷ MWh  +  energie na 1 MWh</code></div>
<p class="pitch">„Nájem je vstupenka, teplo je účet. Naftová kotelna má levnou vstupenku a drahý účet. U tepelného čerpadla je to naopak,
a účet platíte každý den, kdy topíte."</p>
<p>Příklad pro objekt s odběrem 20 MWh v lednu:</p>
{pitch_tbl}
<p>Pro obchodníky jedna věta: <strong>každých 10 MWh tepla stojí z nafty zhruba {czk(10 * M.heat_price('diesel'))},
z tepelného čerpadla {czk(10 * M.heat_price('hp'))}.</strong> Rozdíl {czk(10 * (M.heat_price('diesel') - M.heat_price('hp')))} na každých 10 MWh
platí vyšší nájem. Čím víc zákazník topí a čím nižší teplotu soustava snese, tím víc ušetří.</p>
<p>Po skončení pronájmu dostane zákazník report z kalorimetru a elektroměru: kolik MWh odebral, kolik to stálo a kolik by stála nafta.</p>

<h2><span class="sec">Postup</span>Další kroky</h2>
<ul>
<li>Dotazy na výrobce (hluk, omezení příkonu, výfukové nástavce, provoz v komoře) a posouzení R290 podle EN 378.</li>
<li>Poptat konverzi kontejneru a postavit prototyp M50; změřit hluk, recirkulaci a SPF.</li>
<li>Telefonický průzkum nájmů 5–6 půjčoven mobilních kotelen (25–100 kW) a mobilních chladicích zdrojů.</li>
<li>Smluvní podmínky nájmu, předávací protokol, formulář požadavků na místo (jistič, konektor, plocha, teplota soustavy).</li>
<li>Pilotní nasazení u vlastního zákazníka ve variantě C, první sezóna s měřením.</li>
</ul>
<p class="small">Model: <code>mobilni-kotelna-tc/src/model.py</code>, data jednotky z návodu a výkonových křivek RH X50. Všechna čísla jsou generovaná z modelu; orientační, bez garance úspor.</p>
</main>
"""

OUT.write_text(html, encoding="utf-8")
print("zapsáno:", OUT)
