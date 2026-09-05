# parallel-mapreduce-logs

A from-scratch **parallel MapReduce engine** in Python — no Hadoop, no Spark — applied to web-server log analysis.

Demonstrates multiprocessing fan-out, shuffle/group-by, and reduce aggregation on real Apache Combined Log Format data.

---

## Architecture

```
Input records
      │
      ▼
┌─────────────┐   multiprocessing.Pool
│  MAP phase  │──────────────────────── N workers, each processing one chunk
└─────────────┘
      │  list of (key, value) pairs
      ▼
┌──────────────────┐
│  SHUFFLE phase   │  group values by key (defaultdict)
└──────────────────┘
      │
      ▼
┌──────────────────┐
│  REDUCE phase    │  one reducer call per unique key (sorted order)
└──────────────────┘
      │
      ▼
 sorted list of (key, result) tuples
```

| Module | What it implements |
|---|---|
| `src/mapreduce.py` | `MapReduce` class — chunk → parallel map → shuffle → reduce |
| `src/mappers.py` | Log-line mappers: status code, HTTP method, client IP, hourly bucket, errors |
| `src/reducers.py` | Generic reducers: sum, count, list, max, min, average |
| `main.py` | Demo: load `logs/sample.log`, run five analyses in parallel |

---

## Quickstart

```bash
pip install -r requirements.txt
python main.py
```

---

## Tests

```bash
pytest tests/ -v
```

Covers 27 tests: core engine (word-count, empty input, parallel parity), chunking, and all log mappers.

---

## Key Concepts

**Map phase** — each worker independently applies the mapper to its chunk:

```
mapper(record) -> [(key, value), ...]
```

**Shuffle phase** — group all emitted pairs by key (defaultdict).

**Reduce phase** — one call per unique key, sorted output.

**Parallelism** — `multiprocessing.Pool.map` distributes chunks across CPU cores.

---

## Skills demonstrated

- `multiprocessing.Pool` for CPU-bound fan-out
- Clean map / shuffle / reduce separation
- Generic higher-order functions — any mapper + any reducer compose
- Regex-based log parsing (Combined Log Format)
- Parallel vs. sequential parity verified in tests
