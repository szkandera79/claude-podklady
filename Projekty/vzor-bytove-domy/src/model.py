#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelové scénáře vzorové nabídky — propočet ekonomiky pro 4 velikosti domu.

Čísla z výstupu jsou ručně přepsaná do nabidka.html (sekce 5 a shrnutí).
Po změně předpokladů spustit a tabulky v nabídce srovnat:
    python3 vzor-bytove-domy/src/model.py
"""
import math

UNIT_KW = 25            # REO X50: využitelný výkon při −15 °C a výstupu 50 °C
BIV_LIMIT = 10          # deficit do 10 kW kryje elektrická bivalence, nad ním další jednotka
HOURS = 2000            # plné hodiny vytápění (BD Jandova: 58,3 MWh / 30 kW ≈ 1 950 h)
TUV_RATIO = 0.7         # potřeba tepla na TUV vůči vytápění (typický BD; Jandova měla 1,1)
PRICE_GJ = 1209          # cena tepla z CZT v Ostravě, Kč/GJ bez DPH (ERÚ 2026: 1 354 s DPH; potvrzeno vyúčtováním BD Jandova)
SCOP_UT, SCOP_TUV = 3.0, 2.7
EL = 3500               # Kč/MWh
BIV_SHARE = 0.03        # podíl roční potřeby dokrytý patronami, je-li deficit
# cena kotelny dle počtu jednotek (1 a 2 = nabídka BD Jandova, každá 3. a další jednotka +390 000 Kč)
PRICE = {1: 1_350_000, 2: 1_600_000, 3: 1_990_000, 4: 2_380_000}
SERVICE = {1: 15_000, 2: 25_000, 3: 35_000, 4: 45_000}


def units(loss):
    n = max(1, math.ceil(loss / UNIT_KW))
    if n > 1 and loss - (n - 1) * UNIT_KW <= BIV_LIMIT:
        n -= 1
    return n


def scenario(loss, n=None):
    n = n or units(loss)
    ut = loss * HOURS / 1000
    tuv = ut * TUV_RATIO
    q = ut + tuv
    cost_now = q * 3.6 * PRICE_GJ
    el = ut / SCOP_UT + tuv / SCOP_TUV
    biv = BIV_SHARE if n * UNIT_KW < loss else 0
    el += biv * q * (1 - 1 / SCOP_UT)        # dokrytá část jde přes patronu (COP 1)
    run = el * EL + SERVICE[n]
    save = cost_now - run
    return dict(loss=loss, n=n, kw=n * UNIT_KW, ut=ut, tuv=tuv, q=q, gj=q * 3.6,
                now=cost_now, el=el * EL, run=run, save=save,
                price=PRICE[n], pb=PRICE[n] / save, pct=save / cost_now,
                gjprice=run / (q * 3.6))


if __name__ == "__main__":
    print("dimenzování:", {l: units(l) for l in (25, 30, 35, 36, 50, 60, 61, 75, 85, 86, 100)})
    for loss in (30, 55, 75, 95):
        s = scenario(loss)
        print(f"{loss:>3} kW  {s['n']}× ({s['kw']} kW)  Q={s['q']:.1f} MWh ({s['gj']:.0f} GJ)  "
              f"dnes={s['now']:,.0f}  el={s['el']:,.0f}  provoz={s['run']:,.0f}  "
              f"úspora={s['save']:,.0f} ({s['pct']:.0%})  cena={s['price']:,}  "
              f"návr.={s['pb']:.1f} r  {s['gjprice']:.0f} Kč/GJ")
