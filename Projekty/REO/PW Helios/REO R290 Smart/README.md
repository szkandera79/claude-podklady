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
