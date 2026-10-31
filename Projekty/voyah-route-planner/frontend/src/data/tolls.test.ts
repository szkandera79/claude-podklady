/** Upozornění na dálniční známky a mýtné podle zemí na trase. */
import { describe, expect, it } from "vitest";
import { approxCzk, tollAdvice, TOLL_RULES } from "./tolls";

describe("dálniční známky a mýtné", () => {
  const pts: [number, number][] = [[49.65, 18.67], [48.2, 16.37], [47.0, 15.4], [46.05, 14.5]];
  it("CZ zaplaceno, AT nutná známka, SI jen po silnicích ne, DE zdarma", () => {
    const a = tollAdvice([{ code: "CZ", km: 150, motorwayKm: 120 }, { code: "AT", km: 400, motorwayKm: 380 },
                          { code: "SI", km: 80, motorwayKm: 0 }, { code: "DE", km: 10, motorwayKm: 10 }], pts);
    expect(a.items.filter((i) => i.needed).map((i) => i.rule.country)).toEqual(["AT"]);
    expect(a.items.find((i) => i.rule.country === "CZ")!.rule.kind).toBe("paid");
  });
  it("zvláštní mýtné: tunel Karavanky na trase", () => {
    const a = tollAdvice([{ code: "AT", km: 400, motorwayKm: 380 }], [[46.6, 14.0], [46.51, 14.07], [46.4, 14.15]]);
    expect(a.special.some((x) => x.includes("Karavanky"))).toBe(true);
  });
  it("neznámá země s dálnicí se nahlásí", () => {
    expect(tollAdvice([{ code: "RO", km: 50, motorwayKm: 40 }], pts).unknown).toEqual(["RO"]);
  });
  it("orientační přepočet na Kč", () => {
    expect(approxCzk(TOLL_RULES.AT.options[1])).toBe(310);
  });
});
