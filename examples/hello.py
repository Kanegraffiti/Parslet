"""
Parslet Example: "Hello, Parslet!" - A Basic Workflow
----------------------------------------------------

This script serves as a fundamental example of a Parslet workflow.
It demonstrates:
1. Defining simple tasks using the `@parslet_task` decorator.
2. Chaining tasks together by passing `ParsletFuture` objects as arguments,
   thereby establishing dependencies.
3. Constructing a Directed Acyclic Graph (DAG) from these tasks.
4. Running the DAG using the `DAGRunner`.
5. Retrieving and displaying the results of the terminal tasks.

The workflow itself is a series of arithmetic operations:
- Two initial `add` tasks run in parallel.
- Two `square` tasks run in parallel, each depending on one of the `add` tasks.
- A final `sum_results` task depends on both `square` tasks.

This example is designed to be run either directly (`python examples/hello.py`)
or via the Parslet CLI (`parslet run examples/hello.py`). The direct execution
mode includes verbose steps for building and running the DAG, which can be
helpful for understanding Parslet's mechanics.

Expected output of the final task: (5+3)^2 + (2+4)^2 = 100.
"""

from typing import List
import time  # To simulate work in tasks
import logging  # For task-specific logging

# Import Parslet core components
from parslet.core import (
    parslet_task,
    ParsletFuture,
    DAG,
    DAGRunner,
    DAGCycleError,
)

# Import for direct execution result checking

# Import for type hinting and handling specific exceptions during direct run
from parslet.core.runner import UpstreamTaskFailedError
import sys

# --- Logger Setup for this Example ---
# It's good practice for examples to have their own logger or use a common one.
# This allows users to see log messages from within the tasks if they
# configure logging.
logger = logging.getLogger(__name__)  # Use the name of the current module
if (
    not logger.handlers
):  # Avoid adding multiple handlers if this script is re-run or imported
    # Configure basic logging for this example.
    # When run via Parslet CLI, the CLI's logger settings might override this.
    logging.basicConfig(
        level=logging.INFO,  # Default level for this example
        format=(
            "%(asctime)s - %(name)s - [%(levelname)s] (%(funcName)s) "
            "%(message)s"
        ),
        datefmt="%H:%M:%S",
    )
# To see DEBUG messages from this example's logger,
# you would change level to logging.DEBUG
# logger.setLevel(logging.DEBUG)


# --- Task Definitions ---
# Each function decorated with @parslet_task becomes a node in our DAG.


@parslet_task
def add(a: int, b: int) -> int:
    """
    A simple Parslet task that adds two integers.
    Simulates some work using `time.sleep()`.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The sum of `a` and `b`.
    """
    logger.info(f"Executing add({a}, {b})...")
    time.sleep(0.5)  # Simulate I/O bound or CPU work
    result = a + b
    logger.info(f"Task 'add({a}, {b})' finished. "
                f"Result: {result}")
    return result


@parslet_task
def square(x: int) -> int:
    """
    A simple Parslet task that squares an integer.
    Simulates some work using `time.sleep()`.

    Args:
        x (int): The integer to square.

    Returns:
        int: The square of `x`.
    """
    logger.info(f"Executing square({x})...")
    time.sleep(0.5)  # Simulate work
    result = x * x
    logger.info(f"Task 'square({x})' finished. "
                f"Result: {result}")
    return result


@parslet_task
def sum_results(res1: int, res2: int) -> int:
    """
    A simple Parslet task that sums two integer results from previous tasks.
    Simulates some work using `time.sleep()`.

    Args:
        res1 (int): The first integer result.
        res2 (int): The second integer result.

    Returns:
        int: The sum of `res1` and `res2`.
    """
    logger.info(f"Executing sum_results({res1}, {res2})...")
    time.sleep(0.5)  # Simulate work
    result = res1 + res2
    logger.info(
        f"Task 'sum_results({res1}, {res2})' finished. Result: {result}"
    )
    return result


# --- Workflow Definition ---


def main() -> List[ParsletFuture]:
    r"""
    Defines the main workflow graph for this "Hello, Parslet!" example.

    This function is the designated entry point for the Parslet CLI. It should
    return a list of `ParsletFuture` objects that represent the terminal tasks
    (or desired final outputs) of the DAG.

    The workflow structure:
      add(5,3) ---\\              /--- sum_results
                    -> square_val1 --
      add(2,4) ---/              \\--- sum_results
                    -> square_val2 --

    Returns:
        List[ParsletFuture]: A list containing the `ParsletFuture` for the
                             final `sum_results` task.
    """
    logger.info("Workflow 'main' (hello.py): Constructing task graph...")

    # Stage 1: Initial additions (can run in parallel)
    val1_future: ParsletFuture = add(5, 3)  # Expected result: 8
    val2_future: ParsletFuture = add(2, 4)  # Expected result: 6

    # Stage 2: Squaring operations (depend on results from Stage 1,
    # can run in parallel with each other)
    # `square` is called with ParsletFuture objects. Parslet automatically
    # resolves these to their actual results before executing `square`.
    sq1_future: ParsletFuture = square(
        val1_future
    )  # Depends on val1_future (square(8) = 64)
    sq2_future: ParsletFuture = square(
        val2_future
    )  # Depends on val2_future (square(6) = 36)

    # Stage 3: Final summation (depends on results from Stage 2)
    final_sum_future: ParsletFuture = sum_results(
        sq1_future, sq2_future
    )  # Depends on sq1_future and sq2_future (64 + 36 = 100)

    logger.info(
        "Workflow 'main' (hello.py): "
        "Task graph constructed. Returning terminal future(s)."
    )

    # The CLI runner will execute the DAG to resolve these terminal futures.
    return [final_sum_future]


