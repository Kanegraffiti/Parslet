"""Public exports for Parslet core primitives.

This module defines the long-term stable API surface of ``parslet.core``.
"""

from importlib import metadata

from .concierge import ConciergeOrchestrator, ConciergeSummary  # noqa: F401
from .context import ContextOracle, ContextResult  # noqa: F401
from .dag import DAG, DAGCycleError  # noqa: F401
from .dag_io import export_dag_to_json, import_dag_from_json  # noqa: F401
from .ir import IRGraph, IRTask, infer_edges_from_params, normalize_names, toposort
from .parsl_bridge import (
    convert_task_to_parsl,  # noqa: F401
    execute_with_parsl,
    parsl_python,
)
from .policy import (  # noqa: F401
    AdaptivePolicy,
    BatteryAwarePolicy,
    BatteryDecision,
    EnergyAwarePolicy,
)
from .runner import (
    BatteryLevelLowError,
    DAGRunner,  # noqa: F401
    UpstreamTaskFailedError,
)
from .scheduler import AdaptiveScheduler  # noqa: F401
from .task import (  # noqa: F401
    ParsletFuture,
    parslet_task,
    parslet_workflow,
    set_allow_redefine,
    task_variant,
)

try:
    __version__ = metadata.version("parslet")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "parslet_task",
    "parslet_workflow",
    "ParsletFuture",
    "DAG",
    "DAGRunner",
    "BatteryLevelLowError",
    "UpstreamTaskFailedError",
    "AdaptivePolicy",
    "EnergyAwarePolicy",
    "BatteryAwarePolicy",
    "BatteryDecision",
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
