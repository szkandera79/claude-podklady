"""Nabíječky z OpenStreetMap (Overpass API). Licence ODbL — v aplikaci uvádět „© OpenStreetMap contributors".

Stahuje se po dlaždicích 1° × 1° s cache 7 dní (šetrné k veřejnému Overpass serveru).
Hledají se jen stanice se zásuvkou CCS2 (`socket:type2_combo`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

import time

from .http import SourceError, request_json
from .operators import normalize_operator

OVERPASS_URLS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter",
                 "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]
TILE_TTL_S = 7 * 24 * 3600
UNKNOWN_POWER_KW = 50.0   # konzervativní předpoklad, pokud zdroj výkon neuvádí


@dataclass
class ChargerRecord:
    source: str
    source_id: str
    lat: float
    lon: float
    name: str
    operator: str
    max_kw: float
    power_known: bool
    points: int
    access: str                   # public / customers / private / unknown
    operational: Optional[bool] = None
    updated: Optional[str] = None
    address: str = ""
    notes: List[str] = field(default_factory=list)


def parse_kw(value: Optional[str]) -> Optional[float]:
    """'150 kW', '50 kW;150 kW', '150', '22 kVA' → největší hodnota v kW."""
    if not value:
        return None
    best = None
    for num, unit in re.findall(r"(\d+(?:[.,]\d+)?)\s*(kw|kva|w)?", value.lower()):
        v = float(num.replace(",", "."))
        if unit == "w" or (not unit and v > 1000):
            v /= 1000.0
        best = v if best is None else max(best, v)
    return best


def _int(v: Optional[str], default: int = 1) -> int:
    try:
        return max(1, int(str(v).split(";")[0]))
    except (TypeError, ValueError):
        return default


def parse_element(el: dict) -> Optional[ChargerRecord]:
    t = el.get("tags", {})
    if "socket:type2_combo" not in t or t.get("socket:type2_combo") in ("0", "no"):
        return None
    lat = el.get("lat") or (el.get("center") or {}).get("lat")
    lon = el.get("lon") or (el.get("center") or {}).get("lon")
    if lat is None or lon is None:
        return None
    kw = parse_kw(t.get("socket:type2_combo:output")) or parse_kw(t.get("charging_station:output"))
    access = t.get("access", "unknown")
    if access in ("yes", "public", "permissive"):
        access = "public"
    elif access in ("customers", "destination"):
        access = "customers"
    elif access in ("private", "no", "permit"):
        access = "private"
    op_raw = t.get("operator") or t.get("network") or t.get("brand") or ""
    op = normalize_operator(op_raw)
    notes: List[str] = []
    if kw is None:
        notes.append(f"výkon v datech chybí, počítáno konzervativně s {UNKNOWN_POWER_KW:.0f} kW")
    if access == "customers":
        notes.append("jen pro zákazníky — ověřte otevírací dobu" +
                     (f" ({t['opening_hours']})" if t.get("opening_hours") else ""))
    if op == "Tesla":
        notes.append("Tesla Supercharger — ověřte v aplikaci Tesla, že je stanice otevřená i pro jiné vozy")
    addr = " ".join(x for x in (t.get("addr:street"), t.get("addr:housenumber"), t.get("addr:city")) if x)
    name = t.get("name") or (f"{op} {t.get('addr:city', '')}".strip() if op_raw else "Nabíjecí stanice")
    return ChargerRecord(
        "OSM", f"{el.get('type', 'node')}/{el.get('id')}", float(lat), float(lon), name, op,
        kw if kw is not None else UNKNOWN_POWER_KW, kw is not None,
        _int(t.get("socket:type2_combo"), _int(t.get("capacity"))), access,
        operational=False if t.get("disused:amenity") or t.get("operational_status") in ("closed", "broken") else None,
        updated=None, address=addr, notes=notes,
    )


def tiles_for(points: Iterable[Tuple[float, float]], margin_deg: float = 0.1) -> List[Tuple[int, int]]:
    tiles = set()
    for lat, lon in points:
        for dl in (-margin_deg, 0, margin_deg):
            for dn in (-margin_deg, 0, margin_deg):
                tiles.add((int((lat + dl) // 1), int((lon + dn) // 1)))
    return sorted(tiles)


def _fetch_box(s: float, w: float, n: float, e: float) -> list:
    q = (f'[out:json][timeout:60];nwr["amenity"="charging_station"]["socket:type2_combo"]'
         f'({s},{w},{n},{e});out center tags;')
    last = None
    for attempt, url in enumerate(OVERPASS_URLS):       # veřejné servery bývají přetížené → zrcadla
        try:
            return request_json(url, body={"data": q}, form=True, timeout=90,
                                cache_kind="osm_tiles", ttl_s=TILE_TTL_S).get("elements", [])
        except SourceError as e:
            last = e
            time.sleep(1 + attempt)
    raise last


def fetch_tile(lat0: int, lon0: int) -> List[ChargerRecord]:
    """Dlaždice 1°; při selhání (hustá oblast, přetížený server) se zkusí 4 dlaždice po 0,5°."""
    try:
        elements = _fetch_box(lat0, lon0, lat0 + 1, lon0 + 1)
    except SourceError:
        elements = []
        for dl in (0, 0.5):
            for dn in (0, 0.5):
                elements += _fetch_box(lat0 + dl, lon0 + dn, lat0 + dl + 0.5, lon0 + dn + 0.5)
    return [r for r in (parse_element(el) for el in elements) if r is not None]
