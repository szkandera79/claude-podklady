# Voyah Smart Route Planner — analýza a návrh (Etapa 1–2)

Stav: **návrh ke schválení** · 30. 10. 2026 · nic se zatím neprogramuje.

Legenda ověření: ✅ ověřeno ze zdroje · ⚠️ nejednotné / odhad · ❓ neověřeno, nutno doplnit.

---

## 1. Realizovatelnost — shrnutí

**Projekt je realizovatelný** jako osobní PWA s vlastním backendem. Rozhodující části (energetický model, optimalizace
zastávek, přepočet po ručním zadání SoC) jsou čistě výpočetní a nezávisí na Voyahu ani na placených službách.

| Oblast | Hodnocení | Poznámka |
|---|---|---|
| Výpočet trasy (routing) | ✅ snadné | open-source routery s typem silnice, limity a převýšením |
| Energetický model | ✅ proveditelné | fyzikální jádro + kalibrace z vašich jízd; přesnost poroste s daty |
| Optimalizace zastávek | ✅ proveditelné | dynamické programování nad (nabíječka × SoC), plně testovatelné |
| Databáze nabíječek | ⚠️ střední | statická data dobrá (Open Charge Map), **živá obsazenost** prakticky nedostupná zdarma |
| Ceny nabíjení | ⚠️ ruční | veřejně strojově nedostupné → tarify zadáváte vy v nastavení |
| Data z vozu | ❓ nejisté | žádné veřejné API Voyah nenalezeno; OBD bez známých PID → až etapa 5 |
| iPhone PWA | ✅ | mapa, GPS, plocha; omezení: žádný běh na pozadí |

**Upřímné srovnání s hotovým řešením:** A Better Routeplanner (ABRP) dělá body 3, 5 a 6 zadání už dnes a má i vlastní
kalibraci. Vlastní aplikace dává smysl, pokud chcete: (a) model kalibrovaný přesně na váš Voyah a vaše jízdy,
(b) vlastní tarify a preference sítí, (c) plnou kontrolu a rozšiřitelnost. Doporučuji ABRP při vývoji používat
**jako referenci** — porovnávat jeho plány s našimi (viz testování).

---

## 2. Existující řešení a jejich využitelnost

| Řešení | Co umí | Využití pro nás |
|---|---|---|
| **ABRP** (Iternio, od 2024 Rivian) | plánování s nabíjecími křivkami, počasí, živá data | Planning API placené za každý doručený plán + setup poplatek, cena individuálně (contact@iternio.com). Pro osobní projekt **nevyplatí se**; vhodné jen jako srovnávací měřítko. |
| **Chargemap / PlugShare** | databáze nabíječek, hodnocení, komunita | Bez veřejného volně licencovaného API pro stažení dat → **nepoužitelné jako zdroj**; maximálně ruční odkaz „otevřít v Chargemapu". |
| **Open Charge Map** | otevřená databáze nabíječek, REST API | **Hlavní zdroj nabíječek** (viz kap. 3). |
| **OpenStreetMap** (`amenity=charging_station`) | doplňková data | Záloha/doplnění tam, kde OCM chybí (Overpass API). |
| Open-source EV plánovače | existují akademické/hobby projekty, žádný nedosahuje kvality ABRP | Nepřebírat celé; převezmeme principy (DP nad SoC). |

---

## 3. Doporučená API a datové zdroje

### 3.1 Routing (trasa, typ silnice, rychlost, převýšení)

| Varianta | Výhody | Nevýhody | Cena |
|---|---|---|---|
| **openrouteservice (hostované)** — *doporučeno pro MVP* | profil auto, alternativní trasy, převýšení, `extra_info` (typ cesty, sklon); bez serveru | jen nekomerční užití; 2 000 tras/den, 40/min | 0 Kč |
| **Valhalla (self-host)** — *doporučeno od etapy 4* | plná kontrola, atributy hran (třída silnice, limit), převýšení, bez limitů | server s RAM ~4–8 GB pro ČR + okolí, údržba | VPS ~10–15 €/měs. |
| OSRM | velmi rychlé | slabší atributy (převýšení ne), méně vhodné | self-host |
| GraphHopper (hostované) | kvalitní | free tier omezený, komerční plány placené | od ~0 do desítek €/měs. ❓ |
| Google / Mapbox Directions | kvalita, provoz | podmínky omezují ukládání a kombinaci s jinými mapami, platba | placené |

