# 04 – Hydraulické řešení (rev1)

Schéma: `04-hydraulicke-schema.svg`. Čísla pocházejí z `src/rev1.py`. Jde o koncept pro rozhodnutí, ne o prováděcí projekt.

## 1. Okruhy a hydraulické oddělení

| Okruh | Médium | Pohon | Průtok | Oddělení |
|---|---|---|---|---|
| **O1 primár TČ** | PG 35 % | P1a, P1b – čerpadlo každé X50, spínané jednotkou [D] | 2 × ≈ 11,4 m³/h (jm. 10,32 [D] + 10 % na glykol) | deskový výměník VS-TČ |
| **O2 nabíjení AKU** | voda | P2 (EC, plynule podle Δt) | do 17,2 m³/h (100 kW, Δt 5 K) | AKU = hydraulický oddělovač |
| **O3 přívod do soustavy** | voda | stávající čerpadla větví na RS Kombi 100 | 6,0 m³/h (105 kW, 70/55) až 9,0 m³/h (70/60) | AKU (strana odběru) |
| **O4 elektrický dohřev** | voda | P4 (≈ 3,6 m³/h) | 3,1–4,1 m³/h (72 kW, Δt 20–15 K) | krátký neutrální úsek A–B na přívodu |

**Princip oddělení:**
- AKU 2 × 1 000 l odděluje okruh TČ (O1/O2) od soustavy (O3). Čerpadla TČ a čerpadla větví se navzájem neovlivňují.
- Elektrický dohřev (O4) je na přívodu zapojen jako vstřikovací okruh: odběr v bodě A, vrácení ohřáté vody v bodě B.
  - Úsek A–B je krátký (≤ 4 × DN) a s malou ztrátou, takže P4 neovlivňuje průtok soustavou.
  - Ohřátá voda se vmíchá do přívodu.
  - Zvýšení teploty přívodu při 72 kW: +10,3 K při 6 m³/h, +6,9 K při 9 m³/h.
- **RS Kombi modul 100**: zda obsahuje hydraulický vyrovnávač, **[CHYBÍ]**.
  - Pokud ne, napojujeme se na sběrnou část rozdělovače a čerpadla větví (DAB A 50/180 XM, VA 35/130, A 50/180 XM pro TUV) odebírají z přívodu kotelny.
  - AKU je za nimi jako beztlaký zdroj.
  - Dodatečná ztráta kotelny v O3 (potrubí 2 × 15 m DN65, filtr, AKU) ≈ 5–12 kPa. Ověřit, že ji čerpadla větví pokryjí ([CHYBÍ] křivky čerpadel a ztráty větví).

## 2. Paralelní vs. sériové zapojení elektrokotlů

| Kritérium | Paralelně do AKU (zadání) | **Sériově za AKU (doporučeno)** |
|---|---|---|
| Teplota vstupu do TČ | EK ohřívá celou AKU → zpátečka do VS-TČ stoupá k 60–70 °C | AKU drží jen teplotu z TČ, spodní část zůstává chladná |
| Riziko pro X50 | vysoký tlak / vypínání, pokles výkonu a COP. **Max. vstupní teplota X50 [CHYBÍ]** | minimální |
| Priorita TČ | EK „předbíhá“ TČ, regulace musí složitě blokovat | přirozená: EK dohřívá jen rozdíl mezi AKU a požadovaným přívodem |
| Teplota přívodu | jen tak vysoká, jak se nabije celá AKU (setrvačnost 2 000 l) | okamžitá reakce, dohřev jen přívodu |
| Využití AKU | směšuje teploty, horší stratifikace | AKU zůstává pro TČ (min. doba běhu, odtávání) |
| Nouzový provoz (TČ mimo) | EK nahřívá AKU, pomalý náběh, ale funguje | EK jsou samostatný zdroj na přívodu. Obtok AKU (V3) urychlí náběh; bez V3 funguje také, jen pomaleji |
| Ztráty | celá AKU na vyšší teplotě | nižší |
| Složitost | jednoduchá hydraulika, složitější regulace | o jedno čerpadlo (P4) a obtok V3 víc |

