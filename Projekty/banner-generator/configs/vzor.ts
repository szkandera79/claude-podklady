/**
 * VZOR konfigurace pro generate-banners.ts.
 *
 * Tento soubor je šablona — zkopíruj ho jako `configs/<mojeznacka>.ts`
 * a uprav podle svého produktu. Pak spusť:
 *
 *   npx tsx generate-banners.ts <mojeznacka>
 *
 * Vygeneruje 6 konceptů × 3 formáty = 18 PNG do `outDir`.
 *
 * Struktura: každý koncept má `id`, `slug`, `buildPrompt(format)` který vrátí
 * textový prompt pro Gemini. Volitelně `getReference` / `getReferences`,
 * pokud chceš jako vstup poslat produktovou fotku nebo víc referencí.
 */

import * as path from 'path';
import type { Config, Concept, Format } from '../generate-banners';

// ---------------------------------------------------------------------
// 1) KAM SE BANNERY ULOŽÍ
// ---------------------------------------------------------------------
const OUT_DIR = 'banners-vzor';

// ---------------------------------------------------------------------
// 2) PRODUKTOVÉ FOTKY (pokud chceš v konceptech použít produkt z fotky)
//    Cesty jsou relativní ke kořeni projektu.
// ---------------------------------------------------------------------
const PRODUKT_PHOTO = path.resolve(OUT_DIR, 'produkt.png');

// ---------------------------------------------------------------------
// 3) BRAND BARVY A TYPOGRAFIE
// ---------------------------------------------------------------------
const ACCENT       = '#a8c5e8'; // hlavní brandová barva
const ACCENT_DEEP  = '#5b8bc4'; // tmavší varianta pro akcenty
const DARK_BG      = '#0a0a0a';
const LIGHT_BG     = '#fafafa';

const BRAND_NOTES = `
BRAND GUIDELINES:
- Primary accent: ${ACCENT}
- Deeper accent: ${ACCENT_DEEP}
- Dark base: ${DARK_BG}; light base: ${LIGHT_BG}
- Typography: modern geometric sans-serif (Inter / Geist / Satoshi feel), ULTRA-BOLD for hero text
- Aesthetic: clean, premium, easy to read on mobile in 2 seconds
- Czech language with pixel-perfect diacritics (á, é, í, ě, š, č, ř, ž, ý, ů)
`;

// ---------------------------------------------------------------------
// 4) UNIVERZÁLNÍ STAVEBNÍ BLOKY — Stories safe zone, layout, technické zákazy
//    Tyto bloky se přidávají ke každému promptu — neopravuj, pokud nemusíš.
// ---------------------------------------------------------------------
const storiesSafeZone = (f: Format) =>
  f.width === 1080 && f.height === 1920
    ? `\nSTORIES SAFE AREA: Place all headline, visuals, numbers and the CTA inside the central area. Leave roughly the top one-sixth and the bottom one-fifth as plain empty background — no text, no icons, no rulers, no pixel labels, no coordinate annotations, no guide lines. CTA button should sit around vertical 60–70%, never glued to the bottom edge.`
    : '';

const layoutHint = (f: Format) => {
  if (f.width === 1080 && f.height === 1920) {
    return 'LAYOUT: vertical centered stack. Headline upper-third, visual middle, CTA at ~60–70% height.';
  }
  if (f.width === 1080 && f.height === 1350) {
    return 'LAYOUT: vertical hierarchy. Headline top, visual middle, CTA bottom.';
  }
  return 'LAYOUT: balanced centered composition. Clear hierarchy: hero element → support → CTA.';
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
- Headline must be LARGE, ultra-bold, instantly readable.
- Maximum 2 lines for the headline.
- CTA button: ${ACCENT} background, ${DARK_BG} text, rounded corners (~12px radius), high contrast.
- NEVER split a number across multiple lines (e.g. "990 Kč" must stay as ONE unbroken unit).
- NEVER render any social-media UI: no Instagram progress bars, no reply bars, no swipe-up hints, no username pills, no app chrome, no phone mockups, no device frames. The banner is a flat creative.
- NEVER write pixel coordinates, margin labels, "320px", "safe zone", or any debug text on the canvas.
- NEVER use stock-photo clichés (handshakes, businessmen with laptops, high-fives).
- NEVER use marketing emoji decoration (rockets, fire, money bags, lightning, target, stars).
- Output EXACTLY the requested pixel dimensions.
`;

// ---------------------------------------------------------------------
// 5) KONCEPTY — 6 různých kreativních směrů na stejný produkt.
//    Mix médií: 2× lifestyle foto + 2× ilustrace + 1× UGC + 1× typografie.
//    (viz pravidlo 4 v CLAUDE.md — vyvážení médií)
// ---------------------------------------------------------------------

// K1 — Lifestyle fotka (problem-first headline)
const K1: Concept = {
  id: 'K1',
  slug: 'koncept_1',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: "[Stručný popis konceptu — např. 'Únavná máma v posteli, kdy nemůže vypnout hlavu']"
STYLE: realistic lifestyle photography, natural light, candid emotion. [Detaily atmosféry, prostředí, osvětlení]

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (small, uppercase, ${ACCENT_DEEP}): "[KRÁTKÝ KONTEXT — např. 'KDYŽ HLAVA NECHCE VYPNOUT']"
- Hero headline (dark ${DARK_BG}, ultra-bold, large, max 2 lines): "[Headline řešící konkrétní bolest cílovky]"
- Sub-line (medium gray): "[Krátké doplnění + téma produktu]"
- CTA button (${ACCENT} bg, dark text, rounded): "[Akce — např. 'Vyzkoušet']"
${commonEnd}`,
};

