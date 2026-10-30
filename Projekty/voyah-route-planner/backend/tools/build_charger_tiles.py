"""Předpřipravený balík nabíječek CCS2 z OpenStreetMap pro PWA (frontend/public/data/osm/<lat>_<lon>.json).

Aplikace v telefonu pak nemusí při každém výpočtu volat přetížený veřejný Overpass; ten zůstává jen jako záloha
pro oblasti mimo balík. Licence ODbL: data © OpenStreetMap contributors, odvozená databáze pod ODbL.

Stahuje se po dlaždicích 1° × 1° (malé dotazy, cache 7 dní v ~/.cache/voyah-route-planner) → lze přerušit
a znovu spustit, hotové dlaždice se nestahují znovu. Dlaždice, které se nepodaří stáhnout, nejsou v indexu
a aplikace je dotáhne živě.

Spuštění (obnovit cca 1× měsíčně, pak znovu sestavit a nahrát aplikaci):
    python tools/build_charger_tiles.py            # výchozí oblast: střední Evropa + Jadran
    python tools/build_charger_tiles.py 48 12 52 19   # jen ČR (jih, západ, sever, východ)
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vrp_data.http import SourceError, request_json  # noqa: E402

BBOX = (44, 8, 55, 25)          # jih, západ, sever, východ (DE východ, CZ, SK, AT, PL, HU, SI, HR sever)
MIRRORS = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
           "https://overpass.private.coffee/api/interpreter"]
KEEP = ["socket:type2_combo", "socket:type2_combo:output", "charging_station:output", "capacity", "access", "operator",
        "network", "brand", "name", "opening_hours", "addr:street", "addr:housenumber", "addr:city",
        "disused:amenity", "operational_status"]
OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "data" / "osm"
TTL_S = 7 * 24 * 3600


def fetch_box(s, w, n, e):
    q = (f'[out:json][timeout:60];nwr["amenity"="charging_station"]["socket:type2_combo"]'
         f'({s},{w},{n},{e});out center tags;')
    last = None
    for url in MIRRORS:
        try:
            return request_json(url, body={"data": q}, form=True, timeout=75,
                                cache_kind="osm_bundle", ttl_s=TTL_S).get("elements", [])
        except SourceError as err:
            last = err
            time.sleep(2)
    raise last


def fetch_tile(lat0, lon0):
    try:
        return fetch_box(lat0, lon0, lat0 + 1, lon0 + 1)
    except SourceError:
        out = []
        for dl in (0, 0.5):
            for dn in (0, 0.5):
                out += fetch_box(lat0 + dl, lon0 + dn, lat0 + dl + 0.5, lon0 + dn + 0.5)
        return out


def main() -> None:
    s, w, n, e = (int(x) for x in sys.argv[1:5]) if len(sys.argv) == 5 else BBOX
    OUT.mkdir(parents=True, exist_ok=True)
    ok, failed, total = [], [], 0
    todo = [(la, lo) for la in range(s, n) for lo in range(w, e)]
    for i, (la, lo) in enumerate(todo, 1):
        key = f"{la}_{lo}"
        try:
            els = fetch_tile(la, lo)
        except SourceError as err:
            failed.append(key)
            print(f"[{i}/{len(todo)}] {key}: NEPODAŘILO SE ({err})", flush=True)
            continue
        recs = {}
        for el in els:
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if lat is None or not (la <= lat < la + 1 and lo <= lon < lo + 1):
                continue
            recs[f"{el['type']}/{el['id']}"] = {"type": el["type"], "id": el["id"], "lat": round(lat, 6),
                                                "lon": round(lon, 6),
                                                "tags": {k: v for k, v in el.get("tags", {}).items() if k in KEEP}}
        f = OUT / f"{key}.json"
        if recs:
            f.write_text(json.dumps({"elements": list(recs.values())}, ensure_ascii=False, separators=(",", ":")),
                         encoding="utf-8")
        elif f.exists():
            f.unlink()
        ok.append(key)
        total += len(recs)
        print(f"[{i}/{len(todo)}] {key}: {len(recs)}", flush=True)
    # index: pokryté dlaždice (i prázdné) a dlaždice se soubory; spojí se s dříve staženými oblastmi
    idx_path = OUT / "index.json"
    prev = json.loads(idx_path.read_text()) if idx_path.exists() else {"covered": []}
    covered = sorted((set(prev.get("covered", [])) - set(failed)) | set(ok))
    files = sorted(p.stem for p in OUT.glob("*_*.json"))
    idx_path.write_text(json.dumps({"generated": date.today().isoformat(), "covered": covered, "tiles": files,
                                    "license": "© OpenStreetMap contributors, ODbL 1.0"}), encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.glob("*.json"))
    print(f"Hotovo: {total} stanic v {len(ok)} dlaždicích, selhalo {len(failed)} {failed}, balík {size / 1e6:.1f} MB",
          flush=True)


if __name__ == "__main__":
    main()
