"""Minimalistický HTTP klient (jen standardní knihovna) s diskovou cache.

Cache: JSON soubor podle SHA-1 požadavku, platnost dle `ttl_s`. Klíče API se do klíče cache nezapočítávají
a do souborů se neukládají.
"""
from __future__ import annotations

import hashlib
import json
import ssl
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from .config import CACHE_DIR, USER_AGENT


class SourceError(RuntimeError):
    """Externí zdroj nedostupný nebo vrátil chybu — volající rozhodne o záloze."""


def _cache_path(kind: str, key: str):
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / kind / f"{h}.json"


def request_json(url: str, *, params: Optional[Dict[str, Any]] = None, body: Any = None,
                 headers: Optional[Dict[str, str]] = None, timeout: float = 30.0,
                 cache_kind: Optional[str] = None, ttl_s: float = 0, form: bool = False) -> Any:
    full = url + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    cache_key = full + "|" + (json.dumps(body, sort_keys=True) if body is not None else "")
    path = _cache_path(cache_kind, cache_key) if cache_kind and ttl_s > 0 else None
    if path is not None and path.exists() and time.time() - path.stat().st_mtime < ttl_s:
        return json.loads(path.read_text(encoding="utf-8"))

    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    hdrs.update(headers or {})
    data = None
    if body is not None:
        if form:
            data = urllib.parse.urlencode(body).encode("utf-8")
            hdrs["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(body).encode("utf-8")
            hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(full, data=data, headers=hdrs, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SourceError(f"{urllib.parse.urlsplit(url).netloc}: HTTP {e.code}") from None
    except urllib.error.URLError as e:
        if isinstance(e.reason, ssl.SSLError):
            payload = _curl(full, data, hdrs, timeout)     # staré TLS v systémovém Pythonu macOS
        else:
            raise SourceError(f"{urllib.parse.urlsplit(url).netloc}: {type(e.reason).__name__}") from None
    except (TimeoutError, OSError) as e:
        raise SourceError(f"{urllib.parse.urlsplit(url).netloc}: {type(e).__name__}") from None
    except json.JSONDecodeError:
        raise SourceError(f"{urllib.parse.urlsplit(url).netloc}: neplatná odpověď") from None

    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def _curl(url: str, data: Optional[bytes], hdrs: Dict[str, str], timeout: float) -> Any:
    cmd = ["curl", "-sS", "--fail", "--max-time", str(int(timeout)), url]
    for k, v in hdrs.items():
        cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["--data-binary", "@-"]
    try:
        out = subprocess.run(cmd, input=data, capture_output=True, timeout=timeout + 5, check=True).stdout
        return json.loads(out.decode("utf-8"))
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        raise SourceError(f"{urllib.parse.urlsplit(url).netloc}: nedostupné") from None
