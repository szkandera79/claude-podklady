# Zápis ze schůzky s investorem (RDM) — technická korekce

Opraveno proti výkonovému protokolu RH X50 a projektu kotelny
(TV-BDM-04/05). Změny jsou vypsané na konci.

## Opravené znění

**Doporučená varianta je dvojí:**
- Minimální 2× TČ + elektrická bivalence (nutná).
- Vhodnější 3× TČ, kde třetí jednotka nahrazuje robustní bivalenci. Elektrická bivalence
  zůstává i tak, ale jen v doplňkovém rozsahu (dezinfekce zásobníků TUV, odběrové špičky).

**Podmínky pro porovnání nabídek.** Rozlišit katalogový bod a návrhový bod:
- Katalogový bod pro srovnání nabídek: topení A7/W35, ohřev TUV A7/W55.
- Návrhový bod, podle kterého se zdroj dimenzuje: A−15/W35 pro topení a A−15/W55 pro TUV.
  Při +7 °C má jednotka dvojnásobný výkon než při −15 °C, takže porovnání jen při +7 °C
  o krytí tepelné ztráty nevypovídá.
- Tepelná ztráta objektu 52 kW platí pro venkovní teplotu −15 °C.
- Akumulace topné vody 2× 1 000 l, zásobníky TUV 3× 1 000 l (125 l/b.j. při 24 bytech;
  podle odběrového diagramu zvážit 4. zásobník).

**Výkon RH X50 (protokol výrobce):**

| Bod | Výkon | COP |
|---|---|---|
| A7/W35 (katalog, topení) | 49,3 kW | 3,80 |
| A7/W55 (katalog, TUV) | 41,7 kW | 2,50 |
| A−15/W35 (návrh, topení) | 30,9 kW | 2,10 |
| A−15/W55 (návrh, TUV) | 24,8 kW | 1,50 |

**Řešení 2× TČ (52 kW ztráta):**
- Topení: 2 × 30,9 = 61,8 kW při −15 °C, tj. 119 % ztráty — pokryje s rezervou.
- Ohřev TUV má přednost. Po dobu nabíjení zásobníků dělá jedna jednotka TUV (24,8 kW při −15 °C)
  a na topení zbývá jediná jednotka, tedy 30,9 kW. **Chybí 21,1 kW.** Výkony pro topení a TUV
  se nesčítají — jednotka v daný okamžik buď topí, nebo ohřívá TUV.
- Proto je nutná bivalence ve dvou stupních:
  - krytí deficitu při souběhu s TUV: 2 × 11 kW průtokové patrony (21,1 kW),
  - krytí výpadku jedné jednotky: elektrokotel min. 30 kW (zbývá 30,9 kW z 52 kW, a při
    souběhu s ohřevem TUV nezbývá na topení nic).

**Jak často deficit nastane.** Jedna jednotka pokryje potřebu domu až do −5,6 °C, takže do té doby
deficit nevzniká vůbec. Při −7 °C chybí 3,5 kW, při −10 °C 10,5 kW, plných 21 kW až při −15 °C.
Teplo uložené v soustavě navíc nedostatek oddálí: akumulace 2× 1 000 l drží asi 19 kWh (zhruba
50 minut plného deficitu) a betonová deska podlahového vytápění řádově 100 kWh na každý stupeň
předehřátí. Denní bilance při −15 °C vychází kladně — 5,5 hodiny nabíjení TUV znamená deficit
122 kWh, zatímco ve zbývajících 18,5 hodiny má kaskáda volnou kapacitu 163 kWh. Podle modelu
naskočí bivalence asi 16 hodin za rok. Je to pojistka pro dlouhý mráz, ne zdroj pro běžný provoz.

**Řešení 3× TČ (52 kW ztráta):**
- Topení: 3 × 30,9 = 92,7 kW při −15 °C, tj. 178 % ztráty.
- Při nabíjení TUV topí dvě jednotky (61,8 kW > 52 kW), takže **deficit nevzniká**.
- Při výpadku jedné jednotky zbývají dvě, tedy 61,8 kW — plné krytí bez elektřiny.
- Elektrokotel odpadá. Zůstává doplňková patrona 11 kW pro dezinfekci TUV (65 °C tepelné
  čerpadlo nedosáhne) a pro odběrové špičky.

