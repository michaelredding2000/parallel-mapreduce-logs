"""
Parallel MapReduce engine using multiprocessing.

Usage
-----
from src.mapreduce import MapReduce

mr = MapReduce(mapper=my_map, reducer=my_reduce, workers=4)
result = mr.run(records)      # list of (key, value) pairs, sorted by key
"""

from __future__ import annotations

import collections
import multiprocessing
from typing import Callable


def _map_chunk(args: tuple) -> list[tuple]:
    """Top-level function so multiprocessing can pickle it."""
    mapper, chunk = args
    out = []
    for record in chunk:
        pairs = mapper(record)
        if pairs:
            out.extend(pairs)
    return out


class MapReduce:
    """
    Generic parallel MapReduce.

    Parameters
    ----------
    mapper  : callable(record) -> list[(key, value)]
    reducer : callable(key, values_iter) -> (key, result)
    workers : number of parallel worker processes (default: cpu_count)
    """

    def __init__(self, mapper: Callable, reducer: Callable, workers: int | None = None) -> None:
        self.mapper = mapper
        self.reducer = reducer
        self.workers = workers or multiprocessing.cpu_count()

    def run(self, records: list, chunk_size: int | None = None) -> list[tuple]:
        """Execute map -> shuffle -> reduce over *records*. Returns sorted list of (key, result)."""
        if not records:
            return []

        chunks = self._chunk(records, chunk_size)
        args = [(self.mapper, c) for c in chunks]

        if self.workers == 1 or len(records) < 2:
            mapped: list[tuple] = []
            for a in args:
                mapped.extend(_map_chunk(a))
        else:
            with multiprocessing.Pool(processes=self.workers) as pool:
                results = pool.map(_map_chunk, args)
            mapped = [pair for chunk_result in results for pair in chunk_result]

        grouped: dict = collections.defaultdict(list)
        for key, value in mapped:
            grouped[key].append(value)

        return [self.reducer(k, vs) for k, vs in sorted(grouped.items())]

    @staticmethod
    def _chunk(records: list, chunk_size: int | None) -> list[list]:
        """Split records into equal-sized chunks for the worker pool."""
        n = len(records)
        if chunk_size is None:
            workers = multiprocessing.cpu_count()
            chunk_size = max(1, (n + workers - 1) // workers)
        return [records[i : i + chunk_size] for i in range(0, n, chunk_size)]
