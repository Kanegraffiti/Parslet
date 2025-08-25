from __future__ import annotations

from parslet.core import DAG, DAGRunner, ParsletFuture, parslet_task


@parslet_task(cache=True)
def slow_double(x: int) -> int:
    """Expensive computation that benefits from caching."""
    print(f"doubling {x}")
    return x * 2


def main() -> list[ParsletFuture]:
    """Build and run a DAG with a cached task."""
    dag = DAG()
    fut = slow_double(5)
    dag.build_dag([fut])
    DAGRunner().run(dag)
    return [fut]
