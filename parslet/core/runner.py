"""Execution utilities for Parslet DAGs.

Defines :class:`DAGRunner` and related runtime exceptions.
Public API: ``DAGRunner``, ``UpstreamTaskFailedError``,
``BatteryLevelLowError`` and ``ResourceLimitError``.
"""

import hashlib
import json
import logging
import os
import socket
import time
from concurrent.futures import Future as ExecutorFuture
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

# Absolute import avoids issues when ``parslet`` is imported under
# an alternative package name (e.g. ``Parslet`` during pytest collection).
from parslet.security import shell_guard
from parslet.security.defcon import Defcon

from ..utils.checkpointing import CheckpointManager
from ..utils.diagnostics import find_free_port
from ..utils.network_utils import is_network_available, is_vpn_active
from ..utils.resource_utils import (
    get_available_ram_mb,
    get_battery_level,
    probe_resources,
)
from .cache import compute_cache_key, load_from_cache, save_to_cache
from .dag import DAG, DAGCycleError
from .policy import AdaptivePolicy
from .scheduler import AdaptiveScheduler
from .task import ParsletFuture

__all__ = [
    "DAGRunner",
    "UpstreamTaskFailedError",
    "BatteryLevelLowError",
    "ResourceLimitError",
]


class UpstreamTaskFailedError(RuntimeError):
    """
    Custom exception raised when a task cannot run because one of its
    upstream dependencies failed.

    Attributes:
        skipped_task_id (str): The ID of the task that was skipped.
        skipped_task_name (str): The name of the function for the skipped task.
        original_failure_task_id (Optional[str]): The ID of the upstream task
            that originally failed. Can be None if the root cause is not
            directly traceable to a specific Parslet task ID.
        original_exception (Exception): The actual exception object from the
            failed upstream task.
    """

    def __init__(
        self,
        skipped_task_id: str,
        skipped_task_name: str,
        original_failure_task_id: str | None,
        original_exception: Exception,
    ) -> None:
        self.skipped_task_id = skipped_task_id
        self.skipped_task_name = skipped_task_name
        self.original_failure_task_id = original_failure_task_id
        self.original_exception = original_exception
        message = (
            f"Task '{skipped_task_id}' ({skipped_task_name}) was "
            f"skipped because an upstream task "
            f"({original_failure_task_id or 'unknown'}) failed. "
            f"Original error: {type(original_exception).__name__}: "
            f"{original_exception}"
        )
        super().__init__(message)

    def __str__(self) -> str:
        """Returns the detailed error message."""
        return str(self.args[0])


class BatteryLevelLowError(RuntimeError):
    """Task skipped because system battery level is too low."""

    def __init__(self, task_id: str, task_name: str, battery_level: int) -> None:
        self.task_id = task_id
        self.task_name = task_name
        self.battery_level = battery_level
        super().__init__(
            f"Task '{task_id}' ({task_name}) skipped due to low battery "
            f"({battery_level}%)."
        )


class ResourceLimitError(RuntimeError):
    """Task failed due to system resource exhaustion (e.g., memory)."""


