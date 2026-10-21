#!/usr/bin/env python3
"""Katalog REO R290 Smart (A4, 8 stran) – redesign letáku „REO R290“ (RH030–RH060, 10/26) na řadu Smart.
Hlavní argumenty: vysoká účinnost (SCOP) + topení přímo ze sluníčka (FV → MPPT → DC sběrnice kompresoru).
Ceny = web eko4home (zadal uživatel 20. 10. 2026), data = technická specifikace a ERP protokol výrobce.
    python3 build.py   → REO-R290-Smart_katalog.html + .pdf (headless Chrome)
"""
import base64, math, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).parent
A = ROOT / "assets"
sys.path.insert(0, str(ROOT.parent / "letaky"))
from ilustrace import SVG as ILU  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def uri(p):
    p = A / p if (A / p).exists() else ROOT.parent / "letaky" / "assets" / p
    mime = {"png": "image/png", "jpg": "image/jpeg", "svg": "image/svg+xml"}[p.suffix[1:]]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


HERO = uri("hero-scena.png")
LOGO, UNIT, RHX = uri("logo-cut.png"), uri("smart-cut.png"), uri("rhx-pro-cut.png")
QR = uri("qr-reoheating.svg")

# --- data (spec. výrobce; RH06–RH16 rozsah, COP, hmotnost a rozměry dle katalogu výrobce 10/2025, aktualizováno 21. 10. 2026). P = jmen. výkon A7/W35, rng = rozsah A7/W35,
# cop = A7/W35, A7/W55 (EN 14511), scop = 35/55 °C průměrné klima (EN 14825), lwa = ErP 35/55, lp = 1 m,
# fuse = jištění vč. el. dohřevu 3 kW, price = Kč bez DPH (web eko4home 20. 10. 2026)
M = [
 # model,      ph,  P,  rng,         cop35, cop55, scop35,scop55, lwa,     lp,      fuse, kg,  r290,  rozm,           price
 ("RH06",      "1F", 6,  "3,4–8,5",   "4,88","3,03","5,00","3,84",(52,53),(38,38), 40, 116, "0,6", "1200×463×791",  129000),
 ("RH08",      "3F", 8,  "4,5–11,0",  "4,89","3,04","5,15","3,90",(50,50),(35,34), 25, 120, "0,9", "1328×470×1065", 139000),
 ("RH10",      "3F", 10, "5,2–12,9",  "4,76","2,91","5,20","3,90",(54,55),(39,40), 32, 138, "1,15","1328×470×1065", 149000),
 ("RH12",      "3F", 12, "7,0–17,0",  "4,86","3,01","5,11","3,94",(55,55),(40,40), 40, 165, "1,3", "1328×470×1065", 159000),
 ("RH14",      "3F", 14, "7,6–19,3",  "4,73","2,95","5,29","3,91",(56,55),(41,40), 40, 170, "1,5", "1328×470×1065", 169000),
 ("RH16",      "3F", 16, "8,8–22,0",  "4,70","2,93","5,09","3,88",(55,56),(39,41), 40, 190, "1,7", "1328×470×1065", 189000),
 ("RHX20 Pro", "3F", 20, "10,2–28,0", "4,85","2,92","5,23","3,97",(50,56),(35,40), 32, 265, "2,2", "1375×532×1565", 300000),
 ("RHX30 Pro", "3F", 30, "12,7–40,0", "4,60","2,80","5,25","3,90",(55,59),(39,42), 40, 328, "3,4", "1550×630×1708", 350000),
]
SCOP35_MAX, SCOP55_MAX = "5,29", "3,97"


def kc(v):
    return f"{v:,}".replace(",", "&nbsp;") + "&nbsp;Kč"


# --- ikony (stroke 24×24)
IC = {
 "eff":   "M13 2L3 14h8l-1 8 10-12h-8l1-8z",
 "temp":  "M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z",
 "quiet": "M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z",
 "cpu":   "M9 9h6v6H9z M5 5h14v14H5z M9 2v3 M15 2v3 M9 19v3 M15 19v3 M19 9h3 M19 15h3 M2 9h3 M2 15h3",
 "sun":   "M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M12 2v2 M12 20v2 M4.9 4.9l1.4 1.4 M17.7 17.7l1.4 1.4 M2 12h2 M20 12h2 M4.9 19.1l1.4-1.4 M17.7 6.3l1.4-1.4",
 "drop":  "M12 2.7l5.7 5.7a8 8 0 1 1-11.3 0z",
 "phone": "M7 2h10a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z M11 18h2",
 "shield":"M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z M9 12l2 2 4-4",
 "cert":  "M12 15a7 7 0 1 0 0-14 7 7 0 0 0 0 14z M8.2 13.9L7 23l5-3 5 3-1.2-9.1",
 "box":   "M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7z M3.3 7L12 12l8.7-5 M12 22V12",
 "layers":"M12 2L2 7l10 5 10-5-10-5z M2 17l10 5 10-5 M2 12l10 5 10-5",
 "grid":  "M4 4h6v6H4z M14 4h6v6h-6z M14 14h6v6h-6z M4 14h6v6H4z",
 "wrench":"M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9l-3.8 3.8z",
 "snow":  "M12 2v20 M3.3 7l17.4 10 M20.7 7L3.3 17",
 "mail":  "M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z M22 6l-10 7L2 6",
 "tel":   "M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z",
 "web":   "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M2 12h20 M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10 15 15 0 0 1-4-10 15 15 0 0 1 4-10z",
 "pin":   "M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z M12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
 "wifi":  "M5 12.55a11 11 0 0 1 14.08 0 M1.42 9a16 16 0 0 1 21.16 0 M8.53 16.11a6 6 0 0 1 6.95 0 M12 20h.01",
 "leaf":  "M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z M2 21c0-3 1.85-5.36 5.08-6",
 "home":  "M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z",
 "bld":   "M4 21V4a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v17 M15 9h4a1 1 0 0 1 1 1v11 M8 7h3 M8 11h3 M8 15h3 M2 21h20",
 "chart": "M3 3v18h18 M7 15l4-4 3 3 5-6",
 "bell":  "M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9 M13.7 21a2 2 0 0 1-3.4 0",
 "users": "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M23 21v-2a4 4 0 0 0-3-3.9 M16 3.1a4 4 0 0 1 0 7.8",
 "plug":  "M9 2v6 M15 2v6 M6 8h12v4a6 6 0 0 1-12 0z M12 18v4",
 "x":     "M18 6L6 18 M6 6l12 12",
 "check": "M20 6L9 17l-5-5",
}


