"""Rozcestník „Voyah trasy“ pro artefakt na claude.ai: odkaz na aplikaci + Ceník nabíjení (data z ceniky.json vložená do stránky).
Artefakt nesmí volat vnější služby (CSP) ani GPS → plánovač běží na Netlify, tady je jen spouštění a ceník.
Spuštění: python3 scripts/build-artifact.py  → artefakt/voyah-trasy.html
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "frontend/public/data/ceniky.json").read_text())
APP = "https://voyah-trasy-jindrich.netlify.app/"
for s in DATA["sources"].values():
    s.pop("fingerprint", None); s.pop("new_fingerprint", None)

HTML = """<title>Voyah trasy</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
/* Layout: jeden sloupec do 760 px — nahoře spuštění aplikace, pod tím filtrovatelný ceník. Barvy = aplikace Voyah trasy. */
:root {
  --bg: #f1f5f4; --card: #ffffff; --text: #0f1f1d; --muted: #5b6b68; --line: #dde5e3;
  --accent: #0f766e; --accent-soft: #ccfbf1; --warn: #b45309; --warn-soft: #fef3c7;
  --sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0b1416; --card: #132124; --text: #e6f0ee; --muted: #93a5a1; --line: #22363a;
  --accent: #2dd4bf; --accent-soft: #123a37; --warn: #fbbf24; --warn-soft: #3a2f12; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #0b1416; --card: #132124; --text: #e6f0ee; --muted: #93a5a1; --line: #22363a;
  --accent: #2dd4bf; --accent-soft: #123a37; --warn: #fbbf24; --warn-soft: #3a2f12; color-scheme: dark }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font: 15px/1.5 var(--sans);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 20px 40px; }
main { max-width: 760px; margin: 0 auto; display: grid; gap: 16px; }
h1 { font-size: 26px; margin: 0; letter-spacing: -0.02em; text-wrap: balance; }
h2 { font-size: 18px; margin: 0; text-wrap: balance; }
.muted { color: var(--muted); }
.small { font-size: 13px; }
.hero { background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 20px; display: grid; gap: 12px; }
.open { display: inline-flex; align-items: center; justify-content: center; min-height: 54px; padding: 0 22px; border-radius: 14px;
  background: var(--accent); color: #fff; font-weight: 600; font-size: 17px; text-decoration: none; }
:root[data-theme="dark"] .open { color: #04221f; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .open { color: #04221f; } }
.open:focus-visible, select:focus-visible, button:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.copy { min-height: 44px; padding: 0 14px; border-radius: 12px; border: 1px solid var(--line); background: var(--bg); color: var(--text); font: inherit; cursor: pointer; }
.url { font-family: var(--mono); font-size: 13px; user-select: all; word-break: break-all; }
ol.steps { margin: 0; padding-left: 20px; display: grid; gap: 4px; }
.filters { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; }
label { display: grid; gap: 4px; font-size: 13px; color: var(--muted); }
select { min-height: 42px; border-radius: 10px; border: 1px solid var(--line); background: var(--card); color: var(--text); font: inherit; padding: 0 8px; }
.list { display: grid; gap: 10px; }
.entry { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 14px; display: grid; gap: 8px; min-width: 0; }
.head { display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }
.pill { font-size: 12px; padding: 2px 9px; border-radius: 99px; white-space: nowrap; background: var(--warn-soft); color: var(--warn); }
.pill.ok { background: var(--accent-soft); color: var(--accent); }
.tw { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th { text-align: left; font-weight: 500; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; padding: 4px 6px; }
td { padding: 5px 6px; border-top: 1px solid var(--line); }
td.n { text-align: right; font-family: var(--mono); font-variant-numeric: tabular-nums; }
a { color: var(--accent); }
.foot { font-size: 12px; color: var(--muted); }
</style>
<main>
  <section class="hero">
    <h1>Voyah trasy</h1>
    <p class="muted">Plánovač tras a nabíjení pro Voyah Free 2023. Počítá přímo v zařízení; data a klíče zůstávají v telefonu či počítači.</p>
    <div class="row">
      <a class="open" href="__APP__" target="_blank" rel="noopener">Otevřít plánovač</a>
      <button class="copy" id="copy" type="button">Kopírovat adresu</button>
    </div>
    <div class="url" id="url">__APP__</div>
    <ol class="steps small muted">
      <li>iPhone: otevřít v Safari → Sdílet → Přidat na plochu.</li>
      <li>Klíče služeb jednou: v aplikaci Nastavení → Naskenovat QR kód s klíči (QR vytvoří Mac).</li>
      <li>Každé zařízení má vlastní data — zálohu přenesete přes Nastavení → Záloha dat.</li>
    </ol>
  </section>

  <section class="hero">
    <h2>Ceník nabíjení</h2>
    <p class="small muted" id="meta"></p>
    <div class="filters">
      <label for="f-country">Země<select id="f-country"></select></label>
      <label for="f-op">Provozovatel<select id="f-op"></select></label>
      <label for="f-kind">Výkon<select id="f-kind"><option value="all">vše</option><option value="AC">AC (do 49 kW)</option>
        <option value="DC">DC</option><option value="HPC">HPC / UFC</option></select></label>
      <label for="f-pay">Platba<select id="f-pay"><option value="all">všechny</option><option value="member">členství / registrace</option>
        <option value="roaming">roaming čipem PRE</option><option value="adhoc">jednorázově</option></select></label>
    </div>
  </section>
  <div class="list" id="list"></div>
  <p class="foot">Ceny bez DPH v Kč za kWh; stání v Kč/min po uvedené době. Závazný je ceník provozovatele.
    Stav „staré“ = ověřeno před více než __STALE__ dny; neověřené údaje nejsou aktuální ceny. Stejná data používá aplikace (aktualizace denně).</p>
</main>
<script>
const DATA = __DATA__;
const COUNTRY = { CZ: "Česko", SK: "Slovensko", AT: "Rakousko", DE: "Německo", PL: "Polsko", HU: "Maďarsko", SI: "Slovinsko",
  HR: "Chorvatsko", IT: "Itálie", EU: "více zemí" };
const KIND = { AC: "AC", DC: "DC", HPC: "HPC / UFC" };
const n2 = (v) => v.toLocaleString("cs-CZ", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const d = (iso) => iso ? new Date(iso + "T12:00:00").toLocaleDateString("cs-CZ") : "—";
const age = (iso) => (Date.now() - new Date(iso + "T12:00:00").getTime()) / 864e5;
const pay = (e) => e.payment.includes("roaming") ? "roaming" : e.membership ? "member" : "adhoc";
function state(e) {
  if (e.status !== "ověřeno") return [e.status, false];
  if (!e.verified || age(e.verified) > DATA.stale_after_days) return ["staré — ověřeno " + d(e.verified), false];
  return ["ověřeno " + d(e.verified), true];
}
const el = (t, a = {}, ...c) => { const x = document.createElement(t); Object.assign(x, a); x.append(...c); return x; };
function fill(id, values, label, all) {
  const s = document.getElementById(id);
  s.append(el("option", { value: "all", textContent: all }));
  for (const v of values) s.append(el("option", { value: v, textContent: label(v) }));
}
fill("f-country", [...new Set(DATA.entries.map((e) => e.country))].sort(), (c) => COUNTRY[c] || c, "všechny");
fill("f-op", [...new Set(DATA.entries.map((e) => e.operator))].sort((a, b) => a.localeCompare(b, "cs")), (o) => o, "všichni");
document.getElementById("meta").textContent = "Zdroje zkontrolovány " + d(DATA.checked || DATA.generated) + ". " + DATA.entries.length + " položek, ČR a sítě v Evropě přes roaming PRE.";
function render() {
  const f = (id) => document.getElementById(id).value;
  const [c, o, k, p] = ["f-country", "f-op", "f-kind", "f-pay"].map(f);
  const list = document.getElementById("list");
  list.replaceChildren();
  const shown = DATA.entries.filter((e) => (c === "all" || e.country === c || e.country === "EU") && (o === "all" || e.operator === o)
    && (p === "all" || pay(e) === p) && (k === "all" || e.tiers.some((t) => t.kind === k)));
  if (!shown.length) list.append(el("div", { className: "entry muted", textContent: "Filtru neodpovídá žádná položka." }));
  for (const e of shown) {
    const [lab, ok] = state(e);
    const src = DATA.sources[e.source];
    const head = el("div", { className: "head" },
      el("div", {}, el("b", { textContent: e.operator }), el("span", { className: "muted", textContent: " · " + (COUNTRY[e.country] || e.country) + (e.region ? ", " + e.region : "") }),
        el("div", { className: "small muted", textContent: e.plan + " · " + e.payment + (e.fee_month ? " · " + n2(e.fee_month) + " Kč/měs." : "") })),
      el("span", { className: "pill" + (ok ? " ok" : ""), textContent: lab }));
    const box = el("div", { className: "entry" }, head);
    if (e.tiers.length) {
      const tb = el("tbody");
      for (const t of e.tiers) tb.append(el("tr", {}, el("td", { textContent: KIND[t.kind] }),
        el("td", { textContent: t.to_kw ? t.from_kw + "–" + t.to_kw + " kW" : "od " + t.from_kw + " kW" }),
        el("td", { className: "n", textContent: n2(t.price) }),
        el("td", { className: "small", textContent: t.price_min ? n2(t.price_min) + " Kč/min po " + t.after_min + " min" : "—" })));
      const th = el("thead", {}, el("tr", {}, ...["Typ", "Výkon", "Kč/kWh", "Stání"].map((h) => el("th", { textContent: h }))));
      box.append(el("div", { className: "tw" }, el("table", {}, th, tb)));
    } else box.append(el("p", { className: "small muted", textContent: "Ověřený ceník není k dispozici." }));
    if (e.note) box.append(el("p", { className: "small muted", textContent: e.note }));
    box.append(el("div", { className: "small muted" }, src ? el("span", {}, "Zdroj: ", el("a", { href: src.url, target: "_blank", rel: "noopener", textContent: src.name }))
                                                        : "Zdroj: vlastní odhad"));
    list.append(box);
  }
}
for (const id of ["f-country", "f-op", "f-kind", "f-pay"]) document.getElementById(id).addEventListener("change", render);
render();
document.getElementById("copy").addEventListener("click", (ev) => {
  const done = () => { ev.target.textContent = "Zkopírováno"; };
  try { navigator.clipboard.writeText("__APP__").then(done, () => { getSelection().selectAllChildren(document.getElementById("url")); }); }
  catch { getSelection().selectAllChildren(document.getElementById("url")); }
});
</script>
"""

out = ROOT / "artefakt/voyah-trasy.html"
out.write_text(HTML.replace("__APP__", APP).replace("__STALE__", str(DATA["stale_after_days"]))
               .replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")))
print(out)
