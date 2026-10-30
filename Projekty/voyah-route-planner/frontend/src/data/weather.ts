/** Počasí z Open-Meteo (CC BY 4.0): teplota, protivítr (× 0,6 výška auta), povrch v hodině průjezdu (přepis weather.py). */
import type { Route, Surface } from "../core/models";
import { Polyline, bearingDeg, type LatLon } from "./geo";
import { requestJson } from "./http";

const URL_ = "https://api.open-meteo.com/v1/forecast";
const SAMPLE_KM = 25;

export const headwindKmh = (wind: number, fromDeg: number, heading: number) =>
  wind * 0.6 * Math.cos(((fromDeg - heading) * Math.PI) / 180);
export const surfaceFrom = (precip: number, snow: number): Surface => (snow > 0 ? "snih" : precip >= 0.2 ? "mokro" : "sucho");

export async function applyWeather(route: Route, points: LatLon[], depart: Date = new Date()): Promise<string[]> {
  const line = Polyline.from(points);
  const n = Math.max(2, Math.floor(line.lengthKm / SAMPLE_KM) + 1);
  const samples = Array.from({ length: n }, (_, k) => line.pointAt((line.lengthKm * k) / (n - 1)));
  let data: any;
  try {
    data = await requestJson(URL_, { params: {
      latitude: samples.map(([a]) => a.toFixed(3)).join(","), longitude: samples.map(([, b]) => b.toFixed(3)).join(","),
      hourly: "temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,snowfall", wind_speed_unit: "kmh",
      timezone: "UTC", forecast_days: 7 }, timeoutS: 30, cacheKind: "weather", ttlS: 3600 });
  } catch (e) {
    return [`Počasí nedostupné (${(e as Error).message}) — počítáno s +20 °C bez větru.`];
  }
  if (!Array.isArray(data)) data = [data];
  let km = 0;
  let minutes = 0;
  for (const seg of route.segments) {
    const mid = km + seg.lengthKm / 2;
    const k = line.lengthKm ? Math.min(n - 1, Math.round((mid / line.lengthKm) * (n - 1))) : 0;
    const h = data[k].hourly;
    const t = new Date(depart.getTime() + minutes * 60000);
    const key = t.toISOString().slice(0, 13) + ":00";
    let i = h.time.indexOf(key);
    if (i < 0) i = t < new Date(h.time[0] + "Z") ? 0 : h.time.length - 1;
    const a = line.pointAt(Math.max(0, mid - 0.3));
    const b = line.pointAt(Math.min(line.lengthKm, mid + 0.3));
    seg.tempC = h.temperature_2m[i];
    seg.headwindKmh = headwindKmh(h.wind_speed_10m[i], h.wind_direction_10m[i], bearingDeg(a, b));
    seg.surface = surfaceFrom(h.precipitation[i] || 0, h.snowfall[i] || 0);
    km += seg.lengthKm;
    minutes += (seg.lengthKm / Math.max(seg.speedLimit * 0.9, 20)) * 60;
  }
  return [];
}
