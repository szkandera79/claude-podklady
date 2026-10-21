# REO R290 Smart — návody a prezentace (REO HEATING)

**Název řady:** REO R290 Smart (nová řada, odlišení od starší REO R290 RH030–RH060). Slovo „Helios“ (název řady výrobce)
se nikde ve výstupech ani názvech souborů neuvádí. Modely: RH06–RH16 1F/3F, RHX20 Pro, RHX30 Pro.

Rebranding originálního manuálu výrobce (`../aTechnical Manual Helios Residential and Commercial.pdf`,
99 stran, anglicky) na značku **REO HEATING**.

| Originál | REO HEATING |
|---|---|
| PW06/08/10/12/14/16-DKXLRE1-H8 (1f) | RH06 … RH16 (1-phase) |
| PW08/10/12/14/16-DKXLRE3-H8 (3f) | RH08 … RH16 (3-phase) |
| PW20-DKXLRE3-H8 | RHX20 Pro |
| PW30-DKXLRE3-H8 | RHX30 Pro |
| „Seeking power world’s services“ (tabulky chyb) | „Seeking REO HEATING services“ |

Typový suffix výrobce (DKXLRE1/E3-H8) se neuvádí; 1f/3f varianty stejného výkonu rozlišuje „(1-phase)/(3-phase)“.
Titulka: šedý pruh → modelová řádka + logo REO HEATING. Přepsané jsou i záložky a metadata PDF.

- `rebrand-manual.py` → `REO-R290-Smart_navod-EN.pdf` (skript na konci sám ověří, že v textu,
  záložkách ani metadatech nezůstal odkaz na výrobce a že se jinak text stránek nezměnil)

## Ponecháno beze změny
- Číslo dokumentu `803003-3717` na titulce a čísla schémat `803004-06xx` (bez jména výrobce).
- Aplikace **Huilian Smart** / Tuya v kap. 6 — to je dodavatel ovladače a aplikace, ne výrobce jednotky;
  zákazník ji skutečně stahuje, proto zůstává.
- „PWM“ / „PWR“ ve schématech a tabulce chyb = elektrotechnické zkratky, ne značka.

## Česká verze — `REO-R290-Smart_navod-CZ.pdf`
Překlad vysázený do stejného PDF (obrázky, výkresy a schémata zapojení zůstávají; texty ve schématech zapojení
a snímky displeje/aplikace jsou dál anglicky — displej ovladače je anglický). Tabulky náhradních dílů (str. 16–18)
jsou v originále vektorové křivky → překryty novou českou tabulkou (`cz/nahradni-dily.json`).

Postup (složka `cz/`, spouštět v ní):
1. `extract.py` → `segments.json` (odstavce/buňky + prostor pro sazbu), `chunks/` k překladu
2. překlad: `cs/chunk_*.json` podle `PREKLAD-ZADANI.md` (terminologie); `cs_v2_reused.json` = 1. kolo přemapované na aktuální id
3. `icons_extract.py` + `icons_tokens.py` → ikony v řádcích textu se přesunou za přeložený text
4. `build.py` → PDF (ruční úpravy v `OVERRIDE`, popisky v `CAPTIONS`)

K revizi: kap. 1.2 bod 4 originálu tvrdí „žádné riziko výbuchu/požáru" — u R290 (propan) sporné, doporučuji
v obou jazycích upravit; v originále je dvakrát kapitola 6.6 (Vzhled rozhraní / Sdílení zařízení).
Artefakt s oběma verzemi: https://claude.ai/artifact/2DUqsPohBnVWECCKqTdYYu

## Prezentace — `prezentace/REO-R290-Smart_prezentace-CZ.pptx`
Česká verze prezentace výrobce (`../Power World R290 Helios Series Introduction.pptx`, 50 snímků), přeznačená na REO HEATING.
- Modely: PWxx-DKXLRE1/E3-H8 → RHxx 1F / 3F (1F = 230 V, 3F = 400 V); PW20/PW30 → RHX20 Pro / RHX30 Pro.
- Šablona: loga výrobce → logo REO HEATING, modrá → zelená #2E6B33, titulní pozadí přebarvené.
- Snímek 2 (typové označení) a 4 (přehled vlastností) postaveny znovu — originál obsahoval rozklad kódu výrobce,
  čínský diagram řady a srovnání s jinými řadami výrobce. Vložené OLE objekty (Excel/PPT výrobce) odstraněny.
