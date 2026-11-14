#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schémata REO R290 Smart — regulace komfortní teploty (hydraulika S1–S4 + elektro E1).

Spuštění z kořene repozitáře:  python3 reo-smart-regulace/src/gen_schemata.py
Výstup: reo-smart-regulace/schema-S1.svg … schema-S4.svg, schema-E1.svg
Styl a symboly převzaty z reo-schemata-zapojeni (src/symboly.py).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import symboly as s
from symboly import (RED, BLUE, YEL, TV, SV, INK, GREY, GRN, GRNL, add, T, R, P, arrow, num,
                     valve, antifreeze, separator, pump, exp_vessel, heat_pump, radiator,
                     thermostat, logo, safety_valve, drain_cock, rad_vent, mag_filter,
                     mix_valve, three_way, check_valve, tank_tuv)

OUT = os.path.dirname(HERE)
W, H = 1400, 930
ZT, ZB = 140, 900
WALL, LIV = 360, 1000          # obvodová zeď / hranice obytných prostor
FY, RY = 330, 440              # výstup / vratka
BUS_TOP, BUS_BOT = 212, 878    # trasy signálních kabelů

STYLE = f'''<style>
 .t{{fill:{INK};font-size:14px}} .ts{{fill:{INK};font-size:13px}}
 .tx{{fill:{GREY};font-size:11.5px}} .tb{{fill:{INK};font-size:15px;font-weight:bold}}
 .ttl{{fill:{INK};font-size:28px;font-weight:bold}} .sub{{fill:{GRN};font-size:18px;font-weight:bold}}
 .zone{{fill:{GREY};font-size:12px;font-weight:bold;letter-spacing:1.6px}}
 .num{{fill:#fff;font-size:14px;font-weight:bold}} .tank{{fill:{INK};font-size:24px;font-weight:bold}}
 .lcd{{fill:{GRN};font-size:12px;font-weight:bold}}
 .rs{{fill:{INK};font-size:10.5px;font-weight:bold;letter-spacing:.6px}}
 .lab{{fill:{INK};font-size:13px;font-weight:bold}} .g{{fill:{GREY};font-size:7px}}
 .sig{{fill:#9A6B00;font-size:11.5px;font-weight:bold}}
 .term{{fill:{INK};font-size:12px;font-weight:bold;font-family:Menlo,Consolas,monospace}}
</style>'''


# ------------------------------------------------------------------ pomocné prvky
def start(code, title, subtitle):
    s.reset()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="Avenir Next, Arial, Helvetica, sans-serif">')
    add(STYLE)
    R(0, 0, W, H, fill="#fff", stroke=None)
    logo(36, 22, 190)
    T(256, 62, title, "ttl")
    T(256, 92, subtitle, "sub")
    T(W - 36, 58, f"{code} · REO R290 Smart", "zone", "end")
    T(W - 36, 78, "rev. 0 · 11/2026", "tx", "end")
    add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')


def zones():
    R(30, ZT, WALL - 30, ZB - ZT, fill="#F2F6F9", stroke=None, rx=10)
    R(LIV, ZT, W - 30 - LIV, ZB - ZT, fill="#FBF6EF", stroke=None, rx=10)
    for xx in (WALL, LIV):
        add(f'<line x1="{xx}" y1="{ZT}" x2="{xx}" y2="{ZB}" stroke="{GREY}" stroke-width="2" stroke-dasharray="10 7"/>')
    T(48, ZT + 26, "VENKU", "zone")
    T(WALL + 18, ZT + 26, "TECHNICKÁ MÍSTNOST", "zone")
    T(LIV + 18, ZT + 26, "OBYTNÉ PROSTORY", "zone")
    T(WALL + 4, ZB - 10, "obvodová zeď", "tx")


def legend(y=560):
    items = [(RED, None, "výstup – topná voda"), (BLUE, None, "vratka – ochlazená voda"),
             (YEL, "8 6", "signální / ovládací kabel"), (TV, None, "teplá užitková voda"),
             (SV, None, "studená voda")]
    for i, (c, d, txt) in enumerate(items):
        yy = y + i * 22
        P(f"M50,{yy} L92,{yy}", c, 5, d)
        T(104, yy + 4, txt, "ts")


