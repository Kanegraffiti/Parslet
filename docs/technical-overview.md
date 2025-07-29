# Parslet: Technical Overview

## Introduction

This document provides a high-level technical overview of the Parslet framework. It is intended for developers who wish to understand its architecture, core components, and internal workings, or for those interested in potentially contributing to its development. Parslet aims to provide a simple yet effective way to define and execute task-based workflows in Python.

## Core Components

Parslet's functionality is primarily delivered through a few key modules within the `parslet.core` package, along with a command-line interface and utility modules.

### 1. `parslet.core.task` (`task.py`)

This module is fundamental for defining individual tasks within a workflow.

*   **`@parslet_task` Decorator:**
    *   This decorator is used to designate a standard Python function as a Parslet task.
    *   When a decorated function is called, it does not execute immediately. Instead, the decorator wraps the function call, capturing the function itself and the arguments it was called with.
    *   It then returns a `ParsletFuture` object.

*   **`ParsletFuture` Class:**
    *   Represents the eventual result of a task that has been defined but may not have executed yet.
    *   It acts as a placeholder for the task's output and encapsulates all necessary information for the task's execution: the function to call, its arguments (`args` and `kwargs`), and a unique `task_id`.
    *   Crucially, if a `ParsletFuture` object is passed as an argument to another `@parslet_task` function, Parslet recognizes this as a dependency. The `DAGRunner` will ensure the dependency task (represented by the future) completes before the dependent task is run.

### 2. `parslet.core.dag` (`dag.py`)

This module is responsible for representing and managing the workflow as a Directed Acyclic Graph (DAG).

*   **`DAG` Class:**
    *   The primary role of the `DAG` class is to construct a graph of all tasks in a workflow.
    *   It takes a list of "entry" `ParsletFuture` objects (typically the terminal tasks of a workflow, whose results are desired) and traverses their dependencies.
    *   Dependencies are discovered by inspecting the arguments of each `ParsletFuture`: if an argument is another `ParsletFuture`, an edge is created in the graph from the dependency future's task to the current future's task.
    *   Internally, the `DAG` class uses the `networkx` library to build and manage the graph structure. This allows Parslet to leverage powerful graph algorithms for:
        *   **Cycle Detection:** Ensuring the workflow is truly acyclic via `nx.is_directed_acyclic_graph()` and `nx.find_cycle()`.
        *   **Topological Sort:** Determining a valid execution order for tasks using `nx.topological_sort()`.

### 3. `parslet.core.runner` (`runner.py`)

This module handles the execution of the tasks defined in the DAG.

*   **`DAGRunner` Class:**
    *   Orchestrates the execution of tasks in the order determined by the topological sort from the `DAG` object.
    *   It uses a `concurrent.futures.ThreadPoolExecutor` to run tasks in parallel where dependencies allow. The number of worker threads can be configured.
    *   **Argument Resolution:** Before executing a task, the `DAGRunner` resolves its arguments. If an argument is a `ParsletFuture`, the runner waits for that future's task to complete and then uses its actual result as the input for the current task.
    *   It updates the `ParsletFuture` object of each task with its result or any exception that occurred during execution.
    *   It also collects basic benchmark data (task status and execution time).

### 4. `parslet.main_cli` (`main_cli.py`)

This module provides the command-line interface for Parslet.

*   Acts as the main user entry point for running workflows.
*   **Argument Parsing:** Uses `argparse` to parse command-line arguments (e.g., workflow file path, logging level, export options).
*   **Workflow Module Loading:** Dynamically loads the user's Python workflow script as a module.
*   **Orchestration:** Initializes the `DAG` by calling the `main()` function in the user's workflow script, then builds and validates the DAG. It then invokes the `DAGRunner` to execute the workflow and displays results and benchmark statistics.

## Workflow Definition and Execution Flow

### Defining a Workflow

1.  Users write standard Python functions for each step of their process.
2.  These functions are decorated with `@parslet_task`.
3.  Calling a decorated function (e.g., `future_a = task_A(input_data)`) returns a `ParsletFuture` object.
4.  Dependencies are implicitly defined by passing `ParsletFuture` objects as arguments to other task functions (e.g., `future_b = task_B(future_a)` makes `task_B` dependent on `task_A`).
5.  The workflow script must contain a `main()` function that, when called, returns a list of `ParsletFuture` objects. These are typically the "terminal" tasks of the DAG, representing the final outputs or stages the user is interested in.

### Execution Flow (`parslet run <workflow_file.py>`)

