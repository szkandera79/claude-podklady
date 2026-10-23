# Plot FVE — panely na vnější straně stávajícího plotu

Soukromý projekt: konstrukce pro standardní FV moduly podél stávajícího drátěného plotu
(Moravskoslezský kraj, podhůří Beskyd). Cíl: realizovatelný, ekonomicky optimalizovaný návrh
(varianty A/B/C, sklon 90°/75°/60°, předběžná statika EN 1991-1-4/-1-3, výkresy 1–5 + DXF,
rozpočet, montážní postup). **Předběžný návrh — finální dimenze a kotvení ověří autorizovaný statik.**

## Známé údaje
- Délka plotu 40 m, orientace JV, mírný svah, panely na **vnější** straně.
- Pletivo s PVC povrchem, 3 napínací dráty, výška ≈ 1,5 m (odhad z fotek, neověřeno).
- Sloupky: tenké kruhové trubky (odhad Ø 38–48 mm), zelená povrchová úprava, některé zdvojené
  (napínací/vzpěrné). Mezi sloupky pomocné tenké tyče, některé vychýlené.
- Při zemi podhrabové desky / prkna.
- Stínicí tkanina je dočasná a demontovatelná (dřevěné latě na vnější straně).
- Vně plotu louka se vzrostlými ovocnými stromy, zbytky starého drátěného plotu
  (tenké tyče + rezavý drát) cca 0,3–0,5 m od plotu.
- Fotky: `foto/IMG_6711–6714` vnitřní strana, `foto/IMG_6715–6717` vnější strana.

- Připojení: samostatný string na střídač **SolaX X3-Ultra 25K** (parametry MPPT ověřit
  z datového listu: max. DC napětí 1 000 V, počet MPPT a vstupů, max. proud na MPPT).

## Předběžné závěry z fotek
- Stávající sloupky jsou dimenzované na pletivo, ne na plnou plochu panelů ve větru → varianta A
  (panely jen na stávajících sloupcích) prakticky nepřichází v úvahu; reálně B (samostatná
  konstrukce na zemních vrutech) nebo C.
- Modul 1 pole ≈ 2 panely na výšku (2 × ~1 134 mm + mezery ≈ 2,30 m) odpovídá rozteči sloupků.
  40 m ≈ 17 polí ≈ 34 panelů ≈ 15 kWp (orientačně, podle zvoleného panelu).
- Jeden string je omezen napětím: při Voc ≈ 49–50 V/panel a mrazu (−20 °C, +7–8 %) vychází
  max. ≈ 18 panelů na string (1 000 V). 34 panelů = 2 stringy (2 vstupy jednoho MPPT paralelně,
  pokud je volný), nebo jen ~18 panelů (≈ 8 kWp). Rozhodnout s uživatelem.
- Svislé JV panely mají jiný denní profil než střecha → vlastní MPPT je správně, nespojovat
  do série se střešními panely.
- Riziko zastínění od ovocných stromů na vnější straně — nutno ověřit vzdálenosti a výšky.

## Otevřené body (čeká se na uživatele)
- Komu patří pozemek za plotem? Stojí plot na hranici? (panely vně = zábor cizího pozemku?)
- Obec / nadmořská výška, přesný azimut plotu (kompas).
- Rozteč sloupků (změřit 2–3 pole), obvod sloupku, výška plotu, založení sloupků.
- Převýšení terénu po délce 40 m; vzdálenost a výška stromů vně plotu.
- Typ panelu, cílový výkon, střídač / stávající FVE, vzdálenost k rozvaděči, priorita zima/rok.
