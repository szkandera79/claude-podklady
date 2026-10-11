#!/usr/bin/env python3
"""Generátor výkresů TV-BDM-04 (hydraulika 3× TČ) a TV-BDM-05 (režimy TČ2/TČ3).
Spuštění z kořene projektu BD Michal:  python3 src/gen_3tc.py
Výstup: 04-hydraulika-3TC.svg, 05-rezimy-TC2-TC3.svg (přepíše je)."""
from html import escape as esc
import os

W, H = 1680, 1188
C = dict(sup='#D62828', ret='#1D4E89', t3s='#7B2CBF', t3r='#9D7BD8', tuv='#E8730C',
         tuvl='#F4A261', cw='#3AA0F2', off='#B8C2BC', ink='#16201C', mut='#5F6B64',
         green='#0F3D2E', gb='#1E8F5B', amber='#DA8718')

STYLE = """
  <style>
    .pipe{fill:none;stroke-linecap:round;stroke-linejoin:round}
    .sym{fill:#fff;stroke:#16201C;stroke-width:2}
    .symk{fill:#16201C}
    .t{fill:#16201C;font-size:12px}
    .ts{fill:#16201C;font-size:11px}
    .tx{fill:#5F6B64;font-size:10.5px}
    .tb{fill:#16201C;font-size:14px;font-weight:bold}
    .tbs{fill:#16201C;font-size:12px;font-weight:bold}
    .wt{fill:#fff;font-size:12px;font-weight:bold}
    .eb{fill:#1E8F5B;font-size:12px;font-weight:bold;letter-spacing:2px}
    .zt{fill:#0F3D2E;font-size:12px;font-weight:bold;letter-spacing:1.2px}
    .id{fill:#0F3D2E;font-size:11px;font-weight:bold}
  </style>"""

DEFS = """
  <defs>
    <g id="v"><path class="sym" d="M-10,-7 L0,0 L-10,7 Z"/><path class="sym" d="M10,-7 L0,0 L10,7 Z"/></g>
    <g id="chk"><path class="sym" d="M-10,-7 L9,0 L-10,7 Z"/><line x1="10" y1="-8" x2="10" y2="8" stroke="#16201C" stroke-width="2.2"/></g>
    <g id="pump"><circle class="sym" r="13"/><path class="symk" d="M-5,-6.5 L7,0 L-5,6.5 Z"/></g>
    <g id="flt"><rect class="sym" x="-12" y="-10" width="24" height="20"/><line x1="-12" y1="-10" x2="12" y2="10" stroke="#16201C" stroke-width="1.5"/><line x1="-12" y1="10" x2="12" y2="-10" stroke="#16201C" stroke-width="1.5"/></g>
    <g id="exp"><rect class="sym" x="-13" y="-22" width="26" height="40" rx="12"/><line x1="-13" y1="-2" x2="13" y2="-2" stroke="#16201C" stroke-width="1.5"/></g>
    <g id="sv"><path class="sym" d="M-9,-6 L0,0 L-9,6 Z"/><path fill="none" stroke="#16201C" stroke-width="2" d="M0,0 L0,-9 L8,-9"/><path fill="none" stroke="#5F6B64" stroke-width="1.3" d="M-3,-13 l6,3 l-6,3 l6,3"/></g>
    <g id="ts"><circle class="sym" r="9"/><text x="0" y="4" text-anchor="middle" style="font-size:10px;fill:#16201C;font-weight:bold">T</text></g>
    <g id="fm"><circle class="sym" r="11"/><text x="0" y="4" text-anchor="middle" style="font-size:10px;fill:#16201C;font-weight:bold">Q</text></g>
    <g id="flex"><rect x="-11" y="-7" width="22" height="14" fill="#fff"/><path fill="none" stroke="#16201C" stroke-width="1.8" d="M-11,0 l3,-6 l4,12 l4,-12 l4,12 l4,-12 l3,6"/></g>
    <marker id="ar" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#16201C"/></marker>
  </defs>"""


