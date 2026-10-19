"""MM Holz / Alignum Paskov — rev1: 2 × RH X50 + sériový elektrický dohřev 72 kW, připojení za výměníkem HV VS.

Jediný zdroj čísel pro dokumenty v rev1/. Značení: [D] výrobce, [C] certifikát, [P] projekt klienta (ESL 2005),
[O] vlastní výpočet/odhad, [CHYBÍ] údaj není k dispozici.
Spuštění z kořene repozitáře: python3 mobilni-kotelna-tc/mm-holz/rev1/src/rev1.py
"""
import importlib.util
import math
from pathlib import Path

_p = Path(__file__).resolve().parents[3] / "univerzalni" / "src" / "vypocty.py"
_s = importlib.util.spec_from_file_location("vypocty", _p)
v = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v)

C_W = 1.163                     # kWh/(m³·K) voda
TE = -12.0                      # výpočtová venkovní teplota [P]

# ------------------------------------------------------------------ otopná soustava [P]
HALA = dict(q=3.8, tf=80, tr=60, ti_proj=20, ti=17)      # 5 × SAHARA W3634, DAB A 50/180 XM 2. st.
ADM = dict(q=1.0, tf=75, tr=60, ti=20)                   # Korado Radik VK, DAB VA 35/130
T_MAX = 70.0                                             # max. přívod (zadání rev1)


def p_design(c):
    return c["q"] * C_W * (c["tf"] - c["tr"])


def hala_k(tf=HALA["tf"], tr=HALA["tr"], q=HALA["q"], ta=HALA["ti_proj"]):
    """Součinitel k [kW/K] všech 5 jednotek z návrhového bodu, P = k·(t_m − t_a) [O]."""
    return q * C_W * (tf - tr) / ((tf + tr) / 2 - ta)


def hala_power(t_in, q, k, ta=HALA["ti"]):
    """Výkon při daném vstupu a průtoku vody (střední teplota z bilance), vrací (P, t_zpátečky) [O]."""
    p = k * (t_in - ta) / (1 + k / (2 * C_W * q))
    return p, t_in - p / (C_W * q)


def hala_need(te, ti=HALA["ti"]):
    """Potřeba haly, pokud by projektový výkon odpovídal ztrátě (horní mez) [O]."""
    return p_design(HALA) * (ti - te) / (HALA["ti_proj"] - TE)


def adm_need(te):
    return p_design(ADM) * (ADM["ti"] - te) / (ADM["ti"] - TE)


def rad_power(t_in, q=ADM["q"], n=1.3, design=(75, 60), ti=20):
    """Radiátory administrativy při vstupu t_in a průtoku q (iterace zpátečky) [O]."""
    pn = p_design(ADM)
    tr = t_in - 10
    for _ in range(60):
        p = pn * v.radiator_factor(design, (t_in, max(tr, ti + 0.5)), ti, n)
        tr = t_in - p / (C_W * q)
    return p, tr


def t_in_required(need, q, k, ta=HALA["ti"]):
    return ta + need * (1 + k / (2 * C_W * q)) / k


# ------------------------------------------------------------------ RH X50 [D]
def x50(w, t):
    d = v.V["RHX50"]["D"].get(str(w)) or v.V["RHX50"]["DHi"].get(str(w))
    i = v.AMB.index(t)
    c, cop = d["MAX"]["cap"][i], d["MAX"]["cop"][i]
    return (c, cop, c / cop) if c else (None, None, None)


def x50_interp(w, te):
    a = v.AMB
    for i in range(len(a) - 1):
        if a[i] <= te <= a[i + 1]:
            c0, c1 = x50(w, a[i])[0], x50(w, a[i + 1])[0]
            if c0 is None or c1 is None:
                return None
            return c0 + (c1 - c0) * (te - a[i]) / (a[i + 1] - a[i])


PHE_APPROACH = 3.0          # glykol / voda, K [O]


def hp_out_max(te):
    """Nejvyšší výstup TČ, pro který má mapa data a který držíme v návrhu: W65 do −12 °C, pod tím W60 [D]."""
    return 65 if te >= -12 else 60


