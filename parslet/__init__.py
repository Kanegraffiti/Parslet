"""Public Parslet API surface.

Only a small set of names is re-exported here to keep the package's public
interface compact and easy to learn.  Everything else remains available under
``parslet.core`` or other subpackages.
"""

from .core import DAG, DAGRunner, ParsletFuture, parslet_task

try:
    from importlib.metadata import version as _pkg_version
except Exception:  # pragma: no cover
    from importlib_metadata import version as _pkg_version  # type: ignore

try:
    __version__ = _pkg_version("parslet")
except Exception:
    __version__ = "0.0.0"

__all__ = ["parslet_task", "ParsletFuture", "DAG", "DAGRunner"]
