// Srovnávací list REO R290 (2 strany A4): 1 = sezónní účinnost SCOP, 2 = hlučnost.
// Používá stejná data jako artefakt (MODELS[...].scop / .noise). Text je česky — list slouží
// jako podklad k nabídce, na rozdíl od datových listů s hodnotami výrobce v angličtině.
const f2c = v => v.toFixed(2).replace('.', ',');
const lpAt = (lwa, r) => Math.round(lwa - 20 * Math.log10(r) - 8);

function cmpHeader(ASSETS, title, sub){
  return `<header><h1>${title}<small>${sub}</small></h1><img src="${ASSETS.logo}" alt="REO HEATING"></header>`;
}

// Řádky sloupcového grafu: [{name, ref, bars:[{cls, v, txt}]}], osa 0..max
function cmpBars(rows, axis, fmt){
  const pos = v => ((v - axis[0]) / (axis[1] - axis[0])) * 100;
  const ticks = [];
  for (let v = axis[0]; v <= axis[1] + 1e-9; v += axis[2]) ticks.push(v);
  return `<div class="cmp-bars">${rows.map(r => `
    <div class="cmp-name${r.ref ? ' ref' : ''}">${r.name}</div>
    <div class="cmp-track">${r.bars.map(b =>
      `<div class="cmp-bar ${b.cls}"><i style="width:${pos(b.v)}%"></i><b>${fmt(b.v)}</b></div>`).join('')}</div>`).join('')}
    <div class="cmp-axis">${ticks.map(v => `<span style="left:${pos(v)}%">${fmt(v)}</span>`).join('')}</div>
  </div>`;
}

function cmpLegend(items){
  return `<div class="cmp-legend">${items.map(([cls, txt]) =>
    `<span><i class="${cls}"></i>${txt}</span>`).join('')}</div>`;
}