def ic(k, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="{IC[k]}"/></svg>')


def top(tag, n):
    return (f'<div class="top"><img src="{LOGO}" alt="REO HEATING"><span class="tag">{tag}</span></div>'
            f'<div class="pno">{n}</div>')


FOOT = "REO HEATING · Riva Trade s.r.o., IČ 08864811 · Třinec · reoheating.cz · 10/2026"

# ================================================================ SVG grafiky

def svg_principle():
    """Blokové schéma: FV (DC) → MPPT → DC sběrnice ← usměrňovač ← síť; DC sběrnice → měnič → kompresor."""
    box = lambda x, y, w, h, t, s, fill, fg="#123D25", stroke="none": (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<text x="{x+w/2}" y="{y+h/2-3}" text-anchor="middle" font-size="15" font-weight="800" fill="{fg}">{t}</text>'
        f'<text x="{x+w/2}" y="{y+h/2+15}" text-anchor="middle" font-size="11.5" fill="{fg}" opacity=".8">{s}</text></g>')
    return f"""<svg class="prin" viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <defs>
    <marker id="ay" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#E0A21B"/></marker>
    <marker id="ag" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#7C8A82"/></marker>
    <marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#34A263"/></marker>
  </defs>
  <!-- jednotka (rámeček) -->
  <rect x="222" y="14" width="420" height="272" rx="18" fill="#F5FBF7" stroke="#34A263" stroke-width="2" stroke-dasharray="7 5"/>
  <text x="236" y="38" font-size="12" font-weight="800" fill="#26804B" letter-spacing="1.5">VENKOVNÍ JEDNOTKA REO R290 SMART</text>

  <!-- FV panely -->
  <g transform="translate(14,40)">
    <g transform="skewX(-12)">
      {''.join(f'<rect x="{24+c*30}" y="{r*30}" width="27" height="27" rx="2" fill="#1E3F73" stroke="#7FA6D8" stroke-width="1"/>' for r in range(2) for c in range(4))}
    </g>
    <text x="70" y="82" text-anchor="middle" font-size="15" font-weight="800" fill="#123D25">FV panely</text>
    <text x="70" y="99" text-anchor="middle" font-size="11.5" fill="#5C6B62">stejnosměrný proud (DC)</text>
  </g>
  <circle cx="64" cy="22" r="13" fill="#EFB935"/>
  <!-- síť -->
  <g transform="translate(20,196)">
    <path d="M30 0l-14 70h28z M18 22h24 M14 42h32" fill="none" stroke="#7C8A82" stroke-width="3" stroke-linejoin="round"/>
    <text x="100" y="40" text-anchor="middle" font-size="15" font-weight="800" fill="#123D25">Síť</text>
    <text x="100" y="57" text-anchor="middle" font-size="11.5" fill="#5C6B62">230 / 400 V (AC)</text>
  </g>

  {box(252, 60, 150, 62, "Deska MPPT", "vytěží z panelů maximum", "#FFF3CF", stroke="#EFB935")}
  {box(252, 190, 150, 62, "Usměrňovač", "střídavý → stejnosměrný", "#EEF2EF", stroke="#C9D3CD")}
  {box(440, 118, 82, 82, "DC", "sběrnice", "#34A263", fg="#fff")}
  {box(546, 108, 82, 102, "Měnič", "+ kompresor", "#123D25", fg="#fff")}

  <!-- šipky -->
  <path d="M150 90 H246" stroke="#E0A21B" stroke-width="5" fill="none" marker-end="url(#ay)"/>
  <path d="M150 221 H246" stroke="#7C8A82" stroke-width="5" fill="none" marker-end="url(#ag)"/>
  <path d="M402 91 C424 91 420 140 436 148" stroke="#E0A21B" stroke-width="5" fill="none" marker-end="url(#ay)"/>
  <path d="M402 221 C424 221 420 178 436 172" stroke="#7C8A82" stroke-width="5" fill="none" marker-end="url(#ag)"/>
  <path d="M522 159 H542" stroke="#34A263" stroke-width="5" fill="none" marker-end="url(#ar)"/>
  <!-- teplo -->
  <path d="M628 159 H690" stroke="#D9622B" stroke-width="6" fill="none"/>
  <path d="M684 147 l14 12 -14 12" fill="#D9622B"/>
  <text x="704" y="155" font-size="15" font-weight="800" fill="#123D25">Teplo</text>
  <text x="704" y="172" font-size="11.5" fill="#5C6B62">do domu</text>

  <text x="186" y="80" text-anchor="middle" font-size="11" font-weight="700" fill="#B07A0B">1. přednost</text>
  <text x="186" y="211" text-anchor="middle" font-size="11" font-weight="700" fill="#5C6B62">2. doplní</text>
  <text x="432" y="236" font-size="11" fill="#5C6B62">obě cesty se sejdou v jednom</text>
  <text x="432" y="251" font-size="11" fill="#5C6B62">stejnosměrném „kolektoru“</text>
  <text x="432" y="266" font-size="11" fill="#5C6B62">před měničem kompresoru</text>
</svg>"""


def svg_compare():
    """Klasické řešení přes střídač vs. přímé napojení."""
    def chip(x, y, t, kind):
        fill = {"y": "#FFF3CF", "g": "#EEF2EF", "r": "#F6E1DC", "b": "#34A263", "d": "#123D25"}[kind]
        fg = "#fff" if kind in "bd" else "#123D25"
        w = 12 + len(t) * 7.4
        return (f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="8" fill="{fill}"/>'
                f'<text x="{x+w/2}" y="{y+20}" text-anchor="middle" font-size="12.5" font-weight="700" fill="{fg}">{t}</text>', x + w)

    def row(y, items):
        out, x = [], 10
        for i, (t, k) in enumerate(items):
            s, x2 = chip(x, y, t, k)
            out.append(s)
            if i < len(items) - 1:
                out.append(f'<path d="M{x2+4} {y+15} h14" stroke="#7C8A82" stroke-width="2" fill="none"/>'
                           f'<path d="M{x2+16} {y+10} l6 5 -6 5z" fill="#7C8A82"/>')
            x = x2 + 26
        return "".join(out)

    a = row(30, [("panely", "y"), ("střídač DC→AC", "r"), ("rozvod domu", "g"), ("usměrnění AC→DC", "r"), ("kompresor", "d")])
    b = row(108, [("panely", "y"), ("deska MPPT v jednotce", "b"), ("kompresor", "d")])
    return f"""<svg class="cmpsvg" viewBox="0 0 760 150" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <text x="10" y="20" font-size="12" font-weight="800" fill="#5C6B62" letter-spacing="1">BĚŽNÉ ŘEŠENÍ – FOTOVOLTAICKÁ ELEKTRÁRNA</text>
  {a}
  <text x="10" y="98" font-size="12" font-weight="800" fill="#26804B" letter-spacing="1">REO R290 SMART – PANELY PŘÍMO DO JEDNOTKY</text>
  {b}
</svg>"""


def svg_day():
    """Ilustrační jarní den: výkon FV vs. příkon TČ (kW el.), plochy = podíl sluníčka a sítě."""
    W, H, x0, y0, pw, ph = 760, 250, 46, 20, 690, 190
    hrs = [5 + i * 0.25 for i in range(16 * 4 + 1)]           # 5–21 h

    def pv(h):
        return 0 if h <= 6.5 or h >= 19.5 else 3.6 * math.sin(math.pi * (h - 6.5) / 13) ** 1.6

    def load(h):  # příkon TČ: ráno vyšší (topení + TUV), přes den nižší, večer opět
        return 1.15 + 0.75 * math.exp(-((h - 7) / 1.4) ** 2) + 0.55 * math.exp(-((h - 18.5) / 1.6) ** 2) \
            + 0.55 * math.exp(-((h - 13) / 1.3) ** 2)

    X = lambda h: x0 + (h - 5) / 16 * pw
    Y = lambda v: y0 + ph - v / 4 * ph
    pts = lambda f: " ".join(f"{X(h):.1f},{Y(f(h)):.1f}" for h in hrs)
    sun = lambda h: min(pv(h), load(h))
    area = lambda f, g: (f"M{X(hrs[0]):.1f},{Y(g(hrs[0])):.1f} " + " ".join(f"L{X(h):.1f},{Y(f(h)):.1f}" for h in hrs)
                         + " " + " ".join(f"L{X(h):.1f},{Y(g(h)):.1f}" for h in reversed(hrs)) + "Z")
    grid = "".join(f'<line x1="{x0}" x2="{x0+pw}" y1="{Y(v)}" y2="{Y(v)}" stroke="#E3EAE5"/>'
                   f'<text x="{x0-8}" y="{Y(v)+4}" text-anchor="end" font-size="11" fill="#7C8A82">{v}</text>' for v in range(0, 5))
    ticks = "".join(f'<text x="{X(h)}" y="{y0+ph+18}" text-anchor="middle" font-size="11" fill="#7C8A82">{h}:00</text>'
                    for h in range(6, 22, 2))
    return f"""<svg class="day" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  {grid}{ticks}
  <text x="{x0-30}" y="{y0-6}" font-size="10.5" fill="#7C8A82">kW</text>
  <path d="{area(load, lambda h: 0)}" fill="#C9D3CD"/>
  <path d="{area(sun, lambda h: 0)}" fill="#EFB935"/>
  <polyline points="{pts(pv)}" fill="none" stroke="#C98A0C" stroke-width="2" stroke-dasharray="5 4"/>
  <polyline points="{pts(load)}" fill="none" stroke="#123D25" stroke-width="2.5"/>
  <text x="{X(12.6)}" y="{Y(3.75)}" font-size="12" font-weight="700" fill="#B07A0B">co panely právě vyrábějí</text>
  <text x="{X(13)}" y="{Y(0.75)}" text-anchor="middle" font-size="13" font-weight="800" fill="#123D25">topí sluníčko</text>
  <text x="{X(6.1)}" y="{Y(0.55)}" text-anchor="middle" font-size="12" font-weight="700" fill="#3E4A43">síť</text>
  <text x="{X(20.1)}" y="{Y(0.55)}" text-anchor="middle" font-size="12" font-weight="700" fill="#3E4A43">síť</text>
  <text x="{X(7.2)}" y="{Y(2.2)}" text-anchor="middle" font-size="12" font-weight="700" fill="#123D25">příkon čerpadla</text>
</svg>"""


def svg_scop_bars():
    """SCOP 35/55 °C po modelech (sloupce)."""
    W, H, x0, y0, pw, ph = 760, 260, 40, 26, 710, 190
    n = len(M); gw = pw / n; bw = 26
    vmax = 6
    Y = lambda v: y0 + ph - v / vmax * ph
    out = []
    for v in range(0, 7):
        out.append(f'<line x1="{x0}" x2="{x0+pw}" y1="{Y(v)}" y2="{Y(v)}" stroke="#E3EAE5"/>'
                   f'<text x="{x0-8}" y="{Y(v)+4}" text-anchor="end" font-size="11" fill="#7C8A82">{v}</text>')
    for i, m in enumerate(M):
        cx = x0 + gw * i + gw / 2
        for j, (val, col) in enumerate(((m[6], "#34A263"), (m[7], "#D9622B"))):
            v = float(val.replace(",", "."))
            x = cx - bw - 2 + j * (bw + 4)
            best = (j == 0 and val == SCOP35_MAX) or (j == 1 and val == SCOP55_MAX)
            strk = ' stroke="#123D25" stroke-width="2.5"' if best else ""
            out.append(f'<rect x="{x}" y="{Y(v)}" width="{bw}" height="{Y(0)-Y(v)}" rx="4" fill="{col}"{strk}/>'
                       f'<text x="{x+bw/2}" y="{Y(v)-6}" text-anchor="middle" font-size="{12 if best else 10.5}" '
                       f'font-weight="{800 if best else 600}" fill="{"#123D25" if best else "#3E4A43"}">{val}</text>')
        name = m[0].replace(" Pro", "")
        out.append(f'<text x="{cx}" y="{y0+ph+18}" text-anchor="middle" font-size="12" font-weight="700" fill="#123D25">{name}</text>'
                   f'<text x="{cx}" y="{y0+ph+33}" text-anchor="middle" font-size="10.5" fill="#7C8A82">'
                   f'{"Pro · " if "Pro" in m[0] else ""}{m[2]} kW</text>')
    return (f'<svg class="bars" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">'
            + "".join(out) + "</svg>")


def svg_gwp():
    data = [("R410A", 2088, "#B9C4BD"), ("R32", 675, "#B9C4BD"), ("R290", 3, "#34A263")]
    out = []
    for i, (n, v, c) in enumerate(data):
        y = 8 + i * 34
        w = max(4, v / 2088 * 250)
        out.append(f'<text x="0" y="{y+17}" font-size="13" font-weight="700" fill="#123D25">{n}</text>'
                   f'<rect x="64" y="{y}" width="{w}" height="24" rx="5" fill="{c}"/>'
                   f'<text x="{64+w+8}" y="{y+17}" font-size="13" font-weight="800" fill="{"#26804B" if n=="R290" else "#3E4A43"}">{v:,}</text>'
                   .replace(",", "&#8239;"))
    return ('<svg class="gwp" viewBox="0 0 380 108" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">'
            + "".join(out) + "</svg>")


def svg_hydraulics():
    """Zjednodušené zapojení v rodinném domě."""
    return """<svg class="hyd" viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <rect x="292" y="6" width="462" height="288" rx="16" fill="#F7F9F8" stroke="#DCE6DF"/>
  <text x="308" y="28" font-size="11.5" font-weight="800" fill="#7C8A82" letter-spacing="1.2">V DOMĚ – NAVRHUJE SE PODLE PROJEKTU</text>
  <!-- FV -->
  <g transform="translate(26,14) skewX(-12)">
    <rect x="18" y="0" width="26" height="26" rx="2" fill="#1E3F73"/><rect x="47" y="0" width="26" height="26" rx="2" fill="#1E3F73"/>
    <rect x="76" y="0" width="26" height="26" rx="2" fill="#1E3F73"/><rect x="105" y="0" width="26" height="26" rx="2" fill="#1E3F73"/>
  </g>
  <text x="92" y="60" text-anchor="middle" font-size="12" font-weight="700" fill="#123D25">FV panely (volitelně)</text>
  <path d="M92 66 V108" stroke="#E0A21B" stroke-width="3" stroke-dasharray="6 4"/>
  <!-- jednotka -->
  <rect x="14" y="110" width="196" height="136" rx="10" fill="#2A2E33"/>
  <circle cx="76" cy="178" r="46" fill="#1E2226" stroke="#3E454C" stroke-width="3"/>
  <path d="M76 178 l-30 -14 a34 34 0 0 1 22 -20z M76 178 l28 -18 a34 34 0 0 1 4 30z M76 178 l2 34 a34 34 0 0 1 -32 -12z" fill="#2B4AA0"/>
  <text x="166" y="132" text-anchor="middle" font-size="9" font-weight="800" fill="#C9CED3" letter-spacing=".6">REO HEATING</text>
  <g font-size="10.5" fill="#fff" font-weight="600">
    <text x="132" y="160">čerpadlo</text><text x="132" y="176">dohřev 3 kW</text><text x="132" y="192">expanze 6 l</text><text x="132" y="208">poj. ventil</text></g>
  <text x="112" y="266" text-anchor="middle" font-size="12.5" font-weight="800" fill="#123D25">REO R290 Smart</text>
  <text x="112" y="282" text-anchor="middle" font-size="11" fill="#5C6B62">venkovní jednotka</text>
  <!-- přívod (červená) -->
  <path d="M210 140 H346" stroke="#D9622B" stroke-width="5" fill="none"/>
  <path d="M360 126 V62 H522" stroke="#D9622B" stroke-width="5" fill="none"/>
  <path d="M374 140 H410" stroke="#D9622B" stroke-width="5" fill="none"/>
  <path d="M582 62 H600" stroke="#D9622B" stroke-width="5" fill="none"/>
  <!-- zpátečka (modrá) -->
  <path d="M720 104 V226 H210" stroke="#3B7DD8" stroke-width="5" fill="none"/>
  <path d="M552 140 V226 M441 206 V226" stroke="#3B7DD8" stroke-width="5" fill="none"/>
  <!-- trojcestný ventil -->
  <g transform="translate(360,140)"><path d="M-14 -10 L0 0 L-14 10z M14 -10 L0 0 L14 10z" fill="#123D25"/><path d="M-10 -14 L0 0 L10 -14z" fill="#123D25"/></g>
  <text x="352" y="170" text-anchor="middle" font-size="11" font-weight="700" fill="#123D25">3cestný ventil</text>
  <!-- AKU -->
  <rect x="522" y="30" width="60" height="110" rx="26" fill="#fff" stroke="#9AA6A0" stroke-width="2"/>
  <text x="552" y="90" text-anchor="middle" font-size="12" font-weight="800" fill="#123D25">AKU</text>
  <text x="552" y="104" text-anchor="middle" font-size="9.5" fill="#5C6B62">dle potřeby</text>
  <!-- TUV -->
  <rect x="410" y="118" width="62" height="88" rx="24" fill="#fff" stroke="#9AA6A0" stroke-width="2"/>
  <path d="M426 134 q22 8 0 16 q22 8 0 16 q22 8 0 16" stroke="#D9622B" stroke-width="3" fill="none" transform="translate(6,0)"/>
  <text x="441" y="246" text-anchor="middle" font-size="12" font-weight="800" fill="#123D25">zásobník TUV</text>
  <text x="441" y="260" text-anchor="middle" font-size="10.5" fill="#5C6B62">teplá voda</text>
  <!-- podlahové topení -->
  <path d="M600 62 h120 v14 h-110 v14 h110 v14" stroke="#E07A45" stroke-width="5" fill="none"/>
  <text x="678" y="128" text-anchor="middle" font-size="12" font-weight="800" fill="#123D25">podlahové topení</text>
  <text x="678" y="143" text-anchor="middle" font-size="10.5" fill="#5C6B62">nebo radiátory</text>
  <g font-size="10.5" fill="#5C6B62"><text x="530" y="266">+ filtr, uzavírací armatury,</text>
  <text x="530" y="280">příp. další expanze, ovladač</text></g>
</svg>"""



def hero_overlay():
    """Popisky a symboly přes hero scénu (souřadnice obrázku 1186×838)."""
    def badge(cx, cy, path, fill="#EFB935", fg="#123D25", r=26):
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
                f'<g transform="translate({cx-r*.72},{cy-r*.72}) scale({r*1.44/24})" fill="none" stroke="{fg}" stroke-width="1.9" '
                f'stroke-linecap="round" stroke-linejoin="round"><path d="{path}"/></g>')
    SHOWER = "M4 20V8a4 4 0 0 1 4-4h2a4 4 0 0 1 4 4 M10 8h8 M12 12v1 M16 12v1 M20 12v1 M14 16v1 M18 16v1"
    RAD = "M5 5v14 M9.5 5v14 M14 5v14 M18.5 5v14 M3 8h18 M3 16h18"
    FLOOR = "M3 20h18 M4 15c2.5-5 4.5 5 7 0s4.5 5 7 0 M4 9c2.5-5 4.5 5 7 0s4.5 5 7 0"
    CPU = IC["cpu"]
    box = lambda x, y, w, h: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#fff" fill-opacity=".94" filter="url(#sh)"/>'
    dot = lambda x, y: f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="#123D25" stroke-width="4"/>'
    return f"""<svg class="hero-ov" viewBox="0 0 1186 838" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <defs><filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity=".22"/></filter></defs>
  <!-- jednotka: kompresor Mitsubishi Electric -->
  <path d="M232 418 V478" stroke="#123D25" stroke-width="4"/>{dot(232, 482)}
  <rect x="22" y="322" width="420" height="98" rx="14" fill="#123D25" filter="url(#sh)"/>
  {badge(72, 371, CPU, r=30)}
  <text x="116" y="360" font-size="25" font-weight="800" fill="#fff">Kompresor</text>
  <text x="116" y="390" font-size="25" font-weight="800" fill="#EFB935">Mitsubishi Electric</text>
  <text x="116" y="410" font-size="15" font-weight="600" fill="#fff" opacity=".8">v jednotce REO R290 Smart</text>
  <!-- TUV -->
  <path d="M1012 380 H930" stroke="#123D25" stroke-width="4"/>{dot(926, 380)}
  {box(1012, 292, 166, 176)}
  {badge(1052, 334, SHOWER)}
  <text x="1028" y="392" font-size="22" font-weight="800" fill="#123D25">Teplá voda</text>
  <text x="1028" y="416" font-size="15.5" fill="#3E4A43">zásobník TUV</text>
  <text x="1028" y="436" font-size="15.5" fill="#3E4A43">210 l s výměníkem</text>
  <text x="1028" y="456" font-size="15.5" fill="#3E4A43">v horní části</text>
  <!-- topení -->
  <path d="M1012 690 H936" stroke="#123D25" stroke-width="4"/>{dot(932, 690)}
  {box(1012, 586, 166, 196)}
  {badge(1052, 628, FLOOR, fill="#D9622B", fg="#fff")}{badge(1112, 628, RAD, fill="#D9622B", fg="#fff")}
  <text x="1028" y="686" font-size="22" font-weight="800" fill="#123D25">Topná voda</text>
  <text x="1028" y="710" font-size="15.5" fill="#3E4A43">akumulace 70 l</text>
  <text x="1028" y="730" font-size="15.5" fill="#3E4A43">ve spodní části –</text>
  <text x="1028" y="750" font-size="15.5" fill="#3E4A43">podlaha i radiátory</text>
  <!-- Watertank -->
  <rect x="802" y="794" width="196" height="36" rx="18" fill="#34A263"/>
  <text x="900" y="818" text-anchor="middle" font-size="17" font-weight="800" fill="#fff">REO Watertank 210/70</text>
</svg>"""

