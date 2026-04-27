from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Optional

from point import Point

logger = logging.getLogger(__name__)

# Valid geographic bounds
_LAT_MIN, _LAT_MAX = -90.0, 90.0
_LON_MIN, _LON_MAX = -180.0, 180.0
_ALT_MIN, _ALT_MAX = -500.0, 9000.0


class Loader:

    def load(self, path: str | Path) -> list[Point]:
        # check if file exist, raise an error if not
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path.resolve()}")

        records: list[Point] = []
        skipped_malformed: list[int] = []
        skipped_bounds: list[int] = []

        with path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            self._check_required_columns(reader.fieldnames or [], path)

            for line_num, row in enumerate(reader, start=2):
                record = self._parse_row(row, line_num)
                if record is None:
                    skipped_malformed.append(line_num)
                    continue
                if not self._validate_bounds(record):
                    skipped_bounds.append(line_num)
                    continue
                records.append(record)

        self._log_skip_summary(skipped_malformed, skipped_bounds)

        # Sort by time, remove duplicate timestamps (keep first occurrence)
        records.sort(key=lambda r: r.time)
        records = self._deduplicate(records)

        if len(records) < 2:
            raise ValueError(
                f"Only {len(records)} valid GPS record(s) found in '{path}'. "
                "At least 2 are required to animate a track."
            )

        logger.info("Loaded %d valid GPS records from '%s'.", len(records), path)
        return records

    @staticmethod
    def _check_required_columns(fieldnames: list[str], path: Path) -> None:
        # checks if all 4 columns exist, raise an error if not
        required = {"time", "lat", "lon", "alt"}
        missing = required - {f.strip().lower() for f in fieldnames}
        if missing:
            raise ValueError(
                f"CSV '{path}' is missing required columns: {missing}. "
                f"Found: {fieldnames}"
            )

    def _parse_row(self, row: dict[str, str], line_num: int) -> Optional[Point]:
        # returns Point if all 4 values are floats and None if not
        try:
            time_val = float(row["time"])
            lat_val = float(row["lat"])
            lon_val = float(row["lon"])
            alt_val = float(row["alt"])
        except (KeyError, ValueError, TypeError) as exc:
            logger.debug("Line %d skipped — parse error: %s", line_num, exc)
            return None

        return Point(time=time_val, lat=lat_val, lon=lon_val, alt=alt_val)

    @staticmethod
    def _validate_bounds(record: Point) -> bool:
        if not (_LAT_MIN <= record.lat <= _LAT_MAX):
            return False
        if not (_LON_MIN <= record.lon <= _LON_MAX):
            return False
        # altitude outside range is logged as anomaly later, not discarded here
        return True

    @staticmethod
    def _deduplicate(records: list[Point]) -> list[Point]:
        # remove records with duplicate timestamps, keeping the first occurrence
        seen: set[float] = set()
        unique: list[Point] = []
        for r in records:
            if r.time not in seen:
                seen.add(r.time)
                unique.append(r)
            else:
                logger.debug("Duplicate timestamp %.3f dropped.", r.time)
        return unique

    @staticmethod
    def _log_skip_summary(malformed: list[int], out_of_bounds: list[int]) -> None:
        # prints skipped and malformed rows info
        if malformed:
            logger.warning(
                "%d malformed row(s) skipped (lines: %s).",
                len(malformed),
                ", ".join(map(str, malformed[:10])) + ("…" if len(malformed) > 10 else ""),
            )
        if out_of_bounds:
            logger.warning(
                "%d out-of-bounds row(s) skipped (lines: %s).",
                len(out_of_bounds),
                ", ".join(map(str, out_of_bounds[:10])) + ("…" if len(out_of_bounds) > 10 else ""),
            )
