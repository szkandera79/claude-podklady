#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Složí stránku artefaktu „Zelená kotelna RHX30 Pro – vzor“ z nabidka.html + PDF (tlačítko ke stažení).

    python3 vzor-bytove-domy-rhx30/src/build_artefakt.py <cesta k PDF> <výstupní html>
PDF předem vytisknout headless Chromem z nabidka.html (viz README). Artefakt se publikuje
s capabilities {"downloads": true} na https://claude.ai/artifact/2Q1NABF2A6MQ3H8VeK3t4t.
"""
import base64
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
EXTRA_CSS = """.dl{display:flex;justify-content:flex-end;margin-bottom:14px}
.dl[hidden]{display:none!important}
.dl .btn:focus-visible{outline:3px solid var(--accent-bg);outline-offset:2px}
.dl .msg{font-size:12.5px;color:var(--muted);align-self:center;margin-right:12px}
@media screen and (max-width:760px){.wrap{padding:16px 16px 40px}.doc{overflow-x:auto}}
</style>"""
SCRIPT = """<script>
const PDF_B64="%s";
(async()=>{
  const dl=await window.claude?.use?.("downloads");
  if(!dl)return;
  const box=document.getElementById("dl"),btn=document.getElementById("dlbtn"),msg=document.getElementById("dlmsg");
  box.hidden=false;
  btn.addEventListener("click",async()=>{
    msg.textContent="";
    try{
      const bin=atob(PDF_B64),u=new Uint8Array(bin.length);
      for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
      await dl.save({filename:"ThermaVera-zelena-kotelna-RHX30-Pro.pdf",data:new Blob([u],{type:"application/pdf"})});
    }catch(e){if(e&&e.code!=="declined")msg.textContent="Stažení se nepodařilo dokončit, zkuste to prosím znovu.";}
  });
})();
</script>
"""


def main(pdf, out):
    with open(os.path.join(ROOT, "nabidka.html"), encoding="utf-8") as f:
        h = f.read()
    style = h[h.index("<style>"):h.index("</style>") + 8].replace("</style>", EXTRA_CSS)
    body = h[h.index('<div class="doc">'):h.index("</body>")].replace("</div><!-- /wrap -->", "")
    with open(pdf, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    page = (f"<title>Zelená kotelna RHX30 Pro – vzor</title>\n{style}\n<div class=\"wrap\">\n"
            '<div class="dl" id="dl" hidden><span class="msg" id="dlmsg"></span>'
            '<button class="btn primary" id="dlbtn" type="button">Stáhnout nabídku v PDF</button></div>\n'
            f"{body}\n</div>\n" + SCRIPT % b64)
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("zapsáno:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
