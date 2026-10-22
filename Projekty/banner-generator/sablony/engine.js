/* =====================================================================
   Banner engine — vykreslí bannery z pole window.BANNERS.
   - ?id=R1        → jen jeden banner v plné velikosti (pro export do PNG)
   - bez parametru → galerie všech bannerů (náhled)
   Značení v textech:  [[zelené slovo]]  {{žluté slovo}}  **tučně**
   ===================================================================== */

const ICONS = {
  calc:    '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8"/><path d="M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14v4M8 18h.01M12 18h.01"/>',
  bars:    '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
  trend:   '<path d="M22 7 13.5 15.5 8.5 10.5 2 17"/><path d="M16 7h6v6"/>',
  check:   '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
  tick:    '<path d="M20 6 9 17l-5-5"/>',
  sun:     '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
  bolt:    '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
  plug:    '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>',
  cpu:     '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
  gauge:   '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
  leaf:    '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
  building:'<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4M10 10h4M10 14h4M10 18h4"/>',
  users:   '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  shield:  '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  wrench:  '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  home:    '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
  doc:     '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8M16 17H8M10 9H8"/>',
  key:     '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>',
  coins:   '<circle cx="8" cy="8" r="6"/><path d="M18.09 10.37A6 6 0 1 1 10.34 18"/><path d="M7 6h1v4"/><path d="m16.71 13.88.7.71-2.82 2.82"/>',
  unplug:  '<path d="m19 5 3-3"/><path d="m2 22 3-3"/><path d="M6.3 20.3a2.4 2.4 0 0 0 3.4 0L12 18l-6-6-2.3 2.3a2.4 2.4 0 0 0 0 3.4Z"/><path d="M7.5 13.5 10 11"/><path d="M10.5 16.5 13 14"/><path d="m12 6 6 6 2.3-2.3a2.4 2.4 0 0 0 0-3.4l-2.6-2.6a2.4 2.4 0 0 0-3.4 0Z"/>',
  clock:   '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  flame:   '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
  arrow:   '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
};

