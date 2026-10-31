"""Doplní do přibaleného balíku nabíječek (frontend/public/data/osm) stanice CCS2 z Open Charge Map.

Proč: v Itálii (a místy jinde) mají stanice v OSM často nevyplněné zásuvky — Řím 31. 10. 2026: 361 stanic v OSM,
CCS jen u 6. OCM má typ konektoru a výkon. Aplikace bez klíče OCM (např. nový iPad) tak má i tyto stanice.

Klíč OCM_API_KEY se čte z ~/.config/voyah-route-planner/.env jen při sestavení — do balíku se nezapisuje.
Licence: OCM CC BY 4.0 (poskytovatelé bez otevřené licence se vynechávají v parse_poi).
Záznamy se ukládají do klíče "ocm" v souboru dlaždice; aplikace je slučuje s OSM (merge, do 150 m).

Spuštění (po build_charger_tiles.py; bez argumentů = všechny dlaždice v indexu):
    python tools/build_ocm_tiles.py
    python tools/build_ocm_tiles.py 36 6 48 19      # jen oblast (jih, západ, sever, východ)
"""
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vrp_data.config import secret  # noqa: E402
from vrp_data.http import SourceError, request_json  # noqa: E402
from vrp_data.ocm import CCS2_ID, OCM_URL, parse_poi  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "data" / "osm"
TTL_S = 7 * 24 * 3600
LICENSE = "© OpenStreetMap contributors, ODbL 1.0; Open Charge Map, CC BY 4.0"


def fetch_tile(key: str, la: int, lo: int):
    params = {"output": "json", "boundingbox": f"({la},{lo}),({la + 1},{lo + 1})", "connectiontypeid": CCS2_ID,
              "maxresults": 5000, "compact": "false", "verbose": "false"}
    data = request_json(OCM_URL, params=params, headers={"X-API-Key": key}, timeout=60,
                        cache_kind="ocm_bundle", ttl_s=TTL_S)
    out = []
    for p in data:
        r = parse_poi(p)
        if r is None or not (la <= r.lat < la + 1 and lo <= r.lon < lo + 1):
            continue
        d = asdict(r)
        out.append({"id": d["source_id"], "lat": round(d["lat"], 6), "lon": round(d["lon"], 6), "name": d["name"],
                    "operator": d["operator"], "kw": d["max_kw"] if d["power_known"] else None,
                    "points": d["points"], "access": d["access"], "operational": d["operational"],
                    "updated": d["updated"], "address": d["address"],
                    "notes": [n for n in d["notes"] if n.startswith("cena")]})
    return out


def main() -> None:
    key = secret("OCM_API_KEY")
    if not key:
        sys.exit("Chybí OCM_API_KEY v ~/.config/voyah-route-planner/.env")
    idx_path = OUT / "index.json"
    idx = json.loads(idx_path.read_text())
    covered = idx["covered"]
    if len(sys.argv) == 5:
        s, w, n, e = (int(x) for x in sys.argv[1:5])
        covered = [c for c in covered if s <= int(c.split("_")[0]) < n and w <= int(c.split("_")[1]) < e]
    failed, total = [], 0
    for i, c in enumerate(covered, 1):
        la, lo = (int(x) for x in c.split("_"))
        try:
            recs = fetch_tile(key, la, lo)
        except SourceError as err:
            failed.append(c)
            print(f"[{i}/{len(covered)}] {c}: NEPODAŘILO SE ({err})", flush=True)
            time.sleep(2)
            continue
        f = OUT / f"{c}.json"
        doc = json.loads(f.read_text()) if f.exists() else {"elements": []}
        if recs:
            doc["ocm"] = recs
        else:
            doc.pop("ocm", None)
        if doc.get("elements") or doc.get("ocm"):
            f.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        elif f.exists():
            f.unlink()
        total += len(recs)
        print(f"[{i}/{len(covered)}] {c}: {len(recs)}", flush=True)
        time.sleep(0.3)
    idx["tiles"] = sorted(p.stem for p in OUT.glob("*_*.json"))
    idx["license"] = LICENSE
    idx_path.write_text(json.dumps(idx), encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.glob("*.json"))
    print(f"Hotovo: {total} stanic OCM v {len(covered) - len(failed)} dlaždicích, selhalo {len(failed)} {failed}, "
          f"balík {size / 1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
