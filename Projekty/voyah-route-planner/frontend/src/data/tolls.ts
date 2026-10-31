/**
 * Dálniční známky a mýtné podle zemí na trase (osobní auto do 3,5 t), stav 31. 10. 2026.
 * Země na trase: reverzní geokódování Photon ve vzorcích po trase (zjemnění u hranic), cache 1 rok.
 * Ceny z oficiálních webů provozovatelů, kde je to uvedeno; jinak „ověřte“. Kurzy jen orientační.
 */
import type { Route } from "../core/models";
import { Polyline, type LatLon } from "./geo";
import { requestJson } from "./http";
import { nominatimCountry } from "./nominatim";

export interface TollOption { label: string; price: number; currency: "EUR" | "HUF" | "CHF" | "PLN" | "CZK"; }
export interface TollRule {
  country: string; name: string;
  kind: "vignette" | "toll" | "free" | "paid";
  summary: string; options: TollOption[]; trailer: string; source: string; verified: string; official: boolean;
}

/** Orientační kurzy (Kč) k 31. 10. 2026 — jen pro přepočet „≈ Kč“. */
export const CZK_RATE: Record<TollOption["currency"], number> = { CZK: 1, EUR: 24.4, HUF: 0.066, CHF: 26.3, PLN: 5.75 };

export const TOLL_RULES: Record<string, TollRule> = {
  CZ: { country: "CZ", name: "Česko", kind: "paid", summary: "Dálniční známka je u vašeho vozu vyřízena (elektromobil).", options: [],
        trailer: "Přívěs do 3,5 t samostatnou známku nepotřebuje.", source: "", verified: "2026-10-31", official: true },
  SK: { country: "SK", name: "Slovensko", kind: "vignette", summary: "Elektronická dálniční známka (eznamka.sk), vázaná na SPZ.",
        options: [{ label: "1 den", price: 8.1, currency: "EUR" }, { label: "10 dní", price: 10.8, currency: "EUR" },
                  { label: "30 dní", price: 17.1, currency: "EUR" }, { label: "365 dní", price: 90, currency: "EUR" }],
        trailer: "Přívěs samostatnou známku nepotřebuje (platí jen za tažné vozidlo).",
        source: "https://eznamka.sk/sk/dialnicne-znamky/typy-a-ceny", verified: "2026-10-31", official: true },
  AT: { country: "AT", name: "Rakousko", kind: "vignette", summary: "Dálniční známka (digitální u ASFINAG); některé tunely a úseky mají zvláštní mýtné navíc.",
        options: [{ label: "1 den", price: 9.6, currency: "EUR" }, { label: "10 dní", price: 12.8, currency: "EUR" },
                  { label: "2 měsíce", price: 32, currency: "EUR" }, { label: "rok", price: 106.8, currency: "EUR" }],
        trailer: "Přívěs se pokrývá známkou tažného vozu (ověřte u ASFINAG).",
        source: "https://www.asfinag.at/maut-vignette/vignette/", verified: "2026-10-31", official: true },
  HU: { country: "HU", name: "Maďarsko", kind: "vignette", summary: "Elektronická známka e-matrica, kategorie D1 (osobní auto).",
        options: [{ label: "1 den", price: 5550, currency: "HUF" }, { label: "10 dní", price: 6900, currency: "HUF" },
                  { label: "měsíc", price: 11170, currency: "HUF" }, { label: "rok", price: 61760, currency: "HUF" }],
        trailer: "Přívěs: kategorie U za stejnou cenu jako D1 — zda je u osobního auta nutná, ověřte u provozovatele.",
        source: "https://nemzetimobilfizetes.gov.hu/?p=3283", verified: "2026-10-31", official: true },
  SI: { country: "SI", name: "Slovinsko", kind: "vignette", summary: "Elektronická e-vinjeta, třída 2A; tunel Karavanky se platí zvlášť.",
        options: [{ label: "týden", price: 16, currency: "EUR" }, { label: "měsíc", price: 32, currency: "EUR" },
                  { label: "rok", price: 117.5, currency: "EUR" }],
        trailer: "U přívěsu se cena na webu DARS neuvádí — ověřte.", source: "https://evinjeta.dars.si/en", verified: "2026-10-31", official: true },
  CH: { country: "CH", name: "Švýcarsko", kind: "vignette", summary: "Jen roční známka (platí 1. 12. 2025 – 31. 1. 2027), i elektronicky.",
        options: [{ label: "rok", price: 40, currency: "CHF" }],
        trailer: "Přívěs potřebuje vlastní známku (dalších 40 CHF).", source: "https://www.skrblik.cz/cestovani/cestovani-autem/dalnicni-znamka-svycarsko-cena-kde-koupit-placene-useky/",
        verified: "2026-10-31", official: false },
  PL: { country: "PL", name: "Polsko", kind: "toll", summary: "Placené jen koncesní úseky: A1 Rusocin–Nowa Wieś, A2 Świecko–Konin, A4 Katowice–Kraków (brány / aplikace Autopay).",
        options: [{ label: "A1", price: 29.9, currency: "PLN" }, { label: "A4 (2 brány)", price: 36, currency: "PLN" },
                  { label: "A2 celý úsek (cca)", price: 138, currency: "PLN" }],
        trailer: "S přívěsem vyšší sazba — ověřte.", source: "https://mobility.autopay.eu/cs/silnicni-poplatky/polsko/", verified: "2026-10-31", official: false },
  HR: { country: "HR", name: "Chorvatsko", kind: "toll", summary: "Mýtné podle ujetého úseku v branách (karta, hotově, ENC).", options: [],
        trailer: "S přívěsem vyšší kategorie.", source: "", verified: "", official: false },
  IT: { country: "IT", name: "Itálie", kind: "toll", summary: "Mýtné podle úseku v branách (karta / Telepass).", options: [],
        trailer: "S přívěsem vyšší kategorie.", source: "", verified: "", official: false },
  FR: { country: "FR", name: "Francie", kind: "toll", summary: "Mýtné podle úseku (péage).", options: [], trailer: "", source: "", verified: "", official: false },
  DE: { country: "DE", name: "Německo", kind: "free", summary: "Osobní auta dálnice neplatí.", options: [], trailer: "", source: "", verified: "2026-10-31", official: false },
};

