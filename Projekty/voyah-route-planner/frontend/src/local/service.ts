/**
 * Lokální „server" v telefonu: stejné rozhraní jako dřívější HTTP API (backend/vrp_api/app.py), data v IndexedDB.
 * Nic se neodesílá na vlastní server — jen dotazy na veřejné služby (trasy, nabíječky, počasí, geokódování).
 */
import { addObservation, calibrationFn, emptyCalibration, GROUP, tempBand, uncertainty, type CalibrationData } from "../core/calibration";
import { routeProfile } from "../core/energy";
import type { DriveProfile, EnergyParams, Mode, PlanParams, RoadClass, Route, Station, Tariff, Vehicle } from "../core/models";
import { ChargingCurve, defaultEnergy, planParams, tariff, withVat } from "../core/models";
import { planRoute, type Plan as CorePlan } from "../core/optimizer";
import { socUpdate } from "../core/trip";
import { stationsAlong } from "../data/chargers";
import { Polyline, simplifyByDistance, type LatLon } from "../data/geo";
import { geocode } from "../data/geocode";
import { SourceError, pruneCache } from "../data/http";
import { planGeometry } from "../data/routing";
import { applyWeather } from "../data/weather";
import type { Calibration, Plan, PlanRequest, PlanResult, Settings, SocUpdate, StationBrief, Trip } from "../types";
import { getKeys } from "./keys";
import { idbDel, idbGet, idbKeys, idbPut } from "./idb";

export const ATTRIBUTION = "Mapová a nabíjecí data © OpenStreetMap contributors (ODbL) · Open Charge Map (CC BY 4.0) · " +
  "Weather data by Open-Meteo.com (CC BY 4.0) · geokódování Photon · trasy openrouteservice / OSRM";
const OFFROUTE_WARN_KM = 3;
const CHARGE_DETECT_PCT = 2;
const MIN_OBS_KM = 20;
const MAX_PLANS = 20;

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

// ------------------------------------------------------------------ nastavení

export const DEFAULT_SETTINGS: Settings = {
  vehicle: { name: "Voyah Free 2023", usable_kwh: 100, charge_efficiency: 0.95, mass_kg: 2400, extra_load_kg: 0,
             curve: [[0, 60], [10, 89], [80, 89], [81, 40], [90, 40], [91, 20], [100, 20]] },
  energy: { a: 9.43, b: 0.000997, city_extra: 1.5, heat_start_c: 15, heat_kw_per_c: 0.12, heat_base_kw: 0.3,
            batt_temp_coef: 0.006, regen_efficiency: 0.6, uncertainty: 0.08 },
  planning: { reserve_station: 10, reserve_destination: 15, profile: "standard", conservative: false, stop_overhead_min: 4,
              value_of_time_czk_h: 300, min_station_kw: 0, only_preferred: false, corridor_km: 5, default_price_kwh: 19 },
  tariffs: [],              // doplní DEFAULT_TARIFFS níže
};

/** Verze výchozích tarifů — při zvýšení se v telefonu nahradí uložené tarify novými (s upozorněním). */
export const TARIFFS_VERSION = 2;
const T = (from_kw: number, price: number, price_min = 0, after_min = 9999) => ({ from_kw, price, price_min, after_min });
/** Ceníky 30. 10. 2026, ceny BEZ DPH. Uživatel: PRE Start (základní, bez paušálu) + E.ON Drive registrovaný.
 *  Cizí sítě v ČR = roaming čipem PRE dle „Ceník dobíjení na stanicích ostatních provozovatelů platný od 1. 7. 2026“.
 *  PRE: DC < 150 kW, UFC ≥ 150 kW. E.ON vlastní: pásma 0–100 / 101–200 / 201+ kW (denní sazba). */
