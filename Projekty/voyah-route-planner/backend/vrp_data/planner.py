"""Propojení: adresa → trasa → počasí → nabíječky → optimalizace → výsledek pro API / příkazovou řádku."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from vrp.models import EnergyParams, Mode, PlanParams, Tariff, Vehicle
from vrp.optimizer import Plan, plan_route

from .chargers import stations_along
from .geocode import geocode
from .routing import RouteResult, plan_geometry
from .weather import apply_weather

ATTRIBUTION = ("Mapová a nabíjecí data © OpenStreetMap contributors (ODbL) · Open Charge Map (CC BY 4.0) · "
               "Weather data by Open-Meteo.com (CC BY 4.0) · trasy openrouteservice / OSRM")


@dataclass
class TripResult:
    origin: str
    destination: str
    route: RouteResult
    plans: Dict[str, Plan]
    station_count: int
    notes: List[str] = field(default_factory=list)


def plan_trip(origin: str, destination: str, params: PlanParams, via: Sequence[str] = (),
              vehicle: Optional[Vehicle] = None, energy: Optional[EnergyParams] = None,
              tariffs: Optional[Dict[str, Tariff]] = None, depart: Optional[datetime] = None,
              corridor_km: float = 5.0, modes: Sequence[Mode] = tuple(Mode)) -> TripResult:
    vehicle = vehicle or Vehicle()
    o = geocode(origin)
    d = geocode(destination)
    vias = [geocode(v) for v in via]
    rr = plan_geometry([(o[0], o[1])] + [(v[0], v[1]) for v in vias] + [(d[0], d[1])])
    notes = list(rr.notes)
    notes += apply_weather(rr.route, rr.points, depart)
    stations, issues = stations_along(rr.points, corridor_km)
    notes += issues
    plans = {m.value: plan_route(rr.route, stations, vehicle, replace(params, mode=m), energy, tariffs)
             for m in modes}
    return TripResult(o[2], d[2], rr, plans, len(stations), notes)
