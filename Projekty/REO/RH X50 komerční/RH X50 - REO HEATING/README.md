# RH X50 — podklady REO HEATING

Rebranding dokumentace k jednotce **PW150-DKZLRS-E** (Power World) na značku
**REO HEATING**, obchodní označení **RH X50**. Větší model PW300-DKZLRS-E
je v návodu přeznačen na **RH X100**.

Zdrojové soubory výrobce zůstávají v nadřazené složce `RH X50 komerční/` beze změny.

## Výstupy

| Soubor | Co to je |
|---|---|
| `RH-X50-vykonove-krivky.pdf` | Protokol výkonových charakteristik, 4 strany A4, česky. Postaven znovu v designu REO HEATING z `RH-X50-vykonove-krivky.html`. |
| `RH-X50-vykonove-krivky.html` | Zdroj protokolu (A4 na výšku, tisk do PDF přes Chrome). Data jsou v objektu `DATA` na konci souboru. |
| `RH-X50-energeticky-stitek.pdf` | Energetický štítek podle 811/2013, přeznačený na REO HEATING / RH X50. |
| `RH-X50-operating-manual-EN.pdf` | Návod k použití, 53 stran, anglicky — z anglického originálu výrobce (`rebrand-navod-en.py`). Snímky aplikace: název Wi‑Fi výrobce „pwwm“ → „MyWiFi“ (`ssid_fix.py`, i v CZ verzi). |
| `RH-X50-navod-k-pouziti.pdf` | Návod k použití, 53 stran, česky. Modelové kódy přeznačeny, logo a modelová řádka na titulce. |
| `rebrand-stitek.py`, `rebrand-navod.py`, `rebrand-navod-en.py`, `ssid_fix.py` | Skripty, kterými výstupy vznikly — spouštět ze složky `RH X50 komerční`. |

## Co se NEpřebrandovalo a proč

**HP Keymark** (`PW150-DKZLRS-E Keymark.pdf`) zůstává v originále. Je to certifikát
vydaný **BRE Global Ltd** držiteli **Power World Machinery Equipment Co. Ltd.**,
registrační číslo **041-K032-17**, platnost 14. 7. 2025 – 13. 7. 2035, s podpisem
konkrétní osoby. Přepsat na něm držitele by znamenalo padělání certifikačního
dokumentu. Zákazníkům se předává tak, jak je; pravost lze ověřit v databázi
<https://keymark.eu/en/products/heatpumps/certified-products>.

## K vyřešení před vydáním

1. **Energetický štítek uvádí u vnitřní hlučnosti `00 dB`.** Tak je to i v originálu
   výrobce — zjevně nevyplněný údaj. Před použitím štítku je potřeba doplnit
   skutečnou hodnotu, nebo pole vypustit, pokud se na venkovní jednotku nevztahuje.
2. **Registrace v EPREL.** Uvedením jednotky na trh pod vlastní značkou se REO HEATING
   stává „dodavatelem“ podle nařízení (EU) 2017/1369 a 811/2013 — s povinností
   registrovat model RH X50 ve vlastní databázové položce EPREL a vést technickou
   dokumentaci. Štítek v této složce je podklad, ne náhrada registrace.
3. **Chlazení — EER vs. COP.** V tabulce výrobce je poměr chladicího výkonu a příkonu
   nadepsán „COP“, v grafu „EER“. V protokolu je použito EER a rozdíl je uveden
   v poznámce pod čarou; číselné hodnoty jsou převzaty beze změny.

## Poznámky k datům

Hodnoty v protokolu jsou převzaty z `PW150-DKZLRS-E Performance Curve.pdf` programově
(ne ručně opsané) a zaokrouhleny na uvedený počet desetinných míst — výrobce u části
buněk uváděl čtyři desetinná místa, což je artefakt exportu z tabulkového procesoru.
Prázdné buňky (kombinace teplot mimo pracovní rozsah) jsou v tabulce označené „—“
a v grafech se křivka přeruší.
