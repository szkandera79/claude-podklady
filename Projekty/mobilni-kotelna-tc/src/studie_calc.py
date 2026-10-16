#!/usr/bin/env python3
"""Univerzální mobilní kotelna REO HEATING — výpočty pro studii proveditelnosti (fáze 1).

Jediný zdroj čísel pro studie.html (build: python3 mobilni-kotelna-tc/src/build_studie.py).
Výkonové mapy: ~/Claude/REO/R290-datove-listy/src/data.js (MAX = max. frekvence kompresoru,
MIN = min. frekvence). Elektro RH X50: návod k použití (max. 20 kW / 32 A, jistič 40 A).
Údaje označené [OVĚŘIT] jsou odhady nebo předpoklady, ne údaje výrobce.
"""
import math

AMB = [-25, -20, -15, -12, -10, -7, -5, 0, 2, 5, 7, 10, 12, 15, 21]
T_SHOW = [7, 2, -7, -15, -20]

# --- výkonové mapy (kW), přepis z data.js -------------------------------------
CAP = {
    'RH050': {
        'MAX': {35: [5.5, 6.9, 8.3, 9.2, 9.8, 10.6, 11.2, 12.7, 13.2, 14.1, 14.8, 15.3, 15.5, 15.8, 16.3],
                45: [5.4, 6.7, 8.0, 8.8, 9.4, 10.3, 10.9, 12.3, 12.7, 13.7, 14.3, 14.8, 15.0, 15.3, 15.7],
                55: [5.1, 6.4, 7.6, 8.5, 9.0, 9.8, 10.4, 11.8, 12.2, 13.1, 13.7, 14.2, 14.4, 14.7, 15.0]},
        'MIN': {35: [2.8, 3.2, 3.7, 3.9, 4.1, 4.5, 4.6, 5.1, 5.3, 5.7, 5.9, 6.1, 6.2, 6.3, 6.5]},
        'INP': {55: [4.12, 4.19, 4.27, 4.32, 4.35, 4.37, 4.39, 4.44, 4.45, 4.46, 4.48, 4.51, 4.43, 4.31, 4.08]},
    },
    'RH060': {
        'MAX': {35: [8.2, 10.3, 12.3, 13.6, 14.5, 15.8, 16.7, 18.9, 19.6, 21.0, 22.0, 22.8, 23.1, 23.5, 24.2],
                45: [8.0, 10.0, 11.8, 13.1, 14.0, 15.3, 16.1, 18.3, 18.9, 20.3, 21.2, 22.0, 22.3, 22.7, 23.3],
                55: [7.6, 9.5, 11.4, 12.6, 13.4, 14.6, 15.5, 17.5, 18.1, 19.5, 20.4, 21.1, 21.4, 21.8, 22.4]},
        'MIN': {35: [4.1, 4.8, 5.4, 5.8, 6.2, 6.7, 6.9, 7.6, 7.9, 8.4, 8.8, 9.1, 9.2, 9.4, 9.7]},
        'INP': {55: [6.18, 6.28, 6.40, 6.48, 6.52, 6.55, 6.58, 6.65, 6.66, 6.68, 6.72, 6.76, 6.64, 6.46, 6.11]},
    },
    'RHX50': {
        'MAX': {35: [23.1, 27, 30.9, 33.2, 34.9, 37.4, 39.1, 41.7, 42.8, 46.7, 49.3, 55.8, 60.1, 63.1, 69],
                45: [19.2, 23.2, 27.3, 29.7, 32.1, 35.8, 38.2, 40.8, 41.3, 45.5, 47.7, 49.4, 53.3, 56, 61.3],
                55: [16.9, 20.8, 24.8, 27.2, 31, 33.1, 35.5, 37.6, 38.4, 39.7, 41.7, 43.1, 46.5, 49.3, 54.8],
                60: [11.7, 17, 22.2, 25.4, 26.6, 28.5, 29.7, 32.4, 33.4, 35, 37.2, 38.9, 42.8, 44.7, 49]},
        'MIN': {35: [5.1, 6.8, 8.5, 9.4, 10.2, 11.4, 12.2, 14.8, 15.8, 17.4, 18.4, 19.8, 20.8, 22.3, 25.2]},
        'INP': {55: [14.39, 15.79, 16.87, 17.39, 15.55, 16.34, 17.1, 16.84, 16.75, 16.6, 16.6, 16.59, 16.5, 16.9, 17.5]},
    },
}
COP55 = {
    'RH050': [1.24, 1.53, 1.79, 1.96, 2.07, 2.25, 2.37, 2.66, 2.74, 2.93, 3.05, 3.15, 3.25, 3.40, 3.69],
    'RH060': [1.23, 1.52, 1.78, 1.94, 2.06, 2.23, 2.35, 2.63, 2.72, 2.91, 3.03, 3.12, 3.22, 3.37, 3.66],
    'RHX50': [1.17, 1.3, 1.5, 1.56, 2, 2.03, 2.07, 2.2, 2.3, 2.39, 2.5, 2.6, 2.81, 2.9, 3.1],
}
NOM = {'RH050': 14.8, 'RH060': 22.0, 'RHX50': 49.3}          # A7/W35 MAX = „nominál"
# Max. proud na fázi (A). RH X50 z návodu; RH050/RH060 dopočet z max. příkonu mapy
# (cos φ 0,95) + 25 % rezerva na rozběh/ventilátor/čerpadlo — [OVĚŘIT typový štítek].
I_MAX = {'RHX50': 32.0, 'RH060': 13.0, 'RH050': 9.0}
P_EL_MAX = {'RHX50': 20.0, 'RH060': 7.5, 'RH050': 5.0}       # kW; RH = [OVĚŘIT]
MASS = {'RHX50': 370, 'RH060': 165, 'RH050': 160}             # kg, návody


