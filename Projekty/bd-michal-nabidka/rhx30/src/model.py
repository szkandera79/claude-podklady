#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BD u Dolu Michal — propočet nabídky rev. 1 s jednotkami RHX30 Pro (11/2026).

Varianta A = 3× RHX30 Pro, varianta B = 4× RHX30 Pro (4. jednotka jako záloha se slevou 40 %).
Srovnání se zářijovou nabídkou (2× / 3× RH X50) STEJNOU metodou.

Vstupy domu, teplotní křivka trvání a potřeba TUV se přebírají z ../../src/model.py (PENB, 24 b.j.).
Proti zářijovému modelu se navíc počítá provoz při částečném výkonu: kaskáda v každém binu
volí počet běžících jednotek a COP se interpoluje mezi body MIN a MAX výkonové mapy
(pod minimem jedna jednotka cykluje, COP_MIN × 0,9). Ohřev TUV vždy jedna jednotka na plný výkon při W55.
Volbou --max se spočte postaru (všechny jednotky na MAX), pro kontrolu se zářím.

Čísla z výstupu jsou ručně přepsaná do nabidka.body.html a spolecnici.body.html.
    python3 bd-michal-nabidka/rhx30/src/model.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "src"))
from model import H, LOSS, T_DES, T_LIM, TUV_RATE, Q_TUV, Q_UT, FLATS, EL, AKU_SHIFT, load  # noqa: E402

MAX_ONLY = "--max" in sys.argv


class Unit:
    def __init__(self, name, path):
        d = json.loads(Path(path).read_text())
        self.name, self.amb, self.h = name, d["amb_heat"], d["heat"]

    def v(self, w, mode, key, t):
        xs, ys = self.amb, self.h[w][mode][key]
        t = max(min(t, xs[-1]), xs[0])
        for i in range(len(xs) - 1):
            if xs[i] <= t <= xs[i + 1]:
                return ys[i] + (ys[i + 1] - ys[i]) * (t - xs[i]) / (xs[i + 1] - xs[i])

    def cap(self, t, w="35"):
        return self.v(w, "MAX", "cap", t)

    def cop_at(self, q, t, w="35"):
        """COP jednotky při výkonu q (kW) — interpolace mezi MIN a MAX, pod MIN cykluje."""
        cmax, pmax = self.v(w, "MAX", "cap", t), self.v(w, "MAX", "cop", t)
        if MAX_ONLY:
            return pmax
        cmin, pmin = self.v(w, "MIN", "cap", t), self.v(w, "MIN", "cop", t)
        if q <= cmin:
            return pmin * 0.9
        return pmin + (pmax - pmin) * (q - cmin) / (cmax - cmin)


X50 = Unit("RH X50", HERE.parent.parent / "src" / "rh-x50-data.json")
RHX = Unit("RHX30 Pro", HERE / "rhx30-data.json")
SPIRAL_AKU = 18.0          # kW, spirály 2 × 9 kW v akumulaci (v ceně obou variant)


def heat_el(u, need, avail, t):
    """Nejlepší rozdělení potřeby `need` mezi `avail` jednotek → (teplo z TČ, elektřina)."""
    if need <= 0 or avail == 0:
        return 0.0, 0.0
    cmax = u.cap(t)
    if need >= avail * cmax:
        return avail * cmax, avail * cmax / u.cop_at(cmax, t)
    best = None
    for k in range(1, avail + 1):
        q = need / k
        if q > cmax:
            continue
        el = need / u.cop_at(q, t)
        best = el if best is None else min(best, el)
    return need, best


def run(u, n):
    q_ut = q_tuv = q_biv = el_ut = el_tuv = biv_h = 0.0
    for t, h in H.items():
        c55 = u.cap(t, "55")
        share = min(1.0, TUV_RATE / c55)
        need = load(t) if t < T_LIM else 0.0
        e_hp = 0.0
        def_ = 0.0
        for frac, avail in ((share, n - 1), (1 - share, n)):
            hp, e = heat_el(u, need, avail, t)
            def_ += frac * (need - hp)
            e_hp += frac * e
        def_ = max(0.0, def_ - AKU_SHIFT / 24.0)
        if def_ > 0.01:
            biv_h += h * share
        q_ut += (need - def_) * h / 1000
        q_biv += def_ * h / 1000
        el_ut += e_hp * h / 1000
        q_tuv += TUV_RATE * h / 1000
        el_tuv += TUV_RATE / u.v("55", "MAX", "cop", t) * h / 1000
    q = q_ut + q_tuv + q_biv
    el = el_ut + el_tuv + q_biv
    return dict(q=q, q_biv=q_biv, biv_h=biv_h, el=el, scop=q / el, cost=el * EL,
                scop_ut=(q_ut + q_biv) / (el_ut + q_biv), scop_tuv=q_tuv / el_tuv)


def peak(u, n):
    c35, c55 = u.cap(T_DES), u.cap(T_DES, "55")
    return dict(all=n * c35, with_tuv=(n - 1) * c35, tuv=c55, def_tuv=max(0, LOSS - (n - 1) * c35),
                down=(n - 1) * c35, down_tuv=(n - 2) * c35)


def outage(u, n, t, days=7, spiral=SPIRAL_AKU):
    """Výpadek jedné jednotky: n−1 jednotek, TUV má přednost, chybějící teplo dodají spirály v AKU."""
    need, tuv = load(t), TUV_RATE
    c35, c55 = u.cap(t), u.cap(t, "55")
    share = min(1.0, tuv / c55)
    hp = share * min(need, (n - 2) * c35) + (1 - share) * min(need, (n - 1) * c35)
    _, e1 = heat_el(u, min(need, (n - 2) * c35), n - 2, t)
    _, e2 = heat_el(u, min(need, (n - 1) * c35), n - 1, t)
    e = share * e1 + (1 - share) * e2
    biv = min(spiral, need - hp)
    el = (e + tuv / u.v("55", "MAX", "cop", t) + biv) * 24 * days / 1000
    return dict(el=el, cost=el * EL, cover=(hp + biv) / need if need else 1)