export const DEFAULT_TARIFFS: Settings["tariffs"] = [
  { operator: "PRE", payment: "čip PRE – Start", includes_vat: false, preferred: true, member: true, priority: 1, price: 9.92,
    tiers: [T(0, 9.92), T(150, 11.57)], note: "PRE Point Start: DC 12 / UFC 14 Kč s DPH" },
  { operator: "E.ON", payment: "karta E.ON Drive – registrovaný", includes_vat: true, preferred: true, member: true, priority: 2,
    price: 9.5, tiers: [T(0, 9.5), T(101, 13, 2, 60), T(201, 16.9, 2, 30)],
    note: "denní sazby (noc 20–8 h levněji: 8 / 10 / 12 Kč); DPH dle článků neuvedeno — ověřte v aplikaci E.ON Drive. Čipem PRE by to bylo 14,87 / 17,36 Kč bez DPH" },
  { operator: "Lidl", payment: "čip PRE – roaming", includes_vat: false, preferred: true, member: false, priority: 3, price: 10.91,
    tiers: [T(0, 10.91, 0.83, 60)] },
  { operator: "Tesla", payment: "aplikace Tesla", includes_vat: false, preferred: true, member: false, priority: 4, price: 12,
    note: "dle vaší zkušenosti 10–12 Kč bez DPH; čipem PRE nelze" },
  { operator: "ČEZ", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 15.7,
    tiers: [T(0, 15.7, 1.65, 60), T(150, 21.49, 1.65, 60)] },
  { operator: "IONITY", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 20.66,
    tiers: [T(0, 20.66, 2.48, 60)] },
  { operator: "Teplárny Brno", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 14.05, tiers: [T(0, 14.05, 0.83, 60), T(150, 14.87, 0.83, 60)] },
  { operator: "Shell", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 14.05,
    tiers: [T(0, 14.05, 1.65, 45)] },
  { operator: "Chargee", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 20.66,
    tiers: [T(0, 20.66, 1.65, 90), T(150, 22.31, 1.65, 60)] },
  { operator: "innogy", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 14.87,
    tiers: [T(0, 14.87, 1.65, 90), T(150, 14.87, 1.65, 30)] },
  { operator: "Orlen", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 10.74,
    tiers: [T(0, 10.74), T(150, 14.87)], note: "UFC v ceníku PRE nejednoznačné (13 Kč s DPH × 14,87 bez DPH) — počítáno s vyšší" },
  { operator: "Smatrics", payment: "čip PRE – roaming (AT)", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 10.74, tiers: [T(0, 10.74), T(150, 12.8)] },
  { operator: "EnBW", payment: "čip PRE – roaming (DE)", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 15.29, tiers: [T(0, 15.29, 4.13, 30)] },
  { operator: "Greenway", payment: "čip PRE – roaming (SK, PL)", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 20.8, tiers: [T(0, 20.8, 2.48, 60), T(150, 20.66, 2.48, 60)] },
  { operator: "ZSE", payment: "čip PRE – roaming (SK)", includes_vat: false, preferred: false, member: false, priority: 10, price: 12.4,
    note: "UFC v ceníku PRE nejednoznačné — počítáno 12,40 Kč" },
];
DEFAULT_SETTINGS.tariffs = DEFAULT_TARIFFS;
DEFAULT_SETTINGS.tariffs_version = TARIFFS_VERSION;
DEFAULT_SETTINGS.planning.prices_without_vat = true;

function merged(s: Partial<Settings> | undefined): Settings {
  const d = structuredClone(DEFAULT_SETTINGS);
  if (!s) return d;
  const fresh = (s.tariffs_version ?? 1) < TARIFFS_VERSION;      // starší výchozí tarify → nahradit novými
  return { vehicle: { ...d.vehicle, ...(s.vehicle || {}) }, energy: { ...d.energy, ...(s.energy || {}) },
           planning: { ...d.planning, ...(s.planning || {}) }, tariffs: fresh ? d.tariffs : s.tariffs ?? d.tariffs,
           tariffs_version: TARIFFS_VERSION };
}

const ENERGY_MAP: Record<string, keyof EnergyParams> = {
  a: "a", b: "b", city_extra: "cityExtra", heat_start_c: "heatStartC", heat_kw_per_c: "heatKwPerC",
  heat_base_kw: "heatBaseKw", batt_temp_coef: "battTempCoef", regen_efficiency: "regenEfficiency", uncertainty: "uncertainty",
};

function vehicleFrom(s: Settings): Vehicle {
  const v = s.vehicle;
  return { name: v.name, usableKwh: +v.usable_kwh, chargeEfficiency: +v.charge_efficiency, massKg: +v.mass_kg,
           extraLoadKg: +v.extra_load_kg, connector: "CCS2",
           curve: new ChargingCurve([...v.curve].map(([a, b]) => [+a, +b] as [number, number]).sort((x, y) => x[0] - y[0])) };
}
function energyFrom(s: Settings): EnergyParams {
  const e = defaultEnergy();
  for (const [k, v] of Object.entries(s.energy)) if (ENERGY_MAP[k]) (e as any)[ENERGY_MAP[k]] = +v;
  return e;
}
/** Převod ceny do jednotného základu: bez DPH (výchozí, uživatel je plátce DPH), nebo s DPH. */
export function basePrice(price: number, includesVat: boolean, withoutVat: boolean): number {
  if (withoutVat) return includesVat ? Math.round((price / 1.21) * 100) / 100 : price;
  return withVat(price, includesVat);
}

