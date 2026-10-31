/**
 * Lokální „server" v telefonu: stejné rozhraní jako dřívější HTTP API (backend/vrp_api/app.py), data v IndexedDB.
 * Nic se neodesílá na vlastní server — jen dotazy na veřejné služby (trasy, nabíječky, počasí, geokódování).
 */
import { addObservation, calibrationFn, emptyCalibration, GROUP, tempBand, uncertainty, type CalibrationData } from "../core/calibration";
import { routeProfile } from "../core/energy";
import type { DriveProfile, EnergyParams, Mode, PlanParams, RoadClass, Route, Station, Tariff, Vehicle } from "../core/models";
import { ChargingCurve, defaultEnergy, planParams, station as mkStation, tariff, tariffForStation, withVat } from "../core/models";
import { planRoute, type Plan as CorePlan } from "../core/optimizer";
import { stopAlternatives, type Alternative } from "../core/alternatives";
import { socUpdate } from "../core/trip";
import { merge, stationsAlong, toStations } from "../data/chargers";
import { fetchAlong } from "../data/ocm";
import { fetchTile, tilesFor, type ChargerRecord } from "../data/osm";
import { roadMatrix } from "../data/routing";
import { consumptionPer100 } from "../core/energy";
import { chargeCost, stationChargeTable } from "../core/charging";
import { costWeight } from "../core/optimizer";
import { Polyline, haversineKm, simplifyByDistance, type LatLon } from "../data/geo";
import { candidates, geocode, type Place } from "../data/geocode";
import { SourceError, pruneCache } from "../data/http";
import { planGeometry } from "../data/routing";
import { applyWeather } from "../data/weather";
import type { AssistState, BackupOption, Calibration, NearbyOption, NearbyResult, Plan, PlanRequest, PlanResult, Settings, SocUpdate, StationBrief,
              StopBackups, Trip } from "../types";
import { getKeys } from "./keys";
import { entryState, loadPrices, tariffTiers, type PriceEntry, type PriceList } from "../data/prices";
import { idbDel, idbGet, idbKeys, idbPut } from "./idb";

export const ATTRIBUTION = "Mapová a nabíjecí data © OpenStreetMap contributors (ODbL) · Open Charge Map (CC BY 4.0) · " +
  "Weather data by Open-Meteo.com (CC BY 4.0) · geokódování Photon · trasy openrouteservice / OSRM";
const OFFROUTE_WARN_KM = 3;
const CHARGE_DETECT_PCT = 2;
const MIN_OBS_KM = 20;
const MAX_PLANS = 20;
const IDEAL_BONUS_MIN = 2;      // bonus stanice v ideálním výkonovém rozmezí (vyvážený režim)

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
export const TARIFFS_VERSION = 3;
const T = (from_kw: number, price: number, price_min = 0, after_min = 9999) => ({ from_kw, price, price_min, after_min });
/** Ceníky 30. 10. 2026, ceny BEZ DPH. Uživatel: PRE Start (základní, bez paušálu) + E.ON Drive registrovaný.
 *  Cizí sítě v ČR = roaming čipem PRE dle „Ceník dobíjení na stanicích ostatních provozovatelů platný od 1. 7. 2026“.
 *  PRE: DC < 150 kW, UFC ≥ 150 kW. E.ON vlastní: pásma 0–100 / 101–200 / 201+ kW (denní sazba). */
