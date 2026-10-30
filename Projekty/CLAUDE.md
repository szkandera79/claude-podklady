# CLAUDE.md — Projekty (rozcestník)

Repozitář **Projekty** sdružuje samostatné projekty (ThermaVera, nabídky pro bytové domy,
technické podklady, nástroje). Každý projekt má vlastní složku a vlastní `README.md`
(web navíc vlastní `CLAUDE.md` s pravidly). **Před prací na projektu si přečti jeho README /
CLAUDE.md** a drž se pravidel tam uvedených.

## Kde to leží
- Lokální cesta: `~/Claude/Projekty` (odkaz na iCloud Drive `Claude/Projekty`) — stejná na iMacu i MacBooku.
- Původní cesty `~/Claude/REO`, `~/Claude/banner-generator` atd. jsou odkazy na složky v Projektech (fungují dál).
- GitHub: `szkandera79/Projekty` (soukromý). **Na iMacu se synchronizuje automaticky** po každé práci v Claude Code
  (Stop hook → `~/Developer/ClaudeVoiceCZ/scripts/sync-projekty.sh`, max. 1× za 10 min: kontrola tajných údajů,
  commit, `pull --rebase`, push; log `~/Library/Logs/claude-podklady-sync.log`). Ruční `git commit`/`push` není potřeba.
- Skripty projektů počítají cesty relativně ke svému souboru; příkazy v README se spouštějí
  z kořene repozitáře (např. `python3 bd-jandova/src/gen_schema.py`).
- Náhled v prohlížeči: konfigurace „projekty“ v `.claude/launch.json` (server z kořene na portu 8000)
  → web `http://localhost:8000/thermavera-web/`, projekty `http://localhost:8000/<projekt>/…`;
  samotný web také konfigurace „web“ (port 8001, kořen = `thermavera-web/`).

## Projekty
| Složka | Obsah |
|---|---|
| `thermavera-web/` | web thermavera.cz („zelené kotelny na klíč“) + kalkulačka; vlastní **CLAUDE.md** (i18n, právní mantinely, build `dist/` pro web4u) |
| `vzor-bytove-domy/` | obecná vzorová nabídka zelené kotelny pro SVJ / BD (25–100 kW), jednotky RH X50 |
| `vzor-bytove-domy-rhx30/` | tatáž nabídka ve verzi s jednotkami RHX30 Pro (tišší, vyšší SCOP, FV přímo do TČ) |
| `mala-zelena-kotelna/` | malá zelená kotelna pro menší BD (≈ 12–22 kW): 2 × REO RH060, AKU 1 000 l, TUV 1 000 l; ceny k doplnění |
| `bd-jandova/` | nabídka BD Jandova 7, Ostrava-Zábřeh (17 b.j., náhrada CZT tepelnými čerpadly) |
| `bd-michal/` | BD Michal — koncepční schémata kotelny, PENB, smlouva o dílo |
| `bd-michal-nabidka/` | cenová nabídka BD u Dolu Michal (24 b.j.), varianty A/B, podklady pro společníky |
| `porovnani-x50-2-3/` | porovnání 2× vs. 3× REO X50 (podklad pro výbor SVJ) |
| `konkurence-tc-smart/` | konkurenční srovnání REO R290 Smart / REO R290 vs. 10 značek R290 monobloků (cena, COP/SCOP, hluk, výbava) |
| `plot-fve/` | FV panely na vnější straně stávajícího plotu (40 m, JV, svah) — varianty konstrukce, sklon, předběžná statika, výkresy, rozpočet |
| `audit-akustika-rh030-rh060/` | audit akustické dokumentace RH030–RH060 (LWA/LpA z protokolů TÜV SÜD, chybějící podklady, NV 272/2011) |
| `porovnani-x50-rh060/` | srovnání jednotek pro kaskády BD: RH X50 / X40 / X20 / RH060 |
| `mobilni-kotelna-tc/` | podnikatelský a technický model pronájmu mobilních kotelen s TČ v kontejneru; `univerzalni/` = studie univerzální kotelny (fáze 1 hotová) |
| `mobilni-kotelny-web/` | web služby pronájmu mobilních kotelen s TČ (značka ThermaVera): úvod, kalkulačka celkové ceny tepla (7 zdrojů), článek o ceně tepla; data v `assets/calc-core.js` |
| `nakupni-ceny/` | interní přehled nákupních cen: fakturované ceny PW, ceníky Smart / RHX Pro / Cleanlife / komerční, nádrže, sklad Frankfurt; artefakt |
| `reo-nahradni-dily/` | interní nákupní ceník náhradních dílů RH030–RH060 (USD + Kč), JSON z `REO/PW R290/Spare Part List - revised.pdf`, artefakt |
| `reo-schemata-zapojeni/` | jednoduchá schémata zapojení TČ REO HEATING pro kutily (číslované popisky); varianta 1 = jen topení s AKU + sekundární čerpadlo na bezdrátový termostat |
| `reo-iot-cz/` | rozšíření Chrome nad IOT Power World (CZ překlad, encyklopedie parametrů, chyby, diagnostika); vlastní **CLAUDE.md** (read-only, `podklady/` mimo git) |
| `eko4home-web/` | návrh redesignu eko4home.cz (Riva Trade): design dle klimatizacekasparek.vercel.app, produkty REO RH030–RH060, Smart, RHX Pro, nádrže s cenami |
| `marketing/` | oslovení SVJ (e‑maily, leady CZT, tracker), Google Ads / PPC, grafika |
| `claude-voice-cz/` | **kopie** projektu hlasového asistenta pro iPhone; hlavní verze je v `~/Developer/ClaudeVoiceCZ` |
| `reo-crm/` | vlastní CRM REO HEATING (leady FB/IG z Google Drive, fáze, schůzky, faktury); artefakt LnRFiysRw114a2LJbqid6P; vlastní **CLAUDE.md** (data = osobní údaje, mimo git) |
| `voyah-route-planner/` | osobní plánovač tras a nabíjení pro Voyah Free (PWA + FastAPI); jádro + data (OSM, OCM, ORS/OSRM, Open-Meteo) hotové, plán z CLI funguje; další krok API + PWA |
| `REO/` | značka REO HEATING — návody, datové listy, katalogy, letáky, prezentace, web `reoheating-web/` |
| `banner-generator/` | generátor reklamních bannerů (ThermaVera / REO HEATING / SuperHeating), Gemini API — klíč jen v `.env.local` (není v gitu) |
| `BD Michal Claude/` | podklady k bytovému domu Michal (PDF, smlouvy) |
| `ThermaVera nabídky/` | nabídky ThermaVera (PDF, Word) |
| `Reference zelena kotelna/` | fotky realizací (zdroj pro reference a katalogy) |
| `PW Obchodní/` | obchodní podklady PW |
| `Voyah reklamace/`, `Wok/`, `Bazen chemie/`, `Adria/` | osobní složky |

## Společná pravidla
- Komunikace a texty česky; tón seriózní B2B energetik (viz `thermavera-web/CLAUDE.md`).
- Žádné garance úspor ani návratnosti; u ekonomiky „orientačně“, „u vhodných projektů“.
- Žádné fiktivní reference; nabídky pro konkrétní klienty drž v jejich složce.
- Nový projekt = nová složka v kořeni + `README.md` + řádek do tabulky výše.
