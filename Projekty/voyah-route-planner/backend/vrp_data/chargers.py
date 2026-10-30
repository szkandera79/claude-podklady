"""Kandidátní nabíječky podél trasy: OSM (hlavní) + OCM (doplněk) → sloučení → průmět na trasu → `Station`.

Zajížďka se zatím odhaduje z kolmé vzdálenosti: silniční vzdálenost ≈ 1,4 × vzdušná + 0,3 km, 40 km/h + 1 min.
(Upřesnění maticí vzdáleností routeru je plánované.)
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

from vrp.models import Station

from .geo import Polyline, haversine_km, simplify_by_distance
from .http import SourceError
from .osm import ChargerRecord, fetch_tile, tiles_for
from . import ocm

MERGE_RADIUS_KM = 0.15
DETOUR_ROAD_FACTOR = 1.4
DETOUR_ACCESS_KM = 0.3
DETOUR_SPEED_KMH = 40.0


def merge(osm: Sequence[ChargerRecord], ocm_recs: Sequence[ChargerRecord]) -> List[ChargerRecord]:
    """Stanice OCM do 150 m od OSM stanice se sloučí (doplní stav, datum, poznámky); ostatní se přidají."""
    out = list(osm)
    for o in ocm_recs:
        match = None
        for s in out:
            if s.source != "OSM":
                continue
            if haversine_km((s.lat, s.lon), (o.lat, o.lon)) <= MERGE_RADIUS_KM and \
                    (s.operator == o.operator or "Neznámý" in (s.operator, o.operator) or not o.operator):
                match = s
                break
        if match is None:
            out.append(o)
            continue
        if not match.power_known and o.power_known:
            match.max_kw, match.power_known = o.max_kw, True
            match.notes = [n for n in match.notes if not n.startswith("výkon v datech chybí")]
        if o.operational is False:
            match.operational = False
        match.updated = o.updated or match.updated
        match.notes += [n for n in o.notes if n.startswith("cena")]
        match.source = "OSM+OCM"
    return out


def to_stations(records: Sequence[ChargerRecord], line: Polyline, corridor_km: float) -> List[Station]:
    out = []
    for r in records:
        if r.access == "private":
            continue
        km, off = line.project((r.lat, r.lon))
        if off > corridor_km:
            continue
        det_km = off * DETOUR_ROAD_FACTOR + DETOUR_ACCESS_KM if off > 0.05 else 0.0
        det_min = det_km / DETOUR_SPEED_KMH * 60 + (1.0 if det_km else 0.0)
        out.append(Station(
            id=f"{r.source}:{r.source_id}", name=r.name, operator=r.operator, route_km=km, max_kw=r.max_kw,
            detour_km=det_km, detour_min=det_min, points=r.points, connectors=("CCS2",),
            access_ok=True, data_source=r.source, data_updated=r.updated,
            available=False if r.operational is False else None,
            lat=r.lat, lon=r.lon, address=r.address, notes=tuple(r.notes),
        ))
    return out


def stations_along(points: Sequence[Tuple[float, float]], corridor_km: float = 5.0) -> Tuple[List[Station], List[str]]:
    """Vrátí (stanice, upozornění na výpadky zdrojů)."""
    line = Polyline.from_points(simplify_by_distance(points, 0.2))
    issues: List[str] = []
    osm: List[ChargerRecord] = []
    for lat0, lon0 in tiles_for(simplify_by_distance(points, 5.0)):
        try:
            osm += fetch_tile(lat0, lon0)
        except SourceError as e:
            issues.append(f"OpenStreetMap nedostupné ({e}) — chybí stanice v oblasti {lat0}°N {lon0}°E")
    try:
        ocm_recs = ocm.fetch_along(simplify_by_distance(points, 2.0), corridor_km)
    except SourceError as e:
        ocm_recs = []
        issues.append(f"Open Charge Map nedostupné ({e})")
    uniq = {(r.source, r.source_id): r for r in osm}
    return to_stations(merge(list(uniq.values()), ocm_recs), line, corridor_km), issues
