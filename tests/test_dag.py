from parslet.core import DAG, parslet_task


@parslet_task
def t1():
    return 1


@parslet_task
def t2(x):
    return x + 1


def test_dag_build_and_topological_order():
    a = t1()
    b = t2(a)
    dag = DAG()
    dag.build_dag([b])
    dag.validate_dag()
    order = dag.get_execution_order()
    assert order == [a.task_id, b.task_id]