class Sheet:
    def __init__(self):
        self.L = {k: [] for k in ('bg', 'bar', 'pipe', 'sym', 'txt')}

    # ---------- primitiva ----------
    def raw(self, s, layer='sym'): self.L[layer].append(s)

    def text(self, x, y, s, cls='t', anchor='start', extra=''):
        a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
        self.L['txt'].append(f'<text x="{x}" y="{y}" class="{cls}"{a} {extra}>{esc(s)}</text>')

    def lines(self, x, y, rows, cls='t', dy=15, anchor='start'):
        for i, r in enumerate(rows):
            if r: self.text(x, y + i * dy, r, cls, anchor)

    def pipe(self, pts, color, w=5, dash=None):
        d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.L['pipe'].append(f'<path class="pipe" d="{d}" stroke="{color}" stroke-width="{w}"{da}/>')

    def halo(self, x1, y1, x2, y2, w=13):
        """Bílá mezera — potrubí se kříží bez propojení."""
        self.L['pipe'].append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#fff" stroke-width="{w}"/>')

    def dot(self, x, y, color, r=5):
        self.L['sym'].append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="#fff" stroke-width="1.2"/>')

    def use(self, sid, x, y, rot=0):
        r = f' rotate({rot})' if rot else ''
        self.L['sym'].append(f'<use href="#{sid}" transform="translate({x} {y}){r}"/>')

    def arrow(self, x, y, d, color, s=7):
        pts = {'r': [(x - s, y - s), (x + s, y), (x - s, y + s)], 'l': [(x + s, y - s), (x - s, y), (x + s, y + s)],
               'd': [(x - s, y - s), (x, y + s), (x + s, y - s)], 'u': [(x - s, y + s), (x, y - s), (x + s, y + s)]}[d]
        p = ' '.join(f'{a},{b}' for a, b in pts)
        self.L['sym'].append(f'<polygon points="{p}" fill="{color}" stroke="#fff" stroke-width="1"/>')

    def v3(self, x, y, ports, closed=(), motor='r', labels=None, tag=None, tagpos=(0, 0)):
        vec = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}
        mdx, mdy = vec[motor]
        self.L['sym'].append(f'<line x1="{x}" y1="{y}" x2="{x + mdx * 24}" y2="{y + mdy * 24}" stroke="#16201C" stroke-width="1.6"/>')
        mx, my = x + mdx * 31, y + mdy * 31
        self.L['sym'].append(f'<rect x="{mx - 8}" y="{my - 8}" width="16" height="16" class="sym"/>'
                             f'<text x="{mx}" y="{my + 4}" text-anchor="middle" style="font-size:10px;font-weight:bold;fill:#16201C">M</text>')
        for p in ports:
            dx, dy = vec[p]
            bx, by = x + dx * 14, y + dy * 14
            px, py = -dy * 8, dx * 8
            fill = '#16201C' if p in closed else '#ffffff'
            self.L['sym'].append(f'<polygon points="{x},{y} {bx + px},{by + py} {bx - px},{by - py}" fill="{fill}" stroke="#16201C" stroke-width="1.8"/>')
        for p, s in (labels or {}).items():
            dx, dy = vec[p]
            lx = x + dx * 22 + (9 if dy else 0)
            ly = y + dy * 26 + (-11 if dx else 4)
            self.L['txt'].append(f'<text x="{lx}" y="{ly}" class="tx" text-anchor="{"start" if dy else "middle"}" style="font-weight:bold">{s}</text>')
        if tag:
            self.text(x + tagpos[0], y + tagpos[1], tag, 'id')

    def sensor(self, x, y, side, label, color=None):
        dx = {'l': -24, 'r': 24}[side]
        self.L['sym'].append(f'<line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y}" stroke="#5F6B64" stroke-width="1.3"/>')
        self.use('ts', x + dx, y)
        self.text(x + dx + (12 if side == 'r' else -12), y + 4, label, 'tx', 'start' if side == 'r' else 'end')

    def tank(self, x, y, w, h, rows, fill='#EAF1EC'):
        self.L['bg'].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w / 2 if w < 90 else 40}" fill="{fill}" stroke="#16201C" stroke-width="2.3"/>')
        for i, (s, c) in enumerate(rows):
            self.text(x + w / 2, y + h / 2 - 8 + i * 16, s, c, 'middle')

    def heater(self, x, y, label):
        """Elektrická topná patrona (vodorovná, uvnitř nádoby)."""
        self.L['sym'].append(f'<path fill="none" stroke="{C["amber"]}" stroke-width="2.2" d="M{x},{y} l6,-6 l6,12 l6,-12 l6,12 l6,-12 l6,6"/>')
        self.L['sym'].append(f'<rect x="{x - 14}" y="{y - 8}" width="14" height="16" fill="{C["amber"]}"/>'
                             f'<text x="{x - 7}" y="{y + 4}" text-anchor="middle" style="font-size:10px;font-weight:bold;fill:#fff">E</text>')
        self.text(x + 10, y + 20, label, 'tx')

    def hx(self, x, y, w, h):
        self.L['bg'].append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#16201C" stroke-width="2.2"/>')
        n = 6
        for i in range(1, n):
            yy = y + i * h / n
            self.L['sym'].append(f'<line x1="{x + 4}" y1="{yy}" x2="{x + w - 4}" y2="{yy}" stroke="#5F6B64" stroke-width="1.2"/>')
        self.L['sym'].append(f'<path fill="none" stroke="#16201C" stroke-width="1.6" d="M{x},{y} L{x + w},{y + h} M{x + w},{y} L{x},{y + h}" stroke-opacity="0.35"/>')

    def zone(self, x, y, w, h, title, fill='#FBFDFC', tx=None, ty=None):
        self.L['bg'].insert(0, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#DCE6DF" stroke-width="1.5"/>')
        self.text(tx if tx is not None else x + 14, ty if ty is not None else y + 20, title, 'zt')

    def svg(self):
        body = '\n  '.join(self.L['bg'] + self.L['bar'] + self.L['pipe'] + self.L['sym'] + self.L['txt'])
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">'
                f'{STYLE}{DEFS}\n  <rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>\n'
                f'  <rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none" stroke="#16201C" stroke-width="2"/>\n  {body}\n</svg>\n')


def header(s, title, sub1, sub2):
    s.text(40, 48, 'THERMAVERA ENERGY — PŘEDBĚŽNÝ NÁVRH', 'eb')
    s.text(40, 78, title, 'tb', extra='style="font-size:24px"')
    s.text(40, 100, sub1, 't')
    s.text(40, 117, sub2, 'tx')


def title_block(s, x, y, w, h, rows):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#16201C" stroke-width="1.6"/>', 'bg')
    for i, (txt, cls) in enumerate(rows):
        s.text(x + 14, y + 22 + i * 17, txt, cls)


def warning(s, x, y, w, h, title, rows):
    s.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#FFF6E9" stroke="{C["amber"]}" stroke-width="2.2"/>', 'bg')
    s.raw(f'<polygon points="{x + 30},{y + 12} {x + 48},{y + 42} {x + 12},{y + 42}" fill="{C["amber"]}"/>'
          f'<text x="{x + 30}" y="{y + 38}" text-anchor="middle" style="font-size:18px;font-weight:bold;fill:#fff">!</text>', 'sym')
    s.text(x + 62, y + 26, title, 'tbs', extra=f'style="fill:{C["amber"]};font-size:13px"')
    s.lines(x + 62, y + 44, rows, 'ts', 15)