export const DEFAULT_TARIFFS: Settings["tariffs"] = [
  { operator: "PRE", payment: "čip PRE – Start", includes_vat: false, preferred: true, member: true, priority: 1, price: 9.91,
    tiers: [T(0, 9.91, 1.65, 60), T(150, 11.57, 1.65, 30)], cenik_id: "pre-start",
    note: "PRE CHARGE START (ceník PRE POINT od 1. 12. 2025): DC 12 / UFC 14 Kč s DPH, stání 2 Kč/min po 60 / 30 min" },
  { operator: "E.ON", cenik_id: "eon-drive", payment: "karta E.ON Drive – registrovaný", includes_vat: true, preferred: true, member: true, priority: 2,
    price: 9.5, tiers: [T(0, 9.5), T(101, 13, 2, 60), T(201, 16.9, 2, 30)],
    note: "denní sazby (noc 20–8 h levněji: 8 / 10 / 12 Kč); DPH dle článků neuvedeno — ověřte v aplikaci E.ON Drive. Čipem PRE by to bylo 14,87 / 17,36 Kč bez DPH" },
  { operator: "Lidl", cenik_id: "pr-lidl", payment: "čip PRE – roaming", includes_vat: false, preferred: true, member: false, priority: 3, price: 10.91,
    tiers: [T(0, 10.91, 0.83, 60)] },
  { operator: "Tesla", cenik_id: "tesla", payment: "aplikace Tesla", includes_vat: false, preferred: true, member: false, priority: 4, price: 12,
    note: "dle vaší zkušenosti 10–12 Kč bez DPH; čipem PRE nelze" },
  { operator: "ČEZ", cenik_id: "pr-cez", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 15.7,
    tiers: [T(0, 15.7, 1.65, 60), T(150, 21.49, 1.65, 60)] },
  { operator: "IONITY", cenik_id: "pr-ionity", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 20.66,
    tiers: [T(0, 20.66, 2.48, 60)] },
  { operator: "Teplárny Brno", cenik_id: "pr-teplarny", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 14.05, tiers: [T(0, 14.05, 0.83, 60), T(150, 14.87, 0.83, 60)] },
  { operator: "Shell", cenik_id: "pr-shell", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 14.05,
    tiers: [T(0, 14.05, 1.65, 45)] },
  { operator: "Chargee", cenik_id: "pr-chargee", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 20.66,
    tiers: [T(0, 20.66, 1.65, 90), T(150, 22.31, 1.65, 60)] },
  { operator: "innogy", cenik_id: "pr-innogy", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 14.87,
    tiers: [T(0, 14.87, 1.65, 90), T(150, 14.87, 1.65, 30)] },
  { operator: "Orlen", cenik_id: "pr-orlen", payment: "čip PRE – roaming", includes_vat: false, preferred: false, member: false, priority: 10, price: 10.74,
    tiers: [T(0, 10.74), T(150, 14.87)], note: "UFC v ceníku PRE nejednoznačné (13 Kč s DPH × 14,87 bez DPH) — počítáno s vyšší" },
  { operator: "Smatrics", cenik_id: "pr-smatrics", payment: "čip PRE – roaming (AT)", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 10.74, tiers: [T(0, 10.74), T(150, 12.8)] },
  { operator: "EnBW", cenik_id: "pr-enbw", payment: "čip PRE – roaming (DE)", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 15.29, tiers: [T(0, 15.29, 4.13, 30)] },
  { operator: "Greenway", cenik_id: "pr-greenway", payment: "čip PRE – roaming (SK, PL)", includes_vat: false, preferred: false, member: false, priority: 10,
    price: 20.8, tiers: [T(0, 20.8, 2.48, 60), T(150, 20.66, 2.48, 60)] },
  { operator: "ZSE", cenik_id: "pr-zse", payment: "čip PRE – roaming (SK)", includes_vat: false, preferred: false, member: false, priority: 10, price: 12.4,
    note: "UFC v ceníku PRE nejednoznačné — počítáno 12,40 Kč" },
];
DEFAULT_SETTINGS.tariffs = DEFAULT_TARIFFS;
DEFAULT_SETTINGS.tariffs_version = TARIFFS_VERSION;
DEFAULT_SETTINGS.planning.prices_without_vat = true;
DEFAULT_SETTINGS.planning.tesla_ok = true;     // uživatel na Superchargerech běžně nabíjí
Object.assign(DEFAULT_SETTINGS.planning, {
  ideal_kw_min: 75, ideal_kw_max: 100,     // Voyah nabíjí max. ~89 kW → výkonnější stojan nezrychlí
  max_detour_km: 8, alert_saving_czk: 100, alerts_on: true, prices_auto_update: true, offline_data: true,
  assistant_on: true, soc_prompt_min: 30,
  trailer_extra_motorway: 10, trailer_extra_other: 5,    // přívěs: kWh/100 km navíc (zkušenost uživatele)
  trailer_max_kmh: 115,                                  // s přívěsem jezdí po dálnici ~110–120 km/h
});

const tierSig = (t: Settings["tariffs"][number]) => JSON.stringify([!!t.includes_vat,
  (t.tiers?.length ? t.tiers : [{ from_kw: 0, price: t.price }]).map((x) => [+x.from_kw, +x.price, +(x.price_min ?? 0), +(x.after_min ?? 9999)])]);
/** Výchozí PRE z verze 2 (bez poplatků za stání) — při přechodu na v3 se nahradí, ostatní ruční úpravy zůstanou. */
const PRE_V2 = JSON.stringify([false, [[0, 9.92, 0, 9999], [150, 11.57, 0, 9999]]]);

/** Přechod uložených tarifů na novou verzi výchozích: nahradí jen tarify, které uživatel neupravil. */
function migrateTariffs(stored: Settings["tariffs"], from: number): Settings["tariffs"] {
  if (from < 2) return structuredClone(DEFAULT_TARIFFS);
  const defs = new Map(DEFAULT_TARIFFS.map((t) => [t.operator, t]));
  const out = stored.map((t) => {
    const d = defs.get(t.operator);
    if (!d) return t;
    const same = tierSig(t) === tierSig(d) || (t.operator === "PRE" && tierSig(t) === PRE_V2);
    return same ? { ...structuredClone(d), preferred: t.preferred, priority: t.priority, member: t.member }
                : { ...t, cenik_id: t.cenik_id ?? d.cenik_id, auto: false };
  });
  for (const d of DEFAULT_TARIFFS) if (!stored.some((t) => t.operator === d.operator)) out.push(structuredClone(d));
  return out;
}

function merged(s: Partial<Settings> | undefined): Settings {
  const d = structuredClone(DEFAULT_SETTINGS);
  if (!s) return d;
  const ver = s.tariffs_version ?? 1;
  const tariffs = ver < TARIFFS_VERSION ? migrateTariffs(s.tariffs ?? [], ver) : s.tariffs ?? d.tariffs;
  return { vehicle: { ...d.vehicle, ...(s.vehicle || {}) }, energy: { ...d.energy, ...(s.energy || {}) },
           planning: { ...d.planning, ...(s.planning || {}) }, tariffs, tariffs_version: TARIFFS_VERSION };
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
    defaultPriceKwh: basePrice(+p.default_price_kwh, true, p.prices_without_vat !== false),
    idealKwMin: +(p.ideal_kw_min ?? 75), idealKwMax: +(p.ideal_kw_max ?? 100), idealBonusMin: IDEAL_BONUS_MIN,
    maxDetourKm: +(p.max_detour_km ?? 8), ...Object.fromEntries(Object.entries(over).filter(([, v]) => v !== undefined)) });
}

