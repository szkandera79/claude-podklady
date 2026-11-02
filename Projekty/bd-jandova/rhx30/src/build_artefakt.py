#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stránka artefaktu: tři dokumenty (nabídka, předseda, schůze) v záložkách, bez interních poznámek.

    python3 bd-jandova/rhx30/src/build_artefakt.py <výstupní html>
"""
import os
import re
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(SRC, ".."))
TABS = [("nabidka", "Cenová nabídka", "nabidka.html", "BD-Jandova-nabidka-RHX30-Pro-rev1.pdf"),
        ("predseda", "Pro předsedu", "podklady-predseda.html", "BD-Jandova-podklady-predseda.pdf"),
        ("schuze", "Na schůzi vlastníků", "podklady-schuze.html", "BD-Jandova-podklady-schuze.pdf")]
# PDF se publikují jako soubory artefaktu pod pdf/<název> (files map) a stahují přes capability downloads.


def doc(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        h = f.read()
    css = h[h.index("<style>") + 7:h.index("</style>")]
    body = h[h.index('<div class="doc">'):h.index("</div><!-- /wrap -->")]
    return css, body


def main(out):
    css, _ = doc("nabidka.html")
    css += """
body{background:var(--bg)}
.wrap{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.tab{font:600 14px var(--sans);border:1px solid var(--line);background:#fff;color:var(--ink);padding:10px 16px;border-radius:999px;cursor:pointer}
.tab[aria-selected="true"]{background:var(--accent-2);border-color:var(--accent-2);color:#fff}
.tab:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.note{font-size:12.5px;color:var(--muted);margin:0 0 14px}
.dl{display:flex;justify-content:flex-end;align-items:center;gap:12px;margin-bottom:12px}
.dl .msg{font-size:12.5px;color:var(--muted)}
.dl .btn:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media screen and (max-width:760px){.doc{overflow-x:auto}table{font-size:12.5px}th,td{padding:7px 8px}}
"""
    parts = []
    for i, (tid, label, path, pdf) in enumerate(TABS):
        _, body = doc(path)
        dl = (f'<div class="dl" hidden><span class="msg"></span>'
              f'<button class="btn primary dlbtn" type="button" data-pdf="{pdf}">Stáhnout PDF k tisku</button></div>')
        parts.append(f'<section id="{tid}" role="tabpanel"{"" if i == 0 else " hidden"}>{dl}{body}</section>')
    btns = "".join(f'<button class="tab" role="tab" type="button" data-t="{t}" aria-selected="{str(i == 0).lower()}">{l}</button>'
                   for i, (t, l, _, _p) in enumerate(TABS))
    page = (f'<title>Kotelna BD Jandova 7</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f"<style>{css}</style>\n<div class=\"wrap\">\n<div class=\"tabs\" role=\"tablist\">{btns}</div>\n"
            '<p class="note">Nabídka č. 2026-11-BDJ-02 · ThermaVera Energy · částky bez DPH, orientační.</p>\n'
            + "\n".join(parts) + "\n</div>\n"
            """<script>
const tabs=[...document.querySelectorAll('.tab')];
function show(t){tabs.forEach(b=>b.setAttribute('aria-selected',b.dataset.t===t));
  document.querySelectorAll('section[role=tabpanel]').forEach(s=>s.hidden=s.id!==t);}
tabs.forEach(b=>b.addEventListener('click',()=>{show(b.dataset.t);scrollTo(0,0);}));
const h=location.hash.slice(1);if(tabs.some(b=>b.dataset.t===h))show(h);
(async()=>{
  const dl=await window.claude?.use?.("downloads");
  if(!dl)return;
  document.querySelectorAll('.dl').forEach(box=>{
    box.hidden=false;
    const btn=box.querySelector('.dlbtn'),msg=box.querySelector('.msg');
    btn.addEventListener('click',async()=>{
      msg.textContent='';btn.disabled=true;
      try{
        const r=await fetch('pdf/'+btn.dataset.pdf);
        if(!r.ok)throw new Error('fetch');
        await dl.save({filename:btn.dataset.pdf,data:await r.blob()});
      }catch(e){if(!e||e.code!=='declined')msg.textContent='Stažení se nepodařilo, zkuste to prosím znovu.';}
      finally{btn.disabled=false;}
    });
  });
})();
</script>
""")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("zapsáno:", out)


if __name__ == "__main__":
    main(sys.argv[1])
