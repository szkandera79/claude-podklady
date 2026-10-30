"""Optimalizace nabíjecích zastávek — dynamické programování nad stavem (uzel, SoC po 1 %).

Uzly: start, kandidátní stanice seřazené podél trasy, cíl. Graf je acyklický (jen dopředu), takže DP je exaktní.
- Hrana i→j je přípustná, jen když příjezdový SoC ≥ rezerva (stanice / cíl).
- Na stanici lze odjet s libovolným SoC nad příjezdem → cílové % nabití je výsledkem optimalizace.
- Cílová funkce (v minutách): čas + w_cena·Kč + penalizace − bonus preferované sítě (jen vyvážený režim).
SoC se zaokrouhluje vždy dolů (konzervativně), chyba ≤ 1 % na úsek.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .charging import ChargeTable, charge_cost, station_charge_table
from .energy import CalibrationFn, RouteProfile, detour_energy, route_profile
from .models import DriveProfile, EnergyParams, Mode, PlanParams, Route, Station, Tariff, Vehicle

SINGLE_POINT_PENALTY_MIN = 2.0      # riziko obsazení stanice s jediným bodem
LOW_POWER_PENALTY_MIN = 10.0        # stanice pod uživatelskou preferencí výkonu (měkké omezení)
CHEAPEST_VOT_CZK_H = 30.0           # „Nejlevnější" stále mírně hlídá čas, aby nevznikaly absurdní objížďky
TIEBREAK_PER_SOC = 1e-3             # min na % příjezdového SoC


@dataclass
class StopPlan:
    station: Station
    arrive_km: float
    arrive_soc: int
    depart_soc: int
    charge_min: float
    grid_kwh: float
    cost_czk: float
    avg_kw: float
    next_leg_km: float = 0.0


@dataclass
class Plan:
    feasible: bool
    reason: str = ""
    stops: List[StopPlan] = field(default_factory=list)
    distance_km: float = 0.0
    drive_min: float = 0.0
    charge_min: float = 0.0
    stop_overhead_min: float = 0.0
    total_min: float = 0.0
    cost_czk: float = 0.0
    arrival_soc: int = 0
    trip_energy_kwh: float = 0.0
    warnings: List[str] = field(default_factory=list)
    profile: DriveProfile = DriveProfile.STANDARD
    mode: Mode = Mode.FASTEST


@dataclass
class _Node:
    km: float
    station: Optional[Station] = None
    det_kwh: float = 0.0     # zajížďka jedním směrem
    det_min: float = 0.0
    det_km: float = 0.0
    table: Optional[ChargeTable] = None
    tariff: Optional[Tariff] = None
    penalty_min: float = 0.0
    bonus_min: float = 0.0      # preferovaná síť; plný bonus až od 20 kWh, aby nevznikaly zbytečné mini-zastávky


# label = (objective, time_min, cost_czk, parent)
_Label = Tuple[float, float, float, Optional[Tuple[str, int, int]]]


def _weights(params: PlanParams) -> float:
    """Kolik minut „stojí" 1 Kč."""
    if params.mode == Mode.FASTEST:
        return 1e-4
    if params.mode == Mode.CHEAPEST:
        return 60.0 / CHEAPEST_VOT_CZK_H
    return 60.0 / max(params.value_of_time_czk_h, 1.0)


def usable_stations(stations: Sequence[Station], vehicle: Vehicle, params: PlanParams,
                    tariffs: Dict[str, Tariff], from_km: float, to_km: float) -> List[Station]:
    out = []
    for s in stations:
        if not s.access_ok or vehicle.connector not in s.connectors:
            continue
        if s.available is False:            # ověřený výpadek
            continue
        if not (from_km < s.route_km < to_km):
            continue
        if params.only_preferred and not (tariffs.get(s.operator) and tariffs[s.operator].preferred):
            continue
        out.append(s)
    return sorted(out, key=lambda s: (s.route_km, s.id))


