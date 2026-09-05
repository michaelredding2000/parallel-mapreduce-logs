"""Tests for the core MapReduce engine."""

import pytest
from src.mapreduce import MapReduce


# --- helper map/reduce functions ---

def word_mapper(line: str):
    return [(w.lower(), 1) for w in line.split() if w]


def sum_reducer(key, values):
    return (key, sum(values))


def upper_mapper(word: str):
    return [(word.upper(), len(word))]


class TestMapReduceBasic:
    def test_word_count(self):
        records = ["hello world", "hello python", "world of python"]
        mr = MapReduce(mapper=word_mapper, reducer=sum_reducer, workers=1)
        result = dict(mr.run(records))
        assert result["hello"] == 2
        assert result["world"] == 2
        assert result["python"] == 2
        assert result["of"] == 1

    def test_empty_input(self):
        mr = MapReduce(mapper=word_mapper, reducer=sum_reducer, workers=1)
        assert mr.run([]) == []

    def test_single_record(self):
        mr = MapReduce(mapper=word_mapper, reducer=sum_reducer, workers=1)
        result = dict(mr.run(["one two three"]))
        assert result == {"one": 1, "two": 1, "three": 1}

    def test_output_sorted_by_key(self):
        records = ["c b a", "b a"]
        mr = MapReduce(mapper=word_mapper, reducer=sum_reducer, workers=1)
        keys = [k for k, _ in mr.run(records)]
        assert keys == sorted(keys)

    def test_mapper_skips_empty_returns(self):
        def selective_mapper(x):
            return [("found", 1)] if x == "yes" else []

        mr = MapReduce(mapper=selective_mapper, reducer=sum_reducer, workers=1)
        result = dict(mr.run(["yes", "no", "yes", "maybe"]))
        assert result == {"found": 2}

    def test_custom_reducer(self):
        def collect_reducer(key, values):
            return (key, sorted(values))

        records = ["a b a", "b c"]
        mr = MapReduce(mapper=word_mapper, reducer=collect_reducer, workers=1)
        result = dict(mr.run(records))
        assert result["a"] == [1, 1]
        assert result["b"] == [1, 1]

    def test_parallel_workers(self):
        """Result must be identical whether run with 1 or multiple workers."""
        records = ["the quick brown fox"] * 20 + ["jumped over the lazy dog"] * 10
        mr1 = MapReduce(mapper=word_mapper, reducer=sum_reducer, workers=1)
        mr2 = MapReduce(mapper=word_mapper, reducer=sum_reducer, workers=2)
        r1 = dict(mr1.run(records))
        r2 = dict(mr2.run(records))
        assert r1 == r2


class TestChunking:
    def test_chunk_size_one(self):
        from src.mapreduce import MapReduce
        chunks = MapReduce._chunk(list(range(5)), chunk_size=1)
        assert len(chunks) == 5
        assert chunks == [[0], [1], [2], [3], [4]]

    def test_chunk_larger_than_input(self):
        chunks = MapReduce._chunk([1, 2], chunk_size=10)
        assert chunks == [[1, 2]]

    def test_chunk_even_split(self):
        chunks = MapReduce._chunk(list(range(6)), chunk_size=2)
        assert len(chunks) == 3
        assert all(len(c) == 2 for c in chunks)
