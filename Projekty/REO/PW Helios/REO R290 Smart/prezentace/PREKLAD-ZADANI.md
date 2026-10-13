# Zadání překladu: prezentace tepelných čerpadel REO HEATING R290 (EN → CS)

Vstup: `chunks/chunk_XX.json` = `{id: "anglický text"}`. Výstup: `cs/chunk_XX.json` se **stejnými klíči** a českým textem
(UTF-8, `json.dump(..., ensure_ascii=False)`). Překládej sám, žádné externí služby.

Jde o produktovou prezentaci (50 snímků) pro obchodní partnery a instalační firmy: konstrukce jednotky, technické
tabulky, funkce, ovladač, Wi-Fi, schémata zapojení. Text se vrací do stejných textových polí a buněk tabulek, takže:

## Pravidla
1. **Značky zachovej:** `<f1>…</f1>`, `<f2>…</f2>` označují úseky s odlišným formátováním (tučné, barva, velikost).
   Každá značka musí být ve výstupu **právě jednou a ve stejném pořadí**. Obsah úseků smíš přeformulovat, ale
   tučný/zvýrazněný úsek má nést odpovídající český význam. Prázdný úsek (např. `<f2> </f2>`) ponech, jak je.
   `<br>` (zalomení řádku) zachovej ve **stejném počtu**.
2. **Buď stručný.** Čeština nesmí být výrazně delší než angličtina, místo na snímku je pevné. V tabulkách a
   popiscích používej zkratky (např. „Topný výkon (kW)“, „Max. proud (A)“, „Hmotnost netto (kg)“).
3. **Neměň:** čísla, jednotky, rozsahy, normy (EN14825:2022), kódy a zkratky (SCOP, COP, EER, ErP, DHW→ přelož jako TUV,
   MPPT, PV→FV jen v souvislém textu; SG, EVU, RS485, BMS, Modbus, AHS, IBH, TBH, P_O, P_M1, S3V1, SL1/SL2, TWout2 …),
   názvy parametrů VELKÝMI_PÍSMENY, názvy modelů (RH06…RH16, RHX20 Pro, RHX30 Pro, 1F/3F), názvy dodavatelů komponent
   (MITSUBISHI, SHIMGE, SAGINOMIYA, ACOL…), aplikace „Huilian“, „§14a EnWG“, „SG-Ready“, „PV-Ready“.
4. **Texty z displeje ovladače** (tlačítka a položky menu v uvozovkách nebo zjevně z UI, např. "MODE", "Timer On/Off",
   "Sterilization Timer", "Silent Timer", "Holiday Away", "Force ON TBH", "Floor Heat Dry", 1ZONE.TW, PANEL_CTRL)
   ponech **anglicky** v českých uvozovkách „…“; menu cesty (Advanced setting → Parameters config. → …) anglicky.
5. Výrobce ani jiné značky nepřidávej. Kde originál mluví o „manufacturer/our company“, piš neutrálně („výrobce“).
6. Tón: věcný technický marketing pro B2B, bez superlativů navíc. Vykání. Nadpisy snímků krátké, bez tečky.
7. Když text nic k překladu nemá (jen hodnota/kód), vrať ho beze změny.

## Terminologie
heat pump = tepelné čerpadlo · DC inverter = invertorové (DC) · DHW / hot water = TUV / teplá voda ·
hydraulic module = hydraulický modul · water pump = oběhové čerpadlo · plate heat exchanger = deskový výměník ·
four way valve = čtyřcestný ventil · EEV = elektronický expanzní ventil · microbubble exhaust valve = odvzdušňovací ventil ·
flow switch = průtokový spínač · expansion vessel = expanzní nádoba · safety valve = pojistný ventil ·
refrigerant leakage sensor = snímač úniku chladiva · sound-absorbing cotton = zvukově izolační vata ·
chassis = základový rám · antifreezing = protizámrazová ochrana · wired controller = kabelový ovladač ·
main interface = hlavní obrazovka · zone = zóna · underfloor heating = podlahové vytápění · radiator = radiátor ·
fan coil = fancoil · mixing valve = směšovací ventil · three way valve = trojcestný ventil · buffer tank = akumulační nádrž ·
cascade = kaskáda · master/slave = řídicí/podřízená jednotka · auxiliary heat source = přídavný zdroj tepla ·
internal electric heater = vestavěný elektrický ohřev · tank heater = topná vložka zásobníku · sterilization = sterilizace (antilegionella) ·
silent mode = tichý režim · holiday mode = režim dovolená · weather/temperature compensation curve = ekvitermní křivka ·
PV direct drive = přímé napájení z FV · power limit = omezení příkonu · smart grid = Smart Grid ·
mainboard = řídicí deska · indoor/outdoor mainboard = vnitřní/venkovní řídicí deska · wiring = zapojení ·
Single-phase / Three-phase = jednofázové / třífázové · Product Data = Technické údaje · Thanks! = Děkujeme
