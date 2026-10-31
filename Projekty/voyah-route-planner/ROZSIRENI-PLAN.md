# Rozšíření VOYAH TRASY — analýza a implementační plán (31. 10. 2026)

Stav: **návrh ke schválení** (fáze A + B). Kód zatím nebyl měněn.

## A. Analýza současného stavu

### Výkon (změřeno 31. 10. 2026, Mac, lokální náhled)
| Měření | Výsledek |
|---|---|
| Plánování Vendryně → Praha (402 km), první v sezení | 1,9 s (data z velké části v mezipaměti) |
| Totéž opakovaně | **0,4 s** |
| Optimalizátor samotný, 4 varianty: 300 km / 60 stanic | 36 ms |
| 800 km / 200 stanic | 142 ms |
| 1 500 km / 400 stanic | 305 ms (iPhone odhadem 2–3× pomaleji) |

Cíl „opakovaně do 3 s“ je dnes splněn s velkou rezervou; rozšíření ho nesmí zhoršit (těžší výpočty půjdou na pozadí).

### Co už existuje (zachovat)
| Požadavek | Stav | Kde |
|---|---|---|
| Nabíjecí křivka 89 kW do 80 %, 40 kW do 90 %, pak ~20 kW; výkon stojanu nad 89 kW nic nezrychlí | ✅ | `core/charging.ts` (min(vůz, stojan)) |
| Manipulační čas zastávky | ✅ 4 min | nastavení `stop_overhead_min` |
| Preferované sítě (PRE, E.ON, Lidl, Tesla) s prioritou | ✅ bonus ve vyváženém režimu | `optimizer.ts`, tarify |
| Uživatelské tarify s výkonovými pásmy, minutové a blokovací poplatky, DPH | ✅ | `service.ts` DEFAULT_TARIFFS, editor v Nastavení |
| Minimální výkon 0/50/75/100/150/250 kW (penalizace, ne vyloučení) | ✅ | `min_station_kw` |
| Zajížďka: energie + čas v celkovém hodnocení | ✅ (odhad 1,4 × vzdušná + 0,3 km) | `chargers.ts` |
| Celkový čas, cena, SOC při příjezdu, rezerva u nabíječky a v cíli | ✅ | DP optimalizátor |
| Varianty nejrychlejší / vyvážená / nejlevnější / eko | ✅ | `VARIANTS` |
| Ruční zadání SOC během jízdy + přepočet zbytku + kalibrace | ✅ | `TripScreen`, `service.soc` |
| Export navigace Google (celá trasa) a Apple (po úsecích) | ✅ | `nav.ts` |
| Mezipaměť: balík nabíječek OSM (8 zemí), IndexedDB cache (OCM 1 den, trasy, výšky 30 dní, počasí 1 h) | ✅ | `http.ts`, `osm.ts` |

### Co chybí
- Záložní nabíječky ke každé zastávce, funkce **Najít náhradní nabíječku**, vynucení jiné stanice s přepočtem.
- Aktivní asistent (průběžná GPS, ETA, predikce SOC bez ručního zadání, upozornění).
- Záložka **Ceník nabíjení** (Evropa, AC/DC/HPC, členství/roaming, zdroj + datum ověření) a automatická aktualizace.
- Ekonomické upozornění „levnější nabíječka, úspora X Kč“ s hranicí 100 Kč.
- Nastavení: preferované výkonové rozmezí, max. zajížďka, hranice upozornění, auto-aktualizace ceníků, offline data, zapnutí asistenta.
- Druhá fáze plánování na pozadí, příprava offline dat po naplánování, označení „poslední známé“.

### Co vyžaduje opravu / ověření
- E.ON: není ověřeno, zda ceny 9,5 / 13 / 16,9 Kč jsou s DPH; noční sazby se nemodelují.
- Python referenční jádro nemá výkonová pásma tarifů (golden testy pokrývají jen jednotnou cenu).
- `npm`/`vitest` občas nahradí symlink `node_modules` skutečnou složkou (dnes opraveno ručně) — skript to ošetří.

### Ověření zdrojů dat (zásadní omezení)
- **SOC z vozu:** veřejné API Voyah neexistuje ani není dokumentováno; oficiální aplikace Voyah (Electric Way AS) data třetím stranám neposkytuje. OBD přes Bluetooth z webové aplikace v iPhonu nejde (Safari nemá Web Bluetooth). → **zůstává ruční zadání**, zrychlené a doplněné predikcí.
- **Ceny:** veřejné cenové API v ČR/EU není. OCPI (standard tarifů) je jen mezi provozovateli a roamingovými huby; komerční agregátory jsou placené. → zdroj = **oficiální veřejné ceníky provozovatelů** (web/PDF), stahované a kontrolované automaticky (viz B5).
- **Obsazenost / živý stav:** zdarma dostupný není (PRE, E.ON, ČEZ mají jen ve vlastních aplikacích). Open Charge Map má jen příznak „mimo provoz“. → aplikace zobrazí „neznámá“ a nikdy nebude předstírat živá data.
- **Webová aplikace v iPhonu:** GPS jen když je aplikace otevřená v popředí (na pozadí iOS polohu webovým aplikacím nedává); displej lze držet rozsvícený (Wake Lock). CarPlay nelze.

