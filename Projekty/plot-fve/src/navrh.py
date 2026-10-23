#!/usr/bin/env python3
"""Plot FVE Vendryně — předběžný návrh svislé konstrukce na zemních vrutech.

Spuštění z kořene repozitáře:  python3 plot-fve/src/navrh.py
Výstupy: plot-fve/navrh.html (projektový podklad), plot-fve/dxf/plot-fve.dxf (výkresy 1:1 v mm),
         plot-fve/vystup/statika.json (souhrn výpočtu).
Předběžný návrh — finální dimenze a kotvení musí ověřit autorizovaný statik.
"""
import json, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
np.seterr(all="ignore")      # macOS Accelerate hlásí falešná varování v matmul (rovnováha ověřena)

# ---------------------------------------------------------------- vstupy
SITE = dict(obec="Vendryně (okr. Frýdek-Místek)", lat=49.6689, lon=18.7228, alt=370,
            azimut=150, plot_delka=40.0, plot_vyska=1500, roztec=(2210, 2330), pas=300)
PANEL = dict(L=1762, B=1134, t=30, Wp=450, kg=21.5, Voc=39.5, Vmp=32.8, Isc=14.3,
             tk_voc=-0.25, tk_vmp=-0.29, zad_zkus=2400)  # typický 108 půlčlánků TOPCon
N_PANEL = 19
GAP = 20                     # mezera mezi panely [mm]
Y_TOP = 1500                 # horní hrana panelů = výška plotu
Y_BOT = Y_TOP - PANEL["B"]   # 366
RAIL = 40                    # Al profil 40×40
RAIL_Y = (Y_BOT + 20, Y_TOP - 20)   # osy profilů (podél dlouhých hran rámu)
FIELD = 2270                 # schematická rozteč sloupků plotu (skutečně 2 210–2 330)
X_POST_PLOT = 100            # osa sloupku FV od osy plotu (ven)
POST = dict(b=80, t=3, fy=235, nazev="jekl 80×80×3, S235, žár. Zn")
HEAD = 100                   # hlava vrutu nad terénem
VRUT = dict(d=76, L=1600)
PITCH = PANEL["L"] + GAP
L_WALL = N_PANEL * PANEL["L"] + (N_PANEL - 1) * GAP     # 33 838
DIL = [6 * PITCH - GAP / 2, 13 * PITCH - GAP / 2]       # dilatace profilů v mezeře panelů

# PVGIS 5.2 (SARAH, horizont z DEM), 1 kWp, ztráty 14 %, azimut 150° (aspect −30°)
PVGIS = {90: [37, 46, 64, 75, 67, 65, 72, 77, 69, 63, 42, 34],
         80: [40, 49, 71, 86, 79, 79, 86, 89, 78, 68, 45, 36],
         75: [40, 51, 74, 91, 85, 85, 93, 95, 82, 70, 46, 36],
         60: [41, 53, 80, 103, 100, 102, 109, 108, 90, 74, 47, 36],
         37: [37, 51, 83, 111, 113, 118, 126, 119, 94, 72, 43, 32]}


def post_positions():
    """Sloupky FV: krajní pole 2 ks (0,5 m od sloupku plotu), ostatní pole 1 ks uprostřed."""
    n_fields = math.ceil(L_WALL / FIELD)
    xs = []
    for k in range(n_fields):
        a, b = k * FIELD, (k + 1) * FIELD
        if k in (0, n_fields - 1):
            xs += [a + 500, min(b - 500, L_WALL - 250)]
        else:
            xs.append(a + FIELD / 2)
    return sorted(xs)


POSTS = post_positions()

# ---------------------------------------------------------------- vítr (EN 1991-1-4 + NA ČR)
def wind():
    vb0, cdir, cseas = 25.0, 1.0, 1.0           # větrná oblast II (ověřit v mapě NA)
    vb = vb0 * cdir * cseas
    rho = 1.25
    qb = 0.5 * rho * vb ** 2
    z0, zmin, z0II = 0.05, 2.0, 0.05            # kategorie terénu II (konzervativně: louka, sad)
    kr = 0.19 * (z0 / z0II) ** 0.07
    z = max(Y_TOP / 1000, zmin)
    cr = kr * math.log(z / z0)
    co = 1.0                                    # orografie zanedbána — ověřit (mírný svah)
    vm = cr * co * vb
    Iv = 1.0 / (co * math.log(z / z0))
    qp = (1 + 7 * Iv) * 0.5 * rho * vm ** 2
    h = Y_TOP / 1000
    cp = dict(A=3.4, B=2.1, C=1.7, D=1.2)        # tab. 7.9, l/h ≥ 10, φ = 1, bez nároží
    zones = dict(A=(0, 0.3 * h), B=(0.3 * h, 2 * h), C=(2 * h, 4 * h), D=(4 * h, 1e9))
    return dict(vb=vb, qb=qb, kr=kr, z=z, cr=cr, vm=vm, Iv=Iv, qp=qp, h=h, lh=L_WALL / 1000 / h,
                cp=cp, zones=zones)


W = wind()


def w_at(x_mm):
    """Charakteristický čistý tlak [kPa] ve vzdálenosti od bližšího volného konce."""
    d = min(x_mm, L_WALL - x_mm) / 1000
    for z, (a, b) in W["zones"].items():
        if a <= d < b:
            return W["cp"][z] * W["qp"] / 1000
    return W["cp"]["D"] * W["qp"] / 1000


def zone_at(x_mm):
    d = min(x_mm, L_WALL - x_mm) / 1000
    for z, (a, b) in W["zones"].items():
        if a <= d < b:
            return z
    return "D"


