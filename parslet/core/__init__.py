"""Public exports for Parslet core primitives.

This module defines the long-term stable API surface of ``parslet.core``.
"""

from importlib import metadata

from .concierge import ConciergeOrchestrator, ConciergeSummary  # noqa: F401
from .context import ContextOracle, ContextResult  # noqa: F401
from .dag import DAG, DAGCycleError  # noqa: F401
from .dag_io import export_dag_to_json, import_dag_from_json  # noqa: F401
from .ir import IRGraph, IRTask, infer_edges_from_params, normalize_names, toposort
from .parsl_bridge import convert_task_to_parsl  # noqa: F401
from .parsl_bridge import execute_with_parsl, parsl_python
from .policy import AdaptivePolicy, EnergyAwarePolicy  # noqa: F401
from .runner import DAGRunner  # noqa: F401
from .runner import BatteryLevelLowError, UpstreamTaskFailedError
from .scheduler import AdaptiveScheduler  # noqa: F401
from .task import parslet_task  # noqa: F401
from .task import ParsletFuture, set_allow_redefine, task_variant

try:
    __version__ = metadata.version("parslet")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "parslet_task",
    "ParsletFuture",
    "DAG",
    "DAGRunner",
    "BatteryLevelLowError",
    "UpstreamTaskFailedError",
    "AdaptivePolicy",
    "EnergyAwarePolicy",
    "AdaptiveScheduler",
    "ContextOracle",
    "ContextResult",
    "ConciergeOrchestrator",
    "ConciergeSummary",
    "set_allow_redefine",
    "task_variant",
    "convert_task_to_parsl",
    "execute_with_parsl",
    "parsl_python",
    "IRTask",
    "IRGraph",
    "infer_edges_from_params",
    "toposort",
    "normalize_names",
]