**Srovnání příkonu na krytí stejného deficitu 21,1 kW při −15 °C:**
- elektrokotel: 21 kW elektrického příkonu (účinnost 100 %),
- třetí tepelné čerpadlo: cca 10 kW elektrického příkonu (COP 2,10 při −15 °C/35 °C),
  přičemž celá jednotka dá 30,9 kW tepla za 14,9 kW příkonu.
- Elektrokotel 50 kW by odpovídal krytí celé tepelné ztráty bez tepelných čerpadel, ne krytí deficitu.

**Rezervovaný příkon:**
- 2× TČ + bivalence: jednotky 31,8 kW + elektrické zdroje 52 kW → návrh ≈ 62 kW, jistič 3× 100 A.
- 3× TČ + doplňková patrona: jednotky 46,7 kW + 11 kW → návrh ≈ 47 kW, jistič 3× 80 A.
- V obou případech se počítá s hlídačem hlavního jističe, který odpojí nejdřív bivalenci.

**Cenový rozdíl:** podle ceníku z 23. 9. 2026 stojí třetí jednotka 390 000 Kč bez DPH, zatímco
bivalence, kterou nahradí, jen 90 000 Kč (2× průtokový dohřev 11 kW po 20 000 Kč + elektrokotel
30 kW za 50 000 Kč). **Čistý rozdíl je 300 000 Kč, jak uvádí zápis.** Topné spirály 9 kW s termostatem
do každé nádrže (5 × 12 000 Kč, celkem 45 kW instalovaných) a podružný rozvaděč k tepelným čerpadlům a spínání bivalence (40 000 Kč)
jsou v obou variantách stejné. Celkem 1 790 000 Kč (2 TČ) proti 2 090 000 Kč (3 TČ).

**Ostatní body:**
- CN bude obsahovat provedení v mědi i v oceli. Dimenze z projektu: větve jednotek DN50
  (Cu 54×2), potrubí k výměníku TUV DN80 (Cu 88,9×2), přívod do akumulace DN100 (Cu 108×2,5),
  sběrač a rozdělovač DN150. Dimenze jsou předběžné, platí po výpočtu tlakových ztrát.
- Jindra ověří dálkový odečet tepla: kalorimetry v MID provedení s M-Bus nebo Modbus.
  Měření chladu má smysl jen tehdy, pokud se počítá s chlazením — v současném projektu kotelny
  zdroj chladu není, tepelná čerpadla jsou navržena jako topná. K potvrzení.
- CN na podlahové vytápění — dodá PS.

## Co bylo opraveno a proč

1. **Sčítání výkonů topení a TUV.** V zápise je „2× TČ ... TUV dává 2× 24,8 kW". Jednotka v daný
   okamžik topí, nebo ohřívá TUV. Správně: při ohřevu TUV zbývá na topení o jednu jednotku méně.
2. **Podmínky porovnání.** Bod +7 °C je katalogový; dimenzování se dělá na −15 °C, kde je výkon
   zhruba poloviční (30,9 proti 49,3 kW).
3. **Elektrokotel 50 kW vs 21 kW u třetí jednotky.** Zaměněn tepelný výkon s elektrickým příkonem
   a deficit s celkovou ztrátou. Deficit je 21,1 kW tepla; elektrokotel na něj potřebuje 21 kW
   elektřiny, třetí tepelné čerpadlo asi 10 kW.
4. **„3× TČ bez bivalence".** Doplňková patrona zůstává kvůli dezinfekci zásobníků TUV.
5. **Cenový rozdíl 300 tis. Kč** v zápise je podle ceníku z 23. 9. 2026 správně (dřívější odhad
   190 tis. Kč vycházel z vyšších cen bivalence).
6. **Výpadek jednotky** u varianty se dvěma TČ doplněn jako samostatný důvod pro elektrokotel.

## K ověření
1. **Tepelná ztráta 52 kW** proti PENB č. 530077.2, kde je 53 kW. Rozdíl je pro návrh zanedbatelný,
   ale čísla je potřeba sjednotit.
2. **Počet bytů 24** potvrzen investorem. PENB a výkresy DPS počítají s 27 byty, proto je roční
   potřeba TUV přepočtena poměrem 24/27 na 50,07 MWh (137 kWh/den). Potvrdit skladbu bytů.
3. **Chlazení a měření chladu** — je vůbec v projektu?