**Závěr:** sériový dohřev přívodu je technicky správnější a pro prioritu TČ nutný. Paralelní zapojení do AKU by bylo přijatelné jen s elektrickými tělesy v horní zóně AKU a s odběrem pro TČ zcela dole. Ani tak by nebylo zaručeno, že se horní zóna při odběru nepromíchá.

## 3. Elektrokotle a hydraulika

- **Doporučeno:**
  - průmyslový elektrokotel nebo průtokový ohřívač s topnými tělesy v sekcích 6 kW, spínanými stykači z PLC (3 bloky po 4 × 6 kW),
  - vlastní čerpadlo P4, průtokový spínač, STB a pojistný ventil.
  - Konkrétní výrobek **[CHYBÍ]**, viz rozpočet.
- **Protherm RAY 24 KE** (kandidát ze zadání):
  - nástěnný kotel s vlastní elektronikou, modulací a vestavěným čerpadlem,
  - min. jistič 40 A, kaskáda podle prospektu výrobce.
  - Externí řízení po 6 kW z PLC **není doloženo**.
  - Kdyby se použil, zapojí se mezi A a B paralelně (každý kotel s vlastním čerpadlem a zpětnou klapkou, bez P4). PLC by ho jen povolovalo a zadávalo žádanou teplotu přes ON/OFF nebo eBUS.
  - Stupně po 6 kW pak nelze zaručit, jen 3 stupně po 24 kW s interní modulací. Viz `08-rozpocet.md`.
- EK pracují do max. 70 °C na výstupu přívodu (T_S2). STB na výstupu z každého EK nastavit na 85 °C [O]. Max. teplotu a tlak výrobku **[CHYBÍ]**.

## 4. Průtoky a tlakové ztráty [O]

Ocel, ε 0,05 mm, ζ místních odporů podle počtu armatur.

| Úsek | DN | Průtok | Rychlost | Δp úseku |
|---|---|---|---|---|
| Primár glykol, X50 → VS-TČ, 2 × 10 m | DN80 | 22,7 m³/h | 1,25 m/s | 11 kPa + VS-TČ ≈ 30 kPa [O] + X50 ≤ 80 kPa [D] |
| Nabíjení AKU, VS-TČ → AKU, 2 × 5 m | DN65 | 17,2 m³/h | 1,44 m/s | 13 kPa + VS-TČ ≈ 30 kPa |
| Přívod / zpátečka AKU → RS Kombi, 2 × 15 m, 70/55 | DN65 | 6,0 m³/h | 0,50 m/s | 2,7 kPa |
| dtto při 70/60 | DN65 | 9,0 m³/h | 0,75 m/s | 5,9 kPa |
| Okruh EK, 2 × 6 m | DN40 | 3,6 m³/h | 0,80 m/s | 5 kPa + EK [CHYBÍ] |

**Čerpadla [O]:**

| Čerpadlo | Průtok | Dopravní výška | Poznámka |
|---|---|---|---|
| P1a/P1b | 11,4 m³/h | ≈ 12–13 m | ztráta X50 80 kPa + výměník 30 kPa + potrubí, na glykol |
| P2 | 17 m³/h | ≈ 5 m | EC, řízení na Δt 5 K |
| P4 | 3,6 m³/h | ≈ 3 m | + ztráta EK [CHYBÍ] |

**Pozn.:** nabíjecí větev DN65 s 1,44 m/s je na horní hranici. Pokud to dispozice dovolí, provést DN80 (0,95 m/s).

## 5. Armatury, filtrace, expanze, pojištění

- **Každá X50:**
  - uzávěry, filtr ve zpátečce [D], zpětná klapka, vypouštění, odvzdušnění,
  - teploměr a čidlo, flexibilní připojení (antivibrační).
