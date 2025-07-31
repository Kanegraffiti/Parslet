"""
Parslet Core Package
--------------------

This package provides the core components for defining, managing, and executing
task-based workflows (DAGs).

Key components exposed:
- `@parslet_task`: Decorator to define a function as a Parslet task.
- `ParsletFuture`: Object representing the future result of a task.
- `DAG`: Class to build and manage the Directed Acyclic Graph of tasks.
- `DAGCycleError`: Exception raised when a cycle is detected in the DAG.
- `DAGRunner`: Class to execute tasks in a DAG.
- `UpstreamTaskFailedError`: Exception raised when a task cannot run due to
  the failure of one of its dependencies.

Future components (to be added):
- Functions for exporting DAGs (e.g., to JSON, DOT).
- Functions for visualizing DAGs (e.g., ASCII art).
"""

# Import key components from the .task module
from .task import parslet_task, ParsletFuture, set_allow_redefine

# Import key components from the .dag module
from .dag import DAG, DAGCycleError

# Import key components from the .runner module
from .runner import DAGRunner, UpstreamTaskFailedError, BatteryLevelLowError

try:
    from importlib.metadata import version as _pkg_version
except ImportError:  # pragma: no cover - Python <3.8
    from importlib_metadata import version as _pkg_version  # type: ignore

try:
    __version__ = _pkg_version("parslet")
except Exception:
    __version__ = "0.0.0"
from .scheduler import AdaptiveScheduler
from .parsl_bridge import convert_task_to_parsl, execute_with_parsl
from .dag_io import export_dag_to_json, import_dag_from_json

# Placeholder for imports from .exporter module (once implemented)
# from .exporter import export_dag_to_json, export_dag_to_dot

# Placeholder for imports from .visualization module (once implemented)
# from .visualization import visualize_dag_ascii

# You can define __all__ to specify what gets imported with 'from parslet.core import *'
# For explicit imports like 'from parslet.core import DAG', __all__ is not strictly necessary
# but can be good practice.
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
]
