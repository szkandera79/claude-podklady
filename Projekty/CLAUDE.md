# CLAUDE.md — Projekty (rozcestník)

Repozitář **Projekty** sdružuje samostatné projekty (ThermaVera, nabídky pro bytové domy,
technické podklady, nástroje). Každý projekt má vlastní složku a vlastní `README.md`
(web navíc vlastní `CLAUDE.md` s pravidly). **Před prací na projektu si přečti jeho README /
CLAUDE.md** a drž se pravidel tam uvedených.

## Kde to leží
- Lokální cesta: `~/Claude/Projekty` (odkaz na iCloud Drive `Claude/Projekty`) — stejná na iMacu i MacBooku.
- GitHub: `szkandera79/Projekty` (soukromý). Před prací `git pull`, po práci `git commit` + `git push`.
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
| `bd-jandova/` | nabídka BD Jandova 7, Ostrava-Zábřeh (17 b.j., náhrada CZT tepelnými čerpadly) |
| `bd-michal/` | BD Michal — koncepční schémata kotelny, PENB, smlouva o dílo |
| `bd-michal-nabidka/` | cenová nabídka BD u Dolu Michal (24 b.j.), varianty A/B, podklady pro společníky |
| `porovnani-x50-2-3/` | porovnání 2× vs. 3× REO X50 (podklad pro výbor SVJ) |
| `porovnani-x50-rh060/` | srovnání jednotek pro kaskády BD: RH X50 / X40 / X20 / RH060 |
| `mobilni-kotelna-tc/` | podnikatelský a technický model pronájmu mobilních kotelen s TČ v kontejneru |
| `marketing/` | oslovení SVJ (e‑maily, leady CZT, tracker), Google Ads / PPC, grafika |
| `claude-voice-cz/` | **kopie** projektu hlasového asistenta pro iPhone; hlavní verze je v `~/Developer/ClaudeVoiceCZ` |

## Společná pravidla
- Komunikace a texty česky; tón seriózní B2B energetik (viz `thermavera-web/CLAUDE.md`).
- Žádné garance úspor ani návratnosti; u ekonomiky „orientačně“, „u vhodných projektů“.
- Žádné fiktivní reference; nabídky pro konkrétní klienty drž v jejich složce.
- Nový projekt = nová složka v kořeni + `README.md` + řádek do tabulky výše.
