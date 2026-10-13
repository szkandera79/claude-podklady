// Vykreslí datový list: 1 = Heating 35/45/55 °C (tabulka + křivky),
// 2 = vysokoteplotní provoz 60–75 °C (jen modely s `DHi`), poslední = energetický štítek (jen s `label`).
// ASSETS = { logo:'…', labels:{ 'label-RH030.png':'…' } } — cesty nebo data: URI.
const PAR = [['cap','Heating capacity (kW)',1],['inp','Input power (kW)',2],['cop','COP',2]];
const SERIES = [
  {w:35,m:'MAX',c:'#1F2A8A',mk:'diamond'}, {w:45,m:'MAX',c:'#D61FB7',mk:'square'},
  {w:55,m:'MAX',c:'#8C8C8C',mk:'triangle'},{w:35,m:'MIN',c:'#E8B400',mk:'cross'},
  {w:45,m:'MIN',c:'#3E86DB',mk:'star'},    {w:55,m:'MIN',c:'#2F9E44',mk:'circle'},
];
const SERIES_HI = [
  {w:60,m:'MAX',c:'#1F2A8A',mk:'diamond'}, {w:65,m:'MAX',c:'#D61FB7',mk:'square'},
  {w:70,m:'MAX',c:'#8C8C8C',mk:'triangle'},{w:75,m:'MAX',c:'#C0392B',mk:'plus'},
  {w:60,m:'MIN',c:'#E8B400',mk:'cross'},   {w:65,m:'MIN',c:'#3E86DB',mk:'star'},
  {w:70,m:'MIN',c:'#2F9E44',mk:'circle'},  {w:75,m:'MIN',c:'#7048B6',mk:'plus'},
];
const neg = a => String(a).replace('-','−');

function marker(mk,x,y,c,s){
  const f=`fill="${c}"`, st=`stroke="${c}" stroke-width="${s*.45}"`;
  switch(mk){
    case 'diamond': return `<path d="M${x} ${y-s}L${x+s} ${y}L${x} ${y+s}L${x-s} ${y}Z" ${f}/>`;
    case 'square':  return `<rect x="${x-s*.8}" y="${y-s*.8}" width="${s*1.6}" height="${s*1.6}" ${f}/>`;
    case 'triangle':return `<path d="M${x} ${y-s}L${x+s} ${y+s*.8}L${x-s} ${y+s*.8}Z" ${f}/>`;
    case 'cross':   return `<path d="M${x-s*.8} ${y-s*.8}L${x+s*.8} ${y+s*.8}M${x+s*.8} ${y-s*.8}L${x-s*.8} ${y+s*.8}" ${st}/>`;
    case 'plus':    return `<path d="M${x-s} ${y}H${x+s}M${x} ${y-s}V${y+s}" ${st}/>`;
    case 'star':    return `<path d="M${x-s} ${y}H${x+s}M${x} ${y-s}V${y+s}M${x-s*.7} ${y-s*.7}L${x+s*.7} ${y+s*.7}M${x+s*.7} ${y-s*.7}L${x-s*.7} ${y+s*.7}" ${st}/>`;
    default:        return `<circle cx="${x}" cy="${y}" r="${s*.8}" ${f}/>`;
  }
}

function header(M, logo, sub){
  return `<header><h1>${M.name} ${sub[0]}<small>${sub[1]}</small></h1><img src="${logo}" alt="REO HEATING"></header>`;
}

function legendHtml(series){
  return series.map(se =>
    `<span><svg viewBox="0 0 30 10"><line x1="1" x2="29" y1="5" y2="5" stroke="${se.c}" stroke-width="1.6"/>${marker(se.mk,15,5,se.c,3)}</svg>${se.w} °C ${se.m}</span>`).join('');
}

// Jedna topná strana: tabulka pro zadané teploty + křivky výkonu a COP.
function heatPage(M, ASSETS, opt){
  const amb = M.amb || AMB, temps = opt.temps;
  const ambRow = () => `<tr class="amb"><th class="lbl" colspan="3">Ambient temp. (°C)</th>${amb.map(a=>`<th>${neg(a)}</th>`).join('')}</tr>`;
  let rows = '';
  temps.forEach((w,wi) => {
    if (wi) rows += `<tr class="gap"><td colspan="${3+amb.length}"></td></tr>`;
    ['MAX','MIN'].forEach((m,mi) => PAR.forEach(([k,label,dec],pi) => {
      rows += `<tr class="${k==='cop'?'cop':''}${mi?' zebra':''}">`;
      if (mi===0 && pi===0) rows += `<td class="grp" rowspan="6">Water temp. outlet<b>${w} °C</b></td>`;
      if (pi===0) rows += `<td class="mode" rowspan="3">${m}</td>`;
      rows += `<td class="par">${label}</td>`
            + opt.data[w][m][k].map(v => v == null ? `<td class="na">–</td>` : `<td>${v.toFixed(dec)}</td>`).join('')
            + `</tr>`;
    }));
  });
  // pětimístná čísla (příkon ≥ 10 kW) potřebují menší písmo, jinak se dotýkají linek
  const wide = temps.some(w => ['MAX','MIN'].some(m => opt.data[w][m].inp.some(v => v != null && v >= 10)));
  return `
  <div class="page${temps.length > 3 ? ' dense' : ''}${wide ? ' wide' : ''}">
    ${header(M, ASSETS.logo, opt.head)}
    <table><colgroup><col class="c-grp"><col class="c-mode"><col class="c-par"></colgroup>
      <thead>${ambRow()}</thead><tbody>${rows}</tbody><tfoot>${ambRow()}</tfoot></table>
    <div class="charts">
      <figure><figcaption>Curve of Heating Capacity Performance</figcaption><svg data-k="cap"></svg></figure>
      <figure><figcaption>Curve of COP Performance</figcaption><svg data-k="cop"></svg></figure>
    </div>
    <div class="legend">${legendHtml(opt.series)}</div>
  </div>`;
}