function tariffsFrom(s: Settings): Record<string, Tariff> {
  const net = s.planning.prices_without_vat !== false;
  const out: Record<string, Tariff> = {};
  for (const t of s.tariffs) {
    const v = !!t.includes_vat;
    out[t.operator] = tariff(t.operator, basePrice(+t.price, v, net), {
      priceMin: basePrice(+(t.price_min ?? 0), v, net), sessionFee: basePrice(+(t.session_fee ?? 0), v, net),
      blockingFeeMin: basePrice(+(t.blocking_fee_min ?? 0), v, net), blockingAfterMin: +(t.blocking_after_min ?? 9999),
      preferred: !!t.preferred, member: !!t.member, priority: +(t.priority ?? 99),
      tiers: t.tiers?.length ? t.tiers.map((x) => ({ minKw: +x.from_kw, priceKwh: basePrice(+x.price, v, net),
        priceMin: basePrice(+(x.price_min ?? 0), v, net), afterMin: +(x.after_min ?? 9999) })) : undefined });
  }
  return out;
}
function paramsFrom(s: Settings, soc: number, over: Partial<PlanParams> = {}): PlanParams {
  const p = s.planning;
  return planParams(soc, { reserveStation: +p.reserve_station, reserveDestination: +p.reserve_destination,
    profile: p.profile as DriveProfile, conservative: !!p.conservative, stopOverheadMin: +p.stop_overhead_min,
    valueOfTimeCzkH: +p.value_of_time_czk_h, minStationKw: +p.min_station_kw, onlyPreferred: !!p.only_preferred,
    defaultPriceKwh: basePrice(+p.default_price_kwh, true, p.prices_without_vat !== false), ...Object.fromEntries(Object.entries(over).filter(([, v]) => v !== undefined)) });
}

async function settings(): Promise<Settings> { return merged(await idbGet<Settings>("kv", "settings")); }
async function calibration(): Promise<CalibrationData> { return (await idbGet<CalibrationData>("kv", "calibration")) ?? emptyCalibration(); }

async function models() {
  const s = await settings();
  const cal = await calibration();
  const energy = energyFrom(s);
  if (Object.keys(cal.cells).length) energy.uncertainty = Math.min(energy.uncertainty, uncertainty(cal, energy.uncertainty));
  return { s, vehicle: vehicleFrom(s), energy, tariffs: tariffsFrom(s), cal, calFn: calibrationFn(cal) };
}

// ------------------------------------------------------------------ převody pro UI

const r1 = (x: number) => Math.round(x * 10) / 10;
export function stationBrief(st: Station): StationBrief {
  return { id: st.id, name: st.name, operator: st.operator, lat: st.lat, lon: st.lon, max_kw: st.maxKw, points: st.points,
           address: st.address, route_km: r1(st.routeKm), detour_km: r1(st.detourKm), source: st.dataSource,
           updated: st.dataUpdated, notes: st.notes };
}
export function planToDict(p: CorePlan): Plan {
  return { feasible: p.feasible, reason: p.reason, mode: p.mode, profile: p.profile, distance_km: r1(p.distanceKm),
           drive_min: r1(p.driveMin), charge_min: r1(p.chargeMin), stop_overhead_min: r1(p.stopOverheadMin),
           total_min: r1(p.totalMin), cost_czk: Math.round(p.costCzk), arrival_soc: p.arrivalSoc,
           trip_energy_kwh: r1(p.tripEnergyKwh), warnings: p.warnings,
           stops: p.stops.map((s) => ({ station: stationBrief(s.station), arrive_km: r1(s.arriveKm), arrive_soc: s.arriveSoc,
             depart_soc: s.departSoc, charge_min: r1(s.chargeMin), grid_kwh: r1(s.gridKwh), cost_czk: Math.round(s.costCzk),
             avg_kw: r1(s.avgKw), next_leg_km: r1(s.nextLegKm), arrive_min: r1(s.arriveMin), depart_min: r1(s.departMin) })) };
}

export const VARIANTS: Record<string, Partial<PlanParams>> = {
  nejrychlejsi: { mode: "nejrychlejsi" as Mode }, vyvazeny: { mode: "vyvazeny" as Mode },
  nejlevnejsi: { mode: "nejlevnejsi" as Mode }, eko: { mode: "nejrychlejsi" as Mode, profile: "eko" as DriveProfile },
};

