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
- **Nájem TČ 70 000 Kč/měs. + 90 000 Kč** (pracovní ceník) dává při výchozích cenách TČ celkově jen o ≈ 2 % levněji
  než nafta a dráž než LTO, LPG a plyn (modelový příklad 50 kW, říjen–březen). Rozhodnout cenu před zveřejněním.
- Nájmy konkurence 45 000 Kč/měs. = střed veřejných ceníků (P); pelety a elektrokotel bez ověřeného nájmu.
- Cena plynu bez kapacitní platby; pelety „pod 10 Kč/kg“ = horní mez (ověřit u dodavatele).
- Rozložení potřeby do měsíců a 2 100 h plného výkonu jsou předpoklady.
- Formulář je demo → napojit na `odeslat.php` (jako thermavera-web). i18n EN/DE/PL zatím není.
- Doména / umístění (vlastní doména vs. thermavera.cz/mobilni-kotelny/), název služby, fotky TČ kotelny
  (stávající fotky mobilních kotelen jsou kotle na biomasu/olej → pro TČ nepoužívat).
- Hluk RH X50 na webu neuvádět, dokud není jasné, zda ≤ 62 dB(A) je Lp nebo Lw.
