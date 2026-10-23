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
# Kandidáti 1 762 × 1 134 mm (údaje z datových listů a montážních návodů výrobců, 10/2026).
# Všichni povolují upnutí na dlouhých hranách jen s profily KOLMO na dlouhou hranu.
# zad_navrh = návrhové zatížení zezadu (sání) po součiniteli 1,5; A = poloha svorky od kratší hrany.
PANELS = {
    "JA": dict(nazev="JA Solar JAM54D40-450/LB", typ="bifaciální sklo-sklo, n-TOPCon", L=1762, B=1134, t=30,
               Wp=450, kg=22.0, Voc=39.3, Vmp=32.82, Isc=14.48, tk_voc=-0.25, tk_vmp=-0.29,
               zad_navrh=1600, A=(390, 490), cena=2300,
               zdroj="JA Solar Bifacial Double-glass Installation Manual (2024), tab. Clamps, rails cross the long frame"),
    "AIKO": dict(nazev="AIKO Neostar 2P A465-MAH54Mw", typ="jednostranný, sklo-fólie, ABC (zadní kontakty)", L=1757, B=1134, t=30,
                 Wp=465, kg=21.0, Voc=41.12, Vmp=34.68, Isc=14.29, tk_voc=-0.24, tk_vmp=-0.29,
                 zad_navrh=1600, A=(310, 410), cena=2900,
                 zdroj="AIKO Mono glass Installation Manual v1.1, clamp mounting on long frame (+5400/−2400 Pa zkušební)"),
    "TRINA": dict(nazev="Trina Vertex S+ TSM-440NEG9RC.27", typ="bifaciální sklo-sklo, n-TOPCon", L=1762, B=1134, t=30,
                  Wp=440, kg=21.0, Voc=52.2, Vmp=44.0, Isc=10.67, tk_voc=-0.24, tk_vmp=-0.29,
                  zad_navrh=2667, A=(300, 350), cena=2300,
                  zdroj="Trina Vertex User Manual UM-M-0002 L (08/2024), A-surface clamp, rails perpendicular (−4000/+5400 Pa zkušební)"),
}
VYBER = "JA"
PANEL = PANELS[VYBER]
N_PANEL = 19
GAP = 20                     # mezera mezi panely [mm]
Y_TOP = 1500                 # horní hrana panelů = výška plotu
Y_BOT = Y_TOP - PANEL["B"]   # 366
RAIL = 40                    # Al profil 40×40
RAIL_Y = (Y_BOT + 60, Y_TOP - 60)   # osy vodorovných nosníků (spodní vrstva)
VR_A = sum(PANEL["A"]) / 2          # svislé profily (horní vrstva) od kratší hrany panelu
VR_EXT = 45                         # přesah svislého profilu za hranu panelu (pro svorku)
FIELD = 2270                 # schematická rozteč sloupků plotu (skutečně 2 210–2 330)
X_POST_PLOT = 100            # osa sloupku FV od osy plotu (ven)
POST = dict(b=60, t=4, fy=235, nazev="jekl 60×60×4, S235, žár. Zn")
# hloubková skladba od osy plotu: sloupek | vodorovný nosník | svislý profil | panel | svorka
X_POST_F = X_POST_PLOT + POST["b"] / 2
X_BEAM = (X_POST_F, X_POST_F + RAIL)
X_VR = (X_BEAM[1], X_BEAM[1] + RAIL)
X_PAN = (X_VR[1], X_VR[1] + 30)
X_CLAMP = X_PAN[1] + 10
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
def vr_positions():
    """Svislé profily: 2 na panel ve vzdálenosti A od kratších hran."""
    return [(i, i * PITCH + a) for i in range(N_PANEL) for a in (VR_A, PANEL["L"] - VR_A)]


def panel_pressure(i):
    xs = np.linspace(i * PITCH, i * PITCH + PANEL["L"], 50)
    return float(np.mean([w_at(x) for x in xs]))


