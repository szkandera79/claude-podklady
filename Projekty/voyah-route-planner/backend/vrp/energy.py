"""Energetický model jízdy (ANALYZA.md kap. 5).

E_úsek = [ c(v_vzduch)·d + E_převýšení + P_HVAC(T)·t ] × f_vozovka × f_baterie(T) × k_kalibrace

c(v) = a + b·v²  [kWh/100 km] — nafitováno na uživatelské letní hodnoty (17,5 @ 90, 25 @ 120–130 km/h).
Všechny koeficienty jsou předpoklady, které se zpřesňují kalibrací z jízd.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Callable, List, Optional

from .models import DriveProfile, EnergyParams, RoadClass, Route, Segment, Vehicle

G = 9.81
J_PER_KWH = 3.6e6

# Ekonomický profil: strop rychlosti dle třídy silnice
ECO_CAP = {
    RoadClass.MOTORWAY: 110, RoadClass.EXPRESSWAY: 100, RoadClass.PRIMARY: 80,
    RoadClass.DISTRICT: 80, RoadClass.CITY: 50,
}
CITY_TRAFFIC_FACTOR = 0.7   # průměrná rychlost ve městě vůči limitu (křižovatky, provoz)

CalibrationFn = Callable[[RoadClass, float], float]


def planned_speed(seg: Segment, profile: DriveProfile) -> float:
    """Plánovaná průměrná rychlost úseku; nikdy nad rychlostní limit."""
    limit = seg.speed_limit
    if seg.road_class == RoadClass.CITY:
        base = limit * CITY_TRAFFIC_FACTOR
        return min(base, ECO_CAP[RoadClass.CITY] * CITY_TRAFFIC_FACTOR) if profile == DriveProfile.ECO else base
    if profile == DriveProfile.ECO:
        return min(limit, ECO_CAP[seg.road_class])
    if profile == DriveProfile.STANDARD:
        return limit * 0.95
    return limit


def consumption_per_100km(v_kmh: float, p: EnergyParams, road_class: RoadClass = RoadClass.MOTORWAY,
                          headwind_kmh: float = 0.0) -> float:
    """Jízdní složka při referenčních (letních) podmínkách, bez převýšení a topení."""
    v_air = v_kmh + headwind_kmh
    c = p.a + p.b * v_air * abs(v_air)
    if road_class == RoadClass.CITY:
        c += p.city_extra
    return max(c, 0.0)


def hvac_kw(temp_c: float, p: EnergyParams) -> float:
    if temp_c < p.heat_start_c:
        return p.heat_base_kw + p.heat_kw_per_c * (p.heat_start_c - temp_c)
    if temp_c > p.cool_start_c:
        return p.cool_kw
    return 0.0


def battery_factor(temp_c: float, p: EnergyParams) -> float:
    return 1.0 + p.batt_temp_coef * max(0.0, 15.0 - temp_c)


@dataclass
class SegmentResult:
    speed_kmh: float
    minutes: float
    kwh: float


def segment_energy(seg: Segment, vehicle: Vehicle, p: EnergyParams, profile: DriveProfile,
                   calibration: Optional[CalibrationFn] = None) -> SegmentResult:
    v = planned_speed(seg, profile)
    hours = seg.length_km / v
    drive = consumption_per_100km(v, p, seg.road_class, seg.headwind_kmh) / 100.0 * seg.length_km
    m = vehicle.total_mass
    dz = seg.elevation_delta_m
    if dz >= 0:
        elev = m * G * dz / p.drive_efficiency / J_PER_KWH
    else:
        elev = m * G * dz * p.regen_efficiency / J_PER_KWH
    hvac = hvac_kw(seg.temp_c, p) * hours
    kwh = (drive * p.surface_factor[seg.surface.value] + elev + hvac) * battery_factor(seg.temp_c, p)
    if calibration is not None:
        kwh *= calibration(seg.road_class, seg.temp_c)
    return SegmentResult(v, hours * 60.0, kwh)


@dataclass
class RouteProfile:
    """Kumulativní km, minuty a kWh podél trasy; dotaz na libovolnou polohu lineární interpolací."""

    km: List[float]
    minutes: List[float]
    kwh: List[float]

    def _interp(self, arr: List[float], x: float) -> float:
        if x <= 0:
            return arr[0]
        if x >= self.km[-1]:
            return arr[-1]
        i = bisect_right(self.km, x) - 1
        f = (x - self.km[i]) / (self.km[i + 1] - self.km[i])
        return arr[i] + f * (arr[i + 1] - arr[i])

    def energy_between(self, a_km: float, b_km: float) -> float:
        return self._interp(self.kwh, b_km) - self._interp(self.kwh, a_km)

    def minutes_between(self, a_km: float, b_km: float) -> float:
        return self._interp(self.minutes, b_km) - self._interp(self.minutes, a_km)

    @property
    def total_km(self) -> float:
        return self.km[-1]


def route_profile(route: Route, vehicle: Vehicle, p: EnergyParams, profile: DriveProfile,
                  calibration: Optional[CalibrationFn] = None) -> RouteProfile:
    km, mins, kwh = [0.0], [0.0], [0.0]
    for seg in route.segments:
        r = segment_energy(seg, vehicle, p, profile, calibration)
        km.append(km[-1] + seg.length_km)
        mins.append(mins[-1] + r.minutes)
        kwh.append(kwh[-1] + r.kwh)
    return RouteProfile(km, mins, kwh)


def detour_energy(detour_km: float, vehicle: Vehicle, p: EnergyParams, temp_c: float = 20.0) -> float:
    """Energie zajížďky jedním směrem — počítá se jako okresní silnice 50 km/h."""
    if detour_km <= 0:
        return 0.0
    seg = Segment(detour_km, RoadClass.DISTRICT, 50, temp_c=temp_c)
    return segment_energy(seg, vehicle, p, DriveProfile.FAST).kwh
