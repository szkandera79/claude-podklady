/**
 * Datový model plánovače — přepis backend/vrp/models.py (Python verze zůstává jako referenční implementace).
 * Jednotky: km, km/h, kWh, kW, minuty, Kč s DPH; SoC v % 0–100.
 */

export type RoadClass = "mesto" | "okresni" | "prvni_trida" | "rychlostni" | "dalnice";
export type DriveProfile = "eko" | "standard" | "rychly";
export type Mode = "nejrychlejsi" | "nejlevnejsi" | "vyvazeny";
export type Surface = "sucho" | "mokro" | "snih";

export type CurvePoint = [number, number];

export class ChargingCurve {
  constructor(public points: CurvePoint[]) {}

  powerAt(soc: number): number {
    const p = this.points;
    if (soc <= p[0][0]) return p[0][1];
    for (let i = 0; i < p.length - 1; i++) {
      const [s0, p0] = p[i];
      const [s1, p1] = p[i + 1];
      if (soc <= s1) return s1 === s0 ? p1 : p0 + ((p1 - p0) * (soc - s0)) / (s1 - s0);
    }
    return p[p.length - 1][1];
  }
}

export interface Vehicle {
  name: string;
  usableKwh: number;
  connector: string;
  massKg: number;
  extraLoadKg: number;
  chargeEfficiency: number;
  curve: ChargingCurve;
}

/** uživatel 30. 10. 2026: 10–80 % 89 kW, 80–90 % 40 kW, nad 90 % zhruba polovina (~20 kW) */
export const DEFAULT_CURVE: CurvePoint[] = [[0, 60], [10, 89], [80, 89], [81, 40], [90, 40], [91, 20], [100, 20]];

export function defaultVehicle(): Vehicle {
  return { name: "Voyah Free 2023", usableKwh: 100, connector: "CCS2", massKg: 2400, extraLoadKg: 0,
           chargeEfficiency: 0.95, curve: new ChargingCurve(DEFAULT_CURVE.map((p) => [...p] as CurvePoint)) };
}

export interface Segment {
  lengthKm: number;
  roadClass: RoadClass;
  speedLimit: number;
  elevationDeltaM: number;
  tempC: number;
  headwindKmh: number;
  surface: Surface;
}

export function segment(lengthKm: number, roadClass: RoadClass, speedLimit: number, extra: Partial<Segment> = {}): Segment {
  return { lengthKm, roadClass, speedLimit, elevationDeltaM: 0, tempC: 20, headwindKmh: 0, surface: "sucho", ...extra };
}

export interface Route { segments: Segment[]; }
export const routeLength = (r: Route) => r.segments.reduce((a, s) => a + s.lengthKm, 0);

export interface Station {
  id: string;
  name: string;
  operator: string;
  routeKm: number;
  maxKw: number;
  detourKm: number;
  detourMin: number;
  points: number;
  connectors: string[];
  accessOk: boolean;
  sharedPower: boolean;
  dataSource: string;
  dataUpdated: string | null;
  isLiveStatus: boolean;
  available: boolean | null;
  lat: number | null;
  lon: number | null;
  address: string;
  notes: string[];
}

export function station(id: string, routeKm: number, maxKw: number, extra: Partial<Station> = {}): Station {
  return { id, name: `Stanice ${id}`, operator: "Jiný", routeKm, maxKw, detourKm: 0, detourMin: 0, points: 1,
           connectors: ["CCS2"], accessOk: true, sharedPower: false, dataSource: "", dataUpdated: null,
           isLiveStatus: false, available: null, lat: null, lon: null, address: "", notes: [], ...extra };
}

/** Cenové pásmo podle výkonu stanice (např. PRE: DC < 150 kW, UFC ≥ 150 kW; E.ON: 0–100 / 101–200 / 201+ kW). */
export interface TariffTier {
  minKw: number;             // platí pro stanice s výkonem ≥ minKw (do dalšího pásma)
  priceKwh: number;
  priceMin: number;          // Kč/min po uplynutí afterMin (blokovací / časový poplatek)
  afterMin: number;
}