/** Úseky se zvláštním mýtným, které dálniční známka nepokrývá (přibližná poloha mýtné stanice). */
export const SPECIAL_TOLLS: { name: string; country: string; at: LatLon; radiusKm: number }[] = [
  { name: "A13 Brennerská dálnice", country: "AT", at: [47.196, 11.405], radiusKm: 3 },
  { name: "A10 Taurská dálnice (Tauern + Katschberg)", country: "AT", at: [47.10, 13.50], radiusKm: 8 },
  { name: "A9 Pyhrnská dálnice — tunel Bosruck", country: "AT", at: [47.585, 14.385], radiusKm: 3 },
  { name: "A9 Pyhrnská dálnice — tunel Gleinalm", country: "AT", at: [47.24, 15.06], radiusKm: 4 },
  { name: "S16 Arlberský tunel", country: "AT", at: [47.13, 10.21], radiusKm: 4 },
  { name: "A11 tunel Karavanky", country: "AT", at: [46.51, 14.07], radiusKm: 4 },
];

export interface CountryOnRoute { code: string; km: number; motorwayKm: number; }
export interface TollAdvice {
  countries: CountryOnRoute[];
  items: { rule: TollRule; km: number; motorwayKm: number; needed: boolean }[];
  special: string[];
  unknown: string[];
}

const CACHE_TTL_S = 365 * 86400;
const STEP_KM = 40;
const REFINE_KM = 4;

