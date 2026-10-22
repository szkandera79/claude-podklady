// Hero vizualizace mobilní kotelny ThermaVera přes Gemini (stejný model a klíč jako banner-generator).
// Použití: node gen-hero.mjs H1 [H2 H3]
import fs from 'fs';
import path from 'path';

const BG = '/Users/jindrichszkandera/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projekty/banner-generator';
const REF = '/Users/jindrichszkandera/Library/Mobile Documents/com~apple~CloudDocs/Claude/Projekty/REO/RH X50 komerční/RH X50 - REO HEATING/katalog/obrazky/jednotka-predni.png';
const OUT = process.argv.includes('--out') ? process.argv[process.argv.indexOf('--out') + 1] : process.cwd();

const key = fs.readFileSync(path.join(BG, '.env.local'), 'utf-8').match(/GEMINI_API_KEY\s*=\s*(.+)/)[1].trim().replace(/^["']|["']$/g, '');
const MODEL = 'gemini-3.1-flash-image-preview';
const URL_ = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${key}`;

const UNIT = `Photorealistic architectural photograph, natural light, realistic proportions, shot with a 35 mm lens at eye level, wide 16:9 composition.
The attached image shows the exact outdoor heat pump unit to use: a tall black cabinet (about 1.2 m wide, 1.0 m deep, 1.9 m high) with blue finned heat-exchanger coils on the front and sides and one large round fan on top. Reproduce this unit faithfully (shape, colours, proportions), WITHOUT any logos or text on it.`;

const container = (color) => `one standard 20-foot steel shipping container (about 6 m long, 2.4 m wide, 2.6 m high, clearly about five times longer than one heat pump unit is wide) painted ${color}, clean, with closed steel doors, completely without any text, logos, stickers or signs`;

const GROUND = (color) => `Scene elements: ${container(color)}. Next to the long side of the container stand TWO of the heat pump units side by side on a low steel base, about 1 m apart and at least 1 m away from any wall, with free space above them. Insulated black flexible hoses (about 8 cm diameter) run neatly along the ground from the container to the building's basement wall; one grey electrical cable runs from the container to the building.`;

const ROOF = (color) => `Scene elements: ${container(color)}, standing on the ground. TWO of the heat pump units are mounted ON TOP of the container roof, side by side, on a galvanized steel support frame that rests on the container's corner castings; around them a galvanized grating service walkway with a yellow safety railing, and a fixed galvanized steel ladder with safety cage on the short end of the container. The fans on top of the units face the open sky with nothing above them. Insulated black flexible hoses (about 8 cm diameter) run from the container along the ground to the building's basement wall; one grey electrical cable runs from the container to the building.`;

const RULES = `No people, no vehicles near the container, no chimneys or flue pipes, no smoke, no text anywhere in the image, no watermark.
The image must be ONE continuous photograph from edge to edge: no overlay, no lighter or darker band, no gradient, no frame, no blank or white area anywhere. Compose the shot so the container and heat pumps are in the right half and the left part shows ordinary scenery (sky, yard, lawn, trees or facade).`;

const GREEN = 'dark green (#2E6B33)';
const SCENES = {
  H1: { color: GREEN, set: `Setting: a typical Czech prefabricated concrete panel apartment building (panelák, 8 storeys, renovated with insulated light facade and balconies) on a winter late afternoon, light snow on the grass, overcast sky with soft warm light in some windows. The container and heat pumps stand on a paved area beside the building.` },
  H2: { color: GREEN, set: `Setting: the yard of a medium-sized Central European industrial company: a modern steel-clad production hall with an office wing, asphalt yard, early winter morning, frost on the ground, clear pale sky. The container and heat pumps stand next to the hall wall.` },
  H3: { color: GREEN, set: `Setting: the inner courtyard of an older Czech brick apartment building (činžovní dům, 4–5 storeys, renovated facade in muted colours), late autumn, wet cobblestones, bare trees. The container and heat pumps stand in the courtyard close to the building.` },
  H4: { color: GREEN, set: `Setting: the yard of a Czech food-processing plant or brewery: light rendered production building with stainless steel tanks visible through a large window, concrete yard, winter morning with light frost. The container and heat pumps stand in the yard next to the building.` },
  H5: { color: 'light grey (RAL 7035), slightly weathered', set: `Setting: a large modern logistics warehouse with grey sandwich-panel walls and a row of loading docks with closed roller doors, wide asphalt yard, overcast winter day, wet ground. The container and heat pumps stand at the end of the building, away from the docks.` },
  H6: { color: GREEN, set: `Setting: a Czech woodworking company: timber production hall with dark wooden cladding, stacked sawn timber under a roof in the background, gravel yard, cold winter day with a little snow. The container and heat pumps stand next to the hall.` },
  H7: { color: GREEN, set: `Setting: a renovated historic red-brick factory building (19th-century industrial architecture with tall arched windows) now used as a production plant, cobbled and asphalt yard, clear cold winter afternoon with low sun. The container and heat pumps stand next to the brick building.` },
  H8: { color: 'anthracite grey (RAL 7016)', set: `Setting: a mid-size modern metalworking plant: blue and silver steel-clad hall with a glazed office entrance, a few parked cars far in the background, light snow on the verge, blue hour in winter with interior lights on. The container and heat pumps stand next to the hall.` },
  H9: { color: 'pale cream white (RAL 9001)', set: `Setting: a modern four-star city hotel (6 storeys, light facade, glass entrance canopy) seen from its service side, paved area with low hedges, winter evening with warm light in windows. The container and heat pumps stand on the service area beside the hotel.` },
  R1: { roof: true, color: 'oxide red (RAL 3009)', set: `Setting: the yard of a large modern production hall with light grey cladding and a row of high windows, asphalt yard, crisp sunny winter day with a little snow. The container stands parallel to the hall wall, about 3 m away from it.` },
  R2: { roof: true, color: 'light grey (RAL 7035)', set: `Setting: a renovated Czech panel apartment building (panelák, 8 storeys, light insulated facade with balconies) on an overcast winter day, light snow on the lawn. The container stands on a paved area beside the building, about 4 m from the facade.` },
};

async function gen(id) {
  const parts = [
    { inlineData: { mimeType: 'image/png', data: fs.readFileSync(REF).toString('base64') } },
    { text: [UNIT, (SCENES[id].roof ? ROOF : GROUND)(SCENES[id].color), SCENES[id].set, RULES].join('\n') },
  ];
  const body = { contents: [{ parts }], generationConfig: { responseModalities: ['IMAGE', 'TEXT'], imageConfig: { aspectRatio: '16:9' } } };
  for (let i = 0; i < 3; i++) {
    const res = await fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!res.ok) { console.warn(id, 'HTTP', res.status, (await res.text()).slice(0, 300)); continue; }
    const json = await res.json();
    const img = json?.candidates?.[0]?.content?.parts?.find(p => p.inlineData?.data);
    if (!img) { console.warn(id, 'bez obrázku', json?.candidates?.[0]?.finishReason); continue; }
    const out = path.join(OUT, `hero-${id}.png`);
    fs.writeFileSync(out, Buffer.from(img.inlineData.data, 'base64'));
    console.log('OK', out);
    return;
  }
  console.error('SELHALO', id);
}

for (const id of process.argv.slice(2).filter(a => /^[HR]\d$/.test(a))) await gen(id);
