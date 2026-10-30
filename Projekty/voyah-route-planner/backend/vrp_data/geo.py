"""Geometrie: vzdálenosti, kurz, kódování polyline, průmět bodu na trasu."""
from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from typing import List, Sequence, Tuple

R_KM = 6371.0088
LatLon = Tuple[float, float]


def haversine_km(a: LatLon, b: LatLon) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_KM * math.asin(math.sqrt(h))


def bearing_deg(a: LatLon, b: LatLon) -> float:
    la1, la2 = math.radians(a[0]), math.radians(b[0])
    dlo = math.radians(b[1] - a[1])
    x = math.sin(dlo) * math.cos(la2)
    y = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dlo)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def encode_polyline(points: Sequence[LatLon], precision: int = 5) -> str:
    """Google Encoded Polyline (pořadí lat, lon)."""
    f = 10 ** precision
    out, plat, plon = [], 0, 0
    for lat, lon in points:
        ilat, ilon = int(round(lat * f)), int(round(lon * f))
        for d in (ilat - plat, ilon - plon):
            v = ~(d << 1) if d < 0 else d << 1
            while v >= 0x20:
                out.append(chr((0x20 | (v & 0x1F)) + 63))
                v >>= 5
            out.append(chr(v + 63))
        plat, plon = ilat, ilon
    return "".join(out)


def simplify_by_distance(points: Sequence[LatLon], step_km: float) -> List[LatLon]:
    """Ponechá body zhruba po `step_km` (vždy první a poslední)."""
    if not points:
        return []
    out = [points[0]]
    acc = 0.0
    for p, q in zip(points, points[1:]):
        acc += haversine_km(p, q)
        if acc >= step_km:
            out.append(q)
            acc = 0.0
    if out[-1] != points[-1]:
        out.append(points[-1])
    return out


@dataclass
class Polyline:
    points: List[LatLon]
    cum_km: List[float]

    @classmethod
    def from_points(cls, points: Sequence[LatLon]) -> "Polyline":
        cum = [0.0]
        for p, q in zip(points, points[1:]):
            cum.append(cum[-1] + haversine_km(p, q))
        return cls(list(points), cum)

    @property
    def length_km(self) -> float:
        return self.cum_km[-1]

    def point_at(self, km: float) -> LatLon:
        if km <= 0:
            return self.points[0]
        if km >= self.cum_km[-1]:
            return self.points[-1]
        i = bisect_right(self.cum_km, km) - 1
        seg = self.cum_km[i + 1] - self.cum_km[i]
        f = 0.0 if seg == 0 else (km - self.cum_km[i]) / seg
        a, b = self.points[i], self.points[i + 1]
        return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]))

    def project(self, p: LatLon) -> Tuple[float, float]:
        """Vrátí (km podél trasy, kolmá vzdálenost km) — lokální rovinná aproximace, přesnost stovky metrů."""
        best = (0.0, float("inf"))
        kx = math.cos(math.radians(p[0])) * 111.32
        ky = 110.57
        for i in range(len(self.points) - 1):
            a, b = self.points[i], self.points[i + 1]
            ax, ay = (a[1] - p[1]) * kx, (a[0] - p[0]) * ky
            bx, by = (b[1] - p[1]) * kx, (b[0] - p[0]) * ky
            dx, dy = bx - ax, by - ay
            L2 = dx * dx + dy * dy
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L2))
            cx, cy = ax + t * dx, ay + t * dy
            d = math.hypot(cx, cy)
            if d < best[1]:
                seg = self.cum_km[i + 1] - self.cum_km[i]
                best = (self.cum_km[i] + t * seg, d)
        return best