interface StoredPlan { id: string; created: number; request: PlanRequest; route: Route; points: LatLon[]; stations: Station[]; result: PlanResult; }
interface TripState { reference: { km: number; soc: number }; last: { km: number; soc: number } | null; k_trip: number; plan: Plan; }
interface StoredTrip { id: string; plan_id: string; variant: string; created: number; finished: number | null; state: TripState;
                       readings: { route_km: number; soc: number; ts: number; kind: string; lat?: number; lon?: number }[]; }

const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);

function requestParams(s: Settings, req: PlanRequest, soc: number): PlanParams {
  return paramsFrom(s, soc, { reserveDestination: req.reserve_destination, reserveStation: req.reserve_station,
                              profile: req.profile as DriveProfile | undefined, conservative: req.conservative });
}

// ------------------------------------------------------------------ API

async function plan(req: PlanRequest, progress?: (m: string) => void): Promise<PlanResult> {
  const { s, vehicle, energy, tariffs, calFn } = await models();
  const keys = getKeys();
  const params = requestParams(s, req, req.soc);
  try {
    progress?.("Hledám adresy…");
    const o = await geocode(req.origin);
    const d = await geocode(req.destination);
    const vias = [];
    for (const v of req.via.filter((x) => x.trim())) vias.push(await geocode(v));
    progress?.("Počítám trasu…");
    const rr = await planGeometry([[o[0], o[1]], ...vias.map((v) => [v[0], v[1]] as LatLon), [d[0], d[1]]], keys.ors);
    progress?.("Počasí na trase…");
    const notes = [...rr.notes, ...(await applyWeather(rr.route, rr.points))];
    progress?.("Nabíječky podél trasy…");
    const { stations, issues } = await stationsAlong(rr.points, +s.planning.corridor_km, keys.ocm, progress);
    notes.push(...issues);
    if (!keys.ocm) notes.push("Klíč Open Charge Map není nastaven — nabíječky jen z OpenStreetMap.");
    progress?.("Optimalizuji zastávky…");
    const plans: Record<string, Plan> = {};
    for (const [name, over] of Object.entries(VARIANTS))
      plans[name] = planToDict(planRoute(rr.route, stations, vehicle, { ...params, ...over }, { energy, tariffs, calibration: calFn }));
    const id = uid();
    const result: PlanResult = {
      plan_id: id, origin: o[2], destination: d[2], route_source: rr.source,
      distance_km: r1(rr.route.segments.reduce((a, x) => a + x.lengthKm, 0)),
      geometry: simplifyByDistance(rr.points, 0.1).map(([a, b]) => [+a.toFixed(5), +b.toFixed(5)] as [number, number]),
      notes, calibrated: !!calFn, attribution: ATTRIBUTION, plans, stations: stations.map(stationBrief), request: req,
    };
    await idbPut("kv", `plan:${id}`, { id, created: Date.now(), request: req, route: rr.route, points: rr.points, stations, result } satisfies StoredPlan);
    await prunePlans();
    return result;
  } catch (e) {
    if (e instanceof SourceError) throw new ApiError(502, `Plán nelze spočítat: ${e.message}`);
    throw e;
  }
}

async function prunePlans() {
  const trips = await Promise.all((await idbKeys("kv")).filter((k) => k.startsWith("trip:")).map((k) => idbGet<StoredTrip>("kv", k)));
  const keep = new Set(trips.map((t) => t?.plan_id));
  const plans = (await Promise.all((await idbKeys("kv")).filter((k) => k.startsWith("plan:")).map((k) => idbGet<StoredPlan>("kv", k))))
    .filter((p): p is StoredPlan => !!p).sort((a, b) => b.created - a.created);
  for (const p of plans.slice(MAX_PLANS)) if (!keep.has(p.id)) await idbDel("kv", `plan:${p.id}`);
}

async function loadPlan(id: string): Promise<StoredPlan> {
  const p = await idbGet<StoredPlan>("kv", `plan:${id}`);
  if (!p) throw new ApiError(404, "Plán nenalezen");
  return p;
}
async function loadTrip(id: string): Promise<StoredTrip> {
  const t = await idbGet<StoredTrip>("kv", `trip:${id}`);
  if (!t) throw new ApiError(404, "Cesta nenalezena");
  return t;
}

