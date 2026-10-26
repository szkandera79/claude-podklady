#!/usr/bin/env python3
"""Sestaví ../nahradni-dily.html (artefakt) z ../data/nahradni-dily-rh030-rh060.json.
Spuštění: python3 reo-nahradni-dily/src/build_html.py"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "..", "data", "nahradni-dily-rh030-rh060.json"), encoding="utf-8"))
LOGO = open(os.path.expanduser("~/Claude/REO/logo/logo-reo-heating.svg"), encoding="utf-8").read()
LOGO = LOGO.replace('fill="#363533"', 'style="fill:var(--logo-ink)"').replace('fill="#838383"', 'style="fill:var(--logo-grey)"')
LOGO = re.sub(r'<svg ', '<svg class="logo" ', LOGO, count=1)

RATE, RATE_DATE = 21.741, "23. 10. 2026"
DUTY, VAT = 2.5, 21          # clo % z ceny (orientačně, dle HS kódu), DPH %

HTML = r"""<title>Náhradní díly RH030–RH060</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: servisní katalog — hlavička s kurzem, záložky modelů, tabulka po skupinách dílů */
:root{
  --bg:#F6F8F6; --surface:#FFFFFF; --ink:#1D2420; --muted:#66716B; --line:#DFE6E1;
  --green:#34A263; --green-ink:#1F7A47; --green-soft:#E9F6EE; --amber:#B7791F; --amber-soft:#FDF3E1;
  --logo-ink:#363533; --logo-grey:#838383;
  --f-body:"Figtree", "Segoe UI", system-ui, sans-serif;
  --f-mono:"IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121614; --surface:#1A201D; --ink:#E6ECE8; --muted:#97A39C; --line:#2C3531;
  --green:#46B876; --green-ink:#7FD3A2; --green-soft:#1C2E24; --amber:#E2A84B; --amber-soft:#2E2617;
  --logo-ink:#E6ECE8; --logo-grey:#A9B0AC; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121614; --surface:#1A201D; --ink:#E6ECE8; --muted:#97A39C; --line:#2C3531;
  --green:#46B876; --green-ink:#7FD3A2; --green-soft:#1C2E24; --amber:#E2A84B; --amber-soft:#2E2617;
  --logo-ink:#E6ECE8; --logo-grey:#A9B0AC; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.45}
.wrap{max-width:1180px;margin:0 auto;padding-block:28px 48px;
  padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px))}
header{display:flex;flex-wrap:wrap;gap:20px 32px;align-items:center;justify-content:space-between;
  border-bottom:3px solid var(--green);padding-bottom:20px}
.brand{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
.logo{width:150px;height:auto;display:block}
h1{font-size:clamp(24px,3.4vw,34px);font-weight:800;margin:0;letter-spacing:-.01em;text-wrap:balance}
.sub{color:var(--green-ink);font-weight:600;margin:2px 0 0}
.rates{display:flex;flex-wrap:wrap;gap:8px}
.rate{display:flex;flex-direction:column;gap:4px;background:var(--surface);border:1px solid var(--line);
  border-radius:10px;padding:10px 14px}
.rate label{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.rate .row{display:flex;align-items:center;gap:8px}
#rate{width:104px!important}
.rate input{width:84px;font:600 18px var(--f-mono);color:var(--ink);background:var(--bg);border:1px solid var(--line);
  border-radius:6px;padding:4px 8px}
.rate small{color:var(--muted);font-size:12px}
.rate button{font:600 12px var(--f-body);color:var(--green-ink);background:none;border:0;padding:0;cursor:pointer;text-decoration:underline}
input:focus-visible,button:focus-visible{outline:2px solid var(--green);outline-offset:2px}

.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:24px 0 18px}
.tab{font:600 14px var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);
  border-radius:999px;padding:8px 16px;cursor:pointer}
