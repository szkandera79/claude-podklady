#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BD Michal — propočet variant A (2× RH X50) a B (3× RH X50).

Vstupy: PENB č. 530077.2 (ztráta 53 kW při −15 °C, vytápění 107,45 MWh/rok,
TUV 56,33 MWh/rok) + výkonový protokol RH X50 (rh-x50-data.json).
Model: binová metoda po 1 K, teplotní křivka trvání odvozená z délky otopné sezóny
tak, aby potřeba tepla na vytápění seděla na PENB.

Spuštění:  python3 bd-michal-nabidka/src/model.py
"""
import json, math
from pathlib import Path

D = json.loads((Path(__file__).parent / "rh-x50-data.json").read_text())
AMB = D["amb_heat"]
W35, W55 = D["heat"]["35"]["MAX"], D["heat"]["55"]["MAX"]

LOSS, T_IN, T_DES = 53.0, 20.0, -15.0     # kW, °C, °C  (PENB)
FLATS_PENB, FLATS = 27, 24                # PENB počítá 27 b.j., investor potvrdil 24
Q_UT = 107.45                             # MWh/rok (PENB, dáno obálkou budovy)
Q_TUV = 56.33 * FLATS / FLATS_PENB        # MWh/rok, přepočet PENB na 24 b.j.
T_LIM = 13.0                              # mez vytápění
EL = 3500                                 # Kč/MWh bez DPH
AKU_SHIFT = 15                            # kWh/den, co akumulace 2× 1 000 l reálně přesune
P_UNIT_MAX = 17.0                         # kW el. příkon jednotky (protokol, W55–W65)


def interp(tab, t, key):
    xs, ys = AMB, tab[key]
    t = max(min(t, xs[-1]), xs[0])
    for i in range(len(xs) - 1):
        if xs[i] <= t <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (t - xs[i]) / (xs[i + 1] - xs[i])


cap35 = lambda t: interp(W35, t, "cap")
cop35 = lambda t: interp(W35, t, "cop")
cap55 = lambda t: interp(W55, t, "cap")
cop55 = lambda t: interp(W55, t, "cop")
load = lambda t: max(0.0, LOSS * (T_IN - t) / (T_IN - T_DES))


def bins():
    """Hodiny v roce po 1 K (součet 8 760 h). Tvar rozdělení je kalibrovaný tak, aby
    potřeba tepla na vytápění vyšla na hodnotu z PENB při zachování návrhového bodu −15 °C."""
    def hours(mu, sd=8.0):
        raw = {t: math.exp(-((t - mu) ** 2) / (2 * sd ** 2)) for t in range(-18, 31)}
        k = 8760 / sum(raw.values())
        return {t: v * k for t, v in raw.items()}

    def q_ut(mu):
        h = hours(mu)
        return sum(load(t) * h[t] for t in h if t < T_LIM) / 1000

    lo, hi = 0.0, 20.0                      # bisekce na průměrnou venkovní teplotu
    for _ in range(60):
        mid = (lo + hi) / 2
        if q_ut(mid) > Q_UT:
            lo = mid
        else:
            hi = mid
    mu = (lo + hi) / 2
    return hours(mu), mu


H, T_MEAN = bins()
TUV_RATE = Q_TUV * 1000 / 8760             # průměrný výkon na TUV [kW]


def run(n_units):
    """Bilance po binech. TUV má prioritu, obsluhuje ji jedna jednotka při W55."""
    q_ut_hp = q_tuv_hp = q_biv = el_ut = el_tuv = 0.0
    biv_hours = 0.0
    for t, h in H.items():
        if h <= 0:
            continue
        c35, c55 = cap35(t), cap55(t)
        share_tuv = min(1.0, TUV_RATE / c55)          # podíl času s jednotkou na TUV
        need = load(t) if t < T_LIM else 0.0          # nad mezí vytápění se netopí
        # Během ohřevu TUV topí o jednu jednotku méně. Přebytek v ostatních hodinách
        # pomůže jen do objemu akumulace, zbytek musí dokrýt elektrická bivalence.
        def_rate = share_tuv * max(0.0, need - (n_units - 1) * c35)
        shift = AKU_SHIFT / 24.0                      # kW, co akumulace průměrně přesune
        def_ = max(0.0, def_rate - shift)
        hp = need - def_
        if def_ > 0.01:
            biv_hours += h * share_tuv
        q_ut_hp += hp * h / 1000
        q_biv += def_ * h / 1000
        el_ut += (hp / cop35(t) if hp > 0 else 0.0) * h / 1000
        q_tuv_hp += TUV_RATE * h / 1000
        el_tuv += TUV_RATE / cop55(t) * h / 1000
    el = el_ut + el_tuv + q_biv
    q = q_ut_hp + q_tuv_hp + q_biv
    return dict(q=q, q_biv=q_biv, biv_share=q_biv / q, biv_hours=biv_hours,
                el=el, scop=q / el, cost=el * EL)


def peak(n):
    """Situace při −15 °C [kW tepla]."""
    c35, c55 = cap35(T_DES), cap55(T_DES)
    return dict(heat_all=n * c35, heat_tuv=(n - 1) * c35, tuv=c55,
                deficit_tuv=max(0, LOSS - (n - 1) * c35),
                down_all=(n - 1) * c35, down_tuv=max(0, (n - 2) * c35),
                el_in=n * interp(W35, T_DES, "inp"))


def outage(t, days, variant):
    """Výpadek jedné jednotky: kolik elektřiny spotřebuje krytí potřeby po `days` dní."""
    need_ut, need_tuv = load(t), TUV_RATE
    hrs = 24 * days
    if variant == "A":                    # zbyde 1 TČ + elektrokotel 30 kW
        tuv = min(need_tuv, cap55(t))
        heat_hp = min(need_ut, max(0.0, cap35(t) * (1 - tuv / cap55(t))))
        biv = min(30.0, need_ut - heat_hp)
        el = (heat_hp / cop35(t) + tuv / cop55(t) + biv) * hrs / 1000
        cover = (heat_hp + biv + tuv) / (need_ut + need_tuv)
    else:                                 # zbydou 2 TČ
        tuv = min(need_tuv, cap55(t))
        heat_hp = min(need_ut, 2 * cap35(t) * (1 - tuv / cap55(t)) + cap35(t) * (tuv / cap55(t)))
        el = (heat_hp / cop35(t) + tuv / cop55(t)) * hrs / 1000
        cover = (heat_hp + tuv) / (need_ut + need_tuv)
    return dict(el=el, cost=el * EL, cover=cover)


def reserve(n, biv_kw, blocked=False):
    """Rezervovaný příkon: jednotky při −15 °C (jedna na TUV) + elektrická bivalence."""
    units = (n - 1) * interp(W35, T_DES, "inp") + interp(W55, T_DES, "inp")
    p = units if blocked else units + biv_kw
    return dict(units=units, total=p, amps=p * 1000 / (3 ** 0.5 * 400 * 0.98))


if __name__ == "__main__":
    print(f"RH X50 @ −15 °C:  W35 {cap35(-15):.1f} kW / COP {cop35(-15):.2f} / příkon {interp(W35,-15,'inp'):.2f} kW"
          f"   |   W55 {cap55(-15):.1f} kW / COP {cop55(-15):.2f}")
    print(f"Ztráta {LOSS} kW · TUV {Q_TUV:.2f} MWh/rok pro {FLATS} b.j. ({Q_TUV*1000/365:.0f} kWh/den) · "
          f"průměr {TUV_RATE:.2f} kW · průměrná venkovní teplota modelu {T_MEAN:.1f} °C")
    print(f"Nabíjení TUV při −15 °C: {Q_TUV*1000/365/cap55(T_DES):.1f} h/den")
    print(f"Mez vytápění {T_LIM} °C · hodiny pod 0 °C: {sum(v for k,v in H.items() if k<0):.0f} h\n")
    for n in (2, 3):
        p = peak(n)
        print(f"--- {n}× RH X50 — při −15 °C")
        print(f"   všechny na topení: {p['heat_all']:.1f} kW (ztráta {LOSS}, rezerva {p['heat_all']-LOSS:+.1f} kW = {p['heat_all']/LOSS-1:+.0%})")
        print(f"   souběh s TUV:      topení {p['heat_tuv']:.1f} kW + TUV {p['tuv']:.1f} kW → deficit topení {p['deficit_tuv']:.1f} kW")
        print(f"   výpadek 1 jednotky: topení {p['down_all']:.1f} kW ({p['down_all']/LOSS:.0%} ztráty), se souběhem TUV {p['down_tuv']:.1f} kW")
        print(f"   el. příkon všech jednotek na topení: {p['el_in']:.1f} kW")
    print()
    for n in (2, 3):
        r = run(n)
        print(f"--- {n}× RH X50 — rok")
        print(f"   teplo {r['q']:.1f} MWh · z toho bivalence {r['q_biv']:.2f} MWh ({r['biv_share']:.1%}), "
              f"hodin s deficitem {r['biv_hours']:.0f}")
        print(f"   elektřina {r['el']:.1f} MWh · SCOP {r['scop']:.2f} · náklad {r['cost']:,.0f} Kč/rok".replace(',', ' '))
    a, b = run(2), run(3)
    print(f"\nRozdíl provozu A−B: {a['cost']-b['cost']:,.0f} Kč/rok".replace(',', ' '),
          f"· elektřina {a['el']-b['el']:.1f} MWh/rok")
    print("\nVýpadek jedné jednotky na 7 dní:")
    for t in (-15, -10, -5, 0):
        a, b = outage(t, 7, "A"), outage(t, 7, "B")
        print(f"  {t:>3} °C: A {a['el']:.1f} MWh = {a['cost']:>6,.0f} Kč, krytí {a['cover']:.0%}".replace(',', ' ')
              + f"  |  B {b['el']:.1f} MWh = {b['cost']:>6,.0f} Kč, krytí {b['cover']:.0%}".replace(',', ' '))
    print("\nRezervovaný příkon (jednotky při −15 °C, jedna na TUV):")
    for lab, n, biv in (("A: 2 TČ + 22 kW patrony", 2, 22), ("A: 2 TČ + elektrokotel 30 kW", 2, 30),
                        ("B: 3 TČ + 11 kW patrona", 3, 11)):
        r = reserve(n, biv)
        rb = reserve(n, biv, blocked=True)
        print(f"  {lab:<30} jednotky {r['units']:.1f} kW · s bivalencí {r['total']:.1f} kW = {r['amps']:.0f} A"
              f" · s blokací bivalence {rb['total']:.1f} kW = {rb['amps']:.0f} A")
