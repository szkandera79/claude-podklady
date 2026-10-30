"""Výpočet trasy → `vrp.models.Route` (úseky ≤ 1 km se třídou silnice, limitem a převýšením) + geometrie.

Zdroje:
- openrouteservice (hlavní): převýšení, `extra_info` waycategory (bit 1 = dálnice/silnice pro motorová vozidla)
  a waytype (1 státní silnice, 2 silnice, 3 ulice).
- OSRM (záloha pro vývoj, veřejný demo server): třída dálnice z `intersections.classes`, ostatní třídy z průměrné
  rychlosti routeru; převýšení doplní Open-Meteo Elevation API.
Rychlostní limit: výchozí limit dle třídy a země; mimo dálnice navíc strop 1,1 × rychlost routeru (obce, zatáčky).
"""
from __future__ import annotations

import re
import time

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from vrp.models import RoadClass, Route, Segment

from .config import CACHE_DIR, secret
from .geo import haversine_km
from .http import SourceError, request_json

ORS_URLS = ["https://api.openrouteservice.org/v2/directions/driving-car/geojson"]
OSRM_URL = "https://router.project-osrm.org/route/v1/driving/"
ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
TTL_S = 6 * 3600
CHUNK_KM = 1.0

# dálniční limity podle země — ❓ ověřit, že ORS countryinfo vrací ISO 3166-1 numerický kód (jinak platí 130)
MOTORWAY_LIMIT = {203: 130, 703: 130, 40: 130, 276: 130, 616: 140, 348: 130, 191: 130, 705: 130, 380: 130}
# OSRM demo nevrací třídy silnic → dálnice podle označení (D1, A4, S8, M1, E…) nebo rychlosti routeru
MOTORWAY_REF = re.compile(r"^\s*(D|A|S|M|AP|BAB)\s?\d", re.I)
DEFAULT_LIMIT = {RoadClass.MOTORWAY: 130, RoadClass.EXPRESSWAY: 110, RoadClass.PRIMARY: 90,
                 RoadClass.DISTRICT: 90, RoadClass.CITY: 50}


@dataclass
class RouteResult:
    route: Route
    points: List[Tuple[float, float]]           # (lat, lon) plná geometrie
    source: str
    router_minutes: float
    notes: List[str] = field(default_factory=list)


@dataclass
class _Pt:
    lat: float
    lon: float
    ele: Optional[float]
    cls: RoadClass
    speed: float          # rychlost routeru na úseku od tohoto bodu dál (km/h)
    country: Optional[int] = None


def _limit(cls: RoadClass, country: Optional[int], router_speed: float) -> float:
    lim = MOTORWAY_LIMIT.get(country, 130) if cls == RoadClass.MOTORWAY else DEFAULT_LIMIT[cls]
    if cls != RoadClass.MOTORWAY and router_speed > 0:
        lim = min(lim, max(30.0, router_speed * 1.1))
    return lim


def build_segments(pts: Sequence[_Pt]) -> List[Segment]:
    """Spojí body do úseků ≤ 1 km se stejnou třídou silnice."""
    segs: List[Segment] = []
    i = 0
    n = len(pts)
    while i < n - 1:
        start = i
        dist = 0.0
        t_h = 0.0
        while i < n - 1 and pts[i].cls == pts[start].cls and (dist < CHUNK_KM or i == start):
            d = haversine_km((pts[i].lat, pts[i].lon), (pts[i + 1].lat, pts[i + 1].lon))
            dist += d
            t_h += d / max(pts[i].speed, 5.0)
            i += 1
        if dist <= 0:
            continue
        e0, e1 = pts[start].ele, pts[i].ele
        dz = (e1 - e0) if (e0 is not None and e1 is not None) else 0.0
        speed = dist / t_h if t_h > 0 else 50.0
        segs.append(Segment(dist, pts[start].cls, _limit(pts[start].cls, pts[start].country, speed), dz))
    return segs


def _range_lookup(values: Sequence[Sequence[int]], n: int, default: int) -> List[int]:
    out = [default] * n
    for a, b, v in values:
        for k in range(a, min(b + 1, n)):
            out[k] = v
    return out


def parse_ors(data: dict) -> RouteResult:
    f = data["features"][0]
    coords = f["geometry"]["coordinates"]
    props = f["properties"]
    n = len(coords)
    extras = props.get("extras", {})
    wcat = _range_lookup(extras.get("waycategory", {}).get("values", []), n, 0)
    wtype = _range_lookup(extras.get("waytype", {}).get("values", []), n, 2)
    country = _range_lookup(extras.get("countryinfo", {}).get("values", []), n, 203)
    speed = [50.0] * n
    for seg in props.get("segments", []):
        for st in seg.get("steps", []):
            a, b = st["way_points"]
            v = st["distance"] / 1000 / (st["duration"] / 3600) if st.get("duration") else 50.0
            for k in range(a, min(b + 1, n)):
                speed[k] = v
    pts = []
    for k, c in enumerate(coords):
        if wcat[k] & 1:
            cls = RoadClass.MOTORWAY
        elif wtype[k] == 1:
            cls = RoadClass.PRIMARY
        elif wtype[k] == 3:
            cls = RoadClass.CITY
        else:
            cls = RoadClass.DISTRICT
        pts.append(_Pt(c[1], c[0], c[2] if len(c) > 2 else None, cls, speed[k], country[k]))
    return RouteResult(Route(build_segments(pts)), [(p.lat, p.lon) for p in pts], "openrouteservice",
                       props["summary"]["duration"] / 60)