- Obrázky: logo z fotky a výkresu jednotky odstraněno, čínské popisky oříznuty, infografika §14a EnWG česky.
- Postup: `extract.py` → překlad `cs/` (zadání `PREKLAD-ZADANI.md`) → `images.py` → `build.py` → `check.py` (struktura).
- PDF: `REO-R290-Smart_prezentace-CZ.pdf` = export z Microsoft PowerPointu (`export_pdf.py`, přes sandbox
  kontejner PowerPointu). Po buildu spustit `fix_icons.py` (posune ikony v textu do mezer podle skutečné sazby
  PowerPointu), pak `export_pdf.py`. Celý řetězec:
      python3 build.py && python3 fix_icons.py && python3 check.py REO-…-CZ.pptx && python3 export_pdf.py REO-…-CZ.pptx REO-…-CZ.pdf
- `render_pdf.py` (Quick Look + Chrome) nepoužívat — u této prezentace zaměňuje obrázky mezi snímky i u originálu.

## Letáky — `letaky/`
Dva prodejní letáky A4 (2 strany), generované `letaky/build.py` (HTML → PDF přes headless Chrome):
- `REO-R290-Smart_letak-zakaznici.pdf` — jednoduchý, pro koncové zákazníky (bez jmen konkurence).
- `REO-R290-Smart_letak-partneri.pdf` — technický, pro instalační partnery (tabulka parametrů, integrace, FV DC,
  anonymní srovnání SCOP s trhem: 4 značkové R290 monobloky 8–12 kW, LG/Viessmann/NIBE/Stiebel, stav 10/2026).
Data jsou v poli `M` v build.py (spec. výrobce). Fotka jednotky = `prezentace/media_out/image6.png` (přeznačená).
Obsahové mantinely: žádné garance úspor; „tišší než konkurence“ NEtvrdit (L_WA 50–59 dB(A) je nad LG/NIBE/Stiebel);
max. teplota vody 75 °C (prezentace výrobce uvádí 78 °C — nepoužívat).
Prodej jen ve variantě výrobce „s integrovaným hydroboxem“ (= el. dohřev 3 kW + exp. nádoba 6 l + pojistný ventil 3 bar
ve venkovní jednotce; čerpadlo má i varianta bez). Pro Smart NEpoužívat slovo „hydrobox“ (koliduje s vnitřním REO Hydroboxem
REO-03H/05H) a netvrdit, že nahrazuje vnitřní hydraulické zapojení (trojcestný ventil TUV, filtr, armatury, zásobník, akumulace).
Nabízí se RH06 1F (6 kW, jen jednofázový) + třífázové RH08–RH16 3F (+ RHX20 Pro / RHX30 Pro); ostatní 1F verze se neuvádějí → max. SCOP 35 °C = 5,29 (RH14 3F).
Artefakt Marketing REO HEATING (náhledy + PDF): https://claude.ai/artifact/8zGFmzL6gnPFsy8zTqRjGz — po změně letáků přenahrát (scratchpad/marketing nebo nová kopie).
V zákaznické tabulce: jmenovitý výkon (≈ tepelná ztráta domu) + max. výkon A7/W35. Ilustrace „topí přímo ze slunce“ = `letaky/ilustrace.py` (SVG).

## Výkonové mapy a datové listy (13. 10. 2026)
Výrobce dodal výkonové mapy (`../R290 Helios Performance Curve/*.xls`, část i PDF): 7 teplot vody 35–75 °C ×
15 venkovních teplot −25…+20/21 °C, MAX/MIN (RHX i „Standard“), + chlazení W7/W18 a ohřev TUV.
- `data/parse_maps.py` → `data/vykonove-mapy.json` (všechny mapy, REO označení). Mapy 1F a 3F jsou u RH08/RH10
  společné; RH16 1F vs 3F se liší jen u W55+ při nízkých teplotách (< 1 kW).
- `datove-listy/build.py` → `datove-listy/pdf/<model>_Heating_REO-R290-Smart.pdf` (2 strany A4, anglicky:
  35/45/55 °C + 60–75 °C). Vzhled sdílí `../../R290-datove-listy/src` (sheet.js, sheet.css, logo).
  Modely: RH06 1F, RH08–RH16 3F, RHX20 Pro, RHX30 Pro. Publikováno v artefaktu Manuály.
