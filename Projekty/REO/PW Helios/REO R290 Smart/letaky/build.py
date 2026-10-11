#!/usr/bin/env python3
"""Letáky REO R290 Smart (A4, 2 strany): zákaznický (jednoduchý) a partnerský (technický).
Data = technická specifikace výrobce (EN 14511 / EN 14825, ErP). Výstup: *.html + *.pdf (headless Chrome).
    python3 build.py
"""
import base64, pathlib, subprocess
from ilustrace import SVG as ILU

ROOT = pathlib.Path(__file__).parent
A = ROOT / "assets"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def uri(p):
    return "data:image/png;base64," + base64.b64encode((A / p).read_bytes()).decode()

LOGO, UNIT = uri("logo.png"), uri("jednotka.png")

# --- data (spec. výrobce). P = jmen. výkon A7/W35, rng = rozsah A7/W35, cop35/55 = A7/W35 a A7/W55,
# scop = EN 14825 průměrné klima, lwa/lp = ErP 35/55 °C (lp v 1 m), fuse = jištění vč. el. dohřevu 3 kW
M = [
 # model,   ph,  P,  rng,         cop35, cop55, scop35, scop55, lwa,      lp,       fuse, kg,  r290, rozm
 ("RH06",  "1F", 6,  "3,4–8,5",   "5,04","3,11","5,00","3,84",(52,53),(38,38), 40, 128, "0,6", "1200×465×791"),
 ("RH08",  "3F", 8,  "4,1–11,0",  "4,89","3,04","5,15","3,90",(50,50),(35,34), 25, 165, "0,9", "1328×485×1065"),
 ("RH10",  "3F", 10, "4,2–12,9",  "4,92","3,21","5,20","3,90",(54,55),(39,40), 32, 170, "1,15","1328×485×1065"),
 ("RH12",  "3F", 12, "6,3–17,0",  "5,03","3,35","5,11","3,94",(55,55),(40,40), 40, 178, "1,3", "1328×485×1065"),
 ("RH14",  "3F", 14, "6,6–19,3",  "4,80","3,22","5,29","3,91",(56,55),(41,40), 40, 182, "1,5", "1328×485×1065"),
 ("RH16",  "3F", 16, "7,8–22,0",  "4,90","3,16","5,09","3,88",(55,56),(39,41), 40, 190, "1,7", "1328×485×1065"),
 ("RHX30", "3F", 20, "10,2–28,0", "4,85","2,92","5,23","3,97",(50,56),(35,40), 32, 265, "2,2", "1375×532×1565"),
 ("RHX40", "3F", 30, "12,7–40,0", "4,60","2,80","5,25","3,90",(55,59),(39,42), 40, 328, "3,4", "1550×630×1708"),
]

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
}
def ic(k, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="{IC[k]}"/></svg>')

CONTACT = f"""<div class="contact">
  <span>{ic('mail','ci')}info@reoheating.cz</span>
  <span>{ic('tel','ci')}+420 774 872 467</span>
  <span>{ic('web','ci')}reoheating.cz</span>
  <span>{ic('pin','ci')}Showroom: Smetanova 555, 739 61 Třinec</span>
</div>"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">')

CSS = """
@page{size:A4;margin:0}
:root{--brand:#26804B;--brand-600:#1E6A3D;--dark:#1A5433;--darker:#123D25;--light:#E9F6EE;--tint:#F5FBF7;
 --sun:#EFB935;--fg:#16241C;--muted:#5C6B62;--line:#DCE6DF}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{font-family:Inter,system-ui,sans-serif;color:var(--fg);-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:11mm 12mm 9mm;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column}
.page:last-child{page-break-after:auto}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:5mm}
.top img{height:13mm}
.tag{font-size:8pt;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--brand);
 border:1px solid var(--brand);border-radius:99px;padding:1.2mm 3.2mm}
