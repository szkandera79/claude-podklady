/** Trasa → Route (úseky ≤ 1 km: třída silnice, limit, převýšení) + geometrie (přepis vrp_data/routing.py).
 *  openrouteservice (hlavní; waycategory bit 1 = dálnice, waytype 1/2/3) → záloha OSRM (třída z označení D1/A4…
 *  a rychlosti routeru, převýšení z Open-Meteo). Limit: dle třídy a země, mimo dálnice ≤ 1,1 × rychlost routeru. */
import type { RoadClass, Route, Segment } from "../core/models";
import { segment } from "../core/models";
import { haversineKm, type LatLon } from "./geo";
import { SourceError, requestJson } from "./http";

const ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car/geojson";
const OSRM_URL = "https://router.project-osrm.org/route/v1/driving/";
const ELEVATION_URL = "https://api.open-meteo.com/v1/elevation";
const TTL_S = 6 * 3600;
const CHUNK_KM = 1;
// ❓ ověřit, že ORS countryinfo vrací ISO 3166-1 numerický kód (jinak platí 130)
const MOTORWAY_LIMIT: Record<number, number> = { 203: 130, 703: 130, 40: 130, 276: 130, 616: 140, 348: 130, 191: 130, 705: 130, 380: 130 };
const DEFAULT_LIMIT: Record<RoadClass, number> = { dalnice: 130, rychlostni: 110, prvni_trida: 90, okresni: 90, mesto: 50 };
const MOTORWAY_REF = /^\s*(D|A|S|M|AP|BAB)\s?\d/i;
const ORS_DOWN_KEY = "vrp_ors_down";

export interface RouteResult { route: Route; points: LatLon[]; source: string; routerMinutes: number; notes: string[]; }
interface Pt { lat: number; lon: number; ele: number | null; cls: RoadClass; speed: number; country?: number; }

function limit(cls: RoadClass, country: number | undefined, routerSpeed: number): number {
  let l = cls === "dalnice" ? MOTORWAY_LIMIT[country ?? 203] ?? 130 : DEFAULT_LIMIT[cls];
  if (cls !== "dalnice" && routerSpeed > 0) l = Math.min(l, Math.max(30, routerSpeed * 1.1));
  return l;
}

export function buildSegments(pts: Pt[]): Segment[] {
  const segs: Segment[] = [];
  let i = 0;
  while (i < pts.length - 1) {
    const start = i;
    let dist = 0;
    let tH = 0;
    while (i < pts.length - 1 && pts[i].cls === pts[start].cls && (dist < CHUNK_KM || i === start)) {
      const d = haversineKm([pts[i].lat, pts[i].lon], [pts[i + 1].lat, pts[i + 1].lon]);
      dist += d;
      tH += d / Math.max(pts[i].speed, 5);
      i++;
    }
    if (dist <= 0) continue;
    const [e0, e1] = [pts[start].ele, pts[i].ele];
    const speed = tH > 0 ? dist / tH : 50;
    segs.push(segment(dist, pts[start].cls, limit(pts[start].cls, pts[start].country, speed),
                      { elevationDeltaM: e0 !== null && e1 !== null ? e1 - e0 : 0 }));
  }
  return segs;
}

function ranges(values: number[][] | undefined, n: number, def: number): number[] {
  const out = new Array(n).fill(def);
  for (const [a, b, v] of values || []) for (let k = a; k <= Math.min(b, n - 1); k++) out[k] = v;
  return out;
}

export function parseOrs(data: any): RouteResult {
  const f = data.features[0];
  const coords: number[][] = f.geometry.coordinates;
  const props = f.properties;
  const n = coords.length;
  const ex = props.extras || {};
  const wcat = ranges(ex.waycategory?.values, n, 0);
  const wtype = ranges(ex.waytype?.values, n, 2);
  const country = ranges(ex.countryinfo?.values, n, 203);
  const speed = new Array(n).fill(50);
  for (const seg of props.segments || []) for (const st of seg.steps || []) {
    const [a, b] = st.way_points;
    const v = st.duration ? st.distance / 1000 / (st.duration / 3600) : 50;
    for (let k = a; k <= Math.min(b, n - 1); k++) speed[k] = v;
  }
  const pts: Pt[] = coords.map((c, k) => ({
    lat: c[1], lon: c[0], ele: c.length > 2 ? c[2] : null, speed: speed[k], country: country[k],
    cls: wcat[k] & 1 ? "dalnice" : wtype[k] === 1 ? "prvni_trida" : wtype[k] === 3 ? "mesto" : "okresni",
  }));
  return { route: { segments: buildSegments(pts) }, points: pts.map((p) => [p.lat, p.lon]), source: "openrouteservice",
           routerMinutes: props.summary.duration / 60, notes: [] };
}

