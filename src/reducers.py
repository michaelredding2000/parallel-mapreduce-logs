"""
Built-in reduce functions for log-analysis pipelines.

Each reducer receives (key, list_of_values) and returns (key, result).
"""

from __future__ import annotations


def sum_reducer(key: object, values: list[int]) -> tuple:
    """Sum all values for a key. Good for counting."""
    return (key, sum(values))


def count_reducer(key: object, values: list) -> tuple:
    """Count the number of values (equivalent to sum when values are 1s)."""
    return (key, len(values))


def list_reducer(key: object, values: list) -> tuple:
    """Collect all values for a key into a sorted list."""
    return (key, sorted(values))


def max_reducer(key: object, values: list) -> tuple:
    """Return the maximum value for a key."""
    return (key, max(values))


def min_reducer(key: object, values: list) -> tuple:
    """Return the minimum value for a key."""
    return (key, min(values))


def avg_reducer(key: object, values: list[float]) -> tuple:
    """Return the arithmetic mean of values for a key."""
    return (key, sum(values) / len(values))
