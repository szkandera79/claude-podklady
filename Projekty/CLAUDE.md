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
| `vzor-bytove-domy/` | obecná vzorová nabídka zelené kotelny pro SVJ / BD (25–100 kW) |
| `mala-zelena-kotelna/` | malá zelená kotelna pro menší BD (≈ 12–22 kW): 2 × REO RH060, AKU 1 000 l, TUV 1 000 l; ceny k doplnění |
| `bd-jandova/` | nabídka BD Jandova 7, Ostrava-Zábřeh (17 b.j., náhrada CZT tepelnými čerpadly) |
| `bd-michal/` | BD Michal — koncepční schémata kotelny, PENB, smlouva o dílo |
| `bd-michal-nabidka/` | cenová nabídka BD u Dolu Michal (24 b.j.), varianty A/B, podklady pro společníky |
| `porovnani-x50-2-3/` | porovnání 2× vs. 3× REO X50 (podklad pro výbor SVJ) |
| `konkurence-tc-smart/` | konkurenční srovnání REO R290 Smart / REO R290 vs. 10 značek R290 monobloků (cena, COP/SCOP, hluk, výbava) |
| `porovnani-x50-rh060/` | srovnání jednotek pro kaskády BD: RH X50 / X40 / X20 / RH060 |
| `mobilni-kotelna-tc/` | podnikatelský a technický model pronájmu mobilních kotelen s TČ v kontejneru |
| `reo-iot-cz/` | rozšíření Chrome nad IOT Power World (CZ překlad, encyklopedie parametrů, chyby, diagnostika); vlastní **CLAUDE.md** (read-only, `podklady/` mimo git) |
| `marketing/` | oslovení SVJ (e‑maily, leady CZT, tracker), Google Ads / PPC, grafika |
| `claude-voice-cz/` | **kopie** projektu hlasového asistenta pro iPhone; hlavní verze je v `~/Developer/ClaudeVoiceCZ` |
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
