/**
 * Vyrenderuje HTML šablony bannerů (sablony/<nazev>.html) do PNG.
 *
 * Na rozdíl od generate-banners.ts (AI/Gemini) tu nic negeneruje AI —
 * bannery jsou pixel-přesné HTML/CSS se skutečným logem a fotkami,
 * texty se upravují v poli BANNERS přímo v souboru šablony.
 *
 *   npx tsx render-sablony.ts reo-tc
 *   npx tsx render-sablony.ts thermavera-kotelny
 *   npx tsx render-sablony.ts reo-tc --only=R1,R3
 *
 * Náhled všech bannerů bez renderu: otevři sablony/<nazev>.html v prohlížeči.
 * Výstup: bannery-<nazev>/<ID>_1080x1080.png
 */
import puppeteer from 'puppeteer';
import * as fs from 'fs';
import * as path from 'path';
import { pathToFileURL } from 'url';

const args = process.argv.slice(2);
const name = args.find(a => !a.startsWith('--'));
if (!name) {
  const list = fs.readdirSync('sablony').filter(f => f.endsWith('.html')).map(f => f.replace('.html', ''));
  console.error('Použití: npx tsx render-sablony.ts <šablona> [--only=ID1,ID2]');
  console.error('Dostupné šablony: ' + list.join(', '));
  process.exit(1);
}
const only = args.find(a => a.startsWith('--only='))?.slice(7).split(',');

const file = path.resolve('sablony', `${name}.html`);
if (!fs.existsSync(file)) {
  console.error(`Šablona nenalezena: ${file}`);
  process.exit(1);
}
const outDir = path.resolve(`bannery-${name}`);
fs.mkdirSync(outDir, { recursive: true });

async function waitReady(page: import('puppeteer').Page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(i =>
      i.complete ? null : new Promise(r => { i.onload = i.onerror = r; })));
    // CSS background-image (fotky)
    const urls = [...document.querySelectorAll<HTMLElement>('.bn-photo')]
      .map(el => getComputedStyle(el).backgroundImage.match(/url\("?(.+?)"?\)/)?.[1]).filter(Boolean) as string[];
    await Promise.all(urls.map(u => new Promise(r => { const im = new Image(); im.onload = im.onerror = r; im.src = u; })));
  });
}

async function main() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  const base = pathToFileURL(file).href;

  await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 1 });
  await page.goto(base, { waitUntil: 'networkidle0' });
  const banners: { id: string; h: number }[] = await page.evaluate(
    () => (window as any).BANNERS.map((b: any) => ({ id: b.id, h: b.h || 1080 })));
  const todo = only ? banners.filter(b => only.includes(b.id)) : banners;

  console.log(`🖼  Šablona: ${name} · ${todo.length} bannerů → ${path.relative(process.cwd(), outDir)}/`);
  for (const b of todo) {
    await page.setViewport({ width: 1080, height: b.h, deviceScaleFactor: 1 });
    await page.goto(`${base}?id=${encodeURIComponent(b.id)}`, { waitUntil: 'networkidle0' });
    await waitReady(page);
    const out = path.join(outDir, `${b.id}_1080x${b.h}.png`);
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: b.h } });
    console.log(`   ✅ ${path.basename(out)}`);
  }
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
