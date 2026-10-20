#!/usr/bin/env python3
"""REO HEATING CRM – sestavení stránky artefaktu z kódu (src/) a dat (data/state.json).

    python3 build.py                     # src/index.html + data/state.json → dist/index.html (k publikaci)
    python3 build.py --extract SOUBOR    # stažená stránka artefaktu → data/state.json + src/index.html

Data (leady, kontakty, faktury) jsou osobní údaje → jen v data/ (iCloud), nikdy v gitu (.gitignore).
Artefakt si data ukládá sám (capability `artifact`) – před úpravou kódu vždy nejdřív stáhnout živou verzi
a spustit --extract, jinak by publikace přepsala novější data.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
TAG = '<script type="application/json" id="app-state">'


def split(html):
    i = html.index(TAG) + len(TAG)
    j = html.index('</script>', i)
    return html[:i], json.loads(html[i:j] or '{}'), html[j:]


if '--extract' in sys.argv:
    src = pathlib.Path(sys.argv[sys.argv.index('--extract') + 1])
    head, state, tail = split(src.read_text())
    (ROOT / 'data').mkdir(exist_ok=True)
    old = ROOT / 'data' / 'state.json'
    if old.exists():
        prev = json.loads(old.read_text())
        if (prev.get('rev') or 0) > (state.get('rev') or 0):
            sys.exit(f'Stažená verze má rev {state.get("rev")}, lokální data rev {prev.get("rev")} – nic nepřepisuji.')
        old.rename(old.with_suffix('.json.bak'))
    old.write_text(json.dumps(state, ensure_ascii=False, indent=1))
    (ROOT / 'src' / 'index.html').write_text(head + '{}' + tail)
    print(f'data rev {state.get("rev")} ({state.get("updatedAt")}) → data/state.json; kód → src/index.html')
else:
    head, _, tail = split((ROOT / 'src' / 'index.html').read_text())
    state = json.loads((ROOT / 'data' / 'state.json').read_text())
    safe = json.dumps(state, ensure_ascii=False).replace('</', '<\\/')
    (ROOT / 'dist').mkdir(exist_ok=True)
    out = ROOT / 'dist' / 'index.html'
    out.write_text(head + safe + tail)
    print(f'{out} – {out.stat().st_size / 1e3:.0f} kB, data rev {state.get("rev")}')
