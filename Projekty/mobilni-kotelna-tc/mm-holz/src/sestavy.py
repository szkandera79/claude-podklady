"""MM Holz / Alignum Paskov — mobilní kotelna ze skladových jednotek REO HEATING.

Vychází z univerzální studie (univerzalni/src/vypocty.py, výkonové mapy výrobce).
Podklady klienta [P]: DSP ÚT „Výroba palet Paskov“ (ESL, 01/2005) — technická zpráva, půdorys, výměníková stanice.
Sklad [Z]: několik RH050, 2 × RH060, 2 × RH X50.
Spuštění z kořene repozitáře: python3 mobilni-kotelna-tc/mm-holz/src/sestavy.py
"""
import importlib.util
from pathlib import Path

_p = Path(__file__).resolve().parents[2] / "univerzalni" / "src" / "vypocty.py"
_s = importlib.util.spec_from_file_location("vypocty", _p)
v = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v)

# ------------------------------------------------------------------ zátěž z projektu [P]
TE = -12.0                 # výpočtová venkovní teplota dle půdorysu [P]
HALA_Q, HALA_DT = 3.8, 20  # DAB A 50/180 XM, 2. stupeň 3,8 m³/h; spád 80/60 °C [P]
ADM_Q, ADM_DT = 1.0, 15    # DAB VA 35/130 1 m³/h; spád 75/60 °C [P]
HALA_TI_PROJ, HALA_TI = 20.0, 17.0   # projekt 20 °C, klient požaduje ≈ 17 °C [Z]


def hala_proj():
    return HALA_Q * 1.163 * HALA_DT          # instalovaný výkon jednotek Sahara (z průtoku čerpadla)


def adm_proj():
    return ADM_Q * 1.163 * ADM_DT


def hala_need(te=TE, ti=HALA_TI):
    return hala_proj() * (ti - te) / (HALA_TI_PROJ - TE)


def sahara_factor(tf, tr, ti=HALA_TI, design=(80, 60, 20)):
    """Teplovzdušná jednotka: výkon ≈ úměrný (střední teplota vody − vzduch), exponent ≈ 1 [O]."""
    return ((tf + tr) / 2 - ti) / ((design[0] + design[1]) / 2 - design[2])


# ------------------------------------------------------------------ varianty ze skladu
VARIANTY = [
    ("V1", "malá kaskáda", {"RH060": 2, "RH050": 4}),
    ("V2", "malá kaskáda – plná", {"RH060": 2, "RH050": 5}),
    ("V3", "hybrid", {"RHX50": 1, "RH060": 2, "RH050": 2}),
    ("V4", "2 × RH X50", {"RHX50": 2}),
    ("V5", "2 × RH X50 + 2 × RH060", {"RHX50": 2, "RH060": 2}),
]
# elektro na jednotku: (max. příkon kW, max. proud A na fázi) — X50 z návodu [D], RH0x odhad z mapy + ventilátor/čerpadlo [O]
EL = {"RHX50": (20.0, 32.0), "RH060": (7.5, 12.0), "RH050": (5.0, 8.0)}
AUX = (2.0, 3.5)            # čerpadla glykolového primáru a sekundáru, PLC, temperování kontejneru [O]
JISTIC = [32, 40, 50, 63, 80, 100, 125, 160]
KABEL = {32: "5×6", 40: "5×10", 50: "5×10", 63: "5×16", 80: "5×25", 100: "5×35", 125: "5×50", 160: "5×70"}   # Cu H07RN-F do ≈ 25 m [O]


def label(mix):
    names = {"RHX50": "RH X50", "RH060": "RH060", "RH050": "RH050 3f"}
    return " + ".join(f"{n} × {names[u]}" for u, n in mix.items())


def total(mix, w, t):
    caps = [v.cap(m, w, t) for m, n in mix.items() for _ in range(n)]
    if any(c is None for c in caps):
        return None, None
    return sum(caps), sum(caps) - max(caps)


def inp(model, w, t):
    d = v.V[model]["D"].get(str(w)) or (v.V[model]["DHi"] or {}).get(str(w))
    return d["MAX"]["inp"][v.AMB.index(t)]


def elektro(mix):
    kw = sum(EL[u][0] * n for u, n in mix.items()) + AUX[0]
    a = sum(EL[u][1] * n for u, n in mix.items()) + AUX[1]
    jis = next(j for j in JISTIC if j >= a * 1.05)
    provoz = sum(inp(u, 55, -12) * n for u, n in mix.items()) + AUX[0]
    return kw, a, jis, KABEL[jis], provoz


def emitter_limit(tf, tr):
    """Výkon, který stávající tělesa při dané vodě předají (hala 17 °C + administrativa 20 °C)."""
    return hala_proj() * sahara_factor(tf, tr) + adm_proj() * v.radiator_factor((75, 60), (tf, tr))


if __name__ == "__main__":
    print(f"Hala projekt {hala_proj():.1f} kW (20 °C), při 17 °C {hala_need():.1f} kW; administrativa {adm_proj():.1f} kW")
    for tf, tr in ((55, 45), (60, 50), (70, 60)):
        print(f"  tělesa předají při {tf}/{tr}: {emitter_limit(tf, tr):.0f} kW")
    for code, name, mix in VARIANTY:
        r55, r60 = total(mix, 55, -12), total(mix, 60, -12)
        kw, a, jis, kab, prov = elektro(mix)
        n = sum(mix.values())
        print(f"{code} {label(mix):38s} {n} ks | nom {sum(v.UNITS[u]['nom']*k for u,k in mix.items()):5.1f}"
              f" | −12/W55 {r55[0]:5.1f} (N−1 {r55[1]:5.1f}) | −15/W55 {total(mix,55,-15)[0]:5.1f}"
              f" | −12/W60 {'—' if r60[0] is None else f'{r60[0]:.1f}'}"
              f" | el max {kw:4.1f} kW {a:3.0f} A → jistič 3×{jis} A, kabel {kab}, provoz −12/W55 {prov:4.1f} kW")