def plan_route(route: Route, stations: Sequence[Station], vehicle: Vehicle, params: PlanParams,
               energy: Optional[EnergyParams] = None, tariffs: Optional[Dict[str, Tariff]] = None,
               calibration: Optional[CalibrationFn] = None, start_km: float = 0.0,
               profile_cache: Optional[RouteProfile] = None) -> Plan:
    energy = energy or EnergyParams()
    tariffs = tariffs or {}
    prof = profile_cache or route_profile(route, vehicle, energy, params.profile, calibration)
    end_km = prof.total_km
    mult = params.energy_factor * ((1.0 + energy.uncertainty) if params.conservative else 1.0)
    cap = vehicle.usable_kwh
    w_cost = _weights(params)

    cands = usable_stations(stations, vehicle, params, tariffs, start_km, end_km)
    nodes: List[_Node] = [_Node(start_km)]
    for s in cands:
        t = tariffs.get(s.operator)
        pen = 0.0
        if s.points <= 1 and not s.is_live_status:
            pen += SINGLE_POINT_PENALTY_MIN
        if params.min_station_kw and s.max_kw < params.min_station_kw:
            pen += LOW_POWER_PENALTY_MIN
        bonus = params.preferred_bonus_min / max(t.priority, 1) \
            if params.mode == Mode.BALANCED and t is not None and t.preferred else 0.0
        nodes.append(_Node(
            s.route_km, s, detour_energy(s.detour_km, vehicle, energy) * mult, s.detour_min, s.detour_km,
            station_charge_table(vehicle, s, params.battery_temp_c), t, pen, bonus,
        ))
    nodes.append(_Node(end_km))
    n = len(nodes)
    dest = n - 1

    arr: List[List[Optional[_Label]]] = [[None] * 101 for _ in range(n)]
    dep: List[List[Optional[_Label]]] = [[None] * 101 for _ in range(n)]
    start_soc = int(math.floor(min(params.start_soc, 100.0) + 1e-9))
    dep[0][start_soc] = (0.0, 0.0, 0.0, None)

    for i in range(n - 1):
        ni = nodes[i]
        # 1) na stanici: příjezd a → odjezd b (> a)
        if ni.station is not None:
            for a in range(101):
                la = arr[i][a]
                if la is None:
                    continue
                for b in range(a + 1, 101):
                    t_ch = ni.table.time(a, b)
                    kwh = ni.table.energy(a, b)
                    c = charge_cost(ni.tariff, kwh, t_ch, params.default_price_kwh)
                    t_add = t_ch + params.stop_overhead_min
                    # + nepatrná preference nižšího příjezdového SoC: při shodném čase nezastavovat zbytečně brzy
                    bonus = ni.bonus_min * min(1.0, kwh / 20.0)
                    obj = la[0] + t_add + w_cost * c + ni.penalty_min - bonus + TIEBREAK_PER_SOC * a
                    cur = dep[i][b]
                    if cur is None or obj < cur[0] - 1e-9:
                        dep[i][b] = (obj, la[1] + t_add, la[2] + c, ("arr", i, a))
        states = [(d, lab) for d, lab in enumerate(dep[i]) if lab is not None]
        if not states:
            continue
        # 2) jízda i → j
        for j in range(i + 1, n):
            nj = nodes[j]
            e = prof.energy_between(ni.km, nj.km) * mult + ni.det_kwh + nj.det_kwh
            e_pct = e / cap * 100.0
            if e_pct > 130:
                break
            t = prof.minutes_between(ni.km, nj.km) + ni.det_min + nj.det_min
            reserve = params.reserve_destination if j == dest else params.reserve_station
            for d, lab in states:
                a_f = d - e_pct
                if a_f < reserve - 1e-9:
                    continue
                a = int(math.floor(min(a_f, 100.0) + 1e-9))
                obj = lab[0] + t
                cur = arr[j][a]
                if cur is None or obj < cur[0] - 1e-9:
                    arr[j][a] = (obj, lab[1] + t, lab[2], ("dep", i, d))

    best_soc, best = None, None
    for a, lab in enumerate(arr[dest]):
        if lab is not None and (best is None or lab[0] < best[0] - 1e-9):
            best_soc, best = a, lab
    if best is None:
        return _infeasible(nodes, arr, dep, params, prof, cap, mult, cands, start_soc)
    return _reconstruct(nodes, arr, dep, dest, best_soc, params, prof, cap, mult)