def warn(y=700):
    R(44, y, 296, 112, fill="#FFF4DA", stroke=YEL, sw=2, rx=8)
    add(f'<path d="M64,{y + 22} L78,{y + 46} L50,{y + 46} Z" fill="{YEL}"/>')
    T(64, y + 43, "!", "num", "middle")
    T(88, y + 26, "R290 je hořlavý plyn", "lab")
    T(88, y + 46, "Separátor (4) s odvzdušněním a pojistný", "tx")
    T(88, y + 62, "ventil patří VENKU hned za jednotku.", "tx")
    T(88, y + 78, "Ochranná zóna dle návodu: 0,5 m kolem,", "tx")
    T(88, y + 94, "2 m nad výfukem, 3 m od oken.", "tx")


def hop_v(x, y1, y2, ycross, c):
    """Svislé potrubí x od y1 do y2 s obloučkem přes vodorovné potrubí ve výšce ycross."""
    P(f"M{x},{y1} L{x},{ycross - 12} A12,12 0 0 1 {x},{ycross + 12} L{x},{y2}", c)


def hop_h(y, x1, x2, xcross, c, extra=""):
    """Vodorovné potrubí (x1 < x2) s obloučkem přes svislé potrubí v xcross."""
    P(f"M{x1},{y} L{xcross - 12},{y} A12,12 0 0 1 {xcross + 12},{y} L{x2},{y}{extra}", c)


