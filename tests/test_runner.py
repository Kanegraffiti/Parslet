from parslet.core import DAG, DAGRunner, parslet_task


@parslet_task
def add(x, y):
    return x + y


def test_runner_executes_tasks():
    a = add(1, 2)
    dag = DAG()
    dag.build_dag([a])
    dag.validate_dag()
    runner = DAGRunner(max_workers=1)
    runner.run(dag)
    assert a.result() == 3
