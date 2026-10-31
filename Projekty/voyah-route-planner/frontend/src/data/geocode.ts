/** Geokódování přes Photon (komoot, data OSM, bez klíče); „49.83, 18.26" se bere přímo.
 *  Více míst stejného jména (jiná obec, kraj, země) → candidates() vrátí seznam k výběru. */
import { haversineKm } from "./geo";
import { SourceError, requestJson } from "./http";

export interface Place { lat: number; lon: number; label: string; detail: string; }

const COORDS = /^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$/;
const AMBIGUOUS_KM = 3;
const SAME_NAME_KM = 30;     // obec a stejnojmenný okres/kraj (Budapest město × župa) = jedno místo
const SETTLEMENT = new Set(["city", "town", "village", "hamlet", "municipality"]);

function toPlace(f: any, text: string): Place {
  const [lon, lat] = f.geometry.coordinates;
  const p = f.properties || {};
  const street = p.street ? [p.street, p.housenumber].filter(Boolean).join(" ") : "";
  const name = p.name || street || text;
  const town = p.city || p.district || p.county;
  const label = [name, town !== name ? town : "", p.country].filter(Boolean).join(", ");
  const detail = [street && street !== name ? street : "", p.postcode, town, p.county !== town ? p.county : "", p.state, p.country]
    .filter(Boolean).join(" · ");
  return { lat, lon, label: label || text, detail };
}

async function search(text: string, limit: number): Promise<any[]> {
  const d = await requestJson("https://photon.komoot.io/api/", {
    params: { q: text, limit, lang: "default", lat: 49.8, lon: 15.5 }, timeoutS: 20, cacheKind: "geo", ttlS: 30 * 86400 });
  return d.features || [];
}

export async function geocode(text: string): Promise<[number, number, string]> {
  const m = text.match(COORDS);
  if (m) return [parseFloat(m[1]), parseFloat(m[2]), "Moje poloha"];
  const f = (await search(text, 1))[0];
  if (!f) throw new SourceError(`Adresu „${text}“ se nepodařilo najít`);
  const pl = toPlace(f, text);
  return [pl.lat, pl.lon, pl.label];
}

const norm = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();

/** Místa stejného jména vzdálená od sebe > 3 km; prázdné pole = jednoznačné (nebo souřadnice). */
export async function candidates(text: string): Promise<Place[]> {
  if (COORDS.test(text) || !text.trim()) return [];
  const feats = await search(text, 8);
  if (feats.length < 2) return [];
  const first = norm(text.split(",")[0]);
  const out: Place[] = [];
  const seen = new Set<string>();
  // když jsou mezi výsledky obce, porovnávat jen obce (restaurace „Ostrava“ v Polsku není jiná Ostrava)
  const isPlace = (f: any) => ["place", "boundary"].includes(f.properties?.osm_key);
  const isArea = (f: any) => !SETTLEMENT.has(f.properties?.osm_value) && f.properties?.type !== "city";
  const pool = (feats.some(isPlace) ? feats.filter(isPlace) : feats)
    .map((f, i) => [f, i] as const).sort((a, b) => Number(isArea(a[0])) - Number(isArea(b[0])) || a[1] - b[1]).map(([f]) => f);
  const names: { name: string; at: [number, number] }[] = [];
  for (const f of pool) {
    const p = f.properties || {};
    const name = norm(p.name || p.street || "");
    if (!name || !(name.includes(first) || first.includes(name))) continue;
    // stejná obec (městské části, ulice v ní) = jedno místo; různá obec / okres / kraj / země = nabídnout výběr
    const muni = SETTLEMENT.has(p.osm_value) || p.type === "city" ? p.name : p.city || p.name;
    const key = norm([p.country, p.state, p.county, muni].join("|"));
    const pl = toPlace(f, text);
    if (seen.has(key) || out.some((o) => haversineKm([o.lat, o.lon], [pl.lat, pl.lon]) < AMBIGUOUS_KM)) continue;
    if (names.some((n) => n.name === name && haversineKm(n.at, [pl.lat, pl.lon]) < SAME_NAME_KM)) continue;
    seen.add(key);
    names.push({ name, at: [pl.lat, pl.lon] });
    out.push(pl);
  }
  return out.length >= 2 ? out : [];
}
