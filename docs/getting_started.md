# Getting Started with Parslet

This guide introduces the basics of installing Parslet and running your first workflow. Parslet is designed for offline-first environments but also includes a bridge to the Parsl runtime when you need to scale up to HPC resources.

## Installation

Clone the repository and install Parslet in editable mode:
```bash
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
pip install -e .
```
The development requirements listed in `requirements.txt` may be useful when
running the tests or working on documentation.

## Defining a Workflow

A Parslet workflow is a regular Python script that defines tasks using the `@parslet_task` decorator. The script must contain a `main()` function that returns the *terminal* futures for the workflow.

```python
from parslet import parslet_task, ParsletFuture

@parslet_task
def add_one(x: int) -> int:
    return x + 1

@parslet_task
def multiply(a: int, b: int) -> int:
    return a * b

from typing import List

def main() -> List[ParsletFuture]:
    a = add_one(1)
    b = multiply(a, 5)
    return [b]
```

Running `parslet run workflow.py` will execute the tasks in the correct order and print the result.

## Using Parsl with Parslet

Parlset tasks are standard Python functions, so you can also execute them with [Parsl](https://parsl-project.org/). The `parslet.core.parsl_bridge` module provides helpers to wrap tasks as Parsl apps:

```python
from parslet import convert_task_to_parsl, execute_with_parsl

# Reuse the tasks defined above

if __name__ == "__main__":
    futures = main()
    results = execute_with_parsl(futures)
    print(results)
```

`execute_with_parsl` builds the Parslet DAG and runs it using Parsl's runtime. This allows you to integrate Parslet workflows into larger Parsl deployments when needed. The helper disables Parsl's telemetry by default and creates a unique `run_dir` for each invocation to avoid hanging shutdowns seen in some Parsl versions.

## Converting Existing Parsl or Dask Workflows

Legacy workflows written for Parsl or Dask can be translated to Parslet using the CLI:

```bash
parslet convert --from parsl old_pipeline.py
parslet convert --from dask data_flow.py
```

This produces a new `*_parslet.py` file with equivalent `@parslet_task` decorators.

## Resuming Interrupted Runs

Long workflows can be resumed if they are run with the `--checkpoint-file` option. Completed tasks are stored in the specified JSON file and skipped on subsequent executions:

```bash
parslet run my_workflow.py --checkpoint-file run_state.json
```

Parslet also performs a quick connectivity check at startup. If no internet connection is available or a VPN is active a warning is logged so network-related failures are easier to diagnose.
