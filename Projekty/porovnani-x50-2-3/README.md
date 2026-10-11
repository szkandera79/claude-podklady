# Porovnání variant — 2× vs. 3× REO X50 (podklad pro výbor SVJ)

Obecný porovnávací podklad k nabídce bytovému domu (bez jména klienta), vzniklý 21. 9. 2026 ze zadání:
- **Varianta A** 2× REO X50, AKU 2× 1 000 l, TUV 3× 1 000 l — **1 600 000 Kč** bez DPH
- **Varianta B** 3× REO X50, stejné nádrže — **1 990 000 Kč** bez DPH
- Data z podkladů výrobce ve složce `~/Claude/REO/RH X50 komerční/` výkonový protokol
  (`DATA.json` → kopie `src/rh-x50-data.json`), energetický štítek, technický manuál. Klíčové: **A−15/W55 24,8 kW,
  příkon 16,87 kW, COP 1,50**; A7/W35 49,3 kW, COP 3,80; štítek A++ (55 °C) / A+++ (35 °C); jistič 40 A/jednotku.

Struktura: shrnutí pro výbor · technické parametry · provoz při −15 °C · investice · provozní náklady ·
topná křivka a bod bivalence (graf) · rizika a mitigace · záruky a servis · srovnání s jinými nabídkami (bod A−15/W55) · cenový rámec · doporučení.
Styl a CSS převzaté z `vzor-bytove-domy/nabidka.html`.

## Soubory
- `nabidka.html` — dokument (tisk / PDF z prohlížeče), interní blok se netiskne.
- `src/model.py` — propočet z výkonové tabulky W55 (body bivalence, provoz při −15 °C, náklady); čísla v HTML přepsaná ručně.
- `src/gen_chart.py` — graf topné křivky kaskády 2×/3× vs. potřeba domu → `topna-krivka.svg` + inline do `nabidka.html`
  (mezi `<!--KRIVKA-->`), spouštět z kořene repa: `python3 porovnani-x50-2-3/src/gen_chart.py`.

## Tisk do PDF
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --print-to-pdf="$HOME/Downloads/ThermaVera-porovnani-2x-3x-X50.pdf" \
  "file://$PWD/porovnani-x50-2-3/nabidka.html"
```

## Otevřené body
1. Vzorová nabídka a BD Jandova uvádějí 25 kW při **W50** — podle protokolu je to 24,8 kW při **W55** (při W50 ≈ 26 kW). Sjednotit.
2. Energetická třída: štítek A+++ (35 °C), manuál výrobce „ERP (35 °C): A" — ověřit v KEYMARK/EPREL.
3. Hluk: štítek 66 dB (akustický výkon) vs. manuál ≤ 62 dB(A); vnitřní hluk „00 dB" na štítku neuvádět.
4. KEYMARK je vystaven na výrobní typ jednotky — v nabídce jen zmínka o certifikaci bez čísla a držitele, certifikát se předává v originále.
5. Podíl tepla z patron (1–8 %) je odhad z bodu bivalence, ne z teplotních četností lokality.
6. Záruky a servis — doplnit konkrétní lhůty, reakční dobu, případnou garanci výkonu.
7. Konkurenční parametry/ceny záměrně neuvedeny — doplnit jen z konkrétních nabídek.
8. Ověřit, že u 3 jednotek stačí akumulace 2 000 l.