function labelPage(M, ASSETS){
  return `
  <div class="page">
    ${header(M, ASSETS.logo, ['Energy label','EU energy label · Regulation (EU) 811/2013'])}
    <div class="label-wrap"><img src="${ASSETS.labels[M.label]}" alt="Energy label ${M.erp}"></div>
    <div class="label-note"><span>Model: <b>${M.erp}</b> · air-to-water heat pump, refrigerant R290</span>
      <span>Space heating class: <b>A+++</b> at 35 °C · <b>A++</b> at 55 °C</span></div>
  </div>`;
}

function renderSheet(root, key, ASSETS){
  const M = MODELS[key];
  const pages = [{ data:M.D, temps:[35,45,55], series:SERIES, yCap:M.yCap, yCop:M.yCop || [1,7,1],
                   head:['Heating','Heating performance data · air-to-water heat pump'] }];
  if (M.DHi) pages.push({ data:M.DHi, temps:[60,65,70,75], series:SERIES_HI, yCap:M.yCapHi, yCop:M.yCopHi,
                          head:['Heating 60–75 °C','High-temperature performance data · air-to-water heat pump'] });

  root.innerHTML = pages.map(p => heatPage(M, ASSETS, p)).join('')
                 + (M.label ? labelPage(M, ASSETS) : '');

  const svgs = root.querySelectorAll('svg[data-k]');
  pages.forEach((p,i) => {
    chart(svgs[2*i],   M, p, 'cap', ...p.yCap, 'Heating capacity (kW)');
    chart(svgs[2*i+1], M, p, 'cop', ...p.yCop, 'COP');
  });
}

// Rozměry z layoutu (clientWidth/offsetWidth), takže funguje i ve zmenšeném náhledu (transform).
function chart(svg, M, page, key, yMin, yMax, step, yLabel){
  const amb = M.amb || AMB;
  const W = svg.clientWidth, H = svg.clientHeight;
  const px = svg.closest('.page').offsetWidth/210;   // 1 jednotka = 1 mm
  const L=11*px, R=2*px, T=2*px, B=9.5*px, pw=W-L-R, ph=H-T-B;
  const X=i=>L+pw*(i/(amb.length-1)), Y=v=>T+ph*(1-(v-yMin)/(yMax-yMin));
  const fs=2.9*px, dec = step < 1 ? 1 : 0;
  let s=`<rect x="${L}" y="${T}" width="${pw}" height="${ph}" fill="#F3F5F4"/>`;
  for(let v=yMin; v<=yMax+1e-9; v+=step){
    s+=`<line x1="${L}" x2="${L+pw}" y1="${Y(v)}" y2="${Y(v)}" stroke="#C9D1CC" stroke-width="${.22*px}"/>`;
    s+=`<text x="${L-1.4*px}" y="${Y(v)+fs*.35}" text-anchor="end" font-size="${fs}" fill="#3A4540">${v.toFixed(dec)}</text>`;
  }
  amb.forEach((a,i)=>{
    s+=`<line x1="${X(i)}" x2="${X(i)}" y1="${T}" y2="${T+ph}" stroke="#DDE3DF" stroke-width="${.22*px}"/>`;
    s+=`<text x="${X(i)}" y="${T+ph+4*px}" text-anchor="middle" font-size="${fs}" fill="#3A4540">${neg(a)}</text>`;
  });
  s+=`<rect x="${L}" y="${T}" width="${pw}" height="${ph}" fill="none" stroke="#6F7C74" stroke-width="${.3*px}"/>`;
  page.series.forEach(se=>{
    const v=page.data[se.w][se.m][key];
    // chybějící body (mimo pracovní rozsah) čáru přeruší
    let seg=[];
    const flush=()=>{ if(seg.length>1) s+=`<polyline fill="none" stroke="${se.c}" stroke-width="${.5*px}" stroke-linejoin="round" points="${seg.join(' ')}"/>`; seg=[]; };
    v.forEach((y,i)=>{ if(y==null){ flush(); } else { seg.push(X(i)+','+Y(y)); } });
    flush();
    v.forEach((y,i)=>{ if(y!=null) s+=marker(se.mk,X(i),Y(y),se.c,.9*px); });
  });
  s+=`<text x="${L+pw/2}" y="${H-1.2*px}" text-anchor="middle" font-size="${fs*1.05}" font-weight="600" fill="#16201C">Ambient temp. (°C)</text>`;
  s+=`<text transform="translate(${3*px},${T+ph/2}) rotate(-90)" text-anchor="middle" font-size="${fs*1.05}" font-weight="600" fill="#16201C">${yLabel}</text>`;
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  svg.innerHTML=s;
}
