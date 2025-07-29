from parslet.core import DAG, DAGRunner, parslet_task


@parslet_task
def fragile():
    if not getattr(fragile, "attempt", False):
        fragile.attempt = True
        raise MemoryError("boom")
    return 42


def test_failsafe_serial_execution():
    a = fragile()
    dag = DAG()
    dag.build_dag([a])
    dag.validate_dag()
    runner = DAGRunner(max_workers=2, failsafe_mode=True)
    runner.run(dag)
    assert a.result() == 42
    assert runner.task_statuses[a.task_id] == "SUCCESS"