# ================================================================ STRANY
ICONS = [("sun", "topí ze<br>sluníčka"), ("eff", "SCOP<br>až 5,29"), ("leaf", "chladivo<br>R290"), ("cert", "A+++<br>35 i 55 °C"),
         ("snow", "provoz<br>do −25 °C"), ("temp", "voda<br>až 75 °C"), ("wifi", "Wi-Fi<br>aplikace")]

p1 = f"""
<section class="page cover">
  <div class="cv-glow"></div>
  <div class="cv-top"><img src="{LOGO}" alt="REO HEATING"><div class="qr"><img src="{QR}" alt="reoheating.cz"></div></div>
  <div class="cv-head">
    <div class="eyebrow">Nová řada tepelných čerpadel vzduch–voda</div>
    <h1>REO R290 <span>Smart</span></h1>
    <div class="cv-sub">Česká značka, český servis</div>
  </div>
  <div class="hero"><img src="{HERO}" alt="REO R290 Smart a zásobník REO Watertank">{hero_overlay()}</div>
  <div class="cv-claim">
    <div class="cv-c sun">{ic('sun','ic')}<div><b>Topí přímo ze sluníčka</b><span>panely rovnou do jednotky – bez střídače a baterie</span></div></div>
    <div class="cv-c eff">{ic('eff','ic')}<div><b>SCOP až 5,29</b><span>vysoká účinnost, A+++ pro podlahu i radiátory</span></div></div>
  </div>
  <div class="cv-icons">{''.join(f'<div>{ic(k)}<span>{t}</span></div>' for k,t in ICONS)}</div>
  <div class="cv-bot">
    <div><b>Katalog a ceník 2026</b><span>výkonové modely 6–40 kW · rodinné domy, bytové domy, firmy</span></div>
    <div class="cv-web">reoheating.cz</div>
  </div>
</section>"""

