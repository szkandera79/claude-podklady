#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Návrh kaskády TČ pro bytový dům: RH X50 / RHX30 Pro (i smíšené) a pro srovnání RH060.

Vstup: tepelná ztráta domu (kW, pro spotřebu energie) a potřebný výkon při A−15/W55 (kW, pro dimenzování).
Výstup: varianty seřazené podle výhodnosti — nákup, prodej, marže, náklady zákazníka za 15 let, SPF, záloha.

Použití (z kořene repa):
    python3 porovnani-x50-rh060/src/navrh_kaskady.py --ztrata 60 --vykon 70
    python3 porovnani-x50-rh060/src/navrh_kaskady.py --ztrata 60 --vykon 70 --spad 45 --tuv 0.9 --tarif 4.5
Účinnosti a výkony: keymark_model.py (certifikace KEYMARK + výkonové mapy výrobce).
"""
import argparse, itertools, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import keymark_model as km

# Ceny za kus bez DPH — nákup (vstup uživatele 27. 9. 2026) a prodej (ceník)
PRICE = {
    "X50":   {"nakup": 110_000, "prodej": 430_000},
    "X30":   {"nakup": 100_000, "prodej": 330_000},
    "RH060": {"nakup": 55_000,  "prodej": 150_000},   # faktura US$ 2 398 + ≈7 % doprava a clo (jako u X50)
}
CAP55 = {u: km.U[u]["cap15"][55] for u in PRICE}      # výkon A−15/W55 z výkonových map: 24,8 / 19,0 / 11,4 kW
LW = {"X50": 65, "X30": 59, "RH060": 54}               # akustický výkon dB(A) při 55 °C
AREA = {"X50": 1.195 * 0.98, "X30": 1.55 * 0.63, "RH060": 1.08 * 0.48}   # půdorys m²
KG = {"X50": 370, "X30": 328, "RH060": 170}
NAME = {"X50": "RH X50", "X30": "RHX30 Pro", "RH060": "RH060"}
MAX_N = 8


def variants(need, tol=0.02):
    """Nejmenší kaskády, které pokryjí potřebný výkon (odebráním kteréhokoli kusu by už nestačily).
    tol = povolený deficit dokrytý patronou (výchozí 2 % potřeby)."""
    need = need * (1 - tol)
    out = []
    for a, b in itertools.product(range(MAX_N + 1), repeat=2):
        if 0 < a + b <= MAX_N:
            cap = a * CAP55["X50"] + b * CAP55["X30"]
            if cap >= need and all(cap - CAP55[u] < need for u, k in (("X50", a), ("X30", b)) if k):
                out.append({"X50": a, "X30": b})
    n = math.ceil(need / CAP55["RH060"] - 1e-9)
    out.append({"RH060": n})
    return out


def evaluate(mix, loss, need, spad, tuv_ratio, tarif, flh):
    units = [(u, k) for u, k in mix.items() if k]
    n = sum(k for _, k in units)
    cap = sum(k * CAP55[u] for u, k in units)
    ut = loss * flh / 1000
    tuv = ut * tuv_ratio
    el = sum(k * CAP55[u] / cap * (ut / km.scop_cz(u, spad) + tuv / km.cop_dhw(u)) for u, k in units)
    nakup = sum(k * PRICE[u]["nakup"] for u, k in units)
    prodej = sum(k * PRICE[u]["prodej"] for u, k in units)
    montaz = sum(k * km.U[u]["inst"] for u, k in units) + (0 if n == 1 else 25_000 + 8_000 * n)
    servis = sum(k * km.U[u]["service"] for u, k in units)
    opex = el * tarif * 1000 + servis
    biggest = max(CAP55[u] for u, _ in units)
    return dict(
        mix=mix, n=n, cap=cap, smisena=len(units) > 1, nad8=n > MAX_N,
        nakup=nakup, prodej=prodej, marze=prodej - nakup, spf=(ut + tuv) / el, el=el, opex=opex,
        zakaznik15=prodej + montaz + 15 * opex,
        n1=100 * (cap - biggest) / need,
        hluk=10 * math.log10(sum(k * 10 ** (LW[u] / 10) for u, k in units)),
        plocha=sum(k * AREA[u] for u, k in units), kg=sum(k * KG[u] for u, k in units))


def label(mix):
    return " + ".join(f"{k}× {NAME[u]}" for u, k in mix.items() if k)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ztrata", type=float, required=True, help="tepelná ztráta domu, kW")
    ap.add_argument("--vykon", type=float, required=True, help="potřebný výkon kaskády při A−15/W55, kW")
    ap.add_argument("--spad", type=int, default=55, choices=(35, 45, 55, 65), help="návrhová teplota vody (SCOP)")
    ap.add_argument("--tuv", type=float, default=0.7, help="TUV jako podíl roční potřeby ÚT (výchozí 0,7)")
    ap.add_argument("--tarif", type=float, default=4.0, help="cena elektřiny Kč/kWh bez DPH")
    ap.add_argument("--tol", type=float, default=0.02, help="povolený deficit při −15 °C dokrytý patronou (podíl)")
    ap.add_argument("--flh", type=float, default=2000, help="hodiny plného výkonu ÚT")
    a = ap.parse_args()

    res = [evaluate(m, a.ztrata, a.vykon, a.spad, a.tuv, a.tarif, a.flh) for m in variants(a.vykon, a.tol)]
    ok = [r for r in res if not r["nad8"]]
    best_c = min(r["zakaznik15"] for r in ok)
    # Doporučení: nejvyšší marže mezi variantami do +3 % od nejlevnější pro zákazníka a se zálohou ≥ 50 %
    pool = [r for r in ok if r["zakaznik15"] <= best_c * 1.03 and r["n1"] >= 50] or \
           [r for r in ok if r["zakaznik15"] <= best_c * 1.03]
    rec = max(pool, key=lambda r: r["marze"])

    fmt = lambda v: f"{v:,.0f}".replace(",", " ")
    print(f"\nDům: ztráta {a.ztrata:g} kW, potřeba {a.vykon:g} kW při A−15/W55, spád {a.spad}, TUV {a.tuv:g}× ÚT, "
          f"elektřina {a.tarif:g} Kč/kWh\n")
    hdr = f"{'Kaskáda':28}{'kW':>6}{'Nákup':>10}{'Prodej':>11}{'Marže':>11}{'SPF':>6}{'Zák. 15 let':>13}{'vs. min':>8}{'Záloha':>8}{'dB':>5}{'m²':>5}{'kg':>6}"
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(res, key=lambda r: r["zakaznik15"]):
        tag = []
        if r is rec: tag.append("◀ DOPORUČENO")
        if r["smisena"]: tag.append("smíšená: nadřazená regulace")
        if r["nad8"]: tag.append("NAD 8 KS")
        if r["cap"] < a.vykon: tag.append(f"patrona {a.vykon - r['cap']:.1f} kW")
        d = 100 * (r["zakaznik15"] / best_c - 1)
        print(f"{label(r['mix']):28}{r['cap']:6.1f}{fmt(r['nakup']):>10}{fmt(r['prodej']):>11}{fmt(r['marze']):>11}"
              f"{r['spf']:6.2f}{fmt(r['zakaznik15']):>13}{('+%.1f %%' % d) if d > 0.05 else 'min':>8}"
              f"{r['n1']:7.0f}%{r['hluk']:5.0f}{r['plocha']:5.1f}{fmt(r['kg']):>6}  {' · '.join(tag)}")
    print(f"\nDoporučení: {label(rec['mix'])} — marže {fmt(rec['marze'])} Kč, zákazník za 15 let {fmt(rec['zakaznik15'])} Kč, "
          f"záloha po výpadku největšího kusu {rec['n1']:.0f} % potřeby.")
    xx = [r for r in ok if "RH060" not in r["mix"]]
    if xx and "RH060" in rec["mix"]:
        bx = min(xx, key=lambda r: r["zakaznik15"])
        print(f"Nejlepší jen z RH X50/RHX30 Pro: {label(bx['mix'])} — marže {fmt(bx['marze'])} Kč, "
              f"zákazník za 15 let {fmt(bx['zakaznik15'])} Kč (+{100*(bx['zakaznik15']/best_c-1):.1f} %).")
    print("Pravidlo: nejvyšší marže mezi variantami do +3 % od nejlevnější pro zákazníka, se zálohou ≥ 50 %.")


if __name__ == "__main__":
    main()