# ---------------------------------------------------------------- spojitý nosník (MKP)
def rail_fe():
    E, I = 70000.0, 11.0e4                     # Al 6063-T6, I ≈ 11 cm⁴ (40×40, ověřit u výrobce)
    grid = set(np.arange(0, L_WALL + 1, 20.0).round(1)) | {round(p, 1) for p in POSTS} | {L_WALL}
    xs = np.array(sorted(grid))
    n = len(xs)
    K = np.zeros((2 * n, 2 * n)); F = np.zeros(2 * n)
    for e in range(n - 1):
        l = xs[e + 1] - xs[e]
        k = E * I / l ** 3 * np.array([[12, 6 * l, -12, 6 * l], [6 * l, 4 * l * l, -6 * l, 2 * l * l],
                                        [-12, -6 * l, 12, -6 * l], [6 * l, 2 * l * l, -6 * l, 4 * l * l]])
        q = w_at((xs[e] + xs[e + 1]) / 2) * PANEL["B"] / 2 / 1000      # kN/m = N/mm
        fe = q * np.array([l / 2, l * l / 12, l / 2, -l * l / 12])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k; F[idx] += fe
    sup = [int(np.argmin(abs(xs - p))) * 2 for p in POSTS]
    free = [i for i in range(2 * n) if i not in sup]
    u = np.zeros(2 * n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    R = (K @ u - F)[sup] * -1                  # reakce [N]
    # ohybové momenty z koncových sil prvků
    M = []
    for e in range(n - 1):
        l = xs[e + 1] - xs[e]
        k = E * I / l ** 3 * np.array([[12, 6 * l, -12, 6 * l], [6 * l, 4 * l * l, -6 * l, 2 * l * l],
                                        [-12, -6 * l, 12, -6 * l], [6 * l, 2 * l * l, -6 * l, 4 * l * l]])
        q = w_at((xs[e] + xs[e + 1]) / 2) * PANEL["B"] / 2 / 1000
        fe = q * np.array([l / 2, l * l / 12, l / 2, -l * l / 12])
        f = k @ u[2 * e:2 * e + 4] - fe
        M += [abs(f[1]), abs(f[3])]
    defl = max(abs(u[0::2]))
    return dict(R=[-r for r in R], Mmax=max(M) / 1e6, defl=defl, E=E, I=I)


def statics():
    fe = rail_fe()
    gQ = 1.5
    b, t = POST["b"], POST["t"]
    Wpl = (b ** 3 - (b - 2 * t) ** 3) / 4
    Ipost = (b ** 4 - (b - 2 * t) ** 4) / 12
    Mpl = Wpl * POST["fy"] / 1e6
    zb, zt = RAIL_Y[0] / 1000, RAIL_Y[1] / 1000
    posts = []
    for x, R in zip(POSTS, fe["R"]):
        R = abs(R) / 1000                      # kN na jeden profil
        H = 2 * R
        Mg = R * (zb + zt)                     # moment v úrovni terénu
        Mb = R * (zb + zt - 2 * HEAD / 1000)   # moment v patě sloupku (nad hlavou vrutu)
        Lp = (Y_TOP - HEAD)
        a1, a2 = RAIL_Y[0] - HEAD, RAIL_Y[1] - HEAD
        dtop = sum(R * 1000 * a * a * (3 * Lp - a) / (6 * 210000 * Ipost) for a in (a1, a2))
        posts.append(dict(x=round(x), zona=zone_at(x), H_k=H, M_k=Mg, M_Ed_post=gQ * Mb,
                          M_Ed_vrut=gQ * Mg, UR=gQ * Mb / Mpl, d_top=dtop))
    # panely: plošně průměrný tlak na panel
    pp = []
    for i in range(N_PANEL):
        xs = np.linspace(i * PITCH, i * PITCH + PANEL["L"], 50)
        pp.append(float(np.mean([w_at(x) for x in xs])))
    Ap = PANEL["L"] * PANEL["B"] / 1e6
    clamp = max(pp) * Ap / 4 * gQ
    # rail
    MEd_rail = gQ * fe["Mmax"]
    Wreq = MEd_rail * 1e6 * 1.1 / 160 / 1000   # cm³, f0 = 160 MPa, γM1 = 1,1
    # var. A — stávající sloupek plotu Ø48×1,5 (předpoklad)
    d, tt = 48, 1.5
    Wpl_f = (d ** 3 - (d - 2 * tt) ** 3) / 6
    MRd_f = Wpl_f * 235 / 1e6
    F_f = W["cp"]["D"] * W["qp"] / 1000 * PANEL["B"] / 1000 * FIELD / 1000
    MEd_f = gQ * F_f * (Y_BOT + PANEL["B"] / 2) / 1000
    # šrouby patky 4× M12 8.8, rozteč 120 mm
    Mmax_ed = max(p["M_Ed_vrut"] for p in posts)
    Ft_bolt = Mmax_ed / 0.120 / 2
    FtRd = 0.9 * 800 * 84.3 / 1.25 / 1000
    return dict(fe=fe, posts=posts, Wpl=Wpl, Mpl=Mpl, Ipost=Ipost, panel_p=pp, clamp_Ed=clamp,
                MEd_rail=MEd_rail, Wreq=Wreq, fence=dict(MRd=MRd_f, MEd=MEd_f, UR=MEd_f / MRd_f, F=F_f),
                bolt=dict(Ft=Ft_bolt, FtRd=FtRd), H_total=sum(p["H_k"] for p in posts))


S = statics()

# ---------------------------------------------------------------- string
def string():
    n = N_PANEL
    voc_cold = PANEL["Voc"] * (1 + PANEL["tk_voc"] / 100 * (-25 - 25)) * n
    vmp_hot = PANEL["Vmp"] * (1 + PANEL["tk_vmp"] / 100 * (70 - 25)) * n
    return dict(n=n, kWp=n * PANEL["Wp"] / 1000, voc_cold=voc_cold, vmp_hot=vmp_hot, vmp_stc=PANEL["Vmp"] * n)


STR = string()

# ---------------------------------------------------------------- výkresy (společná geometrie SVG + DXF)
class Sheet:
    def __init__(self, name, th):
        self.name, self.th, self.items = name, th, []
        self.px = (1100, 100000)

    def line(self, x1, y1, x2, y2, c="ink"):
        self.items.append(("L", x1, y1, x2, y2, c))

    def rect(self, x, y, w, h, c="ink", fill=None):
        self.items.append(("R", x, y, w, h, c, fill))

    def circle(self, x, y, r, c="ink", fill=None):
        self.items.append(("C", x, y, r, c, fill))

    def text(self, x, y, s, c="txt", h=None, anchor="middle", rot=0):
        self.items.append(("T", x, y, s, c, h or self.th, anchor, rot))

    def dimh(self, x1, x2, y, s=None, ext=None):
        th = self.th
        self.line(x1, y, x2, y, "dim")
        for x in (x1, x2):
            self.line(x - th * .25, y - th * .25, x + th * .25, y + th * .25, "dim")
            if ext is not None:
                self.line(x, ext, x, y + (th * .3 if y > ext else -th * .3), "dimx")
        self.text((x1 + x2) / 2, y + th * .35, s or f"{round(x2 - x1):,}".replace(",", " "), "dimt")

    def dimv(self, y1, y2, x, s=None, ext=None):
        th = self.th
        self.line(x, y1, x, y2, "dim")
        for y in (y1, y2):
            self.line(x - th * .25, y - th * .25, x + th * .25, y + th * .25, "dim")
            if ext is not None:
                self.line(ext, y, x + (th * .3 if x > ext else -th * .3), y, "dimx")
        self.text(x - th * .35, (y1 + y2) / 2, s or f"{round(y2 - y1):,}".replace(",", " "), "dimt", rot=90)

    def bbox(self):
        xs, ys = [], []
        for it in self.items:
            if it[0] == "L":
                xs += [it[1], it[3]]; ys += [it[2], it[4]]
            elif it[0] == "R":
                xs += [it[1], it[1] + it[3]]; ys += [it[2], it[2] + it[4]]
            elif it[0] == "C":
                xs += [it[1] - it[3], it[1] + it[3]]; ys += [it[2] - it[3], it[2] + it[3]]
            else:
                w = len(it[3]) * it[5] * .55
                xs += [it[1] - w / 2, it[1] + w / 2]; ys += [it[2], it[2] + it[5]]
        return min(xs), min(ys), max(xs), max(ys)

    def svg(self):
        px_width, max_w = self.px
        x0, y0, x1, y1 = self.bbox()
        m = self.th * 1.5
        x0 -= m; y0 -= m; x1 += m; y1 += m
        out = [f'<svg class="dwg" viewBox="{x0:.0f} {-y1:.0f} {x1 - x0:.0f} {y1 - y0:.0f}" '
               f'style="min-width:{px_width}px;max-width:{max_w}px" role="img" aria-label="{self.name}">']
        for it in self.items:
            if it[0] == "L":
                out.append(f'<line class="{it[5]}" x1="{it[1]:.1f}" y1="{-it[2]:.1f}" x2="{it[3]:.1f}" y2="{-it[4]:.1f}"/>')
            elif it[0] == "R":
                cls = it[5] + (f" f-{it[6]}" if it[6] else " nofill")
                out.append(f'<rect class="{cls}" x="{it[1]:.1f}" y="{-(it[2] + it[4]):.1f}" width="{it[3]:.1f}" height="{it[4]:.1f}"/>')
            elif it[0] == "C":
                cls = it[4] + (f" f-{it[5]}" if it[5] else " nofill")
                out.append(f'<circle class="{cls}" cx="{it[1]:.1f}" cy="{-it[2]:.1f}" r="{it[3]:.1f}"/>')
            else:
                _, x, y, s, c, h, anc, rot = it
                tr = f' transform="rotate({-rot} {x:.1f} {-y:.1f})"' if rot else ""
                out.append(f'<text class="{c}" x="{x:.1f}" y="{-y:.1f}" font-size="{h:.0f}" text-anchor="{anc}"{tr}>{s}</text>')
        out.append("</svg>")
        return "\n".join(out)


def sheet_front(x_from=-600, x_to=40600, detail=False):
    th = 70 if detail else 260
    s = Sheet("Výkres 1 – pohled z vnější strany", th)
    s.line(x_from, 0, x_to, 0, "ground")
    # plot (za panely)
    fx = [k * FIELD for k in range(18)] + [40000]
    for x in fx:
        if x_from - 100 <= x <= x_to + 100:
            s.rect(x - 24, 0, 48, SITE["plot_vyska"], "fence")
    s.line(max(x_from, 0), SITE["plot_vyska"], min(x_to, 40000), SITE["plot_vyska"], "fence")
    # panely
    for i in range(N_PANEL):
        x = i * PITCH
        if x + PANEL["L"] < x_from or x > x_to:
            continue
        s.rect(x, Y_BOT, PANEL["L"], PANEL["B"], "ink", "panel")
        for k in (1, 2):
            s.line(x, Y_BOT + k * PANEL["B"] / 3, x + PANEL["L"], Y_BOT + k * PANEL["B"] / 3, "cell")
        s.text(x + PANEL["L"] / 2, Y_BOT + PANEL["B"] / 2 - th * .35, f"P{i + 1}", "ptxt")
    # profily (skryté), dilatace
    for y in RAIL_Y:
        s.line(max(x_from, 0), y, min(x_to, L_WALL), y, "hidden")
    for d in DIL:
        if x_from < d < x_to:
            s.line(d, Y_BOT - 150, d, Y_TOP + 150, "accent")
            s.text(d, Y_TOP + 200, "dilatace profilů", "note", th * .7)
    # sloupky + vruty
    for x in POSTS:
        if not (x_from < x < x_to):
            continue
        s.rect(x - 40, HEAD, 80, Y_BOT - HEAD, "steel", "steel")
        s.rect(x - 40, Y_BOT, 80, Y_TOP - Y_BOT, "hidden")
        s.rect(x - 38, -VRUT["L"] + HEAD, 76, VRUT["L"] - HEAD, "hidden")
    if detail:
        s.dimh(0, PANEL["L"], Y_TOP + 380, ext=Y_TOP)
        s.dimh(PANEL["L"], PITCH, Y_TOP + 380, "20")
        s.dimh(PITCH, PITCH + PANEL["L"], Y_TOP + 380, ext=Y_TOP)
        prev = 0
        for x in [p for p in POSTS if p < x_to]:
            s.dimh(prev, x, -VRUT["L"] - 250, ext=-VRUT["L"] + HEAD)
            prev = x
        for x in fx:
            if 0 < x < x_to:
                s.dimh(x - FIELD, x, -VRUT["L"] - 650, "2 210–2 330" if x > FIELD else "≈ 2 270", ext=0)
        s.dimv(0, Y_BOT, x_from + 250, ext=0)
        s.dimv(Y_BOT, Y_TOP, x_from + 250)
        s.dimv(0, HEAD, x_from + 650, ext=0)
        s.dimv(-VRUT["L"] + HEAD, HEAD, x_from + 650, ext=0)
        s.text(x_from + 900, -VRUT["L"] / 2, "zemní vrut Ø76×1600", "note", anchor="start")
        s.text(POSTS[0] + 70, HEAD + 60, "sloupek 80×80×3", "note", anchor="start")
        s.text(x_to - 50, -VRUT["L"] - 300, "osy sloupků FV", "note", anchor="end")
        s.text(x_to - 50, -VRUT["L"] - 700, "rozteč plotu (skutečná)", "note", anchor="end")
    else:
        s.dimh(0, L_WALL, Y_TOP + 900, ext=Y_TOP)
        s.dimh(L_WALL, 40000, Y_TOP + 900, ext=SITE["plot_vyska"])
        s.text((L_WALL + 40000) / 2, Y_TOP + 350, "vynecháno – stín stromu", "note", th * .8)
        s.dimh(0, 40000, Y_TOP + 1700, "plot ≈ 40 000", ext=Y_TOP + 900)
        s.dimv(0, Y_TOP, -400, ext=0)
        # zóny větru
        h = W["h"] * 1000
        edges = [0, .3 * h, 2 * h, 4 * h]
        for side in (0, 1):
            for z, (a, b) in zip("ABC", zip(edges, edges[1:])):
                xa, xb = (a, b) if side == 0 else (L_WALL - b, L_WALL - a)
                s.line(xa, -350, xa, -650, "dimx"); s.line(xb, -350, xb, -650, "dimx")
                s.text((xa + xb) / 2, -620, z, "note", th * .8)
        s.text(L_WALL / 2, -620, "zóna D", "note", th * .8)
        s.text(L_WALL / 2, -1100, "zóny větru podle ČSN EN 1991-1-4, tab. 7.9", "note", th * .7)
        s.text(PITCH * 9.5, Y_TOP + 350, f"1 string · {N_PANEL} panelů · {STR['kWp']:.2f} kWp", "ptxt2", th * .8)
    return s


def sheet_side():
    s = Sheet("Výkres 2 – boční řez", 30)
    s.line(-700, 0, 900, 0, "ground")
    for x in range(-650, 900, 120):
        s.line(x, 0, x - 60, -60, "ground")
    s.text(-450, 1650, "ZAHRADA (uvnitř)", "note", anchor="middle")
    s.text(600, 1650, "SOUSED", "note", anchor="middle")
    # plot
    s.rect(-24, -800, 48, 800 + SITE["plot_vyska"], "fence")
    s.rect(-25, -50, 50, 250, "fence", "conc")
    s.text(-60, 120, "podhrabová deska", "note", 22, "end")
    s.text(-60, 1350, "sloupek plotu (stávající)", "note", 22, "end")
    s.text(-60, 1300, "pletivo, tkanina odstraněna", "note", 22, "end")
    # hranice
    s.line(SITE["pas"], -1900, SITE["pas"], 1900, "border")
    s.text(SITE["pas"] + 20, 1800, "hranice pozemku (vytyčit)", "note", 22, "start")
    # vrut + sloupek
    x = X_POST_PLOT
    s.rect(x - 38, -VRUT["L"] + HEAD + 150, 76, VRUT["L"] - HEAD - 150, "steel", "steel")
    for k in range(6):
        y = -VRUT["L"] + HEAD + 200 + k * 220
        s.line(x - 70, y, x + 70, y + 60, "steel")
    s.line(x - 38, -VRUT["L"] + HEAD + 150, x, -VRUT["L"] + HEAD, "steel")
    s.line(x + 38, -VRUT["L"] + HEAD + 150, x, -VRUT["L"] + HEAD, "steel")
    s.rect(x - 70, HEAD - 8, 140, 8, "steel", "steel")
    s.rect(x - 80, HEAD, 160, 8, "steel", "steel")
    s.rect(x - 40, HEAD + 8, 80, Y_TOP - HEAD - 8, "steel", "steel")
    s.rect(x - 40, Y_TOP, 80, 6, "ink", "ink")
    # držáky + profily + panel
    xr = x + 40
    for y in RAIL_Y:
        s.rect(x + 40, y - 25, 5, 50, "ink", "ink")
        s.rect(xr + 5, y - RAIL / 2, RAIL, RAIL, "ink", "rail")
    xp = xr + 5 + RAIL
    s.rect(xp, Y_BOT, PANEL["t"], PANEL["B"], "ink", "panel")
    for y in (Y_BOT, Y_TOP):
        s.rect(xp + PANEL["t"], y - 15 if y == Y_TOP else y, 8, 15, "ink", "ink")
    s.text(xp + 60, 900, "FV panel naležato", "note", 22, "start")
    s.text(xp + 60, 860, f"{PANEL['L']}×{PANEL['B']}×{PANEL['t']}", "note", 22, "start")
    s.text(x + 60, -900, f"zemní vrut Ø{VRUT['d']}×{VRUT['L']}", "note", 22, "start")
    s.text(x + 60, -940, "s přírubou, žár. Zn", "note", 22, "start")
    s.text(xr + 60, RAIL_Y[1] + 60, "Al profil 40×40", "note", 22, "start")
    # kóty
    s.dimh(0, x, -1750, ext=-VRUT["L"] + HEAD)
    s.dimh(0, xp + PANEL["t"] + 8, 1950, ext=Y_TOP)
    s.dimh(0, SITE["pas"], 2050, ext=1950)
    s.dimv(0, Y_BOT, 700, ext=xp + PANEL["t"])
    s.dimv(Y_BOT, Y_TOP, 700)
    s.dimv(0, Y_TOP, 820, ext=xp + PANEL["t"])
    s.dimv(-VRUT["L"] + HEAD, 0, -300, ext=x - 38)
    s.dimv(0, HEAD, -300)
    s.dimv(RAIL_Y[0], RAIL_Y[1], 500, ext=xr + 45)
    s.text(150, -2050, f"sklon 90° · azimut {SITE['azimut']}°", "note", 26)
    return s


def sheet_plan():
    s = Sheet("Výkres 3 – půdorys (výřez 0–8 m)", 85)
    X1 = 8200
    s.line(-400, 0, X1, 0, "fence")
    for k in range(5):
        s.circle(k * FIELD, 0, 24, "fence")
    s.rect(-400, -25, X1 + 400, 50, "fence")
    s.line(-400, -SITE["pas"], X1, -SITE["pas"], "border")
    s.text(X1 - 50, -SITE["pas"] - 90, "hranice pozemku (30 cm za osou plotu – vytyčit)", "note", anchor="end")
    s.text(X1 - 50, 160, "plot (stávající, osa)", "note", anchor="end")
    for x in [p for p in POSTS if p < X1]:
        s.rect(x - 40, -X_POST_PLOT - 40, 80, 80, "steel", "steel")
        s.circle(x, -X_POST_PLOT, 38, "hidden")
    for y in (-X_POST_PLOT - 40, -X_POST_PLOT - 85):
        s.line(0, y, X1, y, "hidden")
    for i in range(5):
        x = i * PITCH
        s.rect(x, -X_POST_PLOT - 85 - PANEL["t"], min(PANEL["L"], X1 - x), PANEL["t"], "ink", "panel")
    prev = 0
    for x in [p for p in POSTS if p < X1]:
        s.dimh(prev, x, -800, ext=-X_POST_PLOT - 40)
        prev = x
    s.dimh(0, PANEL["L"], -1150, ext=-X_POST_PLOT - 115)
    s.dimv(-X_POST_PLOT, 0, -250, ext=POSTS[0])
    s.dimv(-SITE["pas"], 0, -500)
    # sever: dolů = vnější normála 150°, nahoru = 330°, sever 30° doprava od svislice
    cx, cy, r = X1 - 600, 900, 300
    a = math.radians(30)
    s.line(cx - r * math.sin(a), cy - r * math.cos(a), cx + r * math.sin(a), cy + r * math.cos(a), "ink")
    s.line(cx + r * math.sin(a), cy + r * math.cos(a), cx + r * math.sin(a) - 90, cy + r * math.cos(a) - 90, "ink")
    s.text(cx + (r + 90) * math.sin(a), cy + (r + 90) * math.cos(a), "S", "ptxt2")
    s.text(cx, cy - r - 160, "panely → 150° (JJV)", "note")
    s.text(3000, 1000, "ZAHRADA", "note")
    s.text(3000, -1550, "POZEMEK SOUSEDA", "note")
    return s


def sheet_details():
    s = Sheet("Výkres 4 – konstrukční detaily", 13)
    # D1 patka: příruba vrutu + patní deska + 4×M12
    ox, oy = 0, 0
    s.rect(ox - 38, oy - 220, 76, 212, "steel", "steel")
    s.rect(ox - 70, oy - 8, 140, 8, "steel", "steel")
    s.rect(ox - 80, oy, 160, 8, "steel", "steel")
    s.rect(ox - 40, oy + 8, 80, 220, "steel", "steel")
    for bx in (-60, 60):
        s.rect(ox + bx - 6, oy - 20, 12, 40, "ink", "ink")
    s.line(ox - 160, oy - 100, ox + 160, oy - 100, "ground")
    s.dimh(ox - 80, ox + 80, oy + 260, ext=oy + 8)
    s.dimh(ox - 60, ox + 60, oy - 260, ext=oy - 20)
    s.text(ox, oy + 300, "D1 – kotvení sloupku na vrut", "h")
    s.text(ox + 95, oy + 20, "patní deska P8 160×160", "note", anchor="start")
    s.text(ox + 95, oy - 6, "příruba vrutu (dle výrobce)", "note", anchor="start")
    s.text(ox + 95, oy - 32, "4× M12 8.8 žár. Zn", "note", anchor="start")
    s.text(ox + 95, oy + 160, "jekl 80×80×3, svar dokola a5", "note", anchor="start")
    # D2 půdorysný řez: sloupek – úhelník – profil
    ox = 520
    s.rect(ox - 40, -40, 80, 80, "steel", "steel")
    s.rect(ox + 40, -30, 5, 60, "ink", "ink")
    s.rect(ox + 40, 25, 50, 5, "ink", "ink")
    s.rect(ox + 45, -20, 40, 40, "ink", "rail")
    s.rect(ox + 85, -40, 30, 80, "ink", "panel")
    s.line(ox - 60, 0, ox + 45, 0, "hidden")
    s.dimh(ox - 40, ox + 40, -90, ext=-40)
    s.dimh(ox + 45, ox + 85, -90, ext=-20)
    s.dimh(ox + 85, ox + 115, -90, ext=-40)
    s.text(ox + 30, 300, "D2 – držák profilu (řez)", "h")
    s.text(ox + 30, 150, "úhelník L50×50×5, l = 80", "note")
    s.text(ox + 30, 128, "1× M10 do sloupku (prův.), 1× T-šroub M8", "note")
    s.text(ox + 30, 106, "do drážky profilu; otvor oválný ±10 mm", "note")
    # D3 svorka na dlouhé hraně panelu
    ox = 1050
    s.rect(ox, -20, 40, 40, "ink", "rail")
    s.rect(ox + 40, -60, 30, 140, "ink", "panel")
    s.rect(ox + 70, 55, 10, 25, "ink", "ink")
    s.line(ox + 75, 55, ox + 20, 55, "ink")
    s.dimh(ox, ox + 40, -100, ext=-20)
    s.dimh(ox + 40, ox + 70, -100, ext=-60)
    s.text(ox + 40, 300, "D3 – koncová svorka na rám", "h")
    s.text(ox + 40, 150, "4 svorky / panel na dlouhých hranách", "note")
    s.text(ox + 40, 128, "v upínací zóně výrobce (typ. ¼ L od rohu)", "note")
    s.text(ox + 40, 106, "rám překrývá profil ≥ 20 mm", "note")
    # D4 dilatace profilu
    ox = 1500
    s.rect(ox, -20, 200, 40, "ink", "rail")
    s.rect(ox + 220, -20, 200, 40, "ink", "rail")
    s.rect(ox + 120, -26, 180, 52, "accent")
    for bx in (150, 270):
        s.rect(ox + bx - 12, -5, 24, 10, "ink")
    s.dimh(ox + 200, ox + 220, -90, "20", ext=-20)
    s.dimh(ox + 120, ox + 300, 90, ext=26)
    s.text(ox + 210, 300, "D4 – dilatační spoj profilu", "h")
    s.text(ox + 210, 150, "2× na řadu, v mezeře mezi panely", "note")
    s.text(ox + 210, 128, "spojka s oválnými otvory, 1 strana pevně", "note")
    return s


SHEETS = [sheet_front(), sheet_front(-700, 7600, detail=True), sheet_side(), sheet_plan(), sheet_details()]
SHEETS[1].name = "Výkres 1b – pohled z vnější strany, výřez 0–7,6 m"
for _sh, _px in zip(SHEETS, [(1100, 100000), (900, 100000), (520, 640), (800, 100000), (860, 100000)]):
    _sh.px = _px


def write_dxf(path):
    layers = {"ink": "OBRYS", "panel": "PANEL", "cell": "PANEL", "steel": "OCEL", "rail": "PROFIL",
              "fence": "PLOT", "ground": "TEREN", "dim": "KOTY", "dimx": "KOTY", "dimt": "KOTY",
              "hidden": "SKRYTE", "border": "HRANICE", "accent": "OCEL", "txt": "TEXT", "note": "TEXT",
              "ptxt": "TEXT", "ptxt2": "TEXT", "h": "TEXT"}
    o = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$DWGCODEPAGE", "3", "ANSI_1250",
         "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]

    def L(x1, y1, x2, y2, lay):
        o.extend(["0", "LINE", "8", lay, "10", f"{x1:.2f}", "20", f"{y1:.2f}", "11", f"{x2:.2f}", "21", f"{y2:.2f}"])
    offy = 0
    for sh in SHEETS:
        x0, y0, x1, y1 = sh.bbox()
        dy = offy - y1
        for it in sh.items:
            if it[0] == "L":
                L(it[1], it[2] + dy, it[3], it[4] + dy, layers.get(it[5], "0"))
            elif it[0] == "R":
                x, y, w, h = it[1], it[2] + dy, it[3], it[4]
                lay = layers.get(it[5], "0")
                L(x, y, x + w, y, lay); L(x + w, y, x + w, y + h, lay); L(x + w, y + h, x, y + h, lay); L(x, y + h, x, y, lay)
            elif it[0] == "C":
                o.extend(["0", "CIRCLE", "8", layers.get(it[4], "0"), "10", f"{it[1]:.2f}", "20", f"{it[2] + dy:.2f}", "40", f"{it[3]:.2f}"])
            else:
                _, x, y, txt, c, h, anc, rot = it
                al = {"start": 0, "middle": 1, "end": 2}[anc]
                o.extend(["0", "TEXT", "8", layers.get(c, "TEXT"), "10", f"{x:.2f}", "20", f"{y + dy:.2f}", "40", f"{h:.1f}",
                          "1", txt, "50", f"{rot}", "72", str(al), "11", f"{x:.2f}", "21", f"{y + dy:.2f}"])
        o.extend(["0", "TEXT", "8", "TEXT", "10", f"{x0:.2f}", "20", f"{offy + sh.th * 2:.2f}", "40", f"{sh.th * 1.4:.1f}", "1", sh.name])
        offy += -(y1 - y0) - 3000
    o.extend(["0", "ENDSEC", "0", "EOF"])
    with open(path, "w", encoding="cp1250", errors="replace") as f:
        f.write("\n".join(o) + "\n")


# ---------------------------------------------------------------- rozpočet (Kč vč. DPH; odhad = neověřeno)
def bom():
    n = len(POSTS)
    rail_bars = 12
    rows = [
        # skupina, název, specifikace, materiál, rozměr, ks, jedn. cena, ověřeno?
        ("Nosná konstrukce", "Sloupek s patní deskou", "jekl 80×80×3 + P8 160×160, 4 otvory Ø14, 2 otvory Ø11 pro držáky, svar a5, žárový zinek", "S235", "l = 1 400 mm", n, 1050, False),
        ("Nosná konstrukce", "Nosný profil FV", "Al profil 40×40 s drážkou (např. G21 HPG2144X), W ≥ 4 cm³", "Al 6063-T6", "6 000 mm", rail_bars, 1070, True),
        ("Nosná konstrukce", "Držák profilu", "úhelník L50×50×5 s oválným otvorem", "S235 žár. Zn", "l = 80 mm", 2 * n, 80, False),
        ("Nosná konstrukce", "Spojka profilu pevná", "pro profil 40×40", "Al", "—", 8, 120, False),
        ("Nosná konstrukce", "Spojka profilu dilatační", "s oválnými otvory", "Al", "—", 4, 250, False),
        ("Nosná konstrukce", "Záslepka sloupku", "PE 80×80", "PE", "—", n, 25, False),
        ("Kotvení", f"Zemní vrut s přírubou", f"Ø{VRUT['d']}×{VRUT['L']} mm, příruba 4× M12, rozteč děr 120 mm", "S235 žár. Zn", f"{VRUT['L']} mm", n, 1200, False),
        ("Kotvení", "Strojní zavrtání vrutů", "vč. dopravy stroje, předvrtání v kamenité zemině", "služba", "—", n, 300, False),
        ("Kotvení", "Zatěžovací zkouška vrutu", "2 ks, vodorovná síla dle tab. statiky", "služba", "—", 1, 2500, False),
        ("Spojovací materiál", "Koncová svorka panelu", "pro rám 30 mm, s T-šroubem M8", "Al + nerez", "—", 4 * N_PANEL, 45, False),
        ("Spojovací materiál", "Šroub + T-šroub držáku", "M10×100 8.8 + M8 T-šroub s maticí", "žár. Zn / nerez", "—", 2 * n, 25, False),
        ("Spojovací materiál", "Šroubová sada patky", "M12×40 8.8, matice, 2 podložky", "žár. Zn", "—", 4 * n, 20, False),
        ("Spojovací materiál", "Pospojování konstrukce", "Cu 6 mm² zelenožlutý + svorky na sloupky, propojení na HOP", "Cu", "≈ 45 m", 1, 2000, False),
        ("Spojovací materiál", "Zinkový sprej", "oprava řezů a poškození Zn", "—", "—", 2, 150, False),
        ("Montáž", "Montáž konstrukce a panelů", "2 osoby × 1,5 dne", "práce", "24 h", 24, 500, False),
    ]
    out = []
    for r in rows:
        out.append(dict(skup=r[0], nazev=r[1], spec=r[2], mat=r[3], rozm=r[4], ks=r[5], cena=r[6], celk=r[5] * r[6], over=r[7]))
    return out


BOM = bom()

# ---------------------------------------------------------------- HTML
def fmt(x, d=0):
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s


def html():
    st = S
    sums = {}
    for r in BOM:
        sums[r["skup"]] = sums.get(r["skup"], 0) + r["celk"]
    tot = sum(sums.values())
    E90 = sum(PVGIS[90])
    Ey = E90 * STR["kWp"]
    pmax = max(st["posts"], key=lambda p: p["M_Ed_vrut"])
    urmax = max(p["UR"] for p in st["posts"])
    win = lambda a: sum(PVGIS[a][i] for i in (0, 1, 10, 11))
    sumr = lambda a: sum(PVGIS[a][i] for i in (5, 6, 7))
    proj = lambda a: PANEL["B"] * math.cos(math.radians(a))

    tilt_rows = ""
    for a in (90, 80, 75, 60, 37):
        hloubka = proj(a) + 130
        fit = "vejde" if hloubka <= SITE["pas"] - 40 else "nevejde"
        lab = {90: "90° svisle (návrh)", 80: "80°", 75: "75°", 60: "60°", 37: "37° optimum (pro srovnání)"}[a]
        tilt_rows += (f"<tr{' class=hl' if a == 90 else ''}><td>{lab}</td><td class=n>{fmt(sum(PVGIS[a]))}</td>"
                      f"<td class=n>{fmt(sum(PVGIS[a]) / sum(PVGIS[37]) * 100)} %</td><td class=n>{win(a)}</td><td class=n>{sumr(a)}</td>"
                      f"<td class=n>{fmt(hloubka)}</td><td><span class='chip {'ok' if fit == 'vejde' else 'bad'}'>{fit}</span></td></tr>")

    post_rows = ""
    for i, p in enumerate(st["posts"], 1):
        post_rows += (f"<tr><td class=n>S{i}</td><td class=n>{fmt(p['x'])}</td><td>{p['zona']}</td><td class=n>{fmt(p['H_k'], 2)}</td>"
                      f"<td class=n>{fmt(p['M_k'], 2)}</td><td class=n>{fmt(p['M_Ed_vrut'], 2)}</td><td class=n>{fmt(p['UR'], 2)}</td>"
                      f"<td class=n>{fmt(p['d_top'], 0)}</td></tr>")

    bom_rows = ""
    cur = None
    for r in BOM:
        if r["skup"] != cur:
            cur = r["skup"]
            bom_rows += f"<tr class=grp><td colspan=8>{cur}</td></tr>"
        bom_rows += (f"<tr><td>{r['nazev']}</td><td>{r['spec']}</td><td>{r['mat']}</td><td>{r['rozm']}</td>"
                     f"<td class=n>{r['ks']}</td><td class=n>{fmt(r['cena'])}</td><td class=n>{fmt(r['celk'])}</td>"
                     f"<td><span class='chip {'ok' if r['over'] else 'est'}'>{'ověřeno' if r['over'] else 'odhad'}</span></td></tr>")
    sum_rows = "".join(f"<tr><td>{k}</td><td class=n>{fmt(v)}</td><td class=n>{fmt(v / STR['kWp'])}</td></tr>" for k, v in sums.items())

    zones_txt = ", ".join(f"{z}: {a:.2f}–{min(b, 99):.2f} m → c<sub>p,net</sub> = {W['cp'][z]} → w = {W['cp'][z] * W['qp'] / 1000:.2f} kPa"
                          for z, (a, b) in W["zones"].items())
    sheets_html = ""
    for sh in SHEETS:
        sheets_html += f'<figure class="sheet"><figcaption>{sh.name}</figcaption><div class="scroll">{sh.svg()}</div></figure>'
    fence = st["fence"]

    css = """
:root{
 /* layout: technický projektový podklad – úzký sloupec textu, výkresy přes celou šíři se svým posuvem */
 --bg:#f4f6f7;--paper:#ffffff;--fg:#1a2228;--muted:#5b6872;--line:#d5dce0;--accent:#0d5c86;
 --dim:#b8432b;--panel:#1f3d5c;--steel:#8f9ba5;--ok:#2f7d4f;--warn:#a86a10;--bad:#b23a2b;
 --hl:#e7f0f5;--fence:#9aa7b0;--ground:#7b6a52;
 --f-display:"Barlow Condensed","Arial Narrow",sans-serif;--f-body:"Barlow",system-ui,sans-serif;--f-mono:"JetBrains Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11171b;--paper:#182026;--fg:#e3e9ec;--muted:#98a6ae;--line:#2c3a42;--accent:#5fb3e0;--dim:#ef8a6c;--panel:#3e6a95;--steel:#7e8b95;--ok:#5cc58a;--warn:#e0a948;--bad:#ef7a6a;--hl:#1d2c36;--fence:#61707a;--ground:#a8946f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#11171b;--paper:#182026;--fg:#e3e9ec;--muted:#98a6ae;--line:#2c3a42;--accent:#5fb3e0;--dim:#ef8a6c;--panel:#3e6a95;--steel:#7e8b95;--ok:#5cc58a;--warn:#e0a948;--bad:#ef7a6a;--hl:#1d2c36;--fence:#61707a;--ground:#a8946f;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:16px;line-height:1.55;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:32px 64px}
main{max-width:1100px;margin:0 auto;display:grid;gap:40px}
header{display:grid;gap:12px}
.eyebrow{font-family:var(--f-mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-family:var(--f-display);font-weight:600;font-size:clamp(34px,6vw,54px);line-height:1.02;margin:0;text-wrap:balance}
h2{font-family:var(--f-display);font-weight:600;font-size:28px;margin:0 0 12px;text-wrap:balance}
h3{font-size:17px;margin:20px 0 6px}
p,li{max-width:72ch}
.lead{font-size:18px;color:var(--muted);max-width:70ch;margin:0}
.warn{border:1px solid var(--warn);color:var(--fg);background:var(--paper);padding:12px 16px;border-radius:4px;font-size:15px}
.warn b{color:var(--warn)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.kpi{background:var(--paper);padding:14px 16px;display:grid;gap:2px}
.kpi .v{font-family:var(--f-display);font-size:30px;font-weight:600;font-variant-numeric:tabular-nums}
.kpi .l{font-size:13px;color:var(--muted)}
section{display:grid;gap:8px;min-width:0}
.tw{overflow-x:auto;border:1px solid var(--line);background:var(--paper)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-weight:600;color:var(--muted);font-size:12px;letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}
td.n,th.n{text-align:right;font-family:var(--f-mono);font-size:13px;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.hl td{background:var(--hl);font-weight:600}
tr.grp td{background:var(--bg);font-weight:600;font-size:13px}
tfoot td{font-weight:700}
.chip{display:inline-block;font-size:12px;padding:1px 8px;border-radius:10px;border:1px solid currentColor;white-space:nowrap}
.chip.ok{color:var(--ok)}.chip.bad{color:var(--bad)}.chip.est{color:var(--warn)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.card{background:var(--paper);border:1px solid var(--line);padding:16px;display:grid;gap:6px;min-width:0}
.card h3{margin:0}
.card.pick{border-color:var(--accent)}
.card ul{margin:0;padding-left:18px}
.mono{font-family:var(--f-mono);font-size:13px}
.calc{background:var(--paper);border:1px solid var(--line);padding:14px 16px;font-family:var(--f-mono);font-size:13px;line-height:1.7;overflow-x:auto}
.sheet{margin:0;background:var(--paper);border:1px solid var(--line)}
.sheet figcaption{font-family:var(--f-display);font-size:20px;font-weight:600;padding:10px 14px;border-bottom:1px solid var(--line)}
.scroll{overflow-x:auto;padding:8px}
svg.dwg{width:100%;height:auto;display:block;margin:0 auto}
svg.dwg *{vector-effect:non-scaling-stroke}
svg .ink{stroke:var(--fg);stroke-width:1.2}
svg .steel{stroke:var(--fg);stroke-width:1}
svg .rail{stroke:var(--fg)}
svg .fence{stroke:var(--fence);stroke-width:1;fill:none}
svg .ground{stroke:var(--ground);stroke-width:1.6}
svg .hidden{stroke:var(--muted);stroke-width:.9;stroke-dasharray:6 4;fill:none}
svg .border{stroke:var(--bad);stroke-width:1.3;stroke-dasharray:14 4 3 4}
svg .accent{stroke:var(--accent);stroke-width:1.6;fill:none}
svg .cell{stroke:var(--paper);stroke-width:.6;opacity:.6}
svg .dim,svg .dimx{stroke:var(--dim);stroke-width:.8}
svg .nofill{fill:none}
svg .f-panel{fill:var(--panel)}svg .f-steel{fill:var(--steel)}svg .f-rail{fill:var(--line)}svg .f-ink{fill:var(--fg)}svg .f-conc{fill:var(--line)}
svg text{font-family:var(--f-body);fill:var(--fg)}
svg text.dimt{fill:var(--dim);font-family:var(--f-mono)}
svg text.note{fill:var(--muted)}
svg text.ptxt{fill:#ffffff;opacity:.85}
svg text.ptxt2{fill:var(--accent);font-weight:600}
svg text.h{font-weight:700}
ol.steps{display:grid;gap:10px;padding-left:22px;margin:0}
ol.steps li{padding-left:4px}
.legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:22px;height:0;border-top:2px solid}
footer{font-size:13px;color:var(--muted)}
"""
    return f"""<meta charset="utf-8">
<title>Fotovoltaický plot Vendryně</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700&family=Barlow+Condensed:wght@600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>{css}</style>
<main>
<header>
 <div class="eyebrow">Projektový podklad · předběžný návrh · 23. 10. 2026</div>
 <h1>Fotovoltaický plot Vendryně</h1>
 <p class="lead">Samostatná svislá konstrukce na zemních vrutech v pásu 30 cm za stávajícím plotem. Jedna řada panelů naležato nahrazuje stínicí tkaninu a vyplňuje plot do výšky 1,5 m. Připojení jako samostatný string na SolaX X3-Ultra 25K.</p>
 <div class="warn"><b>Předběžný návrh, není to ověřený statický projekt.</b> Zatížení je spočteno podle ČSN EN 1991-1-4 s předpoklady uvedenými níže. Dimenze sloupků, kotvení a únosnost vrutů v konkrétní zemině musí před realizací ověřit autorizovaný statik a zkouška vrutů na místě.</div>
</header>

<div class="kpis">
 <div class="kpi"><span class="v">{N_PANEL}</span><span class="l">panelů naležato, 1 řada</span></div>
 <div class="kpi"><span class="v">{fmt(STR['kWp'], 2)} kWp</span><span class="l">instalovaný výkon</span></div>
 <div class="kpi"><span class="v">≈ {fmt(round(Ey, -1))} kWh</span><span class="l">ročně (PVGIS, svisle, 150°)</span></div>
 <div class="kpi"><span class="v">{len(POSTS)}</span><span class="l">zemních vrutů Ø76×1600</span></div>
 <div class="kpi"><span class="v">≈ {fmt(round(tot, -3) / 1000)} tis. Kč</span><span class="l">konstrukce vč. montáže, s DPH, odhad</span></div>
 <div class="kpi"><span class="v">≈ {fmt(round(tot / STR['kWp'], -2))} Kč</span><span class="l">konstrukce na 1 kWp</span></div>
</div>

<section>
<h2>Vstupní údaje</h2>
<div class="tw"><table>
<tr><th>Parametr</th><th>Hodnota</th><th>Zdroj</th></tr>
<tr><td>Lokalita</td><td>{SITE['obec']}, 49°40′ s. š., 18°43′ v. d., {SITE['alt']} m n. m.</td><td>uživatel, kompas iPhone</td></tr>
<tr><td>Plot</td><td>drátěné pletivo, délka ≈ 40 m, výška 1 500 mm, linie v rovině (oba konce ve stejné výšce)</td><td>uživatel, fotografie</td></tr>
<tr><td>Rozteč sloupků plotu</td><td>2 210–2 330 mm, každé pole jinak</td><td>uživatel, změřeno</td></tr>
<tr><td>Sloupky plotu</td><td>tenká kruhová trubka, odhad Ø 38–48 mm, některé zdvojené vzpěrou; patky neznámé</td><td>fotografie, <b>neověřeno</b></td></tr>
<tr><td>Orientace panelů</td><td>azimut 150° (JJV), vnější strana plotu</td><td>uživatel, kompas</td></tr>
<tr><td>Prostor</td><td>pás 300 mm za plotem patří uživateli, dál je pozemek souseda; plot patří uživateli</td><td>uživatel, <b>vytyčit geodetem</b></td></tr>
<tr><td>Zastínění</td><td>na jednom konci strom, vynechat posledních 2–3 pole; vně louka se vzrostlými ovocnými stromy</td><td>uživatel, fotografie</td></tr>
<tr><td>Panel (předpoklad)</td><td>{PANEL['L']}×{PANEL['B']}×{PANEL['t']} mm, {PANEL['Wp']} Wp, ≈ {PANEL['kg']} kg, Voc ≈ {PANEL['Voc']} V, Isc ≈ {PANEL['Isc']} A, zadní zkušební zatížení {PANEL['zad_zkus']} Pa</td><td><b>typ zatím nevybrán</b></td></tr>
<tr><td>Střídač</td><td>SolaX X3-Ultra 25K: 3 MPPT, 36 A na MPPT, 2 vstupy na MPPT, rozsah MPPT 160–950 V</td><td><a href="https://www.solaxpower.com/products/x3-ultra/">solaxpower.com</a></td></tr>
</table></div>
</section>

<section>
<h2>Varianty konstrukce</h2>
<p>Stávající plot je stavěný na pletivo. Plná plocha panelů ve větru působí na sloupek zhruba 2–3× větší silou, než jakou tenká trubka unese.</p>
<div class="grid2">
 <div class="card"><h3>A – na stávajících sloupcích <span class="chip bad">nevyhoví</span></h3>
  <ul><li>Sloupek Ø48×1,5 (optimistický předpoklad): M<sub>Rd</sub> = {fmt(fence['MRd'], 2)} kNm</li>
  <li>Pole 2,27 m, zóna D: M<sub>Ed</sub> = {fmt(fence['MEd'], 2)} kNm → využití <b>{fmt(fence['UR'] * 100)} %</b></li>
  <li>Patky neznámé, sloupky už teď místy vychýlené</li><li>Nejlevnější, ale nebezpečná. Zamítnuto.</li></ul></div>
 <div class="card pick"><h3>B – samostatná konstrukce na zemních vrutech <span class="chip ok">návrh</span></h3>
  <ul><li>Nezávislá na statice plotu, rozteč sloupků FV volná (1 sloupek uprostřed pole plotu)</li>
  <li>Bez betonu a výkopů, rozebíratelná, šroubované spoje</li>
  <li>Vejde se do pásu 300 mm (hloubka konstrukce ≈ 225 mm od osy plotu)</li>
  <li>Vruty je potřeba ověřit zkouškou v místní zemině</li></ul></div>
 <div class="card"><h3>C – kombinace plot + přídavné podpěry <span class="chip est">nevýhodná</span></h3>
  <ul><li>Stávající sloupky nepřenesou ani podíl zatížení bez zesílení, takže se celá síla stejně přesune na nové podpěry</li>
  <li>Spoje k plotu bez známé únosnosti, různé rozteče a vychýlení komplikují montáž</li>
  <li>Úspora proti B je malá: ušetří se nejvýš pár vrutů</li></ul></div>
 <div class="card"><h3>Další možnosti</h3>
  <ul><li><b>Zabetonované sloupky</b>: patka se do pásu 300 mm vejde jen jako vrtaná Ø 250 mm. Řešení je spolehlivé, ale pracnější a nerozebíratelné. Je to záloha, pokud vruty v kamenité zemině nevyhoví.</li>
  <li><b>Bifaciální panely sklo-sklo</b>: zadní strana dostane světlo ze zahrady přes pletivo. Orientačně +5 až 10 % výroby, panel je ale těžší a dražší.</li></ul></div>
</div>
</section>

<section>
<h2>Sklon panelů</h2>
<p>Výroba podle PVGIS 5.2 pro 1 kWp, azimut 150°, ztráty 14 %, včetně horizontu terénu. Hloubka zahrnuje průmět panelu ({PANEL['B']} mm naležato) a 130 mm na sloupek a profil. Sklon kromě svislého by navíc panely vykláněl nad pozemek souseda a nenahradil by stínicí tkaninu.</p>
<div class="tw"><table>
<tr><th>Sklon</th><th class=n>kWh/kWp·rok</th><th class=n>vůči optimu</th><th class=n>zima XI–II</th><th class=n>léto VI–VIII</th><th class=n>hloubka mm</th><th>pás 300 mm</th></tr>
{tilt_rows}
</table></div>
<p><b>Závěr:</b> svisle se ročně vyrobí asi {fmt(sum(PVGIS[90]) / sum(PVGIS[37]) * 100)} % optima, ale v zimě (listopad–únor) <b>{fmt(win(90) / win(37) * 100)} % optima</b>, takže svislá plocha je zimní zdroj. V létě vyrábí méně, což u střídače se střešní FVE nevadí: svislý string pokrývá ráno, zimu a období po sněžení. Větší sklon se do pásu nevejde. Panely naležato mají pruhy článků vodorovně, takže sníh nebo tráva u spodní hrany vyřadí přes bypass diodu jen spodní třetinu panelu.</p>
</section>

<section>
<h2>Rozmístění a zapojení</h2>
<ul>
<li>{N_PANEL} panelů naležato v jedné řadě, mezera {GAP} mm, délka stěny <b>{fmt(L_WALL)} mm</b>. Horní hrana 1 500 mm (= výška plotu), spodní hrana {Y_BOT} mm nad terénem.</li>
<li>Panely <b>nesledují rozteč plotu</b>. Pole mají 2 210–2 330 mm, panel s mezerou 1 782 mm, takže by se nikdy nekryly. Konstrukce má vlastní rastr a sloupky FV stojí uprostřed polí plotu, ≥ 0,5 m od jeho sloupků a patek.</li>
<li>Posledních ≈ 2,7 pole plotu (≈ 6,2 m) u stromu zůstává volných. Tkaninu tam lze ponechat.</li>
<li><b>Jeden string {N_PANEL} panelů</b> na samostatný MPPT: Voc při −25 °C ≈ <b>{fmt(STR['voc_cold'])} V</b> (pod 1 000 V), Vmp při 70 °C ≈ {fmt(STR['vmp_hot'])} V (nad 160 V), proud ≈ {PANEL['Isc']} A (limit MPPT 36 A). Pokud by pole za stromem chtěl uživatel osadit, vejdou se nejvýš 2 panely navíc, tedy 21 panelů a Voc ≈ {fmt(STR['voc_cold'] / N_PANEL * 21)} V. Absolutní max. vstupní napětí ověřit v datovém listu.</li>
<li>Pod panely zůstává mezera {Y_BOT} mm. Pokud má plot dál bránit výhledu, nechá se dole pruh původní tkaniny.</li>
</ul>
</section>

<section>
<h2>Předběžné statické posouzení</h2>
<h3>Zatížení větrem (ČSN EN 1991-1-4 + NA)</h3>
<div class="calc">
v<sub>b,0</sub> = 25 m/s (větrná oblast II, ověřit v mapě NA) · c<sub>dir</sub> = c<sub>season</sub> = 1 → q<sub>b</sub> = {fmt(W['qb'])} Pa<br>
kategorie terénu II (louka, sad – konzervativně), z = max(h; z<sub>min</sub>) = {W['z']:.1f} m · c<sub>r</sub> = {W['cr']:.3f} · c<sub>o</sub> = 1,0 · I<sub>v</sub> = {W['Iv']:.3f}<br>
<b>q<sub>p</sub> = {fmt(W['qp'])} Pa</b><br>
volně stojící stěna (čl. 7.4.1, tab. 7.9), plná φ = 1, l/h = {fmt(W['lh'], 1)} ≥ 10, bez nároží:<br>
{zones_txt}<br>
Čistý tlak působí oběma směry: zepředu (od souseda) tlačí panel na profily, zezadu (od zahrady) ho odtrhuje od svorek. Rozhoduje zadní směr.<br>
Sníh: na svislé ploše se neukládá. Řeší se jen navátý nebo nahrnutý sníh u spodní hrany ({Y_BOT} mm), takže sníh od panelů neodhrnovat.
</div>
<h3>Panely a svorky</h3>
<div class="calc">
plošně průměrný tlak na panel: max. {fmt(max(st['panel_p']), 2)} kPa (krajní panel), běžně {fmt(min(st['panel_p']), 2)} kPa<br>
návrhová únosnost panelu zezadu typ. {PANEL['zad_zkus']} / 1,5 = 1,60 kPa → <b>vyhoví</b>, pokud výrobce povoluje upnutí na dlouhých hranách s profily rovnoběžnými s dlouhou hranou (ověřit v montážním návodu)<br>
síla na svorku (4 ks/panel, ULS): {fmt(st['clamp_Ed'], 2)} kN
</div>
<h3>Nosné profily (spojitý nosník, MKP)</h3>
<div class="calc">
2 profily Al 40×40, každý nese ½ výšky panelu = {PANEL['B'] / 2:.0f} mm, podpory = sloupky FV<br>
M<sub>max,k</sub> = {fmt(st['fe']['Mmax'], 3)} kNm → M<sub>Ed</sub> = {fmt(st['MEd_rail'], 3)} kNm → potřebný W<sub>el</sub> ≥ <b>{fmt(st['Wreq'], 1)} cm³</b> (f<sub>0</sub> = 160 MPa, γ<sub>M1</sub> = 1,1)<br>
průhyb (I = 11 cm⁴ předpoklad) max. {fmt(st['fe']['defl'], 1)} mm
</div>
<h3>Sloupky a vruty</h3>
<p>Sloupek {POST['nazev']}: W<sub>pl</sub> = {fmt(st['Wpl'] / 1000, 1)} cm³, M<sub>pl,Rd</sub> = {fmt(st['Mpl'], 2)} kNm. Síly jsou reakce spojitých profilů. γ<sub>Q</sub> = 1,5. H<sub>k</sub> působí na rameni ≈ {(RAIL_Y[0] + RAIL_Y[1]) / 2000:.2f} m nad terénem.</p>
<div class="tw"><table>
<tr><th class=n>Sloupek</th><th class=n>x mm</th><th>Zóna</th><th class=n>H<sub>k</sub> kN</th><th class=n>M<sub>k</sub> kNm (terén)</th><th class=n>M<sub>Ed</sub> vrut kNm</th><th class=n>Využití sloupku</th><th class=n>Posun vrchu mm</th></tr>
{post_rows}
</table></div>
<div class="calc">
max. využití sloupku {fmt(urmax * 100)} % → <b>vyhoví</b> · patka 4× M12 8.8: F<sub>t,Ed</sub> = {fmt(st['bolt']['Ft'], 1)} kN ≤ F<sub>t,Rd</sub> = {fmt(st['bolt']['FtRd'], 1)} kN → vyhoví<br>
<b>Požadavek na vrut (zadání pro dodavatele):</b> H<sub>k</sub> = {fmt(pmax['H_k'], 2)} kN ve výšce {(RAIL_Y[0] + RAIL_Y[1]) / 2000:.2f} m, M<sub>k</sub> v terénu = {fmt(pmax['M_k'], 2)} kNm, M<sub>Ed</sub> = {fmt(pmax['M_Ed_vrut'], 2)} kNm, tah zanedbatelný (svislá plocha)<br>
Vrut Ø76×1600 je v soudržné zemině obvykle dostačující. V kamenitém flyši nebo navážce musí únosnost potvrdit zkouška; pokud nevyhoví, použít Ø89×2000 nebo vrtanou patku Ø250×1200.<br>
celková vodorovná síla na stěnu H<sub>k</sub> = {fmt(st['H_total'], 1)} kN
</div>
<h3>Co musí statik ověřit nebo doplnit</h3>
<ul>
<li>větrnou oblast a kategorii terénu podle mapy NA a vliv orografie (pozemek ve svahu nad údolím, c<sub>o</sub> může být &gt; 1)</li>
<li>únosnost vrutů v místní zemině: zkouška min. na 2 vrutech, nejlépe krajních</li>
<li>průřezové charakteristiky zvoleného Al profilu a upínací konfiguraci podle návodu výrobce panelu</li>
<li>posun hlavy vrutu a natočení. Konstrukce nemá vzpěry (není na ně místo), takže tuhost závisí jen na vrutu</li>
</ul>
</section>

<section>
<h2>Výkresy</h2>
<div class="legend"><span><i class="sw" style="border-color:var(--fg)"></i>konstrukce</span><span><i class="sw" style="border-color:var(--muted);border-top-style:dashed"></i>skryté hrany</span><span><i class="sw" style="border-color:var(--fence)"></i>stávající plot</span><span><i class="sw" style="border-color:var(--bad);border-top-style:dashed"></i>hranice pozemku</span><span><i class="sw" style="border-color:var(--dim)"></i>kóty v mm</span></div>
{sheets_html}
<p>Výkres 5 (svažitý terén) není potřeba, protože linie plotu je v rovině. Lokální nerovnosti do ±100 mm se vyrovnají hloubkou zavrtání. Všechny výkresy jsou i v editovatelném DXF (R12, mm 1:1, hladiny OBRYS, PANEL, OCEL, PROFIL, PLOT, TEREN, KOTY, SKRYTE, HRANICE) v projektové složce: <span class="mono">plot-fve/dxf/plot-fve.dxf</span>.</p>
</section>

<section>
<h2>Materiál a rozpočet</h2>
<p>Ceny jsou v Kč s DPH pro soukromou osobu. „Ověřeno“ znamená, že cenu potvrdila nabídka českého obchodu (říjen 2026). Ostatní jsou odhady, které je potřeba poptat.</p>
<div class="tw"><table>
<tr><th>Položka</th><th>Specifikace</th><th>Materiál</th><th>Rozměr</th><th class=n>ks</th><th class=n>Kč/ks</th><th class=n>Kč</th><th>Cena</th></tr>
{bom_rows}
<tfoot><tr><td colspan=6>Celkem konstrukce, kotvení, spojovací materiál a montáž</td><td class=n>{fmt(tot)}</td><td></td></tr></tfoot>
</table></div>
<div class="tw"><table>
<tr><th>Skupina</th><th class=n>Kč</th><th class=n>Kč/kWp</th></tr>
{sum_rows}
<tfoot><tr><td>Celkem</td><td class=n>{fmt(tot)}</td><td class=n>{fmt(tot / STR['kWp'])}</td></tr></tfoot>
</table></div>
<p><b>Mimo rozpočet konstrukce:</b> panely ({N_PANEL} × ≈ 2 000 Kč, tedy ≈ {fmt(N_PANEL * 2000)} Kč, odhad), DC kabeláž ke střídači (délka zatím neznámá), elektromontáž a revize (≈ 8 000 Kč), vytyčení hranice geodetem (≈ 6 000 Kč). Úspora při svépomoci: montáž ≈ 12 000 Kč. Vruty lze zavrtat i ručně s pronajatým nářadím, ale bez stroje je těžké dodržet svislost a hloubku v kamenité zemině.</p>
</section>

<section>
<h2>Montážní postup</h2>
<ol class="steps">
<li><b>Příprava:</b> vytyčení hranice geodetem a domluva se sousedem (montáž půjde jen z jeho strany). Ohlášení a souhlas stavebního úřadu podle bodu Předpisy. Sundat tkaninu v osazovaném úseku.</li>
<li><b>Vytyčení os sloupků:</b> šňůra 100 mm od osy plotu. Sloupky FV uprostřed polí plotu, v krajních polích 2 ks 500 mm od sloupků plotu. Polohu ±150 mm přizpůsobit patkám plotu a kamenům. Ověřit sítě v zemi (kabely, voda).</li>
<li><b>Vruty:</b> strojně, svisle (odchylka ≤ 1°), hlava 100 mm nad terénem, všechny příruby do jedné výšky ±10 mm (nivelace laserem). Zatěžovací zkouška 2 vrutů. Při narážení na kámen předvrtat nebo posunout.</li>
<li><b>Sloupky:</b> přišroubovat 4× M12 na přírubu, vyrovnat do svislice (podložky), horní hrany do jedné výšky 1 500 mm. Nasadit záslepky.</li>
<li><b>Držáky a profily:</b> úhelníky na sloupky, profily vodorovně v osách {RAIL_Y[0]} a {RAIL_Y[1]} mm. Dilatační spojky v mezerách za 6. a 13. panelem, ostatní spoje pevné. Profily nesmí přesahovat sloupek o více než 300 mm.</li>
<li><b>Pospojování:</b> Cu 6 mm² mezi všemi sloupky a jedním profilem každé řady, připojit k hlavní ochranné přípojnici (HOP) domu. Svorky s nerezovými podložkami (Al/Zn).</li>
<li><b>Panely:</b> od jednoho konce, koncové svorky na dlouhých hranách v upínací zóně podle návodu výrobce, moment podle výrobce svorky. Konektory MC4 propojit hned za panely, kabely vázat UV odolnými pásky k profilu, bez průvěsu.</li>
<li><b>Kabeláž ke střídači:</b> H1Z2Z2-K 6 mm², od plotu v chráničce KOPOFLEX 40 v hloubce ≥ 0,7 m s výstražnou fólií. Na konstrukci kabely za panely, mimo dosah osob a zvířat. Označit „FV – DC napětí“.</li>
<li><b>Zapojení a revize:</b> elektrikář připojí string na volný MPPT SolaxU, proměří Voc, Isc a izolační odpor a vystaví revizní zprávu.</li>
<li><b>Kontrola po 1. zimě:</b> dotažení šroubů, svislost sloupků, poškození zinku a kabelů.</li>
</ol>
</section>

<section>
<h2>Elektro, předpisy a bezpečnost</h2>
<div class="grid2">
<div class="card"><h3>Distributor (ČEZ Distribuce)</h3><p>Přidáním {fmt(STR['kWp'], 2)} kWp se mění instalovaný výkon výrobny. Podat žádost o změnu nebo oznámení a doložit novou revizi. Rezervovaný výkon se nemění, pokud zůstává stejný střídač. Postup ověřit v portálu distributora před nákupem.</p></div>
<div class="card"><h3>Stavební úřad</h3><p>Konstrukce stojí na hranici pozemku a je vyšší než 1,5 m nad terénem jen o rámeček. Režim (bez povolení, nebo ohlášení) a nutnost souhlasu souseda ověřit u příslušného stavebního úřadu. Souhlas souseda doporučuji mít písemně v každém případě.</p></div>
<div class="card"><h3>Bezpečnost v dosahu osob</h3><ul><li>Panely ve výšce 0,37–1,5 m jsou na dosah z pozemku souseda: sklo může rozbít míč nebo kámen, DC kabely nesmí být přístupné.</li><li>Pospojování konstrukce podle ČSN 33 2000-7-712.</li><li>Žádné ostré hrany: záslepky, zaoblené konce profilů.</li></ul></div>
<div class="card"><h3>Koroze</h3><p>Ocel žárově zinkovaná (sloupky po svaření), spojovací materiál žár. Zn nebo nerez A2. Hliník od zinku oddělit podložkou z nerezu nebo EPDM. Řezy a vrtání opravit zinkovým sprejem. Spodní hrana 366 mm a hlava vrutu 100 mm nad terénem chrání před vlhkostí a sekačkou.</p></div>
</div>
</section>

<section>
<h2>Otevřené body</h2>
<ul>
<li>Typ panelu: rozměry, Voc, zadní zatížitelnost a <b>povolená upínací konfigurace</b> (dlouhé hrany, profily rovnoběžně s dlouhou hranou). Případně bifaciální sklo-sklo.</li>
<li>Vytyčení hranice: od čeho se 30 cm měří (osa, nebo líc pletiva)?</li>
<li>Zemina v pásu za plotem: kamenitá, nebo hlinitá? Zkouška vrutů.</li>
<li>Vzdálenost od plotu ke střídači a trasa kabelu.</li>
<li>Kolik polí u stromu přesně vynechat. Lze ověřit fotkou plotu v zimě kolem poledne.</li>
</ul>
</section>
<footer>Zdroje: PVGIS 5.2 (JRC), ČSN EN 1991-1-4 + NA, ČSN EN 1993-1-1, ČSN EN 1999-1-1, datová stránka SolaX X3-Ultra, cena profilu: zbozi.cz (G21 HPG2144X). Výpočet a výkresy generuje <span class="mono">plot-fve/src/navrh.py</span>.</footer>
</main>"""


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "dxf"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "vystup"), exist_ok=True)
    write_dxf(os.path.join(ROOT, "dxf", "plot-fve.dxf"))
    with open(os.path.join(ROOT, "navrh.html"), "w", encoding="utf-8") as f:
        f.write(html())
    summ = dict(wind={k: v for k, v in W.items() if k not in ("zones",)}, posts=S["posts"], rail_Mmax=S["fe"]["Mmax"],
                Wreq=S["Wreq"], panel_p_max=max(S["panel_p"]), fence=S["fence"], string=STR,
                L_wall=L_WALL, posts_x=POSTS, bom_total=sum(r["celk"] for r in BOM))
    with open(os.path.join(ROOT, "vystup", "statika.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, ensure_ascii=False, indent=1, default=float)
    print(f"qp={W['qp']:.0f} Pa  posts={len(POSTS)}  L={L_WALL}  Voc_cold={STR['voc_cold']:.0f} V")
    for p in S["posts"]:
        print(f"  x={p['x']:6d} {p['zona']} H={p['H_k']:.2f} Mk={p['M_k']:.2f} MEd={p['M_Ed_vrut']:.2f} UR={p['UR']:.2f} d={p['d_top']:.0f}")
    print(f"rail Mmax_k={S['fe']['Mmax']:.3f} Wreq={S['Wreq']:.2f} cm3 defl={S['fe']['defl']:.1f}  panel_p={max(S['panel_p']):.2f}")
    print(f"fence UR={S['fence']['UR']:.2f}  bolt {S['bolt']['Ft']:.1f}/{S['bolt']['FtRd']:.1f}  BOM={summ['bom_total']}")
