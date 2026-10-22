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
- `assets/style.css`, `assets/site.js`: společné styly (paleta thermavera.cz) a menu/formulář.

## Náhled
Konfigurace `mobilni-kotelny-web` v `.claude/launch.json` servíruje kopii ve scratchpadu (iCloud složku
python http.server neotevře). Po úpravě zkopírovat: `rsync -a --delete mobilni-kotelny-web/ <scratchpad>/site/`.

## Otevřené body
- **Ceník TČ (22. 10. 2026, I):** 1× RH X50 (50 kW nom., 24,8 kW při −15 °C) 50 000 Kč/měs., kaskáda 2× (100 kW nom.)
  80 000 Kč/měs., doprava 30 000 + montáž 50 000 Kč vždy zvlášť (`TC_SETS`, `tcSet()` v calc-core.js). Nad 2 jednotky
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
- Hluk RH X50 na webu neuvádět, dokud není jasné, zda ≤ 62 dB(A) je Lp nebo Lw.
