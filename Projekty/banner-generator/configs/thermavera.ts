/**
 * Konfigurace pro generate-banners.ts — značka THERMAVERA ENERGY.
 *
 * Spuštění:
 *   npx tsx generate-banners.ts thermavera
 *   npx tsx generate-banners.ts thermavera --only=K1,K6
 *   npx tsx generate-banners.ts thermavera --format=1080x1080
 *
 * 6 konceptů × 3 formáty = 18 PNG do `banners-thermavera/`.
 * Kontext značky a právní mantinely: viz banners-thermavera/PROJECT.md.
 *
 * Pozn.: žádný koncept zatím nepoužívá reálnou produktovou fotku
 * (realizační fotky partnera nejsou schválené) — vše je AI render /
 * ilustrace / typografie.
 */

import type { Config, Concept, Format } from '../generate-banners';

// ---------------------------------------------------------------------
// 1) KAM SE BANNERY ULOŽÍ
// ---------------------------------------------------------------------
const OUT_DIR = 'banners-thermavera';

// ---------------------------------------------------------------------
// 2) BRAND BARVY (paleta ThermaVera — viz web :root)
// ---------------------------------------------------------------------
const GREEN        = '#2E6B33'; // zelená — tmavé prvky (přesně dle webu thermavera.cz)
const GREEN_BRIGHT = '#5BA32E'; // akcent (eyebrow, ikony) — dle webu
const GREEN_TINT   = '#EAF4DE'; // světlé pozadí odznaků — dle webu
const AMBER        = '#FCC83C'; // CTA pozadí — dle webu
const AMBER_DEEP   = '#EAAE1C'; // CTA hover — dle webu
const CTA_TEXT     = '#241603'; // tmavě hnědý text na amber CTA — dle webu (.btn-amber)
const INK          = '#16201C'; // hlavní text
const MUTED        = '#5F6B64'; // tlumený text
const BG           = '#FFFFFF';
const BG_ALT       = '#F5F9F1'; // dle webu

const BRAND_NOTES = `
BRAND GUIDELINES (ThermaVera Energy — B2B green-energy / heating):
- Use these EXACT brand hex colors, do not drift to other greens/yellows:
- Green (dark elements, deep-green panels): ${GREEN}
- Bright green accent (eyebrow, icons, lines): ${GREEN_BRIGHT}
- Light green tint (badge / panel backgrounds): ${GREEN_TINT}
- Amber CTA background: ${AMBER} (button hover ${AMBER_DEEP}), CTA label text ${CTA_TEXT}
- Ink text: ${INK}; muted text: ${MUTED}; base white: ${BG}; alt light: ${BG_ALT}
- Typography: modern geometric sans-serif (Poppins / Inter feel), ULTRA-BOLD headlines.
- Aesthetic: light, airy, clean and technical — serious B2B energy, NOT eco-activism, NOT kitsch.
- NO leaf motifs as the main visual, NO stock-photo clichés, NO marketing emoji.
- Czech language with pixel-perfect diacritics (á, é, í, ě, š, č, ř, ž, ý, ů, ú).
`;

// ---------------------------------------------------------------------
// 3) UNIVERZÁLNÍ BLOKY (safe zone, layout, technické zákazy)
// ---------------------------------------------------------------------
const storiesSafeZone = (f: Format) =>
  f.width === 1080 && f.height === 1920
    ? `\nSTORIES SAFE AREA: Place all headline, visuals and the CTA inside the central area. Leave roughly the top one-sixth and bottom one-fifth as plain empty background — no text, no icons, no rulers, no pixel labels. CTA button sits around vertical 55–68%, never glued to the bottom edge.`
    : '';

const layoutHint = (f: Format) => {
  if (f.width === 1080 && f.height === 1920)
    return 'LAYOUT: vertical centered stack. Eyebrow + headline upper-third, visual middle, CTA at ~58–68% height.';
  if (f.width === 1080 && f.height === 1350)
    return 'LAYOUT: vertical hierarchy. Eyebrow + headline top, visual middle, CTA bottom.';
  return 'LAYOUT: balanced centered composition. Eyebrow + headline → visual → CTA.';
};

const baseHeader = (f: Format) => `
Create a premium advertising banner for Meta Ads (Facebook/Instagram).
EXACT OUTPUT DIMENSIONS: ${f.width} x ${f.height} pixels.
${layoutHint(f)}
${storiesSafeZone(f)}
${BRAND_NOTES}
`;

