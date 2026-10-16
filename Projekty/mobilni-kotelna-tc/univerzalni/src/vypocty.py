"""Univerzální mobilní kotelna REO HEATING — výpočty fáze 1 (technická koncepce).

Jediný zdroj čísel pro studii (gen_studie.py). Původ údajů:
  [D] dokument výrobce (výkonové tabulky z REO/R290-datove-listy/src/data.js → vykony.json,
      návody RH030–RH060 a RH X50, prezentace komerční řady),
  [Z] sdělil zadavatel, [O] vlastní odborný odhad, [?] nutno ověřit.
Spuštění z kořene repozitáře: python3 mobilni-kotelna-tc/univerzalni/src/vypocty.py
"""
import json, math
from pathlib import Path

SRC = Path(__file__).parent
V = json.loads((SRC / "vykony.json").read_text())
AMB = V["AMB"]                       # stejné pole venkovních teplot pro RH i X50
TEMPS = [7, 2, -7, -15, -20]         # body požadované v zadání

# ------------------------------------------------------------------ jednotky
UNITS = {
    # nom = A7/W35 MAX [D]; el = max. příkon / proud (X50 [D], RH [O]); pump = vestavěné čerpadlo
    "RH050": dict(label="RH050", nom=14.8, el_kw=5.0, amp=9, brk="C16 (3f) / C25 (1f)", pump="ano, výtlak max. 9 m [D]",
                  conn="DN25 [D]", mass=160, dims="1080 × 480 × 1060", flow=2.5),
    "RH060": dict(label="RH060", nom=22.0, el_kw=7.5, amp=13, brk="C20 [O]", pump="ano, výtlak max. 12 m [D]",
                  conn="DN25 [D]", mass=165, dims="1080 × 480 × 1372", flow=3.8),
    "RHX50": dict(label="RH X50", nom=49.3, el_kw=20.0, amp=32, brk="40 A s RCD [D]", pump="ne – externí čerpadlo ≥ 1,1–1,2 × jm. průtoku [D]",
                  conn="G 1½\" [D]", mass=370, dims="1195 × 980 × 1900", flow=10.32),
}


def cap(model, w, t, mode="MAX"):
    d = V[model]["D"].get(str(w)) or (V[model]["DHi"] or {}).get(str(w))
    if not d:
        return None
    return d[mode]["cap"][AMB.index(t)]


def ratio_check():
    """RH060/RH050 v každém bodě tabulky — konstantní poměr = odvozená, ne měřená tabulka."""
    r = [round(a / b, 2) for a, b in zip(V["RH060"]["D"]["55"]["MAX"]["cap"], V["RH050"]["D"]["55"]["MAX"]["cap"])]
    return min(r), max(r)


# ------------------------------------------------------------------ kaskády
CONFIGS = [
    # (kód, název, {model: počet} – jen vytápění, TUV jednotka zvlášť, poznámka)
    ("A1", "≈ 50 kW nominálně", {"RH060": 2, "RH050": 1}, "RH050"),
    ("A2", "≈ 70 kW nominálně", {"RH060": 2, "RH050": 2}, "RH050"),
    ("A3", "5 jednotek pro ÚT", {"RH060": 2, "RH050": 3}, "RH050"),
    ("B1", "1 × RH X50", {"RHX50": 1}, "RH050"),
    ("B2", "2 × RH X50", {"RHX50": 2}, "RH050"),
    ("B3", "RH X50 + 2 × RH060", {"RHX50": 1, "RH060": 2}, "RH050"),
]


def config_rows():
    rows = []
    for code, name, mix, tuv in CONFIGS:
        nom = sum(UNITS[m]["nom"] * n for m, n in mix.items())
        units = sum(mix.values())
        res = {}
        for w in (45, 55):
            for t in TEMPS:
                caps = [cap(m, w, t) for m, n in mix.items() for _ in range(n)]
                res[(w, t)] = (sum(caps), sum(caps) - max(caps))      # celkem, N−1 (bez největší)
        el = sum(UNITS[m]["el_kw"] * n for m, n in mix.items()) + UNITS[tuv]["el_kw"] + 2.0   # +2 kW čerpadla, regulace [O]
        rows.append(dict(code=code, name=name, mix=mix, nom=nom, units=units, res=res, el=el))
    return rows


# ------------------------------------------------------------------ otopná tělesa při nižší teplotě
def lmtd(tf, tr, ti):
    a, b = tf - ti, tr - ti
    return (a - b) / math.log(a / b) if a != b else a


def radiator_factor(design, oper, ti=20, n=1.3):
    return (lmtd(*oper, ti) / lmtd(*design, ti)) ** n


RAD_DESIGNS = [(90, 70), (80, 60), (75, 65), (70, 55), (55, 45)]
RAD_OPER = [(55, 45), (50, 42), (60, 50), (70, 60)]   # 60/50 a 70/60 jen RH X50