## B. Technický návrh

Zásada: rozšiřovat stávající moduly, žádné paralelní řešení; UI ve stejném stylu (karty, tlačítka, spodní lišta záložek).

### B1. Výběr stanic (optimalizátor — malé úpravy)
- Ideální rozmezí 75–100 kW: **jemný bonus** (výchozí 2 min) v rozmezí; stanice < 50 kW dál penalizované (10 min), nikdy vyloučené → při nouzi je planner použije. Stanice > 100 kW bez penalizace (o výhodnosti rozhodne cena a poloha).
- Nový filtr **max. zajížďka** (výchozí 5 km) místo dnešní šířky pásu.
- Volba `requiredStationId` v DP (zastávka musí být u zvolené stanice) — základ pro výměnu stanice a pro záložní varianty. Zbytek algoritmu beze změny; golden testy musí projít.

### B2. Záložní nabíječky + výměna stanice
- Po hlavním výpočtu (fáze 2, na pozadí ve **Web Workeru**, UI neblokuje): ke každé zastávce 2 alternativy z okolí ±30 km trasy, dosažitelné s rezervou; pro každou se spočítá plán s vynucenou stanicí → rozdíl **času, ceny a SOC v cíli** proti původní.
- V detailu zastávky: „Záložní: Lidl Frýdek (+3 min, −40 Kč)“ s tlačítky Navigovat / Použít.
- „Použít“ = přepočet zbytku trasy se stejným cílem; nic se nemění bez potvrzení.

### B3. Najít náhradní nabíječku (výrazné tlačítko v záložce Cesta)
1. GPS poloha → stanice do 40 km z balíku OSM / mezipaměti (+ OCM, je-li síť).
2. Předvýběr 10 nejlepších podle vzdušné vzdálenosti → **skutečná silniční vzdálenost a čas** jedním dotazem matice openrouteservice (záloha OSRM; offline odhad označený „odhad“).
3. Filtr: dosažitelná s aktuálním SOC a rezervou. Pořadí: celkový čas do cíle + cena dle tarifu, bonus preferovaných sítí a 75–100 kW.
4. Seznam 5 stanic: vzdálenost, čas, SOC při příjezdu, cena nabití, výkon, síť, stav (je-li znám, jinak „neznámý“), zdroj dat. Tlačítka **Navigovat (Apple/Google)** a **Použít a přepočítat** (nová trasa poloha → stanice → původní cíl).

### B4. Aktivní asistent během jízdy
- Zapíná se v záložce Cesta (a v Nastavení lze vypnout); `watchPosition` + Wake Lock, jen když je aplikace otevřená.
- Při každé poloze (levné, bez přepočtu): průmět na trasu → ujeté km, **ETA**, odhad SOC = poslední zadaný SOC − modelová spotřeba × korekce jízdy.
- **Události** spouštějící přepočet (nikdy průběžně): ruční zadání SOC; odhad příjezdu k další stanici pod rezervu; odbočení z trasy > 3 km déle než 2 min; výměna stanice; dojetí na nabíječku. Mezi událostmi max. 1 přepočet / 2 min.
- Výzva „Zadejte stav baterie“ zhruba po 30 min / 50 km (jedním klepnutím odložit); rychlé zadání zůstává.
- Upozornění v aplikaci (barevný pruh nahoře + zvuk není v iOS spolehlivý → jen vizuálně).

### B5. Ceník nabíjení (nová záložka) + automatická aktualizace
- Data `ceniky.json`: provozovatel, země, (oblast), způsob platby (vlastní členství / ad hoc / roaming čipem PRE), kategorie **AC / DC / HPC** s výkonovým rozmezím, cena, měna, s/bez DPH, minutové a blokovací poplatky, **zdroj (URL)** a **datum ověření**.
- Filtry: země, provozovatel, výkon, způsob platby. Ceny vždy s měnou a údajem o DPH; přepočet na Kč jen orientačně (kurz ČNB, s datem).
- Záznam starší než 30 dní nebo neověřený = šedě „neověřeno / staré“, planner ho nepoužije jako jistý (upozornění).
- Rozsah: ČR úplně (PRE, E.ON, ČEZ, Lidl, Tesla, IONITY, Orlen, Shell, innogy, Teplárny Brno, Chargee, Greenway…) + země na vašich obvyklých trasách (SK, AT, DE, PL, HU, SI, HR) přes roaming PRE a hlavní sítě. Celá Evropa ne.
- **Aktualizace (doporučeno):** iMac 1× denně (launchd) spustí skript, který stáhne oficiální ceníky (PRE ceník + roamingový ceník PDF, E.ON, ČEZ, IONITY…), vytáhne ceny a porovná se stávajícími. Beze změny → posune datum ověření; změna → zapíše novou cenu se zdrojem; nečitelný zdroj → nechá starou cenu se starým datem (= časem „neověřeno“). Výsledek se automaticky nasadí na Netlify (Netlify CLI s tokenem uloženým jen v `~/.config/voyah-route-planner/.env`). Tím zmizí i ruční nahrávání zipu.
- Aplikace stahuje `ceniky.json` max. 1× denně na pozadí; plánování nikdy nečeká.
- Propojení s tarify: vaše tarify v Nastavení zůstávají (ručně upravené se nikdy nepřepíšou). Tarif převzatý z ceníku se při změně ceny aktualizuje s oznámením „PRE zdražilo z … na …“.

