import logging

import pytest

from parslet import parslet_task
from parslet.core import DAG, DAGRunner


def test_failure_log_contains_task_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    @parslet_task
    def boom() -> None:
        raise FileNotFoundError("missing")

    fut = boom()
    dag = DAG()
    dag.build_dag([fut])
    runner = DAGRunner()
    with caplog.at_level(logging.ERROR):
        runner.run(dag)
    assert fut.task_id in caplog.text
    assert "boom" in caplog.text
