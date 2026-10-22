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

  // Demo: do napojení na odeslat.php jen poděkování
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    form.hidden = true;
    document.getElementById('okmsg').style.display = 'block';
  });
});
