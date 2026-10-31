/** OSM (hlavní) + OCM (doplněk) → sloučení → průmět na trasu → Station (přepis vrp_data/chargers.py).
 *  Zajížďka ≈ 1,4 × vzdušná vzdálenost + 0,3 km, 40 km/h + 1 min (odhad). */
import type { Station } from "../core/models";
import { Polyline, simplifyByDistance, type LatLon } from "./geo";
import { SourceError } from "./http";
import { fetchAlong } from "./ocm";
import { fetchTile, merge, tilesFor, type ChargerRecord } from "./osm";

export { merge } from "./osm";

export function toStations(recs: ChargerRecord[], line: Polyline, corridorKm: number): Station[] {
  const out: Station[] = [];
  for (const r of recs) {
    if (r.access === "private") continue;
    const [km, off] = line.project([r.lat, r.lon]);
    if (off > corridorKm) continue;
    const detKm = off > 0.05 ? off * 1.4 + 0.3 : 0;
    out.push({ id: `${r.source}:${r.sourceId}`, name: r.name, operator: r.operator, routeKm: km, maxKw: r.maxKw,
               detourKm: detKm, detourMin: detKm ? (detKm / 40) * 60 + 1 : 0, points: r.points, connectors: ["CCS2"],
               accessOk: true, sharedPower: false, dataSource: r.source, dataUpdated: r.updated, isLiveStatus: false,
               available: r.operational === false ? false : null, lat: r.lat, lon: r.lon, address: r.address,
               notes: [...r.notes] });
  }
  return out;
}

export async function stationsAlong(points: LatLon[], corridorKm: number, ocmKey?: string,
                                    progress?: (msg: string) => void): Promise<{ stations: Station[]; issues: string[] }> {
  const line = Polyline.from(simplifyByDistance(points, 0.2));
  const issues: string[] = [];
  const osm = new Map<string, ChargerRecord>();
  const tiles = tilesFor(simplifyByDistance(points, 5));
  let done = 0;
  const deadline = Date.now() + 90000;     // celkový limit na živý Overpass
  const queue = [...tiles];
  const worker = async () => {          // max. 2 souběžné dotazy — šetrně k veřejnému Overpass serveru
    for (let t = queue.shift(); t; t = queue.shift()) {
      const [la, lo] = t;
      try { for (const r of await fetchTile(la, lo, deadline)) osm.set(r.sourceId, r); }
      catch (e) { issues.push(`OpenStreetMap nedostupné (${(e as Error).message}) — chybí stanice v oblasti ${la}°N ${lo}°E`); }
      progress?.(`Nabíječky: ${++done}/${tiles.length} oblastí`);
    }
  };
  await Promise.all([worker(), worker()]);
  let ocm: ChargerRecord[] = [];
  try { ocm = await fetchAlong(simplifyByDistance(points, 2), corridorKm, ocmKey); }
  catch (e) { if (!(e instanceof SourceError && e.message.includes("klíč"))) issues.push(`Open Charge Map nedostupné (${(e as Error).message})`); }
  return { stations: toStations(merge([...osm.values()], ocm), line, corridorKm), issues };
}
