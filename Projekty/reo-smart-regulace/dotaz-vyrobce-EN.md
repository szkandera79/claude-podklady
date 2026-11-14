# Dotaz výrobci – otevřené body instalačního standardu v1.0

Připraveno 14. 11. 2026 k odeslání výrobci (kontakt z dotazu k FV 13. 10. 2026). Odkazy na kapitoly odpovídají
CZ návodu (99 str.) a anglické instalační příručce řady H8. Po odpovědi doplnit README a kap. 15 standardu.

---

**Subject:** R290 monobloc H8 series (PW06–PW16, PW20, PW30) – hydraulic and control questions for our installation standard

Dear Sophie,

we are preparing an installation standard for our installers covering hydraulic layouts and room temperature control of your R290 monobloc heat pumps (PW06–PW16 single/three-phase, PW20, PW30). While working through the User & Installation Manual and the Technical Installation Manual (H8 series), we found several points that are not described or that differ between the documents. Could you please confirm the following?

**1. Buffer tank and direct connection**
Technical Installation Manual, chapter 4.4, states that users must install a buffer tank. Is a direct connection without a buffer tank ever acceptable, e.g. for underfloor heating with all loops permanently open? If yes, what is the minimum water volume of the heating circuit (litres per kW or per model)? Is a buffer tank connected in series in the return line acceptable as an alternative to the parallel buffer shown in your application drawings?

**2. Built-in circulation pump**
How is the built-in pump controlled: does it run continuously, only together with the compressor, or with an overrun after the compressor stops? Does it run in standby when there is no heating demand (e.g. room thermostat open)? Can the pump speed or operating mode be set? Please send the pump curve (head vs. flow) for each model, so that we can calculate the external head available at nominal flow.

**3. Three-way valve SV1 – defrost and polarity**
Technical Installation Manual 6.2.6 states that SV1 is ON in hot water, defrost and antifreeze mode. Please confirm that during defrost the unit takes heat from the DHW tank through SV1.
How does defrost work in installations without a DHW tank and without SV1? What minimum water volume or flow is needed in that case?
The User Manual (chapter 2.7, Application 1) says "S3V1 keeps OFF" in DHW mode and "S3V1 keeps ON" in heating mode, which is the opposite of chapter 6.2.6. Which terminal (ON or OFF) must be connected to the DHW coil port of the valve?

