# Nákupní ceny — Power World a nádrže

Interní přehled toho, co platíme výrobcům: skutečně fakturované ceny a aktuální ceníky.
Artefakt: https://claude.ai/artifact/ETdzEjVpW4aTExHd4ST7WC (republikovat přes parametr `url`).

Data jsou napsaná přímo v `index.html` (objekt `SECTIONS`) — při novém ceníku se mění tam
a stránka se znovu publikuje. Kurzy USD/EUR jdou na stránce přepsat, přepočet na Kč se dopočítá.

## Zdroje
| Sekce | Zdroj |
|---|---|
| Skutečně nakoupeno | `PW Obchodní/PW invoice 25 CI&PL DGPW 20250829-01S.pdf` (12. 9. 2025), `PW order 23 PI -DGPW 20231020-01S` (20. 10. 2023) |
| REO R290 Smart | `REO/PW Helios/Power World R290 Helios Heat Pump Technical Specification 2026-10-14.xls`, list „built in hydro box" |
| REO RHX Pro | `REO/PW Helios/Power World Helios Pro 20KW 30KW Price List (3).xls` (14. 10. 2026) |
| REO R290 (Cleanlife) | `PW Obchodní/25Power World R290 Cleanlife Heat Pump Price List (Add new models).pdf` (27. 9. 2026) |
| Komerční jednotky | `PW Obchodní/Power World R290 Commercial Heat Pump Price List.pdf` |
| Nádrže | `Wok/2026042102 … Riva Trade, S.R.O(1).pdf` — proforma faktura 21. 4. 2026, FOB Guangzhou |
| Sklad Frankfurt | `PW Obchodní/Quotation List--Frankfurt warehouse.pdf` (4. 9. 2025), EXW Frankfurt v eurech |

## Pozor
- Všechny ceny bez DPH, **bez dopravy a cla** (EXW Čína, nádrže FOB Guangzhou).
- Ceníky Power World jsou vázané na kurz USD/RMB 7; při odchylce nad 1 % se cena mění.
- Dodavatel nádrží se **nesmí objevit ve veřejných výstupech** (katalogy, letáky) — tenhle podklad je interní.
- Prodejní ceny a marže jsou v `porovnani-x50-rh060/`, náhradní díly v `reo-nahradni-dily/`.
