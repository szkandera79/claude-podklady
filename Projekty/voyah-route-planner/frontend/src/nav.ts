import type { Stop } from "./types";

type LL = { lat: number; lon: number };
const ll = (p: LL) => `${p.lat.toFixed(6)},${p.lon.toFixed(6)}`;

/** Google Maps: celá trasa s nabíječkami jako průjezdními body (start = aktuální poloha telefonu). */
export function googleRoute(dest: LL, stops: Stop[]): string {
  const wp = stops.filter((s) => s.station.lat != null)
    .map((s) => ll({ lat: s.station.lat!, lon: s.station.lon! })).join("|");
  const u = new URL("https://www.google.com/maps/dir/");
  u.searchParams.set("api", "1");
  u.searchParams.set("destination", ll(dest));
  if (wp) u.searchParams.set("waypoints", wp);
  u.searchParams.set("travelmode", "driving");
  return u.toString();
}

export function googleTo(p: LL): string {
  return `https://www.google.com/maps/dir/?api=1&destination=${ll(p)}&travelmode=driving`;
}

const lonlat = (p: LL) => `${p.lon.toFixed(6)},${p.lat.toFixed(6)}`;

/** Mapy.cz (mapy.com/fnc/v1): trasa s až 15 průjezdními body, navigate=true spustí navigaci v aplikaci Mapy.cz.
 *  Bez `from` začíná trasa v aktuální poloze (dle aplikace). Souřadnice lon,lat. */
export function mapyRoute(dest: LL, stops: Stop[] = [], from?: LL): string {
  const u = new URL("https://mapy.com/fnc/v1/route");
  if (from) u.searchParams.set("start", lonlat(from));
  u.searchParams.set("end", lonlat(dest));
  const wp = stops.filter((s) => s.station.lat != null).slice(0, 15).map((s) => lonlat({ lat: s.station.lat!, lon: s.station.lon! }));
  if (wp.length) u.searchParams.set("waypoints", wp.join(";"));
  u.searchParams.set("routeType", "car_fast_traffic");
  u.searchParams.set("navigate", "true");
  return u.toString();
}
export const mapyTo = (p: LL, from?: LL) => mapyRoute(p, [], from);

/** Waze: jen jeden cíl (průjezdní body nepodporuje) → navigace po úsecích; odkaz otevře aplikaci Waze, jinak web. */
export function wazeTo(p: LL): string {
  return `https://waze.com/ul?ll=${ll(p)}&navigate=yes`;
}