- Chybí mapy RH12 1F a **RH14 3F** (datový list RH14 3F zatím z mapy RH14 1F) a RH08/14 v PDF.
- Anomálie v datech výrobce (ponecháno 1:1): RH10 W45 MAX při +21 °C příkon 2,78 kW → COP 4,78 (při +15 °C 3,69).
- Energetické štítky v listech zatím nejsou (štítky výrobce v `../Helios Energy Label and ERP report.zip` nesou
  jeho značku a kódy → nutný rebrand jako u RH X50).

## Video — `video/REO-R290-Smart_video-CZ.mp4`
Česká verze produktového videa výrobce (`../Power World Helios Video.mp4`, 1:50, 1080p60), přeznačená na REO HEATING.
- Logo výrobce vlevo nahoře → bílá deska s AI logem REO HEATING; nápis na horní liště jednotky → „REO HEATING“;
  logo vyražené na vzornících panelů zakryto; závěrečná karta vlastní (logo, „REO R290 Smart“, www.reoheating.cz).
- Titulky → spodní lišta (zelený proužek, česky). Infografiky (Proč R290, únik chladiva, ekvitermní křivky, FV schéma,
  řízení odběru) přestavěny česky ze statických snímků originálu. Snímek „§14a EnWG“ (německý předpis) nahrazen
  českým obsahem o napájení ze sluníčka / doplnění ze sítě / Smart Grid Ready.
- Obsahové úpravy proti originálu: „built-in hydraulic module“ → „integrovaný záložní dohřev 3 kW a pojistná výbava“;
  „SCOP > 5.3“ → „SCOP až 5,29 (35 °C)“; doplněny 3 pilíře (kompresor Mitsubishi Electric, „topí přímo ze sluníčka“).
- Komentář: anglický hlas odstraněn (demucs, hudba zachována), český namluven Gemini TTS (hlas Charon) po větách
  podle střihů (`vo.json`: začátek, konec, text), zrychlení max. 1,15×.
- Postup (scratch adresář s `ffmpeg` z pip `imageio-ffmpeg`, `src/in.mp4`, stillsy `still/s<čas>.png`):
  `tts.py` → `render.py <scratch>` (obraz; `--preview 12,50` = náhledové snímky) → mix zvuku a mux přes ffmpeg.
  `track.json` = sledovaná poloha popisků přípojek (49–54 s).

## Prezentace RHX20 Pro / RHX30 Pro — `prezentace-komercni/REO-R290-Smart_RHX20-RHX30-Pro_prezentace-CZ.pptx` (+ PDF)
Česká verze prezentace výrobce pro lehké komerční použití (`../R290 Cleanlife Ultra- Light Commercial HP Introduction 20kw 30kw.pptx`,
44 snímků), přeznačená na REO HEATING. Název řady výrobce („Cleanlife Ultra“) se nikde neuvádí.
- Modely: PW20/PW30-DKXLRE3-H8 → RHX20 Pro / RHX30 Pro; snímky 37–38 (vnitřní deska menších jednotek) → RH06–RH16.
- Šablona, pozadí, §14a infografika a IoT diagram převzaty z prezentace RH06–RH16 (`../prezentace/media_out`).
- Nový snímek 5 „Výkon při −15 °C“: max. topný výkon a COP min–max (při max. / min. výkonu) RHX20 Pro / RHX30 Pro při A−15/W35 a A−15/W55 z `../data/vykonove-mapy.json`
  + upozornění, že číslo v označení není výkon v mrazu (vkládá se na konci build.py → `fix_icons.py` má čísla snímků +1).
