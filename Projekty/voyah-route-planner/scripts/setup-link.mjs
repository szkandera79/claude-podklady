#!/usr/bin/env node
// Vytvoří nastavovací odkaz s klíči (za „#“, tedy se nikdy neposílá na server) a QR kód pro iPhone.
// Klíče čte z ~/.config/voyah-route-planner/.env; nic nevypisuje. Použití:
//   node scripts/setup-link.mjs https://adresa-aplikace/
import { readFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const require = createRequire(join(dirname(fileURLToPath(import.meta.url)), "../frontend/package.json"));
const QRCode = require("qrcode");
const base = process.argv[2];
if (!base) { console.error("Použití: node scripts/setup-link.mjs https://adresa-aplikace/"); process.exit(1); }
const env = Object.fromEntries(readFileSync(join(homedir(), ".config/voyah-route-planner/.env"), "utf8").split("\n")
  .filter((l) => l.includes("=") && !l.trim().startsWith("#")).map((l) => [l.slice(0, l.indexOf("=")).trim(), l.slice(l.indexOf("=") + 1).trim()]));
const keys = {};
if (env.ORS_API_KEY && env.ORS_API_KEY !== "sem-vlozte-klic") keys.ors = env.ORS_API_KEY;
if (env.OCM_API_KEY) keys.ocm = env.OCM_API_KEY;
const payload = Buffer.from(JSON.stringify(keys)).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const url = base.replace(/#.*$/, "") + "#setup=" + payload;
const outDir = join(homedir(), ".local/share/voyah-route-planner");
mkdirSync(outDir, { recursive: true });
const png = join(outDir, "nastaveni-qr.png");
await QRCode.toFile(png, url, { width: 600, margin: 2 });
execFileSync("open", [png]);
console.log(`QR kód otevřen (${Object.keys(keys).join(" + ") || "bez klíčů"}). Naskenujte ho fotoaparátem iPhonu.`);
console.log(`Soubor: ${png} — po použití ho smažte.`);
