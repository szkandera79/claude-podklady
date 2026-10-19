# Pronájem mobilních kotelen s TČ RH X50 v kontejneru 20'

Interní podnikatelský, technický a obchodní model: pronájem mobilních teplovodních kotelen
s tepelnými čerpadly REO HEATING RH X50 v kaskádě, místo naftových/olejových/plynových kotelen.

## Vstupy od uživatele
- RH X50: 50 kW nominál, **reálně 25 kW při −15 °C**, **110 000 Kč bez DPH**; osazuje se více jednotek do kaskády.
- Kotelna = **kontejner 20'**: akumulace, řízení a elektro uvnitř, v uzamykatelném prostoru.
- Podmínky elektrického připojení **podle návodu** (`~/Claude/REO/RH X50 komerční/RH X50 - REO HEATING/RH-X50-navod-k-pouziti.pdf`, kap. 2.2 a 2.11).
- Orientace ze zahraničí: 100 kW mobilní TČ ≈ 65 000 Kč/měsíc.

## Z návodu RH X50
3×380–400 V ±10 %, **max. 20 kW / 32 A, jistič 40 A s ochranou proti úniku proudu, vodič 10 mm²**, R290 4,0 kg,
≤ 62 dB(A), 370 kg, 1195 × 980 × 1900 mm, sání ze 4 stran ≥ 0,5 m, **výfuk nahoru ≥ 2 m volno**, ≥ 300/500 mm nad terénem,
12 h pod napětím před startem, max. 4 zapnutí/h, glykol doporučen, filtr ve zpátečce. Jednotka umí i chladit.

## Řešení (varianta B)
Kontejner 20' = technická místnost 1,84 m (AKU 1 000 l, výměník, hydraulika, rozvaděč, regulace; zamčená) + plynotěsná
přepážka + **vzduchová komora 3,96 m pro 2 jednotky** (otevřená nahoru, uzamykatelné mřížové bočnice, pororošt).
3. a 4. jednotka na skidu vedle kontejneru. Varianta „jednotky na střeše" zamítnuta (výška soupravy ≈ 6 m > 4 m).
Přívod: M25 3×50 A (CEE 63), M50 3×80 A (CEE 125), M75/M100 dva přívody.

## Soubory
- **`src/model.py`**: předpoklady a výpočty (CAPEX, elektro, SPF binovou metodou z křivek, ceník A/B/C, cena za MWh, citlivost, návratnost, hluk).
- **`src/rh_x50_krivky.json`**: výkonové křivky RH X50 (kopie `DATA.json` z podkladů REO).
- **`src/build_model.py`**: z modelu vygeneruje **`model.html`** vč. výkresu kontejneru (SVG):
  `python3 mobilni-kotelna-tc/src/build_model.py`

## Klíčové výsledky (bez DPH)
- CAPEX: M25 ≈ 0,95 mil., M50 ≈ 1,12 mil., M75 ≈ 1,43 mil., M100 ≈ 1,60 mil. Kč (kontejnerové jádro ≈ 0,77 mil.).
- SPF z křivek: 2,66 (ekviterm 50/35 °C), 1,89 (pevně 55 °C), 3,08 (40/30 °C).
- 20 MWh/měsíc: TČ M50 ≈ 4 600 Kč/MWh vs nafta ≈ 4 900; proti LTO/LPG/plynu TČ nevyhrává.
- Návratnost tržně: M50 5,8 / 3,5 roku, M100 4,4 / 2,8 roku při 6 / 9 měsících obsazenosti; při 3 měsících se nezaplatí.

## Předpoklady k ověření ([OVĚŘIT] v model.py)
Zda ≤ 62 dB(A) je Lp v 1 m; omezení příkonu (nižší jištění); souhlas výrobce s komorou a výfukovými nástavci; EN 378 a ADR pro R290;
ceny konverze kontejneru; nájmy konkurence; ceny energií.

## Artefakt
Webová verze: https://claude.ai/artifact/WbSF8WZjZjJNdHwNKWWNHc (soukromá). Po přegenerování `model.html` publikovat na stejnou URL.

## Univerzální kotelna (studie 10/2026)
Samostatná studie pro pronájem s RH X50 / RH050–060, jednotky venku: `univerzalni/` (viz její README).

## Univerzální mobilní kotelna — studie proveditelnosti (od 16. 10. 2026)
Zadání: kotelna k opakovanému pronájmu (první zákazník: administrativa + hala, ~20 osob, 6 měsíců, ÚT + TUV),
varianta A = RH050/RH060 v kaskádě, varianta B = RH X50 (+ RH050 pro TUV), kontejner 10′/20′, skladové zásobníky.
Postup v 5 fázích; **hotová fáze 1** (technická studie, kritická rizika, kontrolní seznam obhlídky).
- `src/studie_calc.py`: výkony jednotek z map (data.js), kaskády vč. N−1, bod rovnováhy, potřebná teplota otopné
  soustavy, ohřev TUV přes výměník, tlakové ztráty hadic, min. AKU, elektro, doba vychladnutí hadic.
