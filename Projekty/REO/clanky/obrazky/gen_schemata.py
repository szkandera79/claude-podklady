#!/usr/bin/env python3
"""Schémata zapojení akumulační nádoby k tepelnému čerpadlu (článek REO HEATING).

Spuštění z kořene repozitáře:  python3 REO/clanky/obrazky/gen_schemata.py
Výstup: SVG soubory vedle tohoto skriptu.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

RED = "#D9452B"      # výstup (topná voda)
BLUE = "#2F6FB5"     # zpátečka
BRAND = "#26804B"
DARK = "#1A5433"
INK = "#16241C"
MUTED = "#5C6B62"
LINE = "#C9D3CC"
FONT = "Inter, 'Helvetica Neue', Arial, sans-serif"

Y_SUP, Y_RET = 120, 280      # výška výstupního a vratného potrubí
W, H = 720, 400


def arrow(x, y, d, color):
    """Šipka toku; d = 'r' / 'l' / 'u' / 'd'."""
    s = 7
    pts = {
        "r": [(x + s, y), (x - s, y - s), (x - s, y + s)],
        "l": [(x - s, y), (x + s, y - s), (x + s, y + s)],
        "d": [(x, y + s), (x - s, y - s), (x + s, y - s)],
        "u": [(x, y - s), (x - s, y + s), (x + s, y + s)],
    }[d]
    return f'<polygon points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="{color}"/>'


def pipe(points, color, w=6):
    p = " ".join(f"{x},{y}" for x, y in points)
    return (f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def text(x, y, s, size=14, color=INK, weight=400, anchor="middle", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{st}>{s}</text>')


def pump(x, y, d="r", label=None, ly=None):
    out = [f'<circle cx="{x}" cy="{y}" r="13" fill="#fff" stroke="{INK}" stroke-width="2"/>']
    s = 7
    tri = {"r": f"{x-s+2},{y-s} {x+s},{y} {x-s+2},{y+s}",
           "l": f"{x+s-2},{y-s} {x-s},{y} {x+s-2},{y+s}"}[d]
    out.append(f'<polygon points="{tri}" fill="{INK}"/>')
    if label:
        out.append(text(x, ly if ly else y - 22, label, 12, MUTED))
    return "".join(out)


def heat_pump():
    x0, y0, w, h = 30, 95, 150, 210
    g = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="10" fill="#F4F7F5" stroke="{MUTED}" stroke-width="2"/>']
    cx, cy = 105, 205
    g.append(f'<circle cx="{cx}" cy="{cy}" r="48" fill="#fff" stroke="{MUTED}" stroke-width="2"/>')
    for a in (0, 120, 240):
        g.append(f'<ellipse cx="{cx}" cy="{cy-22}" rx="10" ry="22" fill="{LINE}" '
                 f'transform="rotate({a} {cx} {cy})"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{MUTED}"/>')
    # logo pruh
    g.append(f'<rect x="{x0+12}" y="{y0+12}" width="58" height="8" rx="4" fill="{BRAND}"/>')
    g.append(text(105, 330, "Tepelné čerpadlo", 14, INK, 600))
    g.append(text(105, 348, "REO HEATING", 12, BRAND, 600))
    return "".join(g)


def system_box(kind):
    """Otopná soustava vpravo; kind = 'floor' nebo 'rad'."""
    x0, y0, w, h = 555, 95, 145, 210
    g = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="10" fill="#fff" stroke="{MUTED}" '
         f'stroke-width="2" stroke-dasharray="6 5"/>']
    if kind == "floor":
        g.append('<defs><linearGradient id="fl" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{RED}"/><stop offset="1" stop-color="{BLUE}"/>'
                 '</linearGradient></defs>')
        pts = [(555, Y_SUP), (680, Y_SUP)]
        y = Y_SUP
        right = True
        while y + 25 <= Y_RET - 15:
            y += 25
            xa = 680 if right else 580
            xb = 580 if right else 680
            pts += [(xa, y), (xb, y)]
            right = not right
        pts += [(pts[-1][0], Y_RET), (555, Y_RET)]
        p = " ".join(f"{a},{b}" for a, b in pts)
        g.append(f'<polyline points="{p}" fill="none" stroke="url(#fl)" stroke-width="4" '
                 'stroke-linejoin="round"/>')
        g.append(text(627, 330, "Podlahové topení", 14, INK, 600))
        g.append(text(627, 348, "bez regulace průtoku", 12, MUTED))
    else:
        # stoupačky
        g.append(pipe([(555, Y_SUP), (575, Y_SUP), (575, 214)], RED, 4))
        g.append(pipe([(683, 168), (683, Y_RET), (555, Y_RET)], BLUE, 4))
        for ry in (138, 196):
            g.append(pipe([(575, ry + 8), (598, ry + 8)], RED, 3))
            g.append(pipe([(660, ry + 30), (683, ry + 30)], BLUE, 3))
            g.append(f'<rect x="598" y="{ry}" width="62" height="40" rx="3" fill="#fff" stroke="{INK}" stroke-width="2"/>')
            for fx in range(606, 656, 9):
                g.append(f'<line x1="{fx}" y1="{ry+5}" x2="{fx}" y2="{ry+35}" stroke="{LINE}" stroke-width="3"/>')
            # termostatický ventil
            vx, vy = 588, ry + 8
            g.append(f'<polygon points="{vx-6},{vy-5} {vx+6},{vy+5} {vx+6},{vy-5} {vx-6},{vy+5}" fill="{INK}"/>')
            g.append(f'<rect x="{vx-4}" y="{vy-17}" width="8" height="11" rx="2" fill="{BRAND}"/>')
        g.append(text(627, 330, "Otopná tělesa", 14, INK, 600))
        g.append(text(627, 348, "s termostatickými hlavicemi", 12, MUTED))
    return "".join(g)


def tank(x0, y0, w, h, grad_id, top, bottom, label, sub, ly=None):
    g = [f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>'
         '</linearGradient></defs>',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="22" fill="url(#{grad_id})" '
         f'fill-opacity="0.22" stroke="{INK}" stroke-width="2.5"/>']
    ly = ly or (y0 + h + 30)
    cx = x0 + w / 2
    g.append(text(cx, ly, label, 14, INK, 600))
    if sub:
        g.append(text(cx, ly + 18, sub, 12, MUTED))
    return "".join(g)


def legend(with_pump):
    y = 385
    return "".join([
        pipe([(30, y - 4), (60, y - 4)], RED, 5), text(68, y, "výstup – topná voda", 12, MUTED, anchor="start"),
        pipe([(220, y - 4), (250, y - 4)], BLUE, 5), text(258, y, "zpátečka", 12, MUTED, anchor="start"),
    ]) + ("" if not with_pump else "".join([
        f'<circle cx="355" cy="{y-4}" r="8" fill="#fff" stroke="{INK}" stroke-width="1.5"/>',
        f'<polygon points="352,{y-9} 360,{y-4} 352,{y+1}" fill="{INK}"/>',
        text(370, y, "oběhové čerpadlo", 12, MUTED, anchor="start"),
    ]))


def svg(title, sub, body, with_pump=False):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'font-family="{FONT}" role="img" aria-label="{title}">'
            f'<rect width="{W}" height="{H}" fill="#fff"/>'
            + text(30, 40, title, 19, DARK, 700, "start")
            + text(30, 62, sub, 13, MUTED, 400, "start")
            + body + legend(with_pump) + "</svg>")


# 1 — bez nádoby
def s1():
    b = [heat_pump(), system_box("floor"),
         pipe([(180, Y_SUP), (555, Y_SUP)], RED), pipe([(555, Y_RET), (180, Y_RET)], BLUE),
         arrow(370, Y_SUP, "r", RED), arrow(370, Y_RET, "l", BLUE),
         text(367, 200, "plný průtok, dost vody v okruzích", 13, MUTED, italic=True),
         text(367, 218, "→ nádoba není potřeba", 13, BRAND, 600)]
    return svg("Bez akumulační nádoby", "Ideální soustava: velkoplošné topení bez termostatů v místnostech", "".join(b))


# 2 — sériově na zpátečce
def s2():
    tx, tw = 320, 90
    b = [heat_pump(), system_box("floor"),
         pipe([(180, Y_SUP), (555, Y_SUP)], RED),
         pipe([(555, Y_RET), (tx + tw, Y_RET)], BLUE), pipe([(tx, Y_RET), (180, Y_RET)], BLUE),
         tank(tx, 175, tw, 125, "g2", "#7FA9D8", BLUE, "", "", ly=0),
         arrow(370, Y_SUP, "r", RED), arrow(490, Y_RET, "l", BLUE), arrow(250, Y_RET, "l", BLUE),
         text(365, 232, "50–100 l", 15, INK, 700),
         text(365, 158, "Nádoba na zpátečce", 13, INK, 600)]
    return svg("Sériové zapojení na zpátečce", "Řeší malý objem vody v soustavě – průtokem prochází veškerá vratná voda", "".join(b))


# 3 — paralelně čtyřtrubkově
def s3():
    tx, tw = 320, 90
    b = [heat_pump(), system_box("rad"),
         pipe([(180, Y_SUP), (tx, Y_SUP)], RED), pipe([(tx + tw, Y_SUP), (555, Y_SUP)], RED),
         pipe([(555, Y_RET), (tx + tw, Y_RET)], BLUE), pipe([(tx, Y_RET), (180, Y_RET)], BLUE),
         tank(tx, 95, tw, 210, "g3", RED, BLUE, "", "", ly=0),
         arrow(250, Y_SUP, "r", RED), arrow(250, Y_RET, "l", BLUE), arrow(520, Y_RET, "l", BLUE),
         pump(480, Y_SUP, "r", "čerpadlo soustavy", 98),
         text(365, 196, "100–200 l", 15, INK, 700),
         text(365, 214, "míšení", 12, MUTED),
         text(250, 100, "okruh TČ", 12, MUTED),
         text(365, 333, "4 hrdla – hydraulický oddělovač", 12, MUTED),
         text(483, 150, "o pár °C", 12, RED, 600), text(483, 165, "chladnější", 12, RED, 600)]
    return svg("Paralelní zapojení – čtyřtrubkové", "Tepelné čerpadlo má stálý průtok, i když termostatické hlavice zavírají", "".join(b), True)


# 4 — paralelně třítrubkově
def s4():
    tx, tw, ty, th = 325, 80, 160, 110
    cx = tx + tw / 2
    yp = ty + th - 22          # spodní hrdla nádoby
    b = [heat_pump(), system_box("rad"),
         pipe([(180, Y_SUP), (555, Y_SUP)], RED),
         pipe([(555, Y_RET), (440, Y_RET), (440, yp), (tx + tw, yp)], BLUE),
         pipe([(tx, yp), (290, yp), (290, Y_RET), (180, Y_RET)], BLUE),
         pipe([(cx, Y_SUP), (cx, ty)], RED, 5),
         f'<circle cx="{cx}" cy="{Y_SUP}" r="5" fill="{RED}"/>',
         tank(tx, ty, tw, th, "g4", RED, BLUE, "", "", ly=0),
         arrow(250, Y_SUP, "r", RED), arrow(240, Y_RET, "l", BLUE), arrow(510, Y_RET, "l", BLUE),
         arrow(cx, 142, "d", RED),
         pump(480, Y_SUP, "r", "čerpadlo soustavy", 98),
         text(cx, ty + 45, "přebytek", 12, INK, 600),
         text(285, 100, "voda jde přímo do domu", 12, BRAND, 600),
         text(365, 333, "3 hrdla – nádoba bere jen nevyužitý průtok", 12, MUTED)]
    return svg("Paralelní zapojení – třítrubkové", "Bez ztráty teploty; nádoba přebírá jen průtok, který dům právě neodebere", "".join(b), True)


if __name__ == "__main__":
    for name, fn in [("zapojeni-1-bez-nadoby", s1), ("zapojeni-2-seriove-zpatecka", s2),
                     ("zapojeni-3-paralelni-4trubkove", s3), ("zapojeni-4-paralelni-3trubkove", s4)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("✓", name)
