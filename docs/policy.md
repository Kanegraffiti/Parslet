# Adaptive Policy

`AdaptivePolicy` lets Parslet scale worker threads based on current resources.

```python
from parslet.core import DAG, DAGRunner, parslet_task
from parslet.core.policy import AdaptivePolicy

@parslet_task
def work() -> None:
    print("task running")


def main() -> list:
    dag = DAG()
    fut = work()
    dag.build_dag([fut])
    policy = AdaptivePolicy(max_workers=4)
    DAGRunner(policy=policy).run(dag)
    return [fut]
```

The policy can shrink or expand the worker pool as resources change.
See `examples/policy_example.py` for a runnable script.