async function settings(): Promise<Settings> { return merged(await idbGet<Settings>("kv", "settings")); }
async function calibration(): Promise<CalibrationData> { return (await idbGet<CalibrationData>("kv", "calibration")) ?? emptyCalibration(); }

async function models(req?: PlanRequest) {
  return modelsFrom(await settings(), await calibration(), req);
}
/** Přívěs: spotřeba navíc z nastavení, jen když ho žádost o plán obsahuje. */
function withTrailer(e: EnergyParams, s: Settings, req?: PlanRequest): EnergyParams {
  if (req?.trailer) {
    e.trailerMotorway = +(s.planning.trailer_extra_motorway ?? 10);
    e.trailerOther = +(s.planning.trailer_extra_other ?? 5);
    e.maxSpeed = +(s.planning.trailer_max_kmh ?? 115);
  }
  return e;
}
function modelsFrom(s: Settings, cal: CalibrationData, req?: PlanRequest) {
  const energy = withTrailer(energyFrom(s), s, req);
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

interface StoredPlan { id: string; created: number; request: PlanRequest; route: Route; points: LatLon[]; stations: Station[]; result: PlanResult;
                     backups?: Record<string, StopBackups[]>; }
interface TripState { reference: { km: number; soc: number }; last: { km: number; soc: number } | null; k_trip: number; plan: Plan;
                      backups?: { at: number; stops: StopBackups[] }; }
interface StoredTrip { id: string; plan_id: string; variant: string; created: number; finished: number | null; state: TripState;
                       readings: { route_km: number; soc: number; ts: number; kind: string; lat?: number; lon?: number }[]; }

const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);

function requestParams(s: Settings, req: PlanRequest, soc: number): PlanParams {
  return paramsFrom(s, soc, { reserveDestination: req.reserve_destination, reserveStation: req.reserve_station,
                              profile: req.profile as DriveProfile | undefined, conservative: req.conservative });
}

// ------------------------------------------------------------------ API