PILL = [
 ("sun", "sun", "Topí přímo ze sluníčka",
  "Obyčejné fotovoltaické panely připojíte přímo k jednotce. Bez střídače, bez baterie, bez další elektroniky. Když svítí, kompresor jede ze sluníčka; co nepokryje, doplní automaticky síť.",
  "U velkých značek tohle nenajdete."),
 ("eff", "eff", f"SCOP až {SCOP35_MAX}",
  f"Z 1 kWh elektřiny až 5,29 kWh tepla pro podlahové topení (35 °C) a až {SCOP55_MAX} kWh pro radiátory (55 °C). Energetická třída A+++ v obou režimech.",
  "Víc než většina značkových R290 monobloků."),
 ("cpu", "mit", "Kompresor Mitsubishi Electric",
  "Srdcem každé jednotky je invertorový kompresor japonské značky Mitsubishi Electric. Plynule mění výkon podle potřeby domu – tiše a bez zbytečného cyklování.",
  "Renomovaná značka, dlouhá životnost."),
]
FEAT = [
 ("drop", "Topí, chladí, ohřívá vodu", "Jedno zařízení na celý rok – zimní vytápění, letní chlazení a teplá voda."),
 ("temp", "Až 75 °C na výstupu", "Zvládne i starší domy s radiátory. Topí až do venkovní teploty −25 °C."),
 ("leaf", "Přírodní chladivo R290", "GWP 3 – splňuje přísná pravidla EU pro chladiva i do budoucna."),
 ("quiet", "Tichý chod", "Kompresor ve třech stupních odhlučnění, noční tichý režim ve 2 úrovních."),
 ("box", "Výbava přímo v jednotce", "Oběhové čerpadlo, záložní dohřev 3 kW, expanze 6 l a pojistný ventil (RH06–RH16)."),
 ("phone", "Ovládání z mobilu", "Dotykový ovladač 7″ a aplikace přes Wi-Fi, přehled spotřeby i vzdálený servis."),
 ("layers", "Kaskáda až 8 jednotek", "Pro bytové domy a firmy, řízení jedním ovladačem, Modbus pro BMS."),
 ("cert", "Certifikát KEYMARK", "Všechny modely ověřené nezávislou evropskou zkušebnou."),
]
p2 = f"""
<section class="page">
  {top('REO R290 Smart', 2)}
  <div class="eyebrow">Proč REO R290 Smart</div>
  <h2 class="ph">Tři důvody, proč si vybrat právě Smart</h2>
  <div class="pil3">
    {''.join(f'<div class="pc {c}"><div class="pci">{ic(k)}</div><h3>{t}</h3><p>{d}</p><div class="pcx">{x}</div></div>' for k,c,t,d,x in PILL)}
  </div>
  <h2 class="ph2">A k tomu</h2>
  <div class="feat">
    {''.join(f'<div class="f"><div class="fi">{ic(k)}</div><div><h4>{t}</h4><p>{d}</p></div></div>' for k,t,d in FEAT)}
  </div>
  <div class="nums">
    <div><b>6–40 kW</b><span>výkonová řada</span></div><div><b>−25 °C</b><span>spodní mez provozu</span></div>
    <div><b>75 °C</b><span>max. teplota vody</span></div><div><b>GWP 3</b><span>chladivo R290</span></div>
    <div><b>8×</b><span>jednotek v kaskádě</span></div>
  </div>
  <div class="who">
    <div>{ic('home')}<b>Rodinné domy</b><span>novostavby i rekonstrukce · RH06–RH16</span></div>
    <div>{ic('bld')}<b>Bytové domy a SVJ</b><span>kaskády RHX20 Pro / RHX30 Pro</span></div>
    <div>{ic('grid')}<b>Firmy a provozovny</b><span>až 8 jednotek, napojení na BMS</span></div>
  </div>
  <div class="foot">SCOP podle EN 14825, průměrné klima; nejvyšší hodnoty v řadě (35 °C RH14, 55 °C RHX20 Pro). Srovnání se značkovými R290 monobloky podle veřejných technických listů výrobců (10/2026). Údaje podle technických podkladů výrobce. {FOOT}</div>
</section>"""

p3 = f"""
<section class="page">
  {top('Topí přímo ze sluníčka', 3)}
  <div class="solar-h">
    <div class="sic">{ic('sun')}</div>
    <div><div class="eyebrow">Jak to funguje</div><h2 class="ph">Topí přímo ze sluníčka</h2>
    <div class="sub">Bez střídače. Bez baterie. Bez drahé elektroniky.</div></div>
  </div>
  <div class="ilrow">{ILU}
  <p class="lead2">Kompresor tepelného čerpadla je největší spotřebič v jednotce – a uvnitř běží na <b>stejnosměrný proud</b>.
  Stejný proud vyrábějí i solární panely. REO R290 Smart je proto umí připojit <b>přímo</b>: panely jdou kabelem rovnou
  do jednotky, bez střídače a bez zbytečných přeměn energie.</p></div>
  <div class="card prin-c">
    <h3>{ic('plug')} Princip uvnitř jednotky</h3>
    {svg_principle()}
    <div class="steps3">
      <div><b>1</b><h4>Panely → deska MPPT</h4><p>Stejnosměrný proud z panelů zpracuje deska MPPT v jednotce. Průběžně hledá nastavení, při kterém panely dávají nejvíc energie – i při mracích.</p></div>
      <div><b>2</b><h4>Sluníčko má přednost</h4><p>Energie z panelů jde na společnou stejnosměrnou sběrnici, ze které se napájí měnič kompresoru. Když svítí dost, kompresor jede jen ze sluníčka.</p></div>
      <div><b>3</b><h4>Síť plynule doplní</h4><p>Co sluníčko nepokryje, dodá síť přes usměrňovač – automaticky a bez přepínání. Čerpadlo topí stejně dobře ve dne i v noci.</p></div>
    </div>
  </div>
  <div class="card cmp-c">
    {svg_compare()}
    <p class="sm">U běžné fotovoltaiky se proud mění dvakrát (na střídavý a v čerpadle zpátky na stejnosměrný) a každá přeměna stojí kus energie.
    U Smart jde energie z panelů rovnou tam, kde se spotřebuje.</p>
  </div>
  <div class="foot">Přímé napájení z FV vyžaduje volitelnou desku MPPT a samostatné panely zapojené do jednoho řetězce (stringu). Ze sluníčka se napájí kompresor a ventilátor; oběhové čerpadlo, řízení a záložní dohřev jsou napájeny ze sítě. {FOOT}</div>
</section>"""

