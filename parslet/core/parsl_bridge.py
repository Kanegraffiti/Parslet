"""Parsl compatibility helpers for Parslet.

Public API: :func:`convert_task_to_parsl` and :func:`execute_with_parsl`.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import os
import tempfile

from .dag import DAG
from .task import ParsletFuture


__all__ = ["convert_task_to_parsl", "execute_with_parsl"]


def convert_task_to_parsl(parslet_func):
    """Wrap a Parslet task function as a Parsl ``python_app``.

    This requires the ``parsl`` package to be installed. The returned
    function behaves like the original Parslet task but executes under
    Parsl's DataFlowKernel when called.
    """
    try:
        from parsl import python_app
    except Exception as exc:  # ImportError or other
        raise ImportError(
            "Parsl is required for Parslet-Parsl interoperability.\n"
            "Install it via `pip install parsl`."
        ) from exc

    @python_app
    def parsl_task(*args, **kwargs):
        return parslet_func(*args, **kwargs)

    return parsl_task


def execute_with_parsl(
    entry_futures: List[ParsletFuture],
    parsl_config: Optional[Any] = None,
    *,
    run_dir: Optional[str] = None,
) -> List[Any]:
    """Execute a Parslet workflow using Parsl's runtime.

    ``entry_futures`` should be the same list returned by your workflow's
    ``main()`` function. This helper builds the Parslet ``DAG`` and then
    schedules each task as a Parsl ``python_app`` in topological order.

    Parameters
    ----------
    entry_futures:
        Terminal futures from the workflow's ``main()`` function.
    parsl_config:
        Optional ``parsl.config.Config`` instance. If not provided, a simple
        local threads configuration is used.
    run_dir:
        Optional path for Parsl's ``run_dir``. If not supplied, a temporary
        directory is created. A unique run directory helps avoid the hanging
        behavior reported in Parsl issue #3874 when multiple executors are
        launched sequentially within the same process.
    """
    try:
        import parsl
        from parsl.config import Config
        from parsl.executors.threads import ThreadPoolExecutor
    except Exception as exc:
        raise ImportError(
            "Parsl must be installed to run a Parslet workflow via Parsl."
        ) from exc

    parsl.clear()

    # Disable Parsl usage tracking by default. This avoids hangs on shutdown
    # observed when telemetry is enabled in some environments
    # (see Parsl issue #3831).
    os.environ.setdefault("PARSL_TELEMETRY_ENABLED", "false")

    if parsl_config is None:
        parsl_config = Config(executors=[ThreadPoolExecutor(label="local")])

    if run_dir is None:
        run_dir = tempfile.mkdtemp(prefix="parslet-parsl-")
    if getattr(parsl_config, "run_dir", None) is None:
        parsl_config.run_dir = run_dir

    parsl.load(parsl_config)

    dag = DAG()
    dag.build_dag(entry_futures)
    dag.validate_dag()

    order = dag.get_execution_order()
    parsl_futures: Dict[str, Any] = {}

    for task_id in order:
        pf = dag.get_task_future(task_id)
        parsl_app = convert_task_to_parsl(pf.func)

        resolved_args = [
            parsl_futures[a.task_id] if isinstance(a, ParsletFuture) else a
            for a in pf.args
        ]
        resolved_kwargs = {
            k: parsl_futures[v.task_id] if isinstance(v, ParsletFuture) else v
            for k, v in pf.kwargs.items()
        }

        parsl_futures[task_id] = parsl_app(*resolved_args, **resolved_kwargs)

    results = [parsl_futures[f.task_id].result() for f in entry_futures]
    parsl.dfk().cleanup()
    return results