- Barvy (14. 10.): zelená **#34A263** = světlejší varianta `--brand #26804B` z webu reoheating.cz (uživatel chtěl světlejší),
  podklad `--brand-light #E9F6EE` (dříve #2E6B33).
- Titulní a závěrečný snímek (přání uživatele 14. 10.): bílé pozadí, zelené písmo, barevné logo.
- Infografika R290 (sn. 4) v zelené: zelené R290 a štítky, dlaždice bílé se zeleným okrajem, piktogram zeleně, popisek černě;
  hodnoty 75 °C a COP 5,0 jsou přímo v obrázku (překryvy výrobce odstraněny).
- Popis displeje ovladače (sn. 20, image35): modré pozadí → bílé, popisky tmavě šedé, displej a ikony beze změny.
- Fotky jednotek (snímky 3, 7, 31, 32): nápis výrobce na horní liště → „REO HEATING“ (Exo 2 Black Italic, kovový přechod).
- Infografika R290 (sn. 4): logo výrobce v ikoně IoT odstraněno, popisky česky; ikona teploty vody 78 → **75 °C**.
- Česky přesázené obrázky: tabulka ikon ovladače, legenda hydraulického schématu, Modbus diagramy, SG schéma, popisky schématu aplikace.
- OLE: schémata zapojení (ZWCAD, sn. 34–35) → statický obrázek; Excel se seznamem parametrů (sn. 24) odstraněn (odkaz na návod).
- Náhled IoT portálu: název zařízení cizího zákazníka odstraněn. Metadata, alt texty, app.xml přepsány.
- Texty z displeje (UI), detailní popisky ve schématech zapojení a IoT diagramu zůstávají anglicky (jako u RH06–RH16).
- Postup (složka `prezentace-komercni/`, sdílí funkce s `../prezentace/common.py`):
  `extract.py` → `reused.json` (shodné texty přeložené u RH06–RH16) + `cs/chunk_*.json` (nové / opravy) → `images.py` →
  `build.py && fix_icons.py && check.py REO-…-CZ.pptx && export_pdf.py REO-…-CZ.pptx REO-…-CZ.pdf`
- Ponecháno z originálu: názvy dodavatelů komponent (Mitsubishi, Sensata, SANHUA, SAGINOMIYA, ACOL, Shinhoo, YuanZhuo, SUN WILL),
  SG ovladač Ecosoft (třetí strana), „Manufacturer Cloud Console“ v IoT diagramu (obecně „výrobce“).

## Registrace (SVT / NZÚ, EPREL) — `registrace/`
Formuláře dle (EU) 811/2013, energetické štítky a přehled modelů ve dvou variantách: **A** REO HEATING (RHxx) a **B** Power World
(PWxx, Ria Trade jako dovozce, certifikáty HP KEYMARK 041-K032-23…31). Podrobnosti a otevřené body v `registrace/README.md`.

## Katalog — `katalog/` (20. 10. 2026)
8stránkový katalog a ceník A4 `REO-R290-Smart_katalog.pdf` = redesign letáku „REO R290“ (RH030–RH060, 10/26) na řadu Smart.
`katalog/build.py` (HTML → PDF headless Chrome; ilustraci sdílí s `letaky/ilustrace.py`). Strany: titulka · 3 pilíře ·
princip „topí přímo ze sluníčka“ (FV → MPPT → DC sběrnice ← síť) · sluníčko v praxi (ilustrační den, počet panelů, FAQ) ·
účinnost (SCOP 5,29 / 3,97) · modely a ceník · technické údaje + zapojení + ovládání · zásobníky + kontakt.
Ceny = web eko4home (20. 10. 2026): RH06–RH16 129–189 tis., RHX20/30 Pro 300/350 tis. Kč bez DPH; zásobníky dle e-shopu.
SCOP 55 °C: ERP protokol výrobce 3,87–4,00 (průměrné klima) → v katalogu „až 3,97“, údaj 4,9 nemá zdroj.
Titulka (20. 10.): hero scéna jednotka Smart + REO Watertank 210/70 (`katalog/hero_scena.py` vloží Smart do předlohy
`assets/src/hero-scena-orig.webp` → `assets/hero-scena.png`); popisky a symboly (kompresor Mitsubishi Electric, TUV nahoře,
topná voda dole – podlaha/radiátory) jsou SVG v `hero_overlay()`. Build zároveň exportuje `hero-smart-watertank.png` (2×) pro web.

## Produktová brožura — `brozura/` (21. 10. 2026)
Přeznačení produktového katalogu výrobce (vydání 10/2025, 14 stran) do designu katalogu REO HEATING: 8 stran A4,
`brozura/build.py` → `REO-R290-Smart_brozura.pdf` (CSS, ikony, logo a schéma FV se berou z `katalog/build.py`).
- Modely jen RH06 1F + RH08–RH16 3F (ostatní 1F vypuštěny); data tabulky = technické údaje z katalogu výrobce.
  Pozor: liší se od dat v `katalog/` (např. RH06 COP A7/W35 4,88 vs 5,04; hmotnosti 116–190 kg; hloubka 463/470 mm) → sjednotit po potvrzení výrobcem.
- Vypuštěno: německý §14a EnWG (nahrazeno „omezení příkonu“), srovnávací stupnice hluku; přidány 3 pilíře, FV tabulka, umístění jednotky.
- Fotky `brozura/assets/*.jpg` = výřezy z katalogu výrobce bez loga (zkontrolováno); jednotka a hero z `katalog/assets`.