# =====================================================================================
#  TV-BDM-04 — hydraulické schéma 3× TČ
# =====================================================================================
def sheet04():
    s = Sheet()
    header(s, 'Hydraulické schéma zdroje tepla — 3× TČ vzduch/voda, kaskáda — kotelna BD Michal',
           'TČ1 MASTER pouze vytápění · TČ2 SLAVE vytápění + TUV · TČ3 záloha do ÚT nebo TUV (porucha / nedostatek výkonu) · sběrač DN150 · akumulace 2× 1 000 l · TUV 3× 1 000 l',
           'Oddělené okruhy: ① primár TČ (tři paralelní větve) · ② topná akumulace · ③ okruh vytápění · ④ nabíjení TUV přes deskový výměník. Poloha ventilů: TČ2 v ÚT, TČ3 v klidu (výchozí poloha ÚT).')

    s.zone(30, 135, 1120, 525, '① PRIMÁRNÍ OKRUH TČ — TŘI PARALELNÍ VĚTVE, TČ2 A TČ3 PŘEPÍNATELNÉ ÚT / TUV', ty=153)
    s.raw('<rect x="40" y="162" width="1100" height="112" rx="6" fill="#EEF3F9"/>', 'bg')
    s.text(330, 196, 'VENKOVNÍ PROSTOR', 'tx'); s.text(330, 210, 'monobloky na terase / terénu', 'tx')
    s.raw('<line x1="40" y1="285" x2="1140" y2="285" stroke="#16201C" stroke-width="2.5" stroke-dasharray="14 6"/>', 'bg')
    s.text(330, 302, 'obvodová stěna — prostup do kotelny', 'tx')
    s.text(330, 316, '(izolace, protizámrazová ochrana vnější trasy)', 'tx')
    s.zone(30, 670, 530, 375, '② TOPNÁ AKUMULACE', tx=170, ty=690)
    s.zone(570, 670, 390, 375, '③ OKRUH VYTÁPĚNÍ', tx=590, ty=1035)
    s.zone(970, 670, 680, 375, '④ NABÍJENÍ TUV (TČ2 / TČ3)', tx=1110, ty=690)

    for x, t1, t2 in [(135, 'TČ1 · MASTER', 'pouze vytápění'), (560, 'TČ2 · SLAVE', 'vytápění + TUV'),
                      (900, 'TČ3 · ZÁLOHA', 'ÚT nebo TUV při potřebě')]:
        s.raw(f'<rect x="{x}" y="175" width="170" height="80" rx="8" fill="#F4F8F5" stroke="#16201C" stroke-width="2.2"/>', 'bg')
        s.raw(f'<circle cx="{x + 142}" cy="203" r="16" fill="none" stroke="#5F6B64" stroke-width="1.5"/>'
              f'<path d="M{x + 142},188 L{x + 142},218 M{x + 127},203 L{x + 157},203" stroke="#5F6B64" stroke-width="1.2"/>', 'sym')
        s.text(x + 12, 198, t1, 'tbs'); s.text(x + 12, 216, 'vzduch/voda 50 kW', 'ts'); s.text(x + 12, 233, t2, 'tx')

    def branch(n, S, R, cs, cr, out):
        sx = -1 if out == 'l' else 1
        s.use('flex', S, 298, 90); s.use('v', S, 338, 90)
        s.raw(f'<line x1="{S}" y1="314" x2="{S + sx * 20}" y2="314" stroke="#16201C" stroke-width="1.6"/>')
        s.use('sv', S + sx * 28, 314, 0 if sx < 0 else 180)
        s.text(S + sx * 42, 308, 'PV', 'tx', 'end' if sx < 0 else 'start')
        s.sensor(S, 368, out, f'TS2{n}')
        s.use('chk', S, 400, 90); s.text(S + 14, 404, 'ZK', 'tx'); s.use('v', S, 440, 90)
        s.use('flex', R, 298, 90); s.use('v', R, 326, 90); s.use('fm', R, 352)
        s.use('pump', R, 384, -90); s.use('flt', R, 418, 90); s.use('v', R, 448, 90)
        rx = -sx
        s.text(R + rx * 18, 388, f'P{n}', 'id', 'start' if rx > 0 else 'end')
        s.lines(R + rx * 34, 372, [f'větev TČ{n}', '50 kW · 8,7 m³/h', 'DN50 · v ≈ 1,0 m/s'], 'ts', 14, 'start' if rx > 0 else 'end')
        s.arrow(R, 272, 'u', cr, 6); s.arrow(S, 272, 'd', cs, 6)

    # sběrač / rozdělovač
    s.raw(f'<rect x="100" y="520" width="420" height="16" fill="{C["sup"]}" stroke="#7A1010" stroke-width="1.2"/>', 'bar')
    s.raw(f'<rect x="90" y="556" width="430" height="16" fill="{C["ret"]}" stroke="#0E2A4D" stroke-width="1.2"/>', 'bar')
    s.text(292, 532, 'SBĚRAČ PŘÍVODU · DN150', 'wt', extra='style="font-size:10.5px"')
    s.text(292, 568, 'ROZDĚLOVAČ ZPÁTEČKY · DN150', 'wt', extra='style="font-size:10.5px"')
    s.arrow(485, 528, 'l', '#fff', 5); s.arrow(500, 564, 'r', '#fff', 5)

    # TČ1 — pouze ÚT
    S1, R1 = 180, 260
    s.pipe([(S1, 255), (S1, 520)], C['sup']); s.dot(S1, 521, C['sup'])
    s.halo(R1, 513, R1, 543); s.pipe([(R1, 556), (R1, 255)], C['ret']); s.dot(R1, 557, C['ret'])
    branch(1, S1, R1, C['sup'], C['ret'], 'l'); s.arrow(S1, 500, 'd', C['sup'], 6)

    # TČ2, TČ3 — přepínatelné (R vlevo, S vpravo)
    R2, S2, R3, S3 = 605, 685, 945, 1025
    s.pipe([(S2, 255), (S2, 514)], C['sup']); s.pipe([(R2, 550), (R2, 255)], C['ret'])
    s.pipe([(S3, 255), (S3, 462)], C['off'], 5); s.pipe([(R3, 490), (R3, 255)], C['off'], 5)
    branch(2, S2, R2, C['sup'], C['ret'], 'r'); branch(3, S3, R3, C['off'], C['off'], 'r')
    for x, y in ((S2, 476), (S2, 504), (R2, 476), (R2, 504), (R2, 528), (R3, 476)):
        s.halo(x, y - 8, x, y + 8)
    s.pipe([(S2 - 14, 528), (520, 528)], C['sup']); s.dot(520, 528, C['sup'])
    s.halo(552, 528, 568, 528)
    s.pipe([(S3 - 14, 476), (545, 476), (545, 528)], C['sup']); s.dot(545, 528, C['sup'])
    s.pipe([(R3 - 14, 504), (560, 504), (560, 564)], C['ret']); s.dot(560, 564, C['ret'])
    s.pipe([(520, 564), (R2 - 14, 564)], C['ret']); s.dot(520, 564, C['ret'])
    s.text(700, 462, 'větve B → sběrač ÚT · DN50', 'ts')
    # potrubí k VT (porty A)
    s.pipe([(R3, 518), (R3, 645)], C['t3r'], 5)
    s.halo(R3, 607, R3, 623)
    s.pipe([(S2, 542), (S2, 615), (1100, 615), (1100, 740), (1140, 740)], C['t3s'], 5.5)
    s.pipe([(S3, 490), (S3, 615)], C['t3s'], 5); s.dot(S3, 615, C['t3s'])
    s.pipe([(1140, 870), (1060, 870), (1060, 645), (R2, 645), (R2, 578)], C['t3r'], 5.5); s.dot(R3, 645, C['t3r'])
    s.text(710, 607, 'porty A → VT · DN80 · 8,7–17,4 m³/h', 'tx')
    s.arrow(840, 615, 'r', C['t3s'], 6); s.arrow(800, 645, 'l', C['t3r'], 6)
    lab = {'l': 'B', 'd': 'A'}
    s.v3(S2, 528, 'uld', closed='d', motor='r', labels=lab, tag='V2.1', tagpos=(44, 4))
    s.v3(R2, 564, 'uld', closed='d', motor='r', labels=lab, tag='V2.2', tagpos=(44, 4))
    s.v3(S3, 476, 'uld', closed='d', motor='r', labels=lab, tag='V3.1', tagpos=(44, 4))
    s.v3(R3, 504, 'uld', closed='d', motor='r', labels=lab, tag='V3.2', tagpos=(44, 4))

    # EN1 primár
    s.pipe([(400, 572), (400, 596)], C['ret'], 3); s.use('exp', 400, 620); s.use('sv', 422, 590)
    s.text(418, 646, 'EN1 + PV1 primár', 'tx')

    # ---- ② akumulace ----
    s.halo(130, 549, 130, 579)
    s.pipe([(130, 536), (130, 730)], C['sup'], 7); s.dot(130, 537, C['sup'])
    s.use('v', 130, 600, 90); s.sensor(130, 640, 'l', 'TS10')
    s.lines(146, 616, ['přívod do AKU · DN100', '17,4 m³/h (2 TČ v ÚT)', '26,0 m³/h (3 TČ v ÚT)'], 'ts', 14)
    s.tank(110, 730, 110, 260, [('AKU1', 'tbs'), ('1 000 l', 'ts'), ('primár', 'tx')])
    s.tank(330, 730, 110, 260, [('AKU2', 'tbs'), ('1 000 l', 'ts'), ('vytápění', 'tx')])
    s.pipe([(220, 755), (330, 755)], C['sup'], 7); s.pipe([(330, 962), (220, 962)], C['ret'], 7)
    s.text(275, 747, 'DN100', 'tx', 'middle'); s.text(275, 981, 'DN100', 'tx', 'middle')
    s.arrow(275, 755, 'r', C['sup'], 6); s.arrow(275, 962, 'l', C['ret'], 6)
    s.pipe([(110, 962), (60, 962), (60, 564), (90, 564)], C['ret'], 7); s.dot(90, 564, C['ret'])
    s.use('v', 60, 910, 90); s.use('fm', 60, 810); s.text(76, 814, 'M1', 'id')
    s.sensor(60, 760, 'r', ''); s.text(84, 746, 'TS11', 'tx', 'middle'); s.arrow(60, 690, 'u', C['ret'], 6)
    s.heater(150, 800, 'E1'); s.heater(370, 800, 'E2')
    s.use('ts', 425, 752); s.text(425, 777, 'TS1', 'tx', 'middle')
    s.use('ts', 205, 880); s.text(205, 905, 'TS2', 'tx', 'middle')
    s.use('ts', 205, 940); s.text(160, 944, 'TS3', 'tx', 'end')
    s.lines(40, 1012, ['Nádoby propojeny horem i spodem DN100 → pracují jako jedna akumulace',
                       'a hydraulicky oddělují primár od vytápění. Hrdla s rozrážeči proudu.'], 'tx', 13)

    # ---- ③ okruh vytápění ----
    s.pipe([(420, 730), (420, 712), (880, 712)], C['sup'], 5.5)
    s.pipe([(880, 950), (440, 950)], C['ret'], 5.5)
    s.pipe([(680, 950), (680, 726)], C['ret'], 3.5); s.dot(680, 950, C['ret'])
    s.use('v', 600, 712)
    s.v3(680, 712, 'ldr', motor='u', labels={'l': 'A', 'd': 'B', 'r': 'AB'}, tag='V1', tagpos=(14, -30))
    s.use('pump', 752, 712); s.text(752, 737, 'P4 (zdvojené)', 'tx', 'middle')
    s.sensor(812, 712, 'r', ''); s.text(830, 699, 'TS4', 'tx'); s.use('v', 858, 712)
    s.use('v', 858, 950); s.use('fm', 800, 950); s.text(800, 972, 'M3', 'id', 'middle')
    s.use('flt', 740, 950); s.use('v', 600, 950)
    s.arrow(630, 712, 'r', C['sup'], 6); s.arrow(640, 950, 'l', C['ret'], 6)
    s.pipe([(520, 950), (520, 974)], C['ret'], 3); s.use('exp', 520, 998); s.use('sv', 542, 968)
    s.text(470, 1004, 'EN2 + PV2', 'tx', 'end')
    s.raw('<rect x="880" y="695" width="72" height="275" rx="6" fill="#F4F8F5" stroke="#16201C" stroke-width="2"/>', 'bg')
    s.lines(916, 770, ['ÚT', 'BYTY', '', 'bloky', 'A · B · C', '', '9× rozd.', 'podlah.', 'topení', '35/30 °C'], 'ts', 16, 'middle')
    s.lines(700, 775, ['okruh ÚT · DN65', '9,2 m³/h (ztráta 53 kW)', 'ΔT 5 K · max. 35 °C', '', 'V1 omezuje přívod', 'do podlahovky'], 'ts', 15)

    # ---- ④ TUV ----
    s.pipe([(1100, 870), (1100, 892)], C['t3r'], 3); s.use('exp', 1100, 916); s.use('sv', 1122, 886)
    s.text(1085, 956, 'EN3 + PV3', 'tx', 'end')
    s.lines(985, 770, ['okruh', 'TČ2/TČ3', '→ VT', 'DN80'], 'tx', 13)
    s.arrow(1100, 700, 'd', C['t3s'], 6); s.arrow(1060, 780, 'u', C['t3r'], 6)
    s.hx(1140, 730, 50, 160)
    s.lines(1165, 912, ['VT — deskový', 'výměník TUV', '(nerez, ~100 kW)'], 'tx', 13, 'middle')
    s.pipe([(1190, 740), (1215, 740), (1215, 720), (1550, 720), (1550, 770)], C['tuv'], 4.5)
    s.pipe([(1250, 970), (1222, 970), (1222, 870), (1190, 870)], C['tuvl'], 4.5)
    s.use('pump', 1222, 920, -90); s.text(1210, 956, 'P5', 'id', 'end')
    s.arrow(1380, 720, 'r', C['tuv'], 6)
    s.text(1240, 712, 'nabíjení TUV · DN40 · otáčky P5 drží výstup VT 52–55 °C', 'tx')
    for i, x in enumerate((1250, 1380, 1510)):
        s.tank(x, 770, 80, 220, [(f'TUV{i + 1}', 'tbs'), ('1 000 l', 'ts')], fill='#FDF3EA')
        s.heater(x + 24, 915, f'E{i + 3}')
    s.pipe([(1330, 790), (1355, 790), (1355, 970), (1380, 970)], C['tuvl'], 4)
    s.pipe([(1460, 790), (1485, 790), (1485, 970), (1510, 970)], C['tuvl'], 4)
    s.pipe([(1590, 790), (1620, 790), (1620, 700)], C['tuv'], 4.5)
    s.v3(1620, 748, 'udl', motor='r', labels={'l': 'SV'}, tag='TSV', tagpos=(12, 30))
    s.text(1606, 704, 'TUV → byty', 'tbs', 'end')
    s.pipe([(1648, 880), (1590, 880)], C['tuv'], 3, dash='7 4')
    s.use('pump', 1622, 880, 180); s.use('chk', 1600, 880, 180); s.text(1646, 906, 'cirkulace', 'tx', 'end')
    s.use('ts', 1566, 805); s.text(1566, 829, 'TS7', 'tx', 'middle')
    s.use('ts', 1290, 970); s.text(1290, 955, 'TS8', 'tx', 'middle')
    s.pipe([(1000, 1025), (1290, 1025), (1290, 990)], C['cw'], 4.5)
    s.use('v', 1030, 1025); s.use('chk', 1070, 1025)
    s.pipe([(1150, 1025), (1150, 1004)], C['cw'], 3); s.use('exp', 1150, 982); s.use('sv', 1172, 1010)
    s.text(1000, 1015, 'SV', 'tbs'); s.text(1180, 990, 'EN TUV (pitná) + PV', 'tx')
    s.text(1340, 1022, 'série: SV → TUV1 → TUV2 → TUV3 → výstup', 'tx')

    # ---- pravý sloupec ----
    x0 = 1165
    s.raw(f'<rect x="{x0}" y="135" width="485" height="300" rx="8" fill="#fff" stroke="#16201C" stroke-width="1.6"/>', 'bg')
    s.text(x0 + 14, 158, 'PRŮTOKY A PŘEDBĚŽNÉ DIMENZE', 'tbs')
    s.text(x0 + 14, 175, 'voda ~40 °C · ΔT = 5 K · ocel · cílová rychlost 0,8–1,0 m/s', 'tx')
    s.text(x0 + 14, 193, 'Q [m³/h] = P [kW] / (1,152 · ΔT [K])', 'ts', extra='style="font-weight:bold"')
    cols = [x0 + 14, x0 + 196, x0 + 252, x0 + 350, x0 + 404, x0 + 448]
    s.raw(f'<rect x="{x0 + 8}" y="202" width="470" height="20" fill="{C["green"]}"/>', 'bg')
    for cx, h in zip(cols, ['Úsek', 'Výkon', 'Průtok', 'DN', 'v m/s', 'Pa/m']):
        s.text(cx, 216, h, 'wt', extra='style="font-size:11px"')
    rows = [('Větev TČ1 / TČ2 / TČ3', '50 kW', '8,7 m³/h', 'DN50', '1,03', '≈215'),
            ('Přívod AKU: 2 TČ v ÚT', '100 kW', '17,4 m³/h', '(DN80)', '0,90', '≈100'),
            ('Přívod AKU: 3 TČ v ÚT', '150 kW', '26,0 m³/h', 'DN100', '0,80', '≈60'),
            ('Sběrač / rozdělovač', '150 kW', '26,0 m³/h', 'DN150', '0,36', '—'),
            ('Propojení AKU1–AKU2', '≤150 kW', '≤26,0 m³/h', 'DN100', '≤0,80', '—'),
            ('Okruh vytápění', '53 kW', '9,2 m³/h', 'DN65', '0,66', '≈65'),
            ('Potrubí k VT: TČ2 + TČ3', '100 kW', '17,4 m³/h', 'DN80', '0,90', '≈100')]
    for i, r in enumerate(rows):
        yy = 238 + i * 21
        if i % 2 == 0:
            s.raw(f'<rect x="{x0 + 8}" y="{yy - 14}" width="470" height="21" fill="#F4F8F5"/>', 'bg')
        for cx, v in zip(cols, r):
            s.text(cx, yy, v, 'ts', extra='style="font-weight:bold"' if v.startswith('DN') else '')
    s.lines(x0 + 14, 392, ['Přívod do AKU na 150 kW (DN100): topit mohou všechna tři TČ.',
                           'VT a potrubí k němu na 100 kW: TUV mohou nabíjet TČ2 i TČ3 současně.',
                           'S 30 % glykolem: průtok +6 %, tlaková ztráta +35–40 % → obvykle o 1 DN výš.'], 'tx', 14)
    ly = 448
    s.raw(f'<rect x="{x0}" y="{ly}" width="485" height="142" rx="8" fill="#fff" stroke="#DCE6DF" stroke-width="1.5"/>', 'bg')
    s.text(x0 + 14, ly + 20, 'LEGENDA', 'tbs')
    leg = [(C['sup'], 'topná voda — přívod'), (C['ret'], 'topná voda — zpátečka'),
           (C['t3s'], 'okruh TČ2/TČ3 → VT — přívod'), (C['t3r'], 'okruh TČ2/TČ3 → VT — zpátečka'),
           (C['tuv'], 'TUV (teplá)'), (C['tuvl'], 'TUV nabíjení / mezi zásobníky'), (C['cw'], 'studená voda')]
    for i, (col, lab) in enumerate(leg):
        yy = ly + 40 + i * 14
        s.raw(f'<line x1="{x0 + 14}" y1="{yy - 4}" x2="{x0 + 44}" y2="{yy - 4}" stroke="{col}" stroke-width="4"/>', 'sym')
        s.text(x0 + 52, yy, lab, 'tx')
    for i, (sid, lab) in enumerate([('v', 'uzávěr (kulový kohout)'), ('chk', 'zpětná klapka ZK'), ('pump', 'oběhové čerpadlo'),
                                    ('flt', 'filtr + magnetický odkalovač'), ('fm', 'průtokoměr / kalorimetr'), ('flex', 'antivibrační hadice')]):
        yy = ly + 38 + i * 16
        s.raw(f'<use href="#{sid}" transform="translate({x0 + 256} {yy - 4}) scale(0.75)"/>', 'sym')
        s.text(x0 + 274, yy, lab, 'tx')
    s.text(x0 + 240, ly + 138, '3cestný ventil: bílý port = otevřeno, černý = zavřeno', 'tx')
    s.raw(f'<rect x="{x0}" y="600" width="485" height="60" rx="8" fill="#F4F8F5" stroke="#DCE6DF" stroke-width="1.5"/>', 'bg')
    s.lines(x0 + 14, 620, ['Porty přepínacích ventilů: B = sběrač ÚT, A = výměník VT (TUV).',
                           'V2.1+V2.2 a V3.1+V3.2 se přestavují vždy v páru. Průběh režimů: TV-BDM-05.',
                           'Šedě: TČ3 v klidu (záloha), P3 stojí.'], 'tx', 14)

    warning(s, 30, 1055, 1110, 110, 'PŘEDBĚŽNÝ NÁVRH — DIMENZE DN JSOU ORIENTAČNÍ, NUTNÝ VÝPOČET TLAKOVÝCH ZTRÁT',
            ['DN stanoveny jen z průtoku při ΔT 5 K a doporučené rychlosti. Před objednáním: výpočet tlakových ztrát celé trasy (vnější rozvod k monoblokům,',
             'výměníky TČ dle výrobce, deskový výměník VT, armatury, filtry, kalorimetry), návrh čerpadel P1–P5, objemů EN a pojistných ventilů, ověření',
             'minimálního průtoku TČ. Náplň primáru (voda × glykol) rozhodne o výměníku mezi sběračem a akumulací. Autorizovaný projektant TZB.',
             'Symboly T = čidlo teploty, PV = pojistný ventil (u monobloku často vestavěný), E = elektrická topná patrona, EN = expanzní nádoba.'])
    title_block(s, 1150, 1055, 500, 110, [('Stavba: BD Michal — kotelna (Ostrava-Michálkovice)', 'tbs'),
                                          ('Zpracoval: ThermaVera Energy', 'ts'),
                                          ('Výkres: TV-BDM-04 · Stupeň: předběžný návrh · Rev.: 1', 'ts'),
                                          ('Rev. 1: TČ1 jen ÚT, TČ2 ÚT + TUV, TČ3 záloha ÚT / TUV', 'ts'),
                                          ('Režimy TČ2 / TČ3 a poloha ventilů: TV-BDM-05', 'tx')])
    return s.svg()


