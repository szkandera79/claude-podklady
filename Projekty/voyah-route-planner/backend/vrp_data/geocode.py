"""Geokódování adres přes Photon (komoot, data OSM, bez klíče, férové užití). Souřadnice „49.83, 18.26" se berou přímo."""
from __future__ import annotations

import re
from typing import Tuple

from .http import SourceError, request_json

PHOTON_URL = "https://photon.komoot.io/api/"


def geocode(text: str) -> Tuple[float, float, str]:
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$", text)
    if m:
        return float(m.group(1)), float(m.group(2)), text.strip()
    data = request_json(PHOTON_URL, params={"q": text, "limit": 1, "lang": "default",
                                            "lat": 49.8, "lon": 15.5}, timeout=20,
                        cache_kind="geocode", ttl_s=30 * 24 * 3600)
    feats = data.get("features") or []
    if not feats:
        raise SourceError(f"Adresu „{text}“ se nepodařilo najít")
    f = feats[0]
    lon, lat = f["geometry"]["coordinates"]
    p = f.get("properties", {})
    label = ", ".join(x for x in (p.get("name"), p.get("city") or p.get("county"), p.get("country")) if x)
    return lat, lon, label or text