def rail_fe():
    """Vodorovný nosník = spojitý nosník na sloupcích, zatížený bodově od svislých profilů."""
    E, I = 70000.0, 11.0e4                     # Al 6063-T6, I ≈ 11 cm⁴ (40×40, ověřit u výrobce)
    vrs = vr_positions()
    grid = set(np.arange(0, L_WALL + 1, 20.0).round(1)) | {round(p, 1) for p in POSTS} | {L_WALL} \
        | {round(x, 1) for _, x in vrs}
    xs = np.array(sorted(grid))
    n = len(xs)
    K = np.zeros((2 * n, 2 * n)); F = np.zeros(2 * n)
    for i, x in vrs:                            # P/4 na každý styk svislý profil × nosník
        P = panel_pressure(i) * PANEL["L"] * PANEL["B"] / 1e6 * 1000    # N
        F[2 * int(np.argmin(abs(xs - round(x, 1))))] += P / 4
    for e in range(n - 1):
        l = xs[e + 1] - xs[e]
        k = E * I / l ** 3 * np.array([[12, 6 * l, -12, 6 * l], [6 * l, 4 * l * l, -6 * l, 2 * l * l],
                                        [-12, -6 * l, 12, -6 * l], [6 * l, 2 * l * l, -6 * l, 4 * l * l]])
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(idx, idx)] += k
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
        f = k @ u[2 * e:2 * e + 4]
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
    pp = [panel_pressure(i) for i in range(N_PANEL)]
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
def string(p=PANEL, n=N_PANEL):
    voc1 = p["Voc"] * (1 + p["tk_voc"] / 100 * (-25 - 25))       # −25 °C
    n_max = int(1000 * 0.98 // voc1)                             # 2 % rezerva pod 1 000 V
    n = min(n, n_max)
    vmp_hot = p["Vmp"] * (1 + p["tk_vmp"] / 100 * (70 - 25)) * n
    return dict(n=n, n_max=n_max, kWp=n * p["Wp"] / 1000, voc_cold=voc1 * n, vmp_hot=vmp_hot, vmp_stc=p["Vmp"] * n)


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
    pb = POST["b"]
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
    # svislé profily (horní vrstva) – přesahují panel o VR_EXT nahoře i dole
    for _, x in vr_positions():
        if x_from < x < x_to:
            s.rect(x - RAIL / 2, Y_BOT - VR_EXT, RAIL, VR_EXT, "ink", "rail")
            s.rect(x - RAIL / 2, Y_TOP, RAIL, VR_EXT, "ink", "rail")
            s.line(x - RAIL / 2, Y_BOT, x - RAIL / 2, Y_TOP, "hidden")
            s.line(x + RAIL / 2, Y_BOT, x + RAIL / 2, Y_TOP, "hidden")
    # vodorovné nosníky (skryté), dilatace
    for y in RAIL_Y:
        s.line(max(x_from, 0), y, min(x_to, L_WALL), y, "hidden")
    for d in DIL:
        if x_from < d < x_to:
            s.line(d, Y_BOT - 150, d, Y_TOP + 150, "accent")
            s.text(d, Y_TOP + 200, "dilatace nosníků", "note", th * .7)
    # sloupky + vruty
    for x in POSTS:
        if not (x_from < x < x_to):
            continue
        s.rect(x - pb / 2, HEAD, pb, Y_BOT - VR_EXT - HEAD, "steel", "steel")
        s.rect(x - pb / 2, Y_BOT - VR_EXT, pb, Y_TOP - Y_BOT + VR_EXT, "hidden")
        s.rect(x - 38, -VRUT["L"] + HEAD, 76, VRUT["L"] - HEAD, "hidden")
    if detail:
        s.dimh(0, PANEL["L"], Y_TOP + 380, ext=Y_TOP + VR_EXT)
        s.dimh(PANEL["L"], PITCH, Y_TOP + 380, "20")
        s.dimh(PITCH, PITCH + PANEL["L"], Y_TOP + 380, ext=Y_TOP + VR_EXT)
        s.dimh(0, VR_A, Y_TOP + 200, ext=Y_TOP + VR_EXT)
        s.dimh(VR_A, PANEL["L"] - VR_A, Y_TOP + 200, ext=Y_TOP + VR_EXT)
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
        s.dimv(RAIL_Y[0], RAIL_Y[1], x_to - 300, ext=L_WALL if x_to > L_WALL else x_to - 400)
        s.text(x_from + 900, -VRUT["L"] / 2, "zemní vrut Ø76×1600", "note", anchor="start")
        s.text(POSTS[0] + 50, HEAD + 40, f"sloupek {pb}×{pb}×{POST['t']}", "note", anchor="start")
        s.text(x_to - 50, -VRUT["L"] - 300, "osy sloupků FV", "note", anchor="end")
        s.text(x_to - 50, -VRUT["L"] - 700, "rozteč plotu (skutečná)", "note", anchor="end")
    else:
        s.dimh(0, L_WALL, Y_TOP + 900, ext=Y_TOP)
        s.dimh(L_WALL, 40000, Y_TOP + 900, ext=SITE["plot_vyska"])
        s.text((L_WALL + 40000) / 2, Y_TOP + 350, "vynecháno – stín stromu", "note", th * .8)
        s.dimh(0, 40000, Y_TOP + 1700, "plot ≈ 40 000", ext=Y_TOP + 900)
        s.dimv(0, Y_TOP, -400, ext=0)
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
    pb = POST["b"]
    s.line(-700, 0, 900, 0, "ground")
    for x in range(-650, 900, 120):
        s.line(x, 0, x - 60, -60, "ground")
    s.text(-450, 1700, "ZAHRADA (uvnitř)", "note", anchor="middle")
    s.text(620, 1700, "SOUSED", "note", anchor="middle")
    # plot
    s.rect(-24, -800, 48, 800 + SITE["plot_vyska"], "fence")
    s.rect(-25, -50, 50, 250, "fence", "conc")
    s.text(-60, 120, "podhrabová deska", "note", 22, "end")
    s.text(-60, 1350, "sloupek plotu (stávající)", "note", 22, "end")
    s.text(-60, 1300, "pletivo, tkanina odstraněna", "note", 22, "end")
    s.line(SITE["pas"], -1900, SITE["pas"], 1950, "border")
    s.text(SITE["pas"] + 20, 1850, "hranice pozemku (vytyčit)", "note", 22, "start")
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
    top_post = RAIL_Y[1] + 60
    s.rect(x - pb / 2, HEAD + 8, pb, top_post - HEAD - 8, "steel", "steel")
    s.rect(x - pb / 2, top_post, pb, 6, "ink", "ink")
    # vodorovné nosníky na úhelnících, svislý profil, panel, svorky
    for y in RAIL_Y:
        s.rect(X_BEAM[0], y - 30, 4, 60, "ink", "ink")
        s.rect(X_BEAM[0] + 4, y - RAIL / 2, RAIL - 4, RAIL, "ink", "rail")
    s.rect(X_VR[0], Y_BOT - VR_EXT, RAIL, PANEL["B"] + 2 * VR_EXT, "ink", "rail")
    s.rect(X_PAN[0], Y_BOT, PANEL["t"], PANEL["B"], "ink", "panel")
    for y, sgn in ((Y_TOP, 1), (Y_BOT, -1)):
        s.rect(X_PAN[0], y if sgn > 0 else y - 8, X_CLAMP - X_PAN[0], 8, "ink", "ink")
        s.rect(X_PAN[1], y - 14 if sgn > 0 else y + 6, 10, 8, "ink", "ink")
    s.text(X_CLAMP + 40, 900, "FV panel naležato", "note", 22, "start")
    s.text(X_CLAMP + 40, 860, f"{PANEL['L']}×{PANEL['B']}×{PANEL['t']}", "note", 22, "start")
    s.text(x + 60, -900, f"zemní vrut Ø{VRUT['d']}×{VRUT['L']}", "note", 22, "start")
    s.text(x + 60, -940, "s přírubou, žár. Zn", "note", 22, "start")
    s.text(-60, RAIL_Y[1] + 10, "vodorovný nosník 40×40", "note", 22, "end")
    s.text(-60, RAIL_Y[1] - 30, f"svislý profil 40×40, l = {PANEL['B'] + 2 * VR_EXT}", "note", 22, "end")
    s.text(-60, 700, f"sloupek {pb}×{pb}×{POST['t']}", "note", 22, "end")
    # kóty
    s.dimh(0, x, -1750, ext=-VRUT["L"] + HEAD)
    s.dimh(0, X_CLAMP, 1950, ext=Y_TOP + VR_EXT)
    s.dimh(0, SITE["pas"], 2060, ext=1950)
    s.dimh(X_POST_F, X_PAN[1], 1800, ext=Y_TOP + VR_EXT)
    s.dimv(0, Y_BOT, 720, ext=X_CLAMP)
    s.dimv(Y_BOT, Y_TOP, 720)
    s.dimv(0, Y_TOP, 840, ext=X_CLAMP)
    s.dimv(-VRUT["L"] + HEAD, 0, -300, ext=x - 38)
    s.dimv(0, HEAD, -300)
    s.dimv(RAIL_Y[0], RAIL_Y[1], 560, ext=X_BEAM[1])
    s.text(150, -2050, f"sklon 90° · azimut {SITE['azimut']}°", "note", 26)
    return s


def sheet_plan():
    s = Sheet("Výkres 3 – půdorys (výřez 0–8 m)", 85)
    X1 = 8200
    pb = POST["b"]
    s.line(-400, 0, X1, 0, "fence")
    for k in range(5):
        s.circle(k * FIELD, 0, 24, "fence")
    s.rect(-400, -25, X1 + 400, 50, "fence")
    s.line(-400, -SITE["pas"], X1, -SITE["pas"], "border")
    s.text(X1 - 50, -SITE["pas"] - 110, "hranice pozemku (30 cm za osou plotu – vytyčit)", "note", anchor="end")
    s.text(X1 - 50, 160, "plot (stávající, osa)", "note", anchor="end")
    for x in [p for p in POSTS if p < X1]:
        s.rect(x - pb / 2, -X_POST_F, pb, pb, "steel", "steel")
        s.circle(x, -X_POST_PLOT, 38, "hidden")
    for y in (-X_BEAM[0], -X_BEAM[1]):
        s.line(0, y, X1, y, "hidden")
    for _, x in vr_positions():
        if x < X1:
            s.rect(x - RAIL / 2, -X_VR[1], RAIL, RAIL, "ink", "rail")
    for i in range(5):
        x = i * PITCH
        s.rect(x, -X_PAN[1], min(PANEL["L"], X1 - x), PANEL["t"], "ink", "panel")
    prev = 0
    for x in [p for p in POSTS if p < X1]:
        s.dimh(prev, x, -800, ext=-X_POST_F)
        prev = x
    s.dimh(0, PANEL["L"], -1150, ext=-X_PAN[1])
    s.dimv(-X_POST_PLOT, 0, -250, ext=POSTS[0])
    s.dimv(-SITE["pas"], 0, -500)
    cx, cy, r = X1 - 600, 900, 300
    a = math.radians(30)
    s.line(cx - r * math.sin(a), cy - r * math.cos(a), cx + r * math.sin(a), cy + r * math.cos(a), "ink")
    s.line(cx + r * math.sin(a), cy + r * math.cos(a), cx + r * math.sin(a) - 90, cy + r * math.cos(a) - 90, "ink")
    s.text(cx + (r + 90) * math.sin(a), cy + (r + 90) * math.cos(a), "S", "ptxt2")
    s.text(cx, cy - r - 160, "panely → 150° (JJV)", "note")
    s.text(3000, 1000, "ZAHRADA", "note")
    s.text(3000, -1650, "POZEMEK SOUSEDA", "note")
    return s


def sheet_details():
    s = Sheet("Výkres 4 – konstrukční detaily", 13)
    pb = POST["b"]
    # D1 patka: příruba vrutu + patní deska + 4×M12
    ox, oy = 0, 0
    s.rect(ox - 38, oy - 220, 76, 212, "steel", "steel")
    s.rect(ox - 70, oy - 8, 140, 8, "steel", "steel")
    s.rect(ox - 80, oy, 160, 8, "steel", "steel")
    s.rect(ox - pb / 2, oy + 8, pb, 220, "steel", "steel")
    for bx in (-60, 60):
        s.rect(ox + bx - 6, oy - 20, 12, 40, "ink", "ink")
    s.line(ox - 160, oy - 100, ox + 160, oy - 100, "ground")
    s.dimh(ox - 80, ox + 80, oy + 260, ext=oy + 8)
    s.dimh(ox - 60, ox + 60, oy - 260, ext=oy - 20)
    s.text(ox, oy + 300, "D1 – kotvení sloupku na vrut", "h")
    s.text(ox + 95, oy + 20, "patní deska P8 160×160", "note", anchor="start")
    s.text(ox + 95, oy - 6, "příruba vrutu (dle výrobce)", "note", anchor="start")
    s.text(ox + 95, oy - 32, "4× M12 8.8 žár. Zn", "note", anchor="start")
    s.text(ox + 95, oy + 160, f"jekl {pb}×{pb}×{POST['t']}, svar dokola a4", "note", anchor="start")
    # D2 půdorysný řez: sloupek – úhelník – vodorovný nosník – svislý profil – panel
    ox = 520
    s.rect(ox - pb / 2, -pb / 2, pb, pb, "steel", "steel")
    s.rect(ox - pb / 2 - 5, -pb / 2 - 5, 5, pb + 5, "ink", "ink")
    s.rect(ox - pb / 2 - 5, -pb / 2 - 5, pb + 45, 5, "ink", "ink")
    s.rect(ox + pb / 2, -pb / 2 + 10, 40, 40, "ink", "rail")
    s.rect(ox + pb / 2 + 40, -pb / 2 + 10, 40, 40, "ink", "rail")
    s.rect(ox + pb / 2 + 80, -pb / 2 - 30, 30, 120, "ink", "panel")
    s.line(ox - pb, 0, ox + pb / 2 + 20, 0, "hidden")
    s.dimh(ox - pb / 2, ox + pb / 2, -110, ext=-pb / 2)
    s.dimh(ox + pb / 2, ox + pb / 2 + 40, -110, ext=-pb / 2 + 10)
    s.dimh(ox + pb / 2 + 40, ox + pb / 2 + 80, -110, ext=-pb / 2 + 10)
    s.dimh(ox + pb / 2 + 80, ox + pb / 2 + 110, -110, ext=-pb / 2 - 30)
    s.text(ox + 40, 300, "D2 – skladba v půdorysu", "h")
    s.text(ox + 40, 170, "úhelník L50×50×5, l = 80, 1× M10 do sloupku", "note")
    s.text(ox + 40, 148, "vodorovný nosník: T-šroub M8, otvor oválný", "note")
    s.text(ox + 40, 126, "svislý profil: křížový spojovač na nosník", "note")
    # D3 křížový spoj + koncová svorka na dlouhé hraně
    ox = 1080
    s.rect(ox, -20, 40, 40, "ink", "rail")
    s.rect(ox + 40, -120, 40, 260, "ink", "rail")
    s.rect(ox + 36, -32, 48, 6, "accent")
    s.rect(ox + 80, -120 + VR_EXT, 30, 215, "ink", "panel")
    s.rect(ox + 80, 95, 40, 6, "ink", "ink")
    s.rect(ox + 110, 81, 10, 14, "ink", "ink")
    s.dimh(ox + 80, ox + 110, -150, ext=-75)
    s.dimv(95, 140, ox + 150, str(VR_EXT), ext=ox + 80)
    s.text(ox + 60, 300, "D3 – křížový spoj a svorka", "h")
    s.text(ox + 60, 200, "svislý profil přes vodorovný nosník", "note")
    s.text(ox + 60, 178, "4 koncové svorky / panel na dlouhých hranách", "note")
    s.text(ox + 60, 156, f"A = {PANEL['A'][0]}–{PANEL['A'][1]} mm od kratší hrany", "note")
    # D4 dilatace nosníku
    ox = 1520
    s.rect(ox, -20, 200, 40, "ink", "rail")
    s.rect(ox + 220, -20, 200, 40, "ink", "rail")
    s.rect(ox + 120, -26, 180, 52, "accent")
    for bx in (150, 270):
        s.rect(ox + bx - 12, -5, 24, 10, "ink")
    s.dimh(ox + 200, ox + 220, -90, "20", ext=-20)
    s.dimh(ox + 120, ox + 300, 90, ext=26)
    s.text(ox + 210, 300, "D4 – dilatační spoj nosníku", "h")
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
        ("Nosná konstrukce", "Sloupek s patní deskou", "jekl 60×60×4 + P8 160×160, 4 otvory Ø14, 2 otvory Ø11 pro držáky, svar a4, žárový zinek", "S235", "l = 1 400 mm", n, 950, False),
        ("Nosná konstrukce", "Vodorovný nosník (spodní vrstva)", "Al profil 40×40 s drážkou (např. G21 HPG2144X), W ≥ 3 cm³", "Al 6063-T6", "6 000 mm", rail_bars, 1070, True),
        ("Nosná konstrukce", "Svislý profil (horní vrstva)", f"Al profil 40×40, nařezat 2 ks/panel = {2 * N_PANEL} ks à {PANEL['B'] + 2 * VR_EXT} mm (4 ks z tyče)", "Al 6063-T6", "6 000 mm", math.ceil(2 * N_PANEL / 4), 1070, True),
        ("Nosná konstrukce", "Křížový spojovač", "profil na profil 40×40, s T-šroubem M8", "Al + nerez", "—", 4 * N_PANEL, 65, False),
        ("Nosná konstrukce", "Držák profilu", "úhelník L50×50×5 s oválným otvorem", "S235 žár. Zn", "l = 80 mm", 2 * n, 80, False),
        ("Nosná konstrukce", "Spojka profilu pevná", "pro profil 40×40", "Al", "—", 8, 120, False),
        ("Nosná konstrukce", "Spojka profilu dilatační", "s oválnými otvory", "Al", "—", 4, 250, False),
        ("Nosná konstrukce", "Záslepka sloupku", "PE 60×60", "PE", "—", n, 25, False),
        ("Kotvení", f"Zemní vrut s přírubou", f"Ø{VRUT['d']}×{VRUT['L']} mm, příruba 4× M12, rozteč děr 120 mm", "S235 žár. Zn", f"{VRUT['L']} mm", n, 1200, False),
        ("Kotvení", "Strojní zavrtání vrutů", "vč. dopravy stroje, předvrtání v kamenité zemině", "služba", "—", n, 300, False),
        ("Kotvení", "Zatěžovací zkouška vrutu", "2 ks, vodorovná síla dle tab. statiky", "služba", "—", 1, 2500, False),
        ("Spojovací materiál", "Koncová svorka panelu", "pro rám 30 mm, délka ≥ 50 mm, tl. ≥ 4 mm (dle návodu výrobce panelu), T-šroub M8", "Al + nerez", "—", 4 * N_PANEL, 45, False),
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

# ---------------------------------------------------------------- hotové systémy (rešerše 23. 10. 2026)
EUR = 24.5   # Kč/€ (orientačně)
PLN = 5.7    # Kč/zł (orientačně)
HOTOVE = [
    dict(nazev="Solarne Ogrodzenia S1", zeme="PL", url="https://solarneogrodzenia.pl/przeslo-ogrodzenie-solarne-s1-dlugosc-21mb-500w-dwustronne-bez-podmurowek-kolor",
         popis="pole 2,1 m s panelem JA Solar JAM60D41 500 W, bifaciální sklo-sklo 1953×1134, ocel 2 mm žár. Zn + prášková barva, výška 1,69–1,79 m",
         kotveni="betonové sokly (podmurówki) zvlášť", hloubka=None, cena_kc=16 * 1179 * PLN,
         cena_pozn="1 179 zł/pole vč. panelu; 16 polí = 33,6 m, 8,0 kWp; sokly zvlášť",
         plus="nejbližší obdoba německé sady, panel JA sklo-sklo, ocel Zn", minus="výška 1,7–1,8 m (vyšší než plot), panel 1 953 mm jen 16 ks, statika a kotvení neuvedeny", hodnoceni="ok", verdikt="poptat"),
    dict(nazev="Emiter Ogrodzenie PV", zeme="PL", url="https://emiter.net.pl/produkty/ogrodzenie-pv",
         popis="velkoobchod v Katovicích (≈ 80 km od Vendryně): sady vodorovného pole se sloupkem 80×80 i svislého pole (sloupek 120×120, 2× JA 440 Wp), brány a branky",
         kotveni="neuvedeno (výkres PDF na webu)", hloubka=80, cena_kc=None,
         cena_pozn="jen pro firmy (B2B platforma), přes montážní firmu",
         plus="blízko, vodorovná varianta, panely JA", minus="cena neveřejná, prodej přes instalatéry", hodnoceni="ok", verdikt="poptat"),
    dict(nazev="Kleinanzeigen „Solarzaun“ (solar.carport)", zeme="DE", url="https://www.kleinanzeigen.de/",
         popis="pole ≈ 1,9 m: panel 460 W bifaciální sklo-sklo, Al sloupek RAL 7016 výšky 135 cm (nebo 180 cm k zabetonování), patka, krytka, 4 úhelníky",
         kotveni="zabetonování nebo přišroubování na beton či zeď", hloubka=None, cena_kc=(N_PANEL * 175 + 110) * EUR,
         cena_pozn="175 €/pole vč. panelu + 110 € koncový sloupek; jen osobní odběr v Seesenu (≈ 800 km)",
         plus="nejnižší cena", minus="výška 1,35 m, datový list a statika chybí, odvoz", hodnoceni="est", verdikt="levné, ověřit"),
    dict(nazev="Green-Tech (Next2Sun styl)", zeme="PL", url="https://green-tech.com.pl/pionowe-instalacje-fotowoltaiczne/",
         popis="svislý bifaciální plot, ocelové sloupky a příčníky, panely nastojato, výška 1,5–1,8 m (1 řada)",
         kotveni="neuvedeno, montáž firmou", hloubka=None, cena_kc=None,
         cena_pozn="dodávka na klíč „od 10 000 zł za 1 kW“",
         plus="ověřený koncept pro agro-FV", minus="panely nastojato, drahé, jen montáž firmou", hodnoceni="bad", verdikt="nehodí se"),
    dict(nazev="Kirchberger SUNLINE horizontal", zeme="DE", url="https://kirchberger-metall.de/products/solarzaun-pv-zaun-modell-sunline-horizontal-komplettset-basismodul-1-modul-2-pfosten",
         popis="Al sloupek 68×68 s drážkou, osa 178 cm, bezrámový bifaciální panel sklo-sklo 435 Wp (Solitec) vložený do drážky sloupků, výška systému 127 cm, sokl 90 mm",
         kotveni="patka s deskou na přišroubování nebo zabetonování; vruty neuvádí", hloubka=70,
         cena_eur=370 + (N_PANEL - 1) * 310, cena_pozn="370 € základ + 310 € každý další, vč. panelu, bez DPH (cena pro DE)",
         plus="nejmenší hloubka, panel schválený se systémem, rychlá montáž", minus="výška 127 cm (o 23 cm níž než plot), spodní hrana nízko u země, statika neuvedena", hodnoceni="ok", verdikt="nejvhodnější"),
    dict(nazev="Profiness Solarzaun Basic quer", zeme="DE", url="https://shop.profiness.de/en/product/solarzaun-basic-quer/",
         popis="Al sloupek, prvek 1,84 m × 1,25 m, panel Jolywood JW-HD108N 1762×1134, 450 Wp bifaciální, vyráběný na zakázku",
         kotveni="sloupky k zabetonování (volba), plánování vč. statiky zdarma i mimo DE", hloubka=80,
         cena_eur=N_PANEL * 280 + 60, cena_pozn="280 €/prvek (5–35 ks) + koncový sloupek, vč. panelu",
         plus="zdarma statika pro konkrétní místo, panel 1762×1134", minus="výška 1,25 m, běžné panely nelze použít, betonové patky", hodnoceni="ok", verdikt="vhodný"),
    dict(nazev="ClickCon ClickWall", zeme="DE", url="https://clickcon.eu/solarzaun-montagesystem-clickwall/",
         popis="Al sloupky s kabelovým kanálem, panel naležato i nastojato, 1–2 panely nad sebou, pro běžné rámové panely (i bifaciální sklo-sklo)",
         kotveni="patky, pásy, zemní kotvy nebo upravené desky", hloubka=None,
         cena_eur=None, cena_pozn="online kalkulátor, cena neuvedena",
         plus="lze použít vlastní panel (např. JA)", minus="upínání panelu ani hloubka neuvedeny, nutno poptat", hodnoceni="est", verdikt="poptat"),
    dict(nazev="Firend Solarzaun horizontal", zeme="DE", url="https://www.firend24.de/product/solarzaun-2module.html",
         popis="práškově lakovaná ocel, sloupky se stojnou patkou, rozteč ≈ 1 802 mm, jen pro panely 1722×1134×30",
         kotveni="stojná patka (způsob kotvení neuveden)", hloubka=None,
         cena_eur=None, cena_pozn="129,60 € za sadu pro 2 panely, bez panelů",
         plus="velmi levná konstrukce", minus="jen panel 1722 mm, statika ani kotvení neuvedeny", hodnoceni="est", verdikt="levná varianta, rizikové"),
    dict(nazev="Plotík, ALUX/ILIOS, Svaroq, Ploty Dobrý", zeme="CZ", url="https://www.plotik.cz/",
         popis="české hliníkové solární ploty jako náhrada plotu; Plotík výška 1,2–2,2 m i svépomocí, ALUX s panely Trina, Svaroq bifaciální sklo-sklo, Ploty Dobrý s AIKO 540 Wp",
         kotveni="neuvádějí; obvykle betonové patky v linii plotu", hloubka=None,
         cena_eur=None, cena_pozn="na poptávku; ALUX uvádí sestavy 7,1 kWp za 227 000 Kč vč. střídače a montáže",
         plus="dodavatel v ČR, montáž na klíč, servis", minus="řeší se jako nový plot v linii starého, ne v pásu 30 cm; ceny na poptávku", hodnoceni="est", verdikt="poptat jako náhradu plotu"),
]


USD = 23.0   # Kč/$ (orientačně)
CINA = [
    dict(nazev="Xiamen Megan Solar (MG Solar)", url="https://mgsolar.en.made-in-china.com/product/bAiYcwHThKWa/China-Solar-Vertical-Bifacial-Fence-PV-Farms-Mounting-Systems-Fence-Ground-Mount-System.html",
         popis="svislý plot 90°, ocel Q345 žár. Zn (příp. ZnAlMg), panely naležato i nastojato, jedno- i oboustranné",
         kotveni="beton, beraněné piloty nebo zemní vruty", zatizeni="vítr 45 m/s, sníh 1,4 kN/m²", cena="120 $/kW (od 1 kW)", usd=120 * STR["kWp"]),
    dict(nazev="Yanglin Tech (Xiamen)", url="https://yanglinxm.en.made-in-china.com/product/QaEUlOibgChD/China-Easy-to-Install-Bifacial-Solar-Fence-Ground-Vertical-Mounting-System-Solar-Panels-for-Garden-Fence.html",
         popis="bifaciální svislý plot „i pro zahradu“, uhlíková ocel, vlastní zemní vruty (dodání 5–10 dní po záloze)",
         kotveni="zemní vruty (vlastní výroba)", zatizeni="vítr 60 m/s, sníh 1,4 kN/m² (AS/NZS 1170)", cena="0,30–0,80 $/ks (jednotka nejasná)", usd=None),
    dict(nazev="Xiamen Kseng Metal Tech", url="https://www.xmkseng.com/space-saving-bifacial-vertical-solar-panel-fences-for-long-term-use_p262.html",
         popis="ocel žár. Zn + hliník AL6005-T5, panely naležato i nastojato, rámové i bezrámové, i pro rezidenční použití",
         kotveni="neuvedeno", zatizeni="vítr 60 m/s, sníh 2 kN/m² (JIS C 8955)", cena="na poptávku, na Alibabě MOQ 10 kW", usd=None),
    dict(nazev="Xiamen 9Sun Solar", url="https://www.9sunsolar.net/product/ground-bracket-vertical-bifacial-solar-panel-fence-for-solar-ground-mounting-system",
         popis="svislý bifaciální plot pro farmy, Al6005-T5 + ocel",
         kotveni="zemní vruty nebo beton", zatizeni="vítr 38 m/s, sníh 1,4 kN/m²", cena="0,11–0,13 $/W, MOQ 10 kW", usd=0.13 * 10000),
]


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

    sys_rows = ""
    for h in HOTOVE:
        kc = h.get("cena_kc") or (h["cena_eur"] * EUR if h.get("cena_eur") else None)
        cena = f"≈ {fmt(round(kc, -3) / 1000)} tis. Kč" if kc else "—"
        sys_rows += (f"<tr><td><a href=\"{h['url']}\">{h['nazev']}</a> <span class=mono>{h['zeme']}</span></td><td>{h['popis']}</td>"
                     f"<td>{h['kotveni']}</td><td class=n>{h['hloubka'] or '?'}</td><td class=n>{cena}</td><td>{h['cena_pozn']}</td>"
                     f"<td>{h['plus']}</td><td>{h['minus']}</td><td><span class='chip {h['hodnoceni']}'>{h['verdikt']}</span></td></tr>")
    nase = sum(r["celk"] for r in BOM) + N_PANEL * PANEL["cena"]
    cina_rows = ""
    for c in CINA:
        kc = f"≈ {fmt(round(c['usd'] * USD, -3) / 1000)} tis. Kč" if c["usd"] else "—"
        cina_rows += (f"<tr><td><a href=\"{c['url']}\">{c['nazev']}</a></td><td>{c['popis']}</td><td>{c['kotveni']}</td>"
                      f"<td>{c['zatizeni']}</td><td>{c['cena']}</td><td class=n>{kc}</td></tr>")

    pan_rows = ""
    for key, p in PANELS.items():
        st_p = string(p)
        verdict = {"JA": "doporučený", "AIKO": "alternativa", "TRINA": "jen 1 string ≤ 18 ks"}[key]
        chip = {"JA": "ok", "AIKO": "ok", "TRINA": "est"}[key]
        Lw = st_p["n"] * p["L"] + (st_p["n"] - 1) * GAP
        pan_rows += (f"<tr{' class=hl' if key == VYBER else ''}><td>{p['nazev']}</td><td>{p['typ']}</td><td class=n>{p['L']}×{p['B']}</td>"
                     f"<td class=n>{p['Wp']}</td><td class=n>{p['Voc']}</td><td class=n>{p['Isc']}</td>"
                     f"<td class=n>{st_p['n_max']}</td><td class=n>{st_p['n']} ks / {fmt(st_p['kWp'], 2)}</td>"
                     f"<td class=n>{p['A'][0]}–{p['A'][1]}</td><td class=n>{fmt(p['zad_navrh'])}</td>"
                     f"<td class=n>{fmt(p['cena'])}</td><td><span class='chip {chip}'>{verdict}</span></td></tr>")
    pan_src = "".join(f"<li>{p['nazev']}: {p['zdroj']}</li>" for p in PANELS.values())

    tilt_rows = ""
    for a in (90, 80, 75, 60, 37):
        hloubka = proj(a) + X_PAN[0]
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
<tr><td>Panel (návrh)</td><td>{PANEL['nazev']}, {PANEL['L']}×{PANEL['B']}×{PANEL['t']} mm, {PANEL['Wp']} Wp, ≈ {PANEL['kg']} kg, Voc {PANEL['Voc']} V, Isc {PANEL['Isc']} A, návrhové sání {PANEL['zad_navrh']} Pa</td><td>datový list, montážní návod</td></tr>
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
  <li>Vejde se do pásu 300 mm (hloubka konstrukce {fmt(X_CLAMP)} mm od osy plotu, rezerva {fmt(SITE['pas'] - X_CLAMP)} mm)</li>
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
<h2>Hotové systémy solárních plotů</h2>
<p>Rešerše trhu a diskusí (Photovoltaikforum, Akkudoktor), říjen 2026. Hledal jsem systém, který stojí samostatně, je mělký (pás 300 mm), nese jednu řadu panelů naležato a dá se ukotvit bez velkých výkopů.</p>
<div class="tw"><table>
<tr><th>Systém</th><th>Konstrukce</th><th>Kotvení</th><th class=n>hloubka mm</th><th class=n>19 panelů</th><th>Cena</th><th>Výhody</th><th>Nevýhody</th><th></th></tr>
{sys_rows}
<tr class=hl><td>Vlastní návrh (tento podklad)</td><td>sloupky 60×60 na vrutech, 2 vrstvy Al profilů, {PANEL['nazev']}</td><td>zemní vruty Ø76×1600</td><td class=n>{fmt(X_CLAMP - X_POST_PLOT + POST['b'] / 2)}</td><td class=n>≈ {fmt(round(nase, -3) / 1000)} tis. Kč</td><td>konstrukce + montáž + panely, s DPH</td><td>výška 1,5 m = plot, vruty, volba panelu</td><td>více dílů, vlastní statika</td><td><span class='chip ok'>srovnávací</span></td></tr>
</table></div>
<p>Ceny jsou přepočtené kurzem {EUR} Kč/€ a {PLN} Kč/zł. Polské ceny jsou obvykle s polskou DPH 23 %, ověřit. Jsou uvedené bez DPH (v Německu platí pro FV soukromníků 0 %). Při dodání do ČR soukromé osobě se nejspíš připočte 21 % české DPH, doprava a kotvení, montáž v ceně není.</p>
<h3>Co z toho plyne</h3>
<ul>
<li><b>Systémy s drážkovými sloupky</b> (Kirchberger, Profiness) sedí na pás 300 mm nejlépe. Sloupek 68–80 mm nese panel přímo, bez vodorovných nosníků, takže celá stěna je hluboká jen ≈ 7–8 cm. Panel je schválený pro daný systém, takže odpadá problém se způsobem upnutí. Sloupky stojí po 1,78–1,84 m, což je 20 patek místo 17 vrutů.</li>
<li>Oba mají výšku <b>1,25–1,27 m</b>, tedy o 23–25 cm níž než plot. Spodní hrana panelu je těsně nad soklem u země. Je potřeba poptat zvýšené sloupky (spodní hrana ≥ 30 cm kvůli trávě a sněhu) a patku na přírubu zemního vrutu místo betonu.</li>
<li>Při ceně ≈ 140–180 tis. Kč za 19 panelů vychází hotový systém stejně nebo o 10–25 % dráž než vlastní návrh s panely. Ušetří ale výrobu, řezání a dvouvrstvou montáž a za statiku i kompatibilitu ručí dodavatel.</li>
<li><b>Polsko:</b> nejbližší obdobou německé sady je <b>Solarne Ogrodzenia S1</b>, pole 2,1 m s panelem JA 500 W sklo-sklo za 1 179 zł. Na 33,6 m to dělá 16 polí a 8,0 kWp za ≈ 108 tis. Kč bez soklů a montáže. Plot by ale byl vysoký 1,7–1,8 m. <b>Emiter</b> v Katovicích prodává sady vodorovného pole se sloupkem 80×80 jen firmám, poptávka tedy přes montážní firmu. Na Slezsku je to logisticky nejbližší zdroj.</li>
<li><b>Česko:</b> hotovou stavebnici „sloupek + panel“ s veřejnou cenou jsem nenašel. Česká řešení (Plotík, ALUX, Svaroq, Ploty Dobrý) jsou koncipovaná jako <b>náhrada plotu</b> v jeho linii. Plot je váš, takže to je reálná varianta: v osazeném úseku odstranit pletivo i staré sloupky a postavit solární plot na jejich místě. Omezení pásu 30 cm pak odpadá. Vyžaduje to poptávku a betonové patky.</li>
</ul>
<h3>Čína (Alibaba a Made-in-China)</h3>
<p>Alibaba sama vyžaduje ověření posuvníkem (CAPTCHA), proto jsou údaje z výsledků vyhledávání a z webů dodavatelů, kteří na Alibabě prodávají. Všichni jsou z Xiamenu a nabízejí <b>svislé bifaciální ploty pro agro-FV</b>, tedy konstrukce bez panelů, cenu za watt a často minimální objednávku 10 kW.</p>
<div class="tw"><table>
<tr><th>Dodavatel</th><th>Systém</th><th>Kotvení</th><th>Zatížení (dle dodavatele)</th><th>Cena</th><th class=n>{fmt(STR['kWp'], 2)} kWp</th></tr>
{cina_rows}
</table></div>
<ul>
<li><b>Cena samotné konstrukce</b> je nízká: ≈ 25–30 tis. Kč za ocel na {fmt(STR['kWp'], 2)} kWp (9Sun při MOQ 10 kW ≈ 30 tis. Kč). Navíc přijde námořní doprava kusového zboží (LCL) do Hamburku nebo Gdaňsku a kamion (≈ 10–15 tis. Kč), clo, celní deklarace a 21% DPH. Celkem odhadem <b>≈ 45–55 tis. Kč</b> bez panelů a montáže proti ≈ 78 tis. Kč za materiál vlastního návrhu (vč. vrutů, bez montáže).</li>
<li><b>Riziko dovozu hliníku:</b> na hliníkové profily z Číny platí v EU antidumpingové clo (≈ 21–32 %). Ocelová konstrukce je bezpečnější volba. Hodnotu CBAM malý dovoz nepřekročí (limit 50 t/rok).</li>
<li><b>Technická rizika:</b> systémy jsou stavěné pro farmy (panely nastojato, 2 řady, sloupky po 2–4 m). Pro náš případ je potřeba výslovně objednat 1 řadu panelů naležato, horní hranu 1,5 m, hloubku ≤ 250 mm, vruty a svorky odpovídající návodu panelu JA. Deklarovaná zatížení (např. 60 m/s) nejsou ověřená podle eurokódů, takže statiku by stejně musel potvrdit český statik. Záruka se vymáhá jen obtížně, dodání trvá 6–10 týdnů.</li>
<li><b>Závěr:</b> úspora proti vlastnímu návrhu je ≈ 25–30 tis. Kč a nevyváží riziko a čas. Smysl by dávala jen ve spojení s vlastním výpočtem (tento podklad) jako výrobní zadání pro konkrétní továrnu, a to nejlépe u dodavatele Megan Solar (cena od 1 kW, naležato, vruty).</li>
</ul>

<h3>Zkušenosti z diskusí</h3>
<ul>
<li>Svislé ploty se uživatelům osvědčily hlavně v zimě, jeden hlásí 44 kWh za zimní den z 18,5 kWp (<a href="https://www.photovoltaikforum.com/thread/219589-zaun-pv-windlast-wie-bauen-mit-bifazialen-modulen/">Photovoltaikforum</a>).</li>
<li>Doporučují <b>sklo-sklo panely</b>, protože fólii na zadní straně u plotu poškodí tráva a keře. Na sloupky se vyplatí bouřkové kotvy.</li>
<li>Stejná situace jako u vás (starý plot, různé rozteče polí) se řešila v <a href="https://www.photovoltaikforum.com/thread/262607-zaunsolaranlage-vorhandenen-pfosten-verwenden/">tomto vlákně</a>. Rozměry panelů do nepravidelných polí nikdy nesednou. Řešením jsou vodorovné příčníky a na nich držáky panelů nezávislé na sloupcích, stejně jako ve vlastním návrhu.</li>
<li>Kutilské ploty na dřevěných sloupcích a kotvách tvaru H vítr převrátil (12 m plotu), a proto se doporučují kovové sloupky na betonu nebo vrutech (<a href="https://akkudoktor.net/t/erfahrungsaustausch-zu-eigenem-pv-zaun-projekt/24873">Akkudoktor</a>). Dalším častým problémem bylo napětí stringu: 19 panelů s vyšším Voc přesáhlo v mrazu limit střídače, což u zvoleného JA panelu (840 V) nehrozí.</li>
</ul>
<p><b>Doporučení:</b> poptat Kirchberger SUNLINE a Profiness Basic quer. Na rozhodnutí stačí pět údajů: cena s dodáním do ČR, statika pro větrnou oblast II a terén II, sloupky pro výšku 1,5 m se spodní hranou ≥ 30 cm, kotvení na zemní vruty a elektrické údaje panelu (Voc) kvůli stringu 19 ks. Pokud dodavatel zvýšení nebo vruty nenabídne, zůstává vlastní návrh.</p>
</section>

<section>
<h2>Výběr panelu</h2>
<p>Prošel jsem montážní návody tří výrobců panelů 1 762 × 1 134 mm. <b>Žádný z nich nepovoluje upnutí na dlouhých hranách s profily rovnoběžnými s dlouhou hranou</b>: JA Solar má u řady JAM54 v tabulce „N/A“, Trina ani Aiko tuto kombinaci u formátu 54 článků neuvádějí. Povolené je upnutí na dlouhých hranách s profily <b>kolmo</b> na dlouhou hranu. U panelů naležato to znamená svislé profily. Konstrukce je proto dvouvrstvá: vodorovné nosníky na sloupcích a na nich krátké svislé profily, 2 na každý panel.</p>
<div class="tw"><table>
<tr><th>Panel</th><th>Typ</th><th class=n>mm</th><th class=n>Wp</th><th class=n>Voc V</th><th class=n>Isc A</th><th class=n>max. ks / string</th><th class=n>osazeno</th><th class=n>svorky A mm</th><th class=n>sání Pa</th><th class=n>Kč/ks</th><th></th></tr>
{pan_rows}
</table></div>
<p>Max. počet panelů ve stringu je spočten pro −25 °C s 2% rezervou pod 1 000 V. „Sání“ je návrhové zatížení zezadu podle výrobce (zkušební / 1,5) pro upnutí na dlouhých hranách s profily kolmo. Ceny jsou odhad s DPH (říjen 2026), je potřeba je poptat.</p>
<ul>
<li><b>JA Solar JAM54D40-450/LB (doporučený):</b> bifaciální sklo-sklo, vejde se 19 ks na jeden string ({fmt(STR['kWp'], 2)} kWp), v ČR běžně skladem. Zadní strana zachytí odražené a difuzní světlo ze zahrady, orientačně +3 až 6 % (přes pletivo). Verze se sklem 2,0 mm má vyšší únosnost zepředu (3 600 Pa).</li>
<li><b>AIKO Neostar 2P A465 (alternativa):</b> nejvyšší výkon na plochu ({fmt(string(PANELS['AIKO'])['kWp'], 2)} kWp), technologie ABC lépe snáší částečné zastínění (tráva a sníh u spodní hrany, stín stromu na konci). Je jednostranný, sklo-fólie, a dražší.</li>
<li><b>Trina Vertex S+ NEG9RC.27:</b> mechanicky nejodolnější (sání až 4 000 Pa zkušební se svorkou typu „A-surface“), ale má vysoké napětí článků. Na jeden string se vejde jen {string(PANELS['TRINA'])['n_max']} ks, takže celý plot by potřeboval druhý MPPT.</li>
</ul>
<p class="mono">Zdroje upínání:</p><ul class="mono">{pan_src}</ul>
</section>

<section>
<h2>Sklon panelů</h2>
<p>Výroba podle PVGIS 5.2 pro 1 kWp, azimut 150°, ztráty 14 %, včetně horizontu terénu. Hloubka zahrnuje průmět panelu ({PANEL['B']} mm naležato) a {fmt(X_PAN[0])} mm na sloupek a dvě vrstvy profilů. Sklon kromě svislého by navíc panely vykláněl nad pozemek souseda a nenahradil by stínicí tkaninu.</p>
<div class="tw"><table>
<tr><th>Sklon</th><th class=n>kWh/kWp·rok</th><th class=n>vůči optimu</th><th class=n>zima XI–II</th><th class=n>léto VI–VIII</th><th class=n>hloubka mm</th><th>pás 300 mm</th></tr>
{tilt_rows}
</table></div>
<p><b>Závěr:</b> svisle se ročně vyrobí asi {fmt(sum(PVGIS[90]) / sum(PVGIS[37]) * 100)} % optima, ale v zimě (listopad–únor) <b>{fmt(win(90) / win(37) * 100)} % optima</b>, takže svislá plocha je zimní zdroj. V létě vyrábí méně, což u střídače se střešní FVE nevadí: svislý string pokrývá ráno, zimu a období po sněžení. Větší sklon se do pásu nevejde. Panely naležato mají pruhy článků vodorovně, takže sníh nebo tráva u spodní hrany vyřadí přes bypass diodu jen spodní třetinu panelu.</p>
</section>

<section>
<h2>Rozmístění a zapojení</h2>
<ul>
<li>{N_PANEL} panelů {PANEL['nazev']} naležato v jedné řadě, mezera {GAP} mm, délka stěny <b>{fmt(L_WALL)} mm</b>. Horní hrana 1 500 mm (= výška plotu), spodní hrana {Y_BOT} mm nad terénem.</li>
<li>Skladba od plotu: sloupek {POST['b']}×{POST['b']} → vodorovný nosník 40×40 (2 řady, osy {RAIL_Y[0]} a {RAIL_Y[1]} mm) → svislý profil 40×40 délky {PANEL['B'] + 2 * VR_EXT} mm, 2 na panel ve vzdálenosti {fmt(VR_A)} mm od kratších hran → panel → svorky. Svislé profily přesahují panel o {VR_EXT} mm kvůli svorkám, horní konec je tedy {Y_TOP + VR_EXT} mm nad terénem.</li>
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
návrhové sání podle výrobce ({PANEL['nazev']}, svorky na dlouhých hranách, profily kolmo, A = {PANEL['A'][0]}–{PANEL['A'][1]} mm): {fmt(PANEL['zad_navrh'] / 1000, 2)} kPa → využití {fmt(max(st['panel_p']) / PANEL['zad_navrh'] * 1e5)} % → <b>vyhoví</b><br>
síla na svorku (4 ks/panel, ULS): {fmt(st['clamp_Ed'], 2)} kN · svislý profil: svorky leží na jeho koncích nad vodorovnými nosníky, ohyb zanedbatelný
</div>
<h3>Vodorovné nosníky (spojitý nosník, MKP)</h3>
<div class="calc">
2 nosníky Al 40×40, bodová zatížení ¼ tlaku na panel v každém styku se svislým profilem ({2 * N_PANEL} styků na nosník), podpory = sloupky FV<br>
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
<li>průřezové charakteristiky zvoleného Al profilu a únosnost křížových spojovačů a svorek</li>
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
<li><b>Nosníky:</b> úhelníky na sloupky, vodorovné nosníky v osách {RAIL_Y[0]} a {RAIL_Y[1]} mm. Dilatační spojky v mezerách za 6. a 13. panelem, ostatní spoje pevné. Konec nosníku smí přesahovat krajní sloupek nejvýš o 300 mm.</li>
<li><b>Svislé profily:</b> křížovými spojovači na nosníky, 2 na panel ve vzdálenosti {fmt(VR_A)} mm od kratších hran (šablona z latě). Spodní konce do jedné výšky {Y_BOT - VR_EXT} mm nad terénem.</li>
<li><b>Pospojování:</b> Cu 6 mm² mezi všemi sloupky a jedním profilem každé řady, připojit k hlavní ochranné přípojnici (HOP) domu. Svorky s nerezovými podložkami (Al/Zn).</li>
<li><b>Panely:</b> od jednoho konce, 4 koncové svorky na dlouhých hranách (na koncích svislých profilů), svorky a moment podle návodu výrobce panelu. Konektory MC4 propojit hned za panely, kabely vázat UV odolnými pásky k profilu, bez průvěsu.</li>
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
<li>Potvrdit panel u dodavatele: aktuální revize montážního návodu (upnutí na dlouhých hranách, profily kolmo), cena a dostupnost.</li>
<li>Vytyčení hranice: od čeho se 30 cm měří (osa, nebo líc pletiva)?</li>
<li>Zemina v pásu za plotem: kamenitá, nebo hlinitá? Zkouška vrutů.</li>
<li>Vzdálenost od plotu ke střídači a trasa kabelu.</li>
<li>Kolik polí u stromu přesně vynechat. Lze ověřit fotkou plotu v zimě kolem poledne.</li>
</ul>
</section>
<footer>Zdroje: stránky výrobců solárních plotů a diskuse (viz Hotové systémy), montážní návody JA Solar, Trina Solar a AIKO (viz Výběr panelu), PVGIS 5.2 (JRC), ČSN EN 1991-1-4 + NA, ČSN EN 1993-1-1, ČSN EN 1999-1-1, datová stránka SolaX X3-Ultra, cena profilu: zbozi.cz (G21 HPG2144X). Výpočet a výkresy generuje <span class="mono">plot-fve/src/navrh.py</span>.</footer>
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
