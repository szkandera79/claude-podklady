/* Mobilní kotelny ThermaVera — data a výpočet celkové ceny tepla.
   Jediný zdroj čísel pro kalkulačku, modelový příklad na úvodu i tabulky v článku.
   Ceny bez DPH. Štítky: O = ověřeno (zdroj v SOURCES), I = interní vstup ThermaVera,
   P = předpoklad k ověření. Při změně cen upravit DATUM_CEN a zdroj. */

const DATUM_CEN = '22. 10. 2026';

const SOURCES = {
  nafta: { t: 'ČSÚ, průměrná cena nafty 41. týden 2026: 47,74 Kč/l s DPH (přes wattbox.cz)', u: 'https://wattbox.cz/ceny-paliv' },
  el: { t: 'Elektřina 3 000 Kč/MWh bez DPH včetně distribuce: typická smluvní, předem fixovaná cena větších odběratelů (údaj ThermaVera, 22. 10. 2026). Standardní ceníky pro domácnosti a malé odběry jsou vyšší, 5,6–6,6 Kč/kWh s DPH (TZB-info)', u: 'https://www.tzb-info.cz/ceny-paliv-a-energii/14-ceny-elektriny' },
  lpg: { t: 'CALPG: propan pro vytápění ≈ 2,4–2,9 Kč/kWh s DPH', u: 'https://calpg.cz/kolik-stoji-prechod-na-propanove-vytapeni/' },
  lto: { t: 'e-genergie: spotřební daň a vratka u LTO; NRG: koncová cena ≈ 38 Kč/l s DPH (nedatováno)', u: 'https://www.egenergie.com/ropne-produkty/extra-lehky-topny-olej/' },
  plyn: { t: 'TZB-info: ceníky plynu 2026, pásmo nad 63 MWh/rok 1 824–1 936 Kč/MWh s DPH (bez platby za kapacitu)', u: 'https://www.tzb-info.cz/prehled-cen-zemniho-plynu' },
  pelety: { t: 'oEnergetice / Česká peleta 27. 6. 2026: pelety „pod 10 Kč/kg“', u: 'https://oenergetice.cz/energetika-v-cr/vyroba-pelet-v-cr-loni-stoupla-o-dve-pct-na-538-000-tun-vyrazneji-rostl-zajem' },
  mapy: { t: 'Výkonové mapy RH X50, výpočet sezónního topného faktoru (interní model mobilni-kotelna-tc)', u: '' },
  trh: { t: 'Rešerše nájmů 10/2026: olej/LPG 50–110 kW ≈ 35–67 tis. Kč/měs. (ENERENT, Deutsche Thermo)', u: 'https://www.enerent.de/de/heizen/produkte/waermepumpe/erwlw100m-100kw' },
};

/* Sezónní topný faktor TČ podle teploty otopné soustavy (O = výpočet z výkonových map RH X50). */
const SOUSTAVY = {
  nizka:  { label: 'Nízkoteplotní (podlahové, do 45 °C)', spf: 3.08, el: 0,   tag: 'O' },
  stredni:{ label: 'Do 55 °C, řízení podle venkovní teploty', spf: 2.66, el: 0,   tag: 'O' },
  stala55:{ label: 'Stále 55 °C (např. ohřev přes výměník)', spf: 1.89, el: 0,   tag: 'O' },
  vysoka: { label: 'Nad 55 °C (např. CZT 90/70 °C)', spf: 1.89, el: 0.30, tag: 'P' },
};

/* Ceník ThermaVera [I], 10/2026, bez DPH: nájem podle sestavy RH X50, doprava a montáž vždy zvlášť.
   Výkon při −15 °C / 55 °C z výkonové mapy (24,8 kW na jednotku). */
const TC_UNIT_KW = 24.8;
const TC_SETS = [
  { units: 1, nominal: 50, rent: 50000 },
  { units: 2, nominal: 100, rent: 80000 },
];
const TC_TRANSPORT = 30000, TC_INSTALL = 50000;
const TC_ONCE = TC_TRANSPORT + TC_INSTALL;

/* Sestava a nájem pro potřebný výkon v kW. Nad 2 jednotky skládáme z kaskád 100 kW a 50 kW [P]. */
function tcSet(kw) {
  const units = Math.max(1, Math.ceil(kw / TC_UNIT_KW - 1e-9));
  const rent = Math.floor(units / 2) * TC_SETS[1].rent + (units % 2) * TC_SETS[0].rent;
  return { units, nominal: units * 50, kwCold: units * TC_UNIT_KW, rent, listed: units <= 2 };
}

/* Technologie. fuelName = název paliva, unit = jednotka paliva, kwh = kWh tepla ve palivu na jednotku, eta = účinnost,
   rent = nájem Kč/měs., once = doprava + montáž + demontáž, null = neznámé (uživatel doplní). */
