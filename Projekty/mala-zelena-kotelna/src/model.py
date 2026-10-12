#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Malá zelená kotelna — 2 × RH060 v kaskádě: krytí tepelné ztráty a modelová ekonomika.

Výkonová data RH060-PW22 (MAX) z ~/Claude/REO/R290-datove-listy/src/data.js
(= „REO datové listy/RH060 technický list SVT.pdf"). Čísla jsou ručně přepsaná
do nabidka.html — po změně předpokladů spustit a srovnat:
    python3 mala-zelena-kotelna/src/model.py
"""
AMB = [-25, -20, -15, -12, -10, -7, -5, 0, 2, 5, 7, 10, 12, 15, 21]
CAP = {35: [8.2, 10.3, 12.3, 13.6, 14.5, 15.8, 16.7, 18.9, 19.6, 21.0, 22.0, 22.8, 23.1, 23.5, 24.2],
       45: [8.0, 10.0, 11.8, 13.1, 14.0, 15.3, 16.1, 18.3, 18.9, 20.3, 21.2, 22.0, 22.3, 22.7, 23.3],
       55: [7.6, 9.5, 11.4, 12.6, 13.4, 14.6, 15.5, 17.5, 18.1, 19.5, 20.4, 21.1, 21.4, 21.8, 22.4]}
COP = {35: [1.69, 2.09, 2.44, 2.67, 2.83, 3.07, 3.23, 3.62, 3.74, 4.00, 4.16, 4.29, 4.42, 4.63, 5.02],
       45: [1.45, 1.78, 2.08, 2.28, 2.41, 2.62, 2.75, 3.09, 3.19, 3.41, 3.55, 3.66, 3.77, 3.95, 4.29],
       55: [1.23, 1.52, 1.78, 1.94, 2.06, 2.23, 2.35, 2.63, 2.72, 2.91, 3.03, 3.12, 3.22, 3.37, 3.66]}
INP = {45: [5.50, 5.59, 5.69, 5.76, 5.80, 5.83, 5.86, 5.92, 5.93, 5.95, 5.98, 6.01, 5.91, 5.75, 5.44]}

LOSS = 18.0             # tepelná ztráta domu při −15 °C, kW
N = 2                   # počet jednotek
HOURS = 2000            # plné hodiny vytápění (jako vzor-bytove-domy)
TUV_RATIO = 0.7
SCOP_UT, SCOP_TUV = 3.5, 2.8   # RH060: SCOP CZ klima W45 4,01 / W55 3,63 → konzervativně
EL = 3500               # Kč/MWh
SERVICE = 15_000        # Kč/rok za 2 menší jednotky
PRICE_IN = 300_000      # vnitřní část kotelny bez DPH (uživatel 12. 10. 2026)
PRICE_TC = 320_000      # 2 × RH060 à 160 000 Kč bez DPH (uživatel 12. 10. 2026)
GJ = (1209, 967)        # CZT Ostrava / průměr ČR, Kč/GJ bez DPH


def interp(tab, t):
    for i in range(len(AMB) - 1):
        a, b = AMB[i], AMB[i + 1]
        if a <= t <= b:
            return tab[i] + (tab[i + 1] - tab[i]) * (t - a) / (b - a)
    raise ValueError(t)


def loss_at(t, loss=LOSS):
    return loss * (20 - t) / 35


def bivalent(n, w, loss=LOSS):
    t = 20.0
    while t > -25 and n * interp(CAP[w], t) >= loss_at(t, loss):
        t -= 0.1
    return t


if __name__ == "__main__":
    i7, i15 = AMB.index(7), AMB.index(-15)
    print(f"RH060 A7/W55: {CAP[55][i7]} kW, COP {COP[55][i7]}  |  A7/W35: {CAP[35][i7]} kW")
    for w in (35, 45, 55):
        c = CAP[w][i15]
        print(f"A−15/W{w}: 1× {c} kW (COP {COP[w][i15]}) → 2× {2*c:.1f} kW = "
              f"{2*c/LOSS:.0%} ztráty; 1 jednotka sama do {bivalent(1, w):.1f} °C; "
              f"max. ztráta pro 2× bez patron {2*c:.1f} kW")
    print(f"příkon 2× při A−15/W45: {2*INP[45][i15]:.1f} kW")
    ut = LOSS * HOURS / 1000
    tuv = ut * TUV_RATIO
    q = ut + tuv
    el = (ut / SCOP_UT + tuv / SCOP_TUV) * EL
    run = el + SERVICE
    print(f"ÚT {ut:.1f} MWh, TUV {tuv:.1f} MWh, celkem {q:.1f} MWh = {q*3.6:.0f} GJ")
    print(f"elektřina {el:,.0f} Kč, servis {SERVICE:,}, provoz {run:,.0f} Kč = {run/(q*3.6):.0f} Kč/GJ")
    for p in GJ:
        now = q * 3.6 * p
        save = now - run
        pb = f", návratnost {(PRICE_IN + PRICE_TC)/save:.1f} r" if PRICE_IN and PRICE_TC else ""
        print(f"CZT {p} Kč/GJ: dnes {now:,.0f}, úspora {save:,.0f} ({save/now:.0%}){pb}")
