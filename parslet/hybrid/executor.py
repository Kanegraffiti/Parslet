"""Hybrid execution engine for Parslet.

This module provides a minimal helper to execute a Parslet workflow
partly on Parsl and partly on the local DAGRunner.  It is intended as a
starting point for more advanced federated orchestration.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..core import DAG, ParsletFuture
from ..core.parsl_bridge import convert_task_to_parsl


def execute_hybrid(
    entry_futures: List[ParsletFuture],
    parsl_config: Any | None = None,
) -> List[Any]:
    """Execute a workflow mixing local and Parsl-backed tasks.

    Tasks are automatically routed to the remote Parsl backend when they
    are defined with ``@parslet_task(remote=True)``.

    Parameters
    ----------
    entry_futures:
        List of terminal futures defining the workflow.
    parsl_config:
        Optional Parsl ``Config`` object for remote execution.

    Returns
    -------
    List[Any]
        Results for the given ``entry_futures`` in order.
    """
    try:
        import parsl
        from parsl.config import Config
        from parsl.executors.threads import ThreadPoolExecutor
    except Exception as exc:
        raise ImportError(
            "Parsl must be installed for hybrid execution"
        ) from exc

    parsl.clear()
    if parsl_config is None:
        parsl_config = Config(executors=[ThreadPoolExecutor(label="remote")])
    parsl.load(parsl_config)

    dag = DAG()
    dag.build_dag(entry_futures)
    dag.validate_dag()

    order = dag.get_execution_order()
    results: Dict[str, Any] = {}

    for task_id in order:
        pf = dag.get_task_future(task_id)
        resolved_args = [
            results[a.task_id] if isinstance(a, ParsletFuture) else a
            for a in pf.args
        ]
        resolved_kwargs = {
            k: results[v.task_id] if isinstance(v, ParsletFuture) else v
            for k, v in pf.kwargs.items()
        }

        if getattr(pf.func, "_parslet_remote", False):
            parsl_app = convert_task_to_parsl(pf.func)
            results[task_id] = parsl_app(
                *resolved_args, **resolved_kwargs
            ).result()
        else:
            results[task_id] = pf.func(*resolved_args, **resolved_kwargs)

    parsl.dfk().cleanup()
    return [results[f.task_id] for f in entry_futures]
