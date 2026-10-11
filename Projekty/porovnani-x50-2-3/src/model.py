#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Porovnání variant A (2× RH X50) a B (3× RH X50) — propočet pro nabidka.html.

Výkon a COP se berou z výkonového protokolu výrobce (src/rh-x50-data.json = kopie
~/Claude/REO/RH X50 komerční/DATA.json, protokol výkonových charakteristik RH X50).
Čísla jsou do nabídky přepsaná ručně (sekce 2–5). Po změně předpokladů spustit a srovnat:
    python3 porovnani-x50-2-3/src/model.py
"""
import json
from pathlib import Path

D = json.loads((Path(__file__).parent / "rh-x50-data.json").read_text())
AMB = D["amb_heat"]
W55 = D["heat"]["55"]["MAX"]

PRICE = {"A": 1_600_000, "B": 1_990_000}
UNITS = {"A": 2, "B": 3}
SERVICE = {"A": 25_000, "B": 35_000}
HOURS, TUV_RATIO = 2000, 0.7            # předpoklady jako ve vzorové nabídce
SCOP_UT, SCOP_TUV, EL = 3.0, 2.7, 3500  # konzervativně pod třídou A++ (55 °C) ze štítku
CZT = (967, 1325)                       # Kč/GJ bez DPH: průměr ČR ERÚ 2026 / dražší soustavy
T_IN, T_DESIGN = 20, -15


def interp(t, key="cap"):
    xs, ys = AMB, W55[key]
    for i in range(len(xs) - 1):
        if xs[i] <= t <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (t - xs[i]) / (xs[i + 1] - xs[i])
    raise ValueError(t)


def load(loss, t):
    return loss * (T_IN - t) / (T_IN - T_DESIGN)


def bivalence(loss, n):
    """Venkovní teplota, pod kterou kaskáda n jednotek (W55 MAX) nestačí na vytápění."""
    t = T_DESIGN
    if n * interp(t) >= load(loss, t):
        return None
    while n * interp(t) < load(loss, t):
        t += 0.1
    return round(t, 1)


def biv_share(t_biv):
    """Orientační podíl roční potřeby tepla dokrytý patronami (odhad, rozsah)."""
    if t_biv is None or t_biv <= -14.5:
        return (0, 0)
    if t_biv <= -12.5:
        return (0.01, 0.03)
    if t_biv <= -10.5:
        return (0.02, 0.05)
    return (0.03, 0.08)


def peak(loss, v):
    n = UNITS[v]
    cap = n * interp(T_DESIGN)
    hp = min(loss, cap)
    cop = interp(T_DESIGN, "cop")
    return dict(cap=cap, hp=hp, deficit=max(0, loss - cap), el=hp / cop + max(0, loss - cap),
                one_down=(n - 1) * interp(T_DESIGN), t_biv=bivalence(loss, n))


def annual(loss, v):
    ut = loss * HOURS / 1000
    tuv = ut * TUV_RATIO
    q = ut + tuv
    base = ut / SCOP_UT + tuv / SCOP_TUV
    share = biv_share(peak(loss, v)["t_biv"])
    el = [base + s * q * (1 - 1 / SCOP_UT) for s in share]
    run = [e * EL + SERVICE[v] for e in el]
    return dict(q=q, gj=q * 3.6, run=run, share=share, now=[q * 3.6 * p for p in CZT])


if __name__ == "__main__":
    print(f"A-15/W55: {interp(-15):.1f} kW, příkon {interp(-15,'inp'):.2f} kW, COP {interp(-15,'cop'):.2f}")
    for loss in (45, 55, 65, 75):
        print(f"--- ztráta {loss} kW")
        for v in "AB":
            p, a = peak(loss, v), annual(loss, v)
            print(f" {v}: kaskáda {p['cap']:.1f} kW, TČ {p['hp']:.1f}, patrony {p['deficit']:.1f} kW, "
                  f"el. {p['el']:.1f} kW, výpadek 1 j. {p['one_down']:.1f} kW ({p['one_down']/loss:.0%}), "
                  f"bivalence {p['t_biv']} °C, podíl patron {a['share']} | Q {a['q']:.0f} MWh ({a['gj']:.0f} GJ), "
                  f"provoz {a['run'][0]:,.0f}–{a['run'][1]:,.0f}, CZT {a['now'][0]:,.0f}–{a['now'][1]:,.0f}")
        for v in "AB":
            a = annual(loss, v)
            pb = [PRICE[v] / (now - run) for now in a["now"] for run in a["run"]]
            print(f"  návratnost {v}: {min(pb):.1f}–{max(pb):.1f} r")