function scopPage(ASSETS){
  const rows = Object.entries(MODELS).filter(([, M]) => M.scop);
  const x50 = MODELS.RHX50.scop, x30 = MODELS.RHX30.scop;
  const pct = (a, b) => ((a / b - 1) * 100).toFixed(0);
  const less = (a, b) => ((1 - a / b) * 100).toFixed(0);
  const drop = (hi, lo) => ((1 - lo / hi) * 100).toFixed(0);

  const bars = cmpBars(rows.map(([k, M]) => ({
    name: M.name + (k === 'RH060' ? ' *' : ''), ref: k === 'RH060',
    bars: [{cls:'w35', v:M.scop.en[35]}, {cls:'w55', v:M.scop.en[55]}],
  })), [0, 6, 1], v => (v % 1 ? f2c(v) : String(v)));

  const tiles = [
    ['W35 — RHX30 Pro proti RH X50', `+${pct(x30.en[35], x50.en[35])} %`, `o ${less(x50.en[35], x30.en[35])} % nižší spotřeba elektřiny`],
    ['W55 — RHX30 Pro proti RH X50', `+${pct(x30.en[55], x50.en[55])} %`, `o ${less(x50.en[55], x30.en[55])} % nižší spotřeba elektřiny`],
    ['Propad SCOP W35 → W55', `RHX30 Pro −${drop(x30.en[35], x30.en[55])} %`, `RH X50 −${drop(x50.en[35], x50.en[55])} %`],
    ['Hlučnost v 1 m (W55)', `${MODELS.RHX30.noise.lp55} vs. ${MODELS.RHX50.noise.lp55} dB`, `RHX30 Pro je o ${MODELS.RHX50.noise.lp55 - MODELS.RHX30.noise.lp55} dB tišší než RH X50`],
  ];

  return `
  <div class="page cmp">
    ${cmpHeader(ASSETS, 'Srovnání sezónní účinnosti', 'SCOP dle EN 14825 · certifikace KEYMARK · tepelná čerpadla vzduch–voda R290')}
    <p class="cmp-lede">Sezónní topný faktor SCOP pro ekvitermní provoz s výstupní vodou 35 °C (podlahové vytápění)
      a 55 °C (radiátory). Hodnoty jsou certifikované podle EN 14825 pro průměrné klima; sloupce „ČR" v tabulce
      jsou přepočet na české klima s výpočtovou teplotou −15 °C.</p>
    ${cmpLegend([['w35','W35 — podlahové vytápění'], ['w55','W55 — radiátory']])}
    ${bars}
    <div class="cmp-tiles">${tiles.map(([dt, dd, note]) =>
      `<div><span class="dt">${dt}</span><span class="dd">${dd}</span><span class="nt">${note}</span></div>`).join('')}</div>
    <table class="cmp-tab narrow">
      <thead><tr><th class="l">Model</th><th>SCOP W35</th><th>SCOP W55</th>
        <th>ČR W35</th><th>ČR W45</th><th>ČR W55</th><th>ČR W65</th>
        <th>Hluk<br>1 m</th><th>Hluk<br>L<sub>WA</sub></th>
        ${TJ.map(t => `<th>COP ${String(t).replace('-','−')} °C<br>W55</th>`).join('')}</tr></thead>
      <tbody>${rows.map(([k, M]) => {
        const s = M.scop;
        return `<tr class="${k === 'RH060' ? 'ref' : ''}"><td class="l">${M.name}${k === 'RH060' ? ' *' : ''}</td>
          <td class="hi">${f2c(s.en[35])}</td><td class="hi">${f2c(s.en[55])}</td>
          ${[35,45,55,65].map(w => `<td>${f2c(s.cz[w])}</td>`).join('')}
          <td class="hi">${M.noise.lp55}</td><td>${M.noise.lwa55}</td>
          ${s.cop[55].map(v => `<td>${f2c(v)}</td>`).join('')}</tr>`;
      }).join('')}</tbody>
    </table>
    <div class="cmp-sum">
      <h3>Co z čísel plyne</h3>
      <ul>
        <li><b>RHX30 Pro je účinnější v obou režimech</b> a rozdíl roste s teplotou otopné vody: při W35 o ${pct(x30.en[35], x50.en[35])} %, při W55 o ${pct(x30.en[55], x50.en[55])} %. U radiátorových soustav je tedy jeho náskok větší než u podlahového vytápění.</li>
        <li><b>V mrazu jsou si jednotky blízko</b> — při −10 °C a W55 má RH X50 dokonce navrch (COP ${f2c(x50.cop[55][0])} vs. ${f2c(x30.cop[55][0])}). Sezónní rozdíl vzniká v přechodném období, kde jednotky běží nejvíc hodin (+7 °C: ${f2c(x30.cop[55][3])} vs. ${f2c(x50.cop[55][3])}).</li>
        <li><b>RHX30 Pro je zároveň tišší</b> — ${MODELS.RHX30.noise.lp55} dB v 1 m proti ${MODELS.RHX50.noise.lp55} dB u RH X50 (rozdíl ${MODELS.RHX50.noise.lp55 - MODELS.RHX30.noise.lp55} dB, tedy zhruba čtvrtinová hlasitost vnímaná sluchem). U zástavby s okny sousedů to bývá stejně důležité kritérium jako účinnost — podrobnosti na druhé straně.</li>
        <li><b>Do zhruba 90–100 kW je volbou RH060</b> — při W55 má prakticky stejný SCOP jako RHX30 Pro (${f2c(MODELS.RH060.scop.en[55])} vs. ${f2c(x30.en[55])}) a v českém klimatu i lepší (${f2c(MODELS.RH060.scop.cz[55])} vs. ${f2c(x30.cz[55])}). RHX30 Pro dává smysl nad touto hranicí, RH X50 u velkých vysokoteplotních objektů.</li>
      </ul>
    </div>
    <p class="cmp-note">Body COP jsou certifikované hodnoty při W55 a relativní zátěži dle EN 14825 (Tj = −10 / −7 / +2 / +7 / +12 °C).
      Přepočet na české klima interpoluje COP mezi těmito body, pod −10 °C extrapoluje z výkonových map výrobce — je to výpočet, ne certifikát.
      * RH060 je uveden jako referenční jednotka domovní řady. Deklarovaný výkon RHX30 Pro při −15 °C je podle výkonové mapy nižší,
      než by odpovídalo certifikaci; u velkých kaskád doporučujeme ověřit měřením.</p>
  </div>`;
}

