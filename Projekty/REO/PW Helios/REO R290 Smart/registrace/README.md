# Registrace REO R290 Smart – podklady (SVT / NZÚ, EPREL)

Podklady pro 13 modelů řady (RH06 1F … RH16 3F, RHX20 Pro, RHX30 Pro) ve dvou variantách. Vše generuje `build.py`
(`python3 build.py --pdf` = včetně PDF formulářů přes Microsoft Excel). Zdroje: `../../EU regulation SCOP Helios/` (formuláře
výrobce), `../../Helios Energy Label and ERP report/` (štítky, protokoly), `REO/R290 new models/H8 Keymark/` (certifikáty).

| Složka | Značka / model | Dodavatel | Obsah |
|---|---|---|---|
| `A_REO-HEATING/` | REO HEATING, RH06 1F … RHX30 Pro | Ria Trade, s.r.o. (dodavatel) | formuláře 811/2013 (xlsx+pdf), štítky, přehled |
| `B_Power-World/` | POWER WORLD, PWxx-DKXLRE1/3-H8 | výrobce Power World + Ria Trade jako dovozce | totéž + certifikáty HP KEYMARK 041-K032-23…31 a protokoly ErP |

Varianta B záměrně uvádí výrobce (uživatel 14. 10. 2026) – certifikáty HP KEYMARK jsou vydané na Power World; používat jen pro
registraci, ne pro marketing. Varianta A nesmí obsahovat odkaz na výrobce (`build.py` to kontroluje).

## Úpravy proti podkladům výrobce
- Formuláře: model ze jména souboru (opravena chyba výrobce – list 55 °C ve formuláři 30 kW nesl „PW20“), adresa doplněna
  o „Praha 10“, ve variantě B kontakt „Manufacturer … / Importer / supplier: Ria Trade“, tisk listu na 1 stranu A4,
  metadata (autor, vlastnosti WPS) přepsána.
- Štítky A: v obsahu PDF přepsáno „POWER WORLD“ → „REO HEATING“ a model (vložený Calibri), grafika a hodnoty beze změny
  (skript ověřuje, že čísla zůstala). Štítky B = originály výrobce.

## Otevřené body před podáním
1. **Varianta A a KEYMARK:** certifikáty i databáze keymark.eu znají jen modely PWxx. Pro registraci pod značkou REO HEATING
   je potřeba, aby výrobce přidal do HP KEYMARK obchodní značku/modely REO HEATING (tzv. alias / private label), nebo
   prohlášení výrobce o shodě RHxx = PWxx. Bez toho SVT nejspíš uzná jen variantu B.
2. Štítky uvádějí vnitřní hlučnost „00 dB“ (venkovní monoblok bez vnitřní jednotky) – převzato z originálu.
3. Formuláře deklarují TOL −10 °C a Tbiv −7 °C (zkušební deklarace podle EN 14825), ne skutečný provozní limit −25 °C.
4. „Equipped with a supplementary heater: NO“ u všech modelů (RH06–RH16 měřeny bez vestavěného dohřevu 3 kW; RHX dohřev nemají).
5. Formuláře jsou jen pro průměrné klima (pro ČR dostačující).