**4. Room temperature control (PANEL_CTRL 1ZONE.TA)**
When PANEL_CTRL = 1ZONE.TA, which leaving water temperature does the unit produce: the selected climatic curve (e.g. Curve #9), or the fixed setpoint HEAT_TEMP_SET?
Is PANEL_CTRL relevant at all when a room thermostat is used (RT_CTRL = ZONE.A.SWITCH or 2 ZONE.SWITCH)? Which PANEL_CTRL value do you recommend in that case?
What is the setting range of ROOM_TEMP_dT, HEAT_LOAD_dT and HEAT_UNLOAD_dT?

**5. Antifreeze (glycol)**
Technical Installation Manual 4.1 says that the secondary circuit must be filled only with water according to VDI 2035, not with a medium containing antifreeze. Chapter 4.10 and the User Manual recommend antifreeze because of power failures. Is glycol allowed in the circuit of the unit? If yes, which type and maximum concentration, and how should the unit be configured (e.g. capacity or protection settings)? Do you accept an antifreeze (drain) valve on the outdoor piping as an alternative?

**6. Minimum water flow**
What is the minimum water flow (m³/h) for each model, and at what flow does the flow switch trip?

**7. Wired controller**
Where is the wired controller delivered (mounted on the unit or loose)? What is the length of the supplied cable, and what is the maximum length and recommended cable type for an extension? We need to install the controller indoors to use its room temperature sensor.

**8. Room thermostat terminals**
Is there any voltage on terminals L1/L2 (H1, C1, H2), or are they potential-free inputs? Which thermostat contact rating is required?

**9. Mixing valve and buffer sensors**
For the zone B mixing valve (terminals AIV1/AOV1/GND): what control signal is used (0–10 V or other), and what feedback signal is expected? Please recommend a compatible valve actuator.
Which parameter activates the upper and lower buffer tank sensors (T8/AI3, T7/AI2), and how does the unit use them in control?

**10. Sizing data**
What buffer tank volume do you recommend for PW20 and PW30? What DHW coil area is required for PW16 (the table in chapter 4.2.3 of the Technical Installation Manual does not list it)?

Thank you very much for your help. Clear answers to these points will allow us to release the standard to our installers.

Best regards,

---

## České shrnutí (pro interní kontrolu)
1. Je přípustné zapojení bez AKU / jaký minimální objem / je přípustná sériová AKU?
2. Řízení vestavěného čerpadla a jeho křivka.
3. SV1 při odmrazování, provoz bez TUV, polarita SV1 (rozpor návod 2.7 × příručka 6.2.6).
4. Teplota vody při 1ZONE.TA, PANEL_CTRL při termostatu, rozsahy hysterezí.
5. Glykol (rozpor příručka 4.1 × 4.10) a protizámrazový ventil.
6. Minimální průtok.
7. Ovladač – umístění při dodání, kabel.
8. Napětí na svorkách termostatu.
9. Signál směšovacího ventilu, aktivace čidel AKU.
10. AKU pro PW20/PW30 (= RHX20/30 Pro), spirála TUV pro PW16 (= RH16).

---

## Český překlad dotazu (pro kontrolu obsahu)

**Předmět:** Monoblok R290 řady H8 (PW06–PW16, PW20, PW30) – dotazy k hydraulice a regulaci pro náš instalační standard

Dobrý den, Sophie,

připravujeme pro naše montážní firmy instalační standard, který pokrývá hydraulická zapojení a regulaci vnitřní teploty u vašich tepelných čerpadel R290 v provedení monoblok (PW06–PW16 jednofázová i třífázová, PW20, PW30). Při práci s návodem k obsluze a instalaci a s technickou instalační příručkou (řada H8) jsme narazili na několik bodů, které v podkladech nejsou popsány nebo se v jednotlivých dokumentech liší. Mohli byste nám prosím potvrdit následující?

1. **Akumulační nádrž a přímé zapojení.** Technická instalační příručka v kapitole 4.4 uvádí, že akumulační nádrž musí být instalována. Je někdy přípustné přímé zapojení bez akumulační nádrže, např. u podlahového vytápění s trvale otevřenými smyčkami? Pokud ano, jaký je minimální objem vody v otopném okruhu (litry na kW nebo podle modelu)? Je přípustná akumulační nádrž zapojená sériově ve vratce jako alternativa k paralelní nádrži z vašich aplikačních schémat?
2. **Vestavěné oběhové čerpadlo.** Jak je vestavěné čerpadlo řízeno: běží trvale, jen společně s kompresorem, nebo s doběhem po zastavení kompresoru? Běží v pohotovostním stavu, když není požadavek na vytápění (např. rozepnutý pokojový termostat)? Lze nastavit otáčky nebo provozní režim čerpadla? Pošlete nám prosím křivku čerpadla (výtlak v závislosti na průtoku) pro každý model, abychom mohli spočítat dostupný externí výtlak při jmenovitém průtoku.
3. **Trojcestný ventil SV1 – odmrazování a polarita.** Technická instalační příručka v kapitole 6.2.6 uvádí, že SV1 je ve stavu ON v režimu ohřevu TUV, odmrazování a ochrany proti zamrznutí. Potvrďte prosím, že při odmrazování jednotka odebírá teplo ze zásobníku TUV přes SV1. Jak probíhá odmrazování u instalací bez zásobníku TUV a bez SV1? Jaký minimální objem vody nebo průtok je v takovém případě potřeba? Návod k obsluze (kapitola 2.7, Aplikace 1) uvádí, že v režimu TUV „S3V1 zůstává VYP“ a v režimu vytápění „S3V1 zůstává ZAP“, což je opak kapitoly 6.2.6. Která svorka (ON, nebo OFF) se má připojit k vývodu ventilu vedoucímu do spirály zásobníku TUV?
4. **Regulace podle prostorové teploty (PANEL_CTRL 1ZONE.TA).** Jakou teplotu výstupní vody jednotka vyrábí při PANEL_CTRL = 1ZONE.TA: podle zvolené ekvitermní křivky (např. Curve #9), nebo podle pevné žádané hodnoty HEAT_TEMP_SET? Má PANEL_CTRL vůbec vliv, pokud je použit pokojový termostat (RT_CTRL = ZONE.A.SWITCH nebo 2 ZONE.SWITCH)? Jakou hodnotu PANEL_CTRL v takovém případě doporučujete? Jaký je rozsah nastavení parametrů ROOM_TEMP_dT, HEAT_LOAD_dT a HEAT_UNLOAD_dT?
5. **Nemrznoucí směs (glykol).** Technická instalační příručka v kapitole 4.1 uvádí, že sekundární okruh se smí plnit pouze vodou podle VDI 2035, nikoli médiem s nemrznoucí přísadou. Kapitola 4.10 a návod k obsluze naopak nemrznoucí směs kvůli výpadkům proudu doporučují. Je glykol v okruhu jednotky přípustný? Pokud ano, jaký typ a jaká maximální koncentrace, a jak je třeba jednotku nastavit (např. výkon nebo ochrany)? Akceptujete jako alternativu protizámrazový (vypouštěcí) ventil na venkovním potrubí?
6. **Minimální průtok vody.** Jaký je minimální průtok vody (m³/h) pro jednotlivé modely a při jakém průtoku vypne průtokový spínač?
7. **Kabelový ovladač.** Jak je kabelový ovladač dodáván (namontovaný na jednotce, nebo volně)? Jak dlouhý je dodávaný kabel a jaká je maximální délka a doporučený typ kabelu pro prodloužení? Ovladač potřebujeme instalovat uvnitř, abychom mohli využít jeho čidlo prostorové teploty.
8. **Svorky pokojového termostatu.** Je na svorkách L1/L2 (H1, C1, H2) nějaké napětí, nebo jde o bezpotenciálové vstupy? Jaké zatížitelnosti musí být kontakt termostatu?
9. **Směšovací ventil a čidla akumulační nádrže.** Jaký řídicí signál se používá pro směšovací ventil zóny B (svorky AIV1/AOV1/GND) – 0–10 V, nebo jiný – a jaký signál zpětné vazby jednotka očekává? Doporučte nám prosím kompatibilní pohon ventilu. Kterým parametrem se aktivují čidla horní a dolní části akumulační nádrže (T8/AI3, T7/AI2) a jak je jednotka využívá při regulaci?
10. **Údaje pro dimenzování.** Jaký objem akumulační nádrže doporučujete pro PW20 a PW30? Jaká plocha spirály zásobníku TUV je potřeba pro PW16 (tabulka v kapitole 4.2.3 technické instalační příručky ho neuvádí)?

Velmi děkujeme za pomoc. Jasné odpovědi na tyto body nám umožní předat standard našim montážním firmám.

S pozdravem
