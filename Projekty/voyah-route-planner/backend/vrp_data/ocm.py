"""Nabíječky z Open Charge Map. Licence dat CC BY 4.0 (u každé stanice se kontroluje licence poskytovatele dat).

V ČR má OCM zhruba čtvrtinu stanic oproti OSM (ověřeno 30. 10. 2026: 232 vs. 901 s CCS2), proto slouží
jako doplňkový zdroj: stav (mimo provoz), datum ověření, cena v poznámce, stanice chybějící v OSM.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from .config import secret
from .geo import encode_polyline
from .http import SourceError, request_json
from .operators import normalize_operator
from .osm import UNKNOWN_POWER_KW, ChargerRecord

OCM_URL = "https://api.openchargemap.io/v3/poi/"
CCS2_ID = 33
TTL_S = 24 * 3600
ACCESS_BY_USAGE = {1: "public", 4: "public", 5: "public", 7: "public",
                   2: "private", 3: "private", 6: "customers"}


def parse_poi(p: dict) -> Optional[ChargerRecord]:
    prov = p.get("DataProvider") or {}
    if prov and prov.get("IsOpenDataLicensed") is False:
        return None                                   # licence poskytovatele neumožňuje použití
    conns = [c for c in (p.get("Connections") or []) if c.get("ConnectionTypeID") == CCS2_ID]
    if not conns:
        return None
    a = p.get("AddressInfo") or {}
    if a.get("Latitude") is None:
        return None
    kws = [c.get("PowerKW") for c in conns if c.get("PowerKW")]
    kw = max(kws) if kws else None
    points = sum((c.get("Quantity") or 1) for c in conns)
    usage = p.get("UsageTypeID") or (p.get("UsageType") or {}).get("ID")
    status = p.get("StatusType") or {}
    op = normalize_operator((p.get("OperatorInfo") or {}).get("Title") or "")
    notes = []
    if kw is None:
        notes.append(f"výkon v datech chybí, počítáno konzervativně s {UNKNOWN_POWER_KW:.0f} kW")
    if p.get("UsageCost"):
        cost = " ".join(str(p["UsageCost"]).split())
        notes.append(f"cena dle OCM: {cost[:100]}{'…' if len(cost) > 100 else ''}")
    addr = ", ".join(x for x in (a.get("AddressLine1"), a.get("Town")) if x)
    return ChargerRecord(
        "OCM", str(p.get("ID")), float(a["Latitude"]), float(a["Longitude"]),
        a.get("Title") or "Nabíjecí stanice", op, kw if kw is not None else UNKNOWN_POWER_KW, kw is not None,
        max(1, points), ACCESS_BY_USAGE.get(usage, "unknown"),
        operational=status.get("IsOperational") if status else None,
        updated=(p.get("DateLastVerified") or p.get("DateLastStatusUpdate") or "")[:10] or None,
        address=addr, notes=notes,
    )


def fetch_along(points: Sequence[Tuple[float, float]], corridor_km: float) -> List[ChargerRecord]:
    key = secret("OCM_API_KEY")
    if not key:
        raise SourceError("Open Charge Map: chybí OCM_API_KEY")
    params = {"output": "json", "polyline": encode_polyline(points), "distance": corridor_km,
              "distanceunit": "km", "connectiontypeid": CCS2_ID, "maxresults": 5000,
              "compact": "false", "verbose": "false"}
    data = request_json(OCM_URL, params=params, headers={"X-API-Key": key}, timeout=60,
                        cache_kind="ocm", ttl_s=TTL_S)
    return [r for r in (parse_poi(p) for p in data) if r is not None]
