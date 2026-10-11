# Bannery — ThermaVera Energy

Sada reklamních bannerů pro Meta Ads (Facebook/Instagram). 6 konceptů × 3 formáty = 18 PNG.
Generováno přes Gemini (`gemini-3.1-flash-image-preview`) z `configs/thermavera.ts`.
Kontext značky a právní mantinely: `PROJECT.md`.

## Formáty

| Formát | Rozměry | Použití |
|---|---|---|
| Feed (1:1) | 1080×1080 | příspěvek FB/IG feed |
| Stories (9:16) | 1080×1920 | IG/FB Stories, Reels |
| Na výšku (4:5) | 1080×1350 | feed (maximální plocha na mobilu) |

## Koncepty

| ID | Soubor (prefix) | Médium | Cílový problém | Headline | CTA |
|---|---|---|---|---|---|
| K1 | `koncept_1_kotelna` | realistická scéna (kotelna + kaskáda TČ) | „Cena tepla roste, rozpočet to neutáhne" | Teplo, které nepřekvapí účtem. | Spočítat návratnost |
| K2 | `koncept_2_bytovy_dum` | realistická scéna (exteriér BD) | „Jsme rukojmí dodavatele tepla" (SVJ) | Konec závislosti na dodavateli tepla. | Nezávazné posouzení |
| K3 | `koncept_3_kombinace` | infografika (diagram zdrojů) | „Nevím, jaký zdroj se vyplatí" | Tepelné čerpadlo, biomasa, nebo obojí? | Zjistit více |
| K4 | `koncept_4_modelovy_scenar` | karta (modelový scénář) | „Vyplatí se to u objektu jako náš?" | Bytový dům: stabilnější náklady na teplo. | Spočítat návratnost |
| K5 | `koncept_5_ets2` | infografika (graf trendu) | „Co s námi udělá ETS2 a růst cen paliv?" | Méně závislí na cenách paliv. | Zjistit více |
| K6 | `koncept_6_typo` | typografie (brand claim) | rozhodné sdělení / always-on | Teplo levněji, čistěji a nezávisleji. | Spočítat návratnost |

## Poznámky k A/B testování (Meta)

- **Začni širokým mixem médií** — Meta (Andromeda) lépe páruje rozmanité kreativy k publikům. Pusť do testu min. 1× realistickou scénu (K1/K2), 1× infografiku (K3/K5) a 1× typografii (K6) zároveň.
- **Doporučené první kolo:**
  - **K2** (nezávislost na CZT) — nejsilnější bolest pro SVJ, největší segment.
  - **K5** (ETS2) — aktuální téma, hraje na obavu z růstu cen; dobře cílí B2B/obce.
  - **K6** (claim) — stabilní „always-on" kreativa, levné CPM, dobrá pro retargeting.
- **K1 vs K4** — A/B na stejný segment (SVJ/obce): scéna kotelny vs. modelový scénář s číslem. Zjistíš, jestli víc táhne „technická realita" nebo „ekonomické číslo".
- **Formáty:** Stories (9:16) a Na výšku (4:5) mají na mobilu nejvyšší zásah — nasaď je primárně; čtverec drž pro feed/desktop.
- **CTA:** „Spočítat návratnost" (K1/K4/K6) míří přímo na kalkulačku, „Nezávazné posouzení" (K2) na poptávkový formulář, „Zjistit více" (K3/K5) na obsahovou sekci. Měř, která akce má nižší cenu za poptávku.

## Mantinely (platí pro všechny bannery)

- Návratnost vždy „u vhodných projektů obvykle do 7 let" — žádná garance.
- ETS2: „může od 2028 zvýšit náklady" — žádné „určitě zdraží".
- Žádné reálné reference/jména obcí; K4 je výslovně „MODELOVÝ SCÉNÁŘ".
- Zařízení na scénách bez vymyšlených log.

## Regenerování

```bash
# celá sada
npx tsx generate-banners.ts thermavera
# jen vybrané koncepty
npx tsx generate-banners.ts thermavera --only=K2,K5
# jen jeden formát
npx tsx generate-banners.ts thermavera --format=1080x1080
```