PVT = [("RH06 1F", "3,5 kW", "5 ks · 2,5 kWp"), ("RH08 3F", "4,5 kW", "9 ks · 4,5 kWp"), ("RH10–RH16 3F", "5,5 kW", "10 ks · 5,0 kWp")]
FAQ = [
 ("Potřebuji fotovoltaickou elektrárnu se střídačem?", "Ne. Stačí samotné panely, kabel a jističe na stejnosměrné straně. Odpadá střídač, baterie i žádost o připojení výrobny do sítě – jednotka energii do sítě nevrací."),
 ("Co když nesvítí?", "Nic se nestane. Čerpadlo si chybějící energii plynule vezme ze sítě a topí dál. V noci a v zimních mlhách jede ze sítě jako jakékoli jiné tepelné čerpadlo."),
 ("Kdy ušetřím nejvíc?", "Od jara do podzimu – v přechodném období a na ohřevu teplé vody, kdy čerpadlo běží přes den a panely vyrábějí. V prosinci a lednu je výroba panelů malá."),
 ("Už fotovoltaiku mám. Využiji ji?", "Ano. Čerpadlo umí přes kontakt SG Ready reagovat na přebytky vaší FVE nebo levný tarif – přitopí, nahřeje vodu o 5 °C víc a uloží energii do domu."),
]
p4 = f"""
<section class="page">
  {top('Topí přímo ze sluníčka', 4)}
  <div class="eyebrow">Sluníčko v praxi</div>
  <h2 class="ph">Jak se dělí energie během dne</h2>
  <div class="card day-c">
    {svg_day()}
    <div class="legend"><span><i style="background:#EFB935"></i>kompresor jede ze sluníčka</span><span><i style="background:#C9D3CD"></i>doplní síť</span>
    <span><i class="ln"></i>příkon čerpadla</span><span><i class="ln d"></i>výroba panelů</span></div>
    <p class="sm">Ilustrační průběh slunného jarního dne (FV 5 kWp, čerpadlo topí a ohřívá vodu). Skutečný podíl sluníčka závisí na počasí, ročním období, orientaci panelů a spotřebě domu – nejde o garantovanou úsporu.</p>
  </div>
  <div class="two">
    <div class="card">
      <h3>{ic('sun')} Kolik panelů připojit</h3>
      <table class="mt">
        <tr><th>Model</th><th>Max. výkon FV</th><th>Orientačně (500 Wp)</th></tr>
        {''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a,b,c in PVT)}
      </table>
      <p class="sm">Panely v jednom řetězci, napětí 1F 200–400 V, 3F 250–600 V DC. Přesný počet panelů navrhneme podle konkrétního typu panelu (napětí v mrazu). RHX20 Pro / RHX30 Pro na dotaz.</p>
    </div>
    <div class="card">
      <h3>{ic('check')} Co získáte</h3>
      <ul class="chk">
        <li>levnější teplo a teplá voda za slunečných dnů</li>
        <li>méně techniky: žádný střídač, žádná baterie</li>
        <li>méně přeměn energie – panely napájejí kompresor napřímo</li>
        <li>malá sada panelů na zahradě, pergole nebo garáži</li>
        <li>automatika – nic se nepřepíná, o vše se stará jednotka</li>
      </ul>
    </div>
  </div>
  <div class="faq">
    {''.join(f'<div><h4>{q}</h4><p>{a}</p></div>' for q,a in FAQ)}
  </div>
  <div class="foot">Limity FV vstupu podle podkladů výrobce; návrhová hodnota se volí s rezervou pro napětí panelů v mrazu. Deska MPPT je volitelné příslušenství, panely zapojuje elektrikář s oprávněním. {FOOT}</div>
</section>"""

p5 = f"""
<section class="page">
  {top('Vysoká účinnost', 5)}
  <div class="eyebrow">Vysoká účinnost</div>
  <h2 class="ph">Víc tepla z každé kilowatthodiny</h2>
  <div class="kp">
    <div class="k k35"><span class="kl">podlahové topení 35 °C</span><b>{SCOP35_MAX}</b><span>SCOP – průměrný roční topný faktor</span></div>
    <div class="k k55"><span class="kl">radiátory 55 °C</span><b>{SCOP55_MAX}</b><span>SCOP – průměrný roční topný faktor</span></div>
    <div class="k kx"><span class="kl">energetická třída</span><b>A+++</b><span>pro 35 °C i pro 55 °C</span></div>
  </div>
  <div class="eqrow">
    <div class="q el"><b>1 kWh</b><span>elektřina</span></div><i>+</i>
    <div class="q air"><b>4,29 kWh</b><span>zdarma ze vzduchu</span></div><i>=</i>
    <div class="q heat"><b>5,29 kWh</b><span>tepla do domu</span></div>
    <p><b>Co je SCOP?</b> Kolik tepla vyrobí čerpadlo z 1 kWh elektřiny v průměru za celou topnou sezonu – ve zkušebně podle EN 14825. Čím vyšší číslo, tím nižší účty.</p>
  </div>
  <div class="card">
    <h3>{ic('chart')} SCOP po modelech</h3>
    {svg_scop_bars()}
    <div class="legend"><span><i style="background:#34A263"></i>35 °C – podlahové topení</span><span><i style="background:#D9622B"></i>55 °C – radiátory</span><span>orámováno = nejvyšší hodnota v řadě</span></div>
  </div>
  <div class="two">
    <div class="card tint">
      <h3>{ic('eff')} V kontextu trhu · třída 8–12 kW</h3>
      <div class="bar"><span class="l">SCOP 35 °C</span>
        <div class="rail"><div class="rg" style="left:{(4.89-4.6)/0.9*100:.1f}%;width:{(5.23-4.89)/0.9*100:.1f}%"></div>
        <div class="rs" style="left:{(5.11-4.6)/0.9*100:.1f}%;width:{(5.20-5.11)/0.9*100:.1f}%"></div></div>
        <span class="v">značkové 4,89–5,23 · <b>Smart 5,11–5,20</b></span></div>
      <p class="sm">Smart je nad většinou značkových R290 monobloků stejné velikosti (4 hlavní značky na CZ trhu, veřejné technické listy, 10/2026).</p>
    </div>
    <div class="card">
      <h3>{ic('leaf')} Chladivo R290 – GWP</h3>
      {svg_gwp()}
      <p class="sm">Potenciál globálního oteplování (GWP, 100 let). Přírodní propan R290 je oproti R410A téměř 700× šetrnější.</p>
    </div>
  </div>
  <div class="mitsu">{ic('cpu')}<div><b>Kompresor Mitsubishi Electric</b> v každé jednotce řady – invertorový, plynule moduluje výkon (např. RH10 5,2–12,9 kW), proto běží dlouho na nízké otáčky místo častého zapínání a vypínání. To je jeden z důvodů vysokého SCOP.</div></div>
  <div class="foot">COP podle EN 14511, SCOP a energetická třída podle EN 14825 (průměrné klima) – technická specifikace a ERP protokol výrobce. Skutečná spotřeba závisí na domě, otopné soustavě a způsobu provozu. {FOOT}</div>
</section>"""


def mcard(m):
    n, ph, P, rng, c35, c55, s35, s55, lwa, lp, fuse, kg, r, rozm, price = m
    pro = "Pro" in n
    img = RHX if pro else UNIT
    use = "bytové domy, firmy, kaskády" if pro else f"dům s tepelnou ztrátou cca {P} kW"
    return f"""<div class="mc{' pro' if pro else ''}">
      <img src="{img}" alt="{n}">
      <div class="mn">{n} <small>{ph}</small></div>
      <div class="mu">{use}</div>
      <div class="ms"><span>max. výkon A7/W35</span><b>{rng.split('–')[1]} kW</b></div>
      <div class="ms"><span>modulace</span><b>{rng} kW</b></div>
      <div class="ms"><span>SCOP 35 / 55 °C</span><b>{s35} / {s55}</b></div>
      <div class="ms"><span>hluk L<sub>p</sub> 1 m</span><b>{lp[0]} dB(A)</b></div>
      <div class="mp">{kc(price)}<small>bez DPH</small></div>
    </div>"""


p6 = f"""
<section class="page">
  {top('Modelová řada a ceník', 6)}
  <div class="eyebrow">Modelová řada a ceník</div>
  <h2 class="ph">Vyberte výkon pro svůj dům</h2>
  <div class="mgrid">{''.join(mcard(m) for m in M[:6])}</div>
  <div class="mgrid2">{''.join(mcard(m) for m in M[6:])}
    <div class="card incl">
      <h3>{ic('box')} V ceně jednotky RH06–RH16</h3>
      <ul class="chk">
        <li>venkovní jednotka s kompresorem Mitsubishi Electric</li>
        <li>oběhové čerpadlo, záložní el. dohřev 3 kW</li>
        <li>expanzní nádoba 6 l, pojistný ventil 3 bar</li>
        <li>7″ dotykový ovladač, Wi-Fi a aplikace</li>
      </ul>
      <p class="sm">RHX20 Pro / RHX30 Pro: čerpadlo v jednotce, dohřev a expanze se řeší v kotelně. Montáž, vnitřní hydraulika, zásobníky a deska MPPT se oceňují podle projektu.</p>
    </div>
  </div>
  <div class="hint">{ic('home')}<div><b>Jak vybrat výkon?</b> Jmenovitý výkon modelu (číslo v názvu, např. RH10 = 10 kW) orientačně odpovídá tepelné ztrátě domu – kolik tepla dům potřebuje v největších mrazech. Přesný výkon spočítáme zdarma podle vašeho domu. RH06 je jednofázový (230 V), ostatní modely třífázové (400 V).</div></div>
  <div class="foot">Ceny v Kč bez DPH za venkovní jednotku bez montáže, platné od 10/2026; změny cen vyhrazeny. Max. výkon a modulace při A7/W35, hluk = akustický tlak ve vzdálenosti 1 m podle ErP (35 °C). {FOOT}</div>
</section>"""


