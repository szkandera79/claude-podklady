# Rozšíření VOYAH TRASY — analýza a implementační plán (31. 10. 2026)

Stav: **schváleno a implementováno 31. 10. 2026** — výsledná zpráva (fáze E) na konci dokumentu.

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
- **Výsledek ověření (31. 10.):** stránka artefaktu má CSP, která blokuje veškerá síťová volání mimo vlastní soubory
  (fetch/XHR na ORS, Overpass, OCM, Open-Meteo, Photon i mapové dlaždice) a GPS není mezi dostupnými schopnostmi.
  → Plánovač v artefaktu běžet nemůže. Artefakt = **rozcestník** (otevření aplikace na Netlify jedním klepnutím
  z jakéhokoli zařízení, návod na instalaci) + **Ceník nabíjení** (data přibalená k artefaktu, publikují se se stejným `ceniky.json`).

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

## E. Výsledná zpráva (31. 10. 2026)

### Implementováno
| Funkce | Kde | Poznámka |
|---|---|---|
| Ideální výkon 75–100 kW (bonus ve vyváženém režimu), max. zajížďka 8 km, slabší stanice jen penalizované | `core/optimizer.ts`, nastavení | bonus omezen na 0,75 × režie zastávky (oprava: bonus dřív mohl vytvořit zbytečnou zastávku navíc; i v Python jádru) |
| Povinná stanice v plánu (`requiredStationId`) | `core/optimizer.ts` | základ výměny stanice a záloh |
| 2 záložní nabíječky ke každé zastávce + levnější alternativa | `core/alternatives.ts`, `local/worker.ts` (Web Worker) | počítá se po zobrazení plánu, UI nečeká; v detailu zastávky „Použít a přepočítat“ |
| Výběr místa při více shodách (jiná obec / okres / kraj / země) | `data/geocode.ts`, `PlanScreen` | městské části a podniky stejného jména se nenabízejí; výběr se pamatuje |
| Najít náhradní nabíječku (s cestou i bez ní) | `service.nearbyChargers`, `NearbySheet` | GPS → stanice do 40 km → silniční vzdálenost (ORS matrix / OSRM / offline odhad) → SOC při příjezdu, cena dle tarifu, čas do cíle; navigace Apple/Google; přesměrování poloha → stanice → původní cíl |
| Aktivní asistent | `service.assist`, `TripScreen` | GPS + rozsvícený displej, ETA, odhad SOC, riziko dojezdu, mimo trasu > 3 km 2 min → nabídka přepočtu, u nabíječky výzva k SOC, připomenutí SOC po 30 min / 50 km; trasu přepočítává jen na události |
| Ekonomické upozornění (výchozí 100 Kč, nastavitelné, vypínatelné) | `components/Alerts.tsx` | plán i cesta; nic se nemění bez potvrzení |
| Záložka Ceník nabíjení | `components/PriceScreen.tsx`, `data/prices.ts`, `public/data/ceniky.json` | 29 položek: PRE (Start/Silver/Gold/jednorázově), E.ON, roaming čipem PRE v ČR a 9 dalších zemích; AC/DC/HPC, stání, zdroj, datum ověření; filtry země / provozovatel / výkon / platba |
| Denní kontrola ceníků | `backend/tools/update_prices.py`, `scripts/install-ceniky-launchd.sh` | launchd 6:30 (kopie mimo iCloud — macOS ho do iCloud Drive nepustí); beze změny zdroje → nové datum ověření; změna → „zdroj změněn — ověřit“ + upozornění v macOS |
| Ceník → tarify planneru | `service.applyPriceList`, migrace tarifů v3 | jen tarify „z ceníku“ a jen ověřené ceny ≤ 30 dní; ručně upravené se nepřepisují |
| Oprava tarifu PRE Start | výchozí tarify v3 | DC 9,91 Kč + stání 1,65 Kč/min po 60 min, UFC 11,57 Kč + 1,65 Kč/min po 30 min (dříve bez poplatku za stání) |
| Offline příprava po naplánování | `service.prepareOffline` | zálohy všech variant, dlaždice stanic okolo zastávek, ceník → IndexedDB |
| Nastavení | `SettingsScreen` | ideální výkon, max. zajížďka, asistent, interval výzvy SOC, upozornění + hranice, auto-aktualizace ceníků, offline data |
| Artefakt „Voyah trasy“ | `artefakt/voyah-trasy.html` (`scripts/build-artifact.py`) | spuštění aplikace z jakéhokoli zařízení + ceník; https://claude.ai/artifact/9LSdmfRW8jpyzTdxC3nnEg |
| Sestavení a nasazení | `scripts/deploy-netlify.sh` | sestaví, kontroluje, že v balíku nejsou klíče, zip; s tokenem Netlify nasadí sám |

