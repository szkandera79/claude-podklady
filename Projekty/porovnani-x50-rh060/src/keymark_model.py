#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Srovnání RH X50 / RHX30 Pro / RHX20 Pro / RH060 na JEDNOTNÉM základě — certifikované body KEYMARK.

Všechny čtyři jednotky certifikovala stejná zkušebna stejnou metodou (EN 14825, certifikace 14. 8. 2026):
COP při Tj = TOL(−10), −7, +2, +7, +12 °C při stejné relativní zátěži (průměrné klima, W35 a W55 s ekvitermou).
Z nich:
  * SCOP pro české klima (výpočtová −15 °C) — COP interpolovaný v Tj, pod −10 °C extrapolace poměrem
    COP(−15)/COP(−10) z výkonových map (X50, RH060; pro X30/X20 průměr obou),
  * výkon při −15 °C: X50 a RH060 z výkonových map, X30/X20 = deklarovaný výkon KEYMARK při −10 °C/W55 ×
    poměr výkonu −15/−10 z map (průměr X50 a RH060),
  * ekonomika bytových domů 25–150 kW při stejné zátěži (ÚT + TUV).
Spouštět z kořene repa:  python3 porovnani-x50-rh060/src/keymark_model.py   → results2.json
"""
import json, math
from pathlib import Path

HERE = Path(__file__).parent
FX = {"EUR": 24.380, "USD": 21.369}          # ČNB 23. 9. 2026
TJ = [-10, -7, 2, 7, 12]                     # TOL = −10 °C u všech čtyř

U = {
    "X50": dict(name="RH X50", price=round(4_800 * FX["USD"]), inst=60_000, service=6_000,
                scop={35: 4.57, 55: 3.21},
                cop={35: [2.73, 3.28, 4.62, 5.63, 7.44], 55: [1.98, 2.28, 3.19, 4.10, 6.02]},
                pdh={35: [25.81, 25.15, 15.73, 9.38, 11.49], 55: [28.52, 24.08, 14.18, 9.48, 11.23]},
                rated={35: (49.41, 3.86), 55: (46.10, 2.62)},
                cap15={35: 30.9, 45: 27.3, 55: 24.8}, cap15_src="výkonová mapa",
                minA7=18.4, maxA7=49.3, lw=65, kg=370, amp=40, r290=4.0),
    "X30": dict(name="RHX30 Pro", price=round(3_680 * FX["EUR"]), inst=50_000, service=5_000,
                scop={35: 5.25, 55: 3.90},
                cop={35: [2.31, 2.81, 5.18, 7.54, 9.87], 55: [1.70, 1.99, 3.88, 5.64, 7.81]},
                pdh={35: [28.82, 27.05, 16.57, 10.69, 10.05], 55: [26.84, 27.11, 16.61, 10.63, 9.72]},
                rated={35: (29.99, 4.64), 55: (29.97, 2.83)},
                cap15=None, cap15_src="odvozeno z KEYMARK −10 °C",
                minA7=12.7, maxA7=40.0, lw=59, kg=328, amp=40, r290=3.4),
    "X20": dict(name="RHX20 Pro", price=round(2_940 * FX["EUR"]), inst=45_000, service=4_500,
                scop={35: 5.23, 55: 3.97},
                cop={35: [2.26, 2.59, 5.31, 7.61, 9.85], 55: [1.70, 2.06, 3.99, 5.62, 7.42]},
                pdh={35: [17.61, 17.75, 10.97, 7.18, 6.32], 55: [18.44, 17.63, 10.80, 7.16, 6.02]},
                rated={35: (19.91, 4.85), 55: (19.92, 2.92)},
                cap15=None, cap15_src="odvozeno z KEYMARK −10 °C",
                minA7=10.2, maxA7=28.0, lw=56, kg=265, amp=32, r290=2.2),
    "RH060": dict(name="RH060", price=round(2_398 * FX["USD"]), inst=35_000, service=3_500,
                  scop={35: 4.80, 55: 3.89},
                  cop={35: [2.74, 2.97, 4.76, 6.10, 7.86], 55: [2.22, 2.51, 3.72, 5.12, 6.80]},
                  pdh={35: [14.18, 12.63, 7.73, 5.42, 3.76], 55: [12.69, 11.44, 7.39, 4.62, 3.61]},
                  rated={35: (14.10, 4.67), 55: (13.19, 3.17)},
                  cap15={35: 12.3, 45: 11.8, 55: 11.4}, cap15_src="výkonová mapa",
                  minA7=8.8, maxA7=22.0, lw=54, kg=165, amp=25, r290=1.45),
}
# TUV 15→55 °C při max. výkonu (ceníky / protokol): COP při A7 a A20
DHW = {"X50": {"A7": 3.43, "A20": 4.46, "src": "protokol RH X50"},
       "X30": {"A7": 3.08, "A20": 4.10, "src": "výkonová mapa RHX30 Pro (DHW MAX)"},
       "X20": {"A7": 4.34 * 3.08 / 4.10, "A20": 4.34, "src": "ceník 2026 (A20), A7 poměrem z mapy RHX30 Pro"},
       "RH060": {"A7": 3.51, "A20": None, "src": "ceník 10/2024 (A7)"}}
_R20 = 4.46 / 3.43                                        # poměr A20/A7 z protokolu RH X50
for k, v in DHW.items():
    v["A7"] = v["A7"] or v["A20"] / _R20
    v["A20"] = v["A20"] or v["A7"] * _R20
CIRC = 0.5          # podíl energie TUV na cirkulaci a udržování 55 °C (≈ provoz W55, jmenovitý bod A7/W55)
W65_COP = 0.85      # COP(W65)/COP(W55) z mapy RH X50 (−12…+12 °C: 0,79–0,88)
W65_CAP = 23.4 / 27.2   # výkon W65/W55 při −12 °C z mapy RH X50

# extrapolace −10 → −15 °C z výkonových map (MAX)
COP_R = {"X50": {35: 2.10 / 2.30, 55: 1.50 / 2.00}, "RH060": {35: 2.44 / 2.83, 55: 1.78 / 2.06}}
CAP_R = {55: (24.8 / 31.05 + 11.4 / 13.4) / 2}          # výkon −15/−10 při W55
W_R = (30.9 / 24.8 + 12.3 / 11.4) / 2                    # výkon W35/W55 při −15
# RHX30 Pro: výkonová mapa výrobce (~/Claude/REO/PW Helios/…Performance curve.xls, 27. 9. 2026), MAX při −15 °C
X30_MAP = {"cap15": {35: 22.4, 45: 20.8, 55: 19.0, 65: 16.1},
           "cop15": {35: 2.13, 45: 1.75, 55: 1.50, 65: 1.23}, "cop10": {35: 2.39, 55: 1.68},
           "w65_cop": 1.374 / 1.676}                      # COP W65/W55 při −10 °C (při +7 °C 0,86)
U["X30"]["cap15"] = dict(X30_MAP["cap15"])
U["X30"]["cap15_src"] = "výkonová mapa"
COP_R["X30"] = {w: X30_MAP["cop15"][w] / X30_MAP["cop10"][w] for w in (35, 55)}
# RHX20 Pro: stejná řada — mapa RHX30 Pro × poměr deklarovaných výkonů KEYMARK při −10 °C/W55 (18,44 / 26,84)
K20 = 18.44 / 26.84
U["X20"]["cap15"] = {w: round(c * K20, 1) for w, c in X30_MAP["cap15"].items()}
U["X20"]["cap15_src"] = "odvozeno z mapy RHX30 Pro"
COP_R["X20"] = dict(COP_R["X30"])
W65 = {"X50": W65_COP, "RH060": W65_COP, "X30": X30_MAP["w65_cop"], "X20": X30_MAP["w65_cop"]}
for k in ("X50", "RH060"):
    U[k]["cap15"][65] = round(U[k]["cap15"][55] * W65_CAP, 1)

# české klima (výpočtová −15 °C): hodiny po 1 K v topné sezóně (průměr EN 14825 rozšířený o chladnější konec)
BINS = {-15: 4, -14: 6, -13: 9, -12: 14, -11: 20, -10: 26, -9: 34, -8: 42, -7: 60, -6: 80, -5: 105,
        -4: 130, -3: 150, -2: 200, -1: 230, 0: 300, 1: 320, 2: 330, 3: 350, 4: 350, 5: 320, 6: 320,
        7: 310, 8: 300, 9: 290, 10: 270, 11: 220, 12: 180, 13: 150, 14: 110, 15: 74}
T_DES, T_OFF = -15, 16
TARIFF, FLH, TUV_RATIO = 4.0, 2000, 0.7


def cop_at(u, w, t):
    """COP jednotky při venkovní t pro křivku W35/W55 (lineárně mezi body KEYMARK, pod −10 extrapolace)."""
    c = U[u]["cop"][w]
    if t <= -10:
        r = COP_R[u][w]
        return c[0] * (1 - (1 - r) * (-10 - t) / 5)
    if t >= 12:
        return c[-1]
    for i in range(len(TJ) - 1):
        if TJ[i] <= t <= TJ[i + 1]:
            return c[i] + (c[i + 1] - c[i]) * (t - TJ[i]) / (TJ[i + 1] - TJ[i])


def cop_w(u, w, t):
    if w in (35, 55):
        return cop_at(u, w, t)
    if w == 65:
        return cop_at(u, 55, t) * W65[u]
    a, b = cop_at(u, 35, t), cop_at(u, 55, t)          # W45 = harmonický průměr (příkon je aditivní)
    return 2 / (1 / a + 1 / b)


def scop_cz(u, w):
    """Sezónní COP ÚT pro české klima při jednotné relativní zátěži (lineární zátěž 100 % při −15 °C)."""
    q = e = 0.0
    for t, h in BINS.items():
        load = (T_OFF - t) / (T_OFF - T_DES)
        q += load * h
        e += load * h / cop_w(u, w, t)
    return q / e


def scop_en(u, w):
    """Kontrola: SCOP v průměrném klimatu z bodů (má sedět na KEYMARK ± pár %)."""
    bins = {-10: 1, -9: 25, -8: 23, -7: 24, -6: 27, -5: 68, -4: 91, -3: 89, -2: 165, -1: 173, 0: 240,
            1: 280, 2: 320, 3: 357, 4: 356, 5: 303, 6: 330, 7: 326, 8: 348, 9: 335, 10: 315, 11: 215,
            12: 169, 13: 151, 14: 105, 15: 74}
    q = e = 0.0
    for t, h in bins.items():
        load = (T_OFF - t) / 26
        q += load * h
        e += load * h / cop_at(u, w, t)
    return q / e


def cop_dhw(u):
    """Roční COP ohřevu TUV na 55 °C: (1−CIRC) ohřev studené vody 15→55 (60 % v topné sezóně při ≈ A3,
    40 % v létě při A20) + CIRC cirkulace/udržování při W55 (jmenovitý bod EN 14511 A7/W55)."""
    d = DHW[u]
    heat_up = 0.6 * d["A7"] * 0.9 + 0.4 * d["A20"]
    return 1 / ((1 - CIRC) / heat_up + CIRC / U[u]["rated"][55][1])


def n_units(u, loss, w):
    return max(1, math.ceil(loss * 0.95 / U[u]["cap15"][w] - 1e-9))


def capex(u, n):
    return n * (U[u]["price"] + U[u]["inst"]) + (0 if n == 1 else 25_000 + 8_000 * n)


def building(u, loss, w):
    n = n_units(u, loss, w)
    ut = loss * FLH / 1000
    tuv = ut * TUV_RATIO
    el = ut / scop_cz(u, w) + tuv / cop_dhw(u)
    opex = el * TARIFF * 1000 + n * U[u]["service"]
    return dict(unit=u, loss=loss, tw=w, n=n, over=n > 8, capex=capex(u, n), spf=round((ut + tuv) / el, 2),
                el=round(el, 1), opex=round(opex), tco15=round(capex(u, n) + 15 * opex),
                n1=round(100 * (n - 1) * U[u]["cap15"][w] / loss))


def main():
    out = {"units": {}, "scen": [], "sens": {}}
    for u, d in U.items():
        kc15 = d["price"] / d["cap15"][55]
        out["units"][u] = dict(name=d["name"], price=d["price"], cap15=d["cap15"], cap15_src=d["cap15_src"],
                               kc_kw15=round(kc15), kc_kw7=round(d["price"] / d["maxA7"]),
                               scop=d["scop"], scop_en_check={w: round(scop_en(u, w), 2) for w in (35, 55)},
                               scop_cz={w: round(scop_cz(u, w), 2) for w in (35, 45, 55, 65)},
                               cop15={w: round(cop_at(u, w, -15), 2) for w in (35, 55)},
                               cop_dhw=round(cop_dhw(u), 2), minA7=d["minA7"], maxA7=d["maxA7"])
        print(f"{u:6} cena {d['price']:>7,} Kč  −15/W55 {d['cap15'][55]:>5} kW  {kc15:>6,.0f} Kč/kW  "
              f"SCOP_EN kontrola {out['units'][u]['scop_en_check']} vs {d['scop']}  SCOP_CZ {out['units'][u]['scop_cz']}"
              f"  COP−15 {out['units'][u]['cop15']}")
    for loss in (25, 50, 75, 100, 150):
        for w in (35, 45, 55, 65):
            for u in U:
                out["scen"].append(building(u, loss, w))
    for u in U:
        print(u, "TUV COP", round(cop_dhw(u), 2), "cap15", U[u]["cap15"])
    print(f"\n{'kW':>4}{'W':>4} {'jedn':6}{'n':>3}{'CAPEX':>10}{'SPF':>6}{'MWh':>7}{'OPEX':>9}{'TCO15':>11}{'N-1':>5}")
    for r in out["scen"]:
        print(f"{r['loss']:>4}{r['tw']:>4} {r['unit']:6}{r['n']:>3}{r['capex']:>10,}{r['spf']:>6}{r['el']:>7}"
              f"{r['opex']:>9,}{r['tco15']:>11,}{r['n1']:>5}{' !8' if r['over'] else ''}")
    global TARIFF
    keep = TARIFF
    out["sens"]["tariff"] = []
    for tar in (3.0, 4.0, 5.0, 6.0):
        TARIFF = tar
        out["sens"]["tariff"].append({"tariff": tar, **{u: building(u, 50, 55)["tco15"] for u in U}})
    TARIFF = keep
    print("\ntarif (50 kW, W55):", out["sens"]["tariff"])
    (HERE / "results2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
