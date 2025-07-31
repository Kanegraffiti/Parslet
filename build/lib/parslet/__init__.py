"""Parslet subpackage."""

from .core import (
    parslet_task,
    ParsletFuture,
    DAG,
    DAGCycleError,
    DAGRunner,
    UpstreamTaskFailedError,
    BatteryLevelLowError,
    AdaptiveScheduler,
    convert_task_to_parsl,
    execute_with_parsl,
    set_allow_redefine,
    export_dag_to_json,
    import_dag_from_json,
)
from .hybrid import execute_hybrid, FileRelay

try:
    from importlib.metadata import version as _pkg_version
except Exception:  # pragma: no cover
    from importlib_metadata import version as _pkg_version  # type: ignore

try:
    __version__ = _pkg_version("parslet")
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "parslet_task",
    "ParsletFuture",
    "DAG",
    "DAGCycleError",
    "DAGRunner",
    "UpstreamTaskFailedError",
    "BatteryLevelLowError",
    "AdaptiveScheduler",
    "convert_task_to_parsl",
    "execute_with_parsl",
    "set_allow_redefine",
    "export_dag_to_json",
    "import_dag_from_json",
    "execute_hybrid",
    "FileRelay",
]
