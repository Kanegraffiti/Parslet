"""Intermediate representation for Parslet/Parsl interoperability.

This module defines a very small, lossless representation for task graphs
used by the experimental Parsl ↔ Parslet converters.  The structures are
kept intentionally light‑weight so that they can also operate in constrained
Termux environments where heavy dependencies are undesirable.

The IR is intentionally opinionated but designed to be good enough for
round‑trip conversions during testing.  It is *not* a replacement for the
full DAG classes used by Parslet itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple, Set


@dataclass
class IRTask:
    """Representation of a single task in the interoperability graph."""

    name: str
    params: List[str]
    returns: List[str] | None = None
    body_ref: str | None = None
    resources: Dict[str, Any] | None = None
    retries: int | None = None
    cache_key: str | None = None
    metadata: Dict[str, Any] | None = None


@dataclass
class IRGraph:
    """Container for a task graph used in conversions."""

    tasks: Dict[str, IRTask]
    edges: List[Tuple[str, str]] = field(default_factory=list)
    artifacts: Dict[str, Any] | None = None
    policies: Dict[str, Any] | None = None


def infer_edges_from_params(tasks: Dict[str, IRTask]) -> List[Tuple[str, str]]:
    """Derive graph edges by inspecting task parameter references.

    The helper assumes that if a parameter name matches another task name the
    latter is a dependency of the former.  It is purposely conservative –
    callers can override the result with explicit edges if necessary.
    """

    edges: List[Tuple[str, str]] = []
    for task in tasks.values():
        for param in task.params:
            if param in tasks:
                edges.append((param, task.name))
    return edges


def toposort(tasks: Dict[str, IRTask], edges: Iterable[Tuple[str, str]]) -> List[str]:
    """Topologically sort ``tasks`` given an iterable of ``edges``.

    A ``ValueError`` is raised if a cycle is detected.  The algorithm is a
    tiny implementation of Kahn's method and is sufficient for the unit tests
    shipped with this repository.
    """

    graph: Dict[str, Set[str]] = {name: set() for name in tasks}
    for dep, node in edges:
        graph[node].add(dep)

    result: List[str] = []
    ready = [name for name, deps in graph.items() if not deps]

    while ready:
        node = ready.pop()
        result.append(node)
        for other, deps in graph.items():
            if node in deps:
                deps.remove(node)
                if not deps:
                    ready.append(other)

    if len(result) != len(tasks):
        raise ValueError("Cycle detected in IRGraph")

    return result


def normalize_names(tasks: Dict[str, IRTask]) -> Dict[str, IRTask]:
    """Ensure task names are unique by appending numeric suffixes.

    The function mutates the supplied ``IRTask`` instances and returns a new
    dictionary keyed by the normalized names.
    """

    seen: Set[str] = set()
    new_tasks: Dict[str, IRTask] = {}

    for original_key, task in tasks.items():
        base = task.name or original_key
        candidate = base
        i = 1
        while candidate in seen:
            candidate = f"{base}_{i}"
            i += 1
        seen.add(candidate)
        task.name = candidate
        new_tasks[candidate] = task

    return new_tasks


__all__ = [
    "IRTask",
    "IRGraph",
    "infer_edges_from_params",
    "toposort",
    "normalize_names",
]