def cap(model, tw, ta, mode='MAX'):
    """Výkon při venkovní teplotě ta (lineární interpolace v mapě)."""
    row = CAP[model][mode][tw]
    for i in range(len(AMB) - 1):
        if AMB[i] <= ta <= AMB[i + 1]:
            f = (ta - AMB[i]) / (AMB[i + 1] - AMB[i])
            return row[i] + f * (row[i + 1] - row[i])
    raise ValueError(ta)


def cop55(model, ta):
    row = COP55[model]
    for i in range(len(AMB) - 1):
        if AMB[i] <= ta <= AMB[i + 1]:
            f = (ta - AMB[i]) / (AMB[i + 1] - AMB[i])
            return row[i] + f * (row[i + 1] - row[i])


# --- 1. výkony jednotek -------------------------------------------------------
def unit_table():
    out = []
    for m in ('RH050', 'RH060', 'RHX50'):
        for tw in (35, 45, 55):
            out.append((m, tw, [cap(m, tw, t) for t in T_SHOW]))
    return out


# --- 2. kaskády ----------------------------------------------------------------
CASCADES = [
    # (kód, popis, jednotky pro ÚT, rezerva, jednotka TUV)
    ('A-50', 'A „50 kW"', ['RH060', 'RH060', 'RH050'], 'RH050', 'RH050'),
    ('A-70', 'A „70 kW"', ['RH060', 'RH060', 'RH050', 'RH050'], 'RH050', 'RH050'),
    ('A-5×RH050', 'A jen RH050', ['RH050'] * 5, 'RH050', 'RH050'),
    ('H', 'Hybrid X50 + 2× RH060', ['RHX50', 'RH060', 'RH060'], None, 'RH050'),
    ('B-1', 'B 1× X50', ['RHX50'], None, 'RH050'),
    ('B-2', 'B 2× X50', ['RHX50', 'RHX50'], None, 'RH050'),
]


def cascade_rows(tw):
    rows = []
    for code, name, units, reserve, tuv in CASCADES:
        allu = units + ([reserve] if reserve else [])
        nom = sum(NOM[u] for u in allu)
        caps = [sum(cap(u, tw, t) for u in allu) for t in T_SHOW]
        # N−1: výpadek největší jednotky
        big = max(allu, key=lambda u: NOM[u])
        n1 = [c - cap(big, tw, t) for c, t in zip(caps, T_SHOW)] if len(allu) > 1 else [0.0] * len(T_SHOW)
        rows.append(dict(code=code, name=name, units=allu, reserve=reserve, tuv=tuv,
                         nom=nom, caps=caps, n1=n1, n_units=len(allu) + (1 if tuv else 0)))
    return rows


# --- 3. bod rovnováhy (budova vs. kaskáda) -----------------------------------
T_IN, T_DES = 18.0, -15.0          # vážená vnitřní teplota (admin 20 / hala 15) [PŘEDPOKLAD]


def load(p_des, ta):
    return max(0.0, p_des * (T_IN - ta) / (T_IN - T_DES))