async function startTrip(planId: string, variant: string) {
  const p = await loadPlan(planId);
  if (!VARIANTS[variant]) throw new ApiError(400, "Neznámá varianta");
  const soc = +p.request.soc;
  const t: StoredTrip = { id: uid(), plan_id: planId, variant, created: Date.now(), finished: null,
    state: { reference: { km: 0, soc }, last: null, k_trip: 1, plan: p.result.plans[variant] },
    readings: [{ route_km: 0, soc, ts: Date.now(), kind: "start" }] };
  await idbPut("kv", `trip:${t.id}`, t);
  return { trip_id: t.id };
}

async function trip(id: string): Promise<Trip> {
  const t = await loadTrip(id);
  const p = await loadPlan(t.plan_id);
  return { ...t, plan_result: p.result } as unknown as Trip;
}

function observation(route: Route, ref: { km: number; soc: number }, end: { km: number; soc: number }, s: Settings) {
  if (end.km - ref.km < MIN_OBS_KM || end.soc >= ref.soc) return null;
  const prof = routeProfile(route, vehicleFrom(s), energyFrom(s), s.planning.profile as DriveProfile);
  const kmBy: Partial<Record<RoadClass, number>> = {};
  const temps: number[] = [];
  let pos = 0;
  for (const seg of route.segments) {
    const mid = pos + seg.lengthKm / 2;
    if (mid >= ref.km && mid <= end.km) { kmBy[seg.roadClass] = (kmBy[seg.roadClass] || 0) + seg.lengthKm; temps.push(seg.tempC); }
    pos += seg.lengthKm;
  }
  if (!temps.length) return null;
  return { kmByClass: kmBy, tempC: temps.reduce((a, b) => a + b, 0) / temps.length,
           predictedKwh: prof.energyBetween(ref.km, end.km), socStart: ref.soc, socEnd: end.soc, ts: Date.now() };
}

async function addObs(obs: ReturnType<typeof observation>, s: Settings): Promise<boolean | null> {
  if (!obs) return null;
  const cal = await calibration();
  const applied = addObservation(cal, obs, +s.vehicle.usable_kwh);
  await idbPut("kv", "calibration", cal);
  return applied;
}

async function soc(id: string, socNow: number, lat?: number, lon?: number, routeKm?: number): Promise<SocUpdate> {
  const t = await loadTrip(id);
  if (t.finished) throw new ApiError(400, "Cesta je ukončená");
  const p = await loadPlan(t.plan_id);
  const { s, vehicle, energy, tariffs, calFn } = await models();
  const warnings: string[] = [];
  let km: number;
  let off = 0;
  if (lat != null && lon != null) {
    [km, off] = Polyline.from(p.points).project([lat, lon]);
    if (off > OFFROUTE_WARN_KM) warnings.push(`Jste ${Math.round(off)} km mimo plánovanou trasu — pro přesný výsledek naplánujte trasu znovu z aktuální polohy.`);
  } else if (routeKm != null) km = routeKm;
  else throw new ApiError(400, "Chybí poloha (GPS) nebo km trasy");

  const st = t.state;
  const ref = st.reference;
  const params = { ...requestParams(s, p.request, socNow), ...VARIANTS[t.variant] };
  const oldIds = st.plan.stops.filter((x) => x.arrive_km > km).map((x) => x.station.id).join("|");
  let newPlan: CorePlan;
  let result: Pick<SocUpdate, "predicted_soc" | "measured_ratio" | "k_trip">;
  let kind: string;
  const prev = st.last ?? ref;
  if (socNow > prev.soc + CHARGE_DETECT_PCT || km < ref.km) {
    if (st.last) await addObs(observation(p.route, ref, st.last, s), s);
    newPlan = planRoute(p.route, p.stations, vehicle, { ...params, energyFactor: st.k_trip },
                        { energy, tariffs, calibration: calFn, startKm: km });
    result = { predicted_soc: null, measured_ratio: null, k_trip: st.k_trip };
    st.reference = { km, soc: socNow };
    st.last = null;
    kind = "po_nabiti";
  } else {
    const u = socUpdate(p.route, p.stations, vehicle, params, { routeKm: ref.km, soc: ref.soc }, { routeKm: km, soc: socNow },
                        energy, tariffs, calFn);
    newPlan = u.plan;
    warnings.push(...u.warnings);
    st.k_trip = u.kTrip;
    st.last = { km, soc: socNow };
    result = { predicted_soc: r1(u.predictedSoc), measured_ratio: Math.round(u.measuredRatio * 1000) / 1000, k_trip: Math.round(u.kTrip * 1000) / 1000 };
    kind = "jizda";
  }
  const newIds = newPlan.stops.map((x) => x.station.id).join("|");
  if (newPlan.feasible && oldIds !== newIds) warnings.push(newIds ? "Plán zastávek se změnil." : "Další nabíjení už není potřeba.");
  st.plan = planToDict(newPlan);
  t.readings.push({ route_km: km, soc: socNow, ts: Date.now(), kind, lat, lon });
  await idbPut("kv", `trip:${id}`, t);
  const total = p.route.segments.reduce((a, x) => a + x.lengthKm, 0);
  return { route_km: r1(km), offroute_km: r1(off), remaining_km: r1(total - km), actual_soc: socNow, ...result, warnings, plan: st.plan };
}

