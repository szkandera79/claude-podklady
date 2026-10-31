/** Ceník nabíjení (public/data/ceniky.json, generuje backend/tools/ceniky_zdroj.py, denně kontroluje update_prices.py).
 *  V telefonu: poslední stažená verze v IndexedDB → funguje i offline (označeno jako „poslední známé“). */
import { idbGet, idbPut } from "../local/idb";

export type PriceKind = "AC" | "DC" | "HPC";
export interface PriceTier { kind: PriceKind; from_kw: number; to_kw: number | null; price: number; price_min: number; after_min: number | null; }
export interface PriceEntry {
  id: string; operator: string; country: string; region: string; payment: string; plan: string; membership: boolean;
  fee_month: number; currency: string; vat_included: boolean; tiers: PriceTier[]; source: string; verified: string;
  status: string; note: string;
}
export interface PriceSource { name: string; url: string; checked: string; changed: string | null; }
export interface PriceList {
  generated: string; checked?: string; stale_after_days: number; currency_note: string;
  sources: Record<string, PriceSource>; entries: PriceEntry[];
}
export interface LoadedPrices { list: PriceList; fetchedAt: number; offline: boolean; }

const KEY = "ceniky";
export const PRICE_REFRESH_MS = 20 * 3600 * 1000;      // kontrola ~1× denně

export async function storedPrices(): Promise<LoadedPrices | null> {
  return (await idbGet<LoadedPrices>("kv", KEY)) ?? null;
}

/** Stáhne aktuální ceník; bez sítě vrátí poslední uložený (offline = true). Nikdy neblokuje plánování. */
export async function loadPrices(force = false): Promise<LoadedPrices | null> {
  const old = await storedPrices();
  if (!force && old && Date.now() - old.fetchedAt < PRICE_REFRESH_MS) return { ...old, offline: false };
  try {
    const r = await fetch("/data/ceniky.json", { cache: "no-cache" });
    if (!r.ok) throw new Error(String(r.status));
    const fresh: LoadedPrices = { list: await r.json(), fetchedAt: Date.now(), offline: false };
    await idbPut("kv", KEY, fresh);
    return fresh;
  } catch {
    return old ? { ...old, offline: true } : null;
  }
}

const days = (iso: string) => (Date.now() - new Date(iso + "T12:00:00").getTime()) / 86400000;
export const fmtDate = (iso: string) => (iso ? new Date(iso + "T12:00:00").toLocaleDateString("cs-CZ") : "—");

/** Stav údaje pro zobrazení: neověřené a zastaralé ceny se nikdy netváří jako aktuální. */
export function entryState(e: PriceEntry, l: PriceList): { label: string; ok: boolean } {
  if (e.status !== "ověřeno") return { label: e.status, ok: false };
  if (!e.verified || days(e.verified) > l.stale_after_days) return { label: `staré — ověřeno ${fmtDate(e.verified)}`, ok: false };
  return { label: `ověřeno ${fmtDate(e.verified)}`, ok: true };
}

/** Výkonová pásma ceníku → pásma tarifu planneru (jen DC/HPC; Voyah plánuje jen rychlonabíjení). */
export function tariffTiers(e: PriceEntry): { from_kw: number; price: number; price_min: number; after_min: number }[] {
  return e.tiers.filter((t) => t.kind !== "AC").sort((a, b) => a.from_kw - b.from_kw)
    .map((t, i) => ({ from_kw: i === 0 ? 0 : t.from_kw, price: t.price, price_min: t.price_min || 0, after_min: t.after_min ?? 9999 }));
}