const commonEnd = `
TECHNICAL RULES:
- Headline must be LARGE, ultra-bold, instantly readable on mobile.
- Maximum 2 lines for the headline.
- CTA button: ${AMBER} background, ${CTA_TEXT} (dark) text, rounded corners (~12px radius), high contrast.
- ALL VISIBLE TEXT must be Czech only, with correct diacritics. Render ONLY the words specified in the TEXT ON BANNER section — no extra English words, no placeholder/pseudo words, no Lorem Ipsum, no labels I did not ask for.
- Any physical equipment in the scene (heat-pump units, accumulation tanks, boilers, pipes) must be UNBRANDED: no invented logos, no brand names, no model labels, no text printed on the devices. Keep product surfaces clean and plain.
- NEVER split a number or unit across lines (e.g. "7 let" stays as ONE unbroken unit).
- NEVER render social-media UI: no Instagram progress bars, no reply bars, no username pills, no app chrome, no phone mockups, no device frames. The banner is a flat creative.
- NEVER draw safe-zone indicators, layout guides, measurement labels, pixel values, dimension numbers, rulers, brackets, arrows or dashed bounding boxes. Those exist only as instructions to you — they MUST NOT appear as pixels.
- NEVER use stock-photo clichés (handshakes, businesspeople with laptops), leaf/eco clichés, or marketing emoji (fire, rocket, money bag, lightning).
- Output EXACTLY the requested pixel dimensions.
`;

// ---------------------------------------------------------------------
// 4) KONCEPTY (6 různých problémů × 6 různých médií/palet)
//    Mix: 2× realistická scéna + 2× infografika + 1× modelový scénář + 1× typografie
// ---------------------------------------------------------------------

// K1 — Realistická scéna: kotelna / kaskáda TČ — předvídatelnost nákladů
const K1: Concept = {
  id: 'K1',
  slug: 'koncept_1_kotelna',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: A modern, clean INDOOR boiler room (technical "kotelna") seen from inside the building. It contains only INDOOR equipment: white accumulation / buffer tanks, a distribution manifold, circulation pumps, insulated piping, a wall-mounted control unit. Bright professional technical lighting, light walls, polished concrete floor. Conveys reliability and competence (NOT industrial grime).
IMPORTANT REALISM RULE: Do NOT place outdoor air-source heat-pump fan units inside this room — those large external fan units are always installed OUTSIDE the building and must NOT appear in an indoor boiler room. Indoor scene = tanks, manifolds, pumps and pipes only.
STYLE: realistic architectural/technical photography, soft daylight, shallow depth of field. Green ${GREEN} and bright green ${GREEN_BRIGHT} accents subtly present (insulated piping, signage). Overall light and premium.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (small, uppercase, ${GREEN_BRIGHT}): "ŘEŠENÍ PRO OBCE, SVJ I PRŮMYSL"
- Hero headline (dark ${INK}, ultra-bold, may use up to 3 lines): "Zelené kotelny na klíč, které dávají ekonomický smysl."
- Sub-line (medium, ${MUTED}, the word "7 let" bold in ${GREEN}): "Návratnost obvykle do 7 let."
- CTA button (${AMBER} bg, dark text, rounded): "Spočítat návratnost"
${commonEnd}`,
};

// K2 — Realistická scéna: exteriér bytového domu — nezávislost na CZT
const K2: Concept = {
  id: 'K2',
  slug: 'koncept_2_bytovy_dum',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: Exterior of a tidy residential apartment building (Czech/Central-European style) in soft morning light, with a discreet row of outdoor heat-pump units beside it. Calm, optimistic, real-estate quality. No people.
STYLE: realistic exterior architectural photography, warm morning light, clean sky. Light base ${BG_ALT} feeling, green ${GREEN_BRIGHT} accent, amber ${AMBER} only on the CTA.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (small, uppercase, ${GREEN_BRIGHT}): "VYTÁPĚNÍ PRO BYTOVÉ DOMY A SVJ"
- Hero headline (dark ${INK}, ultra-bold, max 2 lines): "Konec závislosti na dodavateli tepla."
- Sub-line (medium, ${MUTED}): "Vlastní zelená kotelna pro bytový dům — levněji, čistěji a nezávisleji."
- CTA button (${AMBER} bg, dark text, rounded): "Nezávazné posouzení"
${commonEnd}`,
};