const TECH = [
  { id: 'tc', name: 'Tepelné čerpadlo', short: 'TČ', fuelName: 'elektřina', unit: 'kWh', price: 3.0, priceTag: 'I', src: 'el',
    kwh: 1, eta: null, rent: 80000, rentTag: 'I', once: TC_ONCE, onceTag: 'I', ours: true,
    note: 'Elektřina přes podružné měření, platí zákazník. Potřebný přívod orientačně 3×50 A pro ≈ 50 kW.' },
  { id: 'plyn', name: 'Zemní plyn', short: 'Plyn', fuelName: 'zemní plyn', unit: 'kWh', price: 1.55, priceTag: 'O', src: 'plyn',
    kwh: 1, eta: 0.93, etaTag: 'P', rent: 45000, rentTag: 'P', once: 25000, onceTag: 'P',
    note: 'Jen kde je plynová přípojka s dostatečnou kapacitou. Platba za denní kapacitu není v ceně.' },
  { id: 'lpg', name: 'LPG ze zásobníku', short: 'LPG', fuelName: 'propan', unit: 'l', price: 15.0, priceTag: 'O', src: 'lpg',
    kwh: 6.6, eta: 0.93, etaTag: 'P', rent: 45000, rentTag: 'P', once: 35000, onceTag: 'P',
    note: 'Zásobník, jeho umístění a odstupy, ohlášení a pravidelné doplňování.' },
  { id: 'lto', name: 'Lehký topný olej', short: 'LTO', fuelName: 'LTO', unit: 'l', price: 32.0, priceTag: 'O', src: 'lto',
    kwh: 10, eta: 0.90, etaTag: 'P', rent: 45000, rentTag: 'P', once: 25000, onceTag: 'P',
    note: 'Nádrž, doplňování, spaliny a zápach u objektu.' },
  { id: 'nafta', name: 'Nafta', short: 'Nafta', fuelName: 'nafta', unit: 'l', price: 39.5, priceTag: 'O', src: 'nafta',
    kwh: 10, eta: 0.90, etaTag: 'P', rent: 45000, rentTag: 'P', once: 25000, onceTag: 'P',
    note: 'Nejčastější palivo mobilních kotelen. Doplňování a spaliny jako u LTO.' },
  { id: 'bio', name: 'Biomasa (pelety)', short: 'Pelety', fuelName: 'pelety', unit: 'kg', price: 8.3, priceTag: 'O', src: 'pelety',
    kwh: 4.6, eta: 0.85, etaTag: 'P', rent: null, rentTag: 'P', once: null, onceTag: 'P',
    note: 'Sklad paliva, zavážení, odvoz popela, komín. Nájem v ČR nemáme ověřený, doplňte nabídku.' },
  { id: 'elk', name: 'Elektrokotel', short: 'Elektrokotel', fuelName: 'elektřina', unit: 'kWh', price: 3.0, priceTag: 'I', src: 'el',
    kwh: 1, eta: 0.99, etaTag: 'P', rent: null, rentTag: 'P', once: null, onceTag: 'P',
    note: 'Potřebuje zhruba 2–3× větší elektrický příkon než TČ. Nájem doplňte podle nabídky.' },
];

/* Rozložení roční potřeby tepla na ÚT do měsíců [P], podle typických denostupňů v ČR. Leden = 0. */
const MONTH_SHARE = [0.181, 0.157, 0.136, 0.082, 0.030, 0.003, 0, 0, 0.024, 0.085, 0.133, 0.169];
const MONTHS = ['leden', 'únor', 'březen', 'duben', 'květen', 'červen', 'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec'];
const FULL_LOAD_HOURS = 2100;   /* [P] hodin plného výkonu za rok, odhad potřeby ze ztráty */
const GJ_PER_MWH = 3.6;
const VAT = 1.21;

/* Podíl roční potřeby tepla v období od startMonth po dobu n měsíců. */
function periodShare(startMonth, n) {
  let s = 0;
  for (let i = 0; i < n; i++) s += MONTH_SHARE[(startMonth + i) % 12];
  return s;
}

/* Celkový sezónní faktor TČ včetně elektrického dohřevu (podíl elShare tepla s účinností 0,99). */
function hpFactor(soustava, elShare) {
  const s = SOUSTAVY[soustava];
  const e = elShare ?? s.el;
  return 1 / ((1 - e) / s.spf + e / 0.99);
}

/* Výpočet celkových nákladů. q = potřeba tepla za období v MWh, months = délka nájmu.
   techs = TECH s případně přepsanými cenami/nájmy. Vrací pole výsledků. */
function compute({ q, months, soustava, elShare, techs }) {
  const qKwh = q * 1000;
  return techs.map(t => {
    const factor = t.id === 'tc' ? hpFactor(soustava, elShare) : t.kwh * t.eta;
    const fuel = qKwh / factor;                                   // jednotky paliva (kWh, l, kg)
    const energy = fuel * t.price;
    const rentKnown = t.rent != null;
    const rent = (t.rent || 0) * months;
    const once = t.once || 0;
    const other = (t.other || 0) * months;
    const total = energy + rent + once + other;
    return {
      ...t, factor, fuel, energy, rent, once, other, total, rentKnown,
      perMwh: q > 0 ? total / q : 0,
      energyPerMwh: q > 0 ? energy / q : 0,
      inputPerKwh: 1 / factor,                                      // jednotek paliva na 1 kWh tepla
    };
  });
}

/* Cena paliva konkurence, při které má stejné celkové náklady jako TČ. */
function breakEven(res, tcRes) {
  const fixed = res.rent + res.once + res.other;
  if (res.fuel <= 0) return null;
  return (tcRes.total - fixed) / res.fuel;
}

const fmt = (n, d = 0) => Number(n).toLocaleString('cs-CZ', { minimumFractionDigits: d, maximumFractionDigits: d });
const fmtKc = (n) => fmt(Math.round(n / 100) * 100) + ' Kč';