ORS_DOWN_MARK = CACHE_DIR / "ors_down"
ORS_DOWN_S = 15 * 60


def route_ors(waypoints: Sequence[Tuple[float, float]]) -> RouteResult:
    key = secret("ORS_API_KEY")
    if not key:
        raise SourceError("openrouteservice: chybí ORS_API_KEY")
    if ORS_DOWN_MARK.exists() and time.time() - ORS_DOWN_MARK.stat().st_mtime < ORS_DOWN_S:
        raise SourceError("openrouteservice: nedávno nedostupné, zkusí se znovu za 15 min")
    body = {"coordinates": [[lon, lat] for lat, lon in waypoints], "elevation": True,
            "extra_info": ["waycategory", "waytype", "countryinfo"], "instructions": True}
    last = None
    for url in ORS_URLS:
        try:
            data = request_json(url, body=body, headers={"Authorization": key,
                                                         "Accept": "application/geo+json, application/json, */*"}, timeout=20,
                                cache_kind="ors", ttl_s=TTL_S)
            return parse_ors(data)
        except SourceError as e:
            last = e
    ORS_DOWN_MARK.parent.mkdir(parents=True, exist_ok=True)
    ORS_DOWN_MARK.touch()
    raise last


def parse_osrm(data: dict) -> Tuple[RouteResult, List[_Pt]]:
    pts: List[_Pt] = []
    for leg in data["routes"][0]["legs"]:
        for st in leg["steps"]:
            cl = set()
            for it in st.get("intersections", []):
                cl.update(it.get("classes", []))
            v = st["distance"] / 1000 / (st["duration"] / 3600) if st.get("duration") else 50.0
            if "motorway" in cl or MOTORWAY_REF.match(st.get("ref") or "") or v >= 95:
                cls = RoadClass.MOTORWAY
            elif v >= 70:
                cls = RoadClass.PRIMARY
            elif v >= 45:
                cls = RoadClass.DISTRICT
            else:
                cls = RoadClass.CITY
            for lon, lat in st["geometry"]["coordinates"]:
                if pts and abs(pts[-1].lat - lat) < 1e-9 and abs(pts[-1].lon - lon) < 1e-9:
                    continue
                pts.append(_Pt(lat, lon, None, cls, v))
    return RouteResult(Route([]), [(p.lat, p.lon) for p in pts], "OSRM (záloha)",
                       data["routes"][0]["duration"] / 60,
                       ["Trasa z OSRM (záloha): třídy silnic odhadnuty z označení silnic a rychlosti routeru."]), pts


def add_elevation(pts: List[_Pt]) -> None:
    """Doplní nadmořskou výšku z Open-Meteo (max. 100 bodů na dotaz) — vzorkuje cca po 1 km a interpoluje."""
    idx = [0]
    acc = 0.0
    for k in range(1, len(pts)):
        acc += haversine_km((pts[k - 1].lat, pts[k - 1].lon), (pts[k].lat, pts[k].lon))
        if acc >= 1.0 or k == len(pts) - 1:
            idx.append(k)
            acc = 0.0
    elev: Dict[int, float] = {}
    for c in range(0, len(idx), 100):
        chunk = idx[c:c + 100]
        data = request_json(ELEVATION_URL, params={
            "latitude": ",".join(f"{pts[k].lat:.5f}" for k in chunk),
            "longitude": ",".join(f"{pts[k].lon:.5f}" for k in chunk)}, timeout=30,
            cache_kind="elevation", ttl_s=30 * 24 * 3600)
        for k, e in zip(chunk, data.get("elevation", [])):
            elev[k] = e
    keys = sorted(elev)
    for a, b in zip(keys, keys[1:]):
        for k in range(a, b + 1):
            f = (k - a) / (b - a) if b > a else 0
            pts[k].ele = elev[a] + f * (elev[b] - elev[a])


def route_osrm(waypoints: Sequence[Tuple[float, float]]) -> RouteResult:
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in waypoints)
    data = request_json(OSRM_URL + coords, params={"overview": "false", "steps": "true",
                                                   "geometries": "geojson"}, timeout=40,
                        cache_kind="osrm", ttl_s=TTL_S)
    if data.get("code") != "Ok":
        raise SourceError(f"OSRM: {data.get('code')}")
    res, pts = parse_osrm(data)
    try:
        add_elevation(pts)
    except SourceError as e:
        res.notes.append(f"Převýšení nedostupné ({e}) — počítáno po rovině.")
    res.route = Route(build_segments(pts))
    return res


def plan_geometry(waypoints: Sequence[Tuple[float, float]]) -> RouteResult:
    """openrouteservice, při výpadku záloha OSRM (s upozorněním)."""
    try:
        return route_ors(waypoints)
    except SourceError as e:
        res = route_osrm(waypoints)
        res.notes.insert(0, f"openrouteservice nedostupné ({e}) — použita záloha.")
        return res