export interface Tariff {
  operator: string;
  priceKwh: number;          // Kč/kWh v jednotném základu (s DPH, nebo bez DPH dle nastavení)
  priceMin: number;
  sessionFee: number;
  blockingFeeMin: number;
  blockingAfterMin: number;
  preferred: boolean;
  member: boolean;
  priority: number;
  tiers?: TariffTier[];
}

/** Tarif pro konkrétní stanici: vybere pásmo podle výkonu stanice (bez pásem vrací tarif beze změny). */
export function tariffForStation(t: Tariff | undefined, stationKw: number): Tariff | undefined {
  if (!t?.tiers?.length) return t;
  const tier = [...t.tiers].sort((a, b) => a.minKw - b.minKw).filter((x) => stationKw >= x.minKw).pop() ?? t.tiers[0];
  return { ...t, priceKwh: tier.priceKwh, blockingFeeMin: tier.priceMin, blockingAfterMin: tier.priceMin ? tier.afterMin : 9999 };
}

export const withVat = (price: number, includesVat: boolean, vat = 0.21) =>
  includesVat ? price : Math.round(price * (1 + vat) * 100) / 100;

export function tariff(operator: string, priceKwh: number, extra: Partial<Tariff> = {}): Tariff {
  return { operator, priceKwh, priceMin: 0, sessionFee: 0, blockingFeeMin: 0, blockingAfterMin: 9999,
           preferred: false, member: false, priority: 99, ...extra };
}

/** Koeficienty energetického modelu — předpoklady ke kalibraci (ANALYZA.md kap. 5). */
export interface EnergyParams {
  a: number;                 // c(v) = a + b·v² [kWh/100 km]; fit 17,5 @ 90 a 25 @ 125 km/h (léto)
  b: number;
  cityExtra: number;
  driveEfficiency: number;
  regenEfficiency: number;
  heatStartC: number;
  heatKwPerC: number;
  heatBaseKw: number;
  coolStartC: number;
  coolKw: number;
  battTempCoef: number;
  surfaceFactor: Record<Surface, number>;
  uncertainty: number;
  trailerMotorway: number;   // přívěs: spotřeba navíc na dálnici / rychlostní silnici [kWh/100 km], 0 = bez přívěsu
  trailerOther: number;      // přívěs: navíc na ostatních silnicích [kWh/100 km]
  maxSpeed: number;          // horní mez plánované rychlosti [km/h] (přívěs), 0 = bez omezení
}

export function defaultEnergy(): EnergyParams {
  return { a: 9.43, b: 0.000997, cityExtra: 1.5, driveEfficiency: 0.9, regenEfficiency: 0.6, heatStartC: 15,
           heatKwPerC: 0.12, heatBaseKw: 0.3, coolStartC: 25, coolKw: 0.5, battTempCoef: 0.006,
           surfaceFactor: { sucho: 1, mokro: 1.05, snih: 1.15 }, uncertainty: 0.08, trailerMotorway: 0, trailerOther: 0, maxSpeed: 0 };
}

export interface PlanParams {
  startSoc: number;
  reserveStation: number;
  reserveDestination: number;
  profile: DriveProfile;
  mode: Mode;
  conservative: boolean;
  stopOverheadMin: number;
  valueOfTimeCzkH: number;
  preferredBonusMin: number;
  onlyPreferred: boolean;
  minStationKw: number;
  defaultPriceKwh: number;
  batteryTempC: number | null;
  energyFactor: number;
  idealKwMin: number;        // ideální výkon stanice (Voyah ~89 kW) — jemný bonus ve vyváženém režimu
  idealKwMax: number;
  idealBonusMin: number;     // 0 = vypnuto
  maxDetourKm: number;       // stanice s delší zajížďkou se nepoužijí
}

export function planParams(startSoc: number, extra: Partial<PlanParams> = {}): PlanParams {
  return { startSoc, reserveStation: 10, reserveDestination: 15, profile: "standard", mode: "nejrychlejsi",
           conservative: false, stopOverheadMin: 4, valueOfTimeCzkH: 300, preferredBonusMin: 5,
           onlyPreferred: false, minStationKw: 0, defaultPriceKwh: 19, batteryTempC: null, energyFactor: 1,
           idealKwMin: 75, idealKwMax: 100, idealBonusMin: 0, maxDetourKm: 99,
           ...extra };
}
