"""Propojení: adresa → trasa → počasí → nabíječky → optimalizace → výsledek pro API / příkazovou řádku."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from vrp.energy import CalibrationFn
from vrp.models import DriveProfile, EnergyParams, Mode, PlanParams, Station, Tariff, Vehicle
from vrp.optimizer import Plan, plan_route

from .chargers import stations_along
from .geocode import geocode
from .routing import RouteResult, plan_geometry
from .weather import apply_weather

ATTRIBUTION = ("Mapová a nabíjecí data © OpenStreetMap contributors (ODbL) · Open Charge Map (CC BY 4.0) · "
               "Weather data by Open-Meteo.com (CC BY 4.0) · trasy openrouteservice / OSRM")

# Varianty k porovnání: tři režimy optimalizace + úsporná jízda (zda pomalejší jízda celkově nevyjde rychleji)
VARIANTS = {
    "nejrychlejsi": dict(mode=Mode.FASTEST),
    "vyvazeny": dict(mode=Mode.BALANCED),
    "nejlevnejsi": dict(mode=Mode.CHEAPEST),
    "eko": dict(mode=Mode.FASTEST, profile=DriveProfile.ECO),
}


@dataclass
class TripResult:
    origin: str
    destination: str
    route: RouteResult
    plans: Dict[str, Plan]
    stations: List[Station]
    notes: List[str] = field(default_factory=list)

    @property
    def station_count(self) -> int:
        return len(self.stations)


def plan_variants_for(rr: RouteResult, stations: Sequence[Station], params: PlanParams, vehicle: Vehicle,
                      energy: Optional[EnergyParams], tariffs: Optional[Dict[str, Tariff]],
                      calibration: Optional[CalibrationFn] = None,
                      variants: Optional[Sequence[str]] = None) -> Dict[str, Plan]:
    out = {}
    for name in variants or VARIANTS:
        out[name] = plan_route(rr.route, stations, vehicle, replace(params, **VARIANTS[name]), energy, tariffs,
                               calibration)
    return out


def plan_trip(origin: str, destination: str, params: PlanParams, via: Sequence[str] = (),
              vehicle: Optional[Vehicle] = None, energy: Optional[EnergyParams] = None,
              tariffs: Optional[Dict[str, Tariff]] = None, depart: Optional[datetime] = None,
              corridor_km: float = 5.0, calibration: Optional[CalibrationFn] = None,
              variants: Optional[Sequence[str]] = None) -> TripResult:
    vehicle = vehicle or Vehicle()
    o = geocode(origin)
    d = geocode(destination)
    vias = [geocode(v) for v in via]
    rr = plan_geometry([(o[0], o[1])] + [(v[0], v[1]) for v in vias] + [(d[0], d[1])])
    notes = list(rr.notes)
    notes += apply_weather(rr.route, rr.points, depart)
    stations, issues = stations_along(rr.points, corridor_km)
    notes += issues
    plans = plan_variants_for(rr, stations, params, vehicle, energy, tariffs, calibration, variants)
    return TripResult(o[2], d[2], rr, plans, stations, notes)
