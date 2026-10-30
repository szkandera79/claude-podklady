/** Nabíječky CCS2 z OpenStreetMap (Overpass), dlaždice 1° s cache 7 dní, záložní servery (přepis vrp_data/osm.py).
 *  Licence ODbL — v aplikaci uvádět „© OpenStreetMap contributors". */
import { normalizeOperator } from "./operators";
import { SourceError, requestJson } from "./http";

export const OVERPASS_URLS = ["https://overpass-api.de/api/interpreter",
                              "https://maps.mail.ru/osm/tools/overpass/api/interpreter"];
const TILE_TTL_S = 7 * 86400;
export const UNKNOWN_POWER_KW = 50;

export interface ChargerRecord {
  source: string; sourceId: string; lat: number; lon: number; name: string; operator: string;
  maxKw: number; powerKnown: boolean; points: number; access: "public" | "customers" | "private" | "unknown";
  operational: boolean | null; updated: string | null; address: string; notes: string[];
}

export function parseKw(v?: string): number | null {
  if (!v) return null;
  let best: number | null = null;
  for (const m of v.toLowerCase().matchAll(/(\d+(?:[.,]\d+)?)\s*(kw|kva|w)?/g)) {
    let x = parseFloat(m[1].replace(",", "."));
    if (m[2] === "w" || (!m[2] && x > 1000)) x /= 1000;
    best = best === null ? x : Math.max(best, x);
  }
  return best;
}

const int = (v: string | undefined, d = 1) => { const n = parseInt(String(v ?? "").split(";")[0], 10); return n > 0 ? n : d; };

export function parseElement(el: any): ChargerRecord | null {
  const t: Record<string, string> = el.tags || {};
  if (!("socket:type2_combo" in t) || ["0", "no"].includes(t["socket:type2_combo"])) return null;
  const lat = el.lat ?? el.center?.lat;
  const lon = el.lon ?? el.center?.lon;
  if (lat == null || lon == null) return null;
  const kw = parseKw(t["socket:type2_combo:output"]) ?? parseKw(t["charging_station:output"]);
  let access: ChargerRecord["access"] = "unknown";
  const a = t.access;
  if (["yes", "public", "permissive"].includes(a)) access = "public";
  else if (["customers", "destination"].includes(a)) access = "customers";
  else if (["private", "no", "permit"].includes(a)) access = "private";
  const opRaw = t.operator || t.network || t.brand || "";
  const op = normalizeOperator(opRaw);
  const notes: string[] = [];
  if (kw === null) notes.push(`výkon v datech chybí, počítáno konzervativně s ${UNKNOWN_POWER_KW} kW`);
  if (access === "customers") notes.push("jen pro zákazníky — ověřte otevírací dobu" + (t.opening_hours ? ` (${t.opening_hours})` : ""));
  if (op === "Tesla") notes.push("Tesla Supercharger — ověřte v aplikaci Tesla, že je stanice otevřená i pro jiné vozy");
  const addr = [t["addr:street"], t["addr:housenumber"], t["addr:city"]].filter(Boolean).join(" ");
  const name = t.name || (opRaw ? `${op} ${t["addr:city"] || ""}`.trim() : "Nabíjecí stanice");
  return { source: "OSM", sourceId: `${el.type || "node"}/${el.id}`, lat: +lat, lon: +lon, name, operator: op,
           maxKw: kw ?? UNKNOWN_POWER_KW, powerKnown: kw !== null, points: int(t["socket:type2_combo"], int(t.capacity)),
           access, operational: t["disused:amenity"] || ["closed", "broken"].includes(t.operational_status) ? false : null,
           updated: null, address: addr, notes };
}

export function tilesFor(points: [number, number][], margin = 0.1): [number, number][] {
  const s = new Set<string>();
  for (const [lat, lon] of points) for (const dl of [-margin, 0, margin]) for (const dn of [-margin, 0, margin])
    s.add(`${Math.floor(lat + dl)},${Math.floor(lon + dn)}`);
  return [...s].sort().map((k) => k.split(",").map(Number) as [number, number]);
}

interface BundleIndex { generated: string; tiles: string[]; bbox: [number, number, number, number]; }
let bundleIndex: Promise<BundleIndex | null> | null = null;

/** Index přibaleného balíku (public/data/osm, generuje backend/tools/build_charger_tiles.py). */
function loadIndex(): Promise<BundleIndex | null> {
  if (!bundleIndex) {
    bundleIndex = fetch("/data/osm/index.json").then((r) => (r.ok ? r.json() : null)).catch(() => null);
  }
  return bundleIndex;
}

/** Dlaždice z přibaleného balíku; null = mimo pokrytí balíku (→ živý Overpass). */
async function fromBundle(lat0: number, lon0: number): Promise<{ els: any[]; generated: string } | null> {
  const idx = await loadIndex();
  if (!idx) return null;
  const [s, w, n, e] = idx.bbox;
  if (lat0 < s || lat0 >= n || lon0 < w || lon0 >= e) return null;
  const key = `${lat0}_${lon0}`;
  if (!idx.tiles.includes(key)) return { els: [], generated: idx.generated };       // pokryto, bez stanic
  const r = await fetch(`/data/osm/${key}.json`).catch(() => null);
  if (!r?.ok) return null;
  return { els: (await r.json()).elements || [], generated: idx.generated };
}

async function fetchBox(s: number, w: number, n: number, e: number, deadline: number): Promise<any[]> {
  const q = `[out:json][timeout:60];nwr["amenity"="charging_station"]["socket:type2_combo"](${s},${w},${n},${e});out center tags;`;
  let last: Error = new SourceError("Overpass nedostupný");
  for (const url of OVERPASS_URLS) {
    const left = (deadline - Date.now()) / 1000;
    if (left < 5) throw new SourceError("Overpass: vypršel časový limit");
    try {
      const d = await requestJson(url, { body: { data: q }, form: true, timeoutS: Math.min(45, left), cacheKind: "osm", ttlS: TILE_TTL_S });
      return d.elements || [];
    } catch (err) { last = err as Error; }
  }
  throw last;
}

/** Dlaždice 1°: nejdřív přibalený balík, jinak živý Overpass (při selhání 4 dlaždice po 0,5°), vše do `deadline`. */
export async function fetchTile(lat0: number, lon0: number, deadline = Date.now() + 90000): Promise<ChargerRecord[]> {
  const b = await fromBundle(lat0, lon0);
  if (b) {
    return b.els.map(parseElement).filter((r): r is ChargerRecord => r !== null)
      .map((r) => ({ ...r, source: "OSM", updated: b.generated }));
  }
  let els: any[];
  try { els = await fetchBox(lat0, lon0, lat0 + 1, lon0 + 1, deadline); }
  catch {
    els = [];
    for (const dl of [0, 0.5]) for (const dn of [0, 0.5]) els.push(...await fetchBox(lat0 + dl, lon0 + dn, lat0 + dl + 0.5, lon0 + dn + 0.5, deadline));
  }
  return els.map(parseElement).filter((r): r is ChargerRecord => r !== null);
}
