"""Sjednocení názvů provozovatelů z různých zdrojů na názvy tarifů v nastavení."""
from __future__ import annotations

import unicodedata

# (hledaný řetězec bez diakritiky a malými písmeny, jednotný název)
ALIASES = [
    ("prazska energetika", "PRE"), ("pre ", "PRE"), ("pre(", "PRE"), ("pre-", "PRE"),
    ("e.on", "E.ON"), ("eon", "E.ON"),
    ("cez", "ČEZ"),
    ("lidl", "Lidl"), ("kaufland", "Kaufland"),
    ("tesla", "Tesla"),
    ("ionity", "IONITY"),
    ("mol", "MOL"), ("shell", "Shell"), ("omv", "OMV"), ("orlen", "Orlen"),
    ("innogy", "innogy"), ("teplarny brno", "Teplárny Brno"), ("chargee", "Chargee"),
]


def _plain(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return " " + s.lower().strip() + " "


def normalize_operator(name: str) -> str:
    if not name:
        return "Neznámý"
    p = _plain(name)
    if p.strip() in ("pre", "pre (cz)"):
        return "PRE"
    for key, out in ALIASES:
        if key in p:
            return out
    return name.strip()