def sensor(x, y, lab, side="r"):
    add(f'<circle cx="{x}" cy="{y}" r="10" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    T(x, y + 4, "T", "rs", "middle")
    T(x + (16 if side == "r" else -16), y + 4, lab, "sig", "start" if side == "r" else "end")


def sig(d):
    P(d, YEL, 2.6, "8 6")


def box(x, y, w, h, l1, l2=None, fill="#fff", stroke=INK):
    R(x, y, w, h, fill=fill, stroke=stroke, sw=2.2, rx=6)
    if l2:
        T(x + w / 2, y + h / 2 - 2, l1, "rs", "middle")
        T(x + w / 2, y + h / 2 + 13, l2, "tx", "middle")
    else:
        T(x + w / 2, y + h / 2 + 4, l1, "rs", "middle")


def controller(x, y, txt="21,5 °C"):
    """Kabelový ovladač (dotykový displej) s vestavěným čidlem prostorové teploty."""
    R(x, y, 92, 62, fill="#fff", stroke=INK, sw=2.4, rx=8)
    R(x + 8, y + 8, 76, 34, fill=GRNL, stroke=GRN, sw=1.5, rx=3)
    T(x + 46, y + 30, txt, "lcd", "middle")
    T(x + 46, y + 55, "OVLADAČ", "rs", "middle")


def trv(x, y):
    """Termostatická hlavice na přívodu tělesa (zjednodušeně)."""
    add(f'<rect x="{x - 22}" y="{y - 8}" width="14" height="16" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/>'
        f'<line x1="{x - 8}" y1="{y}" x2="{x}" y2="{y}" stroke="{INK}" stroke-width="2"/>')


def overflow_valve(x, y):
    """Přepouštěcí (diferenční) ventil ve svislém obtoku — ventil + pružina."""
    valve(x, y, vert=True)
    add(f'<path d="M{x + 14},{y - 10} l8,4 l-8,4 l8,4 l-8,4" fill="none" stroke="{INK}" stroke-width="1.8"/>')


def ufh(x0, x1, ys, yr, ytop, ybot, loops=4):
    """Rozdělovač podlahového topení: přívodní lišta (ys), zpětná lišta (yr), smyčky v podlaze ytop–ybot."""
    R(x0 - 6, ytop - 6, x1 - x0 + 12, ybot - ytop + 12, fill="#EFE6DA", stroke=None, rx=6)
    T(x1, ybot + 22, "podlaha – topné smyčky", "tx", "end")
    step = (x1 - x0) / loops
    for i in range(loops):
        xa = x0 + 14 + i * step
        xb = xa + step - 34
        # přívod dolů (za zpětnou lištou)
        P(f"M{xa},{ys} L{xa},{ytop + 8}", RED, 4)
        n = 4
        pts = [f"M{xa},{ytop + 8}"]
        dy = (ybot - ytop - 16) / n
        for k in range(n):
            yk = ytop + 8 + dy * (k + 0.5)
            pts.append(f"L{xa if k % 2 else xb},{yk}")
        pts.append(f"L{xb},{ybot - 8}")
        P(" ".join(pts), "#A9467A", 3)
        P(f"M{xb},{ybot - 8} L{xb},{yr}", BLUE, 4)
    # lišty (zpětná přes přívody)
    P(f"M{x0},{ys} L{x1},{ys}", RED, 9)
    add(f'<path d="M{x0},{yr} L{x1},{yr}" stroke="#fff" stroke-width="15" fill="none"/>')
    P(f"M{x0},{yr} L{x1},{yr}", BLUE, 9)


def tuv_block(sens=True):
    """Zásobník TUV se spirálou, větev B trojcestného ventilu, pojistná skupina, TV/SV."""
    tx, ty, tw, th = 580, 600, 160, 240
    tank_tuv(tx, ty, tw, th)
    # spirála
    pts = [f"M{tx},{640}", f"L{tx + 14},{640}"]
    for k in range(9):
        pts.append(f"L{tx + (52 if k % 2 == 0 else 14)},{650 + k * 16}")
    pts.append(f"L{tx},{790}")
    P(" ".join(pts), RED, 3)
    # B větev: SV1 → spirála, zpět do vratky (před filtrem)
    hop_v(540, FY + 14, 640, RY, RED)
    P(f"M540,640 L{tx},640", RED)
    arrow(560, 640, 0, RED)
    P(f"M{tx},790 L490,790 L490,{RY}", BLUE)
    arrow(490, 700, 270, BLUE)
    num(520, 610, 8)
    num(tx + tw / 2, ty - 18, 9)
    if sens:
        sensor(690, 760, "T9")
        num(726, 800, 10)
    # TV
    P(f"M{tx + tw},650 L965,650", TV)
    add(f'<path d="M965,642 L980,650 L965,658 Z" fill="{TV}"/>')
    T(962, 638, "TV do domu", "lab", "end")
    # SV
    P(f"M985,820 L{tx + tw},820", SV)
    arrow(940, 820, 180, SV)
    T(962, 846, "SV z vodovodu", "lab", "end")
    valve(905, 820)
    check_valve(865, 820)
    P("M825,820 L825,792", SV, 5)
    exp_vessel(825, 764)
    num(860, 760, 12)
    safety_valve(780, 820, drain=40)
    num(780, 868, 11)


def primary(code_supply_end, return_from_x, aku_parallel=False):
    """TČ venku + armatury + SV1, filtr, expanzní nádoba, plnění."""
    heat_pump(40, 290, 190, 180)
    T(135, 278, "REO R290 Smart", "lab", "middle")
    num(54, 270, 1)
    T(135, 504, "venkovní čidlo T4 je v jednotce", "tx", "middle")
    # výstup
    P(f"M230,{FY} L{code_supply_end},{FY}", RED)
    valve(262, FY)
    separator(312, FY)
    num(262, FY - 44, 2)
    num(352 - 8, FY - 78, 4)
    arrow(420, FY, 0, RED)
    three_way(540, FY)
    # vratka
    P(f"M{return_from_x},{RY} L230,{RY}", BLUE)
    valve(262, RY)
    antifreeze(305, RY)
    num(305, RY + 56, 3)
    valve(385, RY)
    mag_filter(420, RY)
    valve(455, RY)
    num(420, RY + 66, 5)
    arrow(600, RY, 180, BLUE)
    # expanzní nádoba + plnění/vypouštění
    P(f"M640,{RY} L640,{RY + 40}", BLUE, 5)
    exp_vessel(640, RY + 68)
    num(600, RY + 70, 6)
    drain_cock(702, RY)
    num(702, RY + 58, 7)


def buses(top_to=None, bot=True):
    """Signální kabely z elektrorozvaděče TČ: horní trasa (ovladač, termostat, relé) a spodní (čidla)."""
    sig(f"M215,290 L215,{BUS_TOP} L{top_to},{BUS_TOP}")
    T(236, BUS_TOP - 8, "chránička se signálními kabely (ovladač, termostat, výstupy)", "sig")
    if bot:
        sig(f"M222,470 L222,482 L345,482 L345,{BUS_BOT} L700,{BUS_BOT} L700,770")


def finish(name):
    add('</svg>')
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s.o))
    print("zapsáno", path)


