# Zadání překladu: návod k tepelnému čerpadlu REO HEATING RH030–RH060, starší ovladač (EN → CS)

Vstup: `chunks/chunk_XX.json` je JSON objekt `{id: "anglický HTML fragment"}`.
Výstup: `cs/chunk_XX.json` je JSON objekt se **stejnými klíči** `{id: "český HTML fragment"}` (UTF-8, `ensure_ascii=False`).

Každý fragment je odstavec, nadpis, buňka tabulky nebo popisek v obrázku instalačního a uživatelského
návodu k invertorovému tepelnému čerpadlu vzduch–voda s chladivem R290. Český text se potom vysází
**zpět na stejné místo v PDF**, takže:

## Pravidla
1. **Zachovej značky** `<b>…</b>` a `<br>` na odpovídajících místech (stejný počet `<br>`, tučné zůstává tučné).
   Entity `&lt;` `&gt;` `&amp;` ponech jako entity.
2. **Buď stručný.** Čeština je delší než angličtina a místo je omezené. V buňkách tabulek a popiscích
   používej krátké odborné tvary a běžné zkratky (např. „Topný výkon (kW)", „Max. proud (A)").
3. **Neměň:** čísla, jednotky, rozsahy, kódy chyb (Er.ocb, E1…), názvy parametrů VELKÝMI_PÍSMENY
   s podtržítky, kódy parametrů (P01…P29, F01…F08), zkratky (PFC, IPM, DC, AC, COP, EER, ErP, DB/WB, DN25, PPR, PVC),
   názvy aplikací („Smart Life“, „Tuya Smart“, „Google Play Store“, „Apple App Store“), značku kompresoru HIGHLY.
4. **Texty z displeje ovladače a aplikace** (ovladač i aplikace jsou anglicky – NEPŘEKLÁDEJ je, to byla hlavní chyba dosavadního překladu) (tlačítka a položky menu v uvozovkách nebo zjevně z UI, např. "SET", "OK",
   "ON/OFF", "MODE", "SETTING", "TIMER", "UNIT STATUS", "USER PARAMETERS", "FAULTY", "CONFIRM", "CANCEL", "Add Device",
   "SMART MODE", "AP MODE", "Done", "Remove Device", "Work mode", "Water Temp. Setting") ponech
   **anglicky v uvozovkách**, protože displej je anglicky; kolem nich přelož větu. Cesty v menu
   (Advanced setting > Parameters config. > …) ponech anglicky.
5. **Přeznačení modelů (povinné, výrobce se nesmí v textu objevit):**
   | originál | český text |
   |---|---|
   | PW030-DKZLRS-E/S (i rozdělené „PW030-DKZLRS<br>-E/S“) | RH030 |
   | PW040-DKZLRS-E/S | RH040 |
   | PW050-DKZLRS-E/S | RH050 (1fázové) |
   | PW050-DKZLRS-E | RH050 (3fázové) |
   | PW060-DKZLRS-E | RH060 |
   | „Single phase system (PW030/040-DKZLRS-E/S)“ | „Jednofázové provedení (RH030 / RH040)“ |
   | „Single phase system (PW050-DKZLRS-E)“ (chyba originálu, jde o 1f) | „Jednofázové provedení (RH050 1fázové)“ |
   | „Three phase system (PW050/060-DKZLRS-E)“ | „Třífázové provedení (RH050 3fázové / RH060)“ |
   „DC Inverter (Air Source) Heat Pump“ v textu → „tepelné čerpadlo REO HEATING“ nebo „invertorové tepelné čerpadlo vzduch–voda“
   podle kontextu. Formulace „our company“ → „dodavatel“ / „REO HEATING“.
6. Když fragment nic k překladu nemá (jen kód, název modelu, hodnota), vrať ho beze změny.
7. Tón je věcný, technický, vykání („Zkontrolujte…", „Nepoužívejte…"). Zjevné chyby a nesmysly originálu
   opatrně narovnej, nic nepřidávej a neubírej věcně. Žádné komentáře k překladu.
8. Obsah (rejstřík) a nadpisy kapitol musí sedět: stejný nadpis se překládá všude stejně.

