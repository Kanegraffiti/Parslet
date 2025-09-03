from parslet.core.ir import (
    IRTask,
    IRGraph,
    infer_edges_from_params,
    toposort,
    normalize_names,
)
import pytest


def test_infer_edges_and_toposort():
    t1 = IRTask(name="a", params=[], returns=["x"])
    t2 = IRTask(name="b", params=["a"], returns=None)
    tasks = {"a": t1, "b": t2}
    edges = infer_edges_from_params(tasks)
    assert edges == [("a", "b")]
    graph = IRGraph(tasks=tasks, edges=edges)
    order = toposort(graph.tasks, graph.edges)
    assert order == ["a", "b"]


def test_normalize_names():
    t1 = IRTask(name="dup", params=[])
    t2 = IRTask(name="dup", params=[])
    tasks = {"t1": t1, "t2": t2}
    new_tasks = normalize_names(tasks)
    assert len({task.name for task in new_tasks.values()}) == 2


def test_toposort_cycle_detection():
    t1 = IRTask(name="a", params=["b"])
    t2 = IRTask(name="b", params=["a"])
    tasks = {"a": t1, "b": t2}
    edges = infer_edges_from_params(tasks)
    with pytest.raises(ValueError):
        toposort(tasks, edges)
