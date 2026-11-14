#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instalační standard REO HEATING – REO R290 Smart: schémata SM-… v1.0 (schváleno 14. 11. 2026).

Spuštění z kořene repozitáře:  python3 reo-smart-regulace/src/gen_sm.py
Výstup: reo-smart-regulace/schema-SM-P1.svg, -SM-P2, -SM-R1, -SM-R2, -SM-K1, -SM-X1, -SM-E1
Referenční schémata rev. 0 (schema-S1…S4, E1) generuje gen_schemata.py a zůstávají beze změny.

Změny proti rev. 0 (viz README / metodika, kap. Historie):
 - všude zpětný ventil (26) na výstupu TČ – návod kap. 2.8.2 bod 6,
 - regulace podle návodu kap. 4.2.5–4.2.6 (PANEL_CTRL bez termostatu, RT_CTRL s termostatem),
 - SM-K1: RT_CTRL = 2 ZONE.SWITCH (aplikace 4 výrobce), ovladač v technické místnosti.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import symboly as s
import gen_schemata as G
from symboly import (RED, BLUE, YEL, INK, GREY, GRN, add, T, R, P, arrow, num, valve, pump,
                     exp_vessel, logo, safety_valve, mix_valve, drain_cock)

VER = "v1.0 · 11/2026"
CUR = {}


def start(*_):
    code, title, subtitle, ver = CUR["code"], CUR["title"], CUR["sub"], CUR.get("ver", VER)
    s.reset()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {G.W} {G.H}" width="{G.W}" height="{G.H}" '
        f'font-family="Avenir Next, Arial, Helvetica, sans-serif">')
    add(G.STYLE)
    R(0, 0, G.W, G.H, fill="#fff", stroke=None)
    logo(36, 22, 190)
    T(256, 62, title, "ttl")
    T(256, 92, subtitle, "sub")
    T(G.W - 36, 58, f"{code} · REO R290 Smart", "zone", "end")
    T(G.W - 36, 78, ver, "tx", "end")
    add(f'<line x1="30" y1="118" x2="{G.W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')


def check_valve_r(x, y):
    """Zpětný ventil, proudění doprava."""
    add(f'<g transform="translate({x},{y})">'
        f'<path d="M-8,-9 L6,0 L-8,9 Z" fill="#fff" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>'
        f'<line x1="8" y1="-10" x2="8" y2="10" stroke="{INK}" stroke-width="2.6"/></g>')


_primary_orig = G.primary


def primary(a, b, aku_parallel=False):
    _primary_orig(a, b)
    check_valve_r(392, G.FY)
    num(392, G.FY - 40, 26)


G.start = start
G.primary = primary


def setcur(code, title, sub, ver=VER):
    CUR.update(code=code, title=title, sub=sub, ver=ver)


def controller_tech():
    G.controller(590, 230, "nastavení")
    G.sig(f"M636,{G.BUS_TOP} L636,230")
    num(698, 236, 13)


def relay_k1():
    G.box(905, 236, 96, 40, "RELÉ K1", "výstup P_O")
    G.sig(f"M953,{G.BUS_TOP} L953,236")
    G.sig(f"M953,276 L953,{G.FY - 18}")
    num(1018, 252, 20)


def series_aku(ret_from):
    ax, ay, aw, ah = 790, 380, 110, 240
    G.aku(ax, ay, aw, ah, "dle modelu")
    P(f"M{ret_from},{G.RY} L940,{G.RY} L940,470 L{ax + aw},470", BLUE)
    P(f"M{ax},590 L770,590 L770,{G.RY}", BLUE)
    arrow(940, 455, 90, BLUE)
    num(ax + aw / 2, ay - 18, 17)


def thermostat_living(x, label, n=14, conn="C1–L1"):
    G.thermostat(x, 236)
    G.sig(f"M{x + 33},{G.BUS_TOP} L{x + 33},236")
    T(x + 33, 304, f"{label} · {conn}", "sig", "middle")
    num(x + 80, 232, n)


