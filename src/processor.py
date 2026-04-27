from __future__ import annotations

import logging
import math

from point import Point

logger = logging.getLogger(__name__)

# Earth's mean radius in metres
_EARTH_RADIUS_M = 6_371_000.0

# A car travelling faster than this between two consecutive samples is anomalous
_MAX_PLAUSIBLE_SPEED_MPS = 250_000 / 3600  # 250 km/h → m/s

# Altitude outside this range is also flagged (but not discarded)
_ALT_MIN_FLAG = -500.0
_ALT_MAX_FLAG = 9_000.0


class Processor:

    def process(self, records: list[Point]) -> list[Point]:
        # if list is empty - return
        if not records:
            return records

        for i in range(len(records) - 1):
            # time difference between point i and point i+1
            a, b = records[i], records[i + 1]
            dt = b.time - a.time

            # speed is unsigned in this context
            if dt <= 0:
                records[i].speed_mps = 0.0
            else:
                records[i].speed_mps = self._compute_speed(a, b, dt)

        # the last point has no next point
        if len(records) >= 2:
            records[-1].speed_mps = records[-2].speed_mps

        self._flag_anomalies(records)

        anomaly_count = sum(1 for r in records if r.is_anomaly)
        if anomaly_count:
            logger.warning("%d anomalous record(s) flagged.", anomaly_count)

        return records
    def _compute_speed(self, a: Point, b: Point, dt: float) -> float:
        # calculate speed with dv=dx/dt
        dist = self._haversine_m(a.lat, a.lon, b.lat, b.lon)
        return dist / dt

    @staticmethod
    def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # calculate distance between 2 points on earth
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a))

    @staticmethod
    def _flag_anomalies(records: list[Point]) -> None:
        # if speed is too high or alt is out of bounds - flag point as an anomaly
        for r in records:
            if r.speed_mps > _MAX_PLAUSIBLE_SPEED_MPS:
                r.is_anomaly = True
            if not (_ALT_MIN_FLAG <= r.alt <= _ALT_MAX_FLAG):
                r.is_anomaly = True