// K2 — Produktová fotka v lifestylu
const K2: Concept = {
  id: 'K2',
  slug: 'koncept_2',
  getReference: (_f) => PRODUKT_PHOTO,
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: "[Produkt v autentickém kontextu, např. na nočním stolku vedle knihy]"
STYLE: product photography with lifestyle context. Soft natural light. Background neutral with ${ACCENT} accents.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow: "[TÉMA / KATEGORIE]"
- Hero headline: "[Headline]"
- Sub-line: "[Klíčový benefit]"
- CTA: "[Akce]"
${commonEnd}`,
};

// K3 — Ilustrace (problem-first metafora)
const K3: Concept = {
  id: 'K3',
  slug: 'koncept_3',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: "[Metafora problému, např. tělo z nití, které se postupně rozplétá]"
STYLE: minimalist flat illustration, ${ACCENT} + ${ACCENT_DEEP} palette on ${LIGHT_BG} background. No photo, no 3D — clean editorial illustration.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow: "[TÉMA]"
- Hero headline: "[Headline]"
- Sub-line: "[Doplnění]"
- CTA: "[Akce]"
${commonEnd}`,
};

// K4 — UGC / testimonial styl
const K4: Concept = {
  id: 'K4',
  slug: 'koncept_4',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: "[Autentický UGC styl — osoba z cílovky drží produkt, mobilní fotka, ne studiová]"
STYLE: authentic UGC photo, slight imperfection (warm lighting, real bathroom/kitchen background), feels like a friend's recommendation, not a campaign.

TEXT ON BANNER (Czech, exact wording):
- Quote (italic, smaller): "„[Doslovný citát z recenze, max 1 věta]"
- Author label (smaller): "— [Jméno, věk nebo persona]"
- CTA (${ACCENT} bg): "[Akce]"
${commonEnd}`,
};

// K5 — Ilustrace (benefit/data)
const K5: Concept = {
  id: 'K5',
  slug: 'koncept_5',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: "[Vizualizace benefitu — např. infografika rozdílu před/po, klíčové číslo z dat]"
STYLE: editorial infographic illustration. ${DARK_BG} background, ${ACCENT} accents, ultra-bold sans-serif numbers.

TEXT ON BANNER (Czech, exact wording):
- Hero number (huge, ${ACCENT}): "[ČÍSLO — např. '93 %']"
- Label under number (white, smaller): "[Co číslo znamená]"
- Headline (white, bold): "[Co z toho cílovka má]"
- CTA: "[Akce]"
${commonEnd}`,
};

// K6 — Čistá typografie (anti-fluff statement)
const K6: Concept = {
  id: 'K6',
  slug: 'koncept_6',
  buildPrompt: (f) => `${baseHeader(f)}

CONCEPT: "Pure typography statement — provokativní/jasné sdělení v Brand voice"
STYLE: brutally minimal typography. Off-white ${LIGHT_BG} background. Single ${ACCENT} accent (underline last word OR CTA color). No photos, no illustrations.

TEXT ON BANNER (Czech, exact wording):
- Eyebrow (tiny, medium gray, uppercase): "[KATEGORIE / KONTEXT]"
- MASSIVE headline (dark ${DARK_BG}, ultra-bold, multi-line allowed): "[Provokativní/jasné sdělení — max 6–8 slov]"
- Sub-line: "[Krátké doplnění]"
- CTA: "[Akce]"
${commonEnd}`,
};

// ---------------------------------------------------------------------
// 6) FINÁLNÍ EXPORT
// ---------------------------------------------------------------------
const config: Config = {
  outDir: OUT_DIR,
  concepts: [K1, K2, K3, K4, K5, K6],
};

export default config;
