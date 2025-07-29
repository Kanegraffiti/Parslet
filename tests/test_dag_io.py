from parslet.core import DAG, DAGRunner, parslet_task, dag_io


@parslet_task
def t1() -> int:
    return 1


@parslet_task
def t2(x: int) -> int:
    return x + 1


def test_export_import_dag(tmp_path):
    a = t1()
    b = t2(a)
    dag = DAG()
    dag.build_dag([b])
    dag.validate_dag()
    out = tmp_path / "graph.dag"
    dag_io.export_dag_to_json(dag, str(out))

    loaded = dag_io.import_dag_from_json(str(out))
    loaded.validate_dag()

    runner = DAGRunner(max_workers=1)
    runner.run(loaded)
    assert loaded.tasks[b.task_id].result() == 2
