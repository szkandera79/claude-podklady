"""Energetický model a nabíjení — scénáře 4, 5, 6, 11 + ověření proti záznamu PRE 22. 1. 2026."""
from vrp.calibration import estimate_usable_kwh
from vrp.charging import build_charge_table
from vrp.energy import battery_factor, hvac_kw, route_profile
from vrp.models import DriveProfile, EnergyParams, RoadClass, Surface

from conftest import make_route


def per100(route, vehicle, profile=DriveProfile.FAST, p=None):
    prof = route_profile(route, vehicle, p or EnergyParams(), profile)
    return prof.kwh[-1] / prof.total_km * 100


# 4 — dálnice v létě
def test_summer_motorway_matches_user_value(vehicle):
    r = make_route([(100, RoadClass.MOTORWAY, 125, 20)])
    assert abs(per100(r, vehicle) - 25.0) < 0.1


# 6 — okresní silnice
def test_district_road_90(vehicle):
    r = make_route([(100, RoadClass.DISTRICT, 90, 20)])
    assert abs(per100(r, vehicle) - 17.5) < 0.1


# 5 — dálnice v zimě: součet jednotlivých složek, ne vymyšlené číslo
def test_winter_motorway_composed_of_factors(vehicle):
    p = EnergyParams()
    summer = per100(make_route([(100, RoadClass.MOTORWAY, 125, 20)]), vehicle)
    winter = per100(make_route([(100, RoadClass.MOTORWAY, 125, -5)]), vehicle)
    expected = (25.01 + hvac_kw(-5, p) / 125 * 100) * battery_factor(-5, p)
    assert abs(winter - expected) < 0.1
    assert 1.1 < winter / summer < 1.4


def test_snow_headwind_and_climb_increase_consumption(vehicle):
    base = per100(make_route([(100, RoadClass.MOTORWAY, 125, 20)]), vehicle)
    assert per100(make_route([(100, RoadClass.MOTORWAY, 125, 20, 0, Surface.SNOW)]), vehicle) > base * 1.1
    assert per100(make_route([(100, RoadClass.MOTORWAY, 125, 20, 0, Surface.DRY, 20)]), vehicle) > base
    up = per100(make_route([(100, RoadClass.MOTORWAY, 125, 20, 500)]), vehicle)
    down = per100(make_route([(100, RoadClass.MOTORWAY, 125, 20, -500)]), vehicle)
    assert up > base > down
    assert up - base > base - down          # rekuperace nevrátí vše


def test_eco_profile_uses_less_energy_but_more_time(vehicle):
    r = make_route([(200, RoadClass.MOTORWAY, 130, 20)])
    p = EnergyParams()
    eco = route_profile(r, vehicle, p, DriveProfile.ECO)
    fast = route_profile(r, vehicle, p, DriveProfile.FAST)
    assert eco.kwh[-1] < fast.kwh[-1]
    assert eco.minutes[-1] > fast.minutes[-1]


# 11 — 100 kW vs 250 kW stanice: Voyah bere max. 89 kW → stejný čas
def test_station_power_above_car_limit_gives_no_gain(vehicle):
    t100 = build_charge_table(vehicle, 100)
    t250 = build_charge_table(vehicle, 250)
    t50 = build_charge_table(vehicle, 50)
    assert abs(t100.time(10, 80) - t250.time(10, 80)) < 1e-9
    assert t50.time(10, 80) > t100.time(10, 80) * 1.5


def test_charging_above_80_is_slower_per_percent(vehicle):
    t = build_charge_table(vehicle, 150)
    assert t.time(82, 90) / 8 > 2 * t.time(10, 80) / 70


def test_reproduces_pre_record(vehicle):
    """Záznam PRE 200 kW: 28 → 63 % za 23:33 min, 35,4 kWh ze stojanu, 0 °C, zahřátá baterie."""
    t = build_charge_table(vehicle, 200)
    assert abs(t.time(28, 63) - 23.55) / 23.55 < 0.07
    assert abs(t.energy(28, 63) - 35.4) / 35.4 < 0.07


def test_cold_battery_slows_charging(vehicle):
    warm = build_charge_table(vehicle, 150)
    cold = build_charge_table(vehicle, 150, battery_temp_c=-10)
    assert cold.time(10, 80) > warm.time(10, 80) * 1.4


def test_usable_capacity_estimate_from_pre_record():
    est = estimate_usable_kwh(35.4, 28, 63)
    assert 92 < est < 100