async function routeOrs(wps: LatLon[], key?: string): Promise<RouteResult> {
  if (!key) throw new SourceError("openrouteservice: klíč není nastaven");
  const down = Number(localStorage.getItem(ORS_DOWN_KEY) || 0);
  if (Date.now() - down < 15 * 60000) throw new SourceError("openrouteservice: nedávno nedostupné");
  try {
    const data = await requestJson(ORS_URL, {
      body: { coordinates: wps.map(([la, lo]) => [lo, la]), elevation: true, extra_info: ["waycategory", "waytype", "countryinfo"], instructions: true },
      headers: { Authorization: key, Accept: "application/geo+json, application/json, */*" }, timeoutS: 25,
      cacheKind: "ors", ttlS: TTL_S });   // ORS /geojson vrací 406 při Accept jen application/json
    return parseOrs(data);
  } catch (e) {
    try { localStorage.setItem(ORS_DOWN_KEY, String(Date.now())); } catch { /* */ }
    throw e;
  }
}

export function parseOsrm(data: any): Pt[] {
  const pts: Pt[] = [];
  for (const leg of data.routes[0].legs) for (const st of leg.steps) {
    const cl = new Set<string>();
    for (const it of st.intersections || []) for (const c of it.classes || []) cl.add(c);
    const v = st.duration ? st.distance / 1000 / (st.duration / 3600) : 50;
    const cls: RoadClass = cl.has("motorway") || MOTORWAY_REF.test(st.ref || "") || v >= 95 ? "dalnice"
      : v >= 70 ? "prvni_trida" : v >= 45 ? "okresni" : "mesto";
    for (const [lon, lat] of st.geometry.coordinates) {
      const last = pts[pts.length - 1];
      if (last && Math.abs(last.lat - lat) < 1e-9 && Math.abs(last.lon - lon) < 1e-9) continue;
      pts.push({ lat, lon, ele: null, cls, speed: v });
    }
  }
  return pts;
}

async function addElevation(pts: Pt[]): Promise<void> {
  const idx = [0];
  let acc = 0;
  for (let k = 1; k < pts.length; k++) {
    acc += haversineKm([pts[k - 1].lat, pts[k - 1].lon], [pts[k].lat, pts[k].lon]);
    if (acc >= 1 || k === pts.length - 1) { idx.push(k); acc = 0; }
  }
  const elev = new Map<number, number>();
  for (let c = 0; c < idx.length; c += 100) {
    const chunk = idx.slice(c, c + 100);
    const d = await requestJson(ELEVATION_URL, { params: {
      latitude: chunk.map((k) => pts[k].lat.toFixed(5)).join(","), longitude: chunk.map((k) => pts[k].lon.toFixed(5)).join(",") },
      timeoutS: 30, cacheKind: "elev", ttlS: 30 * 86400 });
    chunk.forEach((k, i) => elev.set(k, d.elevation?.[i]));
  }
  const keys = [...elev.keys()].sort((a, b) => a - b);
  for (let i = 0; i < keys.length - 1; i++) {
    const [a, b] = [keys[i], keys[i + 1]];
    for (let k = a; k <= b; k++) pts[k].ele = elev.get(a)! + ((k - a) / (b - a || 1)) * (elev.get(b)! - elev.get(a)!);
  }
}

async function routeOsrm(wps: LatLon[]): Promise<RouteResult> {
  const coords = wps.map(([la, lo]) => `${lo.toFixed(6)},${la.toFixed(6)}`).join(";");
  const data = await requestJson(OSRM_URL + coords, { params: { overview: "false", steps: "true", geometries: "geojson" },
                                                      timeoutS: 40, cacheKind: "osrm", ttlS: TTL_S });
  if (data.code !== "Ok") throw new SourceError(`OSRM: ${data.code}`);
  const pts = parseOsrm(data);
  const notes = ["Trasa z OSRM (záloha): třídy silnic odhadnuty z označení silnic a rychlosti routeru."];
  try { await addElevation(pts); } catch (e) { notes.push(`Převýšení nedostupné (${(e as Error).message}) — počítáno po rovině.`); }
  return { route: { segments: buildSegments(pts) }, points: pts.map((p) => [p.lat, p.lon]), source: "OSRM (záloha)",
           routerMinutes: data.routes[0].duration / 60, notes };
}

export async function planGeometry(wps: LatLon[], orsKey?: string): Promise<RouteResult> {
  try { return await routeOrs(wps, orsKey); }
  catch (e) {
    const r = await routeOsrm(wps);
    r.notes.unshift(`openrouteservice nedostupné (${(e as Error).message}) — použita záloha.`);
    return r;
  }
}
