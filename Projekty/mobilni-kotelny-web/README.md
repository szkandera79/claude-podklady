# Mobilní kotelny ThermaVera — web služby (prototyp)

Samostatný web služby **pronájmu mobilních kotelen s tepelnými čerpadly** pod značkou ThermaVera
(navazuje na thermavera.cz). Pracovní název služby „Teplo na čas“ zatím na webu není (čeká na rozhodnutí).
Technika a ekonomika vychází z `../mobilni-kotelna-tc/` (RH X50, kontejner 20′, ceny energií 10/2026).

## Soubory
- `index.html`: úvod (2 cesty havárie / plánovaná odstávka, cena tepla + modelový příklad, jak to funguje,
  pro koho, technika, pronájem a odkup, 3 údaje před poptávkou, FAQ, poptávka se záložkami).
- `kalkulacka.html` + `assets/kalkulacka.js`: kalkulačka celkové ceny tepla (7 zdrojů), bod zvratu ceny paliva,
  DPH přepínač, předání údajů do poptávky (`index.html?mwh=…#poptavka`).
- `cena-tepla.html`: článek „Proč nízké nájemné neznamená nízké celkové náklady“ (tabulka se počítá z dat).
- `assets/calc-core.js`: **jediný zdroj čísel** (ceny, zdroje, SPF, účinnosti, nájmy, rozložení do měsíců, výpočet).
  Štítky O = ověřeno, I = interní údaj, P = předpoklad. Při změně cen upravit `DATUM_CEN` a `SOURCES`.
- `assets/img/hero-*.jpg`: **AI vizualizace** (Gemini, banner-generator klíč) kontejneru 20′ + 2× RH X50 u paneláku,
  podniku, činžovního domu, potravinářského závodu, logistického skladu, dřevozpracujícího podniku, historické továrny,
  strojírenského závodu a hotelu (scény H1–H9); v hero se střídají strojírenský závod (antracit), hotel (krémový), logistický sklad (šedý) a potravinářský závod
  (zelený) se štítkem „Vizualizace“; `hero-strecha-hala.jpg` a `hero-strecha-panelak.jpg` = návrh jednotek na střeše kontejneru,
  také v hero (6 obrázků; varianta technicky neprověřená: přeprava zvlášť, rám do rohových kostek, servis ve výšce) (nejsou to realizace). Generuje `src/gen-hero.mjs`
  (`node mobilni-kotelny-web/src/gen-hero.mjs H1 H2 H3 --out <složka>`, reference = katalogový obrázek RH X50).
  Kontejner na obrázcích působí kratší než 20′.
- `assets/style.css`, `assets/site.js`: společné styly (paleta thermavera.cz) a menu/formulář.

## Varianty
- **Varianta 1 — samostatný web** (tato složka), navržená doména teplonacas.cz (volná 23. 10. 2026), název „Teplo na čas“.
- **Varianta 2 — integrace do thermavera.cz/mobilni-kotelny/**: návrh a skript náhledu v `integrace-thermavera/`
  (stejné stránky v hlavičce ThermaVera + úpravy homepage s překlady). Zdroj `thermavera-web/` se nemění.

## Náhled
Konfigurace `mobilni-kotelny-web` v `.claude/launch.json` servíruje kopii ve scratchpadu (iCloud složku
python http.server neotevře). Po úpravě zkopírovat: `rsync -a --delete mobilni-kotelny-web/ <scratchpad>/site/`.

## Otevřené body
- **Ceník TČ (23. 10. 2026, I):** 1× RH X50 (50 kW nom., 24,8 kW při −15 °C) 49 000 Kč/měs., kaskáda 2× (100 kW nom.)
  79 000 Kč/měs., doprava 30 000 + montáž 50 000 Kč vždy zvlášť (`TC_SETS`, `tcSet()` v calc-core.js). Nad 2 jednotky
  skládá kalkulačka z těchto sestav (P). Neupřesněno: zda doprava 30 000 je tam i zpět a zda je v montáži demontáž.
  Žádné rozlišení cen podle délky nájmu.
- **Elektřina 3 000 Kč/MWh bez DPH vč. distribuce** (zadání 22. 10. 2026, I).
- **Výsledek (říjen–březen, 55 °C ekviterm):** ztráta 24 kW → TČ 429 tis. vs nafta 485, LTO 449, LPG 411, plyn 367;
  ztráta 48 kW → TČ 658 tis. vs nafta 676, LTO 604, LPG 517. Bod zvratu nájmu proti naftě ≈ 59 tis. (1×) a ≈ 83 tis. (2×).
- Nájmy konkurence 45 000 Kč/měs. = střed veřejných ceníků (P); pelety a elektrokotel bez ověřeného nájmu.
- Cena plynu bez kapacitní platby; pelety „pod 10 Kč/kg“ = horní mez (ověřit u dodavatele).
- Rozložení potřeby do měsíců a 2 100 h plného výkonu jsou předpoklady.
- Formulář je demo → napojit na `odeslat.php` (jako thermavera-web). i18n EN/DE/PL zatím není.
- Doména / umístění (vlastní doména vs. thermavera.cz/mobilni-kotelny/), název služby, fotky TČ kotelny
  (stávající fotky mobilních kotelen jsou kotle na biomasu/olej → pro TČ nepoužívat).
- Elektro (návod RH X50 kap. 2.2/2.11): jednotka max. 20 kW / 32 A, jistič 3×40 A, vodič 10 mm²; kaskáda 2× → přívod ≈ 3×80 A.
- Hluk RH X50 na webu neuvádět, dokud není jasné, zda ≤ 62 dB(A) je Lp nebo Lw.