def trow(m):
    n, ph, P, rng, c35, c55, s35, s55, lwa, lp, fuse, kg, r, rozm, price = m
    cls = ' class="x"' if n.startswith("RHX") else ""
    return (f'<tr{cls}><td><b>{n} {ph}</b></td><td>{P}</td><td>{rng}</td><td>{c35}</td><td>{c55}</td>'
            f'<td class="h">{s35}</td><td class="h">{s55}</td><td>{lwa[0]} / {lwa[1]}</td><td>{lp[0]} / {lp[1]}</td>'
            f'<td>{fuse}</td><td>{r}</td><td>{kg}</td><td>{rozm}</td></tr>')


CTRL = [
 ("phone", "Dotykový ovladač 7″", "s prostorovým čidlem; režimy, teploty, časové programy, statistiky"),
 ("wifi", "Aplikace přes Wi-Fi", "ovládání odkudkoli, sdílení s rodinou, upozornění na poruchu"),
 ("chart", "Statistiky", "spotřeba a účinnost za den, měsíc i roky"),
 ("grid", "3 topné okruhy", "např. podlaha + radiátory + teplá voda, ekvitermní křivky"),
 ("sun", "SG Ready a HDO", "využije přebytky FVE a levný tarif"),
 ("wrench", "Vzdálený servis", "technik REO vidí provozní data – méně výjezdů"),
]
p7 = f"""
<section class="page">
  {top('Technické údaje', 7)}
  <div class="eyebrow">Technické údaje</div>
  <h2 class="ph">Parametry řady REO R290 Smart</h2>
  <table class="tt">
    <thead><tr><th rowspan="2">Model</th><th rowspan="2">P<sub>jm</sub><br>[kW]</th><th rowspan="2">rozsah<br>A7/W35 [kW]</th>
      <th colspan="2">COP (EN 14511)</th><th colspan="2">SCOP (EN 14825)</th><th rowspan="2">L<sub>WA</sub><br>35/55 [dB(A)]</th>
      <th rowspan="2">L<sub>p</sub> 1 m<br>35/55 [dB(A)]</th><th rowspan="2">jištění<br>[A]</th><th rowspan="2">R290<br>[kg]</th>
      <th rowspan="2">hm.<br>[kg]</th><th rowspan="2">Š×H×V [mm]</th></tr>
      <tr><th>A7/W35</th><th>A7/W55</th><th>35 °C</th><th>55 °C</th></tr></thead>
    <tbody>{''.join(trow(m) for m in M)}</tbody>
  </table>
  <p class="tn">Napájení RH06 1F 230 V, ostatní 400 V 3N~. Jištění RH06–RH16 vč. el. dohřevu 3 kW. Provoz: vytápění −25…35 °C, chlazení −5…43 °C, TUV −25…43 °C venkovní teploty;
  topná voda 25–75 °C; TUV 25–75 °C a chlazení 5–30 °C (RH06–RH16), u RHX Pro TUV 20–70 °C a chlazení 5–25 °C. Přípojky DN25/DN32 (RHX Pro DN40). Kaskáda až 8 jednotek (RS485), Modbus RS485 pro BMS.</p>
  <div class="two hy">
    <div class="card">
      <h3>{ic('layers')} Zapojení v rodinném domě</h3>
      {svg_hydraulics()}
      <p class="sm">Část výbavy je přímo v jednotce (RH06–RH16). Jednotka nenahrazuje vnitřní hydraulické zapojení – ventil pro teplou vodu, filtr, armatury, zásobník a případnou akumulaci navrhneme podle domu.</p>
    </div>
  </div>
  <h3 class="h3s">{ic('phone')} Ovládání a aplikace</h3>
  <div class="ctrl">
    {''.join(f'<div>{ic(k)}<div><h4>{t}</h4><p>{d}</p></div></div>' for k,t,d in CTRL)}
  </div>
  <div class="foot">Údaje podle technické specifikace výrobce; hluk podle ErP / EN 12102. Displej ovladače je v angličtině, český návod popisuje všechny obrazovky. Bezpečnost R290: snímač úniku chladiva standardně, při úniku se kompresor zastaví. {FOOT}</div>
</section>"""

TANKS = [
 ("watertank.png", "Watertank 210/70 l", "Kombinovaný zásobník: 210 l teplé vody + 70 l akumulace v jednom štíhlém tanku. Výměník 3,5 m², v každé nádrži spirála 3 kW.", "⌀ 56 × 190 cm", 39000),
 ("tuv-cut.png", "TUV 200 l nerez", "Zásobník teplé vody, nerez 304, výměník ⌀ 25 mm × 20 m (2,7 m²), izolace 50 mm, spirála 3 kW.", "⌀ 52 × 156 cm", 25000),
 ("tuv-cut.png", "TUV 300 l nerez", "Větší zásobník teplé vody, nerez 304, výměník ⌀ 25 mm × 30 m (4,3 m²), izolace 50 mm.", "⌀ 56 × 186 cm", 30000),
 ("aku-100.png", "AKU 100 l nerez", "Akumulační a vyrovnávací zásobník, nerez 304, izolace 50 mm, spirála 3 kW, více zdrojů tepla.", "⌀ 47 × 104,5 cm", 15000),
]
p8 = f"""
<section class="page">
  {top('Zásobníky a kontakt', 8)}
  <div class="eyebrow">Doplňte sestavu</div>
  <h2 class="ph">Prémiové nerezové zásobníky REO</h2>
  <p class="lead2">Zásobníky z nerezové oceli SUS 304 v kvalitní izolaci – minimální tepelné ztráty, rychlý ohřev vody díky velké ploše výměníku
  a stabilizační podložky proti přenosu vibrací. Navržené pro moderní invertorová tepelná čerpadla.</p>
  <div class="tanks">
    {''.join(f'<div class="tk"><div class="ti"><img src="{uri(i)}" alt="{t}"></div><h4>{t}</h4><p>{d}</p><div class="td">{s}</div><div class="mp">{kc(p)}<small>bez DPH</small></div></div>' for i,t,d,s,p in TANKS)}
  </div>
  <div class="steps">
    <h3>Jak postupujeme</h3>
    <div class="st">
      <div><b>1</b><h4>Konzultace</h4><p>Zavoláte nebo napíšete, probereme dům a vaše představy.</p></div>
      <div><b>2</b><h4>Návrh a nabídka</h4><p>Spočítáme tepelnou ztrátu, navrhneme model, zásobníky i panely.</p></div>
      <div><b>3</b><h4>Montáž</h4><p>Odborná instalace a uvedení do provozu partnerskou firmou REO.</p></div>
      <div><b>4</b><h4>Servis</h4><p>Český servis, vzdálený dohled přes aplikaci, náhradní díly.</p></div>
    </div>
  </div>
  <div class="band">
    <div class="bl">
      <div class="eyebrow" style="color:var(--sun)">Chcete topit ze sluníčka?</div>
      <div class="ctah">Nezávaznou nabídku vám pošleme do 24 hodin.</div>
      <div class="contact">
        <span>{ic('mail','ci')}info@reoheating.cz</span><span>{ic('tel','ci')}+420 774 872 467</span>
        <span>{ic('web','ci')}reoheating.cz</span><span>{ic('pin','ci')}Showroom, prodejna a sklad: Smetanova 555, 739 61 Třinec</span>
      </div>
      <div class="hours">Po–Pá 9:00–16:00 · působíme po celé ČR a na Slovensku</div>
    </div>
    <div class="br"><div class="qr2"><img src="{QR}" alt="QR reoheating.cz"></div><div class="dealer">Váš prodejce</div></div>
  </div>
  <div class="foot">Ceny zásobníků v Kč bez DPH podle e-shopu reoheating.cz (10/2026). Rozměry ⌀ × výška. Obrázky jsou ilustrační. {FOOT}</div>
</section>"""

# ================================================================ CSS
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">')

