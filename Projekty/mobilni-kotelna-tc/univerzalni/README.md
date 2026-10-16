# Univerzální mobilní kotelna REO HEATING (studie proveditelnosti)

Zadání 16. 10. 2026: opakovaně pronajímaná kotelna 50–100 kW (první zákazník: administrativa + temperovaná hala,
≈ 20 zaměstnanců, náhrada CZT na ≈ 6 měsíců, včetně TUV). Varianta A = RH050/RH060, varianta B = RH X50 (2 ks skladem).
Jednotky venku na rámech, technologie v kontejneru 20' (10' jako alternativa). Bez elektrokotle, bez glykolu (záměr zadavatele).

## Fáze
1. **Technická koncepce a rizika** — hotovo (`studie.html`, artefakt https://claude.ai/artifact/8E2vxJLSfd4n7GBTZbHnAh).
2. Konstrukce (3D, rámy, hutní materiál), hydraulika s dimenzemi, položkový seznam, dodavatelé a ceny, rozpočet.
3. Cenová mapa pronájmů, ekonomika zakázky (50/70/90 tis. Kč/měs), nájemní smlouva B2B.

## Soubory
- `src/vykony.json` — výkonové tabulky RH050, RH060, RH X50 (export z `REO/R290-datove-listy/src/data.js`).
- `src/vypocty.py` — všechny výpočty (kaskády, N−1, otopná tělesa, odhad zátěže z GJ, průtoky, hadice, AKU, expanze, TUV, výměník, přeprava, hluk, elektro).
- `src/gen_studie.py` — generuje `studie.html`: `python3 mobilni-kotelna-tc/univerzalni/src/gen_studie.py` (z kořene repozitáře; spouštět ve složce `src` kvůli importu).

## Klíčové závěry fáze 1
- RH050/RH060 při A−15/W55 ≈ 51 % nominálu; „50 kW nominálně“ = ≈ 30 kW v mrazu → varianta A jen pro malé objekty.
- RH X50 ověřena: 49,3 kW A7/W35, 24,8 kW A−15/W55, 20,8 kW A−20/W55; bez vestavěného čerpadla, jm. průtok 10,32 m³/h, Δp až 80 kPa, kaskáda až 8 ks (RS485).
- 2 × RH X50 = 49,6 kW při −15/W55 → N+1 jen do ≈ 25 kW zátěže.
- Doporučeno: glykolový primár + VS1 v kontejneru; AKU 1 000 l + 2–3 × TUV 300 l; kmen DN80 pro 2 × X50; hadice DN50 (DN65 pro 100 kW).
- Otevřené: viz kap. 13 studie (data výrobce, výkresy zásobníků, cena AKU 5 000 Kč, RH050 1f/3f).
