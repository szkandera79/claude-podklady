"""Počasí z Open-Meteo (zdarma pro nekomerční užití, CC BY 4.0 — atribuce „Weather data by Open-Meteo.com").

Trasa se navzorkuje po ~25 km; pro každý úsek se vezme nejbližší vzorek a hodina průjezdu.
Protivítr = rychlost větru × 0,6 (10 m → výška auta) × cos(směr, odkud vane − kurz jízdy).
Povrch: sněžení > 0 → sníh, srážky ≥ 0,2 mm/h → mokro.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence, Tuple

from vrp.models import Route, Surface

from .geo import Polyline, bearing_deg
from .http import SourceError, request_json

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
SAMPLE_KM = 25.0
WIND_HEIGHT_FACTOR = 0.6
WET_MM_H = 0.2


def headwind_kmh(wind_kmh: float, wind_from_deg: float, heading_deg: float) -> float:
    return wind_kmh * WIND_HEIGHT_FACTOR * math.cos(math.radians(wind_from_deg - heading_deg))


def surface_from(precip_mm: float, snow_cm: float) -> Surface:
    if snow_cm > 0:
        return Surface.SNOW
    if precip_mm >= WET_MM_H:
        return Surface.WET
    return Surface.DRY


def apply_weather(route: Route, points: Sequence[Tuple[float, float]], depart: Optional[datetime] = None,
                  fallback_temp_c: Optional[float] = None) -> List[str]:
    """Doplní teplotu, protivítr a povrch do úseků trasy. Vrací upozornění."""
    depart = (depart or datetime.now(timezone.utc)).astimezone(timezone.utc)
    line = Polyline.from_points(points)
    n = max(2, int(line.length_km // SAMPLE_KM) + 1)
    samples = [line.point_at(line.length_km * k / (n - 1)) for k in range(n)]
    try:
        data = request_json(FORECAST_URL, params={
            "latitude": ",".join(f"{a:.3f}" for a, _ in samples),
            "longitude": ",".join(f"{b:.3f}" for _, b in samples),
            "hourly": "temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,snowfall",
            "wind_speed_unit": "kmh", "timezone": "UTC", "forecast_days": 7}, timeout=30,
            cache_kind="weather", ttl_s=3600)
    except SourceError as e:
        if fallback_temp_c is not None:
            for s in route.segments:
                s.temp_c = fallback_temp_c
        return [f"Počasí nedostupné ({e}) — " + (f"použita zadaná teplota {fallback_temp_c:.0f} °C."
                                                if fallback_temp_c is not None else "počítáno s +20 °C bez větru.")]
    if isinstance(data, dict):
        data = [data]

    km = 0.0
    minutes = 0.0
    for seg in route.segments:
        mid = km + seg.length_km / 2
        k = min(n - 1, int(round(mid / line.length_km * (n - 1)))) if line.length_km else 0
        h = data[k]["hourly"]
        t = depart + timedelta(minutes=minutes)
        key = t.strftime("%Y-%m-%dT%H:00")
        try:
            i = h["time"].index(key)
        except ValueError:
            i = 0 if t < datetime.fromisoformat(h["time"][0]).replace(tzinfo=timezone.utc) else len(h["time"]) - 1
        a, b = line.point_at(max(0.0, mid - 0.3)), line.point_at(min(line.length_km, mid + 0.3))
        seg.temp_c = h["temperature_2m"][i]
        seg.headwind_kmh = headwind_kmh(h["wind_speed_10m"][i], h["wind_direction_10m"][i], bearing_deg(a, b))
        seg.surface = surface_from(h["precipitation"][i] or 0.0, h["snowfall"][i] or 0.0)
        km += seg.length_km
        minutes += seg.length_km / max(seg.speed_limit * 0.9, 20) * 60
    return []
