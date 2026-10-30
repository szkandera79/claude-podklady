/** Tarify s výkonovými pásmy a ceny bez DPH (výchozí ceníky 30. 10. 2026). */
import { describe, expect, it } from "vitest";
import { tariffForStation } from "../core/models";
import { normalizeOperator } from "../data/operators";
import { DEFAULT_SETTINGS, _internal, basePrice } from "./service";

const tariffs = _internal.tariffsFrom(_internal.merged(undefined));

describe("tarify", () => {
  it("převod DPH", () => {
    expect(basePrice(12, true, true)).toBeCloseTo(9.92, 2);
    expect(basePrice(9.92, false, true)).toBe(9.92);
    expect(basePrice(10, false, false)).toBeCloseTo(12.1, 2);
  });
  it("PRE: DC vs UFC podle výkonu stanice", () => {
    expect(tariffForStation(tariffs.PRE, 75)!.priceKwh).toBeCloseTo(9.92, 2);
    expect(tariffForStation(tariffs.PRE, 150)!.priceKwh).toBeCloseTo(11.57, 2);
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
  it("starší uložené tarify se nahradí novými", () => {
    const old = _internal.merged({ tariffs: [{ operator: "PRE", price: 10, includes_vat: false, preferred: true, member: true, priority: 1 }] });
    expect(old.tariffs.length).toBe(DEFAULT_SETTINGS.tariffs.length);
  });
});
