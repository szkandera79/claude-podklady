#!/usr/bin/env python3
"""Návrhy titulní strany katalogu REO R290 Smart (varianty hero obrázku).
    python3 navrhy_titulka.py  → navrhy-titulka/navrhy-titulka.pdf + titulka-A…E.png + prehled.png
Sdílí data, ikony a CSS s build.py (A = aktuální titulka katalogu)."""
import subprocess
import build as B

OUT = B.ROOT / "navrhy-titulka"
OUT.mkdir(exist_ok=True)
TANK = B.uri("watertank-cut.png")
ic, LOGO, QR, HERO, UNIT = B.ic, B.LOGO, B.QR, B.HERO, B.UNIT

CLAIMS = f"""<div class="cv-claim">
    <div class="cv-c sun">{ic('sun','ic')}<div><b>Topí přímo ze sluníčka</b><span>panely rovnou do jednotky – bez střídače a baterie</span></div></div>
    <div class="cv-c eff">{ic('eff','ic')}<div><b>SCOP až 5,29</b><span>vysoká účinnost, A+++ pro podlahu i radiátory</span></div></div>
  </div>"""
ICONS = f"""<div class="cv-icons">{''.join(f'<div>{ic(k)}<span>{t}</span></div>' for k,t in B.ICONS)}</div>"""
BOT = """<div class="cv-bot"><div><b>Katalog a ceník 2026</b><span>výkonové modely 6–40 kW · rodinné domy, bytové domy, firmy</span></div>
    <div class="cv-web">reoheating.cz</div></div>"""
HEAD = """<div class="cv-head"><div class="eyebrow">Nová řada tepelných čerpadel vzduch–voda</div>
    <h1>REO R290 <span>Smart</span></h1><div class="cv-sub">Česká značka, český servis</div></div>"""
TOP = f"""<div class="cv-top"><img src="{LOGO}" alt="REO HEATING"><div class="qr"><img src="{QR}" alt="reoheating.cz"></div></div>"""
HERO_BOX = f'<img src="{HERO}" alt="REO R290 Smart a REO Watertank">{B.hero_overlay()}'

V = {}

# A – aktuální: scéna v rámečku na bílé
V["A"] = ("Scéna v rámečku (aktuální)", f"""<section class="page cover">
  <div class="cv-glow"></div>{TOP}{HEAD}
  <div class="hero">{HERO_BOX}</div>{CLAIMS}{ICONS}{BOT}</section>""")

# B – scéna přes celou šířku, výhody v tmavém pásu
V["B"] = ("Scéna přes celou šířku", f"""<section class="page cover vb">
  {TOP}{HEAD}
  <div class="hero full">{HERO_BOX}</div>
  <div class="vb-band">
    <div class="vb-c">{ic('sun','ic')}<div><b>Topí přímo ze sluníčka</b><span>panely rovnou do jednotky – bez střídače a baterie</span></div></div>
    <div class="vb-c">{ic('eff','ic')}<div><b>SCOP až 5,29</b><span>A+++ pro podlahové topení i radiátory</span></div></div>
    <div class="vb-c">{ic('cpu','ic')}<div><b>Mitsubishi Electric</b><span>renomovaný invertorový kompresor</span></div></div>
  </div>
  <div class="vb-foot"><b>Katalog a ceník 2026</b> · výkonové modely 6–40 kW<span>reoheating.cz</span></div>
</section>""")

# C – produktové studio: výřezy jednotky a Watertanku, popisky
V["C"] = ("Produktové studio", f"""<section class="page cover vc">
  <div class="cv-glow"></div>{TOP}{HEAD}
  <div class="stage">
    <div class="floor"></div>
    <img class="st-tank" src="{TANK}" alt="REO Watertank">
    <img class="st-unit" src="{UNIT}" alt="REO R290 Smart">
    <div class="co co-mit"><span class="cb">{ic('cpu','ic')}</span><div><b>Kompresor Mitsubishi Electric</b><span>v každé jednotce REO R290 Smart</span></div></div>
    <div class="co co-tuv"><span class="cb y">{ic('drop','ic')}</span><div><b>Teplá voda</b><span>TUV 210 l – horní část</span></div></div>
    <div class="co co-ut"><span class="cb o">{ic('temp','ic')}</span><div><b>Topná voda</b><span>70 l – podlaha i radiátory</span></div></div>
    <div class="scop-b"><small>SCOP až</small><b>5,29</b><small>35 °C · A+++</small></div>
  </div>
  {CLAIMS}{ICONS}{BOT}</section>""")

# D – sluníčko na prvním místě: ilustrace + jednotka
V["D"] = ("Sluníčko na prvním místě", f"""<section class="page cover vd">
  {TOP}
  <div class="cv-head"><div class="eyebrow">REO R290 Smart · nová řada tepelných čerpadel</div>
    <h1>Topí přímo<br><span>ze sluníčka.</span></h1>
    <div class="cv-sub">Panely rovnou do jednotky – bez střídače a bez baterie.</div></div>
  <div class="vd-ilu">{B.ILU}</div>
  <div class="vd-row">
    <img src="{UNIT}" alt="REO R290 Smart">
    <div class="vd-k">
      <div><b>5,29</b><span>SCOP pro podlahové topení</span></div>
      <div><b>3,97</b><span>SCOP pro radiátory</span></div>
      <div class="m">{ic('cpu','ic')}<span><b>Kompresor Mitsubishi Electric</b></span></div>
    </div>
  </div>
  {BOT}</section>""")

# E – tmavá prémiová
V["E"] = ("Tmavá prémiová", f"""<section class="page cover ve">
  <div class="cv-glow"></div>
  <div class="cv-top"><img src="{LOGO}" class="lg" alt="REO HEATING"><div class="qr"><img src="{QR}" alt=""></div></div>
  {HEAD}
  <div class="hero">{HERO_BOX}</div>{CLAIMS}{ICONS}{BOT}</section>""")