.tab small{color:var(--muted);font-weight:500;margin-left:4px}
.tab[aria-selected="true"]{background:var(--green);border-color:var(--green);color:#fff}
.tab[aria-selected="true"] small{color:#E3F5EA}
.tab.cmp{margin-left:auto}

.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:18px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.kpi .k{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.kpi .v{font-size:22px;font-weight:800;font-variant-numeric:tabular-nums;margin-top:2px}
.kpi .v2{font:500 13px var(--f-mono);color:var(--muted)}

.tools{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.tools input{flex:1 1 260px;min-width:0;font:15px var(--f-body);color:var(--ink);background:var(--surface);
  border:1px solid var(--line);border-radius:8px;padding:9px 12px}
.tools .meta{color:var(--muted);font-size:13px}

.tbl{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px}
table{width:100%;border-collapse:collapse;min-width:820px}
th,td{padding:9px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
thead th{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
  background:var(--bg);position:sticky;top:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr.grp td{background:var(--green-soft);color:var(--green-ink);font-weight:700;font-size:12px;letter-spacing:.1em;
  text-transform:uppercase;padding:7px 12px}
tr.grp td span{float:right;letter-spacing:0;text-transform:none;font-weight:600}
.pn{font-weight:600}
.en{display:block;color:var(--muted);font-size:12px}
.code{font:500 13px var(--f-mono);white-space:nowrap}
.spec{color:var(--muted);font-size:12.5px;max-width:360px}
.usd{font-family:var(--f-mono);font-size:13.5px}
.czk{font-weight:700}
.flag{display:inline-block;margin-left:6px;font-size:11px;font-weight:700;color:var(--amber);background:var(--amber-soft);
  border-radius:4px;padding:1px 6px;vertical-align:1px}
tfoot td{font-weight:800;border-bottom:0;background:var(--bg)}
mark{background:var(--amber-soft);color:inherit;border-radius:2px}
.notes{display:grid;gap:10px;margin-top:22px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.note{background:var(--amber-soft);border-radius:10px;padding:12px 16px;font-size:13.5px}
.note b{color:var(--amber)}
.note.info{background:var(--surface);border:1px solid var(--line)}
.note.info b{color:var(--green-ink)}
footer{margin-top:28px;color:var(--muted);font-size:12.5px;display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between}
.empty{padding:28px;text-align:center;color:var(--muted)}
@media (max-width:640px){.tab.cmp{margin-left:0}}
</style>

<div class="wrap">
<header>
  <div class="brand">
    __LOGO__
    <div>
      <h1>Náhradní díly RH030–RH060</h1>
      <p class="sub">Ceník náhradních dílů · tepelná čerpadla REO R290 · nákupní ceny</p>
    </div>
  </div>
  <div class="rates">
    <div class="rate">
      <label for="rate">Kurz USD → Kč</label>
      <div class="row"><input id="rate" type="number" step="0.001" min="1" inputmode="decimal"><small>Kč/USD</small></div>
      <small>ČNB __RATEDATE__</small>
    </div>
    <div class="rate">
      <label for="duty">Clo</label>
      <div class="row"><input id="duty" type="number" step="0.1" min="0" inputmode="decimal"><small>% z ceny</small></div>
      <small>dle HS kódu dílu</small>
    </div>
    <div class="rate">
      <label for="vat">DPH</label>
      <div class="row"><input id="vat" type="number" step="1" min="0" inputmode="decimal"><small>%</small></div>
      <small><button id="rateReset" type="button">vrátit výchozí</button></small>
    </div>
  </div>
</header>

<nav class="tabs" id="tabs" role="tablist"></nav>
<section id="view"></section>

<div class="notes">
  <div class="note info"><b>Ceny</b> jsou nákupní v USD za kus. Kč s clem a DPH = USD × kurz × (1 + clo) × (1 + DPH); DPH se počítá z ceny včetně cla. Doprava není zahrnuta. „Celkem“ = cena × počet kusů v jednotce.</div>
  <div class="note"><b>Clo 2,5 % je výchozí odhad.</b> Skutečná sazba se liší podle HS kódu dílu (kompresor, desky, čerpadlo…); upravte ji v hlavičce.</div>
</div>
<footer><span>Zdroj: Spare Part List – revised (PDF, 10/2026) · interní podklad, nešířit zákazníkům</span><span>REO HEATING · 10/2026</span></footer>
</div>

<script>
const DATA = __DATA__;
const DEFAULT_RATE = __RATE__, DEFAULT_DUTY = __DUTY__, DEFAULT_VAT = __VAT__;
const CAT = {chl:"Chladivový okruh", ele:"Elektronika a ovládání", cid:"Teplotní čidla", hyd:"Hydraulika", ven:"Ventilátor"};
const ORDER = ["chl","ele","hyd","ven","cid"];
function cz(p){
  const s = p.spec.toLowerCase();
  switch(p.name){
    case "Compressor": return ["Kompresor (inverter, R290)","chl"];
    case "Electronic expansion valve": return ["Elektronický expanzní ventil","chl"];
    case "Pressure Switch": return [s.startsWith("low") ? "Nízkotlaký presostat" : "Vysokotlaký presostat","chl"];
    case "Pressure Sensor": return ["Snímač tlaku 0–20 bar","chl"];
    case "Needle valve": return ["Servisní ventilek (jehlový)","chl"];
    case "Non-return valve": return ["Zpětný ventil chladiva","chl"];
    case "Circuit board":
      if (s.includes("driver")) return ["Modul měniče (driver)","ele"];
      if (s.includes("pump")) return ["Deska oběhového čerpadla","ele"];
      if (s.includes("filter")) return ["Filtrační deska (EMC)","ele"];
      if (s.includes("detection")) return ["Deska měření proudu","ele"];
      return ["Hlavní řídicí deska s měničem","ele"];
    case "Controller panel": return ["Ovládací panel (displej)","ele"];
    case "Reactor": return ["Tlumivka (PFC)","ele"];
    case "Coil": return [s.includes("dc12v") ? "Cívka expanzního ventilu (12 V DC)" : "Cívka 4cestného ventilu (230 V)","chl"];
    case "Signal cable": return ["Signální kabel","ele"];
    case "Temperature Sensor": return ["Teplotní čidlo " + (p.spec.match(/CC\.T\d+/)||[""])[0],"cid"];
    case "Circulation pump": return ["Oběhové čerpadlo","hyd"];
    case "Flow switch": return ["Průtokový spínač","hyd"];
    case "Pressure gauge": return ["Manometr","hyd"];
    case "Motor": return ["Motor ventilátoru (DC)","ven"];
    case "Fan blade": return ["Vrtule ventilátoru","ven"];
  }
  return [p.name,"ele"];
}
DATA.models.forEach(m => m.parts.forEach(p => { const [n,c] = cz(p); p.cz = n; p.cat = c; p.q = p.qty ?? 1; p.noQty = p.qty == null; }));

let duty = DEFAULT_DUTY, vat = DEFAULT_VAT;
let rate = DEFAULT_RATE, current = "RH030", query = "";
try { const r = parseFloat(localStorage.getItem("reo-rate")); if (r > 0) rate = r; const d = parseFloat(localStorage.getItem("reo-duty")); if (d >= 0) duty = d; const w = parseFloat(localStorage.getItem("reo-vat")); if (w >= 0) vat = w; const t = localStorage.getItem("reo-tab"); if (t) current = t; } catch(e){}
if (location.hash && (DATA.models.some(m => m.id === location.hash.slice(1)) || location.hash === "#srovnani")) current = location.hash.slice(1);

const fUSD = v => "$" + v.toLocaleString("en-US",{minimumFractionDigits:2, maximumFractionDigits:2});
const fCZK = v => Math.round(v * rate).toLocaleString("cs-CZ") + " Kč";
const full = v => v * rate * (1 + duty/100) * (1 + vat/100);
const fFULL = v => Math.round(full(v)).toLocaleString("cs-CZ") + " Kč";
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const hl = s => { s = esc(s); if (!query) return s; const q = query.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"); return s.replace(new RegExp(q,"gi"), m => "<mark>"+m+"</mark>"); };
const label = m => m.model;
const total = m => m.parts.reduce((a,p) => a + p.usd * p.q, 0);

function tabs(){
  const el = document.getElementById("tabs");
  el.innerHTML = DATA.models.map(m => `<button class="tab" role="tab" data-id="${m.id}" aria-selected="${m.id===current}">${label(m)}<small>${m.kw} kW · ${m.phase}</small></button>`).join("")
    + `<button class="tab cmp" role="tab" data-id="srovnani" aria-selected="${current==="srovnani"}">Srovnání modelů</button>`;
  el.querySelectorAll(".tab").forEach(b => b.onclick = () => { current = b.dataset.id; try{localStorage.setItem("reo-tab",current)}catch(e){} render(); });
}

function modelView(m){
  const parts = m.parts.filter(p => !query || [p.cz,p.name,p.code,p.spec].join(" ").toLowerCase().includes(query.toLowerCase()));
  const comp = m.parts.find(p => p.name === "Compressor");
  const t = total(m);
  let rows = "";
  for (const c of ORDER){
    const ps = parts.filter(p => p.cat === c); if (!ps.length) continue;
    const sub = ps.reduce((a,p) => a + p.usd*p.q, 0);
    rows += `<tr class="grp"><td colspan="8">${CAT[c]}<span>${fUSD(sub)} · ${fFULL(sub)} s clem a DPH</span></td></tr>`;
    rows += ps.map(p => `<tr>
      <td><span class="pn">${hl(p.cz)}</span><span class="en">${hl(p.name)}</span></td>
      <td class="code">${hl(p.code)}</td>
      <td class="spec">${hl(p.spec)}</td>
      <td class="n">${p.q}${p.noQty ? '<span class="flag" title="Počet v ceníku chybí">?</span>' : ""}</td>
      <td class="n usd">${fUSD(p.usd)}</td>
      <td class="n">${fCZK(p.usd)}</td>
      <td class="n czk">${fFULL(p.usd)}</td>
      <td class="n">${fFULL(p.usd*p.q)}</td></tr>`).join("");
  }
  return `
  <div class="summary">
    <div class="kpi"><div class="k">Jednotka</div><div class="v">${label(m)} · ${m.kw} kW</div><div class="v2">${esc(m.variant.replace(/-PW\d+/,""))} · BOM ${esc(m.bom)}</div></div>
    <div class="kpi"><div class="k">Kompresor s clem a DPH</div><div class="v">${fFULL(comp.usd)}</div><div class="v2">${fUSD(comp.usd)} · ${fCZK(comp.usd)} bez cla a DPH</div></div>
    <div class="kpi"><div class="k">Položek v ceníku</div><div class="v">${m.parts.length}</div><div class="v2">${m.parts.reduce((a,p)=>a+p.q,0)} ks celkem</div></div>
    <div class="kpi"><div class="k">Sada dílů s clem a DPH</div><div class="v">${fFULL(t)}</div><div class="v2">${fUSD(t)} · ${fCZK(t)} bez cla a DPH</div></div>
  </div>
  <div class="tools"><input id="q" type="search" placeholder="Hledat díl, kód nebo specifikaci…" value="${esc(query)}" aria-label="Hledat"><span class="meta">${parts.length} z ${m.parts.length} položek</span></div>
  <div class="tbl"><table>
    <thead><tr><th>Díl</th><th>Kód BOM</th><th>Specifikace</th><th class="n">Ks</th><th class="n">USD / ks</th><th class="n">Kč / ks<span class="en" style="text-transform:none;letter-spacing:0">bez cla a DPH</span></th><th class="n">Kč / ks<span class="en" style="text-transform:none;letter-spacing:0">s clem a DPH</span></th><th class="n">Celkem<span class="en" style="text-transform:none;letter-spacing:0">s clem a DPH</span></th></tr></thead>
    <tbody>${rows || '<tr><td colspan="8" class="empty">Nic nenalezeno — zkuste jiný výraz.</td></tr>'}</tbody>
    ${query ? "" : `<tfoot><tr><td colspan="4">Celkem za jednotku (cena × ks)</td><td class="n usd">${fUSD(t)}</td><td class="n">${fCZK(t)}</td><td></td><td class="n">${fFULL(t)}</td></tr></tfoot>`}
  </table></div>`;
}

function cmpView(){
  const groups = [
    ["Kompresor", p => p.name === "Compressor"],
    ["Hlavní deska / modul měniče", p => p.name === "Circuit board" && !/pump|filter|detection/i.test(p.spec)],
    ["Ostatní desky (čerpadlo, filtr, měření)", p => p.name === "Circuit board" && /pump|filter|detection/i.test(p.spec)],
    ["Ovládací panel (displej)", p => p.name === "Controller panel"],
    ["Oběhové čerpadlo", p => p.name === "Circulation pump"],
    ["Elektronický expanzní ventil", p => p.name === "Electronic expansion valve"],
    ["Ventilátor (motor + vrtule)", p => p.cat === "ven"],
    ["Snímač tlaku + presostaty", p => /Pressure (Sensor|Switch)/.test(p.name)],
    ["Teplotní čidla", p => p.cat === "cid"],
    ["Ostatní (kabely, tlumivka, ventilky, cívky, spínač průtoku, manometr)", null],
  ];
  const used = new Set();
  const rows = groups.map(([name, fn]) => {
    const cells = DATA.models.map(m => {
      const ps = m.parts.filter(p => fn ? fn(p) : !used.has(p));
      if (fn) ps.forEach(p => used.add(p));
      const v = ps.reduce((a,p) => a + p.usd*p.q, 0);
      return v ? `<td class="n"><span class="czk">${fFULL(v)}</span><span class="en">${fUSD(v)} · ${fCZK(v)}</span></td>` : `<td class="n"><span class="en">—</span></td>`;
    });
    return `<tr><td class="pn">${name}</td>${cells.join("")}</tr>`;
  });
  return `<div class="tbl"><table>
    <thead><tr><th>Skupina dílů (cena × ks, Kč s clem a DPH)</th>${DATA.models.map(m => `<th class="n">${label(m)}<span class="en" style="text-transform:none;letter-spacing:0">${m.kw} kW · ${m.phase}</span></th>`).join("")}</tr></thead>
    <tbody>${rows.join("")}</tbody>
    <tfoot><tr><td>Sada dílů celkem</td>${DATA.models.map(m => `<td class="n"><span class="czk">${fFULL(total(m))}</span><span class="en">${fUSD(total(m))} · ${fCZK(total(m))}</span></td>`).join("")}</tr></tfoot>
  </table></div>`;
}

function render(){
  tabs();
  const v = document.getElementById("view");
  v.innerHTML = current === "srovnani" ? cmpView() : modelView(DATA.models.find(m => m.id === current) || DATA.models[0]);
  const q = document.getElementById("q");
  if (q) q.oninput = e => { query = e.target.value; const pos = e.target.selectionStart; render(); const n = document.getElementById("q"); n.focus(); n.setSelectionRange(pos,pos); };
}
const ri = document.getElementById("rate");
ri.value = rate;
const di = document.getElementById("duty"), vi = document.getElementById("vat");
di.value = duty; vi.value = vat;
di.oninput = () => { const d = parseFloat(di.value); if (d >= 0){ duty = d; try{localStorage.setItem("reo-duty",d)}catch(e){} render(); } };
vi.oninput = () => { const w = parseFloat(vi.value); if (w >= 0){ vat = w; try{localStorage.setItem("reo-vat",w)}catch(e){} render(); } };
ri.oninput = () => { const r = parseFloat(ri.value); if (r > 0){ rate = r; try{localStorage.setItem("reo-rate",r)}catch(e){} render(); } };
document.getElementById("rateReset").onclick = () => { rate = DEFAULT_RATE; duty = DEFAULT_DUTY; vat = DEFAULT_VAT; ri.value = rate; di.value = duty; vi.value = vat; try{["reo-rate","reo-duty","reo-vat"].forEach(k => localStorage.removeItem(k))}catch(e){} render(); };
render();
</script>
"""

out = (HTML.replace("__LOGO__", LOGO).replace("__DATA__", json.dumps(DATA, ensure_ascii=False))
       .replace("__RATE__", str(RATE)).replace("__DUTY__", str(DUTY)).replace("__VAT__", str(VAT)).replace("__RATEDATE__", RATE_DATE))
dst = os.path.normpath(os.path.join(HERE, "..", "nahradni-dily.html"))
open(dst, "w", encoding="utf-8").write(out)
print("zapsáno:", dst)