### Testy
- TypeScript: 63 testů (nové: povinná stanice, nedosažitelná povinná stanice, max. zajížďka, bonus nepřidá zastávku,
  2 dosažitelné zálohy bez původní stanice, rychlost záloh < 300 ms, PRE se stáním, migrace v2 → v3 se zachováním ručních úprav,
  ceník přepisuje jen navázané a čerstvé ceny). Python: 52 testů; golden (křížová kontrola Python × TS) přegenerován po úpravě bonusu.
- Náhled (Mac): výběr místa „Nová Ves“ (8 obcí), „Praha“ / „Ostrava“ jednoznačné; zálohy a výměna stanice (+12 min / +33 Kč dle zálohy);
  náhradní nabíječka se simulovanou GPS u Olomouce (6 stanic, ORS vzdálenosti, 0,8 s, čas do cíle); přesměrování přes stanici;
  asistent (ETA, odhad SOC, výzva k SOC); levnější alternativa (E.ON, úspora ~700 Kč, +5 min ve variantě Nejrychlejší).
- Výkon: opakované plánování Vendryně → Praha 0,25 s (před rozšířením 0,4 s), první 1,9 s; optimalizátor 4 varianty 1 500 km / 400 stanic 0,3 s.

### Omezení
- Stav baterie z vozu: veřejné API Voyah neexistuje → ruční zadání + odhad z modelu.
- Obsazenost / živý stav stanic: žádný volný zdroj; jen příznak „v provozu (dle OCM)“.
- Asistent běží jen při otevřené aplikaci (iOS webové aplikaci na pozadí polohu nedává); GPS na skutečném iPhonu nevyzkoušena.
- E.ON vlastní ceník: jen z článku, DPH nejasné → „neověřeno“; noční sazby se nemodelují. Tesla a ČEZ (vlastní aplikace) bez ověřeného ceníku.
- Denní kontrola pozná změnu zdroje, nové ceny ale nevyčte sama — doplní se do `backend/tools/ceniky_zdroj.py` (požádat Clauda).
- Automatické nasazení vyžaduje `NETLIFY_AUTH_TOKEN` a `NETLIFY_SITE_ID` v `~/.config/voyah-route-planner/.env`; do té doby zip ručně.
- Artefakt neumí plánovat (CSP blokuje vnější služby, GPS není dostupná) — slouží jako rozcestník a ceník; ceník v něm se obnoví až novým publikováním.
- Ve variantě s povinnou stanicí může plán nabít jen málo a pokračovat další zastávkou — je to optimální plán, ne chyba.

### Doplněno 31. 10. 2026 (po zprávě)
- Navigace: Google (celá trasa), **Mapy.cz** (celá trasa, až 15 zastávek, `navigate=true`), **Waze** (k další zastávce / do cíle); Apple Mapy odstraněny na přání.
- **Jízda s přívěsem** (volba v plánu): +10 kWh/100 km dálnice, +5 ostatní, plánovaná rychlost nejvýš 115 km/h — vše v Nastavení;
  taková jízda se nezapočítává do kalibrace.
- **Dálniční známky a mýtné** (`data/tolls.ts`, karta v Plánu i v Cestě): země na trase zjištěné na pozadí (reverzní geokódování
  Photon po 40 km, zjemnění u hranic, cache 1 rok), km po dálnici v každé zemi, ceny známek (AT, SK, HU, SI z oficiálních webů
  31. 10. 2026; CH, PL z neoficiálních zdrojů), zvláštní mýtné úseky v AT (Brenner, Tauern, Pyhrn, Arlberg, Karavanky),
  CZ = zaplaceno (elektromobil). Přepočet na Kč orientační, mýtné není v ceně cesty.
- Omezení: HR, IT, FR jen obecná informace (mýtné podle úseku); přívěs v HU / SI ověřit; kurzy pevné k 31. 10. 2026.

### Balík nabíječek rozšířen (31. 10. 2026)
- Přidány dlaždice lat 42–47, lon 9–22 (jižní Rakousko, Maďarsko, Slovinsko, Chorvatsko, sever BiH/Srbska): +2 659 stanic,
  balík nyní 101 dlaždic / 112 pokrytých, ~1,2 MB. Plán Vendryně → Budapešť 1,5 s (dřív 93 s živým Overpassem), → Zagreb 2,2 s.
- Výběr místa: obec a stejnojmenný kraj/župa do 30 km se slučují (Budapest město × župa už se nenabízí jako dvě místa).
- Omezení: Photon nezná české exonymy („Záhřeb“, „Lublaň“) — zadávejte místní název (Zagreb, Ljubljana).
- Výpadek Photonu (31. 10. odpoledne, „photon.komoot.io: nedostupné“): geokódování i země pro mýtné mají zálohu Nominatim (OSM, 1 dotaz/s,
  zná české exonymy — „Řím“, „Záhřeb“). Nominatim se použije i tehdy, když Photon obec daného jména nenajde.
- Hlášení „Ceník se změnil“ už se neukazuje, když se cena za kWh nezměnila (DC a HPC za stejnou cenu se slučují do jednoho pásma).
