# 03 – Přepočet výkonu teplovzdušných jednotek SAHARA a výměníku (rev1)

## 1. Co je a co chybí

| Zařízení | Známo [P] | **[CHYBÍ]** | Jak získat |
|---|---|---|---|
| 5 × SAHARA W3634 (hala 1 182 m²) | typ, připojení DN25, šroubení Hertz Stromax Š25/3,5–5,2, spád 80/60 °C, společné čerpadlo DAB A 50/180 XM 3,8 m³/h (2. stupeň) | výrobce a řada (pravděpodobně starší GEA Sahara [O]), jmenovitý výkon, průtok vzduchu, stupně ventilátoru, výkonová tabulka pro teploty vody | foto štítků všech 5 jednotek, dotaz u GEA / Kampmann CZ, případně měření (teploty vody a průtok) za provozu |
| Radiátory administrativy | Korado Radik VK, typy 10/20/21, výšky 600, délky 600–1 600 mm, spád 75/60 °C, ESBE, DAB VA 35/130 1 m³/h | celkový instalovaný výkon (soupis těles z výkresu jen částečně čitelný), skutečná křivka ESBE | soupis těles na obhlídce |
| Výměník HV VS 200 kW (ESL) | voda–voda, primár 95 °C / 0,5 MPa | typ (deskový / trubkový), plocha, teploty sekundáru, tlaková ztráta | štítek výměníku, dokumentace ESL |

Spád 85/60 °C ze zadání rev1 se v podkladech nevyskytuje. Přepočet proto vychází z projektového 80/60 °C a pro srovnání uvádí i variantu 85/60 °C / 88 kW.

## 2. Metoda [O]

Bez tabulky výrobce se jednotky modelují jako výměník s konstantním součinitelem:

- `P = k × (t_m − t_a)`, kde t_m je střední teplota vody a t_a teplota vzduchu.
- k se určí z návrhového bodu.
- Při zadaném vstupu vody a průtoku se t_m dopočte z bilance vody.

Odhad je platný pro stejný průtok vzduchu (stejný stupeň ventilátoru). U lamelových ohříváků s ventilátorem je skutečná závislost obvykle mírně nadlineární (exponent ≈ 1,0–1,15). Přepočet je proto mírně optimistický pro nižší teploty. **Po získání tabulky výrobce nahradit.**

- Návrh hala: 88,4 kW při 80/60 °C, vzduch 20 °C → **k = 1,77 kW/K** (všech 5 jednotek).
- Provoz: vzduch v hale **17 °C** (požadavek klienta).

## 3. Výkon všech 5 jednotek podle teploty vody (vzduch 17 °C)

| Režim | Průtok pro dodržení spádu | Výkon při dodrženém spádu | Výkon při stávajícím průtoku 3,8 m³/h | Zpátečka při 3,8 m³/h |
|---|---|---|---|---|
| 85/60 °C | 3,4 m³/h | 98,1 kW | 100,2 kW | 62,3 °C |
| 80/60 °C (projekt) | 4,0 m³/h | 93,7 kW | 92,8 kW | 59,0 °C |
| **70/60 °C** | **7,3 m³/h** | 84,9 kW | **78,1 kW** | 52,3 °C |
| **70/55 °C** | 4,6 m³/h | 80,4 kW | 78,1 kW | 52,3 °C |
| 65/55 °C | 6,5 m³/h | 76,0 kW | 70,7 kW | 49,0 °C |

Varianta „zadání 85/60 °C = 88 kW“ (průtok 3,03 m³/h): při 70 °C a stávajícím průtoku 71,8 kW, při 70/55 °C 76,3 kW.

**Důležité:** spád 70/60 °C potřebuje ≈ 2× průtok proti projektu. Stávající čerpadlo haly ho nedá. Při 3,8 m³/h se ustálí ≈ 70/52 °C a výkon ≈ 78 kW. Zvýšení na 5 m³/h dá 81 kW (3. stupeň čerpadla, **ověřit křivku DAB A 50/180 XM**).

## 4. Administrativa (radiátory 75/60 °C, n = 1,3, 1 m³/h)

| Vstup | Výkon | Zpátečka |
|---|---|---|
| 70 °C | 15,5 kW (89 % návrhu) | 56,7 °C |
| 65 °C | 13,6 kW | 53,3 °C |
| 60 °C | 11,7 kW | 49,9 °C |

## 5. Ověření tepelného komfortu při max. 70 °C

**a) Projektová potřeba** (horní mez, neodpovídá měření):
- Hala při −12 °C a 17 °C potřebuje 80,1 kW. Při 70 °C dodá 78,1 kW (3,8 m³/h) nebo 81,3 kW (5 m³/h) → **na hraně, s vyšším průtokem vyhoví.**
- Administrativa: 15,5 z 17,4 kW → ve výpočtovém mrazu ≈ 1–2 K pod 20 °C.

**b) Skutečná potřeba z měření** (02, ×1,10; rozdělení hala / administrativa ve stejném poměru jako v projektu):

| t_e | Potřebná teplota přívodu pro halu (3,8 m³/h) |
|---|---|
| 0 °C | 38 °C |
| −5 °C | 45 °C |
| −10 °C | 52 °C |
| −12 °C | **55 °C** |
| −15 °C | **59 °C** |
| −18 °C | **63 °C** |

**Závěr:**
- **Při max. 70 °C je komfort zajištěn s rezervou ≈ 7–15 K.**
- Teplotu 70 °C bude potřeba jen při náběhu po útlumu, při omezeném průtoku nebo pokud se potvrdí horší parametry sahar.
- Platí za předpokladu, že rozdělení potřeby mezi halu a administrativu odpovídá projektu a jednotky Sahara mají projektový výkon. **Obojí [CHYBÍ], ověřit.**

## 6. Výměník HV VS

**V doporučené variantě rev1 je výměník mimo provoz.** Kotelna se připojuje za něj, na sekundár DN65 před rozdělovačem RS Kombi modul 100. Výměník zůstává osazen a uzavřen, aby šlo kdykoli přejít zpět na teplovod.

**Pro srovnání – připojení přes výměník [O]:**
- Bez znalosti typu a plochy lze uvažovat přiblížení 3–5 K.
- 70 °C na primáru by dalo 65–67 °C na sekundáru.
- Teplota z TČ by musela být o 3–5 K vyšší, a to znamená −2 až −4 kW výkonu X50 na jednotku a nižší COP (mapa W60 → W65).
- Proto zamítnuto.
