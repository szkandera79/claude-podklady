# SVJ a bytová družstva v lokalitách s drahým teplem z CZT (2026)

Seznam potenciálních klientů pro zelenou kotelnu: SVJ a bytová družstva v obcích / na adresách,
kde je teplo z centrálního zásobování (CZT) drahé. Vzniklo 22. 9. 2026.

**Soubor:** `SVJ a BD – drahé teplo CZT 2026.xlsx` (37 751 subjektů)

| List | Obsah |
|---|---|
| A – přesné adresy (200) | adresa domu je přímo cenovou lokalitou v ceníku ERÚ → cena se týká tohoto domu |
| B+C – obce s drahým CZT | B = cena CZT ≥ 1 250 Kč/GJ s DPH (21 743), C = 1 140–1 250 Kč/GJ (15 808); napojení domu na CZT **ověřit** |
| Souhrn podle obcí | 43 obcí, cena tepla, počty SVJ / BD |
| Jak s tím pracovat | zdroje, priority, pravidla oslovování |

## Zdroje
- Ceny tepla: ERÚ, předběžné ceny tepelné energie k 1. 1. 2026 (PDF), úroveň domovní předávací stanice /
  sekundární rozvod, vč. DPH. Stejná data jsou v artefaktu https://claude.ai/artifact/56cq7XoAz7XYuJKZjdPnVr
- Subjekty: ARES REST API (právní forma 145 SVJ, 205/233 družstva — jen bytová dle názvu nebo NACE 68.20/68.32,
  bez subjektů v likvidaci). Velká města se dotazují po PSČ z RÚIAN (ARES vrací max. 1 000 výsledků na dotaz).

## Oslovování — DŮLEŽITÉ
- **Žádné hromadné e‑maily ani zprávy do datových schránek bez souhlasu.** Nevyžádaná obchodní sdělení
  e‑mailem zakazuje § 7 zákona č. 480/2004 Sb. i vůči právnickým osobám (dozor ÚOOÚ); obchodní sdělení
  do datové schránky bez souhlasu je přestupek (DIA). Proto seznam e‑maily ani ID datových schránek neobsahuje.
- Doporučeno: **dopis na adresu sídla** (u SVJ = adresa domu) k rukám výboru, se vzorovou nabídkou
  (`vzor-bytove-domy/`). Souhlas s e‑mailem získat až od těch, kdo se ozvou.

## Sledovač leadů (artefakt)
`src/gen_tracker.py` + `src/tracker.template.html` → `tracker.html`, publikováno jako artefakt
https://claude.ai/artifact/JnHmVf43SfzzrusmBizAUL (republikovat přes parametr `url`).
Přístupné z mobilu i dalších zařízení; stav oslovování (nový / dopis odeslán / kontaktováno / zájem /
schůzka / nezájem), poznámky a datum se ukládají ve sdílené databázi artefaktu, **ne do CSV**.
Kontakty se opravují v CSV → znovu spustit generátor a republikovat. Tlačítko „Stáhnout CSV" vyexportuje
kontakty i s obchodním stavem.

## Aktualizace (nový ceník ERÚ vychází k 1. 1.)
Skripty v `src/` (Python 3, openpyxl), spouštět z `src/`:
1. Stáhnout PDF ERÚ jako `eru2026.pdf` a `python3 parse_eru.py` → `eru2026.json`.
2. Upravit cílové obce a ceny v `targets.json` (obec: [cena s DPH, lokalita ERÚ]).
3. `python3 svj.py` → `svj_db.json` (stahuje z ARES, lze přerušit a navázat); nejednoznačné názvy obcí
   mají pevný kód v `FIX` uvnitř `svj.py`.
4. `python3 street.py` → `street_hits.json` (SVJ přímo na adresách z ceníku ERÚ).
5. `python3 build_xlsx.py` → XLSX o úroveň výš.

Mezisoubory (`*.json`, adresní CSV z RÚIAN) se necommitují — jsou velké a dají se kdykoli vygenerovat znovu.
