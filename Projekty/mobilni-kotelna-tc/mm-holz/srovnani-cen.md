# MM Holz / Alignum – cenové srovnání s jinými mobilními kotelnami (interní, 19. 10. 2026)

Ceny jsou bez DPH. Období říjen–březen (6 měsíců).

## Výchozí údaje

- **Potřeba tepla objektu** (měření 2021–2025): ≈ 110 MWh (95–119).
- **Naše kotelna:** 2 × RH X50 + EK 72 kW. Elektřina ≈ 47 MWh (41–53, konzervativní SPF ≈ 2,3).
- **Ceny energií:** stejné jako v modelu `src/model.py`.
  - elektřina 4,5 Kč/kWh,
  - nafta 30 Kč/l, LTO 26 Kč/l (10 kWh/l, účinnost 90 %),
  - LPG 16 Kč/l (6,6 kWh/l, účinnost 93 %).
  - Skutečné ceny Alignum **neznáme**.

## Nájem jinde (veřejné ceníky)

| Zdroj | Co | Cena |
|---|---|---|
| [Deutsche-Thermo](https://www.deutsche-thermo.de/mobile-heizzentrale-mieten/) | mobilní kotelna olej/plyn do 110 kW | 2 200–2 700 €/měsíc (≈ 55–68 tis. Kč) |
| [Deutsche-Thermo – přehled cen](https://www.deutsche-thermo.de/heizcontainer-mieten-technik-einsatz-vorteile/) | zařízení od 100 kW | 1 500–3 000 €/měsíc, doprava a spojovací technika v ceně, palivo a připojení zvlášť |
| [mobile-heizung-mieten.de](https://www.mobile-heizung-mieten.de/), [rental-portal.com](https://www.rental-portal.com/mobile-heizzentralen) | olej/plyn do 100 kW | od 80 €/den při měsíčním nájmu (≈ 60 tis. Kč/měsíc) |
| [mobilnikotelna.eu](https://www.mobilnikotelna.eu/mobilni-kotelna/) (CZ) | kotelna 610 kW | 4 000 Kč/den nad 21 dní (≈ 120 tis. Kč/měsíc) + 15 Kč/km + připojení 1 500 Kč/h |
| Hotmobil HOTPUMP MWP 100 (TČ) | mobilní tepelné čerpadlo 100 kW | cena jen na poptávku |

Tuzemští dodavatelé (Free Heating, Seloenergie, České teplo, Mobilenergy) ceny malých jednotek nezveřejňují.

**Převzato pro srovnání:** fosilní mobilní kotelna 100 kW ≈ **55–68 tis. Kč/měsíc** + doprava a připojení ≈ 40 tis. Kč [O].

## Celkové náklady zákazníka za sezónu

| Varianta | Nájem + jednorázové | Energie / palivo | **Celkem 6 měsíců** | Kč/MWh tepla | Za měsíc |
|---|---|---|---|---|---|
| **Naše TČ** (80 000 Kč/měs. + 50 000 + 30 000) | 560 000 | 211 500 (47 MWh el.) | **771 500** | 7 000 | 128 600 |
| Nafta – mobilní kotelna | 370 000–445 000 | 366 700 (12 200 l) | 737 000–812 000 | 6 700–7 400 | 123 000–135 000 |
| LTO | 370 000–445 000 | 317 800 (12 200 l) | 688 000–763 000 | 6 250–6 950 | 115 000–127 000 |
| LPG | 370 000–445 000 | 286 700 (17 900 l) | 657 000–732 000 | 5 950–6 650 | 109 000–122 000 |

Citlivost na cenu elektřiny (naše varianta): 3,5 Kč/kWh → 724 500 Kč, 5,5 Kč/kWh → 818 500 Kč.

## Závěr

- **Nájem samotný je u nás o ≈ 18–45 % dražší** (80 tis. proti 55–68 tis. Kč/měsíc).
- **Energii ale zákazník platí o ≈ 26–42 % méně** (211 tis. proti 287–367 tis. Kč za sezónu).
- **Celkově za 6 měsíců:**
  - proti naftě jsme **na stejné úrovni**,
  - proti LTO o ≈ 1–12 % dražší,
  - proti LPG o ≈ 5–17 % dražší.
- **Výhody, které fosilní pronájem nemá:**
  - žádné dovozy paliva ani nádrž, žádné spaliny,
  - záloha 72 kW v ceně, dálkový dohled,
  - a hlavně **opce odkupu se započtením nájemného**. Při trvalém provozu po odkupu odpadá nájem a zůstává o ≈ 30–40 % nižší náklad na energii.

## Doporučení k ceně

1. **80 000 Kč/měsíc lze obhájit**, pokud nabídku prezentujeme jako „nájem + energie“ a s opcí odkupu. Samotné srovnání nájmu by vyznělo pro nás nepříznivě.
2. **Chceme-li být jednoznačně levnější než LTO i LPG:**
   - nájem **70 000 Kč/měsíc** → celkem ≈ 711 500 Kč,
   - nebo ponechat 80 000 Kč a **dopravu 30 000 Kč nefakturovat** (celkem 741 500 Kč).
   - První varianta je silnější argument, druhá chrání měsíční cenu pro další zákazníky.
3. V nabídce uvádět **tabulku celkových nákladů se skutečnou cenou elektřiny Alignum**. Výsledky jsou orientační, bez garancí.
4. Vyžádat od MM Holz / Alignum dosavadní cenu tepla z teplovodu. Je to přirozený srovnávací bod a zatím ho neznáme.

> Ceny konkurence jsou veřejné ceníkové údaje a orientační rozpětí (převážně Německo, kurz 25 Kč/€). Skutečnou nabídku tuzemského dodavatele pro ≈ 100 kW je vhodné ověřit poptávkou.
