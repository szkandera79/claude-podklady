/** Tarify s výkonovými pásmy a ceny bez DPH (výchozí ceníky 30. 10. 2026). */
import { describe, expect, it } from "vitest";
import { tariffForStation } from "../core/models";
import { normalizeOperator } from "../data/operators";
import { DEFAULT_SETTINGS, _internal, applyPriceList, basePrice } from "./service";

const tariffs = _internal.tariffsFrom(_internal.merged(undefined));

describe("tarify", () => {
  it("převod DPH", () => {
    expect(basePrice(12, true, true)).toBeCloseTo(9.92, 2);
    expect(basePrice(9.92, false, true)).toBe(9.92);
    expect(basePrice(10, false, false)).toBeCloseTo(12.1, 2);
  });
  it("PRE: DC vs UFC podle výkonu stanice", () => {
    const dc = tariffForStation(tariffs.PRE, 75)!;
    expect([dc.priceKwh, dc.blockingFeeMin, dc.blockingAfterMin]).toEqual([9.91, 1.65, 60]);
    const ufc = tariffForStation(tariffs.PRE, 150)!;
    expect([ufc.priceKwh, ufc.blockingFeeMin, ufc.blockingAfterMin]).toEqual([11.57, 1.65, 30]);
  });
  it("E.ON karta: pásma 0–100 / 101–200 / 201+, převedeno na bez DPH, minutový poplatek", () => {
    expect(tariffForStation(tariffs["E.ON"], 50)!.priceKwh).toBeCloseTo(7.85, 2);
    const g2 = tariffForStation(tariffs["E.ON"], 150)!;
    expect(g2.priceKwh).toBeCloseTo(10.74, 2);
    expect(g2.blockingAfterMin).toBe(60);
    expect(tariffForStation(tariffs["E.ON"], 300)!.priceKwh).toBeCloseTo(13.97, 2);
  });
  it("roaming ČEZ přes čip PRE", () => {
    const t = tariffForStation(tariffs["ČEZ"], 100)!;
    expect([t.priceKwh, t.blockingFeeMin, t.blockingAfterMin]).toEqual([15.7, 1.65, 60]);
  });
  it("názvy sítí v tarifech odpovídají normalizaci z dat", () => {
    for (const t of DEFAULT_SETTINGS.tariffs) expect(normalizeOperator(t.operator)).toBe(t.operator);
  });
  it("přechod v2 → v3: neupravené tarify se obnoví, ruční úpravy zůstanou", () => {
    const v2 = structuredClone(DEFAULT_SETTINGS.tariffs).map((t) => ({ ...t, cenik_id: undefined }));
    const pre = v2.find((t) => t.operator === "PRE")!;
    pre.tiers = [{ from_kw: 0, price: 9.92 }, { from_kw: 150, price: 11.57 }];
    const lidl = v2.find((t) => t.operator === "Lidl")!;
    lidl.tiers = [{ from_kw: 0, price: 9.5, price_min: 0, after_min: 9999 }];          // ruční úprava
    const out = _internal.migrateTariffs(v2 as any, 2);
    expect(out.find((t) => t.operator === "PRE")!.tiers![0].price).toBe(9.91);
    const l = out.find((t) => t.operator === "Lidl")!;
    expect([l.tiers![0].price, l.auto]).toEqual([9.5, false]);
  });
  it("ceník aktualizuje jen navázané a neupravené tarify", () => {
    const s = _internal.merged(undefined);
    s.tariffs.find((t) => t.operator === "ČEZ")!.auto = false;
    const today = new Date().toISOString().slice(0, 10);
    const entry = (id: string, op: string, price: number) => ({ id, operator: op, country: "CZ", region: "", payment: "", plan: "",
      membership: false, fee_month: 0, currency: "CZK", vat_included: false, source: "x", verified: today, status: "ověřeno", note: "",
      tiers: [{ kind: "DC" as const, from_kw: 50, to_kw: 149, price, price_min: 0, after_min: null }] });
    const list = { generated: today, stale_after_days: 30, currency_note: "", sources: {},
                   entries: [entry("pr-lidl", "Lidl", 11.5), entry("pr-cez", "ČEZ", 17)] };
    const r = applyPriceList(s, list);
    expect(r.changes).toHaveLength(1);
    expect(r.settings.tariffs.find((t) => t.operator === "Lidl")!.tiers![0].price).toBe(11.5);
    expect(r.settings.tariffs.find((t) => t.operator === "ČEZ")!.tiers![0].price).toBe(15.7);
    for (const e of list.entries) e.verified = "2026-01-01";                               // zastaralé → nepoužít
    expect(applyPriceList(_internal.merged(undefined), list).changes).toHaveLength(0);
  });
  it("starší uložené tarify se nahradí novými", () => {
    const old = _internal.merged({ tariffs: [{ operator: "PRE", price: 10, includes_vat: false, preferred: true, member: true, priority: 1 }] });
    expect(old.tariffs.length).toBe(DEFAULT_SETTINGS.tariffs.length);
  });
});