1.  **Load:** The `main_cli.py` script loads the specified `<workflow_file.py>` as a Python module.
2.  **Discover Entry Futures:** The CLI calls the `main()` function within the loaded module. This function returns a list of `ParsletFuture` objects.
3.  **Build DAG:** An instance of the `DAG` class is created. Its `build_dag()` method is called with the entry futures. This process traverses the futures and their arguments to construct a `networkx.DiGraph` representing all tasks and dependencies.
4.  **Validate DAG:** The `dag.validate_dag()` method is called to check for cycles using `networkx`. If a cycle is detected, a `DAGCycleError` is raised, and execution halts.
5.  **Get Execution Order:** The `DAGRunner` calls `dag.get_execution_order()`, which performs a topological sort on the graph to get a linear sequence of task IDs that respects dependencies.
6.  **Execute Tasks:** The `DAGRunner.run()` method iterates through the tasks in the determined order:
    *   **Resolve Inputs:** For each task, the runner resolves its arguments. If an argument is a `ParsletFuture`, it effectively waits for that dependency task to complete and fetches its result.
    *   **Submit to Executor:** Once all inputs are concrete values, the task function is submitted to the `ThreadPoolExecutor`.
    *   **Task Execution:** The actual Python function for the task executes in one of the executor's threads.
    *   **Update Future:** Upon completion (or failure), the `_task_done_callback` in `DAGRunner` updates the task's corresponding `ParsletFuture` object with either the return value or the exception. Task status and execution time are also recorded.
7.  **Display Results:** After the runner completes, the CLI displays the status (and results/errors) of the initial entry futures and any collected benchmark statistics.

## Key Features Integration (High-Level)

*   **Resource Awareness:** The `DAGRunner`'s `__init__` method calls `get_cpu_count()` from `parslet.utils.resource_utils` to determine a default number of worker threads for the `ThreadPoolExecutor` if not specified by the user. It also logs available RAM using `get_available_ram_mb()`.
*   **Battery-Saver Mode:** The `--battery-mode` CLI flag is passed to the `DAGRunner`. If true, the runner typically defaults to a single worker thread to conserve power, unless a specific number of workers is also requested by the user.
*   **DAG Export:** When `--export-dot` or `--export-png` is used, the CLI calls functions from `parslet.core.exporter`. These functions use `dag_to_pydot()` which leverages `networkx.drawing.nx_pydot.to_pydot()` to convert the `DAG`'s internal `networkx.DiGraph` into a `pydot.Dot` object. This object can then be written to a DOT file string or rendered as a PNG image (if Graphviz is installed).
*   **Benchmarking:** The `DAGRunner` maintains dictionaries (`task_start_times`, `task_execution_times`, `task_statuses`) to record when tasks start, how long they run, and their final status. The `get_task_benchmarks()` method exposes this data, which the CLI then formats into a table using the Rich library (if available).
*   **Checkpointing & Network Checks:** When a `--checkpoint-file` is supplied the runner records each successfully completed task to that JSON file so interrupted runs can resume later. At startup the runner also warns if no internet connection is detected or if a VPN seems to be active, helping diagnose network-related failures.

## DEFCON Security

Parslet ships with a three-level *DEFCON* system which hardens common workflows:

- **Defcon 1** performs static checks in pull requests and blocks risky calls such as `os.system`.
- **Defcon 2** offers a `sandbox_task` decorator that prevents dangerous modules like `subprocess` from being imported inside a task.
- **Defcon 3** traps unhandled exceptions in the `DAGRunner` and writes a `crash.log` for later inspection.

## Dask and Parsl Compatibility

While Parslet runs its own minimal DAG engine, it can speak the syntax of Dask and Parsl when needed. The `parslet convert` command rewrites existing scripts:

```bash
parslet convert --from parsl legacy.py
parslet convert --from dask pipeline.py
```

The produced files replace `@python_app` or `dask.delayed` decorators with `@parslet_task` so they execute natively with `DAGRunner`. See `parslet.compat.dask_adapter` for runtime shims.

## Extensibility

Parslet is designed with simplicity as a core tenet. Currently, its primary mode of extension is through user-defined task libraries. Users can create complex workflows by composing many `@parslet_task` decorated functions, potentially organizing them into their own Python modules that can be imported by a main workflow script. There is no complex plugin architecture at this stage; the focus is on providing a flexible way to orchestrate arbitrary Python code.

---
This overview should provide a foundational understanding of Parslet's design. For more detailed information, please refer to the in-code documentation within the respective Python modules.