# --- Direct Execution Block ---
# This block allows the example to be run directly using
# `python examples/hello.py`.
# It simulates the core actions of the Parslet CLI for this specific workflow.
if __name__ == "__main__":
    # Use a distinct logger for direct execution messages,
    # or use the module logger.
    # For clarity, using the module logger.
    logger.info("--- Parslet Hello Example (Direct Execution Mode) ---")

    # Step 1: Get the entry futures by calling the workflow's main() function.
    logger.info("Step 1: Calling main() to get entry ParsletFutures...")
    entry_futures = main()  # This is the list of [final_sum_future]
    logger.info(f"Retrieved {len(entry_futures)} entry future(s) from main().")

    # Step 2: Build the DAG from these entry futures.
    logger.info("\nStep 2: Building DAG...")
    workflow_dag = DAG()
    workflow_dag.build_dag(entry_futures)
    logger.info("DAG built successfully.")

    # Optional Step: Visualize the DAG (if pydot and Graphviz are installed)
    try:
        from parslet.core.exporter import (
            save_dag_to_png,
            PydotImportError,
            GraphvizExecutableNotFoundError as GvizNotFound,
        )

        viz_path = "hello_dag.png"
        logger.info(f"Attempting to visualize DAG and "
                    f"save to '{viz_path}'...")
        save_dag_to_png(workflow_dag, viz_path)
        logger.info(f"DAG visualization saved to '{viz_path}'.")
    except (
        ImportError,
        PydotImportError,
        GvizNotFound,
    ) as viz_e:
        logger.warning(
            f"Could not visualize DAG: {viz_e}. "
            "Ensure pydot and Graphviz are installed."
        )
    except Exception as e_viz:
        logger.warning(
            f"An unexpected error occurred during DAG visualization: {e_viz}"
        )

    # Step 3: Validate the DAG (checks for cycles, etc.).
    logger.info("\nStep 3: Validating DAG...")
    try:
        workflow_dag.validate_dag()
        logger.info("DAG is valid (no cycles found).")
    except DAGCycleError as e_cycle:  # Specific exception for cycle errors
        logger.error(f"DAG validation failed: {e_cycle}",
                     exc_info=True)
        sys.exit(1)  # Exit if DAG is invalid

    # Step 4: Create a DAGRunner and execute the workflow.
    # The DAGRunner handles the actual execution of tasks in the correct order.
    # It uses a ThreadPoolExecutor for concurrency.
    # For this direct run, we can pass the module's logger to the runner.
    logger.info(
        "\nStep 4: Initializing DAGRunner and starting DAG execution..."
    )
    # Example: Use 2 worker threads. Can be adjusted or left to default.
    runner = DAGRunner(max_workers=2, runner_logger=logger)
    runner.run(workflow_dag)  # This call blocks until the DAG completes.
    logger.info("DAG execution completed by runner.")

    # Step 5: Display Results for the entry futures.
    logger.info("\n--- Direct Run: Final Results for Entry Futures ---")
    if entry_futures:
        for i, future_obj in enumerate(entry_futures):
            logger.info(
                f"\n--- Output for entry future {i+1}: "
                f"'{future_obj.task_id}' "
                f"(Function: {future_obj.func.__name__}) ---"
            )
            try:
                # Calling .result() on a ParsletFuture will:
                # - Return the value if the task succeeded.
                # - Re-raise the exception if the task failed.
                # - Re-raise UpstreamTaskFailedError if it was skipped due to a
                #   dependency failure.
                result_val = future_obj.result()
                logger.info("  Status: SUCCESSFUL")
                logger.info(f"  Result: {result_val}")
            except UpstreamTaskFailedError as e_upstream:
                logger.warning("  Status: SKIPPED (Upstream Failure)")
                logger.warning(
                    f"  Reason: {e_upstream}"
                )  # The exception itself contains detailed info
            except Exception as e_task:
                logger.error("  Status: FAILED")
                logger.error(
                    f"  Error:  {type(e_task).__name__}: {e_task}",
                    exc_info=True,
                )
    else:
        logger.warning("No entry futures were defined by main().")

    # Display benchmark statistics if available
    if hasattr(runner, "get_task_benchmarks"):
        benchmarks = runner.get_task_benchmarks()
        if benchmarks:
            logger.info("\n--- Task Execution Benchmarks (Direct Run) ---")
            # Basic print for direct run; CLI provides a Rich table.
            for task_id, data in sorted(benchmarks.items()):
                future_obj = workflow_dag.tasks.get(
                    task_id
                )  # Get future for func name
                func_name = future_obj.func.__name__ if future_obj else "N/A"
                status = data.get("status", "UNKNOWN")
                exec_time = data.get("execution_time_s")
                time_str = (
                    f"{exec_time:.4f}s" if exec_time is not None else "N/A"
                )
                logger.info(
                    f"  Task: {task_id} ({func_name}), Status: {status}, "
                    f"Time: {time_str}"
                )

    logger.info("\n--- Direct execution of hello.py finished ---")