async function plan(req: PlanRequest, progress?: (m: string) => void): Promise<PlanResult> {
  const { s, vehicle, energy, tariffs, calFn } = await models(req);
  const keys = getKeys();
  const params = requestParams(s, req, req.soc);
  try {
    progress?.("Hledám adresy…");
    const where = (t: string) => (req.pins?.[t] ? Promise.resolve(req.pins[t]) : geocode(t));
    const o = await where(req.origin);
    const d = await where(req.destination);
    const vias = [];
    for (const v of req.via.filter((x) => x.trim())) vias.push(await where(v));
    progress?.("Počítám trasu…");
    const rr = await planGeometry([[o[0], o[1]], ...vias.map((v) => [v[0], v[1]] as LatLon), [d[0], d[1]]], keys.ors);
    progress?.("Počasí na trase…");
    const notes = [...rr.notes, ...(await applyWeather(rr.route, rr.points))];
    progress?.("Nabíječky podél trasy…");
    const { stations, issues } = await stationsAlong(rr.points, +s.planning.corridor_km, keys.ocm, progress);
    notes.push(...issues);
    if (s.planning.tesla_ok !== false)
      for (const st of stations) if (st.operator === "Tesla") st.notes = st.notes.filter((n) => !n.startsWith("Tesla Supercharger"));
    if (!keys.ocm) notes.push("Klíč Open Charge Map není nastaven — nabíječky jen z OpenStreetMap.");
    if (req.trailer) notes.unshift(`Jízda s přívěsem: max. ${energy.maxSpeed} km/h, spotřeba +${energy.trailerMotorway} kWh/100 km na dálnici, +${energy.trailerOther} kWh/100 km na ostatních silnicích (Nastavení).`);
    progress?.("Optimalizuji zastávky…");
    let requiredStationId: string | undefined;
    if (req.required_station) {
      const rq = req.required_station;
      const hit = stations.map((x) => ({ x, d: haversineKm([rq.lat, rq.lon], [x.lat ?? 0, x.lon ?? 0]) })).sort((a, b) => a.d - b.d)[0];
      if (hit && hit.d <= 0.3) requiredStationId = hit.x.id;
      else notes.push("Zvolená náhradní nabíječka není v datech trasy — plán ji nemusí obsahovat.");
    }
    const plans: Record<string, Plan> = {};
    for (const [name, over] of Object.entries(VARIANTS))
      plans[name] = planToDict(planRoute(rr.route, stations, vehicle, { ...params, ...over },
                                         { energy, tariffs, calibration: calFn, requiredStationId }));
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

/** Pole, jejichž text odpovídá více místům (a uživatel je ještě nevybral) → nabídka k výběru. */
async function ambiguousPlaces(texts: string[], pins: PlanRequest["pins"] = {}): Promise<{ text: string; choices: Place[] }[]> {
  const out = [];
  for (const t of texts) {
    if (!t.trim() || pins[t]) continue;
    try { const c = await candidates(t); if (c.length) out.push({ text: t, choices: c }); } catch { /* ověří až plánování */ }
  }
  return out;
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
  const { s, vehicle, energy, tariffs, calFn } = await models(p.request);
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
    if (st.last && !p.request.trailer) await addObs(observation(p.route, ref, st.last, s), s);
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
  // jízda s přívěsem se do kalibrace vozu nezapočítává (jiná spotřeba)
  const applied = p.request.trailer ? null : await addObs(observation(p.route, t.state.reference, { km, soc: socNow }, s), s);
  t.readings.push({ route_km: km, soc: socNow, ts: Date.now(), kind: "cil", lat, lon });
  t.finished = Date.now();
  await idbPut("kv", `trip:${id}`, t);
  const msg = p.request.trailer ? "Jízda s přívěsem — do kalibrace spotřeby se nezapočítává."
    : applied === null ? "Úsek byl na kalibraci příliš krátký nebo se během něj nabíjelo."
    : applied ? "Jízda byla započtena do kalibrace spotřeby."
    : "Odchylka byla příliš velká (> 40 %) — jízda uložena, ale do modelu nezapočtena.";
  return { ok: true, calibration: msg };
}

// ------------------------------------------------------------------ záložní nabíječky (fáze 2, na pozadí)

/** Vstup výpočtu záložních stanic — jen klonovatelná data, aby šel poslat do Web Workeru. */
export interface BackupInput {
  route: Route; stations: Station[]; settings: Settings; calibration: CalibrationData; request: PlanRequest; variant: string;
  startKm: number; startSoc: number; kTrip: number;
}

function optionView(a: Alternative): BackupOption {
  const first = a.plan.stops.find((x) => x.station.id === a.station.id);
  return { station: stationBrief(a.station), delta_min: r1(a.deltaMin), delta_czk: Math.round(a.deltaCzk),
           arrive_soc: first?.arriveSoc ?? 0, plan: planToDict(a.plan) };
}

/** Čistý výpočet (běží ve Workeru; při nedostupnosti Workeru na hlavním vlákně). */
export function computeBackups(i: BackupInput): StopBackups[] {
  const { vehicle, energy, tariffs, calFn } = modelsFrom(merged(i.settings), i.calibration, i.request);
  const s = merged(i.settings);
  const params = { ...requestParams(s, i.request, i.startSoc), ...VARIANTS[i.variant], energyFactor: i.kTrip };
  const prof = routeProfile(i.route, vehicle, energy, params.profile, calFn);
  const o = { energy, tariffs, calibration: calFn, startKm: i.startKm, profileCache: prof };
  const base = planRoute(i.route, i.stations, vehicle, params, o);
  if (!base.feasible) return [];
  const saving = s.planning.alerts_on === false ? Infinity : +(s.planning.alert_saving_czk ?? 100);
  return stopAlternatives(i.route, i.stations, vehicle, params, o, base, { savingCzk: saving }).map((x) => ({
    station_id: x.stationId, backups: x.backups.map(optionView), cheaper: x.cheaper ? optionView(x.cheaper) : null }));
}

let worker: Worker | null | undefined;
let seq = 0;
const pending = new Map<number, { ok: (v: StopBackups[]) => void; err: (e: Error) => void }>();
function bgWorker(): Worker | null {
  if (worker !== undefined) return worker;
  try {
    worker = new Worker(new URL("./worker.ts", import.meta.url), { type: "module" });
    worker.onmessage = (e: MessageEvent) => {
      const h = pending.get(e.data.id);
      pending.delete(e.data.id);
      if (e.data.error) h?.err(new Error(e.data.error)); else h?.ok(e.data.result);
    };
    worker.onerror = () => { worker = null; for (const h of pending.values()) h.err(new Error("výpočet na pozadí selhal")); pending.clear(); };
  } catch { worker = null; }
  return worker;
}
/** Spustí výpočet záložních stanic mimo hlavní vlákno (UI zůstává plynulé). */
export function runBackups(input: BackupInput): Promise<StopBackups[]> {
  const w = bgWorker();
  if (!w) return new Promise((res) => setTimeout(() => res(computeBackups(input)), 0));
  return new Promise((ok, err) => { const id = ++seq; pending.set(id, { ok, err }); w.postMessage({ id, input }); });
}

const backupsInFlight = new Map<string, Promise<StopBackups[]>>();
function planBackups(planId: string, variant: string): Promise<StopBackups[]> {
  const k = `${planId}|${variant}`;
  let pr = backupsInFlight.get(k);
  if (!pr) { pr = planBackupsNow(planId, variant).finally(() => backupsInFlight.delete(k)); backupsInFlight.set(k, pr); }
  return pr;
}
async function planBackupsNow(planId: string, variant: string): Promise<StopBackups[]> {
  const p = await loadPlan(planId);
  if (p.backups?.[variant]) return p.backups[variant];
  const r = await runBackups({ route: p.route, stations: p.stations, settings: await settings(), calibration: await calibration(),
                               request: p.request, variant, startKm: 0, startSoc: +p.request.soc, kTrip: 1 });
  const fresh = (await idbGet<StoredPlan>("kv", `plan:${planId}`)) ?? p;
  fresh.backups = { ...(fresh.backups || {}), [variant]: r };
  await idbPut("kv", `plan:${planId}`, fresh);
  return r;
}

function tripPosition(t: StoredTrip): { km: number; soc: number } {
  const last = t.readings[t.readings.length - 1];
  return { km: last?.route_km ?? 0, soc: last?.soc ?? t.state.reference.soc };
}

async function tripBackups(tripId: string): Promise<StopBackups[]> {
  const t = await loadTrip(tripId);
  if (t.state.backups && t.state.backups.at === t.readings.length) return t.state.backups.stops;
  const p = await loadPlan(t.plan_id);
  const pos = tripPosition(t);
  const r = await runBackups({ route: p.route, stations: p.stations, settings: await settings(), calibration: await calibration(),
                               request: p.request, variant: t.variant, startKm: pos.km, startSoc: pos.soc, kTrip: t.state.k_trip });
  const fresh = await loadTrip(tripId);
  fresh.state.backups = { at: fresh.readings.length, stops: r };
  await idbPut("kv", `trip:${tripId}`, fresh);
  return r;
}

/** Výměna stanice: přepočet se stejným cílem, zastávka povinně u `stationId`, `excludeId` (původní) vyřazena.
 *  Volá se jen po potvrzení uživatelem. */
async function useStation(ref: { planId: string; variant: string } | { tripId: string }, stationId: string,
                          excludeId?: string): Promise<Plan> {
  const trip = "tripId" in ref ? await loadTrip(ref.tripId) : null;
  const p = await loadPlan(trip ? trip.plan_id : (ref as { planId: string }).planId);
  const { s, vehicle, energy, tariffs, calFn } = await models(p.request);
  const variant = trip ? trip.variant : (ref as { variant: string }).variant;
  const pos = trip ? tripPosition(trip) : { km: 0, soc: +p.request.soc };
  const params = { ...requestParams(s, p.request, pos.soc), ...VARIANTS[variant], energyFactor: trip?.state.k_trip ?? 1 };
  const stations = p.stations.map((x) => (x.id === excludeId ? { ...x, available: false } : x));
  const plan = planRoute(p.route, stations, vehicle, params,
                         { energy, tariffs, calibration: calFn, startKm: pos.km, requiredStationId: stationId });
  if (!plan.feasible) throw new ApiError(400, plan.reason);
  const view = planToDict(plan);
  const name = p.stations.find((x) => x.id === stationId)?.name ?? "zvolená stanice";
  view.warnings.unshift(`Upraveno ručně: zastávka u „${name}“.`);
  if (trip) {
    trip.state.plan = view;
    trip.state.backups = undefined;
    await idbPut("kv", `trip:${trip.id}`, trip);
  } else {
    p.result.plans[variant] = view;
    if (p.backups) delete p.backups[variant];
    await idbPut("kv", `plan:${p.id}`, p);
  }
  return view;
}

// ------------------------------------------------------------------ náhradní nabíječka v okolí

const NEARBY_KM = 40;            // hledání do 40 km vzdušnou čarou
const NEARBY_MATRIX = 12;        // na silniční vzdálenost se ptáme jen u nejlepších 12 (1 dotaz)
const NEARBY_TOP = 6;
const ROAD_FACTOR = 1.3;         // odhad offline: silnice ≈ 1,3 × vzdušná čára, 60 km/h
const ON_ROUTE_KM = 15;

/** Nabíječky v okolí polohy: silniční vzdálenost, SOC při příjezdu, cena dle tarifu, při aktivní cestě i čas do cíle. */
async function nearbyChargers(lat: number, lon: number, socNow: number, tripId?: string | null): Promise<NearbyResult> {
  const { s, vehicle, energy, tariffs, calFn } = await models();
  const keys = getKeys();
  const notes: string[] = [];
  const here: LatLon = [lat, lon];
  const recs = new Map<string, ChargerRecord>();
  const deadline = Date.now() + 30000;
  for (const [la, lo] of tilesFor([here], 0.4)) {
    try { for (const r of await fetchTile(la, lo, deadline)) recs.set(r.sourceId, r); }
    catch (e) { notes.push(`Část okolí bez dat OpenStreetMap (${(e as Error).message}) — zobrazeno poslední známé.`); }
  }
  let ocm: ChargerRecord[] = [];
  if (keys.ocm) {
    try { ocm = await fetchAlong([here, [lat + 0.001, lon]], NEARBY_KM, keys.ocm); }
    catch { notes.push("Open Charge Map nedostupné — jen stanice z OpenStreetMap."); }
  }
  const all = merge([...recs.values()], ocm).filter((r) => r.access !== "private" && r.operational !== false
    && (s.planning.tesla_ok !== false || r.operator !== "Tesla"));

  const t = tripId ? await loadTrip(tripId).catch(() => null) : null;
  const p = t ? await loadPlan(t.plan_id).catch(() => null) : null;
  const kTrip = t?.state.k_trip ?? 1;
  if (p) withTrailer(energy, s, p.request);
  const params = p ? { ...requestParams(s, p.request, socNow), ...VARIANTS[t!.variant], energyFactor: kTrip }
                   : paramsFrom(s, socNow, { mode: "vyvazeny" as Mode });
  const w = costWeight(params);
  const perKm = ((consumptionPer100(80, energy, "okresni") + energy.trailerOther) / 100) * 1.1 * kTrip;      // konzervativně
  const cap = vehicle.usableKwh;
  const pref = (op: string) => !!tariffs[op]?.preferred;
  const ideal = (kw: number) => kw >= params.idealKwMin && kw <= params.idealKwMax;

  const near = all.map((r) => ({ r, air: haversineKm(here, [r.lat, r.lon]) }))
    .filter((x) => x.air <= NEARBY_KM && socNow - (x.air * ROAD_FACTOR * perKm / cap) * 100 >= 0)
    .sort((a, b) => (a.air - (pref(a.r.operator) ? 8 : 0) - (ideal(a.r.maxKw) ? 3 : 0) + (a.r.maxKw < 50 ? 10 : 0))
                  - (b.air - (pref(b.r.operator) ? 8 : 0) - (ideal(b.r.maxKw) ? 3 : 0) + (b.r.maxKw < 50 ? 10 : 0)))
    .slice(0, NEARBY_MATRIX);
  const mx = await roadMatrix(here, near.map((x) => [x.r.lat, x.r.lon] as LatLon), keys.ors);
  if (!mx) notes.push("Bez připojení k síti: vzdálenosti a časy jsou odhad (1,3 × vzdušná čára).");

  const line = p ? Polyline.from(p.points) : null;
  const pos = line ? { km: line.project(here)[0] } : null;                // aktuální poloha na trase (GPS), ne poslední zadání
  const prof = p ? routeProfile(p.route, vehicle, energy, params.profile, calFn) : null;
  const opts: NearbyOption[] = near.map(({ r, air }, i) => {
    const leg = mx?.legs[i] ?? { km: air * ROAD_FACTOR, min: (air * ROAD_FACTOR / 60) * 60 };
    const arrive = socNow - (leg.km * perKm / cap) * 100;
    const st = line ? toStations([r], line, 999)[0] : mkStation(`${r.source}:${r.sourceId}`, 0, r.maxKw,
      { name: r.name, operator: r.operator, points: r.points, lat: r.lat, lon: r.lon, address: r.address, notes: r.notes,
        dataSource: r.source, dataUpdated: r.updated });
    const off = line ? line.project([r.lat, r.lon])[1] : Infinity;
    const tar = tariffForStation(tariffs[r.operator], r.maxKw);
    let chargeTo = Math.min(100, Math.max(80, Math.ceil(arrive) + 10));
    const table = stationChargeTable(vehicle, st, params.batteryTempC);
    const a0 = Math.max(0, Math.floor(arrive));
    let chargeMin = table.time(a0, chargeTo);
    let cost = chargeCost(tar, table.energy(a0, chargeTo), chargeMin, params.defaultPriceKwh);
    let total: number | null = null;
    let destSoc: number | null = null;
    const onRoute = !!(p && pos && prof && off <= ON_ROUTE_KM && st.routeKm > pos.km - ON_ROUTE_KM);
    if (onRoute && st.routeKm <= pos!.km + 0.05) {          // stanice vedle / kousek za polohou: dojezd = silniční cesta k ní
      st.routeKm = pos!.km + 0.05;
      st.detourKm = Math.max(st.detourKm, leg.km);
      st.detourMin = Math.max(st.detourMin, leg.min);
    }
    if (onRoute) {
      const others = p!.stations.filter((x) => x.id !== st.id);
      const plan = planRoute(p!.route, [...others, st], vehicle, { ...params, startSoc: socNow },
                             { energy, tariffs, calibration: calFn, startKm: pos!.km, profileCache: prof!, requiredStationId: st.id });
      const stop = plan.stops.find((x) => x.station.id === st.id);
      if (plan.feasible && stop) {
        total = plan.totalMin; destSoc = plan.arrivalSoc;
        chargeTo = stop.departSoc; chargeMin = stop.chargeMin; cost = stop.costCzk;
      }
    }
    return { station: stationBrief(st), road_km: r1(leg.km), drive_min: r1(leg.min), distance_estimated: !mx || !mx.legs[i],
             arrive_soc: Math.floor(arrive), reachable: arrive >= params.reserveStation, preferred: pref(r.operator),
             price_kwh: tar ? Math.round(tar.priceKwh * 100) / 100 : null, charge_to: chargeTo, charge_min: r1(chargeMin),
             cost_czk: Math.round(cost), total_min: total === null ? null : r1(total), dest_soc: destSoc, on_route: onRoute,
             status: r.operational === true ? "v provozu (dle OCM)" : "stav neznámý" };
  });
  const score = (o: NearbyOption) => (o.reachable ? 0 : 1000) + (o.total_min ?? o.drive_min + o.charge_min + 60) + w * o.cost_czk
    - (o.preferred ? params.preferredBonusMin : 0) - (ideal(o.station.max_kw) ? params.idealBonusMin : 0);
  opts.sort((a, b) => score(a) - score(b));
  if (!opts.length) notes.push(`Do ${NEARBY_KM} km není v datech dosažitelná nabíječka CCS2.`);
  else if (!opts.some((o) => o.reachable)) notes.push(`Žádná stanice není dosažitelná s rezervou ${params.reserveStation} % — jeďte úsporně k nejbližší.`);
  notes.push("Obsazenost a funkčnost stanic datové zdroje neposkytují — ověřte v aplikaci provozovatele.");
  return { options: opts.slice(0, NEARBY_TOP), notes, soc: socNow, lat, lon, distance_source: mx?.source || "odhad" };
}

/** Přesměrování aktivní cesty přes náhradní nabíječku: nová trasa poloha → stanice → původní cíl, stejná varianta.
 *  Bez sítě: přepočet po původní trase s povinnou zastávkou (stanice blízko trasy). Jen po potvrzení uživatelem. */
async function rerouteVia(tripId: string, o: NearbyOption | null, lat: number, lon: number, socNow: number): Promise<{ trip_id: string; note: string }> {
  const t = await loadTrip(tripId);
  const p = await loadPlan(t.plan_id);
  const end = p.result.geometry[p.result.geometry.length - 1];
  const destLabel = p.result.destination;
  const req: PlanRequest = { ...p.request, origin: `${lat.toFixed(5)}, ${lon.toFixed(5)}`, destination: destLabel, via: [],
    soc: socNow, pins: { [destLabel]: [end[0], end[1], destLabel] }, required_station: undefined };
  if (o?.station.lat != null) {
    req.via = [`${o.station.lat.toFixed(6)}, ${o.station.lon!.toFixed(6)}`];
    req.required_station = { lat: o.station.lat, lon: o.station.lon! };
  }
  try {
    const res = await plan(req);
    t.finished = Date.now();
    t.readings.push({ route_km: tripPosition(t).km, soc: socNow, ts: Date.now(), kind: "presmerovano", lat, lon });
    await idbPut("kv", `trip:${t.id}`, t);
    const nt = await startTrip(res.plan_id, t.variant);
    const fresh = await loadTrip(nt.trip_id);
    fresh.state.k_trip = t.state.k_trip;
    await idbPut("kv", `trip:${fresh.id}`, fresh);
    return { trip_id: nt.trip_id, note: o ? `Trasa přepočítána přes „${o.station.name}“ do cíle ${destLabel}.`
                                          : `Trasa přepočítána z aktuální polohy do cíle ${destLabel}.` };
  } catch (e) {
    if (!o?.on_route) throw e;
    const { vehicle } = await models();
    const line = Polyline.from(p.points);
    const id = o.station.id;
    if (!p.stations.some((x) => x.id === id)) {
      const [km, off] = line.project([o.station.lat!, o.station.lon!]);
      const det = off > 0.05 ? off * 1.4 + 0.3 : 0;
      p.stations.push(mkStation(id, km, o.station.max_kw, { name: o.station.name, operator: o.station.operator, points: o.station.points,
        lat: o.station.lat, lon: o.station.lon, address: o.station.address, detourKm: det, detourMin: det ? (det / 40) * 60 + 1 : 0,
        dataSource: o.station.source, dataUpdated: o.station.updated, notes: o.station.notes, connectors: [vehicle.connector] }));
      await idbPut("kv", `plan:${p.id}`, p);
    }
    await useStation({ tripId }, id);
    return { trip_id: tripId, note: "Bez připojení: zastávka změněna na původní trase (bez nové navigace)." };
  }
}

// ------------------------------------------------------------------ aktivní asistent (levné, bez přepočtu trasy)

const profileCache = new Map<string, { prof: ReturnType<typeof routeProfile>; line: Polyline }>();
const NEAR_STOP_KM = 0.3;
const PROMPT_KM = 50;

/** Stav jízdy z GPS: ujeté km, odhad SOC z modelu, ETA, riziko dojezdu. Trasu nepřepočítává — jen hlásí události. */
async function assist(tripId: string, lat: number, lon: number): Promise<AssistState> {
  const t = await loadTrip(tripId);
  const p = await loadPlan(t.plan_id);
  const { s, vehicle, energy, calFn } = await models(p.request);
  const params = { ...requestParams(s, p.request, +p.request.soc), ...VARIANTS[t.variant] };
  const key = `${p.id}|${t.variant}`;
  let c = profileCache.get(key);
  if (!c) { c = { prof: routeProfile(p.route, vehicle, energy, params.profile, calFn), line: Polyline.from(p.points) }; profileCache.set(key, c); }
  const { prof, line } = c;
  const [km, off] = line.project([lat, lon]);
  const last = t.readings[t.readings.length - 1];
  const mult = (params.conservative ? 1 + energy.uncertainty : 1) * t.state.k_trip;
  const cap = vehicle.usableKwh;
  const pct = (a: number, b: number) => (b > a ? (prof.energyBetween(a, b) * mult / cap) * 100 : 0);
  const est = Math.max(0, last.soc - pct(last.route_km, km));
  const ahead = t.state.plan.stops.filter((x) => x.arrive_km > km + 0.2);
  const next = ahead[0];
  const nextSoc = next ? est - pct(km, next.arrive_km) : null;
  // SOC v cíli: po poslední zastávce podle plánu, bez zastávky z odhadu
  const destSoc = ahead.length ? ahead[ahead.length - 1].depart_soc - pct(ahead[ahead.length - 1].arrive_km, prof.totalKm)
                               : est - pct(km, prof.totalKm);
  const remaining = prof.minutesBetween(Math.min(km, prof.totalKm), prof.totalKm)
    + ahead.reduce((a, x) => a + x.charge_min + params.stopOverheadMin, 0);
  let risk: string | null = null;
  if (next && nextSoc! < params.reserveStation)
    risk = `K zastávce ${next.station.name} dorazíte odhadem s ${Math.round(nextSoc!)} % (rezerva ${params.reserveStation} %).`;
  else if (!next && destSoc < params.reserveDestination)
    risk = `Do cíle dorazíte odhadem s ${Math.round(destSoc)} % (rezerva ${params.reserveDestination} %).`;
  const stopNear = t.state.plan.stops.find((x) => x.station.lat != null && haversineKm([lat, lon], [x.station.lat, x.station.lon!]) <= NEAR_STOP_KM);
  const minSince = (Date.now() - last.ts) / 60000;
  return { route_km: r1(km), off_km: r1(off), est_soc: Math.round(est), next_name: next?.station.name ?? null,
           next_soc: nextSoc === null ? null : Math.round(nextSoc), dest_soc: Math.round(destSoc),
           remaining_min: r1(remaining), eta: Date.now() + remaining * 60000, risk, off_route: off > OFFROUTE_WARN_KM,
           at_stop: stopNear?.station.name ?? null,
           prompt_soc: minSince >= +(s.planning.soc_prompt_min ?? 30) || km - last.route_km >= PROMPT_KM };
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

// ------------------------------------------------------------------ ceník → tarify

/** Tarify navázané na ceník (cenik_id, auto ≠ false) převezmou ověřené ceny. Ruční úpravy a neověřené ceny se nemění. */
export function applyPriceList(s: Settings, list: PriceList): { settings: Settings; changes: string[] } {
  const out = structuredClone(s);
  const changes: string[] = [];
  const byId = new Map(list.entries.map((e) => [e.id, e]));
  for (const t of out.tariffs) {
    const e = t.cenik_id ? byId.get(t.cenik_id) : undefined;
    if (!e || t.auto === false || !entryState(e, list).ok) continue;
    const tiers = tariffTiers(e);
    if (!tiers.length) continue;
    const next = { ...t, tiers, price: tiers[0].price, includes_vat: false };
    if (tierSig(next) === tierSig(t)) continue;
    changes.push(`${t.operator}: ${(t.tiers?.length ? t.tiers.map((x) => x.price) : [t.price]).join(" / ")} → ${tiers.map((x) => x.price).join(" / ")} Kč/kWh bez DPH`);
    Object.assign(t, next);
  }
  return { settings: out, changes };
}

/** Na pozadí 1× denně: stáhnout ceník a promítnout do tarifů (plánování nečeká). */
async function refreshPrices(force = false): Promise<{ changes: string[]; offline: boolean } | null> {
  const s = await settings();
  if (!force && s.planning.prices_auto_update === false) return null;
  const lp = await loadPrices(force);
  if (!lp) return null;
  const { settings: ns, changes } = applyPriceList(s, lp.list);
  if (changes.length) await idbPut("kv", "settings", ns);
  return { changes, offline: lp.offline };
}

/** Převzít položku ceníku jako tarif sítě (z obrazovky Ceník). */
async function adoptPriceEntry(e: PriceEntry): Promise<Settings> {
  const s = await settings();
  const tiers = tariffTiers(e);
  if (!tiers.length) throw new ApiError(400, "Položka nemá cenu pro rychlonabíjení.");
  const old = s.tariffs.find((t) => t.operator === e.operator);
  const t = { operator: e.operator, payment: `${e.payment} – ${e.plan}`, includes_vat: false, preferred: old?.preferred ?? false,
              member: e.membership, priority: old?.priority ?? 10, price: tiers[0].price, tiers, cenik_id: e.id, auto: true,
              note: e.note || undefined };
  s.tariffs = old ? s.tariffs.map((x) => (x === old ? t : x)) : [...s.tariffs, t];
  await idbPut("kv", "settings", s);
  return s;
}

/** Po naplánování na pozadí: záložní stanice všech variant, okolí zastávek (pro náhradní nabíječku), ceník.
 *  Vše se ukládá do IndexedDB → cesta funguje i bez signálu (údaje označené jako poslední známé). */
async function prepareOffline(planId: string): Promise<void> {
  const s = await settings();
  if (s.planning.offline_data === false) return;
  await loadPrices().catch(() => null);
  const p = await loadPlan(planId);
  const pts: LatLon[] = [];
  for (const [variant, pl] of Object.entries(p.result.plans)) {
    if (!pl.feasible) continue;
    await planBackups(planId, variant).catch(() => null);
    for (const st of pl.stops) if (st.station.lat != null) pts.push([st.station.lat, st.station.lon!]);
  }
  const deadline = Date.now() + 60000;
  for (const [la, lo] of tilesFor(pts, 0.4)) await fetchTile(la, lo, deadline).catch(() => null);
}

export const service = {
  tariffsUpdated, refreshPrices, adoptPriceEntry, prepareOffline,
  plan, getPlan: async (id: string) => (await loadPlan(id)).result, startTrip, trip, soc, finish,
  planBackups, tripBackups, useStation, ambiguousPlaces, nearbyChargers, rerouteVia, assist,
  settings, saveSettings, resetSettings: async () => { await idbDel("kv", "settings"); return settings(); },
  calibration: calibrationView, resetCalibration: async () => { await idbDel("kv", "calibration"); return { ok: true }; },
  exportData, importData, pruneCache,
};

// pro testy a ladění
export const _internal = { migrateTariffs, merged, vehicleFrom, energyFrom, tariffsFrom, paramsFrom, observation, GROUP, tempBand };