Routing musí vracet **úseky** (délka, třída silnice, rychlostní limit/odhad rychlosti, výškový profil) — z nich se
počítá spotřeba. Rozhraní routeru zabalíme do adaptéru, aby šlo ORS později vyměnit za Valhallu bez změny zbytku.

### 3.2 Nabíjecí stanice

| Zdroj | Stav | Poznámka |
|---|---|---|
| **Open Charge Map API** | ✅ zdarma s API klíčem | licence dat **CC BY 4.0** (dříve BY-SA) + **u každé stanice je uveden poskytovatel dat s vlastní licencí** → při importu hlídat; filtr `opendata=true` vrací jen otevřená data. Atribuce „Open Charge Map" v aplikaci povinná. |
| **OSM / Overpass** | ✅ ODbL | doplnění, atribuce „© OpenStreetMap contributors". |
| **Národní přístupový bod (NAP) dle AFIR** | ❓ | nařízení AFIR (čl. 20) ukládá provozovatelům zveřejňovat statická i dynamická data (vč. dostupnosti a ceny ad hoc) přes NAP, typicky DATEX II. Český NAP a jeho skutečný obsah **jsem nedohledal — ověřit** (MD / dopravniinfo.cz). Pokud funguje, je to nejlepší zdroj živé dostupnosti a cen. |
| API operátorů (ČEZ, E.ON, PRE, IONITY, Tesla) | ❓ | veřejná API obecně nenabízejí; OCPI je B2B (roaming). Nepočítat s tím v MVP. |

