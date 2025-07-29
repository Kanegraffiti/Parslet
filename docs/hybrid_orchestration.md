# Hybrid Orchestration

Parslet can mix local execution with Parsl-powered remote tasks using the
`execute_hybrid` helper. A list of task function names is provided to indicate
which tasks should be dispatched to Parsl while the rest run locally.

```python
from parslet import parslet_task, execute_hybrid

@parslet_task
def local_task():
    return 1

@parslet_task
def remote_task(x):
    return x + 1

if __name__ == "__main__":
    results = execute_hybrid([remote_task(local_task())], remote_tasks=["remote_task"])
    print(results)
```

`execute_hybrid` is intentionally simple. It runs tasks sequentially and
leverages Parsl's thread executor for the remote parts. The function serves as a
foundation for more advanced federated workflows that may span edge devices and
clusters.
