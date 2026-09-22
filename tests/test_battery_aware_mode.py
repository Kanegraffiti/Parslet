import logging
from typing import Literal

import pytest
from _pytest.logging import LogCaptureFixture

from parslet.core import DAG, BatteryAwarePolicy, DAGRunner, parslet_task
from parslet.core.runner import BatteryPolicyDeferredError
from parslet.utils.power import PowerState


def state(
    source: Literal["battery", "ac", "unknown"] = "battery",
    percent: int | None = 50,
    charging: bool | None = False,
) -> PowerState:
    return PowerState(source=source, percent=percent, is_charging=charging)


def test_policy_power_bands_and_worker_limits() -> None:
    policy = BatteryAwarePolicy(low_battery_threshold=40, critical_battery_threshold=15)

    assert policy.band(state(source="ac", percent=5, charging=True)) == "ac"
    assert policy.band(state(percent=70)) == "normal"
    assert policy.band(state(percent=40)) == "low"
    assert policy.band(state(percent=15)) == "critical"
    assert policy.decide_max_workers(state(percent=40), 8) == 4
    assert policy.decide_max_workers(state(percent=15), 8) == 1
    assert policy.decide_max_workers(PowerState(), 8) == 8


def test_policy_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError, match="critical < low"):
        BatteryAwarePolicy(low_battery_threshold=15, critical_battery_threshold=15)


def test_low_battery_defers_only_expensive_best_effort_work() -> None:
    policy = BatteryAwarePolicy()

    @parslet_task(energy_cost="high", qos="best_effort", allow_redefine=True)
    def optional_render() -> str:
        return "rendered"

    @parslet_task(energy_cost="high", qos="high", allow_redefine=True)
    def urgent_upload() -> str:
        return "uploaded"

    assert not policy.decide_task(optional_render(), state(percent=30)).run
    assert policy.decide_task(urgent_upload(), state(percent=10)).run


def test_critical_battery_runs_light_tasks_and_defers_expensive_tasks(
    monkeypatch: pytest.MonkeyPatch, caplog: LogCaptureFixture
) -> None:
    monkeypatch.setattr(
        "parslet.core.runner.get_power_state", lambda: state(percent=10)
    )

    @parslet_task(energy_cost="low", allow_redefine=True)
    def light_task() -> str:
        return "done"

    @parslet_task(energy_cost="high", allow_redefine=True)
    def heavy_task() -> str:
        return "expensive"

    light = light_task()
    heavy = heavy_task()
    dag = DAG()
    dag.build_dag([light, heavy])

    with caplog.at_level(logging.WARNING):
        runner = DAGRunner(max_workers=4, battery_mode=True)
        runner.run(dag)

    assert light.result() == "done"
    assert isinstance(heavy._exception, BatteryPolicyDeferredError)
    assert runner.task_statuses[heavy.task_id] == "DEFERRED"
    assert runner.max_workers == 1
    assert "critical power band" in caplog.text


def test_charging_device_is_not_rationed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "parslet.core.runner.get_power_state",
        lambda: state(source="ac", percent=10, charging=True),
    )
    runner = DAGRunner(max_workers=4, battery_mode=True)
    assert runner.max_workers == 4
