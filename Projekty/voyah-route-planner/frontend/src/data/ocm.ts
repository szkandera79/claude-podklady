/** Open Charge Map — doplňkový zdroj (stav, datum ověření, cena); licence CC BY 4.0, kontrola licence poskytovatele.
 *  V ČR má OCM ~1/4 stanic oproti OSM (30. 10. 2026: 232 vs. 901 s CCS2). */
import { encodePolyline, type LatLon } from "./geo";
import { SourceError, requestJson } from "./http";
import { normalizeOperator } from "./operators";
import { UNKNOWN_POWER_KW, type ChargerRecord } from "./osm";

const OCM_URL = "https://api.openchargemap.io/v3/poi/";
const CCS2 = 33;
const ACCESS: Record<number, ChargerRecord["access"]> = { 1: "public", 4: "public", 5: "public", 7: "public", 2: "private", 3: "private", 6: "customers" };

export function parsePoi(p: any): ChargerRecord | null {
  if (p.DataProvider && p.DataProvider.IsOpenDataLicensed === false) return null;
  const conns = (p.Connections || []).filter((c: any) => c.ConnectionTypeID === CCS2);
  const a = p.AddressInfo || {};
  if (!conns.length || a.Latitude == null) return null;
  const kws = conns.map((c: any) => c.PowerKW).filter(Boolean);
  const kw = kws.length ? Math.max(...kws) : null;
  const notes: string[] = [];
  if (kw === null) notes.push(`výkon v datech chybí, počítáno konzervativně s ${UNKNOWN_POWER_KW} kW`);
  if (p.UsageCost) {
    const c = String(p.UsageCost).split(/\s+/).join(" ");
    notes.push(`cena dle OCM: ${c.slice(0, 100)}${c.length > 100 ? "…" : ""}`);
  }
  const usage = p.UsageTypeID ?? p.UsageType?.ID;
  return { source: "OCM", sourceId: String(p.ID), lat: +a.Latitude, lon: +a.Longitude, name: a.Title || "Nabíjecí stanice",
           operator: normalizeOperator(p.OperatorInfo?.Title || ""), maxKw: kw ?? UNKNOWN_POWER_KW, powerKnown: kw !== null,
           points: Math.max(1, conns.reduce((s: number, c: any) => s + (c.Quantity || 1), 0)), access: ACCESS[usage] ?? "unknown",
           operational: p.StatusType ? p.StatusType.IsOperational ?? null : null,
           updated: (p.DateLastVerified || p.DateLastStatusUpdate || "").slice(0, 10) || null,
           address: [a.AddressLine1, a.Town].filter(Boolean).join(", "), notes };
}

export async function fetchAlong(points: LatLon[], corridorKm: number, key?: string): Promise<ChargerRecord[]> {
  if (!key) throw new SourceError("Open Charge Map: klíč není nastaven");
  const data = await requestJson<any[]>(OCM_URL, {
    params: { output: "json", polyline: encodePolyline(points), distance: corridorKm, distanceunit: "km",
              connectiontypeid: CCS2, maxresults: 5000, compact: "false", verbose: "false" },
    headers: { "X-API-Key": key }, timeoutS: 60, cacheKind: "ocm", ttlS: 86400 });
  return data.map(parsePoi).filter((r): r is ChargerRecord => r !== null);
}