# ================================================================== S1
def s1():
    start("REO-SCH-S1", "Bez akumulační nádrže – podlahové vytápění",
          "Přímé napojení, ekvitermní křivka + prostorová teplota z ovladače · ohřev TUV")
    zones(); legend(); warn()
    primary(1080, 1080)
    # podlaha: rozdělovač
    T(1080, FY - 14, "rozdělovač", "tx")
    ufh(1080, 1340, FY, RY, 520, 690, loops=4)
    P(f"M1340,{FY} L1366,{FY} L1366,{RY} L1340,{RY}", INK, 3)
    overflow_valve(1366, 385)
    num(1066, 500, 15)
    num(1366, 470, 16)
    tuv_block()
    # ovladač a termostat
    buses(top_to=1250)
    sig(f"M1250,{BUS_TOP} L1250,236")
    controller(1204, 236 - 62 + 62, "21,5 °C")
    num(1316, 250, 13)
    thermostat(1100, 180 + 20)
    sig(f"M1133,{BUS_TOP} L1133,200")
    T(1133, 270, "volitelně C1–L1", "sig", "middle")
    num(1186, 196, 14)
    T(1250, 736, "všechny smyčky trvale otevřené", "tx", "end")
    T(1250, 752, "(bez zónových ventilů v referenční místnosti)", "tx", "end")
    finish("schema-S1.svg")


# ================================================================== S2
def radiators(x_end_sup, x_end_ret, ref=True):
    """Dvě otopná tělesa mezi výstupem a vratkou; první s TRV, druhé v referenční místnosti bez TRV."""
    for i, x in enumerate((1040, 1200)):
        radiator(x, 356, 130, 60)
        rad_vent(x + 118, 356)
        P(f"M{x + 12},{FY} L{x + 12},356", RED, 5)
        P(f"M{x + 118},416 L{x + 118},{RY}", BLUE, 5)
        if i == 0 or not ref:
            trv(x + 12, 343)
    num(1060, 470, 15)
    T(1040, 494, "radiátory s TRV (21)" if not ref else "s TRV (21)", "tx")
    if ref:
        T(1200, 494, "referenční místnost", "tx")
        T(1200, 508, "bez TRV, plně otevřené", "tx")
    P(f"M1330,{FY} L1366,{FY} L1366,{RY} L1330,{RY}", INK, 3)
    overflow_valve(1366, 385)
    num(1366, 470, 16)


def aku(x, y, w, h, vol=""):
    add(f'<defs><linearGradient id="ak2" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#F7B9A6"/><stop offset="0.5" stop-color="#F3E3E6"/>'
        f'<stop offset="1" stop-color="#B9D1EE"/></linearGradient></defs>')
    R(x, y, w, h, fill="url(#ak2)", stroke=INK, sw=2.6, rx=40)
    T(x + w / 2, y + h / 2 + 2, "AKU", "tank", "middle")
    if vol:
        T(x + w / 2, y + h / 2 + 22, vol, "ts", "middle")


def s2():
    start("REO-SCH-S2", "Sériová akumulační nádrž ve vratce – radiátory",
          "Objem pro odmrazování a stabilní chod bez sekundárního čerpadla · ekviterm + referenční místnost")
    zones(); legend(); warn()
    primary(1330, 770)
    # sériová AKU ve vratce
    ax, ay, aw, ah = 790, 380, 110, 240
    aku(ax, ay, aw, ah, "100–300 l")
    P(f"M1330,{RY} L940,{RY} L940,470 L{ax + aw},470", BLUE)
    P(f"M{ax},590 L770,590 L770,{RY}", BLUE)
    arrow(940, 455, 90, BLUE)
    num(ax + aw / 2, ay - 18, 17)
    radiators(1330, 1330)
    tuv_block()
    buses(top_to=1250)
    sig(f"M1250,{BUS_TOP} L1250,236")
    controller(1204, 236, "21,0 °C")
    num(1316, 250, 13)
    finish("schema-S2.svg")


