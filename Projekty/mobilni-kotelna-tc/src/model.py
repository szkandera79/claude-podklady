#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pronájem mobilních kotelen s TČ RH X50 v kontejneru 20' — výpočetní model.

Jediný zdroj čísel pro model.html (build_model.py je z tohoto modulu generuje).
Všechny ceny jsou BEZ DPH. Údaje o jednotce jsou z návodu RH X50
a z výkonových křivek výrobce (rh_x50_krivky.json). Předpoklady označené [OVĚŘIT]
jsou odhady, které je třeba potvrdit poptávkou / průzkumem trhu.
    python3 mobilni-kotelna-tc/src/model.py
"""
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CURVES = json.loads((HERE / "rh_x50_krivky.json").read_text())

# ---------------------------------------------------------------- RH X50 (návod k použití, kap. 2.2, 2.6, 2.11)
UNIT = dict(
    name="RH X50", price=110_000,
    kw_15=25,                 # obchodně garantovaný výkon při −15 °C / W50 (křivky: W45 27,3 kW, W55 24,8 kW)
    el_max_kw=20, a_max=32, breaker=40, wire_mm2=10,     # návod: max. příkon, max. proud, jistič, vodič
    refrigerant="R290", charge_kg=4.0,
    lp_1m=62,                 # návod: hlučnost ≤ 62 dB(A); předpoklad = akust. tlak v 1 m [OVĚŘIT]
    mass=370, dims=(1195, 980, 1900),                    # D × Š × V mm
    clear_side=0.5, clear_top=2.0, base_min=0.3, base_snow=0.5,
    water_out=(20, 78), amb=(-25, 43), pipe='G 1½"',
)
UNIT_LW = UNIT["lp_1m"] + 8          # z Lp v 1 m nad odrazivou plochou → akustický výkon

# ---------------------------------------------------------------- kontejner 20' ISO
CONT = dict(ext=(6058, 2438, 2591), int=(5898, 2352, 2393), tare=2200)
AIR_LEN = 0.5 + 0.98 + 1.0 + 0.98 + 0.5          # vzduchová komora pro 2 jednotky (m)
TECH_LEN = CONT["int"][0] / 1000 - AIR_LEN - 0.1  # technická místnost (m), 0,1 m přepážka

# ---------------------------------------------------------------- CAPEX
CORE = [   # kontejnerové jádro: technická místnost + vzduchová komora pro 2 jednotky
    ("Kontejner 20' (použitý, cargo worthy)", 60_000),
    ("Konstrukční úpravy vzduchové komory: výřez střechy a bočnic, výztužný rám, statický posudek", 75_000),
    ("Plynotěsná přepážka mezi komorami, utěsněné prostupy", 18_000),
    ("Technická místnost: zateplení, obklad, podlaha, větrací mřížky", 32_000),
    ("Vzduchová komora: pororošt podlahy, uzamykatelné mřížové panely, ochranná mříž shora", 48_000),
    ("Detektor úniku R290, osvětlení, zásuvky, temperování technické místnosti", 22_000),
    ("Nátěr, značení, bezpečnostní tabulky R290", 12_000),
    ("Akumulační nádrž 1 000 l, izolovaná, 2× el. patrona 6 kW", 52_000),
    ("Deskový výměník 100 kW + glykolová náplň primáru", 52_000),
    ("Hydraulika: čerpadla, expanzomaty, pojistné ventily, magnetický filtr, armatury, izolace", 80_000),
    ("Rychlospojky + 2× 15 m izolované flexi hadice DN50", 45_000),
    ("Měření: kalorimetr MID + elektroměr MID", 16_000),
    ("Hlavní rozvaděč 80 A: vypínač, přepěťová ochrana, pomocné okruhy, přívodka CEE 125 A", 38_000),
    ("Přívodní kabel H07RN-F 5×25 mm², 25 m, s vidlicí CEE 125 A", 26_000),
    ("Regulace kaskády, ekviterm, telemetrie GSM", 35_000),
    ("Kompletace ve výrobě, tlakové zkoušky, oživení", 70_000),
    ("Výchozí revize, posouzení umístění R290 (EN 378), dokumentace, CE", 35_000),
    ("Podkladní patky / roznášecí panely", 8_000),
]
PER_UNIT = [  # na každou osazenou jednotku RH X50
    ("Tepelné čerpadlo RH X50", UNIT["price"]),
    ("Odbočka v rozvaděči: jistič 40 A + proudový chránič typ B, kabel 5×10 mm², komunikace", 24_000),
    ("Antivibrační uložení, kotvení, výfukový nástavec proti recirkulaci", 14_000),
    ("Hydraulické napojení jednotky: flexi, uzávěry, filtr, zpětná klapka", 12_000),
]
SKID = [      # venkovní skid pro 3. a 4. jednotku (M75/M100)
    ("Pozinkovaný skid s kapsami pro VZV, uzamykatelná mřížová klec", 55_000),
    ("Propojení s kontejnerem: 2× 10 m DN50 + rychlospojky", 30_000),
    ("Rozvaděč skidu 80 A + vlastní přívod 5×25 mm² s CEE 125 A", 50_000),
]
RESERVE = 0.07
DEV_ONE_OFF = 250_000    # vývoj kontejneru: projekt, statika, EN 378, prototyp, CE (rozpustit do flotily)

PRODUCTS = {  # sestava: (počet jednotek, skid)
    "M25": (1, False), "M50": (2, False), "M75": (3, True), "M100": (4, True),
}


def capex_items(p):
    n, skid = PRODUCTS[p]
    items = list(CORE)
    items += [(f"{name} ({n}×)" if n > 1 else name, v * n) for name, v in PER_UNIT]
    if skid:
        items += SKID
    return items


def capex(p):
    base = sum(v for _, v in capex_items(p))
    return base, base * RESERVE, base * (1 + RESERVE)


# náklad jednoho nasazení (do 100 km); kontejner = jedna jízda HDS/hákový nosič, skid druhá
DEPLOY_BASE = [("Doprava kontejneru tam a zpět (HDS / hákový nosič, do 100 km)", 24_000),
               ("Napojení hydrauliky, plnění, odvzdušnění", 9_000),
               ("Elektro napojení, měření, protokol", 7_000),
               ("Uvedení do provozu, nastavení kaskády", 5_000),
               ("Demontáž, vypuštění", 6_000),
               ("Kontrola a čištění po návratu", 7_000)]
DEPLOY_SKID = 20_000     # doprava + napojení skidu


def deploy_cost(p):
    return sum(v for _, v in DEPLOY_BASE) + (DEPLOY_SKID if PRODUCTS[p][1] else 0)


# roční fixní náklady na 1 sestavu
INSURANCE, MAINT = 0.012, 0.025
TELEMETRY, STORAGE = 3_000, 15_000
SALES_COMM = 0.05
LIFETIME, RESIDUAL = 8, 0.15      # kontejner má vyšší zůstatkovou hodnotu než skid

# ---------------------------------------------------------------- ceník
RENT = {"M25": 30_000, "M50": 45_000, "M75": 62_000, "M100": 78_000}
MOBIL = {"M25": 50_000, "M50": 55_000, "M75": 70_000, "M100": 75_000}
DISC_RENT, DISC_MOBIL = 0.20, 0.50
CREDIT_SHARE, CREDIT_CAP = 0.50, 0.08
PERM_PRICE = {"M25": 1_350_000, "M50": 1_600_000, "M75": 1_990_000, "M100": 2_380_000}
PERM_MARGIN = 0.22               # [OVĚŘIT interně]

# ---------------------------------------------------------------- elektrické připojení (dle návodu)
AUX_A = 4                        # čerpadla, regulace, osvětlení, temperování
BREAKERS = (40, 50, 63, 80, 100, 125, 160, 200)
CABLE = {50: "5×10 mm²", 80: "5×25 mm²", 125: "5×50 mm²", 160: "5×70 mm²"}   # H07RN-F, do 25 m [OVĚŘIT úbytek]


def electrical(p):
    n, skid = PRODUCTS[p]
    if skid:   # kontejner (2 jednotky) + skid (n-2 jednotek), každý vlastní přívod
        parts = [(2, "kontejner"), (n - 2, "skid")]
    else:
        parts = [(n, "kontejner")]
    out = []
    for k, where in parts:
        a = k * UNIT["a_max"] + (AUX_A if where == "kontejner" else 1)
        main = next(b for b in BREAKERS if b >= a * 1.1 and b > UNIT["breaker"])
        out.append(dict(where=where, units=k, a=a, main=main, kw=k * UNIT["el_max_kw"] + (2 if where == "kontejner" else 0.3),
                        cable=CABLE.get(main, CABLE[min(c for c in CABLE if c >= main)]),
                        plug="CEE 63 A" if main <= 63 else "CEE 125 A"))
    return out


# ---------------------------------------------------------------- SPF z výkonových křivek (binová metoda)
def _interp(xs, ys, x):
    pts = [(a, b) for a, b in zip(xs, ys) if b is not None]
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def perf(t_amb, t_w, mode):
    """Výkon a příkon jednotky (kW) při venkovní teplotě a výstupní vodě; mode MAX/MIN."""
    ws = [35, 45, 55]
    t_w = min(max(t_w, 35), 55)
    lo = max(w for w in ws if w <= t_w)
    hi = min(w for w in ws if w >= t_w)
    res = []
    for key in ("cap", "inp"):
        a = _interp(CURVES["amb_heat"], CURVES["heat"][str(lo)][mode][key], t_amb)
        b = _interp(CURVES["amb_heat"], CURVES["heat"][str(hi)][mode][key], t_amb)
        res.append(a if lo == hi else a + (b - a) * (t_w - lo) / (hi - lo))
    return res


# roční četnost hodin venkovních teplot, střední Čechy (orientačně, topná sezóna do +15 °C)
def bins():
    mu, sd, total = 4.0, 5.8, 5_600
    raw = {t: math.exp(-((t - mu) ** 2) / (2 * sd ** 2)) for t in range(-18, 16)}
    s = sum(raw.values())
    return {t: total * v / s for t, v in raw.items()}


def spf(t_design=-15, w_design=50, w_mild=35, t_limit=15, fixed_w=None, defrost=0.05, aux=0.03, hx=0.03):
    """Sezónní topný faktor soustavy: 1 jednotka, výkon navržen = výkon jednotky při −15 °C."""
    cap_d, _ = perf(t_design, w_design, "MAX")
    q = e = 0.0
    for t, h in bins().items():
        load = cap_d * min(1, (20 - t) / (20 - t_design)) if t < t_limit else 0
        if load <= 0:
            continue
        tw = fixed_w or w_design + (w_mild - w_design) * (t - t_design) / (t_limit - t_design)
        cmax, pmax = perf(t, tw, "MAX")
        cmin, pmin = perf(t, tw, "MIN")
        if load >= cmax:        # deficit kryje patrona (COP 1)
            el = pmax + (load - cmax)
        elif load <= cmin:      # taktování na minimu, 5 % ztráta
            el = pmin * load / cmin * 1.05
        else:                   # modulace mezi MIN a MAX
            r = (load - cmin) / (cmax - cmin)
            cop = cmin / pmin + (cmax / pmax - cmin / pmin) * r
            el = load / cop
        if -7 <= t <= 5:
            el *= 1 + defrost
        q += load * h
        e += el * h
    unit = q / e
    return unit / (1 + aux + hx), unit, q / 1000


SPF_CALC = spf()[0]
SPF_W55 = spf(fixed_w=55)[0]
SPF_LOW = spf(w_design=40, w_mild=30)[0]    # podlahovka / vysoušení staveb
SPF = round(SPF_CALC, 1)

# ---------------------------------------------------------------- energie a alternativy
EL = 4_500
DIESEL, LTO = 30.0, 26.0
OIL_KWH_L, OIL_EFF = 10.0, 0.90
GAS, GAS_EFF = 1_800, 0.93
LPG, LPG_KWH_L = 16.0, 6.6
EL_BOILER_EFF = 0.99
ALT = {"diesel": "Nafta (mobilní kotelna)", "lto": "Lehký topný olej", "lpg": "Plyn LPG (mobilní + nádrž)",
       "gas": "Zemní plyn (přípojka)", "elk": "Elektrokotel"}
ALT_RENT = {"diesel": (18_000, 25_000, 32_000), "lto": (18_000, 25_000, 32_000),
            "lpg": (22_000, 29_000, 36_000), "gas": (20_000, 27_000, 34_000), "elk": (9_000, 12_000, 15_000)}
ALT_MOBIL = {"diesel": 25_000, "lto": 25_000, "lpg": 35_000, "gas": 35_000, "elk": 15_000}


def heat_price(tech, el=EL, spf_=None, diesel=DIESEL, lto=LTO, gas=GAS, lpg=LPG):
    spf_ = spf_ or SPF
    return {"hp": el / spf_, "diesel": diesel / (OIL_KWH_L * OIL_EFF) * 1000,
            "lto": lto / (OIL_KWH_L * OIL_EFF) * 1000, "lpg": lpg / (LPG_KWH_L * GAS_EFF) * 1000,
            "gas": gas / GAS_EFF, "elk": el / EL_BOILER_EFF}[tech]


SCEN = [(10, "M25", 0), (20, "M50", 1), (30, "M75", 2)]   # MWh v lednu → sestava → velikost alternativ
MONTHS = 4


def mwh_table(el=EL, spf_=None):
    rows = []
    for mwh, p, i in SCEN:
        r = {"mwh": mwh, "set": p, "hp_rent": (RENT[p] + MOBIL[p] / MONTHS) / mwh}
        r["hp"] = r["hp_rent"] + heat_price("hp", el, spf_)
        for t in ALT:
            r[t] = (ALT_RENT[t][i] + ALT_MOBIL[t] / MONTHS) / mwh + heat_price(t, el, spf_)
        rows.append(r)
    return rows


def breakeven_el(i=1, alt="diesel"):
    mwh, p, k = SCEN[i]
    alt_total = (ALT_RENT[alt][k] + ALT_MOBIL[alt] / MONTHS) / mwh + heat_price(alt)
    return (alt_total - (RENT[p] + MOBIL[p] / MONTHS) / mwh) * SPF


def sens_el(i=1, els=(3_000, 4_000, 4_500, 5_000, 6_000, 7_000)):
    mwh, p, _ = SCEN[i]
    fixed = (RENT[p] + MOBIL[p] / MONTHS) / mwh
    spfs = (round(SPF_W55, 1), SPF, round(SPF_LOW, 1))
    return {s: [fixed + el / s for el in els] for s in spfs}, els


def sens_fuel(i=1, factors=(0.8, 1.0, 1.2, 1.4)):
    mwh, _, k = SCEN[i]
    out = {}
    for t in ALT:
        fixed = (ALT_RENT[t][k] + ALT_MOBIL[t] / MONTHS) / mwh
        out[t] = [fixed + (EL * f / EL_BOILER_EFF if t == "elk" else heat_price(t) * f) for f in factors]
    return out, factors


def payback(p, months, tier="market"):
    cap = capex(p)[2]
    rent = RENT[p] * (1 - DISC_RENT if tier == "disc" else 1)
    mob = MOBIL[p] * (1 - DISC_MOBIL if tier == "disc" else 1)
    dep = max(1, round(months / 3))
    revenue = rent * months + mob * dep
    var = deploy_cost(p) * dep + rent * months * SALES_COMM
    fixed = cap * (INSURANCE + MAINT) + TELEMETRY + STORAGE
    cf = revenue - var - fixed
    flows = [-cap] + [cf] * LIFETIME
    flows[-1] += cap * RESIDUAL
    return dict(p=p, months=months, tier=tier, deployments=dep, revenue=revenue, var=var, fixed=fixed,
                cf=cf, pb=cap / cf if cf > 0 else float("inf"), irr=_irr(flows), cap=cap)


def payback_mix(p, months, disc_share=0.4):
    a, b = payback(p, months), payback(p, months, "disc")
    cf = a["cf"] * (1 - disc_share) + b["cf"] * disc_share
    return dict(cf=cf, pb=a["cap"] / cf if cf > 0 else float("inf"))


def _irr(flows):
    npv = lambda r: sum(f / (1 + r) ** t for t, f in enumerate(flows))
    lo, hi = -0.99, 2.0
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if npv(lo) * npv(mid) <= 0 else (mid, hi)
    return mid


def credit_example(p="M50", months=4):
    paid = RENT[p] * months
    credit = min(paid * CREDIT_SHARE, PERM_PRICE[p] * CREDIT_CAP)
    margin = PERM_PRICE[p] * PERM_MARGIN
    return dict(p=p, months=months, paid=paid, credit=credit, cap=PERM_PRICE[p] * CREDIT_CAP,
                perm=PERM_PRICE[p], margin=margin, margin_after=margin - credit)


def noise(n_units, r):
    return UNIT_LW + 10 * math.log10(n_units) - 20 * math.log10(r) - 8


def dist_for(n_units, limit):
    return 10 ** ((UNIT_LW + 10 * math.log10(n_units) - 8 - limit) / 20)


if __name__ == "__main__":
    print(f"vzduchová komora {AIR_LEN:.2f} m, technická místnost {TECH_LEN:.2f} m")
    print(f"SPF ekviterm 50/35: {SPF_CALC:.2f} (jednotka {spf()[1]:.2f}), W55 pevně: {SPF_W55:.2f}, 40/30: {SPF_LOW:.2f}")
    print("výkon −15/W50:", [round(x, 1) for x in perf(-15, 50, "MAX")])
    for p in PRODUCTS:
        b, r, t = capex(p)
        print(f"{p}: CAPEX {t:,.0f}  ({t / (PRODUCTS[p][0] * 25):,.0f} Kč/kW)  nasazení {deploy_cost(p):,}  elektro",
              [(e['where'], e['a'], e['main'], e['cable'], e['plug']) for e in electrical(p)])
    for r in mwh_table():
        print(f"  {r['mwh']} MWh {r['set']:<5} TČ {r['hp']:,.0f} (nájem {r['hp_rent']:,.0f}) | " +
              " | ".join(f"{t} {r[t]:,.0f}" for t in ALT))
    print("break-even el. vs nafta/LTO/plyn:", [round(breakeven_el(1, a)) for a in ("diesel", "lto", "gas")])
    for p in PRODUCTS:
        print(p, " | ".join(f"{t} {m}m: {payback(p, m, t)['pb']:.1f}r" for t in ("market", "disc") for m in (3, 6, 9)))
    print("hluk Lw", UNIT_LW, "M50 @10 m", round(noise(2, 10), 1), "odstup pro 40 dB:", round(dist_for(2, 40), 1),
          "M100:", round(dist_for(4, 40), 1))
