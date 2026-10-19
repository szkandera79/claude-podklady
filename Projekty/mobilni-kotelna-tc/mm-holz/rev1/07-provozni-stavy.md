# 07 – Provozní a poruchové stavy (rev1)

Výkony pocházejí z `02-vykonova-bilance.md`. Potřeba je převzatá z měření × 1,10. „Do −x °C“ znamená denní průměr venkovní teploty.

## 1. Provozní stavy

| Stav | Podmínka | TČ | EK | V3 | Výkon / pokrytí |
|---|---|---|---|---|---|
| Léto | T_e > 15,5 °C | stop | stop | zavřen | 0 |
| Monovalentní | T_e > ≈ −9,6 °C | 1–2 × X50, T_AKU,set ≤ 62 °C | blokovány | zavřen | TČ pokryjí celou potřebu |
| Bivalentní | T_e < −5 °C a deficit (kap. 4 v 06) | 2 × X50 max. | 1–7 stupňů (≤ 42 kW) | zavřen | při −18 °C: TČ 44,8 + EK 38,2 kW = 83 kW |
| Nouzový | obě TČ nedostupné | — | až 12 stupňů | otevřen | 72 kW, pokrytí do −13,5 °C |

## 2. Poruchové scénáře

| # | Scénář | Detekce | Automatická reakce | Zbývající výkon / dopad | Nezávislá ochrana (mimo PLC) |
|---|---|---|---|---|---|
| 1 | **Porucha jedné RH X50** | poruchový kontakt, chod bez nárůstu T1, Modbus | přepnout lead na zdravou jednotku, povolit EK i nad −5 °C, pokud deficit trvá; SMS servisu | 1 × X50 + max. 11 stupňů (proudový limit) → pokrytí do **−19,6 °C** | ochrany jednotky [D], jistič + RCD |
| 2 | **Porucha obou X50** | obě poruchy > 5 min | režim 3: EK jako samostatný zdroj, otevřít V3, SMS servisu + Alignum | **72 kW → do −13,5 °C.** Pod tím priority: 1) administrativa 20 °C, 2) hala sníženě (15 °C, ΔT_korekce −5 K). **72 kW nepokryje projektových 88 kW (resp. 105 kW), pokud by je objekt potřeboval.** Měřením je potřeba při −15 °C ≈ 76 kW. | STB, FS, PR, PV 3 bar |
| 3 | **Nedostatek výkonu TČ v silném mrazu** | T_S2 < T_req − 2 K a integrál D (06, kap. 4) | bivalentní režim, stupně po 5 min, TČ zůstávají na max. | při −18 °C deficit 38 kW = 7 stupňů; proud ≈ 111 A < 136 A | PR 150 A |
| 4 | **Výpadek jednoho elektrokotle** (blok 4 × 6 kW) | STB / jistič / zpětné hlášení KM bez nárůstu T_EK, nesymetrie proudu | vyřadit blok z rotace, pokračovat zbylými 8 stupni (48 kW), alarm | bivalence beze změny (potřeba ≤ 42 kW); nouzově 48 kW → do −3,8 °C | STB bloku, jistič 40 A |
| 5 | **Porucha teplotního čidla** | mimo rozsah (< −40 / > 120 °C), skok > 10 K/10 s, nesoulad s druhým čidlem > 8 K | T_e: náhradní hodnota z X50 (vlastní venkovní čidlo [D]), jinak T_req = 60 °C. T_mid/T_bot: použít čidla AKU 2. T_S2: řídit dle T_EK − 2 K. **T_EK: EK okamžitě vypnout** (bez náhrady) | vytápění pokračuje, EK jen pokud je T_EK v pořádku | STB na každém EK nezávisle na čidlech PLC |
| 6 | **Překročení povoleného el. zatížení** | I_max > 136 A / 60 s nebo ≥ 150 A | odpojit stupně EK v obráceném pořadí rotace; TČ se neomezují; při trvání bez EK omezit TČ2 + alarm | krátkodobé snížení výkonu, AKU pokryje (2 000 l × 10 K ≈ 23 kWh ≈ 20 min při 68 kW) | proudové relé PR → KM-EK0, hlavní jistič 160 A |
| 7 | **Porucha čerpadla / nedostatečný průtok** | P2: chod TČ bez Δt nebo porucha měniče; P4: FS; P1: porucha průtoku X50 [D]; soustava: tlak < 1,0 bar | P2: TČ stop (bez průtoku přes VS-TČ). P4: EK okamžitě stop. Soustava: vše stop, alarm. Čerpadla větví jsou stávající, jejich porucha → alarm z T_R/T_S2 | při P2 jen EK (nouzový režim) | FS v řetězci KM-EK0; průtokové ochrany X50 [D]; doporučeno náhradní P2 a P4 na skladě |
| 8 | **Přehřátí akumulace** | T_top > 80 °C nebo T_EK > 82 °C | EK stop, TČ stop, čerpadla soustavy běží (vychlazení), alarm | — | STB-AKU 95 °C v řetězci KM-EK0, pojistné ventily 3 bar, vlastní ochrany X50 (max. 78 °C výstup [D]) |

## 3. Další stavy

| Stav | Reakce |
|---|---|
| Výpadek sítě | X50 a EK stojí. Glykol chrání primár, AKU a soustava jsou uvnitř. PLC na UPS odešle alarm. Po obnovení napětí: X50 podle návodu (předehřev kompresoru) [D], EK se rozjíždějí po stupních od 0 |
| Výpadek PLC | KM-EK0 odpadne → EK vypnuty. X50 běží na vlastní žádanou teplotu 60 °C (nastavit v jednotkách jako nouzovou), P2 přes relé „chod TČ“ |
| Odtávání X50 | krátký pokles T1. AKU pokryje, EK se nepřidávají (06, kap. 4) |
| Mráz v kotelně | T kotelny < 5 °C: alarm, čerpadla soustavy v chodu |
| Ztráta komunikace s X50 | jednotky přejdou na vlastní řízení, PLC je jen povoluje kontakty |

## 4. Nezávislé bezpečnostní prvky (souhrn)

Musí fungovat bez PLC:
- STB 85 °C s ručním resetem na výstupu každého bloku EK,
- STB-AKU 95 °C,
- průtokový spínač FS okruhu EK,
- proudové relé PR 150 A,
- tlačítko TOTAL STOP.

Tyto prvky jsou v sérii v cívce hlavního stykače KM-EK0.

Dále:
- pojistné ventily 3 bar (AKU, každý EK, VS-TČ voda, glykol),
- jištění a RCD každé X50 (40 A [D]),
- vlastní ochrany X50 (presostaty, průtok, protimrazová ochrana) [D].
