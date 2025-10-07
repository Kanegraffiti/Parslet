from __future__ import annotations

import pytest

from parslet.core import ContextOracle, DAG, DAGRunner, parslet_task
from parslet.core.runner import ContextNotSatisfiedError


def test_context_oracle_manual_enable() -> None:
    oracle = ContextOracle(["studio"])
    allowed, results = oracle.evaluate(["studio"])
    assert allowed
    assert results[0].origin == "manual"


def test_context_oracle_battery_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("parslet.core.context.get_battery_level", lambda: 82)
    oracle = ContextOracle()
    allowed, _ = oracle.evaluate(["battery>=60"])
    assert allowed

    monkeypatch.setattr("parslet.core.context.get_battery_level", lambda: 18)
    allowed, details = oracle.evaluate(["battery>=60"])
    assert not allowed
    assert details[0].origin == "battery"


def test_runner_defers_and_honours_context(monkeypatch: pytest.MonkeyPatch) -> None:
    executions: list[str] = []

    @parslet_task(name="concierge_task", contexts=["atelier"], allow_redefine=True)
    def gated_task() -> str:
        executions.append("ran")
        return "opulent"

    # Without context the task should be deferred.
    dag = DAG()
    fut = gated_task()
    dag.build_dag([fut])
    runner = DAGRunner(context_oracle=ContextOracle())
    runner.run(dag)
    assert runner.task_statuses[fut.task_id] == "DEFERRED"
    with pytest.raises(ContextNotSatisfiedError):
        fut.result()
    assert executions == []

    # When the context is enabled manually the task should execute.
    dag_ok = DAG()
    fut_ok = gated_task()
    dag_ok.build_dag([fut_ok])
    runner_ok = DAGRunner(context_oracle=ContextOracle(["atelier"]))
    runner_ok.run(dag_ok)
    assert runner_ok.task_statuses[fut_ok.task_id] == "SUCCESS"
    assert executions == ["ran"]
