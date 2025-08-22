"""Graph construction and validation for Parslet workflows.

Public API: :class:`DAG` for representing task graphs and
``DAGCycleError`` when a cycle is detected.
"""

import networkx as nx
from typing import List, Dict, Set
from pathlib import Path
from collections import deque
import logging

from .task import ParsletFuture
from .exporter import (
    save_dag_to_png,
    PydotImportError,
    GraphvizExecutableNotFoundError,
)

__all__ = ["DAG", "DAGCycleError"]

logger = logging.getLogger(__name__)


class DAGCycleError(ValueError):
    """
    Custom exception raised when a cycle is detected in the task
    dependency graph.

    This error indicates that the defined task dependencies form a circular
    loop, making it impossible to determine a valid execution order. The
    error message often includes the tasks involved in the cycle if they
    can be determined.
    """

    pass


class DAG:
    """
    Represents a Directed Acyclic Graph (DAG) of Parslet tasks.

    This class is responsible for constructing the task graph based on
    declared dependencies between `ParsletFuture` objects. Dependencies are
    established when one `ParsletFuture` is passed as an argument to the
    function call that generates another `ParsletFuture`.

    The DAG can be validated to check for structural issues, primarily cycles,
    and can provide a topological sort of tasks for execution by the
    `DAGRunner`.

    Attributes:
        graph (nx.DiGraph): A NetworkX directed graph representing the task
                            dependencies. Nodes are task IDs, and edges point
                            from a dependency to the task that depends on it.
        tasks (Dict[str, ParsletFuture]): A mapping from task IDs to their
                                         corresponding `ParsletFuture`
                                         objects.
    """

    def __init__(self) -> None:
        """
        Initializes an empty DAG.

        The graph is stored as a NetworkX DiGraph, and task futures are stored
        in a dictionary.
        """
        self.graph: nx.DiGraph = nx.DiGraph()
        # Maps task_id (str) to ParsletFuture instances.
        self.tasks: Dict[str, ParsletFuture] = {}

    def add_task(self, future: ParsletFuture) -> None:
        """
        (Deprecated or Internal) Adds a single task and its dependencies
        recursively.

        Note: This method was part of an earlier graph construction approach.
        The current primary method for graph construction is `build_dag`,
        which uses an iterative approach. This method might be removed or
        refactored.

        If the task (identified by `future.task_id`) is already in the DAG,
        the method returns early. Otherwise, it adds the task as a node and
        then inspects its `args` and `kwargs` for other `ParsletFuture`
        instances. If dependencies are found, they are added to the graph
        first (recursively), and then directed edges are added from each
        dependency to the current task.

        Args:
            future (ParsletFuture): The ParsletFuture object representing the
            task to add.
        """
        # Check if the task has already been added to avoid redundant
        # processing or cycles in this recursive addition (though build_dag
        # is preferred now).
        if future.task_id in self.tasks:
            return

        # Add the current task as a node in the graph.
        # The 'future_obj' attribute stores the actual ParsletFuture.
        self.graph.add_node(future.task_id, future_obj=future)
        self.tasks[future.task_id] = future

        # Collect all ParsletFuture instances from the task's arguments and
        # keyword arguments. These represent the direct dependencies of the
        # current task.
        dependencies_found: List[ParsletFuture] = []
        for arg in future.args:
            if isinstance(arg, ParsletFuture):
                dependencies_found.append(arg)
        for kwarg_value in future.kwargs.values():
            if isinstance(kwarg_value, ParsletFuture):
                dependencies_found.append(kwarg_value)

        # For each dependency found, ensure it's in the graph and then add
        # an edge.
        for dep_future in dependencies_found:
            # If a dependency hasn't been added yet, recursively call add_task
            # for it.
            if dep_future.task_id not in self.tasks:
                self.add_task(dep_future)

            # Add a directed edge from the dependency task to the current task.
            # This signifies that `dep_future` must complete before `future`.
            self.graph.add_edge(dep_future.task_id, future.task_id)

    def build_dag(self, entry_futures: List[ParsletFuture]) -> None:
        """
        Builds the DAG from a list of "entry" ParsletFuture objects.

        Entry futures are typically the terminal tasks of a workflow
        (tasks whose results are desired directly). This method performs a
        breadth-first traversal starting from these entry futures, exploring
        backward along dependencies (as ParsletFuture objects are passed as
        arguments). All discovered tasks are added as nodes, and edges are
        created to represent dependencies.

        Args:
            entry_futures (List[ParsletFuture]): A list of ParsletFuture
            objects that are part of the workflow. These often
            represent the final outputs or key checkpoints of the DAG.
        """
        # Queue for BFS-like traversal of futures and their dependencies.
        queue = deque(entry_futures)
        # Set to keep track of futures whose dependencies have been processed
        # or added to queue.
        visited_futures_for_processing: Set[str] = set()

        while queue:
            current_future = queue.popleft()

            if current_future.task_id in visited_futures_for_processing:
                continue  # Already processed or in queue

            visited_futures_for_processing.add(current_future.task_id)

            # Ensure the current future is registered as a task
            # and a graph node.
            if current_future.task_id not in self.tasks:
                self.graph.add_node(current_future.task_id, future_obj=current_future)
                self.tasks[current_future.task_id] = current_future

            # Discover dependencies from args and kwargs.
            # If a dependency is a ParsletFuture, ensure it's added to the
            # graph and to the processing queue if not already visited.
            # Then, add an edge from the dependency to the current_future.

            dependencies_to_explore: List[ParsletFuture] = []
            for arg in current_future.args:
                if isinstance(arg, ParsletFuture):
                    dependencies_to_explore.append(arg)
            for kwarg_value in current_future.kwargs.values():
                if isinstance(kwarg_value, ParsletFuture):
                    dependencies_to_explore.append(kwarg_value)

            for dep_future in dependencies_to_explore:
                # Add dependency as a task and graph node if it's new.
                if dep_future.task_id not in self.tasks:
                    self.graph.add_node(dep_future.task_id, future_obj=dep_future)
                    self.tasks[dep_future.task_id] = dep_future

                # Add an edge from the dependency to the current task.
                self.graph.add_edge(dep_future.task_id, current_future.task_id)

                # If this dependency hasn't been processed, add it to the
                # queue.
                if dep_future.task_id not in visited_futures_for_processing:
                    queue.append(dep_future)

    def validate_dag(self) -> None:
        """
        Validates the DAG structure, primarily checking for cycles.

        If the graph is empty, validation is considered successful
        (vacuously true). Uses NetworkX's `is_directed_acyclic_graph` to
        check for cycles. If a cycle is found, it attempts to find and
        include the cycle path in the raised `DAGCycleError`.

        Raises:
            DAGCycleError: If a cycle is detected in the graph. The error
            message may include the nodes forming the cycle.
        """
        if not self.graph.nodes:
            # An empty graph is trivially acyclic.
            return

        if not nx.is_directed_acyclic_graph(self.graph):
            cycle_info = "A cycle was detected."  # Default message
            try:
                # Attempt to find the specific cycle for a more informative
                # error. nx.find_cycle returns a list of edges forming a cycle.
                cycle_edges = nx.find_cycle(self.graph, orientation="original")

                path_str = ""
                if cycle_edges:
                    # Extract nodes from the cycle edges to form a path string
                    # like "A -> B -> C -> A"
                    temp_nodes = [
                        cycle_edges[0][0]
                    ]  # Start with the first node of the first edge
                    for (
                        u,
                        v,
                        _,
                    ) in cycle_edges:  # u=source, v=target, _=edge_data_dict
                        if v not in temp_nodes:
                            temp_nodes.append(v)
                        else:  # Cycle closes
                            temp_nodes.append(v)
                            break
                    path_str = " -> ".join(temp_nodes)

                if path_str:
                    cycle_info = f"Cycle detected involving tasks: {path_str}."
            except nx.NetworkXNoCycle:
                # This case should ideally not be reached if
                # is_directed_acyclic_graph was false. It's a defensive
                # measure.
                cycle_info = (
                    "A cycle was detected, but could not "
                    "determine the specific tasks involved."
                )

            raise DAGCycleError(f"Task dependency graph is invalid. {cycle_info}")

    def get_execution_order(self) -> List[str]:
        """
        Performs a topological sort on the DAG to get a valid execution
        order of task IDs.

        Tasks with no dependencies will appear earlier in the list. The order
        respects all defined dependencies, meaning a task will only appear
        after all its prerequisite tasks have appeared.

        Returns:
            List[str]: A list of task IDs (strings) in a valid execution order.
                       Returns an empty list if the DAG is empty.

        Raises:
            DAGCycleError: If the graph contains cycles (re-raised from
            `validate_dag` if `nx.topological_sort` fails due to cycles).
            RuntimeError: If an unexpected graph state leads to failure in
            sorting despite passing cycle validation (highly unlikely).
        """
        if not self.graph.nodes:
            return []  # No tasks to order in an empty graph.

        try:
            # nx.topological_sort returns a generator, so convert it to a list.
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            # This exception is raised by NetworkX if the graph has a cycle,
            # making topological sort impossible.
            # We call validate_dag() again to raise our specific DAGCycleError
            # with potentially more cycle details.
            self.validate_dag()
            # If validate_dag didn't raise (which it should have),
            # then something is very wrong.
            raise RuntimeError(
                "Failed to get execution order due to an unexpected graph "
                "state that passed cycle validation."
            )

    def get_task_future(self, task_id: str) -> ParsletFuture:
        """
        Retrieves the `ParsletFuture` object for a given task ID.

        Args:
            task_id (str): The unique ID of the task.

        Returns:
            ParsletFuture: The `ParsletFuture` object associated with the
            task ID.

        Raises:
            KeyError: If the `task_id` is not found in the DAG's registered
            tasks.
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task ID '{task_id}' not found in the DAG's task registry.")
        return self.tasks[task_id]

    def get_dependencies(self, task_id: str) -> List[str]:
        """
        Returns a list of task IDs that are direct dependencies (predecessors)
        of the specified task.

        Args:
            task_id (str): The ID of the task whose dependencies are to be
            retrieved.

        Returns:
            List[str]: A list of task IDs of direct dependencies.

        Raises:
            KeyError: If the `task_id` is not found in the DAG graph.
        """
        if task_id not in self.graph:  # Check node existence in the graph
            raise KeyError(f"Task ID '{task_id}' not found in the DAG graph.")
        return list(self.graph.predecessors(task_id))

    def get_dependents(self, task_id: str) -> List[str]:
        """
        Returns a list of task IDs that directly depend on (are successors of)
        the specified task.

        Args:
            task_id (str): The ID of the task whose dependents are to be
            retrieved.

        Returns:
            List[str]: A list of task IDs of direct dependents.

        Raises:
            KeyError: If the `task_id` is not found in the DAG graph.
        """
        if task_id not in self.graph:  # Check node existence in the graph
            raise KeyError(f"Task ID '{task_id}' not found in the DAG graph.")
        return list(self.graph.successors(task_id))

    def draw_dag(self, ascii_only: bool = True, filepath: str | None = None) -> str:
        """Return a simple visualisation of the DAG.

        If ``ascii_only`` is True or Graphviz is not available, an ASCII
        representation is returned.  Otherwise, a Graphviz DOT string is
        produced and optionally written to ``filepath``.
        """
        try:
            import pydot  # noqa: F401
        except Exception:  # pragma: no cover - optional dependency
            ascii_only = True

        if ascii_only:
            lines = []
            for node in nx.topological_sort(self.graph):
                deps = list(self.graph.predecessors(node))
                if deps:
                    lines.append(f"{node} <- {', '.join(deps)}")
                else:
                    lines.append(f"{node}")
            ascii_dag = "\n".join(lines)
            if filepath:
                Path(filepath).write_text(ascii_dag)
            return ascii_dag

        dot = nx.nx_pydot.to_pydot(self.graph)
        dot_str = dot.to_string()
        if filepath:
            Path(filepath).write_text(dot_str)
        return dot_str

    def save_png(self, filepath: str) -> None:
        """
        Saves a PNG visualization of the DAG to the specified filepath.

        This method uses the `save_dag_to_png` utility from the exporter
        module.
        It handles potential errors gracefully by logging them without
        crashing.

        Args:
            filepath (str): The path where the PNG image will be saved.
        """
        try:
            save_dag_to_png(self, filepath)
        except (PydotImportError, GraphvizExecutableNotFoundError) as e:
            # These are expected errors if dependencies are missing.
            # Log them as warnings and re-raise to be handled by the CLI.
            logger.warning(f"Could not generate DAG image: {e}")
            logger.warning(
                "Please ensure pydot and Graphviz are installed and in your "
                "system's PATH."
            )
            raise
        except Exception as e_generic:
            # Catch any other unexpected errors during image generation.
            logger.error(
                "An unexpected error occurred while saving the DAG image: %s",
                e_generic,
                exc_info=True,
            )
            raise

    def all_tasks_and_dependencies_known(
        self, entry_futures: List[ParsletFuture]
    ) -> bool:
        """
        (Utility/Debug) Checks if all futures reachable from `entry_futures`
        (including transitive dependencies in their args/kwargs) are known
        to this DAG instance (i.e., present in `self.tasks`).

        This method is for internal checks or debugging to ensure that
        the graph construction process has successfully registered all
        relevant tasks.

        Args:
            entry_futures (List[ParsletFuture]): A list of `ParsletFuture`
            objects to start the reachability check from.

        Returns:
            bool: True if all reachable futures are known to the DAG,
            False otherwise.
        """
        queue = deque(entry_futures)
        visited_ids: Set[str] = set()  # Tracks futures visited during this check

        while queue:
            current_future = queue.popleft()
            if current_future.task_id in visited_ids:
                continue
            visited_ids.add(current_future.task_id)

            # Check if the current future is registered in the DAG's task map.
            if current_future.task_id not in self.tasks:
                return False  # Found an unknown future

            # Add its ParsletFuture dependencies to the queue for checking.
            for arg in current_future.args:
                if isinstance(arg, ParsletFuture):
                    if arg.task_id not in visited_ids:
                        queue.append(arg)
        for kwarg_value in current_future.kwargs.values():
            if isinstance(kwarg_value, ParsletFuture):
                if kwarg_value.task_id not in visited_ids:
                    queue.append(kwarg_value)
        return True  # All reachable futures are known
