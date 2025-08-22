from __future__ import annotations

import time
from pathlib import Path

import pytest

from parslet.core import DAG, DAGRunner
from parslet.core.task import parslet_task

calls: list[int] = []


@parslet_task(cache=True)
def slow_double(x: int) -> int:
    calls.append(x)
    time.sleep(0.1)
    return x * 2


def _run_once() -> float:
    dag = DAG()
    fut = slow_double(2)
    dag.build_dag([fut])
    runner = DAGRunner()
    start = time.perf_counter()
    runner.run(dag)
    duration = time.perf_counter() - start
    assert fut.result() == 4
    return duration


def test_task_caching(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PARSLET_CACHE_DIR", str(tmp_path))
    d1 = _run_once()
    assert calls == [2]
    d2 = _run_once()
    assert calls == [2]
    assert d2 < d1 / 5
