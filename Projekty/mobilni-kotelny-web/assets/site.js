/* Mobilní kotelny ThermaVera — menu, záložky formuláře, demo odeslání */
document.addEventListener('DOMContentLoaded', () => {
  const burger = document.querySelector('.burger');
  const menu = document.querySelector('.menu');
  if (burger) burger.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    burger.setAttribute('aria-expanded', open);
  });
  if (menu) menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => menu.classList.remove('open')));

  // Poptávka: záložky Havárie / Plánovaná odstávka
  const form = document.getElementById('poptavka-form');
  if (!form) return;
  const tabs = document.querySelectorAll('.tabs button');
  const setMode = (mode) => {
    tabs.forEach(b => b.classList.toggle('on', b.dataset.mode === mode));
    form.querySelectorAll('[data-only]').forEach(el => { el.hidden = el.dataset.only !== mode; });
    form.elements.typ.value = mode === 'havarie' ? 'Havárie' : 'Plánovaná odstávka';
  };
  tabs.forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
  document.querySelectorAll('[data-mode-link]').forEach(a => a.addEventListener('click', () => setMode(a.dataset.modeLink)));

  // Hodnoty předané z kalkulačky (?mwh=…&mesicu=…&soustava=…&od=…)
  const qs = new URLSearchParams(location.search);
  const fromCalc = qs.get('mwh');
  setMode(location.hash === '#havarie' ? 'havarie' : 'plan');
  if (fromCalc) {
    setMode('plan');
    const note = `Z kalkulačky: potřeba tepla ≈ ${qs.get('mwh')} MWh, ${qs.get('mesicu')} měs. od ${qs.get('od') || '?'}, soustava: ${qs.get('soustava') || '?'}.`;
    form.elements.zprava.value = note;
    document.getElementById('poptavka').scrollIntoView();
  }

  // Odeslání: s data-endpoint (web ThermaVera) přes odeslat.php, jinak jen poděkování (náhled)
  const done = () => { form.hidden = true; document.getElementById('okmsg').style.display = 'block'; };
  const err = document.getElementById('errmsg');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.reportValidity()) return;
    const endpoint = form.dataset.endpoint;
    if (!endpoint) return done();
    const f = form.elements;
    const pozn = [
      `Typ poptávky: ${f.typ.value}`,
      `Výkon / spotřeba: ${f.vykon.value || '—'}`,
      `Teplota otopné vody: ${f.teplota.value}`,
      f.typ.value === 'Havárie' ? '' : `Od kdy: ${f.od.value || '—'}, na jak dlouho: ${f.doba.value}`,
      `Elektrický přívod: ${f.jistic.value || '—'}`,
      '', f.zprava.value,
    ].filter(x => x !== '').join('\n');
    const data = new FormData();
    data.append('jmeno', f.jmeno.value);
    data.append('email', f.email.value);
    data.append('tel', f.telefon.value);
    data.append('typ', f.objekt.value);
    data.append('misto', f.misto.value);
    data.append('model', `Pronájem mobilní kotelny – ${f.typ.value}`);
    data.append('spotreba', f.vykon.value);
    data.append('souhlas', f.souhlas.checked ? 'ano' : '');
    data.append('website', f.website.value);
    data.append('pozn', pozn);
    data.append('lang', 'cs');
    try {
      const res = await fetch(endpoint, { method: 'POST', body: data, headers: { 'X-Requested-With': 'fetch' } });
      const json = await res.json().catch(() => ({}));
      if (res.ok && json.ok) return done();
      throw new Error(json.error || 'Odeslání se nepodařilo.');
    } catch (ex) {
      err.hidden = false;
      err.textContent = `${ex.message} Zavolejte prosím na +420 774 872 467 nebo napište na info@thermavera.cz.`;
    }
  });
});
