#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BD Jandova 7 — propočet nabídky s jednotkami RHX30 Pro (rev. 1, 11/2026).

Čísla z výstupu jsou ručně přepsaná do nabidka.html, podklady-predseda.html a podklady-schuze.html.
    python3 bd-jandova/rhx30/src/model.py
"""

# ---- vstupy od klienta (vyúčtování Veolia, upřesněno 21. 9. 2026)
UT_MWH, TUV_MWH = 58.3, 64.2          # 210 GJ + 231 GJ
GJ = 441
PRICE_GJ = 1354 / 1.12                # Kč/GJ bez DPH (1 354 s DPH, 12 %) = 1 208,9
BYTY = 17
LOSS = 30                             # kW při −15 °C (odhad ze spotřeby)

# ---- zdroj
UNIT_KW_W55 = 19.0                    # RHX30 Pro, výkonová mapa výrobce A−15/W55
N_BASE, N_EXTRA = 2, 1                # 2 jednotky pokryjí ztrátu, 3. = rezerva / záloha
SCOP_UT, SCOP_TUV = 3.4, 2.7          # konzervativně (SCOP_CZ W55 3,51; TUV dle COP 3,05)
EL = 3500                             # Kč/MWh bez DPH
SERVICE = 35_000                      # Kč/rok, 3 jednotky (vzor RHX30)

# ---- ceny (bez DPH) — stejný obchodní model jako nabídka s X50
INNER = 740_000                       # vnitřní část kotelny (1 600 000 − 2 × 430 000)
UNIT = 350_000                        # RHX30 Pro, jednotky 1 a 2 (uživatel 2. 11. 2026)
EXTRA = 210_000                       # 3. (záložní) jednotka (uživatel 2. 11. 2026) = sleva 40 %
SPL_330 = {60: 8_400, 120: 6_800}     # splátka za jednotku 330 tis./měs, servis v ceně (vzor RHX30)
SPL = {m: round(v * UNIT / 330_000, -2) for m, v in SPL_330.items()}        # poměrem ceny
SPL_X = {m: round(v * EXTRA / 330_000, -2) for m, v in SPL_330.items()}
LOAN_RATE, LOAN_Y = 0.055, 10         # orientační úvěr SVJ na vnitřní část

FV_PER_UNIT_KWP = 5.0                 # 1 string 10 × ~500 Wp na jednotku (výrobce 21. 10.: RHX 1 × 10 ks)
FV_YIELD = 950                        # kWh/kWp/rok, Ostrava
FV_USE = (0.55, 0.70)                 # využitelný podíl (jen když běží kompresor; TUV celoročně)
FV_COST_PER_UNIT = 55_000             # panely + konstrukce + DC rozvod + montáž — ODHAD


def annuity(p, r, y):
    i = r / 12
    return p * i / (1 - (1 + i) ** (-y * 12))


def r(x, k=100):
    return round(x / k) * k


now = GJ * PRICE_GJ
extra = EXTRA
price = INNER + N_BASE * UNIT + extra
el_mwh = UT_MWH / SCOP_UT + TUV_MWH / SCOP_TUV
el = el_mwh * EL
run = el + SERVICE
save = now - run
print(f"Veolia dnes: {now:,.0f} Kč/rok ({now/BYTY:,.0f}/byt, {now/12:,.0f}/měs)")
print(f"Výkon: {N_BASE}× {UNIT_KW_W55} = {N_BASE*UNIT_KW_W55:.0f} kW vs ztráta {LOSS} kW; "
      f"s rezervou {(N_BASE+N_EXTRA)*UNIT_KW_W55:.0f} kW; 1 jednotka v poruše → {N_BASE*UNIT_KW_W55:.0f} kW")
print(f"Cena: {INNER:,} + {N_BASE}×{UNIT:,} + {extra:,.0f} = {price:,.0f} Kč ({price/BYTY:,.0f}/byt)")
print(f"Elektřina {el_mwh:.1f} MWh = {el:,.0f}; servis {SERVICE:,}; provoz {run:,.0f} ({run/BYTY:,.0f}/byt) "
      f"→ {run/GJ:.0f} Kč/GJ; úspora {save:,.0f} ({save/now:.0%}); návratnost {price/save:.1f} r; "
      f"15 let {(save*15-price)/1e6:.1f} mil. čistého")
el2 = el_mwh * 5250 + SERVICE
print(f"El. +50 %: úspora {now-el2:,.0f}, návratnost {price/(now-el2):.1f} r")

for m, s in SPL.items():
    mon = s * N_BASE + SPL_X[m] * N_EXTRA
    yr = mon * 12 + el
    print(f"Pronájem {m} m: {s:,.0f}+{s:,.0f}+{SPL_X[m]:,.0f} → splátka {mon:,.0f}/měs; ročně vč. el. {yr:,.0f}; úspora {now-yr:,.0f} "
          f"({(now-yr)/BYTY/12:,.0f}/byt/měs); vstup {INNER:,} → návratnost vstupu {INNER/(now-yr):.1f} r")
    ln = annuity(INNER, LOAN_RATE, LOAN_Y)
    yr2 = yr + ln * 12
    print(f"   + úvěr na vnitřek {ln:,.0f}/měs → bez vlastních peněz ročně {yr2:,.0f}; "
          f"proti Veolii {now-yr2:,.0f} ({(now-yr2)/BYTY/12:,.0f}/byt/měs)")

full = annuity(price, LOAN_RATE, LOAN_Y)
print(f"Celé úvěrem SVJ {LOAN_RATE:.1%}/{LOAN_Y} let: {full:,.0f}/měs; ročně + provoz {full*12+run:,.0f}; "
      f"proti Veolii {now-full*12-run:,.0f}")

for n in (1, 3):
    kwp = n * FV_PER_UNIT_KWP
    prod = kwp * FV_YIELD / 1000
    lo, hi = prod * FV_USE[0] * EL, prod * FV_USE[1] * EL
    c = n * FV_COST_PER_UNIT
    print(f"FV {n} string(y) {kwp:.0f} kWp: výroba {prod:.1f} MWh, úspora {lo:,.0f}–{hi:,.0f}/rok, "
          f"cena ~{c:,} → návratnost {c/hi:.1f}–{c/lo:.1f} r")
