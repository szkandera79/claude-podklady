"""Aktivní cesta: ruční zadání SoC → porovnání s predikcí → přepočet plánu (ANALYZA.md kap. 7).

Krátkodobá odchylka (`k_trip`) se použije jen pro zbytek této cesty. Dlouhodobý profil se mění až po
skončení cesty přes `calibration.CalibrationTable` — jednorázová vichřice tak nezkazí model.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence

from .energy import CalibrationFn, route_profile
from .models import EnergyParams, PlanParams, Route, Station, Tariff, Vehicle
from .optimizer import Plan, plan_route

K_TRIP_MIN, K_TRIP_MAX = 0.7, 1.6
FULL_WEIGHT_KWH = 20.0       # pod touto spotřebou se měřená odchylka bere jen částečně (±1 % SoC = ±1 kWh)
WARN_DEVIATION_PCT = 5.0


@dataclass
class SocReading:
    route_km: float
    soc: float


@dataclass
class TripUpdate:
    predicted_soc: float
    actual_soc: float
    measured_ratio: float     # skutečná / predikovaná spotřeba od referenčního bodu
    k_trip: float             # použitá korekce pro zbytek cesty
    plan: Plan
    warnings: List[str] = field(default_factory=list)


def soc_update(route: Route, stations: Sequence[Station], vehicle: Vehicle, params: PlanParams,
               reference: SocReading, current: SocReading, energy: Optional[EnergyParams] = None,
               tariffs: Optional[Dict[str, Tariff]] = None, calibration: Optional[CalibrationFn] = None,
               previous_plan: Optional[Plan] = None) -> TripUpdate:
    """`reference` = poslední známý bod (start nebo odjezd z nabíječky), `current` = právě zadaný SoC."""
    energy = energy or EnergyParams()
    prof = route_profile(route, vehicle, energy, params.profile, calibration)
    predicted_kwh = prof.energy_between(reference.route_km, current.route_km)
    predicted_pct = predicted_kwh / vehicle.usable_kwh * 100.0
    used_pct = reference.soc - current.soc
    used_kwh = used_pct / 100.0 * vehicle.usable_kwh

    ratio = used_kwh / predicted_kwh if predicted_kwh > 0.5 else 1.0
    w = min(1.0, max(used_kwh, 0.0) / FULL_WEIGHT_KWH)
    k_trip = min(K_TRIP_MAX, max(K_TRIP_MIN, 1.0 + (ratio - 1.0) * w))

    new_params = replace(params, start_soc=current.soc, energy_factor=k_trip)
    plan = plan_route(route, stations, vehicle, new_params, energy, tariffs, calibration,
                      start_km=current.route_km, profile_cache=prof)

    warnings: List[str] = []
    predicted_soc = reference.soc - predicted_pct
    deviation = current.soc - predicted_soc
    if deviation <= -WARN_DEVIATION_PCT:
        warnings.append(f"Baterie je o {-deviation:.0f} % níž, než předpokládal plán "
                        f"(spotřeba ≈ {ratio * 100 - 100:+.0f} % proti modelu). Zbytek cesty počítán se zvýšenou spotřebou.")
    if not plan.feasible:
        warnings.append("POZOR: se současnou spotřebou nelze bezpečně dojet. " + plan.reason)
    elif plan.stops and plan.stops[0].arrive_soc < params.reserve_station + 3:
        warnings.append(f"Příjezd k další nabíječce jen s {plan.stops[0].arrive_soc} % — zvažte nižší rychlost.")
    if previous_plan is not None and plan.feasible:
        old = [s.station.id for s in previous_plan.stops if s.arrive_km > current.route_km]
        new = [s.station.id for s in plan.stops]
        if old != new:
            warnings.append("Plán zastávek se změnil: " + " → ".join(s.station.name for s in plan.stops) if new
                            else "Plán zastávek se změnil: další nabíjení už není potřeba.")
    return TripUpdate(predicted_soc, current.soc, ratio, k_trip, plan, warnings)