CSS = """
@page{size:A4;margin:0}
:root{--brand:#34A263;--brand-600:#26804B;--dark:#1A5433;--darker:#123D25;--light:#E9F6EE;--tint:#F5FBF7;
 --sun:#EFB935;--sun-l:#FFF6DA;--heat:#D9622B;--fg:#16241C;--muted:#5C6B62;--line:#DCE6DF}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{font-family:Inter,system-ui,sans-serif;color:var(--fg);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:10mm 12mm 8mm;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column}
.page:last-child{page-break-after:auto}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:5mm}
.top img{height:11mm}
.tag{font-size:7.6pt;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--brand-600);
 border:1px solid var(--brand);border-radius:99px;padding:1.1mm 3.2mm;margin-right:9mm}
.pno{position:absolute;top:11.2mm;right:12mm;width:7mm;height:7mm;border-radius:50%;background:var(--brand);color:#fff;
 font-size:8pt;font-weight:800;display:flex;align-items:center;justify-content:center}
.eyebrow{font-size:8pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--brand-600)}
h2.ph{font-size:20pt;font-weight:800;letter-spacing:-.02em;color:var(--darker);margin:1mm 0 4mm;line-height:1.1}
h2.ph2{font-size:12pt;font-weight:800;color:var(--muted);margin:1mm 0 3mm}
h3{font-size:10.5pt;font-weight:800;color:var(--dark);display:flex;align-items:center;gap:2mm;margin-bottom:2.5mm}
h4{font-size:9.2pt;font-weight:700;color:var(--darker);margin-bottom:.8mm}
p{font-size:8.8pt;line-height:1.45}
.ic{width:5.5mm;height:5.5mm;color:var(--brand);flex:none}
.ci{width:3.6mm;height:3.6mm;vertical-align:-.7mm;margin-right:1.5mm}
.sm{font-size:7.5pt;color:var(--muted);margin-top:2mm;line-height:1.4}
.lead2{font-size:9.6pt;line-height:1.5;margin-bottom:4mm}
.lead2 b{color:var(--darker)}
.card{border:1px solid var(--line);border-radius:4mm;padding:4mm 5mm;margin-bottom:4mm}
.card.tint{background:var(--tint)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
.two .card{margin-bottom:4mm}
.foot{margin-top:auto;padding-top:2.5mm;border-top:1px solid var(--line);font-size:6.5pt;line-height:1.4;color:var(--muted)}
ul.chk{list-style:none}
ul.chk li{position:relative;padding-left:5mm;font-size:8.5pt;line-height:1.4;margin-bottom:1.2mm}
ul.chk li:before{content:"";position:absolute;left:0;top:1.3mm;width:2.4mm;height:1.3mm;border-left:2px solid var(--brand);
 border-bottom:2px solid var(--brand);transform:rotate(-45deg)}
.legend{display:flex;flex-wrap:wrap;gap:1.5mm 5mm;font-size:7.6pt;color:var(--muted);margin-top:1.5mm}
.legend i{display:inline-block;width:4mm;height:2.6mm;border-radius:1mm;margin-right:1.4mm;vertical-align:-.2mm}
.legend i.ln{height:0;border-top:2.5px solid var(--darker);border-radius:0}
.legend i.ln.d{border-top:2px dashed #C98A0C}

/* --- titulka */
.cover{padding:0;background:#fff}
.cv-glow{position:absolute;right:-40mm;top:-40mm;width:150mm;height:150mm;border-radius:50%;
 background:radial-gradient(circle,rgba(255,215,90,.75) 0%,rgba(255,215,90,.25) 40%,rgba(255,215,90,0) 70%)}
.cv-top{position:relative;display:flex;justify-content:space-between;align-items:flex-start;padding:11mm 14mm 0}
.cv-top>img{height:17mm}
.qr{background:#fff;padding:2.2mm;border-radius:3mm;box-shadow:0 1mm 4mm rgba(0,0,0,.08)}
.qr img{width:18mm;height:18mm;display:block}
.cv-head{position:relative;padding:5mm 14mm 0}
.cv-head h1{font-size:42pt;font-weight:800;letter-spacing:-.03em;color:var(--darker);line-height:1;margin:2mm 0 1.5mm}
.cv-head h1 span{color:var(--brand)}
.cv-sub{font-size:13pt;font-weight:600;color:var(--brand-600)}
.hero{position:relative;margin:6mm 10mm 0;border-radius:5mm;overflow:hidden;box-shadow:0 2mm 7mm rgba(18,61,37,.18)}
.hero img{display:block;width:100%}
.hero-ov{position:absolute;inset:0;width:100%;height:100%}
.cv-claim{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:3.5mm;padding:5mm 10mm 0}
.cv-c{display:flex;gap:3mm;align-items:center;border-radius:4mm;padding:3.2mm 4mm}
.cv-c .ic{width:9mm;height:9mm;flex:none}
.cv-c b{display:block;font-size:13pt;font-weight:800;letter-spacing:-.01em}
.cv-c span{font-size:8.2pt;line-height:1.3}
.cv-c.sun{background:var(--sun);color:var(--darker)}.cv-c.sun .ic{color:var(--darker)}
.cv-c.eff{background:var(--darker);color:#fff}.cv-c.eff .ic{color:var(--sun)}
.cv-icons{position:relative;padding:4mm 10mm 0;display:grid;grid-template-columns:repeat(7,1fr);gap:2.5mm}
.cv-icons div{background:#fff;border:1px solid var(--line);border-radius:3mm;padding:2.3mm 1mm 2mm;text-align:center}
.cv-icons .ic{width:6.5mm;height:6.5mm;display:block;margin:0 auto 1.2mm}
.cv-icons span{font-size:7pt;font-weight:700;line-height:1.2;color:var(--darker)}
.cv-bot{position:absolute;left:0;right:0;bottom:0;background:var(--darker);color:#fff;padding:6mm 14mm;display:flex;justify-content:space-between;align-items:center}
.cv-bot b{display:block;font-size:13pt;font-weight:800}
.cv-bot span{font-size:8.8pt;opacity:.85}
.cv-web{font-size:13pt;font-weight:800;color:var(--sun)}

/* --- strana 2 */
.pil3{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin-bottom:5mm}
.pc{border-radius:4mm;padding:5mm 4.8mm;color:#fff;display:flex;flex-direction:column}
.pc.sun{background:var(--sun);color:var(--darker)}.pc.eff{background:var(--brand)}.pc.mit{background:var(--darker)}
.pci{width:11mm;height:11mm;border-radius:50%;background:rgba(255,255,255,.22);display:flex;align-items:center;justify-content:center;margin-bottom:3mm}
.pc .ic{width:6.5mm;height:6.5mm;color:currentColor}
.pc h3{font-size:14pt;color:inherit;line-height:1.15;margin-bottom:2.5mm;letter-spacing:-.01em}
.pc p{font-size:8.7pt;line-height:1.45;flex:1}
.pcx{margin-top:3mm;padding-top:2.5mm;border-top:1px solid rgba(255,255,255,.35);font-size:8.6pt;font-weight:800}
.pc.sun .pcx{border-color:rgba(18,61,37,.25)}
.feat{display:grid;grid-template-columns:1fr 1fr;gap:3mm 5mm;margin-bottom:5mm}
.f{display:flex;gap:3mm;align-items:flex-start}
.fi{flex:none;width:9.5mm;height:9.5mm;border-radius:50%;background:var(--light);display:flex;align-items:center;justify-content:center}
.f p{font-size:8.3pt;color:#33433A;line-height:1.4}
.who{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-bottom:4mm}
.who div{border:1.5px solid var(--brand);border-radius:3.5mm;padding:3.5mm 4mm;display:flex;flex-direction:column;gap:.8mm}
.who .ic{width:7mm;height:7mm;margin-bottom:1mm}
.who b{font-size:10pt;color:var(--darker)}.who span{font-size:8pt;color:var(--muted)}

.nums{display:grid;grid-template-columns:repeat(5,1fr);gap:0;background:var(--tint);border-radius:4mm;padding:4mm 2mm;margin-bottom:5mm}
.nums div{text-align:center;border-left:1px solid var(--line)}.nums div:first-child{border:0}
.nums b{display:block;font-size:16pt;font-weight:800;color:var(--brand-600);letter-spacing:-.02em}
.nums span{font-size:7.6pt;color:var(--muted)}
.feat{margin-bottom:6mm}
/* --- strana 3 a 4 – sluníčko */
.solar-h{display:flex;align-items:center;gap:4mm;margin-bottom:3mm}
.solar-h h2.ph{margin:.5mm 0 .5mm}
.sic{flex:none;width:16mm;height:16mm;border-radius:50%;background:var(--sun);display:flex;align-items:center;justify-content:center}
.sic .ic{width:9mm;height:9mm;color:var(--darker)}
.sub{font-size:10.5pt;font-weight:700;color:var(--brand-600)}
.ilrow{display:grid;grid-template-columns:96mm 1fr;gap:5mm;align-items:center;margin-bottom:4mm}
.ilrow .lead2{margin:0}
.ilu{display:block;width:100%;height:auto;border-radius:3mm}
.prin-c{background:var(--tint);padding:3.5mm 5mm 4mm}
.prin{display:block;width:100%;height:auto;margin:-1mm 0 2mm}
.steps3{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.steps3 b{display:flex;width:7mm;height:7mm;border-radius:50%;background:var(--sun);color:var(--darker);font-weight:800;align-items:center;justify-content:center;font-size:9pt;margin-bottom:1.5mm}
.steps3 p{font-size:8pt;line-height:1.4;color:#33433A}
.cmp-c{padding:3mm 5mm 3.5mm}
.cmpsvg{display:block;width:100%;height:auto}
.day-c{padding:4mm 5mm}
.day{display:block;width:100%;height:auto}
.mt{width:100%;border-collapse:collapse;font-size:8.5pt}
.mt th{text-align:left;font-size:7.2pt;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);font-weight:600;padding:0 0 1.2mm}
.mt td{padding:1mm 0;border-top:1px solid var(--line)}
.faq{display:grid;grid-template-columns:1fr 1fr;gap:3.5mm 5mm;background:var(--sun-l);border:1.5px solid var(--sun);border-radius:4mm;padding:4.5mm 5mm;margin-bottom:4mm}
.faq p{font-size:8.2pt;line-height:1.42;color:#33433A}

/* --- strana 5 – účinnost */
.kp{display:grid;grid-template-columns:1fr 1fr .8fr;gap:4mm;margin-bottom:4mm}
.k{border-radius:4mm;padding:4mm 5mm;color:#fff}
.k.k35{background:var(--brand)}.k.k55{background:var(--heat)}.k.kx{background:var(--darker)}
.k b{display:block;font-size:34pt;font-weight:800;letter-spacing:-.03em;line-height:1.05;margin:1mm 0}
.k span{font-size:8pt;opacity:.9}.k .kl{font-size:8.6pt;font-weight:700;text-transform:uppercase;letter-spacing:.06em;opacity:1}
.eqrow{display:grid;grid-template-columns:auto auto auto auto auto 1fr;align-items:center;gap:2mm;margin-bottom:4mm}
.eqrow i{font-style:normal;font-weight:800;color:var(--muted);font-size:13pt}
.q{border-radius:2.5mm;padding:2.5mm 3.5mm;text-align:center;color:#fff}
.q b{display:block;font-size:11pt;font-weight:800}.q span{font-size:7pt;opacity:.92}
.q.el{background:#8A968F}.q.air{background:#4FA6C9}.q.heat{background:var(--brand)}
.eqrow p{font-size:8pt;color:#33433A;padding-left:3mm;line-height:1.4}
.bars{display:block;width:100%;height:auto}
.gwp{display:block;width:100%;height:auto}
.bar{display:grid;grid-template-columns:17mm 1fr;align-items:center;gap:0 2mm;margin:2mm 0 1mm}
.bar .l{font-size:7.6pt;font-weight:700;grid-row:span 2}
.rail{position:relative;height:5mm;background:#fff;border:1px solid var(--line);border-radius:99px}
.rg{position:absolute;top:.5mm;height:3.8mm;background:#B9C4BD;border-radius:99px}
.rs{position:absolute;top:1.1mm;height:2.6mm;background:var(--brand);border-radius:99px;box-shadow:0 0 0 1px #fff}
.bar .v{font-size:7.4pt;color:var(--muted);margin-top:.8mm}.bar .v b{color:var(--brand-600)}
.mitsu{display:flex;gap:3.5mm;align-items:center;background:var(--darker);color:#fff;border-radius:4mm;padding:4mm 5mm;font-size:8.8pt;line-height:1.45;margin-bottom:4mm}
.mitsu .ic{width:9mm;height:9mm;color:var(--sun)}

/* --- strana 6 – modely */
.mgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:3.5mm;margin-bottom:3.5mm}
.mgrid2{display:grid;grid-template-columns:1fr 1fr 1.25fr;gap:3.5mm;margin-bottom:3.5mm}
.mc{border:1px solid var(--line);border-radius:4mm;padding:2.5mm 4mm 3mm;display:flex;flex-direction:column;background:#fff}
.mc img{height:15mm;object-fit:contain;margin:0 auto 1.5mm}
.mc.pro{background:var(--tint)}
.mc.pro img{height:22mm}
.mn{font-size:15pt;font-weight:800;color:var(--darker);letter-spacing:-.01em}
.mn small{font-size:8pt;font-weight:700;color:#fff;background:var(--brand);border-radius:99px;padding:.4mm 2mm;vertical-align:2.2mm}
.mu{font-size:7.8pt;color:var(--muted);margin-bottom:2mm}
.ms{display:flex;justify-content:space-between;font-size:7.8pt;padding:.8mm 0;border-top:1px solid var(--line)}
.ms span{color:var(--muted)}.ms b{color:var(--darker)}
.mp{margin-top:2mm;font-size:13.5pt;font-weight:800;color:var(--brand-600);letter-spacing:-.01em}
.mp small{font-size:7.5pt;font-weight:600;color:var(--muted);margin-left:1.5mm;letter-spacing:0}
.incl{margin:0;background:var(--tint)}
.incl ul.chk li{font-size:8pt;margin-bottom:.9mm}
.hint{display:flex;gap:3.5mm;align-items:flex-start;background:var(--sun-l);border-left:4px solid var(--sun);border-radius:3mm;padding:3.5mm 4.5mm;font-size:8.5pt;line-height:1.45;margin-bottom:4mm}
.hint .ic{width:7mm;height:7mm;color:var(--darker)}

/* --- strana 7 – technika */
.tt{width:100%;border-collapse:collapse;font-size:7.3pt;margin-bottom:2mm}
.tt th{background:var(--dark);color:#fff;font-weight:600;font-size:6.7pt;padding:1.2mm .8mm;text-align:center;border:1px solid #2c6a49;line-height:1.2}
.tt td{padding:.9mm .8mm;text-align:center;border-bottom:1px solid var(--line);white-space:nowrap}
.tt td:first-child{text-align:left}
.tt tbody tr:nth-child(even) td{background:var(--tint)}
.tt td.h{font-weight:700;color:var(--brand-600)}
.tt tr.x td{border-top:1.5px solid var(--brand)}
.tt tr.x + tr.x td{border-top:1px solid var(--line)}
.tn{font-size:6.9pt;color:var(--muted);line-height:1.4;margin-bottom:3.5mm}
.two.hy{grid-template-columns:1fr}
.hyd{display:block;width:100%;height:auto}
.h3s{margin:0 0 2.5mm}
.ctrl{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-bottom:4mm}
.ctrl>div{display:flex;gap:2.5mm;align-items:flex-start;border:1px solid var(--line);border-radius:3mm;padding:3mm}
.ctrl .ic{width:6mm;height:6mm}
.ctrl p{font-size:7.8pt;line-height:1.35;color:#33433A}

/* --- strana 8 */
.tanks{display:grid;grid-template-columns:repeat(4,1fr);gap:3.5mm;margin-bottom:5mm}
.tk{border:1px solid var(--line);border-radius:4mm;padding:3.5mm 3.5mm 4mm;display:flex;flex-direction:column}
.ti{height:44mm;display:flex;align-items:center;justify-content:center;margin-bottom:2.5mm}
.ti img{max-height:44mm;max-width:100%;object-fit:contain}
.tk p{font-size:7.8pt;line-height:1.38;color:#33433A;flex:1}
.td{font-size:7.6pt;color:var(--muted);margin-top:1.5mm}
.tk .mp{font-size:12.5pt}
.steps{margin-bottom:5mm}
.st{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}
.st b{display:flex;width:8mm;height:8mm;border-radius:50%;background:var(--sun);color:var(--darker);font-weight:800;align-items:center;justify-content:center;font-size:10pt;margin-bottom:2mm}
.st p{font-size:8pt;color:#33433A}
.band{background:var(--darker);color:#fff;border-radius:4mm;padding:6mm 7mm;display:flex;gap:6mm;align-items:center;margin-bottom:4mm}
.bl{flex:1}
.ctah{font-size:15pt;font-weight:800;margin:1mm 0 3mm}
.contact{display:flex;flex-wrap:wrap;gap:2mm 6mm;font-size:9pt;font-weight:600}
.band .ci{color:var(--sun)}
.hours{font-size:8.4pt;opacity:.8;margin-top:2.5mm}
.br{display:flex;flex-direction:column;gap:3mm;align-items:center}
.qr2{background:#fff;padding:2mm;border-radius:2.5mm}.qr2 img{width:22mm;height:22mm;display:block}
.dealer{width:48mm;height:22mm;border:1.5px dashed rgba(255,255,255,.55);border-radius:2.5mm;font-size:7pt;text-transform:uppercase;letter-spacing:.08em;padding:1.5mm 2.5mm;opacity:.85}
"""

def main():
    SLUG = "REO-R290-Smart_katalog"
    html = (f'<!doctype html><html lang="cs"><head><meta charset="utf-8"><title>REO R290 Smart – katalog a ceník | REO HEATING</title>'
            f'{FONTS}<style>{CSS}</style></head><body>{p1+p2+p3+p4+p5+p6+p7+p8}</body></html>')
    out = ROOT / f"{SLUG}.html"
    out.write_text(html, encoding="utf-8")
    pdf = ROOT / f"{SLUG}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("PDF", pdf)

    hero_html = ROOT / "hero-smart-watertank.html"
    hero_html.write_text(f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>html,body{{margin:0}}'
                         f'.hero{{position:relative;width:1186px}}.hero img{{display:block;width:100%}}'
                         f'.hero-ov{{position:absolute;inset:0;width:100%;height:100%}}</style></head>'
                         f'<body><div class="hero"><img src="{HERO}">{hero_overlay()}</div></body></html>', encoding="utf-8")
    png = ROOT / "hero-smart-watertank.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=1186,838", "--virtual-time-budget=8000", f"--screenshot={png}", hero_html.as_uri()],
                   check=True, capture_output=True)
    hero_html.unlink()
    print("PNG", png)


if __name__ == "__main__":
    main()
