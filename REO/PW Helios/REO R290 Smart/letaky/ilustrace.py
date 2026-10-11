"""Ilustrace pro leták (jednoduchý plochý obrázek, ne schéma): slunce → panely na zahradě → kabel přímo
do tepelného čerpadla u domu → teplo do domu. Minimum popisků, aby to pochopil laik.
SVG viewBox 760×340; vkládá se inline do HTML (build.py: from ilustrace import SVG)."""

SVG = """<svg class="ilu" viewBox="0 6 760 334" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE3F5"/><stop offset="1" stop-color="#EAF6FB"/></linearGradient>
    <linearGradient id="lawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9ED27F"/><stop offset="1" stop-color="#78BC5E"/></linearGradient>
    <linearGradient id="pv" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3D6FB0"/><stop offset=".55" stop-color="#1E3F73"/><stop offset="1" stop-color="#16305A"/></linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="#FFE38A" stop-opacity=".9"/><stop offset="1" stop-color="#FFE38A" stop-opacity="0"/></radialGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE38A" stop-opacity=".55"/><stop offset="1" stop-color="#FFE38A" stop-opacity="0"/></linearGradient>
    <linearGradient id="hp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B4047"/><stop offset="1" stop-color="#23272C"/></linearGradient>
    <clipPath id="frame"><rect x="0" y="0" width="760" height="340" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
  <rect width="760" height="340" fill="url(#sky)"/>

  <!-- mraky -->
  <g fill="#fff" opacity=".9">
    <ellipse cx="300" cy="46" rx="44" ry="14"/><ellipse cx="326" cy="38" rx="26" ry="14"/>
    <ellipse cx="470" cy="62" rx="36" ry="11"/><ellipse cx="488" cy="55" rx="20" ry="11"/>
  </g>

  <!-- kopce a trávník -->
  <path d="M0 214 C 120 176, 230 196, 330 206 S 560 168, 760 196 V340 H0z" fill="#B9DFA0"/>
  <path d="M0 236 C 160 214, 330 230, 470 224 S 680 214, 760 222 V340 H0z" fill="url(#lawn)"/>

  <!-- slunce + paprsky na panely -->
  <circle cx="92" cy="62" r="70" fill="url(#glow)"/>
  <polygon points="80,82 30,246 236,236 112,78" fill="url(#beam)"/>
  <circle cx="92" cy="62" r="30" fill="#FFC93C"/>
  <g stroke="#FFC93C" stroke-width="5" stroke-linecap="round">
    <line x1="92" y1="14" x2="92" y2="22"/><line x1="140" y1="62" x2="132" y2="62"/><line x1="44" y1="62" x2="52" y2="62"/>
    <line x1="126" y1="28" x2="120" y2="34"/><line x1="58" y1="28" x2="64" y2="34"/><line x1="126" y1="96" x2="120" y2="90"/>
  </g>

  <!-- strom -->
  <g><rect x="722" y="168" width="7" height="32" fill="#7A5A3A"/><circle cx="725" cy="160" r="22" fill="#4E9A45"/><circle cx="712" cy="170" r="14" fill="#5BAA50"/></g>

  <!-- dům -->
  <g>
    <polygon points="452,170 524,152 524,268 452,262" fill="#E8DCC8"/>
    <polygon points="440,174 524,154 626,80 556,66" fill="#5B6670"/>
    <polygon points="524,152 626,80 728,152 728,268 524,268" fill="#F7F1E6"/>
    <polyline points="514,158 626,74 738,158" fill="none" stroke="#3E4851" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"/>
    <rect x="548" y="176" width="44" height="40" rx="3" fill="#FFE7A3" stroke="#8C7B63" stroke-width="3"/>
    <line x1="570" y1="176" x2="570" y2="216" stroke="#8C7B63" stroke-width="2"/>
    <rect x="660" y="176" width="44" height="40" rx="3" fill="#FFE7A3" stroke="#8C7B63" stroke-width="3"/>
    <line x1="682" y1="176" x2="682" y2="216" stroke="#8C7B63" stroke-width="2"/>
    <rect x="608" y="208" width="34" height="60" rx="3" fill="#8C6A4A"/>
    <circle cx="634" cy="240" r="2.5" fill="#E8C66A"/>
    <rect x="606" y="112" width="40" height="26" rx="3" fill="#FFE7A3" stroke="#8C7B63" stroke-width="3"/>
    <g fill="none" stroke="#E2553A" stroke-width="3" stroke-linecap="round" opacity=".85">
      <path d="M556 210 c 4 -6 -4 -10 0 -16"/><path d="M568 210 c 4 -6 -4 -10 0 -16"/><path d="M580 210 c 4 -6 -4 -10 0 -16"/>
      <path d="M668 210 c 4 -6 -4 -10 0 -16"/><path d="M680 210 c 4 -6 -4 -10 0 -16"/><path d="M692 210 c 4 -6 -4 -10 0 -16"/>
    </g>
  </g>

  <!-- potrubí do domu -->
  <path d="M432 236 H460" stroke="#2A2E33" stroke-width="7" stroke-linecap="round"/>
  <path d="M432 248 H460" stroke="#2A2E33" stroke-width="7" stroke-linecap="round"/>

  <!-- tepelné čerpadlo -->
  <g>
    <rect x="316" y="264" width="130" height="10" rx="3" fill="#C9CCC9"/>
    <rect x="322" y="190" width="116" height="74" rx="7" fill="url(#hp)"/>
    <rect x="322" y="190" width="116" height="7" rx="3.5" fill="#4A5058"/>
    <circle cx="361" cy="230" r="26" fill="#1B1E22" stroke="#555C64" stroke-width="2"/>
    <g fill="#3F78C8"><ellipse cx="361" cy="216" rx="6" ry="13"/><ellipse cx="361" cy="216" rx="6" ry="13" transform="rotate(120 361 230)"/><ellipse cx="361" cy="216" rx="6" ry="13" transform="rotate(240 361 230)"/></g>
    <circle cx="361" cy="230" r="4" fill="#AEB6BE"/>
    <g stroke="#4A5058" stroke-width="2"><line x1="398" y1="208" x2="428" y2="208"/><line x1="398" y1="218" x2="428" y2="218"/><line x1="398" y1="228" x2="428" y2="228"/><line x1="398" y1="238" x2="428" y2="238"/><line x1="398" y1="248" x2="428" y2="248"/></g>
  </g>

  <!-- panely na zahradě -->
  <g>
    <g stroke="#8D969E" stroke-width="5" stroke-linecap="round">
      <line x1="58" y1="286" x2="58" y2="304"/><line x1="196" y1="286" x2="196" y2="304"/>
      <line x1="214" y1="262" x2="214" y2="280"/><line x1="300" y1="262" x2="300" y2="280"/>
    </g>
    <polygon points="34,290 222,290 236,226 66,226" fill="url(#pv)" stroke="#D5DCE3" stroke-width="3"/>
    <g stroke="#7FA2D2" stroke-width="1.4" opacity=".8">
      <line x1="50" y1="258" x2="229" y2="258"/>
      <line x1="100" y1="226" x2="94" y2="290"/><line x1="134" y1="226" x2="130" y2="290"/><line x1="168" y1="226" x2="166" y2="290"/><line x1="202" y1="226" x2="202" y2="290"/>
    </g>
    <polygon points="206,266 306,266 314,222 222,222" fill="url(#pv)" stroke="#D5DCE3" stroke-width="3"/>
    <g stroke="#7FA2D2" stroke-width="1.4" opacity=".8">
      <line x1="214" y1="244" x2="310" y2="244"/><line x1="246" y1="222" x2="240" y2="266"/><line x1="272" y1="222" x2="268" y2="266"/>
    </g>
    <polygon points="72,232 122,232 114,250 66,250" fill="#fff" opacity=".18"/>
  </g>

  <!-- kabel z panelů přímo do čerpadla -->
  <path d="M200 296 C 252 306, 300 304, 340 276" fill="none" stroke="#1F2328" stroke-width="5" stroke-linecap="round"/>
  <path d="M200 296 C 252 306, 300 304, 340 276" fill="none" stroke="#FFC93C" stroke-width="3" stroke-dasharray="8 7" stroke-linecap="round"/>

  <!-- popisky -->
  <g font-weight="800" font-size="13">
    <g transform="translate(150 206)"><rect x="-62" y="-15" width="124" height="24" rx="12" fill="#fff"/><text y="2" text-anchor="middle" fill="#16305A">Solární panely</text></g>
    <g transform="translate(380 172)"><rect x="-66" y="-15" width="132" height="24" rx="12" fill="#fff"/><text y="2" text-anchor="middle" fill="#23272C">Tepelné čerpadlo</text></g>
    <g transform="translate(626 296)"><rect x="-60" y="-15" width="120" height="24" rx="12" fill="#fff"/><text y="2" text-anchor="middle" fill="#C2412A">Teplo do domu</text></g>
    <g transform="translate(270 324)"><rect x="-132" y="-15" width="264" height="25" rx="12.5" fill="#FFC93C"/><text y="2.5" text-anchor="middle" fill="#123D25" font-size="12.5">Přímo do čerpadla – bez střídače a baterie</text></g>
  </g>
  </g>
</svg>"""
