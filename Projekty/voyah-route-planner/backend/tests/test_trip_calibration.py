"""Aktivní cesta a kalibrace — scénáře 8 a 9."""
from vrp.calibration import CalibrationTable, Observation
from vrp.energy import route_profile
from vrp.models import EnergyParams, PlanParams, RoadClass
from vrp.optimizer import plan_route
from vrp.trip import SocReading, soc_update

from conftest import motorway, station

STATIONS = [station(str(k), k) for k in range(100, 600, 50)]


def predicted_soc_at(route, vehicle, km, start=90):
    prof = route_profile(route, vehicle, EnergyParams(), PlanParams(start).profile)
    return start - prof.energy_between(0, km) / vehicle.usable_kwh * 100


# 8 — ruční aktualizace podle predikce
def test_soc_update_on_prediction(vehicle):
    r = motorway(600)
    p = PlanParams(90)
    soc = predicted_soc_at(r, vehicle, 120)
    upd = soc_update(r, STATIONS, vehicle, p, SocReading(0, 90), SocReading(120, soc))
    assert abs(upd.k_trip - 1.0) < 0.02
    assert upd.plan.feasible
    assert not [w for w in upd.warnings if "níž" in w]
    assert all(s.arrive_km > 120 for s in upd.plan.stops)


# 9 — výrazně vyšší spotřeba
def test_much_higher_consumption_warns_and_replans(vehicle):
    r = motorway(600)
    p = PlanParams(90)
    before = plan_route(r, STATIONS, vehicle, p)
    soc = predicted_soc_at(r, vehicle, 150) - 12
    upd = soc_update(r, STATIONS, vehicle, p, SocReading(0, 90), SocReading(150, soc), previous_plan=before)
    assert upd.k_trip > 1.2
    assert any("níž" in w for w in upd.warnings)
    assert upd.plan.feasible
    assert upd.plan.charge_min > 0


def test_soc_update_infeasible_gives_clear_warning(vehicle):
    r = motorway(400)
    upd = soc_update(r, [], vehicle, PlanParams(90), SocReading(0, 90), SocReading(100, 50))
    assert not upd.plan.feasible
    assert any(w.startswith("POZOR") for w in upd.warnings)


def test_small_deviation_on_short_leg_has_low_weight(vehicle):
    r = motorway(600)
    soc = predicted_soc_at(r, vehicle, 20) - 2          # 2 % chyba po 20 km ≈ šum zaokrouhlení
    upd = soc_update(r, STATIONS, vehicle, PlanParams(90), SocReading(0, 90), SocReading(20, soc))
    assert upd.k_trip < 1.15


def test_calibration_shrinks_toward_measurements():
    cal = CalibrationTable(usable_kwh=100)
    for _ in range(5):
        cal.add(Observation({RoadClass.MOTORWAY: 200}, 0.0, predicted_kwh=50, soc_start=90, soc_end=35))  # 55 kWh
    k = cal.factor(RoadClass.MOTORWAY, 0.0)
    assert 1.05 < k <= 1.10
    assert cal.factor(RoadClass.MOTORWAY, 20.0) == 1.0     # jiné teplotní pásmo nedotčeno
    assert cal.factor(RoadClass.CITY, 0.0) == 1.0
    assert cal.uncertainty() < 0.08


def test_calibration_rejects_outliers():
    cal = CalibrationTable(usable_kwh=100)
    applied = cal.add(Observation({RoadClass.MOTORWAY: 100}, 20.0, predicted_kwh=25, soc_start=90, soc_end=50))
    assert not applied
    assert cal.factor(RoadClass.MOTORWAY, 20.0) == 1.0
    assert len(cal.observations) == 1


def test_calibration_feeds_planner(vehicle):
    cal = CalibrationTable(usable_kwh=100)
    for _ in range(10):
        cal.add(Observation({RoadClass.MOTORWAY: 200}, 20.0, predicted_kwh=50, soc_start=90, soc_end=30))
    r = motorway(450)
    base = plan_route(r, STATIONS, vehicle, PlanParams(90))
    cal_plan = plan_route(r, STATIONS, vehicle, PlanParams(90), calibration=cal.as_fn())
    assert cal_plan.trip_energy_kwh > base.trip_energy_kwh * 1.05
