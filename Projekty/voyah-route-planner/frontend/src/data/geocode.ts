/** Geokódování přes Photon (komoot, data OSM, bez klíče); „49.83, 18.26" se bere přímo. */
import { SourceError, requestJson } from "./http";

export async function geocode(text: string): Promise<[number, number, string]> {
  const m = text.match(/^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$/);
  if (m) return [parseFloat(m[1]), parseFloat(m[2]), "Moje poloha"];
  const d = await requestJson("https://photon.komoot.io/api/", {
    params: { q: text, limit: 1, lang: "default", lat: 49.8, lon: 15.5 }, timeoutS: 20, cacheKind: "geo", ttlS: 30 * 86400 });
  const f = d.features?.[0];
  if (!f) throw new SourceError(`Adresu „${text}“ se nepodařilo najít`);
  const [lon, lat] = f.geometry.coordinates;
  const p = f.properties || {};
  return [lat, lon, [p.name, p.city || p.county, p.country].filter(Boolean).join(", ") || text];
}
