from __future__ import annotations

from parslet.core import DAG, DAGRunner, ParsletFuture, parslet_task
from parslet.core.policy import AdaptivePolicy


@parslet_task
def work() -> None:
    """A tiny task used to demonstrate AdaptivePolicy."""
    print("task running")


def main() -> list[ParsletFuture]:
    dag = DAG()
    fut = work()
    dag.build_dag([fut])
    policy = AdaptivePolicy(max_workers=4)
    DAGRunner(policy=policy).run(dag)
    return [fut]