# ------------------------------------------------------------------ odhad výkonu z odběru tepla
def design_load_from_consumption(gj_year, tuv_share=0.15, degree_days=3500, ti=19, te=-15):
    """P = Q_ÚT / (D · 24 h) · (ti − te). D = denostupně pro ti/te (ČR ≈ 3 300–3 900 K·d)."""
    q_ut_kwh = gj_year * (1 - tuv_share) / 3.6 * 1000
    ua = q_ut_kwh / (degree_days * 24)          # kW/K
    return ua, ua * (ti - te)


# ------------------------------------------------------------------ hydraulika
RHO, NU = 988.0, 0.55e-6       # voda 50 °C


def flow_m3h(kw, dt):
    return kw / (1.163 * dt)


def dp_pair(q_m3h, d_mm, length_m, eps_mm=0.02, zeta=8.0):
    """Tlaková ztráta přívod + zpátečka (2 × délka) v kPa; ζ = 2 rychlospojky a koncovky na hadici."""
    d = d_mm / 1000
    v = q_m3h / 3600 / (math.pi * d * d / 4)
    re = v * d / NU
    lam = 0.25 / (math.log10(eps_mm / 1000 / (3.7 * d) + 5.74 / re ** 0.9)) ** 2
    dp = (lam * 2 * length_m / d + zeta) * RHO * v * v / 2
    return v, dp / 1000


HOSE_ID = {"DN40": 40, "DN50": 50, "DN65": 65}
LENGTHS = [5, 10, 20, 30]
LOADS = [50, 70, 100]


def aku_min(p_min_kw, minutes=10, dt=5):
    """Objem pro minimální dobu běhu kompresoru: V = P · t / (c · ΔT)."""
    return p_min_kw * minutes * 60 / (4.18 * dt)


def expansion(v_l, t_max=60, p0=1.0, pe=2.5, n=0.0171):
    ve = v_l * n
    vn = ve * (pe + 1) / (pe - p0) * 1.2 + 0.005 * v_l   # +20 % a vodní předloha 0,5 %
    return ve, vn


# ------------------------------------------------------------------ TUV
def heat_time(v_l, kw, t0=10, t1=55):
    e = v_l * 1.163 * (t1 - t0) / 1000
    return e, e / kw


def coil_power(t_tank, t_flow=60, dt_coil=5, area=3.3, u=450):
    t_ret = t_flow - dt_coil
    if t_ret <= t_tank:
        return 0.0
    return u * area * lmtd(t_flow, t_ret, t_tank) / 1000


# ------------------------------------------------------------------ přeprava, kotvení
G = 9.81
TANKS = [  # (název, prázdná [O], plná, výška těžiště prázdné [O], rozteč noh / opěr [O])
    ("TUV 300 l (sklad, 1 ks)", 95, 395, 0.75, 0.42),
    ("AKU 300 l (sklad, 1 ks)", 60, 360, 0.75, 0.42),
    ("AKU 1 000 l (nová)", 160, 1160, 1.00, 0.60),
    ("TUV 1 000 l (nová)", 260, 1260, 1.00, 0.60),
]
ROAD = dict(vpred=0.8, bok=0.5, vzad=0.5)   # ČSN EN 12195-1, silniční přeprava


def transport_forces(m):
    return {k: m * G * c / 1000 for k, c in ROAD.items()}   # kN


def tip_check(m, h_cg, base):
    """Klopný moment při 0,8 g vs. stabilizující moment vlastní tíhy (bez kotvení)."""
    m_tip = m * G * 0.8 * h_cg
    m_stab = m * G * base / 2
    return m_tip / 1000, m_stab / 1000


# ------------------------------------------------------------------ hluk
def lp(lwa, r, q=2):
    return lwa - 20 * math.log10(r) - 11 + 10 * math.log10(q)


def sum_db(*levels):
    return 10 * math.log10(sum(10 ** (l / 10) for l in levels))


if __name__ == "__main__":
    print("Poměr RH060/RH050 v tabulce W55:", ratio_check())
    for r in config_rows():
        print(r["code"], r["name"], f"nom {r['nom']:.1f}", " ".join(f"{t}:{r['res'][(55, t)][0]:.1f}" for t in TEMPS), f"el {r['el']:.1f} kW")
    print("Radiátory 90/70 → 55/45:", round(radiator_factor((90, 70), (55, 45)), 2))
    print("Odhad 500 GJ/rok:", [round(x, 1) for x in design_load_from_consumption(500)])
    for ld in LOADS:
        for dn, d in HOSE_ID.items():
            v, dp = dp_pair(flow_m3h(ld, 10), d, 20)
            print(ld, dn, f"v={v:.2f} m/s dp20m={dp:.1f} kPa")
    print("AKU min X50:", round(aku_min(cap('RHX50', 45, 7, 'MIN'))), "RH050:", round(aku_min(cap('RH050', 45, 7, 'MIN'))))
    print("Expanze 1 300 l:", [round(x) for x in expansion(1300)])
    print("Cívka 3,3 m² při 50 °C:", round(coil_power(50), 1), "kW")