def balance_point(units, p_des, tw):
    """Nejnižší venkovní teplota, kdy sestava ještě pokryje ztrátu (krok 0,5 K)."""
    t = 15.0
    while t >= -25:
        if sum(cap(u, tw, t) for u in units) < load(p_des, t):
            return t + 0.5
        t -= 0.5
    return -25.0


# --- 4. otopná soustava zákazníka: potřebná teplota přívodu -----------------
def supply_needed(t_sup_n, t_ret_n, ta, n=1.3, ti=20.0, te=-15.0):
    """Teplota přívodu pro otopná tělesa navržená na t_sup_n/t_ret_n (ekvitermně)."""
    f = (ti - ta) / (ti - te)
    if f <= 0:
        return ti
    dtm_n = (t_sup_n + t_ret_n) / 2 - ti
    dtm = dtm_n * f ** (1 / n)
    return ti + dtm + (t_sup_n - t_ret_n) / 2 * f


def limit_temp(t_sup_n, t_ret_n, t_max):
    """Nejnižší venkovní teplota, kdy stačí přívod t_max."""
    ta = 20.0
    while ta > -25:
        if supply_needed(t_sup_n, t_ret_n, ta) > t_max:
            return ta + 0.5
        ta -= 0.5
    return -25.0


def radiator_share(t_sup_n, t_ret_n, t_sup, t_ret, n=1.3, ti=20.0):
    return (((t_sup + t_ret) / 2 - ti) / ((t_sup_n + t_ret_n) / 2 - ti)) ** n


# --- 5. TUV: doba ohřevu přes výměník ----------------------------------------
U_COIL = 450.0     # W/m²K, trubkový výměník, nucený průtok uvnitř / přirozená konvekce [ODHAD]
T_FLOW_MAX = 58.0  # °C, RH050: doporučená max. teplota vody 60 °C (návod) → s rezervou 58


def tuv_heatup(volume_l, area_m2, hp_kw, t_start=10.0, t_end=50.0, dt_hp=5.0):
    """Ohřev promíchaného zásobníku. Vrací (hodiny, průměrný výkon kW, dosažitelné max °C)."""
    c = volume_l * 4.186 / 3600       # kWh/K
    ua = U_COIL * area_m2 / 1000      # kW/K
    t, hours, step = t_start, 0.0, 1 / 60
    # max. dosažitelná teplota: výměník přenese aspoň 1 kW při T_flow_max
    while t < t_end:
        # výkon omezený čerpadlem nebo výměníkem (vstup T_FLOW_MAX, výstup T_FLOW_MAX-dt)
        a, b = T_FLOW_MAX - t, T_FLOW_MAX - dt_hp - t
        if b <= 0.2:
            return None, None, t
        lmtd = (a - b) / math.log(a / b)
        q = min(hp_kw, ua * lmtd)
        if q < 0.5:
            return None, None, t
        t += q * step / c
        hours += step
    return hours, volume_l * 4.186 * (t_end - t_start) / 3600 / hours, t_end


def t_max_reachable(area_m2, min_kw=1.0, dt_hp=5.0):
    ua = U_COIL * area_m2 / 1000
    t = 30.0
    while t < T_FLOW_MAX:
        a, b = T_FLOW_MAX - t, T_FLOW_MAX - dt_hp - t
        if b <= 0.2 or ua * (a - b) / math.log(a / b) < min_kw:
            return t
        t += 0.1
    return t


TUV_CONFIGS = [
    ('A', '3 × 300 l skladové, výměníky paralelně', 900, 3 * 3.3),
    ('B', '2 × 300 l skladové', 600, 2 * 3.3),
    ('C', '1 × 1 000 l nový (plocha výměníku ~4,5 m² [OVĚŘIT])', 1000, 4.5),
]


# --- 6. hydraulika -------------------------------------------------------------
def flow_m3h(p_kw, dt, cp=4.186, rho=990):
    return p_kw / (cp * dt) / rho * 3600


def dp_pipe(q_m3h, d_mm, length_m, zeta=0.0, nu=0.6e-6, rho=990, k_mm=0.05):
    """Tlaková ztráta (kPa) – Darcy–Weisbach, Swamee–Jain."""
    a = math.pi * (d_mm / 1000) ** 2 / 4
    v = q_m3h / 3600 / a
    re = v * d_mm / 1000 / nu
    lam = 64 / re if re < 2300 else 0.25 / math.log10(k_mm / (3.7 * d_mm) + 5.74 / re ** 0.9) ** 2
    dp = (lam * length_m / (d_mm / 1000) + zeta) * rho * v * v / 2
    return dp / 1000, v