- **Výměník VS-TČ:** uzávěry na obou stranách, manometry, vypouštění (proplach).
- **AKU:**
  - paralelně podle Tichelmanna, uzávěry pro odstavení každé nádrže,
  - čidla T_top / T_mid / T_bot (jímky v obou AKU, PLC bere AKU 1 a kontroluje AKU 2),
  - odvzdušnění a vypouštění.
- **Zpátečka ze soustavy:** filtr + magnetický odkalovač (stará ocelová soustava z roku 2005), kalorimetr MID na přívodu (Q).
- **Okruh EK:** P4, zpětná klapka, průtokový spínač FS (blokuje EK hardwarově), vyvažovací ventil, uzávěry, pojistný ventil 3 bar na každém EK.
- **Expanze:**
  - Glykol: EN-G ≈ 35 l + PV 3 bar [O].
  - Voda: kotelna (AKU 2 000 l + potrubí ≈ 300 l) ΔV ≈ 52 l → **EN ≥ 160 l, navrženo 200 l** [O].
  - Stávající Reflex N 32/3 pokryje jen původní soustavu. Musí se přepočítat na celek, protože objem soustavy, statická výška a nastavení PV jsou **[CHYBÍ]**.
  - PV 3 bar předpoklad: tlak sekundáru HV VS **[CHYBÍ]**.
- **AKU – kandidát Allegro PS-00 1 000 l** (08, B2):
  - skutečný objem jen **843 l** (2 × 843 = 1 686 l). Min. objem pro X50 ≈ 527 l/jednotku je splněn.
  - **Hrdla 6/4″ (≈ DN40):** nabíjení při plném výkonu TČ (65 °C, A7 ≈ 68 kW, Δt 5 K → 11,7 m³/h, tj. 5,85 m³/h na nádrž) dává ve hrdle 1,23 m/s.
  - Pro stratifikaci je to hodně. Připojit každý proud dvěma hrdly, nebo nabíjet s Δt 8 K (P2 na nižší průtok).
  - Expanze s 1 990 l vody: ΔV ≈ 45 l → EN ≥ 140 l (navrženo 200 l zůstává).
  - Klopná výška 2,14 m bez izolace (izolace je odnímatelná). Ø 0,96 m s izolací.
- **Doplňování:** stávající úprava vody DETO KZV 100 zůstává. Plnění AKU upravenou vodou podle VDI 2035 / ČSN 07 7401 [O].

## 6. Glykol – zdůvodnění

- Návod X50 při teplotách pod 0 °C nemrznoucí směs **požaduje** [D]. Venkovní jednotky by bez ní při výpadku proudu zamrzly.
- Cena za glykol: výměník s přiblížením ≈ 3 K, takže TČ musí dát o 3 K víc. Z naměřené potřeby (02) vychází max. požadovaná teplota přívodu 55–63 °C. TČ pracují na W58–W65, to mapa pokrývá do −12 °C, resp. W60 do −25 °C.
- Teplota 70 °C se dosahuje elektrickým dohřevem, nikoli TČ.

## 7. Umístění a odprodej

- **Výchozí varianta A – stávající kotelna:**
  - AKU, výměník, čerpadla a rozvaděč v kotelně, X50 venku na betonových patkách.
  - Při odkupu Alignem zůstává vše na místě.
  - Provést rozebíratelně: příruby a šroubení, rozvaděč kotelny jako samostatná skříň, X50 připojené flexibilně, aby šlo kotelnu při ukončení pronájmu bez odkupu demontovat.
  - **Prostor kotelny [CHYBÍ]:** podle výkresu VS délka ≈ 4,8 m, dnes v ní HV VS, RS Kombi, ACV 320, expanze a úprava vody. 2 × AKU Ø ≈ 1,0 m s izolací, klopná výška ≈ 2,3 m.
- **Varianta B – kontejner 20′** (pokud se do kotelny nevejde nebo pokud se odkup nepotvrdí):
  - technologie podle studie `univerzalni/`, X50 vedle kontejneru,
  - napojení na RS Kombi 2 × DN65 přes stěnu.
  - Ceny jsou v rozpočtu (08).
