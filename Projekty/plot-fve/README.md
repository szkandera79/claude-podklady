# Plot FVE — panely na vnější straně stávajícího plotu

Soukromý projekt: konstrukce pro standardní FV moduly podél stávajícího drátěného plotu
(Moravskoslezský kraj, podhůří Beskyd). Cíl: realizovatelný, ekonomicky optimalizovaný návrh
(varianty A/B/C, sklon 90°/75°/60°, předběžná statika EN 1991-1-4/-1-3, výkresy 1–5 + DXF,
rozpočet, montážní postup). **Předběžný návrh — finální dimenze a kotvení ověří autorizovaný statik.**

## Stav (23. 10. 2026)
Varianta **B: samostatná svislá konstrukce na zemních vrutech v pásu 30 cm**, 1 řada panelů **naležato**
(náhrada stínicí tkaniny, horní hrana 1 500 = výška plotu).
- Panel: **JA Solar JAM54D40-450/LB** (bifaciální sklo-sklo), alternativa AIKO Neostar 2P A465, Trina NEG9RC.27
  (Voc 52 V → max. 18 ks/string). Žádný výrobce nepovoluje upnutí s profily rovnoběžně s dlouhou hranou
  → **dvouvrstvý systém**: vodorovné nosníky 40×40 na sloupcích + svislé profily 40×40 (2/panel, A ≈ 440 mm).
- 19 panelů = 8,55 kWp, **1 string** na volný MPPT SolaX X3-Ultra 25K (Voc −25 °C ≈ 840 V);
  PVGIS 90°/150° ≈ 710 kWh/kWp → ≈ 6 070 kWh/rok.
- 17 sloupků jekl 60×60×4 (využití ≤ 66 %) na vrutech Ø76×1600, hloubka konstrukce 250 mm od osy plotu.
- Vítr: qp = 556 Pa (oblast II, terén II), volně stojící stěna tab. 7.9; var. A (stávající sloupky) využití 315 % → zamítnuto.
- Konstrukce vč. montáže ≈ 98 tis. Kč s DPH (odhad).
- Hotové systémy (rešerše 23. 10.): nejvhodnější Kirchberger SUNLINE horizontal a Profiness Basic quer
  (drážkové Al sloupky, hloubka ≈ 7–8 cm, výška 1,25–1,27 m, ≈ 140–180 tis. Kč za 19 panelů) → poptat
  zvýšené sloupky, kotvení na vruty, statiku, dodání do ČR. CZ firmy (Plotík, ALUX, Svaroq) = náhrada plotu v linii.
- Podklad: `navrh.html` (artefakt CvKMLkVx9LvPeLw9rx7acp), výkresy `dxf/plot-fve.dxf`, souhrn `vystup/statika.json`;
  generuje `python3 plot-fve/src/navrh.py` (volba panelu = `VYBER`).

## Známé údaje
- Délka plotu 40 m, orientace JV, panely na **vnější** straně. Pozemek je v mírném svahu,
  ale **linie plotu je v rovině** → bez výškového odstupňování modulů.
- Pletivo s PVC povrchem, 3 napínací dráty, výška ≈ 1,5 m (odhad z fotek, neověřeno).
- Sloupky: tenké kruhové trubky (odhad Ø 38–48 mm), zelená povrchová úprava, některé zdvojené
  (napínací/vzpěrné). Mezi sloupky pomocné tenké tyče, některé vychýlené.
- Při zemi podhrabové desky / prkna.
- Stínicí tkanina je dočasná a demontovatelná (dřevěné latě na vnější straně).
- Vně plotu louka se vzrostlými ovocnými stromy, zbytky starého drátěného plotu
  (tenké tyče + rezavý drát) cca 0,3–0,5 m od plotu.
- Fotky: `foto/IMG_6711–6714` vnitřní strana, `foto/IMG_6715–6717` vnější strana.