function noisePage(ASSETS){
  const rows = Object.entries(MODELS).filter(([, M]) => M.noise);
  const bars = cmpBars(rows.map(([, M]) => ({
    name: M.name,
    bars: [{cls:'lwa', v:M.noise.lwa55}, {cls:'lp', v:M.noise.lp55}],
  })), [35, 70, 5], v => String(v));

  return `
  <div class="page cmp">
    ${cmpHeader(ASSETS, 'Srovnání hlučnosti', 'Akustický výkon a akustický tlak · aplikace 55 °C · tepelná čerpadla vzduch–voda R290')}
    <p class="cmp-lede">Akustický výkon L<sub>WA</sub> (hodnota z energetického štítku, resp. z podkladů výrobce) a akustický tlak
      ve vzdálenosti 1 m při provozu s výstupní vodou 55 °C, tedy v nejhlasitějším režimu.</p>
    ${cmpLegend([['lwa','Akustický výkon (LWA)'], ['lp','Akustický tlak v 1 m']])}
    ${bars}
    <table class="cmp-tab">
      <thead><tr><th class="l">Model</th><th>L<sub>WA</sub> 35 °C</th><th>L<sub>WA</sub> 55 °C</th><th>Energetický štítek</th>
        <th>Tlak v 1 m</th><th>3 m</th><th>5 m</th><th>10 m</th></tr></thead>
      <tbody>${rows.map(([, M]) => {
        const n = M.noise, d = r => { const v = lpAt(n.lwa55, r); return `<td class="${v <= 40 ? 'ok' : ''}">${v}</td>`; };
        return `<tr><td class="l">${M.name}</td><td>${n.lwa35 ?? '—'}</td><td class="hi">${n.lwa55}${n.lwaMax ? ' *' : ''}</td>
          <td>${n.label ?? '—'}</td><td class="hi">${n.lp55}</td>${d(3)}${d(5)}${d(10)}</tr>`;
      }).join('')}</tbody>
    </table>
    <div class="cmp-sum">
      <h3>Co z čísel plyne</h3>
      <ul>
        <li><b>Nejtišší je RHX30 Pro</b> (${MODELS.RHX30.noise.lp55} dB v 1 m) — a to při nejvyšším výkonu domovních i komerčních jednotek kromě RH X50. Z domovní řady je nejtišší RH030 (${MODELS.RH030.noise.lp55} dB), nejhlasitější RH040 (${MODELS.RH040.noise.lp55} dB).</li>
        <li><b>Domovní modely se pod noční limit 40 dB dostanou orientačně od 5 m</b> od jednotky; při 3 m jsou na hraně (${lpAt(MODELS.RH040.noise.lwa55, 3)}–${lpAt(MODELS.RH030.noise.lwa55, 3)} dB).</li>
        <li><b>RH X50 potřebuje odstup zhruba 10 m</b> (${lpAt(MODELS.RHX50.noise.lwa55, 10)} dB) — u zástavby s okny sousedů blíž je na místě umístění s protihlukovou clonou nebo akustická studie.</li>
      </ul>
    </div>
    <p class="cmp-note">Hodnoty v dB, resp. dB(A). Odstup 3–10 m je orientační výpočet pro volné pole nad odrazivou plochou
      (L<sub>p</sub> = L<sub>WA</sub> − 20·log₁₀ r − 8), ne měření — skutečnost ovlivní odrazy od stěn, protihlukové clony i umístění jednotky;
      pro konkrétní projekt nenahradí akustickou studii. Zvýrazněné hodnoty jsou do 40 dB, což je noční hygienický limit
      u chráněného venkovního prostoru staveb. * U RH X50 uvádějí podklady výrobce maximální akustický výkon ≤ 77 dB,
      energetický štítek deklaruje 66 dB; v tabulce je hodnota ze štítku. RHX30 Pro zatím nemá energetický štítek,
      jeho hodnoty jsou z podkladů výrobce.</p>
  </div>`;
}

function renderCompare(root, ASSETS){
  root.innerHTML = scopPage(ASSETS) + noisePage(ASSETS);
}
