"""Registr nabídek mobilní kotelny pro konkrétní zákazníky (záložka „Nabídky“ v artefaktu Mobilní kotelna).

Každá nabídka má vlastní složku nabidky/<slug>/ (README, podklady z obhlídky, výpočty). Novou nabídku
přidej sem a do složky; obsah nabídky se vkládá z nabidky/<slug>/nabidka.html, pokud existuje.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / 'nabidky'

NABIDKY = [
    dict(slug='mm-holz', zakaznik='MM Holz', stav='připravuje se', datum='',
         popis='Nabídka mobilní kotelny. Čeká na podklady z obhlídky (kontrolní seznam v kap. 11 studie).'),
]


def html():
    cards = ''
    for n in NABIDKY:
        f = ROOT / n['slug'] / 'nabidka.html'
        body = f.read_text(encoding='utf-8') if f.exists() else f'<p class="note">{n["popis"]}</p>'
        cards += f'''<article class="offer" id="nabidka-{n["slug"]}">
<header><h3>{n["zakaznik"]}</h3><span class="pill">{n["stav"]}</span>{f'<span class="meta">{n["datum"]}</span>' if n["datum"] else ''}</header>
{body}</article>'''
    return f'''<p>Nabídky pro konkrétní zákazníky. Každá vychází ze studie (sestavy, rozpočet, ekonomika) a z údajů z obhlídky daného objektu.</p>
<div class="offers">{cards}</div>'''
