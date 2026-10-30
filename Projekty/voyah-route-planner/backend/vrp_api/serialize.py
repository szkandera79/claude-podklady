"""Převod objektů jádra na JSON pro API a zpět (trasa a stanice se ukládají k plánu pro přepočty během cesty)."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Sequence, Tuple

from vrp.models import RoadClass, Route, Segment, Station, Surface
from vrp.optimizer import Plan

from vrp_data.geo import simplify_by_distance


def station_to_dict(s: Station) -> Dict[str, Any]:
    d = asdict(s)
    d["connectors"] = list(s.connectors)
    d["notes"] = list(s.notes)
    return d


def station_from_dict(d: Dict[str, Any]) -> Station:
    d = dict(d)
    d["connectors"] = tuple(d.get("connectors") or ("CCS2",))
    d["notes"] = tuple(d.get("notes") or ())
    return Station(**d)


def route_to_dict(route: Route, points: Sequence[Tuple[float, float]], source: str) -> Dict[str, Any]:
    return {
        "source": source,
        "points": [[round(a, 5), round(b, 5)] for a, b in simplify_by_distance(points, 0.1)],
        "segments": [[round(s.length_km, 4), s.road_class.value, s.speed_limit, round(s.elevation_delta_m, 1),
                      s.temp_c, round(s.headwind_kmh, 1), s.surface.value] for s in route.segments],
    }


def route_from_dict(d: Dict[str, Any]) -> Tuple[Route, List[Tuple[float, float]]]:
    segs = [Segment(L, RoadClass(c), lim, dz, t, w, Surface(sf)) for L, c, lim, dz, t, w, sf in d["segments"]]
    return Route(segs), [(a, b) for a, b in d["points"]]


def station_brief(s: Station) -> Dict[str, Any]:
    return {"id": s.id, "name": s.name, "operator": s.operator, "lat": s.lat, "lon": s.lon, "max_kw": s.max_kw,
            "points": s.points, "address": s.address, "route_km": round(s.route_km, 1),
            "detour_km": round(s.detour_km, 1), "source": s.data_source, "updated": s.data_updated,
            "notes": list(s.notes)}


def plan_to_dict(p: Plan) -> Dict[str, Any]:
    return {
        "feasible": p.feasible, "reason": p.reason, "mode": p.mode.value, "profile": p.profile.value,
        "distance_km": round(p.distance_km, 1), "drive_min": round(p.drive_min, 1),
        "charge_min": round(p.charge_min, 1), "stop_overhead_min": round(p.stop_overhead_min, 1),
        "total_min": round(p.total_min, 1), "cost_czk": round(p.cost_czk), "arrival_soc": p.arrival_soc,
        "trip_energy_kwh": round(p.trip_energy_kwh, 1), "warnings": p.warnings,
        "stops": [{
            "station": station_brief(s.station), "arrive_km": round(s.arrive_km, 1), "arrive_soc": s.arrive_soc,
            "depart_soc": s.depart_soc, "charge_min": round(s.charge_min, 1), "grid_kwh": round(s.grid_kwh, 1),
            "cost_czk": round(s.cost_czk), "avg_kw": round(s.avg_kw, 1), "next_leg_km": round(s.next_leg_km, 1),
            "arrive_min": round(s.arrive_min, 1), "depart_min": round(s.depart_min, 1),
        } for s in p.stops],
    }
