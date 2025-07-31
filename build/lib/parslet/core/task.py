"""Task utilities and decorators for building Parslet DAGs."""

import uuid
import functools
import logging
from typing import Callable, Any, List, Dict, Optional
from threading import Event

# Global registry for Parslet tasks.
# This dictionary maps a task's registered name (str) to the actual callable function.
# It's used to look up task functions, though direct function references are common in ParsletFutures.
_TASK_REGISTRY: Dict[str, Callable[..., Any]] = {}
# Global flag controlling whether protected tasks can be redefined.  This is
# toggled via the CLI using the ``--force-redefine`` option or directly in
# tests.
_ALLOW_REDEFINE: bool = False

# Sentinel object used to indicate that a ParsletFuture's result has not yet been computed.
# This helps distinguish between a result of `None` and no result being set.
_RESULT_NOT_SET = object()

# Module-level logger for task utilities
logger = logging.getLogger(__name__)


class ParsletFuture:
    """
    Represents the placeholder for the future result of a Parslet task.

    When a function decorated with `@parslet_task` is called, it does not execute
    immediately. Instead, it returns a `ParsletFuture` object. This object acts as a
    proxy for the task's eventual output, holding metadata such as a unique task ID,
    the function to be executed, and the arguments it was called with.

    The `DAGRunner` is responsible for executing the task and then populating
    the `ParsletFuture` with either its result or any exception that occurred
    during execution. Other tasks that depend on this future can then access
    its result to proceed.

    Attributes:
        task_id (str): A unique identifier for this specific task invocation.
        func (Callable[..., Any]): The underlying Python function that this future represents.
        args (tuple): The positional arguments passed to the task function.
        kwargs (Dict[str, Any]): The keyword arguments passed to the task function.
        _result (Any): Internal storage for the task's result. Initialized to `_RESULT_NOT_SET`.
        _exception (Optional[Exception]): Internal storage for any exception raised during task execution.
                                         Defaults to None.
    """

    def __init__(
        self,
        task_id: str,
        func: Callable[..., Any],
        args: tuple,
        kwargs: Dict[str, Any],
    ):
        """
        Initializes a new ParsletFuture.

        Args:
            task_id (str): The unique ID for this task instance.
            func (Callable[..., Any]): The callable (function) that will be executed.
            args (tuple): The positional arguments for the function.
            kwargs (Dict[str, Any]): The keyword arguments for the function.
        """
        self.task_id: str = task_id
        self.func: Callable[..., Any] = func
        self.args: tuple = args
        self.kwargs: Dict[str, Any] = kwargs

        # Internal attributes to store the outcome of the task execution.
        self._result: Any = _RESULT_NOT_SET
        self._exception: Optional[Exception] = None
        # Event used to signal completion of this task (success or failure)
        self._done: Event = Event()
        # self.func_name: str = func.__name__ # Alternative: store name if needed for registry lookup

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the ParsletFuture.

        Returns:
            str: A string like "<ParsletFuture task_id='...' func='...'>".
        """
        return f"<ParsletFuture task_id='{self.task_id}' func='{self.func.__name__}'>"

    def set_result(self, value: Any) -> None:
        """
        Sets the successful result of the task.

        This method is typically called by the `DAGRunner` once the task has
        completed successfully.

        Args:
            value (Any): The result value of the task.

        Raises:
            RuntimeError: If an exception has already been set for this future,
                          as a future cannot both succeed and fail.
        """
        if self._exception is not None:
            # Prevent setting a result if the task has already been marked as failed.
            raise RuntimeError(
                f"Cannot set result for task {self.task_id} ('{self.func.__name__}'); it has already failed with an exception."
            )
        self._result = value
        self._done.set()

    def set_exception(self, exception: Exception) -> None:
        """
        Records an exception that occurred during the task's execution.

        This method is typically called by the `DAGRunner` if the task
        raises an unhandled exception.

        Args:
            exception (Exception): The exception object that was raised.
        """
        self._exception = exception
        # Ensure that if an exception is set, any previously set result (though unlikely)
        # or the initial _RESULT_NOT_SET sentinel is cleared to reflect failure.
        self._result = _RESULT_NOT_SET
        self._done.set()

    def result(self, timeout: Optional[float] = None) -> Any:
        """
        Retrieves the result of the task.

        If the task executed successfully, its return value is provided.
        If the task failed, the exception that occurred during its execution
        is re-raised. If the result is not yet available (i.e., the task has
        not completed), this method will raise a `RuntimeError`.

        Note: In the current implementation, this method does not implement
        actual blocking with a timeout. The `timeout` argument is a placeholder
        for potential future enhancements (e.g., in an asynchronous runner).
        The `DAGRunner` ensures that `result()` is called on dependency futures
        in a way that implicitly waits for their completion.

        Args:
            timeout (Optional[float]): A placeholder for future timeout functionality.
                                       Currently not used.

        Returns:
            Any: The result of the task if it completed successfully.

        Raises:
            Exception: The exception that was raised by the task if it failed.
                       This is the original exception, not a wrapper.
            RuntimeError: If the task's result is not yet available (i.e., it hasn't
                          been set by the runner, often meaning the task hasn't completed
                          or was not run).
        """
        if self._exception is not None:
            # If an exception was recorded, re-raise it to the caller.
            raise self._exception

        if self._result is _RESULT_NOT_SET:
            # Block until the task has completed (result set or exception raised)
            self._done.wait(timeout)
            if self._result is _RESULT_NOT_SET and self._exception is None:
                raise RuntimeError(
                    f"Result for task {self.task_id} ('{self.func.__name__}') is not available yet. "
                    "Ensure the task has been executed by a Parslet DAGRunner and has completed."
                )
            if self._exception is not None:
                raise self._exception
        return self._result

    # Example for future async compatibility (not currently implemented):
    # def __await__(self):
    #     # This would require integration with an asyncio event loop and futures.
    #     # For instance, self._result might become an asyncio.Future.
    #     if self._result is _RESULT_NOT_SET and self._exception is None:
    #         # Placeholder: yield from an internal asyncio.Future or event.
    #         pass
    #     if self._exception is not None:
    #         raise self._exception
    #     return self._result


def parslet_task(
    _func: Optional[Callable[..., Any]] = None,
    *,
    # The 'dependencies' argument here refers to explicit naming of dependencies,
    # which is a potential feature but not the primary mechanism used in Parslet's
    # current DAG construction (which relies on ParsletFuture objects passed as arguments).
    # It's kept as a placeholder for future extensibility.
    dependencies: Optional[List[str]] = None,
    name: Optional[str] = None,
    protected: bool = False,
    battery_sensitive: bool = False,
    # Other potential parameters for future extension:
    # retries: Optional[int] = None,
    # cache_policy: Optional[str] = None,
    # resources: Optional[Dict[str, Any]] = None, (e.g., {'cpu': 1, 'memory_mb': 1024})
):
    """
    Decorator to define a Python function as a Parslet task.

    When a function decorated with `@parslet_task` is called, it does not execute
    immediately. Instead, it captures the function call (the function itself,
    arguments, and keyword arguments) and returns a `ParsletFuture` object.
    This `ParsletFuture` acts as a node in the DAG and a placeholder for the
    task's eventual result.

    The actual execution of the task is managed by the `DAGRunner`, which
    respects task dependencies.

    Args:
        _func (Optional[Callable[..., Any]]): The function being decorated. This is
            supplied automatically by Python when the decorator is used without
            parentheses (e.g., `@parslet_task`). If used with parentheses
            (e.g., `@parslet_task(name="my_custom_name")`), this will be `None`.
        dependencies (Optional[List[str]]): (Placeholder for future use)
            A list of task names (strings) that this task explicitly depends on.
            Currently, dependencies are primarily inferred from `ParsletFuture`
            objects passed as arguments.
        name (Optional[str]): An optional custom name for the task. If not provided,
            the function's `__name__` attribute (its original name) is used as the
            base for the task name and task ID.
        protected (bool): If True, attempts to register another task with the
            same name will raise an error unless ``_ALLOW_REDEFINE`` is True.
        battery_sensitive (bool): If True, the task may be skipped when the
            system battery level is below 20% unless the user overrides this
            behaviour in the CLI.

    Returns:
        Callable: A wrapped function that, when called, returns a `ParsletFuture`.
    """

    def decorator_parslet_task(func_to_wrap: Callable[..., Any]):
        # Determine the task's base name: use custom 'name' if provided, else function's own name.
        task_name = name if name is not None else func_to_wrap.__name__

        # (Optional) Register the original function in a global registry.
        # This could be used for looking up tasks by name, though Parslet primarily
        # uses direct function references stored in ParsletFutures.
        if task_name in _TASK_REGISTRY:
            existing_func = _TASK_REGISTRY[task_name]
            existing_protected = getattr(
                existing_func, "_parslet_protected", False
            )
            if existing_protected and not _ALLOW_REDEFINE:
                raise ValueError(
                    f"Task '{task_name}' is protected and already defined. Use --force-redefine to override."
                )
            if existing_protected and _ALLOW_REDEFINE:
                logger.warning(
                    "Force redefining protected Parslet task '%s'.",
                    task_name,
                )
            else:
                logger.warning(
                    "Parslet task '%s' is being redefined. Ensure this is intended.",
                    task_name,
                )
        _TASK_REGISTRY[task_name] = func_to_wrap

        # Attach metadata to the original function object for potential inspection,
        # though this is not heavily used by the current core logic.
        func_to_wrap._parslet_task_name = task_name  # type: ignore[attr-defined]
        func_to_wrap._parslet_dependencies = (  # type: ignore[attr-defined]
            dependencies if dependencies is not None else []
        )
        func_to_wrap._parslet_protected = protected  # type: ignore[attr-defined]
        func_to_wrap._parslet_battery_sensitive = battery_sensitive  # type: ignore[attr-defined]

        @functools.wraps(func_to_wrap)
        def wrapper(*args: Any, **kwargs: Any) -> ParsletFuture:
            """
            This wrapper is what's actually called when a @parslet_task-decorated
            function is invoked. It constructs and returns a ParsletFuture.
            """
            # Generate a unique ID for this specific invocation of the task.
            # This ensures that even if the same function is called multiple times
            # with different arguments, each call results in a unique task node in the DAG.
            # Format: "task_name_uuid_hex_short"
            unique_task_id = f"{task_name}_{uuid.uuid4().hex[:8]}"

            # Create the ParsletFuture object, capturing the original function,
            # its arguments, and this unique task ID.
            future_instance = ParsletFuture(
                task_id=unique_task_id,
                func=func_to_wrap,  # The original, undecorated function
                args=args,
                kwargs=kwargs,
            )

            # self.logger.debug(f"Parslet task '{task_name}' called. Returning future: {future_instance.task_id}")
            return future_instance

        # Store references to the original function and its Parslet metadata on the wrapper itself.
        # This can be useful for introspection or if the DAG builder needs to access
        # the original function or its defined task name.
        wrapper._parslet_original_func = func_to_wrap  # type: ignore[attr-defined]
        wrapper._parslet_task_name = task_name  # type: ignore[attr-defined]
        wrapper._parslet_dependencies = func_to_wrap._parslet_dependencies  # type: ignore[attr-defined]
        wrapper._parslet_protected = protected  # type: ignore[attr-defined]
        wrapper._parslet_battery_sensitive = battery_sensitive  # type: ignore[attr-defined]

        return wrapper

    # This logic handles whether the decorator is used as @parslet_task or @parslet_task(...)
    if _func is None:
        # Decorator called with arguments (e.g., @parslet_task(name="foo"))
        # Return the decorator itself, which will then be called with the function.
        return decorator_parslet_task
    else:
        # Decorator called without arguments (e.g., @parslet_task)
        # Apply the decorator directly to the function.
        return decorator_parslet_task(_func)


# --- Helper functions for registry interaction (mostly for potential future use or debugging) ---


def get_task_from_registry(task_name: str) -> Optional[Callable[..., Any]]:
    """
    Retrieves a task function from the global task registry by its name.

    Note: Parslet primarily operates on direct function references passed to
    `ParsletFuture`. This registry is more for potential introspection or
    alternative ways of defining/linking tasks by name.

    Args:
        task_name (str): The registered name of the task.

    Returns:
        Optional[Callable[..., Any]]: The callable task function if found, else None.
    """
    return _TASK_REGISTRY.get(task_name)


def set_allow_redefine(flag: bool) -> None:
    """Enable or disable overriding of protected tasks."""
    global _ALLOW_REDEFINE
    _ALLOW_REDEFINE = flag


def get_all_registered_tasks() -> Dict[str, Callable[..., Any]]:
    """
    Returns a copy of the global task registry.

    Returns:
        Dict[str, Callable[..., Any]]: A dictionary mapping registered task names
                                       to their callable functions.
    """
    return _TASK_REGISTRY.copy()
