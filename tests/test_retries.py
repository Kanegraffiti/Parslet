from parslet.core import DAG, DAGRunner, parslet_task


def test_task_retries_then_succeeds() -> None:
    attempts = {"n": 0}

    @parslet_task(retries=2)
    def flaky() -> int:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("temporary")
        return 42

    fut = flaky()
    dag = DAG()
    dag.build_dag([fut])
    runner = DAGRunner(max_workers=1)
    runner.run(dag)
    assert fut.result() == 42
    assert attempts["n"] == 3