async function countryAt([lat, lon]: LatLon): Promise<string> {
  try {
    const d = await requestJson("https://photon.komoot.io/reverse", {
      params: { lat: lat.toFixed(2), lon: lon.toFixed(2), limit: 1 }, timeoutS: 10, cacheKind: "rev", ttlS: CACHE_TTL_S });
    return (d.features?.[0]?.properties?.countrycode || "").toUpperCase();
  } catch {
    return nominatimCountry(lat, lon);        // výpadek Photonu → Nominatim (pomaleji, 1 dotaz/s)
  }
}

/** Země podél trasy s délkou celkem a po dálnici/rychlostní silnici. Vzorky po 40 km, u hranic zjemnění na ~4 km. */
export async function routeCountries(points: LatLon[], route: Route): Promise<CountryOnRoute[]> {
  const line = Polyline.from(points);
  const total = line.lengthKm;
  const at = new Map<number, string>();
  const get = async (km: number) => { if (!at.has(km)) at.set(km, await countryAt(line.pointAt(km)).catch(() => "")); return at.get(km)!; };
  const kms: number[] = [];
  for (let k = 0; k < total; k += STEP_KM) kms.push(k);
  kms.push(total);
  const queue = [...kms];
  const worker = async () => { for (let k = queue.shift(); k !== undefined; k = queue.shift()) await get(k); };
  await Promise.all([worker(), worker(), worker(), worker()]);        // 4 souběžné dotazy, šetrně k Photonu
  // zjemnění hranic (bisekce mezi vzorky s různou zemí)
  const refine = async (a: number, b: number): Promise<void> => {
    if (b - a <= REFINE_KM || (await get(a)) === (await get(b))) return;
    const m = Math.round(((a + b) / 2) * 10) / 10;
    await refine(a, m);
    await refine(m, b);
  };
  await Promise.all(kms.slice(0, -1).map((k, i) => refine(k, kms[i + 1])));
  const sorted = [...at.entries()].sort((x, y) => x[0] - y[0]);
  const countryOf = (km: number) => { let c = sorted[0][1]; for (const [k, v] of sorted) { if (k > km) break; c = v || c; } return c; };
  const out = new Map<string, CountryOnRoute>();
  let pos = 0;
  for (const seg of route.segments) {
    const c = countryOf(pos + seg.lengthKm / 2);
    pos += seg.lengthKm;
    if (!c) continue;
    const o = out.get(c) ?? { code: c, km: 0, motorwayKm: 0 };
    o.km += seg.lengthKm;
    if (seg.roadClass === "dalnice" || seg.roadClass === "rychlostni") o.motorwayKm += seg.lengthKm;
    out.set(c, o);
  }
  return [...out.values()].map((o) => ({ ...o, km: Math.round(o.km), motorwayKm: Math.round(o.motorwayKm) }));
}

const MIN_MOTORWAY_KM = 1;      // známka se týká dálnic a rychlostních silnic

export function tollAdvice(countries: CountryOnRoute[], points: LatLon[]): TollAdvice {
  const items = countries.filter((c) => TOLL_RULES[c.code]).map((c) => ({
    rule: TOLL_RULES[c.code], km: c.km, motorwayKm: c.motorwayKm,
    needed: TOLL_RULES[c.code].kind !== "free" && TOLL_RULES[c.code].kind !== "paid" && c.motorwayKm >= MIN_MOTORWAY_KM }));
  const line = Polyline.from(points);
  const special = SPECIAL_TOLLS.filter((t) => countries.some((c) => c.code === t.country) && line.project(t.at)[1] <= t.radiusKm)
    .map((t) => t.name);
  const unknown = countries.filter((c) => !TOLL_RULES[c.code] && c.motorwayKm >= MIN_MOTORWAY_KM).map((c) => c.code);
  return { countries, items, special, unknown };
}

export const approxCzk = (o: TollOption) => Math.round((o.price * CZK_RATE[o.currency]) / 10) * 10;
export const fmtPrice = (o: TollOption) =>
  `${o.price.toLocaleString("cs-CZ", { maximumFractionDigits: 2 })} ${o.currency === "EUR" ? "€" : o.currency === "HUF" ? "Ft" : o.currency === "CZK" ? "Kč" : o.currency}`;