- **Hranice:** plot sousedí se sousedem; za plotem patří uživateli pás jen **30 cm**
  (ověřit vytyčením hranice geodetem). Celá konstrukce vč. vrutů, profilů a panelů se musí
  vejít do tohoto pásu → prakticky jen **svislé panely (90°)**; 75° (průmět ≈ 0,46 m) a 60°
  (≈ 0,88 m) se nevejdou. Montáž a údržba jen ze sousedního pozemku → souhlas souseda.
- Připojení: samostatný string na střídač **SolaX X3-Ultra 25K** (parametry MPPT ověřit
  z datového listu: max. DC napětí 1 000 V, počet MPPT a vstupů, max. proud na MPPT).

- Plot (sloupky, pletivo) patří uživateli.
- Rozteč sloupků **220–238 cm, každé pole jinak** → modul „1 pole = 2 panely“ nefunguje
  (2 panely na výšku potřebují ≈ 2,29 m). Nosná konstrukce bude mít **vlastní pravidelný rastr
  nezávislý na sloupcích plotu** (průběžné vodorovné profily, podpěry mimo patky sloupků).

## Předběžné závěry z fotek
- Stávající sloupky jsou dimenzované na pletivo, ne na plnou plochu panelů ve větru → varianta A
  (panely jen na stávajících sloupcích) prakticky nepřichází v úvahu; reálně B (samostatná
  konstrukce na zemních vrutech) nebo C.
- Modul 1 pole ≈ 2 panely na výšku (2 × ~1 134 mm + mezery ≈ 2,30 m) odpovídá rozteči sloupků.
  40 m ≈ 17 polí ≈ 34 panelů ≈ 15 kWp (orientačně, podle zvoleného panelu).
- Svislé JV panely mají jiný denní profil než střecha → vlastní MPPT je správně, nespojovat
  do série se střešními panely.
- Plot je **jediné volné místo** pro FV → maximalizovat výkon na plotě. Prověřit
  (a) **bifaciální sklo-sklo panely** (zadní strana k SZ; tkanina se sundá, pletivo stíní málo),
  (b) **2 řady na šířku nad sebou** (≈ 36 panelů / 16 kWp, horní hrana ≈ 2,8 m — vyšší vítr,
  výšková omezení, výhled souseda, stringy 2 × 18 na hraně 1 000 V).
- Riziko zastínění od ovocných stromů na vnější straně — nutno ověřit vzdálenosti a výšky.
- **Rozhodnuto:** osadit téměř celou délku, poslední 2–3 pole u stínícího stromu vynechat.
  Pracovní předpoklad ≈ 14 polí = 28 panelů ≈ 12–12,6 kWp → **2 stringy po 14 panelech**
  (Voc v mrazu ≈ 750 V < 1 000 V), stejná délka i orientace → paralelně na 1 MPPT
  (ověřit max. proud MPPT ≥ ~28 A). Přesný počet polí po změření rozteče.

## Otevřené body (čeká se na uživatele)
- Je hranice vytyčená / vyznačená? (plot je uživatele — dodáno)
- Vztah se sousedem: souhlas s montáží z jeho pozemku a se stavbou na hranici.
- Lokalita **Vendryně (okres Frýdek-Místek), ≈ 400 m n. m.** Větrnou a sněhovou oblast ověřit
  v mapách NA k ČSN EN 1991-1-4 / 1-3. Chybí přesný azimut plotu (kompas). Pracovně: větrná oblast II (vb,0 = 25 m/s), kategorie terénu III
  (zahrady, sad, zástavba); sníh u svislých panelů rozhoduje jen u paty (navátý sníh, odhrnování).
- Obvod sloupku, výška plotu, založení sloupků (rozteč dodána: 220–238 cm, každé pole jiné).
- Vzdálenost a výška stromů vně plotu.
- Typ panelu, cílový výkon, střídač / stávající FVE, vzdálenost k rozvaděči, priorita zima/rok.
