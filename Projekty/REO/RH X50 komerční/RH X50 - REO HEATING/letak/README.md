# RH X50 / RH X100 — produktový leták (rebrand)

Věrný rebrand letáku výrobce „R290 Commercial Heat Pump Series“ (`../../R290-Commercial-Heat-Pump-Series.pdf`,
2 strany na šířku 1207×825 pt) na **REO HEATING RH X50 / RH X100**. Sazba, texty a fotky zůstávají, mění se značka.

- `rebrand.py` → `REO-RH-X50-X100_letak-EN.pdf`
  - úvodní obrázek: `assets/hero-podnik-na-vysku.png` = AI vizualizace `hero-podnik.jpg` z webu mobilních kotelen
    (Projekty/mobilni-kotelny-web), rozšířená přes Gemini na výšku (3:4) — původní obrázek výrobce by šel dohledat;
    rendery jednotek, stíny a „teplo“ nad ventilátory z originálu odstraněny
  - energetický štítek výrobce → `../RH-X50-energeticky-stitek.pdf` (vlevo dole, vpravo by zakryl jednotky)
  - logo výrobce v záhlaví a na jednotkách ve fotkách (vektor) → logo REO HEATING (na jednotkách jednobarevně šedé)
  - nadpis „RH X50 · RH X100 / R290 Commercial Series“; tabulka: nový sloupec RH X100 (návod tab. 2.2 + list
    parametrů komerčních jednotek výrobce)
- `translate.py extract|build` → `REO-RH-X50-X100_letak-CZ.pdf` (postup z katalogu REO R290 Smart; překlad
  `cz/cs.json`, sazba `cz/override.json`: odrážky a hodnoty tabulky po řádcích, vektorové nápisy v `vector_words`)
- Artefakt: Marketing REO HEATING https://claude.ai/artifact/8zGFmzL6gnPFsy8zTqRjGz (sekce RH X50 · RH X100)

Otevřené: velký nápis „R290 SERIES COMMERCIAL“ na úvodní fotce je vektorová grafika — v CZ zůstává anglicky;
štítek RH X50 uvádí vnitřní hlučnost „00 dB“ (viz ../README.md); RH X100 nemá vlastní štítek;
chlazení 7~35 °C podle letáku (návod uvádí 7~30 °C).