class DAGRunner:
    """
    Executes tasks defined in a Parslet DAG in the correct topological order.

    The DAGRunner uses a `ThreadPoolExecutor` to run tasks concurrently where
    dependencies allow. It handles resolving task arguments from the outputs of
    their dependencies, manages task states (running, success, failure,
    skipped), and collects basic benchmark data like execution times.

    It can adjust its concurrency based on available system resources using an
    :class:`AdaptivePolicy`.
    """

    def __init__(
        self,
        max_workers: int | None = None,
        runner_logger: logging.Logger | None = None,
        policy: AdaptivePolicy | None = None,
        ignore_battery: bool = False,
        json_logs: bool = False,
        monitor_port: int = 6300,
        checkpoint_file: str | None = None,
        failsafe_mode: bool = False,
        signature_file: str | None = None,
        watch_files: list[str] | None = None,
        disable_cache: bool = False,
    ) -> None:
        """
        Initializes the DAGRunner.

        Args:
            max_workers (Optional[int]): The maximum number of worker threads
                for the ThreadPoolExecutor. If None or 0, the number of
                workers defaults based on CPU count or battery mode.
            runner_logger (Optional[logging.Logger]): An optional logger
                instance. If None, a logger named 'parslet-runner' is used,
                which might be pre-configured (e.g., by the CLI) or receive a
                basic default configuration.
            policy (Optional[AdaptivePolicy]): Policy controlling worker pool
                size based on resource probes.
            ignore_battery (bool): If True, battery-sensitive tasks will run
                even when the system battery level is below the recommended
                threshold.
            monitor_port (int): Preferred port for optional monitoring server.
                If the port is occupied, a free port is chosen automatically.
            checkpoint_file (Optional[str]): Path to a JSON file used to
                record completed tasks so a run can resume after
                interruptions.
            failsafe_mode (bool): If True, tasks that fail due to resource
                exhaustion will be retried sequentially using a basic
                executor.
            disable_cache (bool): If True, disables task caching even for tasks
                that request it. Can also be set via the ``PARSLET_NO_CACHE``
                environment variable.
        """
        if runner_logger:
            self.logger = runner_logger
        else:
            # Attempt to get a logger that might have been configured by the
            # CLI
            self.logger = logging.getLogger("parslet-runner")
            if not self.logger.handlers:  # Check if it has handlers (i.e., configured)
                # Fallback to a basic configuration if no handlers are found.
                base_logger = logging.getLogger("parslet")  # Check base logger too
                if base_logger.handlers:
                    self.logger = base_logger  # Use base logger if it's configured
                else:  # Last resort: basicConfig
                    logging.basicConfig(
                        level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - "
                        "%(message)s",
                    )
                    self.logger = logging.getLogger("parslet-runner-fallback")
                    self.logger.info(
                        "Runner logger not specified or pre-configured, "
                        "using basicConfig fallback."
                    )

        self.ignore_battery = ignore_battery
        self.failsafe_mode = failsafe_mode
        self.fallback_active = False
        user_specified_max_workers = max_workers
        self.signature_file = Path(signature_file) if signature_file else None
        self.json_logs = json_logs
        self._tamper_check = (
            Defcon.tamper_guard(Path(p) for p in watch_files) if watch_files else None
        )

        self.disable_cache = disable_cache or bool(os.getenv("PARSLET_NO_CACHE"))

        if policy is not None:
            if user_specified_max_workers is not None:
                policy.max_workers = user_specified_max_workers
            self.policy = policy
        else:
            self.policy = AdaptivePolicy(max_workers=user_specified_max_workers)

        self.scheduler = AdaptiveScheduler(policy=self.policy)
        self.max_workers = self.scheduler.calculate_worker_count()
        self.logger.info(f"DAGRunner initialized with max_workers={self.max_workers}")

        # Determine monitoring port, fallback if busy
        self.monitor_port = monitor_port
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", self.monitor_port))
        except OSError:
            new_port = find_free_port(self.monitor_port + 1)
            self.logger.warning(
                f"Monitoring port {self.monitor_port} in use. "
                f"Falling back to {new_port}."
            )
            self.monitor_port = new_port

        # Initialize checkpoint manager if requested
        self.checkpoint = (
            CheckpointManager(checkpoint_file) if checkpoint_file else None
        )

        # --- Benchmark Data Collection ---
        # Stores the monotonic start time of each task.
        self.task_start_times: dict[str, float] = {}
        # Stores the execution duration (in seconds) of each completed or
        # failed task.
        self.task_execution_times: dict[str, float] = {}
        # Stores the final status of each task: "SUCCESS", "FAILED",
        # "SKIPPED", or "RUNNING" (transient).
        self.task_statuses: dict[str, str] = {}

        # Reference to the DAG being executed, used for richer error messages
        self._dag: DAG | None = None

    def get_task_benchmarks(self) -> dict[str, dict[str, Any]]:
        """
        Retrieves benchmark data for all tasks processed or known by the
        runner.

        The returned data includes the status of each task and its execution
        time in seconds if the task was run.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary where keys are task IDs.
                Each value is a dictionary with:
                - "status" (str): The execution status (e.g., "SUCCESS",
                  "FAILED", "SKIPPED").
                - "execution_time_s" (Optional[float]): The execution time in
                  seconds. This will be None for tasks that were skipped or
                  whose time was not recorded.
        """
        benchmarks = {}
        # Consolidate all task IDs encountered during execution
        all_tracked_task_ids = (
            set(self.task_statuses.keys())
            | set(self.task_execution_times.keys())
            | set(self.task_start_times.keys())
        )

        for task_id in all_tracked_task_ids:
            status = self.task_statuses.get(
                task_id, "UNKNOWN"
            )  # Default if somehow not set
            exec_time = self.task_execution_times.get(
                task_id
            )  # None if skipped or not timed

            benchmarks[task_id] = {
                "status": status,
                "execution_time_s": exec_time,
            }
        return benchmarks

    def _resolve_task_arguments(
        self, dag: DAG, parslet_future_to_resolve: ParsletFuture
    ) -> tuple[list[object], dict[str, object], Exception | None]:
        """
        Resolves the arguments for a given ParsletFuture by obtaining results
        from its dependency ParsletFutures.

        This method iterates through the `args` and `kwargs` of the
        `parslet_future_to_resolve`. If an argument is another `ParsletFuture`
        (a dependency), its `result()` method is called. This call will block
        until the dependency's result is available or an exception is set on
        it.

        Args:
            dag (DAG): The DAG object, used to potentially retrieve future
                objects if needed (though current implementation gets results
                from futures directly).
            parslet_future_to_resolve (ParsletFuture): The ParsletFuture whose
                arguments are to be resolved.

        Returns:
            tuple[list[object], dict[str, object], Exception | None]:
                A tuple containing:
                - resolved_args (list[object]): Positional arguments with
                  ParsletFutures replaced by their results.
                - resolved_kwargs (dict[str, object]): Keyword arguments with
                  ParsletFutures replaced by their results.
                - first_exception (Exception | None): The first exception
                  encountered from a failed dependency. If all dependencies
                  succeed, this is None.
        """
        resolved_args: list[object] = []
        first_exception: Exception | None = None

        for arg in parslet_future_to_resolve.args:
            if isinstance(arg, ParsletFuture):
                try:
                    # This call blocks until the dependency's result is
                    # available or an exception is raised.
                    dependency_result = arg.result()
                    resolved_args.append(dependency_result)
                except Exception as e:
                    if first_exception is None:  # Capture the first failure
                        first_exception = e
                    resolved_args.append(
                        None
                    )  # Append a placeholder; task won't run if
                    # first_exception is set
            else:
                resolved_args.append(arg)

        resolved_kwargs: dict[str, object] = {}
        for key, kwarg_val in parslet_future_to_resolve.kwargs.items():
            if isinstance(kwarg_val, ParsletFuture):
                try:
                    dependency_result = kwarg_val.result()
                    resolved_kwargs[key] = dependency_result
                except Exception as e:
                    if first_exception is None:  # Capture the first failure
                        first_exception = e
                    resolved_kwargs[key] = None  # Placeholder
            else:
                resolved_kwargs[key] = kwarg_val

        return resolved_args, resolved_kwargs, first_exception

    @staticmethod
    def _wrapped_task_execution(
        parslet_future: ParsletFuture,
        args: list[object],
        kwargs: dict[str, object],
    ) -> object:
        """Execute a task function and translate resource errors."""
        allow_shell = getattr(parslet_future.func, "_parslet_allow_shell", False)
        try:
            with shell_guard(allow_shell):
                return parslet_future.func(*args, **kwargs)
        except (MemoryError, OSError) as e:
            raise ResourceLimitError(str(e)) from e

    def _maybe_resize_pool(self) -> None:
        """Adjust executor worker count based on current policy."""

        if not hasattr(self, "executor") or self.policy is None:
            return
        snapshot = probe_resources()
        new_size = self.policy.decide_pool_size(snapshot)
        old_size = getattr(self, "_pool_size", new_size)
        if new_size != old_size:
            self.executor._max_workers = new_size
            self._pool_size = new_size
            if self.json_logs:
                self.logger.info(
                    json.dumps(
                        {"event": "pool_resize", "old": old_size, "new": new_size}
                    )
                )
            else:
                self.logger.info(f"Resized worker pool from {old_size} to {new_size}")

    def _remediation_hint(self, exc: Exception) -> str:
        """Provide a simple one-line remediation hint based on the exception."""
        if isinstance(exc, FileNotFoundError):
            return "File not found: verify path or working directory"
        return "Check task inputs or environment"

    def _task_done_callback(
        self, parslet_future: ParsletFuture, executor_future: ExecutorFuture[Any]
    ) -> None:
        """
        Callback executed when a task submitted to the ThreadPoolExecutor
        completes.

        This method retrieves the result (or exception) from the
        `ExecutorFuture` and updates the corresponding `ParsletFuture`'s
        state. It also records the task's execution time and final status for
        benchmarking.

        Args:
            parslet_future (ParsletFuture): The ParsletFuture associated with
                the completed task.
            executor_future (ExecutorFuture): The `concurrent.futures.Future`
                object from the ThreadPoolExecutor.
        """
        task_id = parslet_future.task_id
        try:
            result = executor_future.result()
            parslet_future.set_result(result)
            self.task_statuses[task_id] = "SUCCESS"
            self.logger.info(
                f"Task '{task_id}' ({parslet_future.func.__name__}) "
                "completed successfully."
            )
            if (
                getattr(parslet_future.func, "_parslet_cache", False)
                and not self.disable_cache
            ):
                cache_key = getattr(parslet_future, "_cache_key", None)
                if cache_key:
                    try:
                        save_to_cache(cache_key, result)
                    except Exception as e:  # pragma: no cover - cache errors non-fatal
                        self.logger.warning(
                            f"Failed to write cache for task '{task_id}': {e}"
                        )
            if self.checkpoint:
                self.checkpoint.mark_complete(task_id, "SUCCESS")
        except ResourceLimitError as e:
            if self.failsafe_mode:
                self.logger.warning(
                    f"Task '{task_id}' hit resource limits: {e}. "
                    "Re-running serially."
                )
                args = getattr(parslet_future, "_resolved_args", [])
                kwargs = getattr(parslet_future, "_resolved_kwargs", {})
                self._run_task_serially(parslet_future, args, kwargs)
                return
            parslet_future.set_exception(e)
            self.task_statuses[task_id] = "FAILED"
            self.logger.error(
                f"Task '{task_id}' ({parslet_future.func.__name__}) failed "
                f"due to resource limits: {e}",
                exc_info=True,
            )
        except Exception as e:
            # Task execution failed.
            parslet_future.set_exception(e)
            self.task_statuses[task_id] = "FAILED"
            deps: list[str] = []
            if self._dag:
                try:
                    deps = self._dag.get_dependencies(task_id)
                except Exception:  # pragma: no cover - best effort
                    deps = []
            deps_str = ", ".join(deps) if deps else "none"
            hint = self._remediation_hint(e)
            self.logger.error(
                f"Task '{task_id}' ({parslet_future.func.__name__}) failed "
                f"with {type(e).__name__}: {e}. Predecessors: {deps_str}. "
                f"Hint: {hint}",
                exc_info=True,
            )
        finally:
            # Record execution time regardless of success or failure, if start
            # time was logged.
            if task_id in self.task_start_times:
                end_time = time.monotonic()
                duration = end_time - self.task_start_times[task_id]
                self.task_execution_times[task_id] = duration
                self.logger.debug(
                    f"Task '{task_id}' finished. Duration: {duration:.4f}s. "
                    f"Status: {self.task_statuses.get(task_id)}"
                )
            self._maybe_resize_pool()

    def _run_task_serially(
        self,
        parslet_future: ParsletFuture,
        args: list[object],
        kwargs: dict[str, object],
    ) -> None:
        """Execute a task synchronously in fallback mode."""
        if not self.fallback_active:
            self.logger.warning(
                "Failsafe executor activated. Tasks will run serially where " "needed."
            )
            self.fallback_active = True
        task_id = parslet_future.task_id
        self.logger.info(
            f"Running task '{task_id}' ({parslet_future.func.__name__}) in "
            "failsafe executor."
        )
        start = time.monotonic()
        try:
            result = parslet_future.func(*args, **kwargs)
            parslet_future.set_result(result)
            self.task_statuses[task_id] = "SUCCESS"
            if (
                getattr(parslet_future.func, "_parslet_cache", False)
                and not self.disable_cache
            ):
                cache_key = getattr(parslet_future, "_cache_key", None)
                if cache_key:
                    try:
                        save_to_cache(cache_key, result)
                    except Exception as e:  # pragma: no cover
                        self.logger.warning(
                            f"Failed to write cache for task '{task_id}': {e}"
                        )
            if self.checkpoint:
                self.checkpoint.mark_complete(task_id, "SUCCESS")
        except Exception as e:
            parslet_future.set_exception(e)
            self.task_statuses[task_id] = "FAILED"
            self.logger.error(
                f"Task '{task_id}' ({parslet_future.func.__name__}) failed in "
                f"failsafe executor: {type(e).__name__}: {e}",
                exc_info=True,
            )
        finally:
            duration = time.monotonic() - start
            self.task_execution_times[task_id] = duration
            self.logger.debug(
                f"Task '{task_id}' finished in failsafe executor. "
                f"Duration: {duration:.4f}s. "
                f"Status: {self.task_statuses.get(task_id)}"
            )

    def run(self, dag: DAG) -> None:
        """
        Executes all tasks in the provided DAG according to their dependencies.

        The method first validates the DAG and gets a topological execution
        order. It then iterates through tasks, resolving their arguments
        (which waits for dependencies to complete) and submits them to a
        ThreadPoolExecutor. Task statuses and execution times are recorded.

        Args:
            dag (DAG): The Parslet DAG object containing tasks to be executed.
        """
        self._dag = dag
        self.logger.info(
            f"DAGRunner starting execution with {self.max_workers} worker " "thread(s)."
        )

        if not is_network_available():
            self.logger.warning(
                "No internet connection detected. Tasks that require the "
                "network may fail."
            )
        if is_vpn_active():
            self.logger.info(
                "A VPN connection appears to be active. Network behaviour "
                "may differ."
            )

        # Log available system RAM at the start of the run.
        available_ram = get_available_ram_mb()
        if available_ram is not None:
            self.logger.info(f"Available RAM at runner start: {available_ram:.2f} MB.")
        else:
            self.logger.info(
                "Available RAM information: Not available (psutil might not "
                "be installed or accessible)."
            )

        try:
            # Ensure DAG is valid (e.g., no cycles) before starting.
            dag.validate_dag()
            execution_order = dag.get_execution_order()  # List of task_ids
            files = {Path(f.func.__code__.co_filename) for f in dag.tasks.values()}
            if not Defcon.scan_code(files):
                self.logger.error("DEFCON1 scan failed")
                return
            dag_hash = hashlib.sha256(
                "".join(sorted(str(p) for p in files)).encode()
            ).hexdigest()
            if not Defcon.verify_chain(
                dag_hash, self.signature_file or Path("signature.txt")
            ):
                self.logger.error("DEFCON2 integrity check failed")
                return
        except DAGCycleError as e:
            self.logger.error(
                f"Cannot run DAG due to cycle: {e}", exc_info=False
            )  # No full stack trace for cycle error
            return
        except Exception as e:
            self.logger.error(
                f"Failed to get execution order or validate DAG: {e}",
                exc_info=True,
            )
            return

        if not execution_order:
            self.logger.info("DAG is empty. No tasks to execute.")
            return

        # Execute tasks using a ThreadPoolExecutor.
        # The 'with' statement ensures the pool is properly shut down.
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            self.executor = executor
            self._pool_size = self.max_workers
            for task_id in execution_order:
                if self._tamper_check and not self._tamper_check():
                    self.logger.critical("DEFCON3 tamper detected; aborting run")
                    return
                current_parslet_future = dag.get_task_future(task_id)
                if self.checkpoint and task_id in self.checkpoint.completed:
                    self.logger.info(
                        f"Skipping task '{task_id}' as it was already "
                        "completed in a previous run."
                    )
                    self.task_statuses[task_id] = "SKIPPED"
                    current_parslet_future.set_result(None)
                    continue
                self.logger.debug(
                    f"Preparing task '{task_id}' "
                    f"({current_parslet_future.func.__name__})..."
                )

                # Resolve arguments by getting results from dependency
                # ParsletFutures. This implicitly waits for dependencies to
                # complete before proceeding.
                (
                    resolved_args,
                    resolved_kwargs,
                    dependency_exception,
                ) = self._resolve_task_arguments(dag, current_parslet_future)

                if dependency_exception is not None:
                    # An upstream dependency failed. Mark this task as SKIPPED
                    # and set its exception.
                    original_failing_task_id: str | None = None
                    true_original_exception = dependency_exception
                    if isinstance(dependency_exception, UpstreamTaskFailedError):
                        # If the dependency itself was skipped, trace back to
                        # the root cause.
                        true_original_exception = (
                            dependency_exception.original_exception
                        )
                        original_failing_task_id = (
                            dependency_exception.original_failure_task_id
                        )

                    err_msg_for_log = (
                        f"Task '{task_id}' "
                        f"({current_parslet_future.func.__name__}) skipped "
                        "due to upstream failure in task "
                        f"'{original_failing_task_id or 'unknown'}'. "
                        f"Root error: {type(true_original_exception).__name__}"
                        f": {true_original_exception}"
                    )
                    self.logger.error(err_msg_for_log)
                    self.task_statuses[task_id] = "SKIPPED"

                    current_parslet_future.set_exception(
                        UpstreamTaskFailedError(
                            skipped_task_id=task_id,
                            skipped_task_name=(current_parslet_future.func.__name__),
                            original_failure_task_id=original_failing_task_id,
                            original_exception=true_original_exception,
                        )
                    )
                    continue  # Move to the next task in the execution order.

                cache_enabled = (
                    getattr(current_parslet_future.func, "_parslet_cache", False)
                    and not self.disable_cache
                )
                if cache_enabled:
                    version = getattr(
                        current_parslet_future.func, "_parslet_cache_version", "1"
                    )
                    task_name = getattr(
                        current_parslet_future.func,
                        "_parslet_task_name",
                        current_parslet_future.func.__name__,
                    )
                    cache_key = compute_cache_key(
                        task_name, tuple(resolved_args), resolved_kwargs, version
                    )
                    try:
                        cached = load_from_cache(cache_key)
                    except FileNotFoundError:
                        current_parslet_future._cache_key = cache_key  # type: ignore[attr-defined]
                    else:
                        self.logger.info(
                            f"Cache hit for task '{task_id}' ({task_name})."
                        )
                        current_parslet_future.set_result(cached)
                        self.task_statuses[task_id] = "SUCCESS"
                        self.task_execution_times[task_id] = 0.0
                        if self.checkpoint:
                            self.checkpoint.mark_complete(task_id, "SUCCESS")
                        continue

                # Check battery level for battery-sensitive tasks.
                batt_level = get_battery_level()
                if (
                    getattr(
                        current_parslet_future.func,
                        "_parslet_battery_sensitive",
                        False,
                    )
                    and not self.ignore_battery
                    and batt_level is not None
                    and batt_level < 20
                ):
                    self.logger.warning(
                        f"Skipping battery-sensitive task '{task_id}' due to "
                        f"low battery ({batt_level}%)."
                        " Use --ignore-battery to override."
                    )
                    self.task_statuses[task_id] = "SKIPPED"
                    current_parslet_future.set_exception(
                        BatteryLevelLowError(
                            task_id,
                            current_parslet_future.func.__name__,
                            batt_level,
                        )
                    )
                    if self.checkpoint:
                        self.checkpoint.mark_complete(task_id, "SKIPPED")
                    continue

                # All dependencies resolved successfully, submit the task to
                # the executor.
                try:
                    self.logger.info(
                        f"Submitting task '{task_id}' "
                        f"({current_parslet_future.func.__name__}) to "
                        "executor."
                    )
                    self.task_start_times[task_id] = time.monotonic()
                    self.task_statuses[task_id] = "RUNNING"

                    # store resolved args for potential failsafe re-run
                    current_parslet_future._resolved_args = resolved_args  # type: ignore[attr-defined]
                    current_parslet_future._resolved_kwargs = resolved_kwargs  # type: ignore[attr-defined]

                    exec_future = executor.submit(
                        self._wrapped_task_execution,
                        current_parslet_future,
                        resolved_args,
                        resolved_kwargs,
                    )

                    # Add a callback to handle task completion/failure and
                    # update ParsletFuture.
                    def _cb(
                        executor_fut: ExecutorFuture[Any],
                        parslet_fut: ParsletFuture = current_parslet_future,
                    ) -> None:
                        self._task_done_callback(parslet_fut, executor_fut)

                    exec_future.add_done_callback(_cb)
                except (MemoryError, OSError) as e:
                    if self.failsafe_mode:
                        self.logger.warning(
                            f"Executor rejected task '{task_id}' due to "
                            f"resource limits: {e}. Running serially."
                        )
                        self._run_task_serially(
                            current_parslet_future,
                            resolved_args,
                            resolved_kwargs,
                        )
                    else:
                        err_msg = (
                            "Failed to submit task " f"'{task_id}' to executor: {e}"
                        )
                        self.logger.critical(err_msg, exc_info=True)
                        current_parslet_future.set_exception(RuntimeError(err_msg))
                        self.task_statuses[task_id] = "FAILED"
                        if task_id in self.task_start_times:
                            end_time = time.monotonic()
                            duration = end_time - self.task_start_times[task_id]
                            self.task_execution_times[task_id] = duration
                except Exception as e:
                    err_msg = f"Failed to submit task '{task_id}' to executor: {e}"
                    self.logger.critical(err_msg, exc_info=True)
                    current_parslet_future.set_exception(RuntimeError(err_msg))
                    self.task_statuses[task_id] = "FAILED"
                    if task_id in self.task_start_times:
                        end_time = time.monotonic()
                        duration = end_time - self.task_start_times[task_id]
                        self.task_execution_times[task_id] = duration

        self.logger.info("DAGRunner finished processing all tasks.")
