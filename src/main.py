from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from loader import Loader
from processor import Processor
from visualizer import Visualizer


def _configure_logging() -> None:
    # log settings
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GPS Track Visualiser")
    parser.add_argument(
        "csv",
        nargs="?",
        default="car_track.csv",
        help="Path to the GPS track CSV file (default: car_track.csv)",
    )
    parser.add_argument("--port", type=int, default=8050, help="Port to serve on")
    parser.add_argument("--debug", action="store_true", help="Enable Dash debug mode")
    return parser.parse_args()


def main() -> None:
    _configure_logging()
    args = _parse_args()

    try:
        records = Loader().load(args.csv)
        records = Processor().process(records)
        Visualizer(records).run(debug=args.debug, port=args.port)
    except FileNotFoundError as exc:
        logging.critical("File error: %s", exc)
        sys.exit(1)
    except ValueError as exc:
        logging.critical("Data error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