def reserve(u, n, biv=0.0):
    p = (n - 1) * u.v("35", "MAX", "inp", T_DES) + u.v("55", "MAX", "inp", T_DES) + biv
    return p, p * 1000 / (3 ** 0.5 * 400 * 0.98)


# ---- ceny (bez DPH)
INNER = 740_000                 # vnitřek kotelny (vzor: 1 600 000 − 2 × 430 000), jako u BD Jandova
SPIRALS, ROZV = 60_000, 40_000  # spirály 5 × 12 000, podružný rozvaděč — v obou variantách
UNIT, EXTRA = 350_000, 210_000  # RHX30 Pro; záložní jednotka se slevou 40 % (jako BD Jandova, 2. 11. 2026)
PRICE = {"A": INNER + SPIRALS + ROZV + 3 * UNIT,
         "B": INNER + SPIRALS + ROZV + 3 * UNIT + EXTRA,
         "X50-A": 1_790_000, "X50-B": 2_090_000}
SERVICE = {"A": 35_000, "B": 40_000, "X50-A": 25_000, "X50-B": 35_000}   # Kč/rok, orientačně
DIRECT_KWH = 3.5                # Kč/kWh tepla přímotopem (3 500 Kč/MWh)


def fmt(x):
    return f"{x:,.0f}".replace(",", " ")


if __name__ == "__main__":
    print(f"{'MAX-only' if MAX_ONLY else 'částečný výkon'} · ztráta {LOSS} kW · ÚT {Q_UT} + TUV {Q_TUV:.2f} MWh · {FLATS} b.j.")
    for u in (X50, RHX):
        print(f"{u.name} @ −15: W35 {u.cap(-15):.1f} kW COP {u.v('35','MAX','cop',-15):.2f} příkon {u.v('35','MAX','inp',-15):.2f}"
              f" | W55 {u.cap(-15,'55'):.1f} kW COP {u.v('55','MAX','cop',-15):.2f}"
              f" | MIN W35 @−15 {u.v('35','MIN','cap',-15):.1f} kW, @+7 {u.v('35','MIN','cap',7):.1f} kW COP {u.v('35','MIN','cop',7):.2f}")
    print()
    cases = [("X50-A", X50, 2), ("X50-B", X50, 3), ("A", RHX, 3), ("B", RHX, 4)]
    res = {}
    for key, u, n in cases:
        r = run(u, n)
        p = peak(u, n)
        res[key] = r
        price = PRICE[key]
        run_cost = r["cost"] + SERVICE[key]
        print(f"--- {key}: {n}× {u.name} · cena {fmt(price)} Kč ({fmt(price/FLATS)}/byt, {fmt(price/p['all'])} Kč/kW)")
        print(f"   −15 °C: vše {p['all']:.1f} kW ({p['all']/LOSS:.0%}) · souběh TUV topení {p['with_tuv']:.1f} → deficit {p['def_tuv']:.1f}"
              f" · výpadek {p['down']:.1f} kW ({p['down']/LOSS:.0%}), s TUV {p['down_tuv']:.1f}")
        print(f"   rok: teplo {r['q']:.1f} MWh, bivalence {r['q_biv']:.2f} MWh / {r['biv_h']:.0f} h · el. {r['el']:.1f} MWh"
              f" · SCOP {r['scop']:.2f} (ÚT {r['scop_ut']:.2f}, TUV {r['scop_tuv']:.2f}) · elektřina {fmt(r['cost'])} Kč"
              f" = {r['cost']/r['q']/1000:.2f} Kč/kWh · + servis {fmt(SERVICE[key])} = {fmt(run_cost)} ({fmt(run_cost/FLATS)}/byt)")
        o = outage(u, n, -15)
        biv = 0 if key != "X50-A" else 30
        rp, amps = reserve(u, n, biv)
        print(f"   výpadek týden −15 °C: {o['el']:.1f} MWh = {fmt(o['cost'])} Kč, krytí {o['cover']:.0%}"
              f" · rezervovaný příkon {rp:.1f} kW = {amps:.0f} A")
    print()
    d = res["X50-B"]["el"] - res["B"]["el"]
    print(f"B vs X50-B: elektřina −{d:.1f} MWh/rok = −{fmt(d*EL)} Kč/rok ({d/res['X50-B']['el']:.0%}),"
          f" za 15 let {fmt(d*EL*15)} Kč; cena +{fmt(PRICE['B']-PRICE['X50-B'])}")
    d = res["X50-A"]["el"] - res["A"]["el"]
    print(f"A vs X50-A: elektřina −{d:.1f} MWh/rok = −{fmt(d*EL)} Kč/rok; cena +{fmt(PRICE['A']-PRICE['X50-A'])}")
    q = res["B"]["q"]
    print(f"Přímotop: {fmt(q*DIRECT_KWH*1000)} Kč/rok ({fmt(q*DIRECT_KWH*1000/FLATS)}/byt) · B úspora "
          f"{fmt(q*DIRECT_KWH*1000-res['B']['cost'])} Kč/rok")
    for t in (-15, -10, -5, 0, 7):
        print(f"  {t:>3} °C potřeba {load(t):.1f} kW | RHX: 1 jedn. {RHX.cap(t):.1f}, 3× {3*RHX.cap(t):.1f}, 4× {4*RHX.cap(t):.1f}"
              f" | X50 3× {3*X50.cap(t):.1f}")
