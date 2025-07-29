from parslet.core import DAG, DAGRunner, parslet_task
from parslet.core.runner import BatteryLevelLowError


@parslet_task(battery_sensitive=True)
def needs_power(x):
    return x * 2


def test_battery_sensitive_skipped(monkeypatch):
    def fake_batt():
        return 10

    monkeypatch.setattr("parslet.core.runner.get_battery_level", fake_batt)

    fut = needs_power(3)
    dag = DAG()
    dag.build_dag([fut])
    runner = DAGRunner(max_workers=1)
    runner.run(dag)
    assert isinstance(fut._exception, BatteryLevelLowError)
    assert runner.task_statuses[fut.task_id] == "SKIPPED"


def test_ignore_battery_runs(monkeypatch):
    def fake_batt():
        return 10

    monkeypatch.setattr("parslet.core.runner.get_battery_level", fake_batt)

    fut = needs_power(4)
    dag = DAG()
    dag.build_dag([fut])
    runner = DAGRunner(max_workers=1, ignore_battery=True)
    runner.run(dag)
    assert fut.result() == 8
    assert runner.task_statuses[fut.task_id] == "SUCCESS"
