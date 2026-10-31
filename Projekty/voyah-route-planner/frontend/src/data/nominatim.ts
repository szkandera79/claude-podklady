/** Záloha geokódování: Nominatim (OSM). Zná i české exonymy („Řím“, „Záhřeb“), ale smí max. 1 dotaz/s
 *  → dotazy se řadí za sebe. Výsledky se převádějí do tvaru Photonu, aby se zbytek kódu neměnil. */
import { requestJson } from "./http";

const BASE = "https://nominatim.openstreetmap.org";
const GAP_MS = 1100;
let chain: Promise<unknown> = Promise.resolve();
let last = 0;

function throttled<T>(fn: () => Promise<T>): Promise<T> {
  const run = chain.then(async () => {
    const wait = last + GAP_MS - Date.now();
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
    last = Date.now();
    return fn();
  });
  chain = run.catch(() => undefined);
  return run;
}

const SETTLEMENT_TYPES = new Set(["city", "town", "village", "hamlet", "municipality"]);

function toPhoton(x: any): any {
  const a = x.address || {};
  const type = x.addresstype || x.type;
  return {
    geometry: { coordinates: [parseFloat(x.lon), parseFloat(x.lat)] },
    properties: {
      osm_key: x.category, osm_value: SETTLEMENT_TYPES.has(type) ? type : x.type, type,
      name: x.name || undefined, street: a.road, housenumber: a.house_number, postcode: a.postcode,
      city: a.city || a.town || a.village || a.municipality, county: a.county, state: a.state,
      country: a.country, countrycode: (a.country_code || "").toUpperCase(),
    },
  };
}

const COMMON = { format: "jsonv2", addressdetails: 1, "accept-language": "cs" };

export async function nominatimSearch(text: string, limit: number): Promise<any[]> {
  const d = await throttled(() => requestJson<any[]>(`${BASE}/search`, {
    params: { ...COMMON, q: text, limit }, timeoutS: 20, cacheKind: "geo-n", ttlS: 30 * 86400, referrerPolicy: "origin" }));
  return (d || []).map(toPhoton);
}

export async function nominatimCountry(lat: number, lon: number): Promise<string> {
  const d = await throttled(() => requestJson<any>(`${BASE}/reverse`, {
    params: { ...COMMON, lat: lat.toFixed(2), lon: lon.toFixed(2), zoom: 3 }, timeoutS: 20, cacheKind: "rev-n",
    ttlS: 365 * 86400, referrerPolicy: "origin" }));
  return (d?.address?.country_code || "").toUpperCase();
}