.eyebrow{font-size:8pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--brand)}
h1{font-size:25pt;line-height:1.08;font-weight:800;letter-spacing:-.02em}
h2{font-size:14pt;font-weight:800;letter-spacing:-.01em;color:var(--dark);margin-bottom:3mm}
h3{font-size:10pt;font-weight:700;color:var(--dark)}
p{font-size:9pt;line-height:1.45}
.ic{width:6mm;height:6mm;color:var(--brand)}
.ci{width:3.6mm;height:3.6mm;vertical-align:-.7mm;margin-right:1.5mm}
.contact{display:flex;flex-wrap:wrap;gap:2mm 6mm;font-size:9pt;font-weight:600}
.foot{margin-top:auto;padding-top:3mm;border-top:1px solid var(--line);font-size:6.6pt;line-height:1.4;color:var(--muted)}
.band{background:var(--dark);color:#fff;border-radius:4mm;padding:6mm 7mm}
.band .contact{color:#fff}.band .ci{color:var(--sun)}
ul.chk{list-style:none}
ul.chk li{position:relative;padding-left:5mm;font-size:8.6pt;line-height:1.4;margin-bottom:1.3mm}
ul.chk li:before{content:"";position:absolute;left:0;top:1.3mm;width:2.4mm;height:1.3mm;border-left:2px solid var(--brand);
 border-bottom:2px solid var(--brand);transform:rotate(-45deg)}
"""

# ============================ ZÁKAZNICKÝ LETÁK ============================
BEN = [
 ("temp","Pro novostavby i starší domy","Ohřeje topnou vodu až na 75 °C, poradí si i s klasickými radiátory. Topí i při −25 °C."),
 ("quiet","Tichý chod","Trojitě odhlučněný kompresor a noční tichý režim. V 1 m jen 34–41 dB(A) podle modelu."),
 ("drop","Topí, chladí a ohřívá vodu","Jedno zařízení na celý rok: v zimě teplo, v létě chlad, celoročně teplá voda."),
 ("phone","Ovládání z mobilu","Barevný dotykový displej a aplikace přes Wi-Fi. Přehled o spotřebě za den, měsíc i rok."),
 ("shield","Ekologické a bezpečné","Přírodní chladivo R290 splňuje přísná pravidla EU. Jednotka sama hlídá případný únik."),
 ("cert","Ověřeno nezávislou zkušebnou","Všechny modely mají evropský certifikát kvality KEYMARK."),
]

cust_p1 = f"""
<section class="page">
  <div class="top"><img src="{LOGO}" alt="REO HEATING"><span class="tag">Tepelná čerpadla vzduch–voda</span></div>
  <div class="hero">
    <div class="hero-txt">
      <div class="eyebrow">Novinka · REO R290 Smart</div>
      <h1>Teplo pro váš dům.<br>Úsporně, spolehlivě<br><span class="hl">a ze slunce.</span></h1>
      <p class="lead">Tepelné čerpadlo vzduch–voda 6–30 kW pro rodinné domy. Topí, chladí a ohřívá vodu – v novostavbě i ve starším domě s radiátory.</p>
    </div>
    <div class="hero-img"><img src="{UNIT}" alt="Tepelné čerpadlo REO R290 Smart"></div>
  </div>

  <div class="pil">
    <div class="pc sun">
      <div class="pt">{ic('sun','ic')}<span>Topí přímo ze slunce</span></div>
      <div class="big">bez střídače<br>a baterií</div>
      <p>Připojte k čerpadlu obyčejné solární panely – nic dalšího nepotřebujete. Když svítí, topí jen ze slunce. Co chybí, vezme si samo ze sítě. <b>U velkých značek tepelných čerpadel tohle nenajdete.</b></p>
    </div>
    <div class="pc eff">
      <div class="pt">{ic('eff','ic')}<span>Ušetří víc než konkurence</span></div>
      <div class="big">SCOP až 5,29*</div>
      <p>Z 1 kWh elektřiny až 5,29 kWh tepla – víc než u většiny značkových tepelných čerpadel. Méně elektřiny za stejné teplo = nižší účty.</p>
    </div>
    <div class="pc mit">
      <div class="pt">{ic('cpu','ic')}<span>Srdce od Mitsubishi Electric</span></div>
      <div class="big">kompresor<br>Mitsubishi Electric</div>
      <p>Celé čerpadlo je postavené na kompresoru japonské značky Mitsubishi Electric. Renomovaný výrobce, spolehlivost a dlouhá životnost.</p>
    </div>
  </div>

  <h2 class="sec">A k tomu</h2>
  <div class="ben">
    {''.join(f'<div class="b"><div class="bi">{ic(k)}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for k,t,d in BEN)}
  </div>
    <div class="card tech">
      <h2>{ic('box','ic')} Část technologie přímo v jednotce – v domě ušetříte místo</h2>
      <ul class="chk c2">
        <li>oběhové čerpadlo s úsporným motorem</li>
        <li>elektrický dohřev 3 kW jako zálohu pro největší mrazy</li>
        <li>expanzní nádobu, pojistný a odvzdušňovací ventil</li>
        <li>vyhřívanou základnu proti zamrzání v zimě</li>
      </ul>
      <p class="sm">V domě se doplní ventil pro ohřev vody, filtr, zásobník teplé vody a další prvky – podle návrhu pro váš dům.</p>
    </div>
  <div class="foot">* SCOP = průměrný poměr vyrobeného tepla a spotřebované elektřiny za celou topnou sezonu podle EN 14825
  (průměrné klima, podlahové topení 35 °C, nejvyšší hodnota v řadě). Srovnání se značkovými R290 tepelnými čerpadly
  podle veřejných technických listů výrobců (10/2026). Hodnoty podle technických podkladů výrobce.</div>
</section>"""

ROWS_C = [("RH06","6 kW","8,5 kW","cca 6 kW"),("RH08","8 kW","11,0 kW","cca 8 kW"),("RH10","10 kW","12,9 kW","cca 10 kW"),("RH12","12 kW","17,0 kW","cca 12 kW"),
          ("RH14","14 kW","19,3 kW","cca 14 kW"),("RH16","16 kW","22,0 kW","cca 16 kW"),
          ("RHX30","20 kW","28,0 kW","cca 20 kW"),("RHX40","30 kW","40,0 kW","cca 30 kW")]

cust_p2 = f"""
<section class="page">
  <div class="top"><img src="{LOGO}" alt="REO HEATING"><span class="tag">REO R290 Smart</span></div>

  <div class="solar">
    <div class="sh">{ic('sun','ic sic')}<div><h2>Topí přímo ze slunce</h2>
      <div class="sub">Bez střídače. Bez baterií. Bez drahé elektroniky.</div></div></div>
    {ILU}
    <div class="scopln"><b>SCOP 5,29</b> = z 1 kWh elektřiny až 5,29 kWh tepla. Zbytek bere čerpadlo zdarma ze vzduchu – a tu 1 kWh mu může dodat slunce.</div>
    <p class="sn"><b>Velké značky tepelných čerpadel tohle nenabízejí</b> – u nich potřebujete celou fotovoltaickou elektrárnu se střídačem. Už fotovoltaiku máte? Čerpadlo využije i její přebytky.</p>
    <p class="sm">Nejvíc ušetříte od jara do podzimu, hlavně na ohřevu vody. Panely jsou volitelné, zapojí je elektrikář.</p>
  </div>

    <div class="card models">
      <h2>{ic('grid','ic')} Výběr modelu</h2>
      <table class="mt">
        <tr><th>Model</th><th>Jmenovitý výkon</th><th>Max. výkon (A7/W35)</th><th>Pro dům s tepelnou ztrátou</th></tr>
        {''.join(f'<tr><td><b>{m}</b></td><td>{p}</td><td>{x}</td><td>{v}</td></tr>' for m,p,x,v in ROWS_C)}
      </table>
      <p class="sm"><b>Tepelná ztráta</b> = kolik tepla dům potřebuje v největších mrazech; přesný výkon spočítáme podle vašeho domu.
      RH06 je jednofázový (230 V), ostatní modely třífázové (400 V). Pro větší objekty lze propojit až 8 jednotek.</p>
    </div>
  <div class="band cta">
    <div><div class="eyebrow" style="color:var(--sun)">Chcete vědět víc?</div>
    <div class="ctah">Ozvěte se nám – navrhneme řešení pro váš dům.</div>
    <p class="ctap">Nezávazná konzultace · výkon spočítáme podle tepelné ztráty domu · odborná montáž · servis</p></div>
    {CONTACT}
  </div>

  <div class="foot">Hodnoty podle technických podkladů výrobce (EN 14511, EN 14825 – průměrné klima; hluk podle ErP, akustický tlak v 1 m).
  Skutečná spotřeba závisí na domě, otopné soustavě a způsobu provozu. Přímé napájení z FV je volitelné příslušenství.
  Změny vyhrazeny. REO HEATING · Riva Trade s.r.o., IČ 08864811 · 10/2026</div>
</section>"""

CSS_C = CSS + """
.hero{display:grid;grid-template-columns:1.15fr .85fr;gap:4mm;align-items:center;background:var(--tint);
 border-radius:5mm;padding:4.5mm 6mm 4.5mm 8mm;margin-bottom:4mm}
.hero h1{margin:2mm 0 2.5mm;color:var(--darker);font-size:22pt}
.hl{color:var(--brand)}
.lead{font-size:10.2pt;line-height:1.45;color:var(--fg)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:2.5mm}
.stats div{background:#fff;border-radius:3mm;padding:2.8mm 3mm;border:1px solid var(--line)}
.stats b{display:block;font-size:15pt;font-weight:800;color:var(--brand);letter-spacing:-.02em}
.stats span{font-size:7.4pt;color:var(--muted);line-height:1.25;display:block;margin-top:.6mm}
.hero-img img{width:100%;mix-blend-mode:multiply}
h2.sec{font-size:12pt;margin-bottom:3mm;color:var(--muted)}
.ben{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm 4mm;margin-bottom:2mm}
.b{display:flex;gap:3mm;align-items:flex-start;padding:3.2mm 3.5mm;border:1px solid var(--line);border-radius:3.5mm}
.bi{flex:none;width:9mm;height:9mm;border-radius:50%;background:var(--light);display:flex;align-items:center;justify-content:center;margin-bottom:2.5mm}
.b h3{margin-bottom:.8mm;font-size:9.2pt}
.b p{font-size:8.4pt;color:#33433A;line-height:1.42}
.two{display:grid;grid-template-columns:1fr 1fr;gap:4.5mm;margin-bottom:4mm}
.card{border:1px solid var(--line);border-radius:4mm;padding:4.5mm 5.5mm}
.card h2{display:flex;align-items:center;gap:2mm;font-size:12.5pt}
.card.scop{background:var(--tint)}
.eq{display:flex;align-items:center;gap:1.6mm;margin:3mm 0 2.5mm}
.eq i{font-style:normal;font-weight:800;color:var(--muted);font-size:12pt}
.q{flex:1;border-radius:2.5mm;padding:2.5mm 1.5mm;text-align:center;color:#fff}
.q b{display:block;font-size:11pt;font-weight:800}.q span{font-size:7pt;opacity:.9}
.q.el{background:#8A968F}.q.air{background:#4FA6C9}.q.heat{background:var(--brand);flex:1.2}
.sm{font-size:7.8pt;color:var(--muted);margin-top:2mm}
.mt{width:100%;border-collapse:collapse;font-size:8.6pt}
.mt th{text-align:left;font-size:7.4pt;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:600;padding:0 0 1.2mm}
.mt td{padding:.55mm 0;border-top:1px solid var(--line)}
.steps{margin-bottom:5mm}
.st{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}
.st>div{position:relative;padding-top:1mm}
.st b{display:flex;width:8mm;height:8mm;border-radius:50%;background:var(--sun);color:var(--darker);font-weight:800;
 align-items:center;justify-content:center;font-size:10pt;margin-bottom:2mm}
.st h3{font-size:9.2pt;margin-bottom:.8mm}.st p{font-size:8pt;color:#33433A}
.cta{display:flex;flex-direction:column;gap:2mm;margin-bottom:2mm;padding:3.8mm 7mm}
.sunpill{display:inline-flex;align-items:center;gap:2mm;background:var(--sun);color:var(--darker);border-radius:99px;
 padding:1.6mm 4mm 1.6mm 2.6mm;font-size:9.6pt;margin-top:2.5mm}
.sunpill .ic{width:5mm;height:5mm;color:var(--darker)}
.b.hot{background:#FFF6DA;border:1.5px solid var(--sun)}
.b.hot .bi{background:var(--sun)}.b.hot .ic{color:var(--darker)}
.solar{background:#FFF6DA;border:2px solid var(--sun);border-radius:5mm;padding:4mm 5.5mm;margin-bottom:3.5mm}
.sh{display:flex;align-items:center;gap:3.5mm;margin-bottom:2.5mm}
.sic{width:12mm!important;height:12mm!important;color:var(--darker)!important;background:var(--sun);border-radius:50%;padding:2mm}
.sh h2{font-size:17pt;margin:0;color:var(--darker)}
.sub{font-size:10.5pt;font-weight:700;color:var(--brand-600)}
.flow{background:#fff;border-radius:3mm;padding:2.5mm 4mm;margin-bottom:3mm}
.fl{display:flex;align-items:center;gap:1.6mm;font-size:8.6pt;padding:1.4mm 0}
.fl+.fl{border-top:1px dashed var(--line)}
.fk{width:31mm;font-weight:700;color:var(--muted);font-size:8.2pt}
.fl.ok .fk{color:var(--brand-600)}
.c{background:#EEF2EF;border-radius:2mm;padding:1.2mm 2.4mm;font-weight:600}
.c.x{background:#F6E1DC;color:#A0412D;text-decoration:line-through}
.c.g{background:var(--brand);color:#fff}
.fl i{font-style:normal;color:var(--muted)}
.done{margin-left:2mm;font-weight:700;color:var(--brand-600)}
.sp{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm}
.sp b{display:block;font-size:9pt;color:var(--darker);margin-bottom:.8mm}
.sp p{font-size:8pt;line-height:1.35;color:#33433A}
.solar .sm{margin-top:1.2mm}
.card.tech{margin-bottom:3.5mm;padding:3.5mm 5.5mm}
.card.models{margin-bottom:3.5mm;padding:3.5mm 5.5mm}
.card.models .mt th{white-space:nowrap}
.ilu{display:block;width:100%;height:auto;margin:.5mm 0 2.5mm}
.sn{font-size:9pt;line-height:1.45}
.scopln{background:#fff;border-radius:2.5mm;padding:2.2mm 3.5mm;font-size:9.2pt;margin-bottom:2.5mm}
.scopln b{color:var(--brand-600)}
.pil{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin-bottom:4mm}
.pc{border-radius:4mm;padding:4mm 4.5mm 4.5mm;color:#fff}
.pc.sun{background:var(--sun);color:var(--darker)}
.pc.eff{background:var(--brand)}
.pc.mit{background:var(--darker)}
.pt{display:flex;align-items:center;gap:2mm;font-size:9pt;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.pc .ic{width:6mm;height:6mm;color:currentColor}
.big{font-size:16pt;font-weight:800;line-height:1.1;letter-spacing:-.02em;margin:2.5mm 0 2mm;min-height:12mm}
.pc p{font-size:8.8pt;line-height:1.42;opacity:.95}
.cmp{margin:1mm 0 0}
.cr{display:grid;grid-template-columns:34mm 1fr 15mm;align-items:center;gap:2mm;font-size:8pt;margin-bottom:1.6mm}
.cr b{font-size:9pt;text-align:right}
.cb{height:3.4mm;background:#fff;border-radius:99px;border:1px solid var(--line);overflow:hidden}
.cb i{display:block;height:100%;background:#B9C4BD}
.cr.me{font-weight:700;color:var(--brand-600)}.cr.me .cb i{background:var(--brand)}
.ctap{font-size:9pt;opacity:.85;margin-top:1.5mm}
ul.c2{columns:2;column-gap:6mm}
.ctah{font-size:15pt;font-weight:800;margin-top:1mm}
"""

# ============================ PARTNERSKÝ LETÁK ============================
def trow(m):
    n, ph, P, rng, c35, c55, s35, s55, lwa, lp, fuse, kg, r, rozm = m
    cls = ' class="x"' if n.startswith("RHX") else ""
    return (f'<tr{cls}><td><b>{n} {ph}</b></td><td>{P}</td><td>{rng}</td><td>{c35}</td><td>{c55}</td>'
            f'<td class="h">{s35}</td><td class="h">{s55}</td><td>{lwa[0]} / {lwa[1]}</td><td>{lp[0]} / {lp[1]}</td>'
            f'<td>{fuse}</td><td>{r}</td><td>{kg}</td><td>{rozm}</td></tr>')

PV = [("RH06 1F","200–400","13","3,5"),("RH08 3F","250–600","13","4,5"),
      ("RH10–16 3F","250–600","13","5,5")]

part_p1 = f"""
<section class="page">
  <div class="top"><img src="{LOGO}" alt="REO HEATING"><span class="tag">Pro instalační partnery</span></div>
  <div class="phead">
    <div>
      <div class="eyebrow">Nová řada · monoblok vzduch–voda R290</div>
      <h1>REO R290 Smart</h1>
      <p class="plead">Monoblok 6–30 kW: RH06 1F 230 V, RH08–RH16 3F 400 V, RHX30 / RHX40 (20 / 30 kW) 3F. Integrovaný záložní dohřev 3 kW a pojistná výbava, SG Ready, Modbus.</p>
    </div>
    <img src="{UNIT}" alt="REO R290 Smart">
  </div>

  <div class="pil">
    <div class="pc sun">
      <div class="pt">{ic('sun','ic')}<span>FV přímo do kompresoru</span></div>
      <div class="big">bez střídače a baterie</div>
      <p>DC vstup přes desku MPPT (1F 200–400 V, 3F 250–600 V DC), 3,5–5,5 kW FV. Kombinace FV + síť automaticky.
      <b>Hlavní značkové řady na CZ trhu tuto funkci nenabízejí.</b></p>
    </div>
    <div class="pc eff">
      <div class="pt">{ic('eff','ic')}<span>Úspornější než většina značek</span></div>
      <div class="big">SCOP 35 °C až 5,29</div>
      <p>Třída 8–12 kW: <b>Smart 5,11–5,20</b> – nad 3 ze 4 hlavních značek (4,89–5,09), na úrovni nejlepší (5,23). A+++ i pro 55 °C.</p>
    </div>
    <div class="pc mit">
      <div class="pt">{ic('cpu','ic')}<span>Renomovaný kompresor</span></div>
      <div class="big">Mitsubishi Electric</div>
      <p>Kompresor japonské značky v celé řadě, DC inverter (RHX30/40: APB100 / APB119). Plynulá modulace, např. RH10 4,2–12,9 kW při A7/W35.</p>
    </div>
  </div>
  <div class="facts"><span><b>A+++</b> 35 i 55 °C</span><span><b>75 °C</b> výstup topné vody</span><span><b>−25 °C</b> spodní mez provozu</span>
    <span><b>KEYMARK</b> všechny modely</span><span><b>kaskáda</b> až 8 jednotek</span></div>

  <div class="cols">
    <div>
      <div class="blk"><h3>{ic('cpu','ic')} Chladivový okruh</h3><ul class="chk">
        <li>DC inverter kompresor <b>Mitsubishi Electric</b> (komerční: APB100 / APB119)</li>
        <li>EEV Fujikoki, 4cestný ventil Sanhua, snímač NT Saginomiya</li>
        <li>deskový výměník AISI 316L, výparník s hydrofilní úpravou lamel, DC ventilátor</li>
        <li>R290 (GWP 3), náplň 0,6–1,7 kg (RHX 2,2 / 3,4 kg)</li>
        <li>odtávání s vyhřívanou základovou vanou proti zamrzání kondenzátu</li>
        <li>odhlučnění kompresoru ve 3 stupních (pružné uložení, tlumicí obal, izolační kryt) + PU izolace plechů</li>
      </ul></div>
      <div class="blk"><h3>{ic('box','ic')} Integrovaná hydraulická výbava (6–16 kW)</h3><ul class="chk">
        <li>DC oběhové čerpadlo Shimge, dopravní výška 9 / 12 m</li>
        <li>el. dohřev 3 kW (IBH), expanzní nádoba 6 l, pojistný ventil 3 bar, odvzdušňovač, průtokový spínač</li>
        <li>manometr vody + VT manometr chladiva přímo v jednotce</li>
        <li>přípojky DN25/DN32 a kabelové průchodky vzadu dole</li>
        <li><b>nenahrazuje vnitřní hydraulické zapojení</b>: trojcestný ventil TUV, filtrace, uzavírací armatury, zásobník TUV, příp. akumulace a doplňková expanze se navrhují dle projektu</li>
      </ul></div>
      <div class="blk"><h3>{ic('shield','ic')} Bezpečnost R290</h3><ul class="chk">
        <li>snímač úniku chladiva standardně: při 15 % LFL alarm, stop kompresoru a el. ohřevů, ventilátor na min.</li>
        <li>automatický odvzdušňovač odvede případný únik z deskového výměníku mimo vodní okruh v domě</li>
      </ul></div>
    </div>
    <div>
      <div class="blk"><h3>{ic('grid','ic')} Řízení a integrace</h3><ul class="chk">
        <li>7" dotykový kabelový ovladač s prostorovým čidlem, Wi-Fi aplikace + IoT vzdálený dohled</li>
        <li>3 teplotní zóny (A / B1 / B2), řízení 4 třícestných/směšovacích ventilů a čerpadel zón, TUV, cirkulace, solár</li>
        <li>ekvitermní regulace: 8 předvoleb + 1 uživatelská křivka pro topení i chlazení</li>
        <li><b>SG Ready + EVU (HDO)</b>: blokace, normál, přednostní ohřev TUV (+5 K, max. 70 °C)</li>
        <li><b>Modbus RS485 / BMS</b>, dálkové omezení příkonu kompresoru bez vypnutí jednotky</li>
        <li>výstup pro bivalentní zdroj (AHS), topná vložka zásobníku (TBH)</li>
        <li>statistika spotřeby a účinnosti (24 h – 10 let), sušení podlahy, dovolená, antilegionela, tichý režim ve 2 stupních</li>
      </ul></div>
      <div class="blk"><h3>{ic('layers','ic')} Kaskáda</h3><ul class="chk">
        <li>až 8 jednotek přes RS485, jeden ovladač (master #0 + 7 slave)</li>
        <li>stupňování výkonu podle ΔT vody, záloha při poruše jednotky, volitelný počet jednotek pro TUV</li>
      </ul></div>
      <div class="blk"><h3>{ic('sun','ic')} FV přímo do kompresoru (volitelná deska MPPT)</h3>
        <table class="pv"><tr><th>Model</th><th>U<sub>oc</sub> [V DC]</th><th>I<sub>max</sub> [A]</th><th>P<sub>max</sub> [kW]</th></tr>
        {''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a,b,c,d in PV)}</table>
        <p class="sm">Bez střídače a baterie – samostatné panely přímo do jednotky. Při nedostatku FV výkonu kompresor plynule dobírá ze sítě. Přínos je největší v přechodném období a pro TUV.</p></div>
    </div>
  </div>
</section>"""

part_p2 = f"""
<section class="page">
  <div class="top"><img src="{LOGO}" alt="REO HEATING"><span class="tag">REO R290 Smart · technické údaje</span></div>
  <h2>Technické parametry</h2>
  <table class="tt">
    <thead><tr><th rowspan="2">Model</th><th rowspan="2">P<sub>jm</sub><br>[kW]</th><th rowspan="2">rozsah<br>A7/W35 [kW]</th>
      <th colspan="2">COP (EN 14511)</th><th colspan="2">SCOP (EN 14825)</th><th rowspan="2">L<sub>WA</sub><br>35/55 [dB(A)]</th>
      <th rowspan="2">L<sub>p</sub> 1 m<br>35/55 [dB(A)]</th><th rowspan="2">jištění<br>[A]</th><th rowspan="2">R290<br>[kg]</th>
      <th rowspan="2">hm.<br>[kg]</th><th rowspan="2">Š×H×V [mm]</th></tr>
      <tr><th>A7/W35</th><th>A7/W55</th><th>35 °C</th><th>55 °C</th></tr></thead>
    <tbody>{''.join(trow(m) for m in M)}</tbody>
  </table>
  <p class="tn">P<sub>jm</sub> = jmenovitý výkon (A7/W35), orientačně odpovídá tepelné ztrátě objektu; maximální výkon viz rozsah. Napájení RH06 1F 230 V, ostatní 400 V 3N~. Jištění 6–16 kW vč. el. dohřevu 3 kW (dohřev je jednofázový 230 V i u 3F modelů, cca 13,8 A). RHX30 / RHX40 = jmenovitě 20 / 30 kW (max. 28 / 40 kW), DN40,
  čerpadlo Shinhoo 13 / 15 m. Rozsah provozu: vytápění −25…35 °C, chlazení −5…43 °C, TUV −25…43 °C; voda: topení 25–75 °C, TUV 20–70 °C, chlazení 5–25 °C.
  TUV (A20, 15→55 °C): COP 4,3–5,3, 205–903 l/h. Chlazení A35/W18: EER 4,75–5,18.</p>

  <div class="pgrid">
    <div class="card mkt">
      <h3>Účinnost v kontextu trhu · 8–12 kW</h3>
      <div class="bar"><span class="l">SCOP 35 °C</span>
        <div class="rail"><div class="rg" style="left:{(4.89-4.6)/0.9*100:.1f}%;width:{(5.23-4.89)/0.9*100:.1f}%"></div>
        <div class="rs" style="left:{(5.11-4.6)/0.9*100:.1f}%;width:{(5.20-5.11)/0.9*100:.1f}%"></div></div>
        <span class="v">trh 4,89–5,23 · <b>Smart 5,11–5,20</b></span></div>
      <div class="bar"><span class="l">SCOP 55 °C</span>
        <div class="rail"><div class="rg" style="left:{(3.70-3.5)/0.6*100:.1f}%;width:{(4.02-3.70)/0.6*100:.1f}%"></div>
        <div class="rs" style="left:{(3.90-3.5)/0.6*100:.1f}%;width:{(3.94-3.90)/0.6*100:.1f}%"></div></div>
        <span class="v">trh 3,70–4,02 · <b>Smart 3,90–3,94</b></span></div>
      <p class="sm"><span class="lg g"></span>značkové monobloky R290 (4 hlavní značky na CZ trhu)<br>
      <span class="lg s" style="margin-left:0"></span>REO R290 Smart. Zdroj: veřejné technické a ErP listy výrobců, 10/2026.</p>
    </div>
    <div class="card">
      <h3>Argumenty pro vaše zákazníky</h3>
      <ul class="chk">
        <li><b>Topí přímo ze slunce</b> – obyčejné panely rovnou do jednotky, bez střídače a baterie. U velkých značek zákazník tuto funkci nenajde.</li>
        <li><b>Ušetří víc než většina značkových</b> – SCOP 35 °C až 5,29, A+++ i pro 55 °C.</li>
        <li><b>Srdce od Mitsubishi Electric</b> – kompresor japonské značky, kterou zákazník zná.</li>
        <li><b>Rekonstrukce</b> – 75 °C na výstupu, provoz do −25 °C.</li>
        <li><b>Bytové domy a SVJ</b> – kaskáda až 8 jednotek, Modbus/BMS.</li>
      </ul>
    </div>
  </div>

  <div class="pgrid">
    <div class="card">
      <h3>{ic('wrench','ic')} Montáž a servis</h3>
      <ul class="chk">
        <li>uživatelská svorkovnice přístupná po sejmutí bočního panelu</li>
        <li>ruční test komponent a „Function Debug“ (čerpadlo, topení, chlazení, TUV) přímo v ovladači</li>
        <li>servisní náhled: teploty, nízký tlak, otevření EEV, verze desek, historie poruch</li>
        <li>vzdálená diagnostika přes IoT – méně výjezdů</li>
      </ul>
    </div>
    <div class="card">
      <h3>{ic('cert','ic')} Co od REO HEATING dostanete</h3>
      <ul class="chk">
        <li>český instalační a uživatelský návod, prezentace a datové listy</li>
        <li>certifikáty KEYMARK (041-K032-23 až -31) a ErP dokumentaci</li>
        <li>technickou podporu při návrhu a uvedení do provozu</li>
        <li>partnerské podmínky na vyžádání</li>
      </ul>
    </div>
  </div>

  <div class="band pcta">
    <div class="ctah">Staňte se partnerem REO HEATING</div>
    {CONTACT}
  </div>

  <div class="foot">Údaje podle technické specifikace výrobce: COP podle EN 14511, SCOP a energetická třída podle EN 14825 (průměrné klima),
  hluk podle ErP / EN 12102 (L<sub>p</sub> v 1 m). Rozhraní ovladače je v angličtině; český návod obsahuje popis všech obrazovek a parametrů.
  Přímé napájení z FV vyžaduje volitelnou desku MPPT. Změny vyhrazeny. REO HEATING · Riva Trade s.r.o., IČ 08864811 · 10/2026</div>
</section>"""

CSS_P = CSS + """
.page{padding:10mm 11mm 8mm}
.top{margin-bottom:4mm}
.phead{display:grid;grid-template-columns:1fr 55mm;gap:4mm;align-items:center;margin-bottom:4mm}
.phead h1{font-size:27pt;color:var(--darker);margin:1.5mm 0 2mm}
.phead img{width:100%;mix-blend-mode:multiply}
.plead{font-size:9.6pt;line-height:1.45}
.kpi{display:grid;grid-template-columns:repeat(6,1fr);gap:2mm;margin-bottom:6mm}
.kpi div{background:var(--dark);color:#fff;border-radius:2.5mm;padding:2.8mm 2.6mm}
.kpi b{display:block;font-size:13.5pt;font-weight:800;letter-spacing:-.02em;color:#fff}
.kpi div:last-child b{font-size:11.2pt;padding:1.1mm 0 .6mm}
.kpi span{display:block;font-size:6.6pt;line-height:1.3;opacity:.85;margin-top:.6mm}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.blk{margin-bottom:3.5mm}
.blk h3{display:flex;align-items:center;gap:1.8mm;margin-bottom:2mm;padding-bottom:1.5mm;border-bottom:2px solid var(--light)}
.blk .ic{width:5mm;height:5mm}
ul.chk li{font-size:8pt;margin-bottom:1mm}
.blk ul.chk li{font-size:8pt;margin-bottom:1mm}
.pv{width:100%;border-collapse:collapse;font-size:8pt}
.pv th{text-align:left;color:var(--muted);font-weight:600;font-size:7pt;padding-bottom:.8mm}
.pv td{padding:.7mm 0;border-top:1px solid var(--line)}
.sm{font-size:7.2pt;color:var(--muted);margin-top:1.5mm;line-height:1.4}
.tt{width:100%;border-collapse:collapse;font-size:7.3pt;margin-bottom:2mm}
.tt th{background:var(--dark);color:#fff;font-weight:600;font-size:6.7pt;padding:1.2mm .8mm;text-align:center;border:1px solid #2c6a49;line-height:1.2}
.tt td{padding:.7mm .8mm;text-align:center;border-bottom:1px solid var(--line);white-space:nowrap}
.tt td:first-child{text-align:left}
.tt tbody tr:nth-child(even) td{background:var(--tint)}
.tt td.h{font-weight:700;color:var(--brand-600)}
.tt tr.x td{border-top:1.5px solid var(--brand)}
.tt tr.x + tr.x td{border-top:1px solid var(--line)}
.tn{font-size:6.9pt;color:var(--muted);line-height:1.4;margin-bottom:3.5mm}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-bottom:3.5mm}
.card{border:1px solid var(--line);border-radius:3.5mm;padding:4.2mm 4.8mm}
.card h3{display:flex;align-items:center;gap:1.8mm;margin-bottom:2.5mm}
.card .ic{width:5mm;height:5mm}
.mkt{background:var(--tint)}
.bar{display:grid;grid-template-columns:17mm 1fr;align-items:center;gap:0 2mm;margin-bottom:3.2mm}
.bar .l{font-size:7.6pt;font-weight:700;grid-row:span 2}
.rail{position:relative;height:5mm;background:#fff;border:1px solid var(--line);border-radius:99px}
.rg{position:absolute;top:.5mm;height:3.8mm;background:#B9C4BD;border-radius:99px}
.rs{position:absolute;top:1.1mm;height:2.6mm;background:var(--brand);border-radius:99px;box-shadow:0 0 0 1px #fff}
.bar .v{font-size:7.2pt;color:var(--muted);margin-top:.8mm}
.bar .v b{color:var(--brand-600)}
.lg{display:inline-block;width:5mm;height:2mm;border-radius:99px;vertical-align:.1mm;margin:0 1mm 0 0}
.lg.g{background:#B9C4BD}.lg.s{background:var(--brand);margin-left:2mm}
.pcta{display:flex;flex-direction:column;gap:2.5mm;padding:4mm 6mm;margin-bottom:2mm}
.pil{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin-bottom:3mm}
.pc{border-radius:3.5mm;padding:4mm 4.2mm;color:#fff}
.pc.sun{background:var(--sun);color:var(--darker)}.pc.eff{background:var(--brand)}.pc.mit{background:var(--darker)}
.pt{display:flex;align-items:center;gap:1.8mm;font-size:7.8pt;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.pc .ic{width:5mm;height:5mm;color:currentColor}
.big{font-size:13.5pt;font-weight:800;line-height:1.1;letter-spacing:-.02em;margin:2mm 0 1.8mm}
.pc p{font-size:7.8pt;line-height:1.4}
.facts{display:flex;flex-wrap:wrap;gap:1.5mm 5mm;font-size:8pt;color:var(--muted);padding:2mm 0 2.5mm;margin-bottom:3.5mm;border-bottom:1px solid var(--line)}
.facts b{color:var(--darker)}
.ctah{font-size:13pt;font-weight:800}
"""

DOCS = [
    ("REO-R290-Smart_letak-zakaznici", "REO R290 Smart – leták pro zákazníky | REO HEATING", CSS_C, cust_p1 + cust_p2),
    ("REO-R290-Smart_letak-partneri",  "REO R290 Smart – leták pro partnery | REO HEATING",  CSS_P, part_p1 + part_p2),
]
for slug, title, css, body in DOCS:
    html = (f'<!doctype html><html lang="cs"><head><meta charset="utf-8"><title>{title}</title>{FONTS}'
            f'<style>{css}</style></head><body>{body}</body></html>')
    out = ROOT / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    pdf = ROOT / f"{slug}.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf}", out.as_uri()],
                   check=True, capture_output=True)
    print("PDF", pdf.name)
