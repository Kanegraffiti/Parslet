# Task Caching

Parslet tasks may opt into result caching by specifying `cache=True` in the
`@parslet_task` decorator. Cached results are keyed by a deterministic hash of
all task inputs and an optional version string.

```python
from parslet.core import DAG, DAGRunner, parslet_task


@parslet_task(cache=True)
def slow_double(x: int) -> int:
    print("doubling", x)
    return x * 2


def main() -> list:
    dag = DAG()
    fut = slow_double(5)
    dag.build_dag([fut])
    DAGRunner().run(dag)
    return [fut]
```

Run the script twice and the second invocation will reuse the cached result.
See `examples/cached_task.py` for the full version.

Caching is disabled unless a task requests it, and it can be globally disabled
via the `--no-cache` CLI flag or the `PARSLET_NO_CACHE` environment variable.

Cached data is stored under `~/.parslet/cache` by default. Set
`PARSLET_CACHE_DIR` to override the location. Results are serialized with
Python's `pickle` module, so task return values must be pickle‑safe.

Cache files are not automatically invalidated. When task logic changes, bump the
`version` parameter in the decorator to compute a new cache key.