CSS = B.CSS + """
/* B */
.vb .cv-head{padding-bottom:0}
.vb .cv-head h1{font-size:48pt}
.vb .cv-top{padding-top:13mm}
.hero.full{margin:auto 0 0;border-radius:0;box-shadow:none}
.vb-band{background:var(--darker);color:#fff;display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;padding:6mm 10mm}
.vb-c{display:flex;gap:2.5mm;align-items:flex-start}
.vb-c .ic{width:8mm;height:8mm;color:var(--sun)}
.vb-c b{display:block;font-size:11.5pt;font-weight:800}.vb-c span{font-size:7.8pt;opacity:.85;line-height:1.3}
.vb-foot{background:var(--darker);color:#fff;border-top:1px solid rgba(255,255,255,.15);padding:4mm 10mm 6mm;font-size:10pt;display:flex;justify-content:space-between}
.vb-foot span{font-weight:800;color:var(--sun)}
.vb .cv-icons{display:none}
/* C */
.stage{position:relative;height:150mm;margin:2mm 10mm 0}
.floor{position:absolute;left:0;right:0;bottom:4mm;height:22mm;border-radius:50%;background:radial-gradient(ellipse at center,rgba(18,61,37,.16),rgba(18,61,37,0) 70%)}
.st-tank{position:absolute;right:8mm;top:4mm;height:118mm}
.st-unit{position:absolute;left:-2mm;bottom:5mm;width:132mm;filter:drop-shadow(0 4mm 5mm rgba(0,0,0,.25))}
.co{position:absolute;display:flex;gap:2.5mm;align-items:center;background:#fff;border-radius:3.5mm;padding:2.5mm 3.5mm;
 box-shadow:0 1.2mm 4mm rgba(0,0,0,.14);font-size:7.8pt;line-height:1.3}
.co b{display:block;font-size:10pt;color:var(--darker)}.co span{color:var(--muted)}
.cb{flex:none;width:9mm;height:9mm;border-radius:50%;background:var(--darker);display:flex;align-items:center;justify-content:center}
.cb .ic{width:5.5mm;height:5.5mm;color:var(--sun)}
.cb.y{background:var(--sun)}.cb.y .ic{color:var(--darker)}.cb.o{background:var(--heat)}.cb.o .ic{color:#fff}
.co-mit{left:2mm;top:36mm}.co-tuv{right:-4mm;top:20mm}.co-ut{right:-4mm;top:74mm}
.scop-b{position:absolute;left:8mm;top:0;width:34mm;height:34mm;border-radius:50%;background:var(--brand);color:#fff;
 display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 1.5mm 5mm rgba(52,162,99,.4)}
.scop-b b{font-size:24pt;font-weight:800;line-height:1}.scop-b small{font-size:7.5pt;font-weight:700;opacity:.9}
/* D */
.vd{background:#FFFBEF}
.vd .cv-head h1{font-size:40pt}
.vd .cv-head h1 span{color:#E0A21B}
.vd .cv-sub{font-size:12pt;color:var(--darker);font-weight:600}
.vd-ilu{margin:6mm 10mm 0}
.vd-ilu .ilu{display:block;width:100%;border-radius:5mm;box-shadow:0 2mm 6mm rgba(0,0,0,.12)}
.vd-row{display:grid;grid-template-columns:1fr 1fr;gap:6mm;align-items:center;margin:6mm 10mm 0}
.vd-row img{width:100%;filter:drop-shadow(0 4mm 5mm rgba(0,0,0,.22))}
.vd-k{display:flex;flex-direction:column;gap:3mm}
.vd-k>div{border-radius:4mm;padding:3mm 4.5mm;background:var(--brand);color:#fff}
.vd-k>div:nth-child(2){background:var(--heat)}
.vd-k b{display:block;font-size:24pt;font-weight:800;line-height:1.05}.vd-k span{font-size:8.5pt}
.vd-k .m{background:var(--darker);display:flex;gap:3mm;align-items:center}.vd-k .m .ic{width:8mm;height:8mm;color:var(--sun)}
.vd-k .m b{font-size:11pt}
/* E */
.ve{background:var(--darker)}
.ve .cv-top img.lg{height:17mm;background:#fff;border-radius:3mm;padding:2mm 3mm}
.ve .cv-head h1{color:#fff}.ve .cv-head h1 span{color:var(--sun)}
.ve .eyebrow{color:#9FD9B6}.ve .cv-sub{color:#CDEBD8}
.ve .hero{box-shadow:0 0 0 1.2mm var(--sun),0 3mm 10mm rgba(0,0,0,.4)}
.ve .cv-c.eff{background:var(--brand)}
.ve .cv-icons div{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.18)}
.ve .cv-icons span{color:#fff}.ve .cv-icons .ic{color:var(--sun)}
.ve .cv-bot{background:#0B2817}
.ve .cv-glow{opacity:.35}
"""

html = (f'<!doctype html><html lang="cs"><head><meta charset="utf-8"><title>Návrhy titulky – REO R290 Smart</title>'
        f'{B.FONTS}<style>{CSS}</style></head><body>{"".join(v[1] for v in V.values())}</body></html>')
src = OUT / "navrhy-titulka.html"
src.write_text(html, encoding="utf-8")
pdf = OUT / "navrhy-titulka.pdf"
subprocess.run([B.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
                f"--print-to-pdf={pdf}", src.as_uri()], check=True, capture_output=True)
print("PDF", pdf, "–", ", ".join(f"{k}: {v[0]}" for k, v in V.items()))
