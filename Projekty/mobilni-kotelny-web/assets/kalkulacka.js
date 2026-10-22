/* Kalkulačka celkové ceny tepla — UI nad calc-core.js */
(function () {
  const $ = (id) => document.getElementById(id);
  const PRICE_KEYS = [
    { key: 'el', label: 'Elektřina', unit: 'Kč/kWh', step: 0.1 },
    { key: 'plyn', label: 'Zemní plyn', unit: 'Kč/kWh', step: 0.05 },
    { key: 'lpg', label: 'Propan (LPG)', unit: 'Kč/l', step: 0.5 },
    { key: 'lto', label: 'Lehký topný olej', unit: 'Kč/l', step: 0.5 },
    { key: 'nafta', label: 'Nafta', unit: 'Kč/l', step: 0.5 },
    { key: 'pelety', label: 'Pelety', unit: 'Kč/kg', step: 0.1 },
  ];
  const defaultPrice = (key) => TECH.find(t => t.src === key).price;

  // --- sestavení vstupů ---
  $('flh-txt').textContent = fmt(FULL_LOAD_HOURS);
  document.querySelectorAll('.datum').forEach(el => { el.textContent = DATUM_CEN; });
  $('start').innerHTML = MONTHS.map((m, i) => `<option value="${i}"${i === 9 ? ' selected' : ''}>${m}</option>`).join('');
  $('soustava').innerHTML = Object.entries(SOUSTAVY).map(([k, s]) => `<option value="${k}"${k === 'stredni' ? ' selected' : ''}>${s.label}</option>`).join('');
  $('prices').innerHTML = PRICE_KEYS.map(p => `
    <tr><td class="l">${p.label} <span class="t t-O" title="${SOURCES[p.key].t}">O</span></td>
    <td><input type="number" min="0" step="${p.step}" id="p-${p.key}" value="${defaultPrice(p.key)}" aria-label="${p.label} ${p.unit}"></td>
    <td class="l note">${p.unit}</td></tr>`).join('');
  $('rents').innerHTML = TECH.map(t => `
    <tr><td class="l">${t.name} ${t.rent != null ? `<span class="t t-${t.rentTag}">${t.rentTag}</span>` : ''}</td>
    <td style="text-align:center"><input type="checkbox" id="inc-${t.id}" checked aria-label="Zahrnout ${t.name}" style="width:auto"></td>
    <td><input type="number" min="0" step="1000" id="r-${t.id}" value="${t.rent ?? ''}" placeholder="neznámý" aria-label="Nájem ${t.name}"></td>
    <td><input type="number" min="0" step="1000" id="o-${t.id}" value="${t.once ?? ''}" placeholder="neznámé" aria-label="Jednorázově ${t.name}"></td>
    <td><input type="number" min="0" step="500" id="x-${t.id}" value="0" aria-label="Další náklady ${t.name}"></td></tr>`).join('');
  $('sources').innerHTML = Object.values(SOURCES).map(s => `<li>${s.u ? `<a href="${s.u}" target="_blank" rel="noopener">${s.t}</a>` : s.t}</li>`).join('') +
    `<li>Výhřevnost: nafta a LTO 10 kWh/l, propan 6,6 kWh/l, pelety 4,6 kWh/kg (norma pro pelety A1 ≥ 16,5 MJ/kg).</li>
     <li>Účinnost <span class="t t-P">P</span>: kotle na olej a naftu 90 %, plyn a LPG 93 %, pelety 85 %, elektrokotel 99 %.</li>
     <li>Tepelné čerpadlo <span class="t t-O">O</span>: sezónní topný faktor ${Object.values(SOUSTAVY).filter(s => s.tag === 'O').map(s => fmt(s.spf, 2)).join(' / ')} podle teploty vody, vypočtený z výkonových map RH X50 pro typický průběh teplot.</li>
     <li>Nájmy konkurence <span class="t t-P">P</span>: střední hodnota veřejných ceníků 35–60 tis. Kč/měs. (zahraniční půjčovny, přepočet kurzem). U pelet a elektrokotle nájem v ČR nemáme ověřený.</li>
     <li>Nájem tepelného čerpadla <span class="t t-I">I</span>: orientační ceník ThermaVera pro kotelnu ≈ 50 kW. Přesnou cenu stanoví nabídka.</li>
     <li>Výpočet nezahrnuje teplou vodu, stálé platby za přípojky a ceny povolenek ETS2.</li>`;

  // --- čtení vstupů ---
  const num = (id) => { const v = parseFloat($(id).value); return Number.isFinite(v) ? v : null; };
  const mode = () => document.querySelector('input[name=mode]:checked').value;

  function heatNeed(months, start) {
    const share = periodShare(start, Math.min(months, 12)) + Math.max(0, months - 12) / 12;   // nad 12 měsíců průměrně
    if (mode() === 'kw') return (num('kw') || 0) * FULL_LOAD_HOURS / 1000 * share;
    if (mode() === 'rok') {
      const v = num('rok') || 0, u = $('rokUnit').value;
      const annual = u === 'gj' ? v / GJ_PER_MWH : u === 'mwh' ? v : v * 10.6 * 0.9 / 1000;
      return annual * share;
    }
    const v = num('obd') || 0;
    return $('obdUnit').value === 'gj' ? v / GJ_PER_MWH : v;
  }

  function readTechs() {
    return TECH.filter(t => $('inc-' + t.id).checked).map(t => ({
      ...t,
      price: num('p-' + t.src) ?? 0,
      rent: num('r-' + t.id),
      once: num('o-' + t.id),
      other: num('x-' + t.id) || 0,
    }));
  }

  const fuelTxt = (r) => {
    if (r.unit === 'kWh') return `${fmt(r.fuel / 1000, 1)} MWh`;
    if (r.unit === 'kg') return `${fmt(r.fuel / 1000, 1)} t`;
    return `${fmt(r.fuel)} l`;
  };
  const unitTxt = (r) => (r.unit === 'kWh' ? 'Kč/kWh' : r.unit === 'kg' ? 'Kč/kg' : 'Kč/l');

  // --- výpočet a vykreslení ---
  function render() {
    const months = Math.max(1, Math.round(num('months') || 1));
    const start = +$('start').value;
    const soustava = $('soustava').value;
    $('elshare-wrap').hidden = soustava !== 'vysoka';
    const elShare = soustava === 'vysoka' ? Math.min(100, Math.max(0, num('elshare') ?? 30)) / 100 : 0;
    const factor = hpFactor(soustava, elShare);
    $('spf-hint').innerHTML = `Tepelné čerpadlo vyrobí z 1 kWh elektřiny ≈ ${fmt(factor, 2)} kWh tepla <span class="t t-${SOUSTAVY[soustava].tag}">${SOUSTAVY[soustava].tag}</span>.`;

    const q = heatNeed(months, start);
    const vat = document.querySelector('input[name=vat]:checked').value === '1' ? VAT : 1;
    const money = (n) => fmtKc(n * vat);
    const techs = readTechs();
    const res = compute({ q, months, soustava, elShare, techs }).sort((a, b) => a.total - b.total);
    const tc = res.find(r => r.id === 'tc');

    // KPI
    $('k-q').textContent = `${fmt(q, 1)} MWh`;
    $('k-q2').textContent = `${fmt(q * GJ_PER_MWH)} GJ · ${months} měs., začátek ${MONTHS[start]}`;
    $('k-tc').textContent = tc ? money(tc.total) : '–';
    $('k-tc2').textContent = tc && q > 0 ? `${fmt(tc.perMwh / GJ_PER_MWH * vat)} Kč za GJ tepla` : 'není zahrnuto';
    const known = res.filter(r => r.rentKnown);
    const best = known[0];
    $('k-best').textContent = best ? best.name : '–';
    $('k-best2').textContent = best ? money(best.total) : '';

    // grafy
    const max = Math.max(...res.map(r => r.total), 1);
    const w = (v) => (v / max * 100).toFixed(2) + '%';
    $('bars').innerHTML = res.map(r => `
      <div class="bar-row${r.ours ? ' ours' : ''}${r.rentKnown ? '' : ' unknown'}">
        <span class="nm">${r.name}</span>
        <div class="bar" role="img" aria-label="${r.name}: celkem ${money(r.total)}">
          <i class="s-rent" style="width:${w(r.rent)}"></i><i class="s-once" style="width:${w(r.once)}"></i><i class="s-energy" style="width:${w(r.energy)}"></i><i style="width:${w(r.other)};background:#e7ecef"></i>
        </div>
        <span class="val">${money(r.total)}${r.rentKnown ? '' : ' <span class="unk" title="Nájem neznámý">+ nájem?</span>'}</span>
      </div>`).join('');

    // rozpis
    $('detail').innerHTML = res.map(r => `
      <tr class="${r.ours ? 'ours' : ''}"><td class="l">${r.name}</td><td>${fuelTxt(r)}</td><td>${money(r.energy)}</td>
      <td>${r.rentKnown ? money(r.rent) : '<span class="unk">?</span>'}</td><td>${r.once ? money(r.once) : (r.rentKnown ? '0 Kč' : '<span class="unk">?</span>')}</td>
      <td>${money(r.other)}</td><td><b>${money(r.total)}</b></td><td>${q > 0 ? fmt(r.perMwh / GJ_PER_MWH * vat) : '–'}</td></tr>`).join('');

    // bod zvratu
    const be = [];
    if (tc) {
      res.filter(r => r.id !== 'tc').forEach(r => {
        const p = breakEven(r, tc);
        const cur = `${fmt(r.price, 2)} ${unitTxt(r)}`;
        const note = r.rentKnown ? '' : ' (bez nájmu, který neznáme)';
        if (p == null) return;
        if (p <= 0) be.push(`<li><b>${r.name}:</b> tepelné čerpadlo vyjde dráž i při nulové ceně paliva${note}. Rozhoduje rozdíl v nájmu.</li>`);
        else if (r.price > p) be.push(`<li><b>${r.name}:</b> tepelné čerpadlo je levnější, dokud ${r.fuelName} stojí víc než <b>${fmt(p, 2)} ${unitTxt(r)}</b> (zadáno ${cur})${note}.</li>`);
        else be.push(`<li><b>${r.name}:</b> tepelné čerpadlo by bylo levnější až při ceně nad <b>${fmt(p, 2)} ${unitTxt(r)}</b> (zadáno ${cur})${note}.</li>`);
      });
    }
    $('be').innerHTML = be.join('') || '<li>Zahrňte tepelné čerpadlo a aspoň jeden další zdroj.</li>';

    // sdělení
    const msgs = [];
    const byRent = known.filter(r => r.rent > 0).sort((a, b) => a.rent / months - b.rent / months);
    if (byRent.length > 1 && byRent[0].id !== best.id) {
      const r = byRent[0];
      const rank = known.indexOf(r) + 1;
      msgs.push(`<div class="callout"><b>Nízký nájem ≠ nízké náklady.</b> Nejnižší nájem má ${r.name}, celkově ale vychází na ${rank}. místě ze ${known.length}. Palivo tvoří ${fmt(r.energy / r.total * 100)} % jeho nákladů.</div>`);
    }
    if (tc && best && best.id !== 'tc') msgs.push(`<div class="callout">Při zadaných hodnotách vychází celkově levněji <b>${best.name}</b> než tepelné čerpadlo, o ${money(tc.total - best.total)}. Kalkulačka to ukazuje stejně otevřeně jako opačné případy. Pro rozhodnutí zvažte i provoz bez paliva a spalin.</div>`);
    if (tc && q / months < 3) msgs.push(`<div class="callout">Potřeba tepla je v tomto období nízká (≈ ${fmt(q / months, 1)} MWh za měsíc). Mimo topnou sezónu rozhoduje hlavně nájem, ne cena energie.</div>`);
    if (soustava === 'vysoka') msgs.push(`<div class="callout">Soustava nad 55 °C: počítáme s ${fmt(elShare * 100)} % tepla z elektrického dohřevu. Mnoho soustav navržených na 90/70 °C stačí s nižší teplotou. Ověříme to na obhlídce.</div>`);
    if (res.some(r => !r.rentKnown)) msgs.push(`<div class="callout">U zdrojů označených „+ nájem?“ neznáme nájem. V pořadí jsou porovnány jen palivem a dalšími náklady. Doplňte nabídku v tabulce níže.</div>`);
    if (res.some(r => r.id === 'plyn')) msgs.push(`<div class="callout green">Mobilní kotelna na zemní plyn je možná jen tam, kde je plynová přípojka s dostatečnou kapacitou. Platbu za kapacitu doplňte do sloupce „Další“.</div>`);
    $('msgs').innerHTML = msgs.join('');

    // předání do poptávky
    const p = new URLSearchParams({ mwh: fmt(q, 1), mesicu: months, od: MONTHS[start], soustava: SOUSTAVY[soustava].label });
    $('to-form').href = `index.html?${p}#poptavka`;
  }

  document.querySelector('.calc').addEventListener('input', render);
  document.querySelector('.calc').addEventListener('change', (e) => {
    if (e.target.name === 'mode') document.querySelectorAll('[data-mode]').forEach(el => { el.hidden = el.dataset.mode !== mode(); });
    render();
  });
  $('reset').addEventListener('click', () => {
    PRICE_KEYS.forEach(p => { $('p-' + p.key).value = defaultPrice(p.key); });
    TECH.forEach(t => { $('r-' + t.id).value = t.rent ?? ''; $('o-' + t.id).value = t.once ?? ''; $('x-' + t.id).value = 0; $('inc-' + t.id).checked = true; });
    render();
  });
  render();
})();
