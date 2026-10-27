#!/usr/bin/env python3
"""Článek (Markdown) → tisková HTML stránka A4 se schématy a logem REO HEATING → PDF.

Spuštění z kořene repozitáře:
    python3 REO/clanky/build_pdf.py REO/clanky/akumulacni-nadoba-k-tepelnemu-cerpadlu.md
Výstup: <název>.html a <název>.pdf vedle Markdownu (PDF přes Chrome headless).
Převod Markdownu pokrývá jen to, co články používají: nadpisy, odstavce, seznamy,
zaškrtávací seznam, citace, tabulky, obrázky SVG, tučné/kurzíva, vodorovná čára.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

LOGO = Path.home() / "Claude/REO/logo/logo-reo-heating.svg"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def svg_inline(path, alt):
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r'\swidth="\d+" height="\d+"', "", svg, count=1)
    return f'<figure class="schema" aria-label="{html.escape(alt)}">{svg}</figure>'


def convert(md, base):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S).strip()
    lines = md.split("\n")
    out, i = [], 0
    title, lead = None, None
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("# "):
            title = inline(ln[2:])
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:])}</h2>")
        elif ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>")
        elif ln.strip() == "---":
            out.append("<hr>")
        elif m := re.match(r"!\[(.*?)\]\((.*?)\)", ln):
            out.append(svg_inline(base / m.group(2), m.group(1)))
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            t = "<div class=\"tbl\"><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(t + "</tbody></table></div>")
            continue
        elif ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            out.append(f"<aside class=\"tip\">{inline(' '.join(buf))}</aside>")
            continue
        elif re.match(r"\s*(- |\d+\. )", ln):
            ordered = bool(re.match(r"\d+\. ", ln))
            check = ln.startswith("- [ ]")
            items = []
            while i < len(lines) and (re.match(r"\s*(- |\d+\. )", lines[i]) or lines[i].startswith("  ")):
                cur = lines[i]
                if re.match(r"(- |\d+\. )", cur):
                    items.append([re.sub(r"^(- \[ \] |- |\d+\. )", "", cur), []])
                elif re.match(r"\s+- ", cur):
                    items[-1][1].append(cur.strip()[2:])
                else:
                    if items[-1][1]:
                        items[-1][1][-1] += " " + cur.strip()
                    else:
                        items[-1][0] += " " + cur.strip()
                i += 1
            tag = "ol" if ordered else "ul"
            cls = ' class="check"' if check else ""
            lis = []
            for text, sub in items:
                s = inline(text)
                if sub:
                    s += "<ul>" + "".join(f"<li>{inline(x)}</li>" for x in sub) + "</ul>"
                lis.append(f"<li>{s}</li>")
            out.append(f"<{tag}{cls}>{''.join(lis)}</{tag}>")
            continue
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r"(#|>|\||- |\d+\. |!\[|---)", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            p = " ".join(buf)
            if lead is None and title and not out:
                lead = inline(p.strip("*"))
            else:
                out.append(f"<p>{inline(p)}</p>")
            continue
        i += 1
    return title, lead, "\n".join(out)


CSS = """
:root{--brand:#26804B;--brand-dark:#1A5433;--tint:#E9F6EE;--fg:#16241C;--muted:#5C6B62;--line:#DCE5DF;
--sans:"Figtree","Segoe UI",system-ui,sans-serif}
@page{size:A4;margin:16mm 17mm 18mm}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:#fff;color:var(--fg);font:10.5pt/1.55 var(--sans)}
.doc{max-width:176mm;margin:0 auto}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid var(--brand);padding-bottom:4mm;margin-bottom:7mm}
.top svg{height:15mm;width:auto}
.top .kind{font-size:8.5pt;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:600;text-align:right}
h1{font-size:23pt;line-height:1.15;margin:0 0 4mm;color:var(--brand-dark);text-wrap:balance;letter-spacing:-.01em}
.lead{font-size:12pt;color:var(--muted);margin:0 0 6mm;max-width:66ch}
h2{font-size:14.5pt;color:var(--brand-dark);margin:8mm 0 2.5mm;break-after:avoid;text-wrap:balance}
h3{font-size:11.5pt;margin:5mm 0 1.5mm;break-after:avoid}
p{margin:0 0 2.5mm}
ul,ol{margin:0 0 3mm;padding-left:6mm}
li{margin:.8mm 0}
strong{color:var(--fg)}
hr{border:0;border-top:1px solid var(--line);margin:6mm 0}
.tip{background:var(--tint);border-radius:2mm;padding:3mm 4mm;margin:3mm 0 4mm;font-size:10pt}
figure.schema{margin:3mm 0 5mm;break-inside:avoid;border:1px solid var(--line);border-radius:2mm;padding:2mm;background:#fff}
figure.schema svg{display:block;width:100%;height:auto}
figcaption{font-size:8.5pt;color:var(--muted);padding:1mm 2mm 0}
.tbl{overflow-x:auto;margin:2mm 0 5mm;break-inside:avoid}
table{border-collapse:collapse;width:100%;font-size:9.5pt}
th{background:var(--brand-dark);color:#fff;text-align:left;font-weight:600;padding:2mm 2.5mm}
td{border-bottom:1px solid var(--line);padding:2mm 2.5mm;vertical-align:top}
tr:nth-child(even) td{background:#F6FAF7}
ul.check{list-style:none;padding-left:0}
ul.check li{padding-left:7mm;position:relative}
ul.check li::before{content:"";position:absolute;left:0;top:1.2mm;width:3.6mm;height:3.6mm;border:1.5px solid var(--brand);border-radius:.8mm}
.cta{margin-top:6mm;background:var(--brand-dark);color:#fff;border-radius:2mm;padding:5mm 6mm;break-inside:avoid}
.cta p{margin:0 0 2mm}.cta strong{color:#fff}
.cta .contact{font-weight:600;letter-spacing:.01em}
.foot{margin-top:4mm;font-size:8.5pt;color:var(--muted)}
"""


def build(md_path):
    md_path = Path(md_path).resolve()
    title, lead, body = convert(md_path.read_text(encoding="utf-8"), md_path.parent)
    # závěrečná výzva + kontakt do zeleného boxu, poznámka pod něj
    m = re.search(r"<hr>\s*(<p><strong>Nevíte.*?</p>)\s*(<p>.*?</p>)\s*(<p><em>.*?</em></p>)\s*$", body, flags=re.S)
    if m:
        contact = re.sub(r"[📞✉️]\s*", "", m.group(2)).replace('<p>', '<p class="contact">')
        body = body[:m.start()] + f'<div class="cta">{m.group(1)}{contact}</div><p class="foot">{m.group(3)[3:-4]}</p>'
    logo = LOGO.read_text(encoding="utf-8")
    page = f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{re.sub('<.*?>', '', title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,400;0,600;0,700;1,400&display=swap">
<style>{CSS}</style></head><body><div class="doc">
<div class="top">{logo}<div class="kind">Poradna<br>REO HEATING</div></div>
<h1>{title}</h1>
<p class="lead">{lead}</p>
{body}
</div></body></html>"""
    out_html = md_path.with_suffix(".html")
    out_pdf = md_path.with_suffix(".pdf")
    out_html.write_text(page, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", "--virtual-time-budget=8000",
                    out_html.as_uri()], check=True, capture_output=True)
    print("✓", out_html.name, "→", out_pdf.name)


if __name__ == "__main__":
    build(sys.argv[1])
