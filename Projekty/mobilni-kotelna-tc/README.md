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