# =====================================================================================
#  TV-BDM-05 — dva režimy TČ3
# =====================================================================================
def scen_panel(s, ox, oy, key, title, sub, bar, units, act, valves, note):
    """units: dict n -> 'ut' | 'tuv' | 'off' | 'fault'; act: set of active segments."""
    W_, H_ = 805, 330
    s.raw(f'<rect x="{ox}" y="{oy}" width="{W_}" height="{H_}" rx="8" fill="#FBFDFC" stroke="#DCE6DF" stroke-width="1.5"/>', 'bg')
    s.raw(f'<rect x="{ox}" y="{oy}" width="{W_}" height="32" rx="8" fill="{bar}"/><rect x="{ox}" y="{oy + 20}" width="{W_}" height="12" fill="{bar}"/>', 'bg')
    s.text(ox + 16, oy + 22, f'{key} · {title}', 'wt', extra='style="font-size:14px;letter-spacing:0.8px"')
    s.text(ox + W_ - 16, oy + 22, sub, 'wt', 'end', extra='style="font-size:11px;font-weight:normal"')
    x1, x2, x3 = ox + 245, ox + 415, ox + 585
    yv, yu, yt = oy + 150, oy + 230, oy + 280
    UT, TV = C['sup'], C['t3s']

    def seg(pts, on, col):
        if on: s.pipe(pts, col, 6)
        else: s.pipe(pts, C['off'], 3, dash='7 5')

    # bloky
    s.raw(f'<rect x="{ox + 20}" y="{oy + 175}" width="140" height="125" rx="8" fill="#fff" stroke="#16201C" stroke-width="2"/>', 'bg')
    s.lines(ox + 90, oy + 222, ['', 'sběrač → AKU', '2× 1 000 l'], 'ts', 16, 'middle')
    s.text(ox + 90, oy + 222, 'PRIMÁR ÚT', 'tbs', 'middle')
    s.raw(f'<rect x="{ox + 670}" y="{oy + 225}" width="115" height="85" rx="8" fill="#FDF3EA" stroke="#16201C" stroke-width="2"/>', 'bg')
    s.lines(ox + 727, oy + 262, ['', '3× 1 000 l'], 'ts', 16, 'middle')
    s.text(ox + 727, oy + 262, 'VT → TUV', 'tbs', 'middle')

    # sběrná potrubí (dílčí úseky)
    seg([(ox + 160, yu), (x1, yu)], 'c1' in act, UT)
    seg([(x1, yu), (x2 - 40, yu)], 'c2' in act, UT)
    seg([(x2 - 40, yu), (x3 - 40, yu)], 'c3' in act, UT)
    seg([(x2, yt), (x3, yt)], 't2' in act, TV)
    seg([(x3, yt), (ox + 670, yt)], 't3' in act, TV)
    # jednotky
    seg([(x1, oy + 85), (x1, yu)], units[1] == 'ut', UT)
    for n, x in ((2, x2), (3, x3)):
        st = units[n]
        col = UT if st == 'ut' else TV
        seg([(x, oy + 85), (x, yv - 14)], st in ('ut', 'tuv'), col)
        seg([(x - 14, yv), (x - 40, yv), (x - 40, yu)], st == 'ut', UT)
        if n == 2:
            s.halo(x - 9, yu, x + 9, yu, 13)
        seg([(x, yv + 14), (x, yt)], st == 'tuv', TV)
    for x, y in ((x1, yu), (x2 - 40, yu), (x3, yt)):
        s.dot(x, y, '#16201C', 3.5)
    for n, x in ((1, x1), (2, x2), (3, x3)):
        st = units[n]
        fill = {'ut': '#F4F8F5', 'tuv': '#F4F8F5', 'off': '#EEF0EF', 'fault': '#FDECEC'}[st]
        stroke = C['sup'] if st == 'fault' else '#16201C'
        s.raw(f'<rect x="{x - 55}" y="{oy + 45}" width="110" height="40" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="2"/>', 'bg')
        s.text(x, oy + 62, f'TČ{n}', 'tbs', 'middle')
        lab = {'ut': '→ vytápění', 'tuv': '→ TUV', 'off': 'záloha — stojí', 'fault': 'PORUCHA'}[st]
        s.text(x, oy + 78, lab, 'tx', 'middle', extra=f'style="fill:{C["sup"]};font-weight:bold"' if st == 'fault' else '')
        if st in ('ut', 'tuv'):
            s.arrow(x, oy + 115, 'd', UT if st == 'ut' else TV, 7)
    if 'c1' in act: s.arrow(ox + 200, yu, 'l', UT, 7)
    if 't3' in act: s.arrow(ox + 640, yt, 'r', TV, 7)
    for n, x in ((2, x2), (3, x3)):
        s.v3(x, yv, 'uld', closed=valves[n], motor='r', labels={'l': 'B', 'd': 'A'}, tag=f'V{n}', tagpos=(44, 4))
    s.lines(ox + 190, oy + 312, note, 'tx', 13)