## Terminologie (dodržuj jednotně)
| EN | CS |
|---|---|
| heat pump | tepelné čerpadlo |
| DC inverter (air source) heat pump | invertorové tepelné čerpadlo vzduch–voda |
| DHW, domestic hot water | TUV (teplá užitková voda) – při prvním výskytu v odstavci „teplá užitková voda (TUV)" |
| water tank / DHW tank | zásobník TUV |
| buffer tank | akumulační nádrž |
| wire(d) controller | kabelový ovladač |
| main interface | hlavní obrazovka |
| user interface | uživatelské rozhraní |
| space heating | vytápění |
| floor heating (loop) | podlahové vytápění (okruh) |
| fan coil (FCU) | fancoil (FCU) |
| radiator | radiátor (otopné těleso) |
| room thermostat | pokojový termostat |
| auxiliary heat source (AHS) | přídavný zdroj tepla (AHS) |
| internal backup heater (IBH) / auxiliary electric heater | záložní elektrický ohřev (IBH) / přídavný elektrokotel |
| tank booster heater (TBH) | elektrická topná vložka v zásobníku (TBH) |
| circulation pump | oběhové čerpadlo |
| 3-way valve | trojcestný ventil |
| mixing valve / mixing station | směšovací ventil / směšovací sestava |
| plate heat exchanger | deskový výměník |
| evaporator / condenser | výparník / kondenzátor |
| compressor | kompresor |
| four-way valve | čtyřcestný ventil |
| electronic expansion valve | elektronický expanzní ventil |
| expansion vessel/tank | expanzní nádoba |
| safety valve | pojistný ventil |
| water flow switch | průtokový spínač |
| leakage sensor | snímač úniku chladiva |
| sensor / probe | čidlo |
| outlet / inlet water temperature | teplota výstupní / vstupní vody |
| leaving water temperature | teplota výstupní vody |
| ambient temperature | venkovní teplota |
| defrost(ing) | odmrazování |
| sterilization (legionella) | sterilizace (antilegionella) |
| silent mode | tichý režim |
| holiday away | režim dovolená |
| climate related curves | ekvitermní křivky |
| smart grid | Smart Grid (SG) |
| DIP switch | DIP přepínač |
| drive board | budicí deska (měnič) |
| main board / PCB | hlavní deska / DPS |
| fuse or circuit breaker | jistič |
| wire diameter | průřez vodiče |
| power supply | napájení |
| heating capacity | topný výkon |
| power input | příkon |
| cooling capacity | chladicí výkon |
| sound power / noise | akustický výkon / hlučnost |
| net weight / net dimension | hmotnost netto / rozměry netto |
| spare parts | náhradní díly |
| exploded view | rozpad dílů |
| wiring diagram | schéma zapojení |
| error code / fault | chybový kód / porucha |
| troubleshooting | odstraňování závad |
| maintenance | údržba |
| installer | instalační technik |
| qualified / authorized service | odborný / autorizovaný servis |
| WARNING / CAUTION / DANGER / Note | VAROVÁNÍ / UPOZORNĚNÍ / NEBEZPEČÍ / Poznámka |
| Figure | Obrázek |
| Section 1 | Kapitola 1 |
| Table of Contents | Obsah |
| OPERATING INSTRUCTION MANUAL | NÁVOD K INSTALACI A OBSLUZE |

## Věcné opravy originálu (proveď v překladu)
Překlad je určen zákazníkům a montážním firmám v ČR; originál obsahuje chyby a americké reálie. Oprav takto:
- **NEC / CEC / „National Electrical Code“, „national, state, and local codes“** → „platné předpisy a normy ČSN / EN“,
  „místní předpisy“. Elektroinstalaci provádí „osoba s odbornou kvalifikací v elektrotechnice“.
- **R290 je hořlavé chladivo (propan).** Vlastnost č. 4 v „General Features“ („No potential danger of any inflammable…
  explosion, fire…“) přelož jako: „4. V budově se nespaluje žádné palivo – odpadá riziko otravy spalinami a rizika spojená
  se skladováním paliva. Chladivo R290 je však hořlavé, dodržujte bezpečnostní pokyny.“
- „Compared with traditional oil/LPG boilers … up to 50% less CO2 whilst saves 80% running cost“ → přelož věrně, ale vždy
  s „až“ („až o 50 % nižší emise CO2 a až o 80 % nižší provozní náklady“).
- „high voltage switch / low voltage switch“ v souvislosti s tlakem = **vysokotlaký / nízkotlaký spínač** (presostat);
  „Low pressure too low“ = „příliš nízký tlak na sání“.
- „detailed error code from 1 to 348“ → 384 (překlep originálu, tabulka končí 384).
- „More than 52℃ hot water can cause damage“ → „Voda teplejší než 52 °C může způsobit opaření…“.
- „main power switch should set much higher 1.4 meter“ → „ve výšce min. 1,4 m“.
- Desetinná čárka v běžném textu (0,5 m; 1,4 m), ale v tabulkách technických dat a rozsazích nech čísla tak, jak jsou.
- Jednotky: „kpa“ → „kPa“, „HZ“ → „Hz“, „MIN“ → „min“, mezera mezi číslem a jednotkou („30 min“, „70 °C“) v běžném textu.
- „Antisepsis“ = **sterilizace (antilegionella)**; „Vacation mode“ = **režim dovolená**; „Power mode“ = **výkonný režim**;
  „Smart mode“ = **chytrý režim** (v uvozovkách anglicky jen tam, kde jde o popisek na displeji).
- „shockproof bushes“ = antivibrační podložky (silentbloky); „Quick Connect fittings“ = rychlospojky/šroubení;
  „loose joint“ = rozebíratelný spoj (šroubení); „limber hole“ = odvodňovací otvor.