async function finish(id: string, socNow: number, lat?: number, lon?: number) {
  const t = await loadTrip(id);
  const p = await loadPlan(t.plan_id);
  const s = await settings();
  const km = lat != null && lon != null ? Polyline.from(p.points).project([lat, lon])[0]
    : p.route.segments.reduce((a, x) => a + x.lengthKm, 0);
  const applied = await addObs(observation(p.route, t.state.reference, { km, soc: socNow }, s), s);
  t.readings.push({ route_km: km, soc: socNow, ts: Date.now(), kind: "cil", lat, lon });
  t.finished = Date.now();
  await idbPut("kv", `trip:${id}`, t);
  const msg = applied === null ? "Úsek byl na kalibraci příliš krátký nebo se během něj nabíjelo."
    : applied ? "Jízda byla započtena do kalibrace spotřeby."
    : "Odchylka byla příliš velká (> 40 %) — jízda uložena, ale do modelu nezapočtena.";
  return { ok: true, calibration: msg };
}

async function saveSettings(body: Settings): Promise<Settings> {
  const s = merged(body);
  if (!["eko", "standard", "rychly"].includes(s.planning.profile) || !(s.vehicle.usable_kwh > 0) || s.vehicle.curve.length < 2)
    throw new ApiError(400, "Neplatné nastavení");
  await idbPut("kv", "settings", s);
  return s;
}

async function calibrationView(): Promise<Calibration> {
  const s = await settings();
  const cal = await calibration();
  return {
    cells: Object.entries(cal.cells).sort().map(([k, [f, w]]) => {
      const [group, band] = k.split("|");
      return { group, band: +band, factor: Math.round(f * 1000) / 1000, weight: Math.round(w * 100) / 100 };
    }),
    uncertainty: Math.round(uncertainty(cal, +s.energy.uncertainty) * 1000) / 1000,
    observations: cal.observations.slice(-50).map((o) => ({ km: o.kmByClass as Record<string, number>, temp_c: r1(o.tempC),
      predicted_kwh: r1(o.predictedKwh), soc_start: o.socStart, soc_end: o.socEnd, applied: !!o.applied })),
  };
}

/** Záloha všech dat (bez klíčů API) → JSON; obnova ze zálohy. */
async function exportData(): Promise<string> {
  const out: Record<string, unknown> = {};
  for (const k of await idbKeys("kv")) out[k] = await idbGet("kv", k);
  return JSON.stringify({ app: "voyah-route-planner", version: 1, exported: new Date().toISOString(), data: out });
}
async function importData(json: string): Promise<number> {
  const d = JSON.parse(json);
  if (d.app !== "voyah-route-planner" || typeof d.data !== "object") throw new ApiError(400, "Neplatný soubor zálohy");
  for (const [k, v] of Object.entries(d.data)) await idbPut("kv", k, v);
  return Object.keys(d.data).length;
}

/** True, pokud uložené nastavení mělo starší tarify (pak se nahradí novými a uloží). */
async function tariffsUpdated(): Promise<boolean> {
  const stored = await idbGet<Settings>("kv", "settings");
  if (!stored || (stored.tariffs_version ?? 1) >= TARIFFS_VERSION) return false;
  await idbPut("kv", "settings", merged(stored));
  return true;
}

export const service = {
  tariffsUpdated,
  plan, getPlan: async (id: string) => (await loadPlan(id)).result, startTrip, trip, soc, finish,
  settings, saveSettings, resetSettings: async () => { await idbDel("kv", "settings"); return settings(); },
  calibration: calibrationView, resetCalibration: async () => { await idbDel("kv", "calibration"); return { ok: true }; },
  exportData, importData, pruneCache,
};

// pro testy a ladění
export const _internal = { merged, vehicleFrom, energyFrom, tariffsFrom, paramsFrom, observation, GROUP, tempBand };
