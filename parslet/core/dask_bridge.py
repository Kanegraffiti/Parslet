"""Dask compatibility helpers for Parslet.

Public API: :func:`execute_with_dask` to run a workflow via Dask.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Union

from .dag import DAG
from .task import ParsletFuture


__all__ = ["execute_with_dask"]


def execute_with_dask(
    entry_futures: List[ParsletFuture],
    scheduler: Optional[Union[str, Any]] = None,
) -> List[Any]:
    """Execute a Parslet workflow using Dask.

    Parameters
    ----------
    entry_futures:
        Terminal futures from the workflow's ``main()`` function.
    scheduler:
        Optional scheduler specification passed to :func:`dask.compute`.
        This may be a string such as ``"threads"`` or ``"processes"`` or
        a ``dask.distributed.Client`` instance.  If ``None`` a threaded
        scheduler is used.

    Examples
    --------
    >>> from parslet.core import parslet_task
    >>> from parslet.core.dask_bridge import execute_with_dask
    >>> @parslet_task
    ... def inc(x):
    ...     return x + 1
    >>> futures = [inc(1)]
    >>> execute_with_dask(futures)
    [2]
    """
    try:
        from dask import delayed, compute

        try:
            from dask.distributed import Client
        except Exception:  # pragma: no cover - distributed optional
            Client = None  # type: ignore
    except Exception as exc:  # pragma: no cover - dask not installed
        raise ImportError(
            "Dask must be installed to run a Parslet workflow via Dask."
        ) from exc

    dag = DAG()
    dag.build_dag(entry_futures)
    dag.validate_dag()

    order = dag.get_execution_order()
    dask_futures: Dict[str, Any] = {}

    for task_id in order:
        pf = dag.get_task_future(task_id)
        dask_task = delayed(pf.func)

        resolved_args = [
            dask_futures[a.task_id] if isinstance(a, ParsletFuture) else a
            for a in pf.args
        ]
        resolved_kwargs = {
            k: dask_futures[v.task_id] if isinstance(v, ParsletFuture) else v
            for k, v in pf.kwargs.items()
        }

        dask_futures[task_id] = dask_task(*resolved_args, **resolved_kwargs)

    entry_tasks = [dask_futures[f.task_id] for f in entry_futures]

    if scheduler is None:
        scheduler = "threads"

    if "Client" in locals() and Client is not None and isinstance(scheduler, Client):
        futures = [scheduler.compute(t) for t in entry_tasks]
        results = scheduler.gather(futures)
    else:
        results = compute(*entry_tasks, scheduler=scheduler)

    return list(results)
