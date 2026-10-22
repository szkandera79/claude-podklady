"""Generuje nabídkové letáky REO R290 pro modely RH030–RH060 z letak.tpl.html.

Ceny jednotek bez DPH: RH040 104 900 Kč (mejlová nabídka 10/2026), ostatní podle cen
pro e-shop zadaných uživatelem 20. 10. 2026 (95/125/169 tis. → zaokrouhleno na …900 jako RH040).
Příslušenství, doprava a orientační instalace jsou u všech modelů stejné jako v mejlu (RH040).
Vhodná tepelná ztráta: rozsah RH040 z mejlu (7–10 kW) přepočtený poměrem výkonu při −12 °C/W35
z technických listů (RH030 5,5 · RH040 7,1 · RH050 9,2 · RH060 13,6 kW).
COP = max. COP při A7/W35 z letáku REO R290; hlučnost LpA v 1 m a LWA z protokolů TÜV SÜD (datové listy).

Spuštění: python3 gen.py  → letak-RHxxx.html + REO_HEATING_Letak_RHxxx.pdf
"""
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

AKU, TUV, DOPRAVA = 12000, 25000, 4500
INST_A, INST_B = 20000 + 25000, 30000 + 25000

MODELS = [
    dict(MODEL="RH030", KW="8", PRICE=94900, COP="5,17", LP="44", LWA="58", CARD_KICKER="Pro menší domy",
         FIT="Pro novostavby a menší domy do cca 200 m² s tepelnou ztrátou cca 5–8 kW.",
         ALT="pro středně velké domy <b>RH040 · 12 kW</b> za 104 900 Kč", range="menší novostavby",
         PARTNER=None),
    dict(MODEL="RH040", KW="12", PRICE=104900, COP="5,29", LP="43–47", LWA="57–61", CARD_KICKER="Nejžádanější model",
         FIT="Pro domy s tepelnou ztrátou cca 7–10 kW.",
         ALT="RH030 · 8 kW o <b>10 000 Kč</b> levněji — pro menší novostavby do 200 m²", range="středně velké domy",
         PARTNER=74990),
    dict(MODEL="RH050", KW="15", PRICE=124900, COP="5,22", LP="44–45", LWA="59", CARD_KICKER="Pro větší domy",
         FIT="Pro větší domy s tepelnou ztrátou cca 9–13 kW.",
         ALT="pro velké domy <b>RH060 · 22 kW</b> za 168 900 Kč", range="větší domy",
         PARTNER=None),
    dict(MODEL="RH060", KW="22", PRICE=168900, COP="5,24", LP="45–46", LWA="60–62", CARD_KICKER="Pro velké domy",
         FIT="Pro velké domy s tepelnou ztrátou cca 13–19 kW; v kaskádě až 8 jednotek.",
         ALT="pro větší domy <b>RH050 · 15 kW</b> za 124 900 Kč", range="velké domy, kaskády",
         PARTNER=None),
]


def kc(n):
    return f"{n:,}".replace(",", " ")


def render(m):
    tpl = open(os.path.join(HERE, "letak.tpl.html"), encoding="utf-8").read()
    p = m["PRICE"]
    a_dod, b_dod = p + AKU + DOPRAVA, p + AKU + TUV + DOPRAVA
    hl = ' class="hl"'
    rng = "\n".join(
        f'    <div{hl if o is m else ""}><b>{o["MODEL"]} · {o["KW"]} kW</b>'
        f'<span>{o["range"]}</span><span class="rp">{kc(o["PRICE"])} Kč</span></div>' for o in MODELS)
    others = ", ".join(f'{o["MODEL"]} {kc(o["PRICE"])} Kč' for o in MODELS if o is not m)
    partner = (f'{kc(m["PARTNER"])} Kč <small style="font-size:8pt;font-weight:600">bez DPH</small>'
               if m["PARTNER"] else 'cena na dotaz')
    val = dict(COP=m["COP"], LP=m["LP"], LWA=m["LWA"], MODEL=m["MODEL"], KW=m["KW"], PRICE=kc(p), CARD_KICKER=m["CARD_KICKER"], FIT=m["FIT"],
               ALT=m["ALT"], RANGE=rng, PARTNER=partner,
               A_DOD=kc(a_dod), A_TOT=kc(a_dod + INST_A), B_DOD=kc(b_dod), B_TOT=kc(b_dod + INST_B),
               INST_NOTE=f"Ostatní modely (jednotka, bez DPH): {others}.")
    for k, v in val.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    assert "{{" not in tpl, tpl[tpl.index("{{"):tpl.index("{{") + 40]
    return tpl


if __name__ == "__main__":
    for m in MODELS:
        html = os.path.join(HERE, f'letak-{m["MODEL"]}.html')
        open(html, "w", encoding="utf-8").write(render(m))
        pdf = os.path.join(HERE, f'REO_HEATING_Letak_{m["MODEL"]}.pdf')
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", "--virtual-time-budget=8000", f"file://{html}"],
                       stderr=subprocess.DEVNULL, check=True)
        print(m["MODEL"], "ok")
