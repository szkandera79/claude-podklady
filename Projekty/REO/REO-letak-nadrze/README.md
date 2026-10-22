# REO HEATING — Katalog nerezových nádrží

Tiskový katalog akumulačních a zásobníkových nádrží ve značce **REO HEATING**.
Vznikl přeznačením cizího anglického katalogu; **v materiálu nesmí zůstat žádná
zmínka o původním výrobci nádrží** (název, modelové kódy `WK*`, čínské popisky
hrdel, výrobní štítky na fotkách).

## Soubory
- `letak.html` — zdroj, jeden soubor, A4 na výšku, interní CSS, bez JS.
- `REO_HEATING_Katalog_nadrzi.pdf` — vyexportovaný tisk (10 stran).
- `obrazky/` — fotky a řezy nádrží (PNG, 350 dpi, retušované).
- V dokumentu se **nepoužívá `mix-blend-mode`** — do PDF se ukládá jako průhledná
  skupina a některé prohlížeče i tiskové RIPy ji nevykreslí. Všechny podklady leží
  na bílé, takže prolnutí není potřeba. Kontrola po buildu: počet `/Group` objektů
  v PDF musí být 0.
- `logo-reo-heating.svg` / `logo-reo-heating-white.svg` — **závazné logo REO HEATING
  (od 22. 10. 2026)**, kopie z `../logo/` (tam README, build a PNG). Při změně loga
  zkopírovat znovu odtud. Bílá varianta jen na tmavé/zelené podklady.
- **ZASTARALÉ, nepoužívat:** `build-logo.py` + `logo-reoheating.svg` / `logo-reoheating-white.svg`
  (vlastní kreslená napodobenina „REOHEATING S.R.O.“ podle vzoru Riva Trade). Od 22. 10. 2026
  nahrazeno logem z `../logo/`; soubory ponechány jen jako archiv.
- `logo-reo*.png` — starší modré logo `RH`. V tomto katalogu se už nepoužívá.

## Build PDF
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="REO_HEATING_Katalog_nadrzi.pdf" \
  --virtual-time-budget=8000 "file://$PWD/letak.html"
```

## Struktura stran
1. Obálka · 2. Přehled řady · 3. REO AN (akumulace) · 4. REO ZV (vlnitý výměník)
· 5. REO ZH (zesílený hladký výměník) · 6. REO ZD (dva výměníky) · 7. REO KN (2 v 1)
· 8. REO ZS (solární) · 9. Zakázková výroba · 10. Kontakt

## Konvence
- **Paleta = přesně paleta www.thermavera.cz** (uživatel ji chce sdílenou; zelenožlutý
  banner REOHEATING je z ní vyrobený). Zdroj pravdy: `~/Claude/Projekty/thermavera-web/index.html`
  `:root`, potvrzeno i v `~/Claude/banner-generator/configs/thermavera.ts`:
  `--green:#2E6B33` (nadpisy), `--green-bright:#5BA32E` (akcent, eyebrow, čísla),
  `--green-tint:#EAF4DE` (podbarvení), `--amber:#FCC83C` (štítky, CTA, linka
  u poznámek), `--amber-deep:#EAAE1C`, `--cta-text:#241603`, `--ink:#16201C`,
  `--body:#5F6B64`, `--line:#E6EEE0`, `--soft:#F5F9F1`, bílá základna.
- Dokument je **světlý a vzdušný jako thermavera.cz** — žádné tmavé pruhy.
  **Obálka je celá bílá** (uživatel zelený pás za nádržemi odmítl), zakončená
  jen 5mm linkou v `--green-bright`. Kontaktní strana má spodní pás v `--green-tint`.
- Typografie Avenir Next jako v `../REO-katalog-instalaci/katalog.html`.
- Modelové kódy jsou vlastní značení REO (`AN / ZV / ZH / ZD / KN / ZS` + objem).
  V původním podkladu žádné kódy nádrží nebyly, jsou nově zavedené.
- Na produktových stranách je **řez vždy větší než vnější pohled** (přání uživatele):
  `.pics figure:nth-child(1)` = fotka, šířka 20 mm; `:nth-child(2)` = řez, šířka 32 mm.
- Tabulky jsou proti originálu **transponované**: společné parametry jsou
  v bloku „Provedení", tabulka „Parametry" má na řádku model.
- Technické hodnoty drž shodné s podkladem výrobce. Nikde negarantovat
  úspory ani životnost. U každého produktu ponechat poznámku o orientačnosti údajů.
- **Neuvádět zemi ani firmu, kde se nádrže vyrábějí.**

## Retuš fotek
Fotky pochází z podkladu výrobce a byly zbaveny výrobních štítků a čínských
popisků hrdel (skript v pracovní složce sezení: detekce světlých destiček
a přebarvení svislou interpolací z čistého řádku nad štítkem). Při výměně fotek
za nové vždy zkontrolovat, zda na plášti nezůstal štítek.

## TODO
- Doplnit reálnou fotku instalované nádrže v kotelně REO (místo studiové fotky
  výrobce) — až bude k dispozici.
- Zvážit anglickou mutaci pro export.

## Webová verze (artefakt)
- `web/build_web.py` + `web/web.css` — z `letak.html` udělá jednu responzivní stránku
  (fotky jako JPEG data URI, bez tiskových patiček). Spuštění z této složky:
  `python3 web/build_web.py . /cesta/katalog-nadrzi.html`
- Publikováno jako artefakt https://claude.ai/artifact/EPYT2QCFdGPg3cduyU1vGL (2026-10-15).
  Po změně `letak.html` přegenerovat a znovu publikovat na stejnou URL.
  **22. 10. 2026: nové logo v `letak.html` i `build_web.py`, artefakt přepublikován (verze 2).**