def sheet05():
    s = Sheet()
    header(s, 'Režimy přepínatelných jednotek TČ2 a TČ3 — kotelna BD Michal',
           'TČ1 MASTER pouze vytápění · TČ2 SLAVE vytápění + TUV · TČ3 záloha: připojí se k ÚT nebo k TUV jen při poruše nebo nedostatku výkonu · navazuje na TV-BDM-04',
           'Zjednodušeně jednočarově (přívod + zpátečka = jedna čára) · silná červená = tok do vytápění · silná fialová = tok k VT/TUV · šedá čárkovaná = bez průtoku · port ventilu: bílý = otevřeno, černý = zavřeno')
    G = '#1E8F5B'
    scen_panel(s, 30, 135, 'A', 'NORMÁLNÍ PROVOZ — VYTÁPĚNÍ', 'TČ1 + TČ2 → ÚT · TČ3 v záloze', G,
               {1: 'ut', 2: 'ut', 3: 'off'}, {'c1', 'c2'}, {2: 'd', 3: 'd'},
               ['V2: B otevřeno (ÚT) · V3: klidová poloha B · P3 a P5 stojí'])
    scen_panel(s, 845, 135, 'B', 'NORMÁLNÍ PROVOZ — TČ2 NABÍJÍ TUV', 'TČ1 → ÚT · TČ2 → TUV · TČ3 v záloze', C['t3s'],
               {1: 'ut', 2: 'tuv', 3: 'off'}, {'c1', 't2', 't3'}, {2: 'l', 3: 'd'},
               ['V2: A otevřeno (TUV) · V3: klidová poloha B · P5 běží · TČ1 topí sám'])
    scen_panel(s, 30, 475, 'C', 'ZÁLOHA ÚT — TČ3 DO VYTÁPĚNÍ', 'nedostatek výkonu ÚT nebo porucha TČ1/TČ2', C['sup'],
               {1: 'ut', 2: 'ut', 3: 'ut'}, {'c1', 'c2', 'c3'}, {2: 'd', 3: 'd'},
               ['V2 a V3: B otevřeno (ÚT) · 3 TČ = 26,0 m³/h do sběrače · patrony AKU až po TČ3'])
    scen_panel(s, 845, 475, 'D', 'ZÁLOHA TUV — TČ3 DO TUV', 'porucha TČ2 nebo nedostatek výkonu TUV', C['amber'],
               {1: 'ut', 2: 'fault', 3: 'tuv'}, {'c1', 't3'}, {2: 'd', 3: 'l'},
               ['V3: A otevřeno (TUV) · V2: klidová poloha B, TČ2 blokováno · P5 běží'])

    # matice režimů
    s.raw('<rect x="30" y="815" width="805" height="235" rx="8" fill="#fff" stroke="#16201C" stroke-width="1.6"/>', 'bg')
    s.text(46, 837, 'MATICE REŽIMŮ A PODMÍNEK', 'tbs')
    cx = [46, 76, 146, 226, 316]
    s.raw(f'<rect x="38" y="846" width="789" height="20" fill="{C["green"]}"/>', 'bg')
    for x, h in zip(cx, ['', 'TČ1', 'TČ2 · V2', 'TČ3 · V3', 'Spouštěč (vše s potvrzením v čase)']):
        s.text(x, 860, h, 'wt', extra='style="font-size:11px"')
    rows = [('A', 'ÚT', 'ÚT · B', 'stojí · B', ['výchozí stav, TUV nabitá (TS7 ≥ 45 °C)']),
            ('B', 'ÚT', 'TUV · A', 'stojí · B', ['TS7 < 45 °C → nabíjet do TS8 ≥ 52 °C, max. 60 min', 'mezitím topí TČ1 sám']),
            ('C', 'ÚT', 'ÚT / TUV', 'ÚT · B', ['deficit ÚT: dostupná TČ ≥ 95 % po 15 min a AKU pod žádanou −3 K,',
                                               'nebo porucha TČ1, nebo porucha TČ2 v době topení']),
            ('D', 'ÚT', 'TUV / porucha', 'TUV · A', ['porucha TČ2 při požadavku TUV, nebo nabíjení > 60 min',
                                                     'a TS7 < 42 °C, nebo TČ2 nutně potřeba ve vytápění'])]
    y = 884
    for i, (k, a, b, c, d) in enumerate(rows):
        hgt = 16 * len(d) + 6
        if i % 2 == 0:
            s.raw(f'<rect x="38" y="{y - 14}" width="789" height="{hgt}" fill="#F4F8F5"/>', 'bg')
        for x, v in zip(cx[:4], [k, a, b, c]):
            s.text(x, y, v, 'ts', extra='style="font-weight:bold"' if x == 46 else '')
        s.lines(cx[4], y, d, 'ts', 16)
        y += hgt
    s.lines(46, 1036, ['TČ3 vždy jen k jednomu okruhu. Chybějící výkon po vyčerpání všech TČ kryjí patrony (TV-BDM-03).'], 'tx', 13)

    # logika
    s.raw('<rect x="845" y="815" width="805" height="235" rx="8" fill="#fff" stroke="#16201C" stroke-width="1.6"/>', 'bg')
    s.text(861, 837, 'LOGIKA ŘÍZENÍ — STRUČNĚ', 'tbs')
    s.lines(861, 858, [
        'Priorita požadavků: bezpečnost a protizámraz > TUV pod 40 °C > vytápění > komfort TUV > patrony.',
        'TČ2 přepíná do TUV sám (režim B). TČ3 se připojí jen při poruše nebo potvrzeném deficitu.',
        'Žádá-li TČ3 současně ÚT i TUV: TUV pod 40 °C má přednost, jinak vytápění. Zbytek patrony.',
        'TČ3 zpět do zálohy: požadavek zanikl na 20 min nebo porucha odstraněna. Min. doba v režimu 30 min.',
        'Role jsou pevné. TČ2 nese nejvíc práce — zvážit střídání rolí TČ2/TČ3 po 500 h.',
        'Záloha musí fungovat: TČ3 zkušební běh 1× týdně 30 min, střídavě do ÚT a do TUV.',
        'Sekvence přepnutí (TČ2 i TČ3): 1. stop kompresoru, doběh čerpadla 2 min · 2. oba ventily páru',
        'přestaví současně · 3. kontrola koncových spínačů · 4. změna režimu a žádané teploty přes Modbus ·',
        '5. start po min. době klidu. TČ2 a TČ3 se nikdy nepřepínají současně. Nesoulad spínačů → alarm.',
        'Žádané teploty: ÚT dle ekvitermy AKU 30–45 °C · TUV výstup TČ 55–58 °C, VT drží 52–55 °C.'], 'ts', 18)

    warning(s, 30, 1060, 1110, 105, 'POŽADAVKY NA PŘEPÍNACÍ VENTILY',
            ['V2.1/V2.2 a V3.1/V3.2: těsné 3cestné kulové ventily (L-port) DN50 s pohonem a koncovými spínači, bez polohy „vše zavřeno“.',
             'Klidová poloha B (ÚT): stojící jednotka zůstává napojená na primár s expanzní nádobou EN1. Hlídání průtoku každé přepínatelné',
             'jednotky. Okruh k VT má vlastní EN3 a PV3. Při přepnutí ÚT → TUV roste výstupní teplota o 10–25 K, proto zastavení kompresoru.',
             'Prahy a časy jsou výchozí hodnoty k seřízení při uvádění do provozu.'])
    title_block(s, 1150, 1060, 500, 105, [('Stavba: BD Michal — kotelna (Ostrava-Michálkovice)', 'tbs'),
                                          ('Zpracoval: ThermaVera Energy', 'ts'),
                                          ('Výkres: TV-BDM-05 · Stupeň: předběžný návrh · Rev.: 1', 'ts'),
                                          ('Rev. 1: čtyři režimy, TČ2 ÚT + TUV, TČ3 záloha', 'ts'),
                                          ('Souvisí: TV-BDM-04 hydraulika, TV-BDM-03 řízení', 'tx')])
    return s.svg()


if __name__ == '__main__':
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, fn in (('04-hydraulika-3TC.svg', sheet04), ('05-rezimy-TC2-TC3.svg', sheet05)):
        with open(os.path.join(base, name), 'w', encoding='utf-8') as f:
            f.write(fn())
        print('zapsáno', name)