# ================================================================== SM-P1
def sm_p1():
    setcur("SM-P1", "Podlahové vytápění – sériová akumulace",
           "AKU ve vratce, trvale otevřené smyčky · prostorové čidlo ovladače + ekvitermní křivka · TUV")
    start(); G.zones(); G.legend(); G.warn()
    G.primary(1080, 770)
    series_aku(1080)
    T(1340, 512, "rozdělovač podlahy", "tx", "end")
    G.ufh(1080, 1340, G.FY, G.RY, 520, 690, loops=4)
    P(f"M1340,{G.FY} L1366,{G.FY} L1366,{G.RY} L1340,{G.RY}", INK, 3)
    G.overflow_valve(1366, 385)
    num(1066, 500, 15)
    num(1366, 470, 16)
    G.tuv_block()
    G.buses(top_to=1250)
    G.sig(f"M1250,{G.BUS_TOP} L1250,236")
    G.controller(1204, 236, "21,5 °C")
    num(1316, 250, 13)
    T(1250, 318, "standard: čidlo ovladače", "sig", "middle")
    G.thermostat(1080, 236)
    G.sig(f"M1113,{G.BUS_TOP} L1113,236")
    T(1113, 304, "alternativa · C1–L1", "sig", "middle")
    num(1162, 232, 14)
    T(1340, 736, "smyčky trvale otevřené", "tx", "end")
    T(1340, 752, "(hlavice jen výjimečně, např. ložnice)", "tx", "end")
    G.finish("schema-SM-P1.svg")


# ================================================================== SM-P2
def sm_p2():
    setcur("SM-P2", "Podlahové vytápění – paralelní akumulace",
           "AKU jako hydraulický oddělovač, čerpadlo P_O spíná pokojový termostat · zónové ventily · TUV")
    G.s3_core("", "", "")
    T(1340, 512, "rozdělovač podlahy", "tx", "end")
    G.ufh(1080, 1330, G.FY, G.RY, 520, 690, loops=4)
    P(f"M1330,{G.FY} L1366,{G.FY} L1366,{G.RY} L1330,{G.RY}", INK, 3)
    G.overflow_valve(1366, 385)
    num(1066, 500, 15)
    num(1366, 470, 16)
    T(1330, 736, "zónové (termoelektrické) hlavice přípustné", "tx", "end")
    G.tuv_block()
    G.buses(top_to=1300)
    relay_k1()
    controller_tech()
    thermostat_living(1220, "ref. místnost")
    G.finish("schema-SM-P2.svg")


# ================================================================== SM-R1
def sm_r1():
    setcur("SM-R1", "Radiátory – paralelní akumulace",
           "AKU jako hydraulický oddělovač, čerpadlo P_O spíná pokojový termostat · křivka nebo konstantní teplota · TUV")
    G.s3_core("", "", "")
    G.radiators(1330, 1330, ref=True)
    G.tuv_block()
    G.buses(top_to=1300)
    relay_k1()
    controller_tech()
    thermostat_living(1220, "ref. místnost")
    G.finish("schema-SM-R1.svg")


# ================================================================== SM-R2
def sm_r2():
    setcur("SM-R2", "Radiátory – sériová akumulace",
           "Jednoduchý okruh, AKU ve vratce, bez sekundárního čerpadla · čidlo ovladače + křivka · TUV")
    start(); G.zones(); G.legend(); G.warn()
    G.primary(1330, 770)
    series_aku(1330)
    G.radiators(1330, 1330)
    G.tuv_block()
    G.buses(top_to=1250)
    G.sig(f"M1250,{G.BUS_TOP} L1250,236")
    G.controller(1204, 236, "21,0 °C")
    num(1316, 250, 13)
    T(1250, 318, "ref. místnost bez TRV", "sig", "middle")
    G.finish("schema-SM-R2.svg")


# ================================================================== SM-K1
def sm_k1():
    setcur("SM-K1", "Kombinace – radiátory a směšovaná podlaha",
           "Doplňková varianta · 2 zóny, RT_CTRL = 2 ZONE.SWITCH · zóna B přes směšovací ventil TMV1 + P_M1 · TUV")
    ax, ay, aw, ah = G.s3_core("", "", "")
    G.radiators(1330, 1330, ref=False)
    T(1040, 512, "zóna A", "lab")
    G.hop_h(470, ax + aw, 980, 950, RED)
    P("M980,470 L980,640 L1016,640", RED)
    mix_valve(1030, 640)
    num(1004, 690, 22)
    P("M1044,640 L1190,640", RED)
    pump(1075, 640)
    num(1075, 680, 23)
    G.sensor(1118, 618, "T10", "r")
    P("M1118,628 L1118,640", INK, 2)
    num(1119, 680, 24)
    R(1150, 627, 26, 26, fill="#fff", stroke=INK, sw=2, rx=4)
    T(1163, 645, "ϑ", "rs", "middle")
    num(1163, 680, 25)
    G.ufh(1190, 1350, 640, 720, 760, 860, loops=3)
    T(1190, 626, "zóna B – podlaha", "lab")
    P("M1190,720 L950,720 L950,590", BLUE)
    P("M1030,720 L1030,654", BLUE, 5)
    G.tuv_block()
    G.buses(top_to=1300)
    relay_k1()
    G.box(1180, 520, 112, 40, "RELÉ K2", "P_M1 · TMV1")
    G.sig("M1236,560 L1236,582 L1075,582 L1075,622")
    G.sig("M1180,540 L1030,540 L1030,612")
    G.sig(f"M1185,{G.BUS_TOP} L1185,520")
    num(1180, 512, 20)
    controller_tech()
    thermostat_living(1040, "zóna A", 14, "C1–L1")
    thermostat_living(1240, "zóna B", 14, "H1–L1")
    G.finish("schema-SM-K1.svg")


