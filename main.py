"""
Demo: analyse logs/sample.log with parallel MapReduce.

Usage
-----
    python main.py [--log logs/sample.log] [--workers 4]
"""

from __future__ import annotations

import argparse
import pathlib

from src.mapreduce import MapReduce
from src.mappers import status_code_mapper, method_mapper, ip_mapper, error_mapper, hourly_mapper
from src.reducers import sum_reducer


def load_lines(path: str) -> list[str]:
    return pathlib.Path(path).read_text().splitlines()


def run_analysis(lines: list[str], workers: int) -> None:
    def _run(label: str, mapper, reducer=sum_reducer):
        mr = MapReduce(mapper=mapper, reducer=reducer, workers=workers)
        results = mr.run(lines)
        print(f"\n{'─'*40}")
        print(f"  {label}")
        print(f"{'─'*40}")
        for key, val in results:
            print(f"  {key:<30} {val}")

    _run("Requests by HTTP status code", status_code_mapper)
    _run("Requests by HTTP method",       method_mapper)
    _run("Requests per hour",             hourly_mapper)
    _run("Top client IPs",                ip_mapper)
    _run("Error count (4xx/5xx)",         error_mapper)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parallel log analyser")
    parser.add_argument("--log",     default="logs/sample.log", help="Path to log file")
    parser.add_argument("--workers", default=4, type=int,       help="Worker processes")
    args = parser.parse_args()

    lines = load_lines(args.log)
    print(f"Loaded {len(lines)} log lines from {args.log} (workers={args.workers})")
    run_analysis(lines, workers=args.workers)


if __name__ == "__main__":
    main()
