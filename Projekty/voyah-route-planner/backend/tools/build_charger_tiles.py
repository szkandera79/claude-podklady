"""Předpřipravený balík nabíječek CCS2 z OpenStreetMap pro PWA (frontend/public/data/osm/<lat>_<lon>.json).

Aplikace v telefonu pak nemusí při každém výpočtu volat přetížený veřejný Overpass; ten zůstává jen jako záloha
pro oblasti mimo balík. Licence ODbL: data © OpenStreetMap contributors, odvozená databáze pod ODbL.

Spuštění (obnovit cca 1× měsíčně, pak znovu sestavit a nahrát aplikaci):
    python tools/build_charger_tiles.py
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vrp_data.http import SourceError, request_json  # noqa: E402

COUNTRIES = ["CZ", "SK", "AT", "PL", "HU", "SI", "HR", "DE"]
MIRRORS = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]
KEEP = ["socket:type2_combo", "socket:type2_combo:output", "charging_station:output", "capacity", "access", "operator",
        "network", "brand", "name", "opening_hours", "addr:street", "addr:housenumber", "addr:city",
        "disused:amenity", "operational_status"]
OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "data" / "osm"


def fetch_country(cc: str) -> list:
    q = (f'[out:json][timeout:300];area["ISO3166-1"="{cc}"][admin_level=2]->.a;'
         f'nwr["amenity"="charging_station"]["socket:type2_combo"](area.a);out center tags;')
    last = None
    for attempt in range(2):
        for url in MIRRORS:
            try:
                return request_json(url, body={"data": q}, form=True, timeout=320).get("elements", [])
            except SourceError as e:
                last = e
                print(f"  {cc}: {e}, zkouším další server…", flush=True)
                time.sleep(5)
    raise last


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tiles: dict = {}
    covered = set()
    stats = {}
    for cc in COUNTRIES:
        print(f"{cc}…", flush=True)
        try:
            els = fetch_country(cc)
        except SourceError as e:
            print(f"  {cc} VYNECHÁNO ({e})")
            continue
        n = 0
        for el in els:
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if lat is None:
                continue
            key = f"{int(lat // 1)}_{int(lon // 1)}"
            covered.add(key)
            t = {k: v for k, v in el.get("tags", {}).items() if k in KEEP}
            tiles.setdefault(key, {})[f"{el['type']}/{el['id']}"] = {
                "type": el["type"], "id": el["id"], "lat": round(lat, 6), "lon": round(lon, 6), "tags": t}
            n += 1
        stats[cc] = n
        print(f"  {n} stanic")
    # pokryté dlaždice = všechny 1° čtverce v obálce zpracovaných zemí, kde máme data (prázdné nemají soubor)
    for old in OUT.glob("*.json"):
        old.unlink()
    for key, els in tiles.items():
        (OUT / f"{key}.json").write_text(json.dumps({"elements": list(els.values())}, ensure_ascii=False,
                                                    separators=(",", ":")), encoding="utf-8")
    lats = [int(k.split("_")[0]) for k in tiles] or [0]
    lons = [int(k.split("_")[1]) for k in tiles] or [0]
    index = {"generated": date.today().isoformat(), "countries": stats, "tiles": sorted(tiles),
             "bbox": [min(lats), min(lons), max(lats) + 1, max(lons) + 1],
             "license": "© OpenStreetMap contributors, ODbL 1.0"}
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    size = sum(f.stat().st_size for f in OUT.glob("*.json"))
    print(f"Hotovo: {sum(stats.values())} stanic, {len(tiles)} dlaždic, {size / 1e6:.1f} MB → {OUT}")


if __name__ == "__main__":
    main()