# ================================================================== SM-X1
def sm_x1():
    setcur("SM-X1", "Hydraulické oddělení deskovým výměníkem",
           "Primár TČ s nemrznoucí směsí, sekundár voda · AKU ve vratce sekundáru · P_O spíná termostat · TUV",
           ver="v0.9 · podmíněné ověřením · 11/2026")
    start(); G.zones(); G.legend(); G.warn()
    G.primary(740, 740)
    # výměník
    hx, hy, hw, hh = 740, 300, 60, 170
    R(hx, hy, hw, hh, fill="#EEF2F5", stroke=INK, sw=2.4, rx=4)
    for k in range(1, 8):
        yy = hy + k * hh / 8
        add(f'<line x1="{hx + 6}" y1="{yy}" x2="{hx + hw - 6}" y2="{yy - 14}" stroke="{GREY}" stroke-width="1.6"/>')
    num(hx - 22, hy + 8, 27)
    T(hx + hw / 2 - 6, 292, "primár", "tx", "end")
    T(hx + hw / 2 + 6, 292, "sekundár", "tx")
    # sekundár: výstup → P_O → radiátory
    P(f"M{hx + hw},{G.FY} L1330,{G.FY}", RED)
    pump(850, G.FY)
    valve(882, G.FY)
    num(850, G.FY + 34, 19)
    safety_valve(905, G.FY, drain=40)
    P(f"M968,{G.FY} L968,300", RED, 5)
    exp_vessel(968, 272)
    num(936, 236, 28)
    # sériová AKU ve vratce sekundáru
    ax, ay, aw, ah = 870, 380, 90, 240
    G.aku(ax, ay, aw, ah)
    num(ax + aw / 2, ay - 18, 17)
    P(f"M1330,{G.RY} L985,{G.RY} L985,470 L{ax + aw},470", BLUE)
    P(f"M{ax},590 L830,590 L830,{G.RY} L{hx + hw},{G.RY}", BLUE)
    arrow(985, 455, 90, BLUE)
    G.radiators(1330, 1330, ref=True)
    G.tuv_block()
    G.buses(top_to=1300)
    G.box(760, 226, 96, 40, "RELÉ K1", "výstup P_O")
    G.sig(f"M808,{G.BUS_TOP} L808,226")
    G.sig(f"M808,266 L808,280 L850,280 L850,{G.FY - 18}")
    num(742, 214 + 30, 20)
    thermostat_living(1220, "ref. místnost")
    G.finish("schema-SM-X1.svg")


# ================================================================== SM-E1
def sm_e1():
    G.e1()
    src = os.path.join(G.OUT, "schema-E1.svg")
    svg = open(src, encoding="utf-8").read()
    svg = svg.replace("REO-SCH-E1 · REO R290 Smart", "SM-E1 · REO R290 Smart")
    svg = svg.replace("rev. 0 · 11/2026", VER)
    svg = svg.replace("Způsob připojení (RT_CTRL)", "Termostat: RT_CTRL (PANEL_CTRL jen bez RT)")
    svg = svg.replace("230 V, 3vodičový, ON = TUV", "230 V, 3vodičový, polaritu ověřit testem")
    svg = svg.replace("sekundární čerpadlo za AKU (P_O)", "P_O: běží při topení, v TUV stojí (SM-P2/R1/K1/X1)")
    open(os.path.join(G.OUT, "schema-SM-E1.svg"), "w", encoding="utf-8").write(svg)
    # referenční E1 rev. 0 obnovit přesně (e1() ho přepsal stejným obsahem)
    print("zapsáno schema-SM-E1.svg")


if __name__ == "__main__":
    sm_p1(); sm_p2(); sm_r1(); sm_r2(); sm_k1(); sm_x1(); sm_e1()