# ------------------------------------------------------------------ elektro
U, COSF = 400.0, 0.95
I_X50, P_X50 = 32.0, 20.0                    # na jednotku [D]
P_EK, N_STAGE = 72.0, 12                     # 12 × 6 kW [zadání]
I_STAGE = 6.0 / (math.sqrt(3) * U / 1000)    # ≈ 8,7 A, odporová zátěž cos φ 1
I_AUX = 5.0                                  # čerpadla, PLC, ostatní [O]
I_MAIN = 160.0
I_LIM_CONT, I_LIM_SHORT, I_TRIP_SHED = 0.85 * I_MAIN, 0.95 * I_MAIN, 150.0


def i_hp(p_kw):
    return p_kw * 1000 / (math.sqrt(3) * U * COSF)


def stages_allowed(i_other):
    return max(0, min(N_STAGE, int((I_LIM_CONT - i_other) // I_STAGE)))


# ------------------------------------------------------------------ hydraulika
def flow(p, dt):
    return p / (C_W * dt)


def dp_pair(q, dn, length, zeta):
    return v.dp_pair(q, dn, length, zeta=zeta)


# ------------------------------------------------------------------ skutečná potřeba z měření MM Holz
import json as _json
import collections as _col

_HEAT = {tuple(map(int, k.split("-"))): q for k, q in _json.load(open(Path(__file__).parent / "dodavka_tepla.json"))["mwh"].items()}
_MET = _json.load(open(Path(__file__).parent / "meteo_paskov.json"))
_DAYS = _col.defaultdict(list)
for _t, _tm in zip(_MET["time"], _MET["t_mean"]):
    _y, _m, _ = map(int, _t.split("-"))
    _DAYS[(_y, _m)].append(_tm)
YEARS_FIT = range(2021, 2026)        # nové měřidlo od 30. 11. 2018, 2017–2018 vyřazeno (nefunkční měření) [P]


def fit_load(years=YEARS_FIT, tb=None):
    """Měsíční regrese Q = a·dny + H·Σ(tb − t_den)⁺·24 h. Vrací (tb, základ kW, H kW/K, R², RMSE MWh, n)."""
    def one(tb):
        X, Y = [], []
        for (y, mo), q in _HEAT.items():
            if y in years and (y, mo) in _DAYS and q > 0:
                d = _DAYS[(y, mo)]
                X.append((len(d), sum(max(0.0, tb - t) for t in d) * 24 / 1000))
                Y.append(q)
        s11 = sum(a * a for a, _ in X); s12 = sum(a * b for a, b in X); s22 = sum(b * b for _, b in X)
        t1 = sum(a * y for (a, _), y in zip(X, Y)); t2 = sum(b * y for (_, b), y in zip(X, Y))
        det = s11 * s22 - s12 * s12
        a, h = (t1 * s22 - t2 * s12) / det, (s11 * t2 - s12 * t1) / det
        pred = [a * x[0] + h * x[1] for x in X]
        my = sum(Y) / len(Y)
        r2 = 1 - sum((pp - yy) ** 2 for pp, yy in zip(pred, Y)) / sum((yy - my) ** 2 for yy in Y)
        rmse = (sum((pp - yy) ** 2 for pp, yy in zip(pred, Y)) / len(Y)) ** 0.5
        return tb, a * 1000 / 24, h, r2, rmse, len(Y)
    if tb is not None:
        return one(tb)
    return max((one(x / 2) for x in range(20, 40)), key=lambda r: r[3])


TB, BASE_KW, H_KWK, R2, RMSE, NFIT = fit_load()
DYN = 1.10                   # rezerva na ranní náběh, vítr, hodinové minimum vs. denní průměr [O]


def load_meas(te, dyn=1.0):
    """Potřeba tepla na vytápění bez TUV (bez konstantního základu) z měření [O]."""
    return max(0.0, H_KWK * (TB - te)) * dyn


def share(te):
    """Poměr skutečné a projektové potřeby (hala 17 °C + administrativa)."""
    return load_meas(te) / (hala_need(te) + adm_need(te))


if __name__ == "__main__":
    k80 = hala_k()
    k85 = hala_k(85, 60, q=88 / (C_W * 25))
    print(f"Hala návrh {p_design(HALA):.1f} kW (80/60, 3,8 m³/h), k = {k80:.2f} kW/K; adm {p_design(ADM):.1f} kW")
    print("Přepočet sahar (hala 17 °C):")
    for name, k, q0 in (("projekt 80/60", k80, 3.8), ("zadání 85/60 (88 kW)", k85, 88 / (C_W * 25))):
        for t_in, tr_set in ((85, 60), (80, 60), (70, 60), (70, 55), (65, 55)):
            q_req = None
            # výkon při stávajícím průtoku a průtok potřebný pro požadovaný spád
            p0, tr0 = hala_power(t_in, q0, k)
            tm = (t_in + tr_set) / 2
            p_set = k * (tm - HALA["ti"])
            q_req = p_set / (C_W * (t_in - tr_set))
            print(f"  {name:22s} {t_in}/{tr_set}: spád dodrží při {q_req:4.1f} m³/h → {p_set:5.1f} kW"
                  f" | při stávajícím {q0:.2f} m³/h: {p0:5.1f} kW, zpátečka {tr0:4.1f} °C")
    for q in (3.8, 5.0):
        p, tr = hala_power(70, q, k80)
        print(f"  70 °C, {q} m³/h: {p:.1f} kW (zp. {tr:.1f}) vs potřeba −12 °C {hala_need(-12):.1f} kW")
    for t in (70, 65, 60):
        p, tr = rad_power(t)
        print(f"  adm vstup {t} °C, 1 m³/h: {p:.1f} kW (zp. {tr:.1f}) vs potřeba −12 °C {adm_need(-12):.1f} kW")

    print("\nRH X50 [D] W70 a další:")
    for w in (70, 65, 60):
        print("  W", w, [(t, x50(w, t)) for t in (7, 2, -7, -10, -12, -15)])

    print(f"\nRegrese spotřeby {min(YEARS_FIT)}–{max(YEARS_FIT)}: tb {TB} °C, základ (TUV+ztráty) {BASE_KW:.2f} kW, H {H_KWK:.3f} kW/K,"
          f" R² {R2:.3f}, RMSE {RMSE:.1f} MWh, n {NFIT}")
    for yrs, lab in ((range(2019, 2026), "2019–2025"), (range(2009, 2017), "2009–2016"),
                     ([y for y in range(2007, 2027) if y not in (2017, 2018)], "2007–2026 bez 2017–18")):
        tb, b, h, r2, rm, n = fit_load(yrs)
        print(f"  kontrola {lab}: tb {tb}, H {h:.3f}, R² {r2:.3f} → P(−12) {h * (tb + 12):.1f} kW, P(−15) {h * (tb + 15):.1f} kW")
    yrs_tot = {y: sum(q for (yy, _), q in _HEAT.items() if yy == y) for y in range(2019, 2026)}
    print("  roční odběr MWh:", {y: round(q, 1) for y, q in yrs_tot.items()})
    cold = sorted(zip(_MET["t_mean"], _MET["time"]))[:3]
    print("  nejchladnější dny (denní průměr):", cold)

    print("\nBilance (potřeba z měření ×1,10; TČ při W55/W60; EK po 6 kW, limit 136 A):")
    print(" te  | potřeba | podíl proj. | přívod pro halu (3,8 m³/h) | TČ W55 | TČ W60 | deficit W55 | stupně EK | proud")
    for te in (5, 0, -5, -7, -10, -12, -15, -18):
        need = load_meas(te, DYN)
        r = share(te)
        tin = t_in_required(r * hala_need(te) * DYN, 3.8, k80)
        hp55 = 2 * x50_interp(55, te)
        hp60 = 2 * x50_interp(60, te)
        defi = max(0.0, need - hp55)
        st = math.ceil(defi / 6)
        i_tc = 2 * i_hp(x50_interp(55, te) / (x50(55, -12)[1] if te >= -12 else x50(55, -15)[1]))
        print(f" {te:+3d} | {need:5.1f} | {r:4.2f} | {tin:5.1f} °C | {hp55:5.1f} | {hp60:5.1f} | {defi:5.1f} | {st:2d} ({6 * st} kW)"
              f" | {i_tc + st * I_STAGE + I_AUX:5.0f} A")
    # bod bivalence
    for w in (55, 60):
        te = 10.0
        while te > -25 and 2 * x50_interp(w, te) >= load_meas(te, DYN):
            te -= 0.1
        print(f"  bod bivalence W{w}: {te + 0.1:+.1f} °C")
    for p_ek in (48, 72):
        te = 15.0
        while load_meas(te, DYN) <= p_ek:
            te -= 0.1
        print(f"  samotná elektřina {p_ek} kW pokryje (×1,10) do {te + 0.1:+.1f} °C; 1 × X50 W55 + {p_ek} kW:", end=" ")
        te = 0.0
        while te > -25 and x50_interp(55, te) + min(p_ek, stages_allowed(I_X50 + I_AUX) * 6) >= load_meas(te, DYN):
            te -= 0.1
        print(f"do {te + 0.1:+.1f} °C")
    print(f"\nElektro: stupeň 6 kW = {I_STAGE:.1f} A; EK 72 kW = {12 * I_STAGE:.0f} A; X50 2× max {2 * I_X50:.0f} A;"
          f" součet max {2 * I_X50 + 12 * I_STAGE + I_AUX:.0f} A; limit trvale {I_LIM_CONT:.0f} A")
    print(f"  Při max. X50 (64 A) povoleno {stages_allowed(2 * I_X50 + I_AUX)} stupňů = {6 * stages_allowed(2 * I_X50 + I_AUX)} kW")
    print(f"  Nouzově bez TČ: {stages_allowed(I_AUX)} stupňů, {12 * I_STAGE + I_AUX:.0f} A")
    print(f"  Jen EK pokryje halu+adm do te = ", end="")
    te = 15.0
    while hala_need(te) + adm_need(te) <= 72 and te > -30:
        te -= 0.5
    print(f"{te + 0.5:+.1f} °C; jen halu do {HALA['ti'] - 72 / hala_need(TE) * (HALA['ti'] - TE):+.1f} °C")

    print("\nHydraulika:")
    q_x = 10.32 * 1.1
    print(f"  Primár glykol: 2 × {q_x:.1f} m³/h (jm. 10,32 [D] +10 % glykol) = {2 * q_x:.1f} m³/h")
    q_aku = flow(100, 5)
    print(f"  Nabíjení AKU z výměníku (100 kW, ΔT 5 K): {q_aku:.1f} m³/h")
    for name, p, dt in (("soustava 105 kW 70/55", 105, 15), ("soustava 105 kW 70/60", 105, 10),
                        ("EK okruh 72 kW ΔT 20", 72, 20), ("EK okruh 72 kW ΔT 15", 72, 15)):
        print(f"  {name}: {flow(p, dt):.1f} m³/h")
    for name, q, dn, l, z in (("přívod+zpátečka AKU→VS DN65, 2×15 m", 6.0, 65, 15, 12),
                              ("dtto při 70/60", 9.0, 65, 15, 12),
                              ("EK okruh DN40 2×6 m", 3.6, 40, 6, 10),
                              ("primár glykol DN80 2×10 m", 22.7, 80, 10, 10),
                              ("nabíjení AKU DN65 2×5 m", 17.2, 65, 5, 10)):
        vel, dp = dp_pair(q, dn, l, z)
        print(f"  {name}: v = {vel:.2f} m/s, Δp = {dp:.1f} kPa")
    dt_ek = 72 / (C_W * 6.0)
    print(f"  Zvýšení teploty přívodu EK při 6,0 m³/h: +{dt_ek:.1f} K; při 9,0 m³/h +{72 / (C_W * 9):.1f} K")
    v_water = 2000 + 300
    ve, vn = v.expansion(v_water, t_max=70, p0=1.0, pe=2.5, n=0.0228)
    print(f"  Expanze vodní části kotelny {v_water} l (10→70 °C): ΔV {ve:.0f} l, nádoba ≥ {vn:.0f} l (bez stávající soustavy)")