ZETA_HOSE_PAIR = 8.0   # 4 rychlospojky + 2 kulové kohouty + oblouky na trase tam i zpět [ODHAD]


def hose_table(dt=10.0):
    rows = []
    for p in (50, 70, 100):
        q = flow_m3h(p, dt)
        for dn in (40, 50, 65):
            vals = []
            for L in (5, 10, 20, 30):
                dp, v = dp_pipe(q, dn, 2 * L, ZETA_HOSE_PAIR)
                vals.append(dp)
            rows.append((p, q, dn, v, vals))
    return rows


def min_buffer_l(p_min_kw, t_run_min=10, dt_hyst=5.0):
    return p_min_kw * t_run_min * 60 / (4.186 * dt_hyst)


def freeze_hours(dn_mm, ins_mm=30, t_water=40.0, t_amb=-15.0, lam=0.04):
    """Hodiny bez průtoku, než voda v izolované hadici vychladne na 0 °C (bez latentního tepla)."""
    r1, r2 = dn_mm / 2000 + 0.006, dn_mm / 2000 + 0.006 + ins_mm / 1000   # stěna hadice ~6 mm
    ua = 2 * math.pi * lam / math.log(r2 / r1)                 # W/(m·K)
    c = math.pi * (dn_mm / 2000) ** 2 * 1000 * 4186            # J/(m·K)
    tau = c / ua                                               # s
    return tau * math.log((t_water - t_amb) / (0 - t_amb)) / 3600


# --- 7. elektro ---------------------------------------------------------------
AUX_KW, AUX_A = 3.0, 6.0   # oběhová čerpadla, regulace, router, osvětlení, temperace kontejneru [ODHAD]


def electro(units):
    i = sum(I_MAX[u] for u in units) + AUX_A
    p = sum(P_EL_MAX[u] for u in units) + AUX_KW
    return p, i


def breaker(i):
    for b in (32, 40, 50, 63, 80, 100, 125, 160, 200):
        if b >= i * 1.1:
            return b
    return 250


CABLE = {32: '5×6', 40: '5×10', 50: '5×16', 63: '5×16', 80: '4×25+PE', 100: '4×35+PE',
         125: '4×50+PE', 160: '4×70+PE', 200: '4×95+PE'}

if __name__ == '__main__':
    for m, tw, vals in unit_table():
        print(m, tw, [round(v, 1) for v in vals])
    for tw in (45, 55):
        print('--- kaskády W', tw)
        for r in cascade_rows(tw):
            print(r['code'], round(r['nom'], 1), [round(c, 1) for c in r['caps']], 'N-1', [round(c, 1) for c in r['n1']])
    for p in (30, 40, 50, 70):
        print('ztráta', p, {c[0]: balance_point(c[2] + ([c[3]] if c[3] else []), p, 55) for c in CASCADES},
              'X50 sám', balance_point(['RHX50'], p, 55))
    for sys in ((90, 70), (80, 60), (75, 65), (70, 55), (55, 45)):
        print(sys, 'stačí 55 °C do', limit_temp(*sys, 55), '| 60 °C do', limit_temp(*sys, 60),
              '| 70 °C do', limit_temp(*sys, 70), '| podíl výkonu při 55/45:', round(radiator_share(*sys, 55, 45), 2))
    for code, name, v, a in TUV_CONFIGS:
        for ta in (7, -7, -15):
            hp = cap('RH050', 55, ta)
            print('TUV', code, ta, round(hp, 1), tuv_heatup(v, a, hp), 'tmax', round(t_max_reachable(a), 1))
    for r in hose_table():
        print(r[0], round(r[1], 2), r[2], round(r[3], 2), [round(x, 1) for x in r[4]])
    for m in ('RH050', 'RH060', 'RHX50'):
        print('buffer', m, round(min_buffer_l(cap(m, 35, 7, 'MIN'))), 'l')
    for code, name, units, res, tuv in CASCADES:
        allu = units + ([res] if res else []) + [tuv]
        p, i = electro(allu)
        print('elektro', code, round(p, 1), round(i, 1), breaker(i))
    for dn in (40, 50, 65):
        print('zamrzani', dn, round(freeze_hours(dn), 1), 'h; 20 mm', round(freeze_hours(dn, 20), 1))
    print('prutoky dT5', {m: round(flow_m3h(NOM[m], 5), 2) for m in NOM})