// K3 — Infografika: kombinace zdrojů — nejistota výběru
const K3: Concept = {
  id: 'K3',
  slug: 'koncept_3_kombinace',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: A clean editorial infographic / diagram of an energy-source combination: simple icons for a heat pump and a biomass boiler and an accumulation tank, connected by clean flow arrows to a single building icon. Schematic, confident, easy to read in 2 seconds.
STYLE: flat editorial infographic on deep green ${GREEN} background, accents in bright green ${GREEN_BRIGHT} and amber ${AMBER}, white/light text. Geometric, minimal, NOT cluttered, NO photos, NO 3D.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (small, uppercase, ${GREEN_BRIGHT}): "KOMBINACE ZDROJŮ NA MÍRU"
- Hero headline (white, ultra-bold, max 2 lines): "Tepelné čerpadlo, biomasa, nebo obojí?"
- Sub-line (light ${GREEN_TINT}): "Navrhneme mix zdrojů podle vašeho objektu a spotřeby. Posouzení, projekt i dotace."
- Diagram labels (white, small) — render ONLY these Czech words on the icons: "Tepelné čerpadlo", "Biomasa", "Akumulace", "Objekt"
- CTA button (${AMBER} bg, dark text, rounded): "Zjistit více"
${commonEnd}`,
};

// K4 — Modelový scénář (náhrada UGC) — "vyplatí se to nám?"
const K4: Concept = {
  id: 'K4',
  slug: 'koncept_4_modelovy_scenar',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: A clean "model scenario" card on a light background — clearly labelled as an illustrative example (NOT a real reference). A simple apartment-building icon, and one slim horizontal indicator bar suggesting a payback range, plus the figure "do 7 let". Editorial, trustworthy, restrained.
STYLE: light card design, base white ${BG} with mint tint ${GREEN_TINT} panel, bright green ${GREEN_BRIGHT} accents, dark ${INK} text. Flat, minimal, NO photos, NO fake testimonials, NO quotation marks with a person's name.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (small, uppercase, ${GREEN_BRIGHT}): "MODELOVÝ SCÉNÁŘ"
- Hero headline (dark ${INK}, ultra-bold, max 2 lines): "Bytový dům: stabilnější náklady na teplo."
- Sub-line (medium, ${MUTED}): "Orientační příklad přechodu na tepelná čerpadla. Návratnost u vhodných projektů obvykle do 7 let."
- Indicator label (small, ${GREEN_BRIGHT}): "Orientační návratnost"
- CTA button (${AMBER} bg, dark text, rounded): "Spočítat návratnost"
${commonEnd}`,
};

// K5 — Infografika: ochrana před růstem cen / ETS2
const K5: Concept = {
  id: 'K5',
  slug: 'koncept_5_ets2',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: An editorial infographic contrasting two simple cost trend lines: one rising line (fossil fuels) in amber ${AMBER}, one stable/flat line (green energy source) in bright green ${GREEN_BRIGHT}. Abstract chart — NO specific numbers on the axes, illustrative only. Conveys "less exposure to fuel-price swings".
STYLE: editorial data illustration on dark ink ${INK} background, ultra-bold sans-serif. Two clean trend lines, minimal grid, lots of negative space.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (small, uppercase, ${AMBER}): "PŘIPRAVTE SE NA ETS2"
- Hero headline (white, ultra-bold, max 2 lines): "Méně závislí na cenách paliv."
- Sub-line (light gray): "ETS2 může od roku 2028 zvýšit náklady na fosilní paliva. Zelená kotelna tu závislost snižuje."
- Line labels (small) — render ONLY: "Fosilní paliva" (near amber line), "Zelená kotelna" (near green line)
- CTA button (${AMBER} bg, dark text, rounded): "Zjistit více"
${commonEnd}`,
};

// K6 — Čistá typografie: brand claim
const K6: Concept = {
  id: 'K6',
  slug: 'koncept_6_typo',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: Pure typography statement, brutally minimal. The brand claim is the hero. One bright-green accent (underline of the last word) and the amber CTA. No photos, no illustrations, no diagrams.
STYLE: off-white ${BG_ALT} background, dark ${INK} ultra-bold type, single ${GREEN_BRIGHT} accent. Editorial, premium, lots of whitespace.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (tiny, uppercase, ${MUTED}): "ZELENÉ KOTELNY NA KLÍČ"
- MASSIVE headline (dark ${INK}, ultra-bold, may use 3 lines), underline the last word in ${GREEN_BRIGHT}: "Teplo levněji, čistěji a nezávisleji."
- Sub-line (medium, ${MUTED}): "Spočítáme návratnost pro váš objekt. Posouzení, projekt, dotace i realizace."
- CTA button (${AMBER} bg, dark text, rounded): "Spočítat návratnost"
${commonEnd}`,
};

// ---------------------------------------------------------------------
// 5) FINÁLNÍ EXPORT
// ---------------------------------------------------------------------
const config: Config = {
  outDir: OUT_DIR,
  concepts: [K1, K2, K3, K4, K5, K6],
};

export default config;