- `src/build_studie.py` → `studie.html`: `python3 mobilni-kotelna-tc/src/build_studie.py`
- Artefakt: https://claude.ai/artifact/28JzYEi6eUNqyWW4CAkjcM (republikovat stejný soubor / přes `url`).

Hlavní zjištění: dimenzovat podle výkonu při −15 °C/W55, ne podle nominálu (2× RH X50 = 49,6 kW, po výpadku 24,8 kW);
návod RH X50 požaduje pod 0 °C glykol → doporučen glykolový primár + deskový výměník, rozdělovač/separátor uvnitř kontejneru;
RH050 ohřeje TUV přes výměník jen na ≈ 52 °C → topná vložka na sterilizaci; zásadní neznámá = teplotní spád soustavy zákazníka (CZT 90/70).
Další fáze: 2 hydraulika a regulace, 3 konstrukce a kotvení, 4 rešerše trhu a rozpočet, 5 ekonomika a smlouva.
- **Rešerše trhu (fáze 4, 16. 10. 2026)**: `src/market.html` (vkládá se do studie jako kap. 13). Kontejner: nový 20′ one-trip ≈ 62 500 Kč
  (kontik), 10′ není levnější; doprava rukou ≈ 5–12 tis./cesta. Sada hadic 2× 20 m: DN50 ≈ 45–50 tis., DN65 ≈ 60–70 tis. (CALORTEC 100 + Camlock GMS, těsnění EPDM).
  Pronájmy: v ČR žádné mobilní TČ s cenou; ENERENT TČ 105 kW ≈ 46–51 tis. Kč/měs. + 65 tis. paušál; olej/LPG 50–110 kW 35–67 tis./měs.
- **Rozpočet (fáze 4, 16. 10. 2026)**: `src/rozpocet.py` (položky se zdrojem T/Z/O, varianty Ekonomická/Univerzální × sestavy B-2/A-50,
  skladové díly, ztráta prodejní hodnoty, opotřebení za sezónu, nádrže A/B/C) → vkládá se jako kap. 14.
  Nové výdaje ≈ 1,10–1,36 mil. Kč (vč. 10 % rezervy); skladové díly účetně ≈ 0,29–0,33 mil.; ztráta prodejní hodnoty 2× RH X50 ≈ 0,48 mil.
  K doplnění od uživatele: účetní a prodejní hodnoty zásobníků TUV 300 l a skladových AKU (nyní odhad).
- **Fáze 5 (16. 10. 2026)**: `src/ekonomika.py` → kap. 15 (přímé náklady zakázky ≈ 186 tis., scénáře 50/70/90 tis., bod zvratu).
  Při 70 tis./měs. hrubý příspěvek ≈ 324 tis./zakázku, návratnost nových výdajů ≈ 4,2 zakázky (univerzální), 3,5 (ekonomická);
  ekonomická nula ≈ 69 tis./měs. Smlouva o nájmu (Claude Docs): https://claude.ai/code/artifact/4ab9fbf4-395c-48f0-97e0-f627aa43c372 — ke kontrole advokátem.
- **Rozhodnutí uživatele 16. 10. 2026:** bez hydraulického separátoru a deskového výměníku; jednotky přímo na AKU, soustava na vodu
  s protimrazovými ventily, uzávěry s pružinovým návratem a UPS. Vychází finančně zhruba stejně jako glykol; riziko vůči návodu RH X50 trvá.

## Zakázky
- **`mm-holz/`**: MM Holz / Alignum Paskov — rev1 (`mm-holz/rev1/`): 2 × RH X50 + el. bivalence 72 kW, potřeba z měření 62–69 kW; rev0: návrh 2 × RH X50 ze skladu (výkony při 55/60/70 °C, limit jednotek Sahara, otevřené body). Výpočty `python3 mobilni-kotelna-tc/mm-holz/src/sestavy.py`.
- **`univerzalni/`**: studie univerzální mobilní kotelny (fáze 1), artefakt https://claude.ai/artifact/28JzYEi6eUNqyWW4CAkjcM.
- **Artefakt „Mobilní kotelna“** (16. 10. 2026) = https://claude.ai/artifact/28JzYEi6eUNqyWW4CAkjcM, záložky Studie a ekonomika /
  Nabídky / Smlouva. Nové nabídky: řádek v `src/nabidky.py` + složka `nabidky/<slug>/` (fragment `nabidka.html`), pak
  `python3 mobilni-kotelna-tc/src/build_studie.py` a publikovat `studie.html` na stejnou URL. Rozpracováno: MM Holz.
- **Ceny energií 16. 10. 2026** (ekonomika.py, bez DPH): nafta 39,5 Kč/l (ČSÚ 47,74 s DPH), LTO ≈ 32 Kč/l, propan pro vytápění ≈ 15 Kč/l,
  elektřina pro firmy ≈ 5,0 Kč/kWh. Úspora energie proti naftě ≈ 40–57 % (≈ 180–260 tis. Kč za sezónu u 50 kW).
