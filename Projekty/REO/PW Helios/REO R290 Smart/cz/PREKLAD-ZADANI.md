# Zadání překladu: návod k tepelnému čerpadlu REO HEATING (EN → CS)

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
   s podtržítky (HOT_WATER_TEMP_SET, ZONE_A_HEAT_CURVE…), zkratky signálů a komponent (TWout2, T1S, AHS, IBH, TBH,
   PUMPo, S3V1, SV1, SG, EVU, MPPT, PFC, PWM, IPM, EEV, SCBA, ATEX, Uoc, Vmpp, DN25), názvy modelů (RH06…RH16, RHX30,
   RHX40, R290, PZ46M), názvy aplikací (Huilian Smart, Tuya, APP STORE, GOOGLE PLAY).
4. **Texty z displeje ovladače a aplikace** (tlačítka a položky menu v uvozovkách nebo zjevně z UI, např. "SET", "OK",
   "Display Settings", "Force ON TBH", "Smart mode", "Add Device", "Home", "Logout", "Sterilization Timer") ponech
   **anglicky v uvozovkách**, protože displej je anglicky; kolem nich přelož větu. Cesty v menu
   (Advanced setting > Parameters config. > …) ponech anglicky.
5. „1-phase" / „3-phase" přelož jako „1fázové" / „3fázové". Model v nadpisu „RH06 (1-phase)" → „RH06 (1fázové)".
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
