"""JSON serialization helpers for Parslet DAGs.

Public API: :func:`export_dag_to_json` and :func:`import_dag_from_json`.
"""

import json
import importlib
from typing import Any, Dict, List

from .dag import DAG
from .task import ParsletFuture


__all__ = ["export_dag_to_json", "import_dag_from_json"]


def _serialize_arg(arg: Any) -> Any:
    if isinstance(arg, ParsletFuture):
        return {"__future__": arg.task_id}
    return arg


def export_dag_to_json(dag: DAG, path: str) -> None:
    tasks: List[Dict[str, Any]] = []
    for task_id in dag.graph.nodes:
        future = dag.tasks[task_id]
        task_data = {
            "task_id": task_id,
            "module": future.func.__module__,
            "func_name": future.func.__name__,
            "task_name": getattr(
                future.func, "_parslet_task_name", future.func.__name__
            ),
            "battery_sensitive": getattr(
                future.func, "_parslet_battery_sensitive", False
            ),
            "protected": getattr(future.func, "_parslet_protected", False),
            "args": [_serialize_arg(a) for a in future.args],
            "kwargs": {k: _serialize_arg(v) for k, v in future.kwargs.items()},
            "dependencies": dag.get_dependencies(task_id),
        }
        tasks.append(task_data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks}, f, indent=2)


def _deserialize_arg(val: Any, task_map: Dict[str, ParsletFuture]) -> Any:
    if isinstance(val, dict) and "__future__" in val:
        return task_map[val["__future__"]]
    return val


def import_dag_from_json(path: str) -> DAG:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    tasks_data = data.get("tasks", [])
    task_map: Dict[str, ParsletFuture] = {}
    # First pass: create futures without args
    for t in tasks_data:
        module = importlib.import_module(t["module"])
        func = getattr(module, t["func_name"])
        if hasattr(func, "_parslet_original_func"):
            func = getattr(func, "_parslet_original_func")
        future = ParsletFuture(task_id=t["task_id"], func=func, args=(), kwargs={})
        task_map[t["task_id"]] = future
    # Second pass: assign args
    for t in tasks_data:
        future = task_map[t["task_id"]]
        future.args = tuple(_deserialize_arg(a, task_map) for a in t.get("args", []))
        future.kwargs = {
            k: _deserialize_arg(v, task_map) for k, v in t.get("kwargs", {}).items()
        }
    dag = DAG()
    dag.graph.add_nodes_from((tid, {"future_obj": f}) for tid, f in task_map.items())
    dag.tasks = task_map
    for t in tasks_data:
        for dep in t.get("dependencies", []):
            dag.graph.add_edge(dep, t["task_id"])
    return dag
