"""Public exports for Parslet core primitives.

This module defines the long-term stable API surface of ``parslet.core``.
"""

from importlib import metadata

from .dag import DAG, DAGCycleError  # noqa: F401
from .dag_io import (  # noqa: F401
    export_dag_to_json,
    import_dag_from_json,
)
from .parsl_bridge import (  # noqa: F401
    convert_task_to_parsl,
    execute_with_parsl,
)
from .policy import AdaptivePolicy  # noqa: F401
from .runner import (  # noqa: F401
    BatteryLevelLowError,
    DAGRunner,
    UpstreamTaskFailedError,
)
from .scheduler import AdaptiveScheduler  # noqa: F401
from .task import ParsletFuture, parslet_task, set_allow_redefine  # noqa: F401

try:
    __version__ = metadata.version("parslet")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "parslet_task",
    "ParsletFuture",
    "DAG",
    "DAGRunner",
    "AdaptivePolicy",
    "AdaptiveScheduler",
]
