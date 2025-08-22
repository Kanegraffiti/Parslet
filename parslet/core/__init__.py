"""Public exports for Parslet core primitives."""

from importlib import metadata

from .dag import DAG, DAGCycleError  # noqa: F401
from .dag_io import export_dag_to_json, import_dag_from_json  # noqa: F401
from .parsl_bridge import convert_task_to_parsl, execute_with_parsl  # noqa: F401
from .runner import (
    BatteryLevelLowError,  # noqa: F401
    DAGRunner,
    UpstreamTaskFailedError,  # noqa: F401
)
from .scheduler import AdaptiveScheduler  # noqa: F401
from .task import ParsletFuture, parslet_task, set_allow_redefine  # noqa: F401

try:
    __version__ = metadata.version("parslet")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["parslet_task", "ParsletFuture", "DAG", "DAGRunner"]
