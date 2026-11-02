# BD Jandova 7 — nabídka rev. 1 s jednotkami RHX30 Pro (2. 11. 2026)

Aktualizace nabídky 2026-09-BDJ-01 (2× REO X50) → **2026-11-BDJ-02: 3× RHX30 Pro na střeše**, stejný obchodní
model (vnitřek kotelny + jednotky; pronájem jednotek se splátkami, servis ve splátce). Přípojka CZT zůstává jako záloha.

## Dimenzování
Ztráta 30 kW při −15 °C (odhad). RHX30 Pro 19,0 kW při A−15/W55 (mapa výrobce) → **2 jednotky = 38 kW kryjí ztrátu
zcela**, 3. jednotka = výkonová rezerva (souběh ÚT + TUV) a záloha; při poruše kterékoli zbývá 38 kW. Bez el. patron.

## Klíčová čísla (bez DPH) — `src/model.py`
| | |
|---|---|
| Cena | 740 000 vnitřek + 2 × 350 000 + 3. jednotka 210 000 (sleva 40 %) = **1 650 000 Kč** (ceny jednotek zadal uživatel 2. 11.) |
| Provoz | elektřina 40,9 MWh = 143 200 + servis 35 000 = **178 200 Kč/rok** (404 Kč/GJ) |
| Úspora / návratnost | **354 900 Kč/rok (67 %) · 4,6 roku** |
| Pronájem 120 měs. | splátka 18 700 Kč/měs (7 200 × 2 + 4 300, poměrem ceny ze vzoru 6 800/330 tis.), úspora 165 500 Kč/rok, vstup 740 000 |
| Bez vlastních peněz | pronájem + úvěr SVJ na vnitřek (5,5 %, 10 let, 8 031 Kč/měs) → 464 000 Kč/rok, **o 69 100 Kč méně než Veolia** |
| FV (volitelně) | 10 panelů / jednotku ≈ 5 kWp, ≈ 55 000 Kč (odhad), 9–12 tis. Kč/rok |

Pozn.: úvěr SVJ na **celou** kotelnu (17 907 Kč/měs) by vyšel levněji než pronájem jednotek (140 000 Kč/rok pod Veolií) —
v podkladech pro klienta záměrně neuvedeno, rozhodnutí na obchodníkovi.

## Soubory
- `nabidka.html` — cenová nabídka rev. 1 (interní blok se netiskne)
- `podklady-predseda.html` — 10 bodů, 4 cesty financování, otázky a odpovědi, co připravit
- `podklady-schuze.html` — list pro vlastníky „Proč hlasovat pro novou kotelnu“ + vzor usnesení
- `schema-rhx30.svg` ← `src/gen_schema.py`; `src/build.py` skládá všechny tři HTML (styl `src/style.css`, těla `src/*.body.html`)
- `pdf/` — vytištěné PDF (kopie i v `~/Downloads/BD Zábřeh RHx50 nabídka/`)

```
python3 bd-jandova/rhx30/src/gen_schema.py && python3 bd-jandova/rhx30/src/build.py
```
PDF: headless Chrome jako v `bd-jandova/README.md` (`file://…/nabidka.html`).

## ⚠️ Otevřené body
1. Splátky jsou přepočet poměrem ceny (350 / 210 tis. vůči 330 tis.) — potvrdit s financující stranou.
2. Splátky a úvěr orientační; ceny převzaté z modelu X50 / vzoru RHX30.
3. **Střecha**: statika, rám, kotvení, jeřáb, trasa potrubí do kotelny, zámraz — zatím „není v ceně“.
4. **Smlouva s Veolií**: stálé platby při ponechané přípojce, sjednaný výkon; úpravy předávací stanice pro zálohu.
5. FV u RHX Pro: limity dle výrobce 21. 10. 2026 (20 A, Uoc < 537 V, 1 × 10 ks); cena sady je odhad.
6. Otevřené body původní nabídky (ztráta výpočtem, jistič, teplotní spád, DPH) platí dál — `../README.md`.
