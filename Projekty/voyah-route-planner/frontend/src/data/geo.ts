/** Geometrie: vzdálenosti, kurz, kódování polyline, průmět bodu na trasu (přepis vrp_data/geo.py). */
export type LatLon = [number, number];
const R_KM = 6371.0088;
const rad = (d: number) => (d * Math.PI) / 180;

export function haversineKm(a: LatLon, b: LatLon): number {
  const [la1, lo1, la2, lo2] = [rad(a[0]), rad(a[1]), rad(b[0]), rad(b[1])];
  const h = Math.sin((la2 - la1) / 2) ** 2 + Math.cos(la1) * Math.cos(la2) * Math.sin((lo2 - lo1) / 2) ** 2;
  return 2 * R_KM * Math.asin(Math.sqrt(h));
}

export function bearingDeg(a: LatLon, b: LatLon): number {
  const la1 = rad(a[0]);
  const la2 = rad(b[0]);
  const dlo = rad(b[1] - a[1]);
  const x = Math.sin(dlo) * Math.cos(la2);
  const y = Math.cos(la1) * Math.sin(la2) - Math.sin(la1) * Math.cos(la2) * Math.cos(dlo);
  return ((Math.atan2(x, y) * 180) / Math.PI + 360) % 360;
}

export function encodePolyline(points: LatLon[], precision = 5): string {
  const f = 10 ** precision;
  let out = "";
  let plat = 0;
  let plon = 0;
  for (const [lat, lon] of points) {
    const ilat = Math.round(lat * f);
    const ilon = Math.round(lon * f);
    for (const d of [ilat - plat, ilon - plon]) {
      let v = d < 0 ? ~(d << 1) : d << 1;
      while (v >= 0x20) { out += String.fromCharCode((0x20 | (v & 0x1f)) + 63); v >>= 5; }
      out += String.fromCharCode(v + 63);
    }
    plat = ilat; plon = ilon;
  }
  return out;
}

export function simplifyByDistance(points: LatLon[], stepKm: number): LatLon[] {
  if (!points.length) return [];
  const out: LatLon[] = [points[0]];
  let acc = 0;
  for (let i = 1; i < points.length; i++) {
    acc += haversineKm(points[i - 1], points[i]);
    if (acc >= stepKm) { out.push(points[i]); acc = 0; }
  }
  const last = points[points.length - 1];
  if (out[out.length - 1] !== last) out.push(last);
  return out;
}

export class Polyline {
  constructor(public points: LatLon[], public cumKm: number[]) {}

  static from(points: LatLon[]): Polyline {
    const cum = [0];
    for (let i = 1; i < points.length; i++) cum.push(cum[i - 1] + haversineKm(points[i - 1], points[i]));
    return new Polyline(points, cum);
  }
  get lengthKm() { return this.cumKm[this.cumKm.length - 1]; }

  pointAt(km: number): LatLon {
    const c = this.cumKm;
    if (km <= 0) return this.points[0];
    if (km >= c[c.length - 1]) return this.points[this.points.length - 1];
    let lo = 0;
    let hi = c.length - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (c[m] <= km) lo = m; else hi = m; }
    const seg = c[lo + 1] - c[lo];
    const f = seg ? (km - c[lo]) / seg : 0;
    const [a, b] = [this.points[lo], this.points[lo + 1]];
    return [a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])];
  }

  /** [km podél trasy, kolmá vzdálenost km] — lokální rovinná aproximace. */
  project(p: LatLon): [number, number] {
    let best: [number, number] = [0, Infinity];
    const kx = Math.cos(rad(p[0])) * 111.32;
    const ky = 110.57;
    for (let i = 0; i < this.points.length - 1; i++) {
      const [a, b] = [this.points[i], this.points[i + 1]];
      const ax = (a[1] - p[1]) * kx; const ay = (a[0] - p[0]) * ky;
      const bx = (b[1] - p[1]) * kx; const by = (b[0] - p[0]) * ky;
      const dx = bx - ax; const dy = by - ay;
      const L2 = dx * dx + dy * dy;
      const t = L2 === 0 ? 0 : Math.max(0, Math.min(1, -(ax * dx + ay * dy) / L2));
      const d = Math.hypot(ax + t * dx, ay + t * dy);
      if (d < best[1]) best = [this.cumKm[i] + t * (this.cumKm[i + 1] - this.cumKm[i]), d];
    }
    return best;
  }
}