def _reconstruct(nodes, arr, dep, dest, soc, params, prof, cap, mult) -> Plan:
    # cesta zpět: arr(dest) → dep(i) → arr(i) → ...
    chain = []
    kind, idx, s = "arr", dest, soc
    while True:
        lab = (arr if kind == "arr" else dep)[idx][s]
        chain.append((kind, idx, s, lab))
        if lab[3] is None:
            break
        kind, idx, s = lab[3]
    chain.reverse()

    stops: List[StopPlan] = []
    for k, (kind, idx, s, lab) in enumerate(chain):
        if kind == "dep" and nodes[idx].station is not None:
            a = chain[k - 1][2]
            nd = nodes[idx]
            t_ch = nd.table.time(a, s)
            kwh = nd.table.energy(a, s)
            stops.append(StopPlan(
                nd.station, nd.km, a, s, t_ch, kwh,
                charge_cost(nd.tariff, kwh, t_ch, params.default_price_kwh),
                kwh / (t_ch / 60.0) if t_ch > 0 else 0.0,
            ))
    for k, st in enumerate(stops):
        nxt = stops[k + 1].arrive_km if k + 1 < len(stops) else prof.total_km
        st.next_leg_km = nxt - st.arrive_km

    final = arr[dest][soc]
    charge_min = sum(s.charge_min for s in stops)
    overhead = params.stop_overhead_min * len(stops)
    start_km = nodes[0].km
    det_km = sum(2 * n.det_km for n in nodes if n.station is not None and n.station in [s.station for s in stops])
    plan = Plan(
        feasible=True, stops=stops,
        distance_km=prof.total_km - start_km + det_km,
        drive_min=final[1] - charge_min - overhead, charge_min=charge_min, stop_overhead_min=overhead,
        total_min=final[1], cost_czk=final[2], arrival_soc=soc,
        trip_energy_kwh=prof.energy_between(start_km, prof.total_km) * mult,
        profile=params.profile, mode=params.mode,
    )
    for st in stops:
        if not st.station.is_live_status:
            plan.warnings.append(f"{st.station.name}: dostupnost neověřena (data {st.station.data_source or 'bez zdroje'}"
                                 f"{', ' + st.station.data_updated if st.station.data_updated else ''}).")
        for note in st.station.notes:
            plan.warnings.append(f"{st.station.name}: {note}")
    return plan


def _infeasible(nodes, arr, dep, params, prof, cap, mult, cands, start_soc) -> Plan:
    reached = [i for i in range(len(nodes) - 1) if any(x is not None for x in dep[i])]
    far = max(reached, key=lambda i: nodes[i].km)
    nf = nodes[far]
    best_d = max(d for d, x in enumerate(dep[far]) if x is not None)
    nxt = far + 1 if far + 1 < len(nodes) else None
    where = nf.station.name if nf.station else "start"
    if not cands:
        reason = ("V datech není žádná použitelná nabíječka (CCS2, přístupná) na trase a cíl není dosažitelný "
                  f"s rezervou {params.reserve_destination:.0f} %. Zkontrolujte zdroj dat nabíječek.")
    else:
        target = nodes[nxt]
        need = prof.energy_between(nf.km, target.km) * mult / cap * 100.0
        name = target.station.name if target.station else "cíl"
        reserve = params.reserve_station if target.station else params.reserve_destination
        reason = (f"Bezpečný plán neexistuje: z místa „{where}“ (km {nf.km:.0f}, max. {best_d} %) "
                  f"na „{name}“ (km {target.km:.0f}) je potřeba ~{need:.0f} % + rezerva {reserve:.0f} %. "
                  "Zvažte nižší rychlost, menší rezervu nebo delší zajížďku k nabíječce.")
    return Plan(feasible=False, reason=reason, profile=params.profile, mode=params.mode)


def plan_variants(route: Route, stations: Sequence[Station], vehicle: Vehicle, params: PlanParams,
                  energy: Optional[EnergyParams] = None, tariffs: Optional[Dict[str, Tariff]] = None,
                  calibration: Optional[CalibrationFn] = None) -> Dict[str, Plan]:
    """Varianty pro porovnání: rychlá jízda / standard / eko × zvolený režim + režimy pro standardní jízdu."""
    from dataclasses import replace
    out: Dict[str, Plan] = {}
    for prof in DriveProfile:
        out[f"jizda:{prof.value}"] = plan_route(route, stations, vehicle, replace(params, profile=prof),
                                                energy, tariffs, calibration)
    for mode in Mode:
        out[f"rezim:{mode.value}"] = plan_route(route, stations, vehicle, replace(params, mode=mode),
                                                energy, tariffs, calibration)
    return out