### B6. Ekonomické upozornění
- Fáze 2 a asistent porovnají celkové náklady alternativ (energie zajížďky i čas v ceně). Úspora ≥ hranice (výchozí **100 Kč**, nastavitelná, lze vypnout) → „Na trase je levnější nabíječka … úspora 140 Kč, cesta delší o 5 min. [Použít] [Ne]“. Bez potvrzení se trasa nezmění.

### B7. Dvoufázové plánování a offline
- Fáze 1 = dnešní výpočet (beze změny rychlosti). Fáze 2 ve Web Workeru: záložní stanice, levnější alternativy, širší koridor pro preferované sítě, stažení ceníku. Lepší varianta → nabídka.
- Po naplánování se uloží s plánem: stanice podél trasy, záložní stanice, poslední ceník a ceny zemí na trase → cesta funguje i bez signálu (trasa se nemění, přepočty z uložených dat).
- Platnost: stanice 30 dní (balík 1× měsíčně), ceníky 1 den, stav stanic dle OCM 1 h. Offline údaje vždy „poslední známé (datum)“.

### B8. Nastavení (doplnit jen chybějící, vše trvale v IndexedDB, zahrnuto v záloze)
Nové: preferované výkonové rozmezí (75–100 kW), max. zajížďka, hranice upozornění (100 Kč / vypnuto), automatická aktualizace ceníků, offline ukládání dat, aktivní asistent zap/vyp, interval výzvy k SOC. Stávající (preferované sítě, tarify, min. výkon, rezervy = min. SOC při příjezdu) zůstávají.

### B9. Verze v artefaktech claude.ai (přání 31. 10.)
- Cíl: stejná aplikace publikovaná jako soukromý artefakt → spustitelná odkazem z claude.ai na jakémkoli zařízení (vedle Netlify, ne místo něj).
- Sestavení `dist` je statické (JS + balík nabíječek ~0,4 MB) → limit 16 MB vyhovuje; publikace skriptem po každém sestavení.
- **Nutno nejdřív ověřit:** zda stránka artefaktu smí volat externí služby (openrouteservice, Overpass, Open Charge Map, Open-Meteo, Photon, mapové dlaždice) a používat GPS; service worker tam nejspíš nepůjde (offline režim jen na Netlify verzi). Pokud by síťová volání blokovala, varianta = artefakt jen jako rozcestník/ceník a plánovač dál na Netlify.
- Klíče: stejně jako dnes jen v úložišti zařízení (nastavovacím odkazem / QR), nikdy v artefaktu.

### Rizika
| Riziko | Opatření |
|---|---|
| Weby provozovatelů změní formát → skript ceny nepřečte | stará cena zůstane se starým datem → „neověřeno“; log + upozornění na Macu |
| Ceny Tesla jsou jen v aplikaci Tesla (per stanice) | ruční tarif, označeno „orientačně“ |
| iOS uspí webovou aplikaci na pozadí | asistent funguje jen otevřený; jasně uvedeno v UI |
| Limity openrouteservice (matice 500/den) | 1 dotaz na hledání; záloha OSRM / odhad |
| Zpomalení | těžké výpočty ve Workeru; měření před/po v testech (limit v CI testu) |

## C. Pořadí implementace (po schválení)
0. Ověřit proveditelnost artefaktu (B9) na současné verzi — krátký test, ať je jasné, pro co vše stavíme.
1. Nastavení + úpravy optimalizátoru (B1, B8) + testy.
2. Záložní stanice a výměna stanice (B2), Web Worker fáze 2 (B7).
3. Najít náhradní nabíječku (B3).
4. Aktivní asistent (B4) + ekonomické upozornění (B6).
5. Ceník: data + záložka (B5), pak denní aktualizace na iMacu + auto-nasazení.
6. Offline příprava a označení (B7).
7. Fáze D: testy (energie, dosažitelnost záloh, přepočet při změně stanice, tarify, offline, výkon první/opakovaný, regrese původních funkcí); fáze E: zpráva.

Odhad: několik pracovních sezení; každá etapa končí funkční verzí k nahrání.
