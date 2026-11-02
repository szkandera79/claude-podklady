# BD u Dolu Michal — nabídka rev. 1 s jednotkami RHX30 Pro (2. 11. 2026)

Aktualizace nabídky TV-BDM-NAB-A/B (9/2026, 2× / 3× RH X50) → **TV-BDM-NAB-02: kaskáda RHX30 Pro**, po vzoru
`bd-jandova/rhx30/`. Investor (developer), oslovení „Vážení pánové“, novostavba 24 b.j., ztráta 53 kW, podlahovka 35/30 °C.

## Varianty (bez DPH)
| | A — 3× RHX30 Pro | B — 4× RHX30 Pro (doporučená) | září B — 3× RH X50 |
|---|---|---|---|
| Výkon −15 °C / W35 | 67,2 kW (127 %) | 89,6 kW (169 %) | 92,7 kW |
| Souběh s TUV | 44,8 kW + spirály AKU (deficit 8,2 kW) | 67,2 kW, bez deficitu | 61,8 kW |
| Výpadek jednotky | 44,8 kW + spirály AKU 18 kW | 67,2 kW (127 %) | 61,8 kW |
| Elektřina / rok (model) | 42,4 MWh · SCOP 3,71 · 148 500 Kč | 42,1 MWh · SCOP 3,74 · 147 500 Kč | 48,6 MWh · 3,24 · 170 100 Kč |
| Cena | 1 890 000 Kč | **2 100 000 Kč** | 2 090 000 Kč |
| Investice + elektřina 15 let | 4 117 200 Kč | 4 312 200 Kč | 4 641 800 Kč |

Cena = vnitřek 740 000 + spirály 60 000 + rozvaděč 40 000 + 3 × 350 000 (+ 4. jednotka 210 000, sleva 40 %).
Ceny jednotek stejné jako u BD Jandova — **potvrzeno uživatelem 2. 11. 2026**.

## Model (`src/model.py`)
Přebírá dům, binovou křivku a TUV z `../src/model.py`. **Nově provoz při částečném výkonu**: kaskáda v každém binu volí
počet běžících jednotek, COP interpolací MIN↔MAX výkonové mapy (pod MIN cykluje, ×0,9); TUV jedna jednotka na plný výkon W55.
Zářijové RH X50 přepočteny stejně (SCOP 3,24 místo 3,15). `--max` = stará metoda (vše na MAX).
Data RHX30 Pro: `src/rhx30-data.json` ← `~/Claude/REO/R290-datove-listy/src/data.js` (mapa PW30…Performance curve.xls).
Proč RHX30 vychází lépe: při −15 °C COP téměř shodný (2,13 vs 2,10), ale při částečném výkonu RHX30 COP roste (MIN +7 °C 5,36), X50 klesá (4,30).

## Soubory
- `nabidka.html` — cenová nabídka rev. 1 (interní blok se netiskne), 6 stran A4
- `podklad-spolecnici.html` — podklad pro jednání společníků: 8 předností, efektivita, celkové náklady 15 let, záloha, přínosy pro developera, tabulka pro konkurenci
- `schema-rhx30.svg` ← `src/gen_schema.py` (4 jednotky, varianta A = bez TČ 4); `src/build.py` skládá HTML (styl `src/style.css`, těla `src/*.body.html`)
- `pdf/` — vytištěné PDF

```bash
python3 bd-michal-nabidka/rhx30/src/model.py
```
```bash
python3 bd-michal-nabidka/rhx30/src/gen_schema.py && python3 bd-michal-nabidka/rhx30/src/build.py
```
PDF: headless Chrome (`--print-to-pdf`, `file://…/nabidka.html`) jako v `bd-jandova/README.md`.

## Artefakt
https://claude.ai/artifact/6FH8VjLb28LZHDfpVCph6b — dvě záložky + „Stáhnout PDF k tisku“.
`python3 bd-michal-nabidka/rhx30/src/build_artefakt.py <výstup.html>` → publikovat na stejnou URL s `capabilities {"downloads": true}`
a `files` = `pdf/<název>.pdf` ← `bd-michal-nabidka/rhx30/pdf/`.

## ⚠️ Otevřené body
1. Hluk: LWA 59 dB(A) (štítek RHX30 Pro) vs 66 (RH X50); hluková studie není v ceně.
2. FV přímo do jednotek (1 × 10 panelů / jednotku) vs projektovaná FVE 46 kWp — jen jako možnost, posoudit s projektantem FVE.
3. Servis (~40 000 Kč/rok za 4 jednotky) není v propočtu; pronájem jednotek jen zmíněn bez splátek.
4. Otevřené body původní nabídky platí dál (ztráta výpočtem, TUV objem, rezervovaný příkon, cena elektřiny) — `../README.md`.
