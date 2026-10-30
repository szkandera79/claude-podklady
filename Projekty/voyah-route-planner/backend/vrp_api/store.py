"""SQLite úložiště (mimo iCloud): nastavení, spočítané plány, aktivní cesty, odečty SoC, kalibrace."""
from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(os.environ.get("VRP_DB", Path.home() / ".local" / "share" / "voyah-route-planner" / "app.sqlite"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, created REAL NOT NULL, request TEXT NOT NULL,
                                  route TEXT NOT NULL, stations TEXT NOT NULL, result TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS trips (id TEXT PRIMARY KEY, plan_id TEXT NOT NULL, variant TEXT NOT NULL,
                                  created REAL NOT NULL, finished REAL, state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id TEXT NOT NULL, ts REAL NOT NULL,
                                     route_km REAL NOT NULL, soc REAL NOT NULL, lat REAL, lon REAL, kind TEXT NOT NULL);
"""


class Store:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path or DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        return c

    # --- klíč/hodnota (nastavení, kalibrace)
    def get(self, key: str, default: Any = None) -> Any:
        with self._conn() as c:
            r = c.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

    def put(self, key: str, value: Any) -> None:
        with self._conn() as c:
            c.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (key, json.dumps(value), time.time()))

    # --- plány
    def save_plan(self, request: Dict, route: Dict, stations: List, result: Dict) -> str:
        pid = uuid.uuid4().hex[:12]
        with self._conn() as c:
            c.execute("INSERT INTO plans VALUES (?,?,?,?,?,?)", (pid, time.time(), json.dumps(request),
                      json.dumps(route), json.dumps(stations), json.dumps(result)))
            c.execute("DELETE FROM plans WHERE created < ? AND id NOT IN (SELECT plan_id FROM trips)",
                      (time.time() - 30 * 86400,))
        return pid

    def load_plan(self, pid: str) -> Optional[Dict]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM plans WHERE id=?", (pid,)).fetchone()
        if not r:
            return None
        out = {k: json.loads(r[k]) for k in ("request", "route", "stations", "result")}
        out["id"] = pid
        return out

    # --- cesty
    def create_trip(self, plan_id: str, variant: str, state: Dict) -> str:
        tid = uuid.uuid4().hex[:12]
        with self._conn() as c:
            c.execute("INSERT INTO trips VALUES (?,?,?,?,?,?)", (tid, plan_id, variant, time.time(), None,
                                                                json.dumps(state)))
        return tid

    def load_trip(self, tid: str) -> Optional[Dict]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM trips WHERE id=?", (tid,)).fetchone()
        if not r:
            return None
        return {"id": r["id"], "plan_id": r["plan_id"], "variant": r["variant"], "created": r["created"],
                "finished": r["finished"], "state": json.loads(r["state"])}

    def update_trip(self, tid: str, state: Dict, finished: bool = False) -> None:
        with self._conn() as c:
            c.execute("UPDATE trips SET state=?, finished=COALESCE(finished, ?) WHERE id=?",
                      (json.dumps(state), time.time() if finished else None, tid))

    def add_reading(self, tid: str, route_km: float, soc: float, lat: Optional[float], lon: Optional[float],
                    kind: str) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO readings (trip_id, ts, route_km, soc, lat, lon, kind) VALUES (?,?,?,?,?,?,?)",
                      (tid, time.time(), route_km, soc, lat, lon, kind))

    def readings(self, tid: str) -> List[Dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM readings WHERE trip_id=? ORDER BY id", (tid,))]

    def trips(self, limit: int = 50) -> List[Dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT t.id, t.variant, t.created, t.finished, p.request FROM trips t JOIN plans p ON p.id=t.plan_id "
                "ORDER BY t.created DESC LIMIT ?", (limit,))]