# ================================================================== S3
def s3_core(code, title, subtitle):
    start(code, title, subtitle)
    zones(); legend(); warn()
    primary(770, 745)
    ax, ay, aw, ah = 790, 380, 100, 240
    aku(ax, ay, aw, ah)
    # primár do AKU
    P(f"M770,{FY} L770,410 L{ax},410", RED)
    P(f"M{ax},590 L745,590 L745,{RY}", BLUE)
    num(ax + aw / 2, ay - 18, 17)
    sensor(ax + 22, 450, "T8", "r")
    sensor(ax + 22, 560, "T7", "r")
    num(ax + aw + 22, 505, 18)
    sig(f"M{ax + 22},570 L{ax + 22},{BUS_BOT} L700,{BUS_BOT}")
    # sekundár zóna A
    P(f"M{ax + aw},410 L920,410 L920,{FY} L1330,{FY}", RED)
    pump(955, FY)
    valve(985, FY)
    num(955, FY + 34, 19)
    P(f"M1330,{RY} L950,{RY} L950,590 L{ax + aw},590", BLUE)
    arrow(950, 520, 90, BLUE)
    return ax, ay, aw, ah


def s3():
    s3_core("REO-SCH-S3", "Paralelní akumulační nádrž – radiátory",
            "AKU jako hydraulický oddělovač, sekundární čerpadlo P_O řízené pokojovým termostatem · TUV")
    radiators(1330, 1330, ref=True)
    tuv_block()
    buses(top_to=1286)
    # relé pro čerpadlo P_O
    box(905, 236, 96, 40, "RELÉ K1", "výstup P_O")
    sig(f"M953,{BUS_TOP} L953,236")
    sig(f"M953,276 L953,{FY - 18}")
    num(1018, 252, 20)
    thermostat(1110, 236)
    sig(f"M1143,{BUS_TOP} L1143,236")
    T(1143, 304, "C1–L1", "sig", "middle")
    num(1192, 232, 14)
    controller(1240, 236, "21,0 °C")
    sig(f"M1286,{BUS_TOP} L1286,236")
    num(1348, 230, 13)
    finish("schema-S3.svg")


# ================================================================== S4
def s4():
    ax, ay, aw, ah = s3_core("REO-SCH-S4", "Dvě zóny – radiátory a směšovaná podlaha",
                             "Zóna A radiátory (P_O), zóna B podlaha přes směšovací ventil TMV1 + P_M1 · AKU · TUV")
    radiators(1330, 1330, ref=False)
    T(1040, 512, "zóna A", "lab")
    # zóna B: z AKU (horní polovina) → směšovací ventil → P_M1 → T10 → pojistný termostat → rozdělovač
    hop_h(470, ax + aw, 980, 950, RED)
    P(f"M980,470 L980,640 L1016,640", RED)
    mix_valve(1030, 640)
    num(1004, 690, 22)
    P(f"M1044,640 L1190,640", RED)
    pump(1075, 640)
    num(1075, 680, 23)
    sensor(1118, 618, "T10", "r")
    P("M1118,628 L1118,640", INK, 2)
    num(1119, 680, 24)
    R(1150, 627, 26, 26, fill="#fff", stroke=INK, sw=2, rx=4)
    T(1163, 645, "ϑ", "rs", "middle")
    num(1163, 680, 25)
    ufh(1190, 1350, 640, 720, 760, 860, loops=3)
    T(1190, 626, "zóna B – podlaha", "lab")
    # vratka zóny B → AKU, obtok směšovače
    P(f"M1190,720 L950,720 L950,590", BLUE)
    P("M1030,720 L1030,654", BLUE, 5)
    tuv_block()
    buses(top_to=1300)
    box(1180, 520, 112, 40, "RELÉ K2", "P_M1 · TMV1")
    sig(f"M1236,560 L1236,582 L1075,582 L1075,622")
    sig("M1180,540 L1030,540 L1030,612")
    sig(f"M1185,{BUS_TOP} L1185,520")
    box(905, 236, 96, 40, "RELÉ K1", "výstup P_O")
    sig(f"M953,{BUS_TOP} L953,236")
    sig(f"M953,276 L953,{FY - 18}")
    num(1180, 512, 20)
    # termostaty
    thermostat(1040, 236)
    sig(f"M1073,{BUS_TOP} L1073,236")
    T(1073, 304, "zóna A · C1–L1", "sig", "middle")
    num(1120, 232, 14)
    controller(1208, 236, "B 21,5 °C")
    num(1316, 230, 13)
    T(1254, 314, "zóna B · prostorová teplota", "sig", "middle")
    finish("schema-S4.svg")


