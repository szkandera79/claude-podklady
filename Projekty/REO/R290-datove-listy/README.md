# REO R290 – datové listy (RH030–RH060, REO R290 Smart RH06–RH16, RH X50, RHX20 Pro, RHX30 Pro)

Jednotný set datových listů tepelných čerpadel REO HEATING R290 ve stylu vzoru
`../RH050-datovy-list/RH050-PW15-heating.html`. Každý model = 2 strany A4:
1. **Heating** – tabulka výkon / příkon / COP (35/45/55 °C, MAX/MIN, −25…21 °C) + křivky
2. **Energy label** – energetický štítek ErP (EU 811/2013)

| Model | ErP označení | Topný výkon A7/W35 max |
|---|---|---|
| RH030-PW8  | RH030-PW8-A2  | 8,9 kW |
| RH040-PW12 | RH040-PW12-A2 | 11,4 kW |
| RH050-PW15 | RH050-PW15-A3 | 14,8 kW |
| RH060-PW22 | RH060-PW22-A3 | 22,0 kW |
| RH X50 | RH X50 | 49,3 kW |
| RHX30 Pro | – (štítek zatím nedodán) | 40,0 kW |

Komerční modely **RH X50** a **RHX30 Pro** mají navíc stranu s vysokoteplotním provozem
60/65/70/75 °C (`DHi` v datech); chybějící body mimo pracovní rozsah se v tabulce tisknou
jako „–" a křivku přeruší.

## Struktura
- `src/data.js` – všechna data (jediný zdroj pravdy); `src/sheet.js` + `sheet.css` – vykreslení listu
- `src/index.template.html` – artefakt (přepínač modelů)
- `src/assets/` – logo + štítky (PNG vyrenderované z `../REO datové listy/RH 0x0 Energy Label.pdf`)
- **Logo:** `src/assets/logo-reo-heating.svg` (+ `.png`) = kopie závazného loga z `../logo/` (od 22. 10. 2026; staré
  `logo-reoheating.png` vyřazeno). Do listů se vkládá SVG jako data URI (`build.py`, `ASSETS.logo`), výška 18 mm v hlavičce.
- `build.py` → `print/*.html`, `pdf/*.pdf` (headless Chrome), `index.html` (artefakt)

## Zdroje dat
- RH030, RH040, RH060: tabulky z `../REO datové listy/RHxxx technický list SVT.pdf` (přepsáno 1:1;
  RH040 ověřeno proti `~/Downloads/RH040 heating.jpg`)
- RH050: beze změny z hotového `RH050-PW15-heating.html`
- RH X50: `../RH X50 komerční/DATA.json` (výkonový protokol výrobce), štítek z `RH X50 - REO HEATING/RH-X50-energeticky-stitek.pdf`
- RHX30 Pro: výkonová mapa `../PW Helios/PW30-DKXLRE3-H8 Performance curve.xls`; energetický štítek zatím není k dispozici
  (řada Helios 6–16 kW a 20 kW zatím nemá plné výkonové mapy — jen nominální body a KEYMARK)

**Značení:** ve výstupech se uvádí jen REO označení (RH X50, RHX30 Pro) — typové označení
původního výrobce ani název jeho řady se nikde neobjevuje.

## Srovnávací sekce v artefaktu
- **SCOP** (RHX30 Pro vs. RH X50, RH060 referenčně): KEYMARK EN 14825 + přepočet na české klima —
  data převzata z `~/Claude/Projekty/porovnani-x50-rh060/src/keymark_model.py`.
- **Hlučnost** (všech 6 modelů): L_WA z ErP dat / štítků, akustický tlak z ceníků výrobce,
  odhad tlaku v odstupu 3/5/10 m dopočtený (volné pole).
Obě srovnání jsou i tiskovým listem: `src/compare.js` → `pdf/REO-R290-srovnani_REO-HEATING.pdf`
(2 strany A4, česky — na rozdíl od datových listů, které jsou v angličtině podle podkladů výrobce).
V artefaktu se stahuje tlačítkem „Srovnání SCOP + hlučnost".

## Build
    python3 build.py            # vše vč. PDF (build ověří, že žádná hodnota nepřesahuje osu grafu)
    python3 build.py --no-pdf   # jen HTML

## Rozšíření 16. 10. 2026 (artefakt REO R290 = všechny řady)
- Artefakt má 3 skupiny modelů: REO R290 (RH030–RH060), REO R290 Smart (RH06 1F, RH08–RH16 3F), komerční (RHX20 Pro,
  RHX30 Pro, RH X50). Hlučnost se zobrazuje pro skupinu vybraného modelu.
- Smart + RHX20 Pro: data generuje `build.py` z `../PW Helios/REO R290 Smart/data/vykonove-mapy.json` (pole `SMART`,
  hluk z formulářů EU 811/2013 a technického listu 10/2026); RHX30 Pro zůstává v `src/data.js`.
- Štítky Smart/RHX (`src/assets/label-RH06…RHX30.png`) = PNG z `../PW Helios/REO R290 Smart/registrace/A_REO-HEATING/energeticke-stitky/`.
- PDF datových listů a dokumenty (`navody/` – návod RH030–RH060, prezentace RHX20/30 Pro) se publikují jako samostatné
  soubory artefaktu (`files`), stránka je stahuje přes `fetch` + capability downloads.
