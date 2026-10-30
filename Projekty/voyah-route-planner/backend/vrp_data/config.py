"""Konfigurace a tajné klíče. Klíče se čtou z proměnných prostředí nebo z ~/.config/voyah-route-planner/.env
(mimo iCloud a git). Nikdy se nevypisují do logu."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional

ENV_FILE = Path(os.environ.get("VRP_ENV_FILE", Path.home() / ".config" / "voyah-route-planner" / ".env"))
CACHE_DIR = Path(os.environ.get("VRP_CACHE_DIR", Path.home() / ".cache" / "voyah-route-planner"))
USER_AGENT = "VoyahRoutePlanner/0.1 (osobni nekomercni projekt)"

_loaded: Optional[Dict[str, str]] = None


def _load_file() -> Dict[str, str]:
    out: Dict[str, str] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def secret(name: str) -> Optional[str]:
    global _loaded
    if name in os.environ and os.environ[name]:
        return os.environ[name]
    if _loaded is None:
        _loaded = _load_file()
    v = _loaded.get(name) or None
    return None if v in (None, "", "sem-vlozte-klic") else v