# ================================================================== E1
def e1():
    s.reset()
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 980" width="{W}" height="980" '
        f'font-family="Avenir Next, Arial, Helvetica, sans-serif">')
    add(STYLE)
    R(0, 0, W, 980, fill="#fff", stroke=None)
    logo(36, 22, 190)
    T(256, 62, "Schéma elektrického zapojení regulace", "ttl")
    T(256, 92, "Svorky řídicí desky TČ, pokojové termostaty, výstupy, čidla a Smart Grid", "sub")
    T(W - 36, 58, "REO-SCH-E1 · REO R290 Smart", "zone", "end")
    T(W - 36, 78, "rev. 0 · 11/2026", "tx", "end")
    add(f'<line x1="30" y1="118" x2="{W - 30}" y2="118" stroke="{GRN}" stroke-width="3"/>')

    # deska
    bx, by, bw, bh = 480, 160, 420, 660
    R(bx, by, bw, bh, fill="#F5F7F8", stroke=INK, sw=2.6, rx=12)
    T(bx + bw / 2, by + 30, "ŘÍDICÍ DESKA TČ", "tb", "middle")
    T(bx + bw / 2, by + 48, "elektrorozvaděč ve venkovní jednotce", "tx", "middle")
    T(bx + bw / 2, by + 64, "(svorkovnice J22/J23, konektory čidel)", "tx", "middle")

    def term(x, y, labels, anchor="l"):
        """Svorkovnice: řada políček s názvy svorek; anchor l = na levé hraně desky, r = pravé."""
        w = 46
        x0 = x if anchor == "l" else x - w * len(labels)
        for i, lb in enumerate(labels):
            R(x0 + i * w, y - 13, w, 26, fill="#fff", stroke=INK, sw=1.6)
            T(x0 + i * w + w / 2, y + 4, lb, "term", "middle")
        return x0, x0 + w * len(labels)

    def wire(d, c=INK, dash=None, w=2.4):
        P(d, c, w, dash)

    # ---------------- vlevo: vstupy
    # napájení
    term(bx, 270, ["L", "N", "PE"])
    box(60, 240, 250, 60, "ROZVADĚČ DOMU", "jistič + proudový chránič dle tabulky")
    wire(f"M310,270 L{bx},270", "#7A4E2D", None, 4)
    T(395, 260, "1F: L/N/PE", "tx", "middle")
    T(395, 292, "3F: L1–L3/N/PE", "tx", "middle")
    # SG / EVU
    term(bx, 350, ["SG", "EVU", "GND"])
    box(60, 320, 250, 60, "FV STŘÍDAČ / HDO / ELEKTROMĚR", "bezpotenciálové kontakty")
    wire(f"M310,342 L{bx},342", YEL, "8 6"); wire(f"M310,358 L{bx},358", YEL, "8 6")
    T(395, 332, "J13/J14 · konfig. 7", "tx", "middle")
    # ovladač
    R(bx, 417, 92, 26, fill="#fff", stroke=INK, sw=1.6)
    T(bx + 46, 434, "OVLADAČ", "term", "middle")
    controller(150, 400)
    T(110, 486, "kabelový ovladač – referenční místnost", "tx")
    T(110, 500, "1,5 m nad podlahou, mimo slunce a zdroje tepla", "tx")
    wire(f"M242,430 L{bx},430", YEL, "8 6")
    T(360, 420, "kabel ovladače", "tx", "middle")
    # termostaty
    x0, x1 = term(bx, 560, ["H1", "L1", "C1", "L2", "H2"])
    T(bx + 8, 538, "POKOJOVÉ TERMOSTATY (bezpot. kontakt)", "rs")
    R(44, 510, 300, 300, fill="#FBF6EF", stroke=None, rx=10)
    T(60, 534, "Způsob připojení (RT_CTRL)", "lab")
    rows = [("ZONE.A.SWITCH", "L1–C1: sepnuto = topí zóna A", 570),
            ("ZONE.A.MODE.SW", "L1–H1 topení · L1–C1 chlazení", 630),
            ("2 ZONE.SWITCH", "A: L1–C1 · B1: L1–H1", 690),
            ("3 ZONE.SWITCH", "A: L1–C1 · B1: L1–H1 · B2: L2–H2", 750)]
    for name, txt, yy in rows:
        T(60, yy, name, "term")
        T(60, yy + 18, txt, "tx")
    # kontakty termostatu (ZONE.A.SWITCH) – vodiče
    wire(f"M{bx + 69},573 L{bx + 69},618 L436,618", YEL, "8 6")
    wire(f"M{bx + 115},573 L{bx + 115},636 L436,636", YEL, "8 6")
    thermostat(370, 600)
    T(403, 672, "RT zóna A", "sig", "middle")
    T(403, 688, "(L1–C1)", "tx", "middle")

    # ---------------- vpravo: výstupy
    outs = [
        (250, ["P_O", "N"], "RELÉ K1 → ČERPADLO ZÓNY A", "sekundární čerpadlo za AKU (P_O)"),
        (315, ["P_M1", "N"], "RELÉ K2 → ČERPADLO ZÓNY B", "podlahová zóna za směšovačem"),
        (380, ["ON", "OFF", "N"], "TROJCESTNÝ VENTIL TUV (SV1)", "230 V, 3vodičový, ON = TUV"),
        (445, ["TBH", "N"], "STYKAČ KM1 → VLOŽKA TUV", "topná vložka v zásobníku TUV"),
        (510, ["AHS1", "AHS2"], "EXTERNÍ ZDROJ (kotel)", "bezpotenciálový kontakt"),
        (575, ["AOV1", "AIV1", "GND"], "SMĚŠOVACÍ VENTIL TMV1", "řízení 0–10 V + zpětná vazba, napájení 230 V zvlášť"),
        (640, ["DFR", "ERR"], "SIGNALIZACE", "odmrazování / porucha (kontakty)"),
    ]
    for y, labels, l1, l2 in outs:
        xa, xb = term(bx + bw, y, labels, "r")
        wire(f"M{bx + bw},{y} L1010,{y}", "#7A4E2D" if labels[0] not in ("AOV1", "AHS1", "DFR") else YEL,
             None if labels[0] not in ("AOV1", "AHS1", "DFR") else "8 6", 3)
        box(1010, y - 28, 350, 56, l1, l2)
    R(996, 214, 378, 262, fill="none", stroke=GRN, sw=2, rx=10, extra=' stroke-dasharray="9 6"')
    T(1360, 206, "rozvodnice regulace v domě (doporučeno)", "sig", "end")
    T(bx + bw - 6, 734, "Výstupy 230 V: max. 0,2 A na výstup –", "tx", "end")
    T(bx + bw - 6, 750, "čerpadla, vložku a ventily nad 0,2 A spínat přes relé / stykač.", "tx", "end")

    # ---------------- dole: čidla
    sens = [("T9", "AI6B", "zásobník TUV"), ("T8", "AI3", "AKU nahoře"), ("T7", "AI2", "AKU dole"),
            ("T10", "AI6C", "podlaha zóna B1"), ("T5", "AI0", "podlaha zóna B2"), ("T20", "AI6A", "TWout3 (AHS)")]
    for i, (t, ai, txt) in enumerate(sens):
        x = 520 + i * 60
        R(x - 26, bh + by - 40, 52, 26, fill="#fff", stroke=INK, sw=1.6)
        T(x, bh + by - 22, ai, "term", "middle")
        wire(f"M{x},{bh + by - 14} L{x},{860 + (i % 2) * 40}", YEL, "8 6")
        sensor(x, 870 + (i % 2) * 40, t, "r")
        T(x + 2, 896 + (i % 2) * 40, txt, "tx", "middle")
    T(bx - 10, 880, "čidla NTC (příslušenství);", "tx", "end")
    T(bx - 10, 896, "T9 je součástí dodávky (kabel cca 10 m)", "tx", "end")
    # RS485
    term(bx + bw, 705, ["A", "B"], "r")
    wire(f"M{bx + bw},705 L1010,705", YEL, "8 6")
    box(1010, 677, 350, 56, "RS485 – BMS / KASKÁDA", "nadřazený systém, Modbus (dle dodavatele)")

    T(30, 965, "Zjednodušené orientační schéma – závazné je schéma zapojení v návodu (kap. 2.10) pro konkrétní model a revizi desky. "
               "Před zapojením termostatu změřte, že na svorkách L1/L2 není cizí napětí.", "tx")
    add('</svg>')
    path = os.path.join(OUT, "schema-E1.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s.o))
    print("zapsáno", path)


if __name__ == "__main__":
    s1(); s2(); s3(); s4(); e1()
