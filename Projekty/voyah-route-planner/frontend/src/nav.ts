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

/** Apple Mapy: spolehlivě jen jeden cíl → navigace úsek po úseku. */
export function appleTo(p: LL, name?: string): string {
  const q = name ? `&q=${encodeURIComponent(name)}` : "";
  return `https://maps.apple.com/?daddr=${ll(p)}&dirflg=d${q}`;
}

/** Waze: jen jeden cíl (průjezdní body nepodporuje) → navigace po úsecích; odkaz otevře aplikaci Waze, jinak web. */
export function wazeTo(p: LL): string {
  return `https://waze.com/ul?ll=${ll(p)}&navigate=yes`;
}
