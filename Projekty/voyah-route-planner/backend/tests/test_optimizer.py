"""Optimalizace zastávek — scénáře 1, 2, 3, 7, 10, 12, 13, 14 a režimy."""
from dataclasses import replace

from vrp.models import DriveProfile, Mode, PlanParams
from vrp.optimizer import plan_route, plan_variants

from conftest import motorway, station


def params(soc=90, **kw):
    return PlanParams(start_soc=soc, **kw)


# 1 — bez nabíjení
def test_reachable_without_charging(vehicle):
    plan = plan_route(motorway(200), [station("A", 100)], vehicle, params(80))
    assert plan.feasible and plan.stops == []
    assert plan.arrival_soc >= 15
    assert plan.charge_min == 0


# 2 — jedna zastávka
def test_one_stop(vehicle):
    st = [station("A", 150), station("B", 250), station("C", 350)]
    plan = plan_route(motorway(450), st, vehicle, params(90))
    assert plan.feasible and len(plan.stops) == 1
    s = plan.stops[0]
    assert s.arrive_soc >= 10 and plan.arrival_soc >= 15
    assert s.depart_soc > s.arrive_soc
    assert abs(plan.total_min - (plan.drive_min + plan.charge_min + plan.stop_overhead_min)) < 1e-6


# 3 — více zastávek
def test_multiple_stops(vehicle):
    st = [station(str(k), k) for k in range(100, 900, 100)]
    plan = plan_route(motorway(900), st, vehicle, params(90))
    assert plan.feasible and len(plan.stops) >= 2
    assert all(s.arrive_soc >= 10 for s in plan.stops)
    assert plan.arrival_soc >= 15
    kms = [s.arrive_km for s in plan.stops]
    assert kms == sorted(kms)


# 10 — nabití nad 80 % je výhodnější, když ušetří zastávku s velkou zajížďkou
def test_charging_above_80_when_it_saves_a_costly_stop(vehicle):
    st = [station("A", 250), station("B", 450, detour_km=8, detour_min=10)]
    plan = plan_route(motorway(560), st, vehicle, params(90))
    assert plan.feasible and len(plan.stops) == 1
    assert plan.stops[0].depart_soc > 80


def test_two_short_stops_beat_charging_above_80_without_detour(vehicle):
    st = [station("A", 250), station("B", 450)]
    plan = plan_route(motorway(560), st, vehicle, params(90))
    assert plan.feasible
    assert all(s.depart_soc <= 82 for s in plan.stops)


def test_does_not_blindly_stop_at_furthest_station(vehicle):
    """Stanice 50 kW dál po trase vs. rychlá stanice dřív — hlavní nabití proběhne na rychlé stanici.

    Pozn.: nad 90 % nabíjí Voyah jen ~20 kW, proto krátké dobití na 50kW stanici vyjde rychleji než 1 zastávka na 94 %.
    """
    st = [station("rychla", 180, kw=150), station("pomala", 260, kw=50)]
    plan = plan_route(motorway(500), st, vehicle, params(90))
    only_slow = plan_route(motorway(500), st[1:], vehicle, params(90))
    one_stop = plan_route(motorway(500), st[:1], vehicle, params(90))
    assert plan.feasible
    assert plan.stops[0].station.id == "rychla"
    assert plan.total_min < only_slow.total_min
    assert plan.total_min <= one_stop.total_min


# 7 — výpadek plánované stanice
def test_station_outage_replans(vehicle):
    st = [station("A", 200), station("B", 260), station("C", 320)]
    first = plan_route(motorway(500), st, vehicle, params(90))
    chosen = first.stops[0].station.id
    broken = [replace(s, available=False) if s.id == chosen else s for s in st]
    second = plan_route(motorway(500), broken, vehicle, params(90))
    assert second.feasible
    assert chosen not in [s.station.id for s in second.stops]


# 12 — preference registrovaného provozovatele
def test_preferred_operator_in_balanced_mode(vehicle, tariffs):
    st = [station("cizi", 200, operator="Jiný"), station("pre", 205, operator="PRE")]
    plan = plan_route(motorway(450), st, vehicle, params(90, mode=Mode.BALANCED), tariffs=tariffs)
    assert [s.station.operator for s in plan.stops] == ["PRE"]
    assert plan.cost_czk > 0


def test_preference_is_not_absolute_when_much_faster_exists(vehicle, tariffs):
    st = [station("cizi", 200, kw=150, operator="Jiný"), station("pre", 205, kw=50, operator="PRE")]
    plan = plan_route(motorway(450), st, vehicle, params(90, mode=Mode.FASTEST), tariffs=tariffs)
    assert [s.station.operator for s in plan.stops] == ["Jiný"]
    only = plan_route(motorway(450), st, vehicle, params(90, only_preferred=True), tariffs=tariffs)
    assert [s.station.operator for s in only.stops] == ["PRE"]


def test_cheapest_mode_picks_cheapest_network(vehicle, tariffs):
    st = [station("eon", 200, operator="E.ON"), station("lidl", 210, operator="Lidl"),
          station("pre", 220, operator="PRE")]
    plan = plan_route(motorway(450), st, vehicle, params(90, mode=Mode.CHEAPEST), tariffs=tariffs)
    assert [s.station.operator for s in plan.stops] == ["Lidl"]


# 13 — nedostupná data o nabíječkách
def test_no_charger_data(vehicle):
    plan = plan_route(motorway(500), [], vehicle, params(90))
    assert not plan.feasible
    assert "žádná použitelná nabíječka" in plan.reason


# 14 — žádná bezpečně dosažitelná nabíječka
def test_gap_without_reachable_charger(vehicle):
    st = [station("A", 50), station("B", 470)]
    plan = plan_route(motorway(520), st, vehicle, params(80))
    assert not plan.feasible
    assert "km 470" in plan.reason


def test_inaccessible_and_wrong_connector_ignored(vehicle):
    st = [station("tesla", 200, access_ok=False), station("chademo", 210, connectors=("CHAdeMO",))]
    plan = plan_route(motorway(500), st, vehicle, params(90))
    assert not plan.feasible


def test_conservative_mode_plans_more_energy(vehicle):
    st = [station(str(k), k) for k in range(100, 700, 50)]
    normal = plan_route(motorway(700), st, vehicle, params(90))
    cons = plan_route(motorway(700), st, vehicle, params(90, conservative=True))
    assert cons.trip_energy_kwh > normal.trip_energy_kwh
    assert cons.charge_min >= normal.charge_min


def test_detour_counted_in_time_and_distance(vehicle):
    base = plan_route(motorway(450), [station("A", 250)], vehicle, params(90))
    det = plan_route(motorway(450), [station("A", 250, detour_km=3, detour_min=4)], vehicle, params(90))
    assert abs(det.distance_km - base.distance_km - 6) < 1e-6
    assert det.total_min > base.total_min + 7


def test_variants_compare_profiles(vehicle):
    st = [station(str(k), k) for k in range(100, 800, 60)]
    v = plan_variants(motorway(800), st, vehicle, params(90))
    eco, fast = v["jizda:eko"], v["jizda:rychly"]
    assert eco.feasible and fast.feasible
    assert eco.charge_min < fast.charge_min           # méně energie → kratší nabíjení
    assert eco.drive_min > fast.drive_min


def test_unverified_availability_is_flagged(vehicle):
    plan = plan_route(motorway(450), [station("A", 250)], vehicle, params(90))
    assert any("dostupnost neověřena" in w for w in plan.warnings)