function icon(name, sw = 1.9) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ''}</svg>`;
}

/* [[zelená]] {{žlutá}} **tučně** | → zalomení řádku */
function md(s = '') {
  return String(s)
    .replace(/\[\[(.+?)\]\]/g, '<span class="hl">$1</span>')
    .replace(/\{\{(.+?)\}\}/g, '<span class="y">$1</span>')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/\|/g, '<br>');
}

const TV_MARK = '<svg viewBox="0 0 32 32" fill="none"><rect x="1" y="1" width="30" height="30" rx="9" fill="#2E6B33"/><path d="M9.8 10.6H21.6L14 23.4" fill="none" stroke="#FCC83C" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';

function logoHtml(brand, b = {}) {
  if (brand.logo === 'thermavera') {
    return `<div class="bn-logo-tv">${TV_MARK}<span><span class="b">Therma</span><span class="t">Vera</span> <span class="e">Energy</span></span></div>`;
  }
  // tmavý banner → světlá varianta loga (brand.logoDark), pokud ji značka má
  const src = (b.dark && brand.logoDark) ? brand.logoDark : brand.logo;
  return `<img class="bn-logo" src="${src}" alt="">`;
}

const BOTTOM_H = { band: 150, cta: 140, icons: 172, aud: 104, calc: 116 };

function bottomHtml(b) {
  const parts = b.bottom || [];
  let h = 0, html = '';
  for (const p of parts) {
    h += BOTTOM_H[p.type] || 0;
    if (p.type === 'band')  html += `<div class="bb-band">${icon(p.icon || 'trend', 2)}<div>${md(p.text)}</div></div>`;
    if (p.type === 'cta')   html += `<div class="bb-cta"><a>${md(p.text)}${icon(p.arrow || 'arrow', 2.4)}</a></div>`;
    if (p.type === 'aud')   html += `<div class="bb-aud">${icon(p.icon || 'users', 2)}<span>${md(p.text)}</span></div>`;
    if (p.type === 'calc')  html += `<div class="bb-calc"><span class="dot">${icon('calc', 2)}</span><span>${md(p.text)}</span></div>`;
    if (p.type === 'icons') html += `<div class="bb-icons">${p.items.map(i => `<div>${icon(i.i, 1.8)}<span>${md(i.t)}</span></div>`).join('')}</div>`;
  }
  return { h, html: html ? `<div class="bn-bottom">${html}</div>` : '' };
}

function bannerHtml(b, brand) {
  const bottom = bottomHtml(b);
  const vars = Object.entries(b.vars || {}).map(([k, v]) => `--${k}:${v}`).join(';');
  const cls = ['bn', b.dark ? 'is-dark' : '', b.photoFull ? 'photo-full' : ''].join(' ');
  let s = `<div class="${cls}" id="bn-${b.id}" style="--bottom-h:${bottom.h}px;--h:${b.h || 1080}px;${vars}">`;

  if (b.photo) s += `<div class="bn-photo" style="background-image:url('${b.photo}')"></div>`;
  if (b.dark) s += `<div class="bn-dark-edge"></div><div class="bn-dark-panel"></div>`;
  else if (!b.noVeil) s += `<div class="bn-veil"></div>`;
  if (b.product) s += `<div class="bn-ground"></div><img class="bn-product" src="${b.product}" alt="">`;
  if (b.pill) s += `<div class="bn-pill"><span class="chk">${icon(b.pill.icon || 'tick', 3)}</span><span>${md(b.pill.text)}</span></div>`;
  if (b.stat) s += `<div class="bn-stat"><div class="lbl">${md(b.stat.label)}</div><div class="num">${md(b.stat.num)}</div><div class="note">${md(b.stat.note || '')}</div></div>`;

  s += `<div class="bn-col">${logoHtml(brand, b)}`;
  if (b.h1) s += `<h1 class="bn-h1">${md(b.h1)}</h1>`;
  if (b.rule !== false) s += `<div class="bn-rule"></div>`;
  if (b.sub) s += `<p class="bn-sub">${md(b.sub)}</p>`;
  if (b.feats) s += `<ul class="bn-feats">${b.feats.map(f => `<li><span class="ic${f.y ? ' y' : ''}">${icon(f.i, 1.7)}</span><span>${md(f.t)}</span></li>`).join('')}</ul>`;
  if (b.ask) s += `<div class="bn-ask"><span class="dot">${icon(b.ask.icon || 'bars', 2.2)}</span><div><strong>${md(b.ask.q)}</strong><span>${md(b.ask.a)}</span></div></div>`;
  if (b.aud) s += `<div class="bn-aud">${b.aud.map(a => `<div>${icon(a.i, 1.6)}<span>${md(a.t)}</span></div>`).join('')}</div>`;
  if (b.cta) s += `<a class="bn-cta ${b.cta.style || ''}">${md(b.cta.text)}${icon(b.cta.arrow || 'arrow', 2.6)}</a>`;
  s += `</div>`;

  if (b.badge) s += `<div class="bn-badge">${icon(b.badge.icon || 'calc', 1.8)}<span>${md(b.badge.text)}</span></div>`;
  if (b.foot) s += `<div class="bn-foot" style="bottom:calc(${bottom.h}px + ${b.footBottom || 14}px)">${md(b.foot)}</div>`;
  s += bottom.html;
  if (b.css) s += `<style>${b.css.replace(/&/g, '#bn-' + b.id)}</style>`;
  s += `</div>`;
  return s;
}

function render() {
  const brand = window.BRAND, list = window.BANNERS;
  for (const [k, v] of Object.entries(brand.theme || {})) document.documentElement.style.setProperty('--' + k, v);
  const id = new URLSearchParams(location.search).get('id');
  if (id) {
    const b = list.find(x => x.id === id);
    document.body.innerHTML = b ? bannerHtml(b, brand) : `Banner ${id} nenalezen`;
    return;
  }
  document.body.className = 'gallery';
  const S = 0.42;
  document.body.innerHTML =
    `<div class="g-head"><h1>${brand.title}</h1><p>${list.length} bannerů · 1080×1080 · klikni na ID pro plnou velikost</p></div>` +
    `<div class="g-grid">` +
    list.map(b => `<div class="g-card"><div class="g-t"><span>${b.id} — ${b.name || ''}</span><a href="?id=${b.id}">plná velikost ↗</a></div>` +
      `<div class="g-frame" style="--s:${S};--fh:${b.h || 1080}px">${bannerHtml(b, brand)}</div></div>`).join('') +
    `</div>`;
}

window.BANNER_IDS = () => window.BANNERS.map(b => b.id);
document.addEventListener('DOMContentLoaded', render);