**Pravidlo:** stav stanice z OCM je „poslední hlášený", ne živý. UI ho tak bude i označovat
(„dostupnost neověřena", datum poslední aktualizace záznamu).

### 3.3 Počasí

**Open-Meteo** ✅ — bez klíče, předpověď po hodinách: teplota, vítr (rychlost + směr), srážky, sníh.
Free jen pro **nekomerční** užití (limit 10 000 volání/den), data CC BY 4.0, nutná atribuce. Pro osobní použití ideální.

### 3.4 Mapové podklady

**MapLibre GL JS** (open-source) + dlaždice **OpenFreeMap** (zdarma, bez klíče) nebo MapTiler (free tier s klíčem).
Přímé dlaždice tile.openstreetmap.org pro aplikace nepoužívat (zásady užití OSM).

### 3.5 Předání do navigace

| Navigace | Průjezdní body v URL | Postup |
|---|---|---|
| **Google Maps** (univerzální URL `google.com/maps/dir/?api=1`) | ✅ parametr `waypoints` (na mobilu omezený počet) | celá trasa „start → zastávky → cíl" jedním odkazem |
| **Apple Maps** | ⚠️ oficiálně dokumentován jen start + cíl; vícebodové odkazy nespolehlivé | otevírat **úsek po úseku** (do další nabíječky) — tlačítko „Navigovat k zastávce" |
| Waze | jen cíl | úsek po úseku |

---

## 4. Vozidlo — výchozí parametry (vše editovatelné)

| Parametr | Vaše hodnota | Zdroje | Výchozí v aplikaci |
|---|---|---|---|
| Baterie nominální | ~108 kWh | ⚠️ evropská specifikace uvádí **106 kWh** (EV Database, EVKX) | 106 kWh |
| Využitelná kapacita | 100 kWh | ❓ výrobce neuvádí | 100 kWh (kalibruje se) |
| Max. DC výkon | 89–90 kW (vaše zkušenost) | ⚠️ databáze uvádějí **100 kW**, ale jako odhad („Voyah has not released details") | **90 kW** — vaše pozorování má přednost |
| Konektor DC | — | ✅ **CCS2** (EU), vlevo vzadu | CCS2 |
| AC | — | ❓ 11 kW? ověřit v TP | — |

**Nabíjecí křivka** se zadává jako tabulka bodů *(SoC %, max. výkon kW)* s lineární interpolací. Výchozí:

| SoC | 0 | 10 | 50 | 80 | 85 | 90 | 95 | 100 |
|---|---|---|---|---|---|---|---|---|
| kW | 60 ❓ | 90 | 90 | 85 ❓ | 40 | 40 | 20 ❓ | 7 ❓ |

Body s ❓ jsou dočasné předpoklady (je potřeba je změřit — viz kap. 11). Čas nabíjení:

```
t = Σ přes kroky 1 % SoC:  ΔE / P(SoC)      kde ΔE = 1 % × využitelná kapacita / η_nabíjení
P(SoC) = min( křivka_vozu(SoC) × k_teplota_baterie , výkon_stanice × k_sdílení )
```

- `η_nabíjení` (ztráty mezi stojanem a baterií) — výchozí 0,95, kvůli ceně (platí se kWh ze stojanu).
- `k_teplota_baterie` — v zimě po příjezdu se studenou baterií < 1 (výchozí: lineárně 0,6 při −10 °C → 1,0 při +15 °C,
  **jen předpoklad**, kalibruje se ze skutečných nabíjení). Pokud vůz umí předehřev, nastaví se 1,0.
- `k_sdílení` — některé stanice dělí výkon mezi dva body; z dat obvykle neznámé → konzervativní režim ho sníží.
- **Stanice 150/250 kW není rychlejší než 100 kW**, jakmile vůz bere max. 90 kW — výpočet to dělá automaticky přes `min()`.
  Preference „výkonné stanice" se použije jen jako **rezerva** (sdílení výkonu, degradace) v podobě malého bonusu, ne jako zrychlení.

---

## 5. Energetický model

### 5.1 Princip

Trasa se rozdělí na úseky (~0,5–2 km) s atributy: délka, třída silnice, plánovaná rychlost, převýšení, teplota,
vítr, srážky. Spotřeba úseku:

```
E_úsek = [ c_jízda(v, třída) × d                      ← odpor vzduchu + valivý odpor, z kalibrace
         + E_převýšení(Δh)                             ← m·g·Δh / η_pohon  (stoupání)  |  m·g·Δh · η_rekup (klesání)
         + P_HVAC(T) × t                               ← topení/klima, kW × hodiny
         ] × f_baterie(T) × f_vozovka(srážky) × k_kalibrace(třída, teplotní pásmo)
```

### 5.2 Jízdní složka c(v)

Fyzikálně spotřeba roste s v² (aerodynamika). Model `c(v) = a + b·v²` [kWh/100 km] se nafituje na vaše letní hodnoty:

- 17,5 kWh/100 km při 90 km/h
- 25 kWh/100 km při dálniční rychlosti — **❓ potřebuji vědět, při jaké skutečné rychlosti** (předpoklad 130 km/h)

S předpokladem 130 km/h vyjde `a ≈ 10,6`, `b ≈ 0,00085` → 50 km/h ≈ 12,7; 110 km/h ≈ 20,9; 130 km/h ≈ 25,0.
Jsou to **odvozené odhady**, ne měření; ve městě se navíc přičítá složka za zastavování (konfigurovatelná).

**Vítr:** v aerodynamickém členu se použije rychlost vůči vzduchu `v + v_protivítr` (průmět větru do směru jízdy).

### 5.3 Teplotní a zimní složky (koeficienty, ne „pravdy")

| Složka | Tvar | Výchozí hodnota (předpoklad, kalibruje se) |
|---|---|---|
| Vytápění `P_HVAC(T)` | `P0 + k·max(0, 18 − T)` kW pro T < 18 °C; klima nad 25 °C | P0 = 0,3 kW, k = 0,12 kW/°C (→ ~2,7 kW při −2 °C) |
| Účinnost baterie `f_baterie(T)` | 1 nad +15 °C, lineárně roste pod | 1,10 při −10 °C |
| Vozovka `f_vozovka` | suchá / mokrá / sníh | 1,00 / 1,05 / 1,15 |
| Hmotnost `m` | vůz + posádka + náklad | 2 400 kg + uživatel |
| Rekuperace `η_rekup` | podíl potenciální energie vrácený z klesání | 0,6 |

Zimní odhad se tedy **nevymýšlí jako jedno číslo**, ale skládá z oddělených členů, které jdou jednotlivě kalibrovat
(topení se projeví hlavně v pomalé jízdě, baterie a vozovka plošně).

### 5.4 Jízdní profily

| Profil | Rychlost úseku |
|---|---|
| Ekonomický | min(limit, strop) — např. dálnice 110, silnice 80 |
| Standardní | ~95 % limitu / typická rychlost routeru |
| Rychlý | limit (nikdy nad limit) |

Optimalizátor spočítá všechny tři a **zobrazí skutečný rozdíl v celkovém čase vč. nabíjení** — typicky odhalí, kdy
rychlá jízda nic neušetří.

### 5.5 Nejistota

Každý plán nese pásmo nejistoty (např. ±8 % spotřeby bez kalibrace, postupně méně). Konzervativní režim plánuje na
horní hranici pásma. Dokud není kalibrace, UI ukazuje „odhad — model nekalibrován".

---

## 6. Optimalizační algoritmus

### 6.1 Postup

1. **Kostra trasy:** router vrátí 1–3 alternativní trasy (A/B), pro každou úseky s atributy.
2. **Koridor nabíječek:** stanice s CCS2 ≤ X km od trasy (výchozí 5 km, konzervativní 2 km); vyřadit nepřístupné
   (privátní, „jen zákazníci", Tesla bez otevření pro ostatní).
3. **Zajížďka:** pro každou kandidátní stanici čas a energie odbočení (matice routeru: bod trasy → stanice → zpět).
4. **Graf:** uzly = start, kandidátní stanice (seřazené podél trasy), cíl. Hrana i→j = jízda po trase + zajížďky,
   s energií z modelu (kap. 5).
5. **Dynamické programování nad stavem (uzel, SoC po 1 %):**
   - ze stanice lze odjet s libovolným SoC ∈ {příjezd … 100 %} → **cílové % nabití je výsledkem optimalizace**, ne pravidlo 80 %;
   - hrana je přípustná, jen když příjezdový SoC ≥ rezerva (nabíječka 10 %, cíl 15 %, v konzervativním režimu + pásmo nejistoty);
   - cena hrany = čas jízdy + čas nabíjení (křivka) + režie zastávky (výchozí 4 min: příjezd, připojení, platba).
   - Velikost úlohy: ~200 stanic × 101 SoC × hrany jen dopředu do dosahu → v Pythonu desítky ms až jednotky sekund.
6. **Režimy:**
   - *Nejrychlejší* — minimalizuje čas.
   - *Nejlevnější* — minimalizuje Kč (cena kWh dle tarifu sítě, časové/blokovací poplatky) s limitem „max. +X % času".
   - *Vyvážený* — minimalizuje `čas + λ·Kč` (λ = hodnota vaší hodiny, nastavitelná) + bonus preferované sítě.
   - Implementačně label-setting s Paretovými štítky (čas, Kč) — z jednoho běhu se vyberou všechny tři varianty.
7. **Preferované sítě:** změkčené — sleva na „ceně" hrany (minuty), ne zákaz. Režim „pouze preferované" jen na výslovné přání.
8. **Čekání na obsazenou stanici:** pokud zdroj poskytne dostupnost, přičte se očekávané čekání; jinak se nepřičítá,
   ale stanice s 1 bodem dostane malou penalizaci (riziko obsazení) a UI nabídne **záložní stanici** pro každou zastávku.
9. **Žádné řešení** → aplikace jasně řekne proč (např. „úsek X–Y 210 km bez CCS2 nabíječky, při rezervě 10 % dojezd 185 km")
   a nabídne povolit menší rezervu / delší zajížďku. Nikdy nevrátí nereálný plán.

### 6.2 Proč DP, ne A*/Dijkstra „naslepo"

Stav (stanice, SoC) a jednosměrnost podél trasy dělají z úlohy acyklický graf → DP je exaktní, deterministické a
snadno testovatelné. A* by přineslo zrychlení jen u celoevropských tras; lze doplnit později (heuristika = zbývající
čas jízdy).

---

## 7. Aktivní cesta a ruční aktualizace baterie

1. Uživatel (stojící vůz) zadá velkým číselníkem „47 %" → aplikace vezme GPS.
2. Promítne polohu na trasu, porovná s predikcí v tom bodě: odchylka Δ = skutečný − predikovaný SoC.
3. **Rozlišení krátkodobé vs. dlouhodobé odchylky:**
   - *faktor jízdy* `k_trip` = skutečně spotřebováno / predikováno od posledního bodu (vážený energií úseku,
     krátké úseky < 10 kWh mají malou váhu — ±1 % SoC = ±1 kWh nejistota);
   - zbytek trasy se přepočítá s `k_trip` (rychlá adaptace jen pro tuto cestu);
   - **dlouhodobý profil** se aktualizuje až po skončení cesty (kap. 8), aby jednorázová vichřice nezkazila model.
4. Spustí se znovu optimalizace z aktuální polohy a SoC; když se plán změní, ukáže se „Původně: … → Nově: …".
5. Riziko: pokud příjezd k další zastávce klesne pod rezervu → výrazné červené varování + návrh bližší stanice / snížení rychlosti
   (s výpočtem, kolik % ušetří jízda 110 místo 130).

---

## 8. Učení ze skutečných jízd (kalibrace)

- Ukládá se každý **úsek mezi dvěma známými SoC** (start, ruční zadání, nabíječka, cíl): vzdálenost po třídách silnic,
  průměrná rychlost, teplota, převýšení, predikovaná a „skutečná" energie (ΔSoC × využitelná kapacita).
- Kalibrační faktory `k(třída, teplotní pásmo)` — tabulka např. 3 třídy × 5 pásem (< −5, −5…5, 5…15, 15…25, > 25 °C).
- Aktualizace: vážený průměr se „smrštěním" k 1,0 (Bayesovsky jednoduché):
  `k_nový = (n0·k_starý + w·k_změřený) / (n0 + w)`, kde w = spotřebovaná energie úseku / 10 kWh, n0 = dosavadní váha.
- Odlehlé hodnoty (|k_změřený − 1| > 0,4) se uloží, ale do modelu nevstoupí bez potvrzení.
- Zvlášť se kalibruje **využitelná kapacita** (z nabíjení: kWh ze stojanu × η vs. ΔSoC) a **nabíjecí křivka**
  (uživatel zadá při nabíjení výkon v pár bodech, např. při 20/50/80 %).
- Vše transparentní: obrazovka „Model" ukazuje tabulku faktorů, počet jízd a jak se který měnil.

---

## 9. Uživatelské rozhraní (PWA, iPhone, česky)

| Obrazovka | Obsah |
|---|---|
| **Plán** | „Odkud" (GPS / adresa), „Kam", průjezdní body, SoC (posuvník + číslo), rezerva v cíli, profil (Eko/Standard/Rychle), režim (Nejrychlejší/Nejlevnější/Vyvážený), tlačítko **Naplánovat trasu** |
| **Výsledky** | mapa s trasou a zastávkami; karty variant A/B/C: jízda · nabíjení · celkem · příjezd · SoC v cíli · Kč; pod tím časová osa zastávek |
| **Zastávka** | stanice, operátor, výkon stanice vs. očekávaný výkon pro Voyah, příjezd s X % → odjezd s Y %, doba, cena, stav dat (stáří záznamu), záložní stanice, **Navigovat** |
| **Aktivní cesta** | zbývá km / čas, predikce SoC na další zastávce a v cíli, velké tlačítko **Zadat baterii**, přepočet, další krok navigace |
| **Nastavení** | vůz (kapacita, křivka – tabulka), spotřeba a koeficienty, sítě (preference, členství, Kč/kWh, Kč/min, blokovací poplatek, priorita), rezervy, profily, konzervativní režim |
| **Historie / Model** | jízdy, odchylky predikce, kalibrační tabulka |

Zásady: velké ovládací prvky, tmavý režim, minimum psaní; zadávání SoC jen při stání (aplikace to připomene).
Omezení iOS PWA: neběží na pozadí (přepočet jen při otevření), GPS jen s otevřenou aplikací, notifikace jen u PWA na ploše (iOS ≥ 16.4).

---

## 10. Technická architektura

```
iPhone (PWA)                                  Server (VPS, Docker)
React + TypeScript + Vite                     FastAPI (Python 3.12)
MapLibre GL, OpenFreeMap  ─── HTTPS/JSON ──►  ├─ routing/      adaptér ORS → později Valhalla
IndexedDB (offline poslední plán,             ├─ energy/       energetický model (čistý Python, bez I/O)
           rozpracované zadání)               ├─ chargers/     import OCM (+OSM), cache, filtr koridoru
Service worker (instalace na plochu)          ├─ optimizer/    DP / Pareto štítky
                                              ├─ weather/      Open-Meteo, cache 1 h
                                              ├─ prefs/        vozidlo, sítě, tarify, profily
                                              ├─ trips/        aktivní cesta, historie, kalibrace
                                              ├─ telemetry/    rozhraní pro budoucí OBD/API (zatím ruční)
                                              └─ SQLite (SQLAlchemy → kdykoli PostgreSQL/PostGIS)
```

| Rozhodnutí | Proč | Alternativa |
|---|---|---|
| **Backend FastAPI** (ne vše v prohlížeči) | API klíče mimo frontend; Python vhodný pro výpočty a testy (pytest); stejný kód lze pouštět v testech na reálných trasách | čistě klientská PWA — jednodušší hosting, ale klíče by byly veřejné a výpočet na mobilu pomalejší |
| **React + TS PWA** | jedna kódová základna, instalace na plochu, bez App Store | nativní SwiftUI — lepší pozadí, CarPlay, ale řádově dražší vývoj; zvážit v etapě 5 |
| **SQLite** | nulová správa, jeden uživatel | PostgreSQL + PostGIS při více uživatelích / geodotazech nad celou EU |
| **Energetický model a optimalizátor bez I/O** | deterministické, reprodukovatelné testy na fixturách | — |
| **Přístup** | aplikace jen pro vás → jednoduché přihlášení (passkey nebo token) + HTTPS | — |

Hosting: malý VPS (např. Hetzner/OVH) s Dockerem a HTTPS (Caddy). iMac jako server nedoporučuji — telefon na cestách potřebuje stálou veřejnou adresu.

---

## 11. Provozní náklady (orientačně)

| Položka | MVP | Po etapě 4 (self-host Valhalla) |
|---|---|---|
| VPS | ~5 €/měs. (2 GB RAM) | ~10–15 €/měs. (8 GB RAM) |
| Routing ORS | 0 (nekomerční, 2 000 tras/den) | 0 |
| Open Charge Map | 0 | 0 |
| Open-Meteo | 0 (nekomerční) | 0 |
| Mapové dlaždice OpenFreeMap | 0 | 0 |
| Doména | ~300 Kč/rok (volitelné) | ~300 Kč/rok |
| **Celkem** | **≈ 150 Kč/měs.** | **≈ 300–400 Kč/měs.** |

Pozor: všechny bezplatné tarify jsou **nekomerční**. Pokud by aplikace jednou šla zákazníkům (ThermaVera/REO),
je nutné přejít na komerční licence (ORS self-host, Open-Meteo placené, OCM dle licencí poskytovatelů).

---

## 12. Harmonogram

| Etapa | Obsah | Odhad (práce s Claude Code) |
|---|---|---|
| 1 Analýza | tento dokument | ✅ hotovo po schválení |
| 2 Architektura | datový model, API kontrakty, kostra repozitáře, CI s testy | 1–2 sezení |
| 3a Jádro | energetický model + nabíjecí křivka + optimalizátor + **14 testovacích scénářů** (fixtury) | 2–3 sezení |
| 3b Data | adaptér ORS, import OCM pro CZ/SK/PL/AT/DE, Open-Meteo | 1–2 sezení |
| 3c PWA | 5 obrazovek, mapa, navigace do Google/Apple Maps, ruční SoC, přepočet | 2–3 sezení |
| 3d Nasazení | VPS, HTTPS, přihlášení, instalace na iPhone | 1 sezení |
| 4 Kalibrace | 4–8 týdnů reálných jízd (léto i zima je ideál), ladění koeficientů, srovnání s ABRP | průběžně |
| 5 Rozšíření | OBD/telemetrie, živá dostupnost (NAP), Valhalla, historie, CarPlay (jen nativní app) | dle priorit |

MVP použitelné na první reálnou cestu: **cca 7–11 pracovních sezení**.

---

## 13. Propojení s vozem (etapa 5 — jen průzkum)

| Varianta | Zjištění | Doporučení |
|---|---|---|
| A. Oficiální API Voyah | ❓ nenalezeno žádné veřejné ani partnerské API | dotaz na importéra |
| B. Aplikace Voyah | aplikaci pro EU vydává **Electric Way AS** (Norsko); nenalezeno žádné zdokumentované rozhraní | reverzní inženýrství nedoporučuji (podmínky užití, bezpečnost účtu) |
| C. Komunitní integrace | ❓ žádný projekt pro Voyah Free (GitHub, Home Assistant) nenalezen | sledovat |
| D. OBD-II | standardní OBD u EV obvykle SoC nevrací; nutné výrobcem specifické PID přes CAN — pro Voyah **nenalezeny** (OBDb/WiCAN) | možný vlastní průzkum: adaptér ELM327/WiCAN + Car Scanner, záznam komunikace. Jen čtení, žádné zápisy do jednotek. |

Rozhraní `telemetry/` bude od začátku připravené, takže pozdější zdroj SoC (OBD, API) jen nahradí ruční zadání.

---

## 14. Testy (automatické, reprodukovatelné)

Všechny scénáře běží nad **fixturami** (uložená trasa + sada stanic + počasí), takže výsledek je deterministický.
Fiktivní stanice existují jen v testech, nikdy v produkčním režimu.

1. trasa bez nabíjení · 2. jedna zastávka · 3. více zastávek · 4. dálnice léto · 5. dálnice zima ·
6. okresní silnice · 7. výpadek plánované stanice (přeplánování) · 8. ruční SoC během cesty ·
9. výrazně vyšší skutečná spotřeba (varování) · 10. nabíjení do 80 % vs. nad 80 % (DP zvolí 90 %, když ušetří zastávku) ·
11. stanice 100 vs. 250 kW (stejný čas pro Voyah) · 12. preference registrovaného operátora ·
13. chybějící data o nabíječkách (čitelná chyba) · 14. trasa bez bezpečně dosažitelné stanice (žádný plán + důvod).

Navíc „zlaté" testy: 3–5 reálných tras (např. Ostrava–Praha, Ostrava–Vídeň, Ostrava–Chorvatsko) porovnávané s ABRP
a později se skutečnými jízdami.

---

## 15. Co od vás potřebuji

1. **Dálniční spotřeba 25 kWh/100 km — při jaké rychlosti** (tempomat 130? 120?) a při jaké teplotě.
2. **Zimní zkušenost**, i hrubá: spotřeba na dálnici / silnici kolem 0 °C a −10 °C.
3. **Nabíjecí křivka:** co ukazuje vůz/stojan při ~20 %, 50 %, 70 %, 80 %, 90 % (i pár fotek displeje stačí).
   Máte složku „PRE 200kw" — pokud jsou tam záznamy z nabíjení, využiji je.
4. **Využitelná kapacita:** máte záznam nabíjení s kWh ze stojanu a % před/po?
5. Umí vůz **předehřev baterie** před nabíjením (při navigaci k nabíječce)?
6. **Sítě a tarify:** u kterých operátorů máte účet/kartu a za kolik (Kč/kWh, minutové, blokovací poplatky).
7. **Typické trasy** a země (jen ČR + okolí, nebo i Chorvatsko/Itálie apod.) — ovlivní objem dat a velikost serveru.
8. **Hosting:** souhlas s VPS (~150 Kč/měs.) a případně doménou; nebo jiná preference.
9. Hmotnost: typicky kolik osob/zavazadel, tažné zařízení?
10. Potvrzení stacku (React+TS PWA + FastAPI + SQLite) a rozsahu MVP dle kap. 12.

---

## Zdroje

- Voyah Free 106 kWh — [EV Database](https://ev-database.org/car/2049/Voyah-Free-106-kWh), [EVKX specifikace](https://evkx.net/models/voyah/free/free/specifications), [EVKX nabíjecí křivka (odhad)](https://evkx.net/models/voyah/free/free/chargingcurve)
- [Open Charge Map API](https://openchargemap.org/site/develop/api), [licence CC BY 4.0](https://community.openchargemap.org/t/announcing-our-new-simpler-data-license-for-ocm-data-cc-by-4-0-international/565)
- [openrouteservice — tarify](https://openrouteservice.org/plans/)
- [Open-Meteo — podmínky](https://open-meteo.com/en/terms), [ceník](https://open-meteo.com/en/pricing)
- [Iternio / ABRP API](https://iternio.com/api), [ceny Planning API](https://abrp.featurebase.app/help/articles/1764088-iternio-apis)
- [Apple Map Links (archiv)](https://developer.apple.com/library/iad/featuredarticles/iPhoneURLScheme_Reference/MapLinks/MapLinks.html), [ABRP: vícebodové trasy v iOS](https://abrp.upvoty.com/b/report-a-bug/sharing-route-with-multiple-stops-on-ios-only-shows-directions-to-first-stop/)
- AFIR a datové povinnosti — [Mennekes](https://www.mennekes.org/emobility/knowledge/afir/), [Eco-Movement čl. 20](https://www.eco-movement.com/?p=3154)
- [Aplikace VOYAH (App Store)](https://apps.apple.com/dk/app/voyah/id6444374135), [WiCAN — postup hledání SoC PID](https://github.com/meatpiHQ/wican-fw/wiki/EV-Battery-SoC-in-Home-Assistant-%E2%80%90-Example)
