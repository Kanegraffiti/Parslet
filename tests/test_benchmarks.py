from parslet.core import DAG, DAGRunner, parslet_task


@parslet_task
def inc(x):
    return x + 1


def test_benchmark_output_contains_task():
    f = inc(1)
    dag = DAG()
    dag.build_dag([f])
    dag.validate_dag()
    runner = DAGRunner(max_workers=1)
    runner.run(dag)
    bench = runner.get_task_benchmarks()
    assert f.task_id in bench
    assert bench[f.task_id]["status"] == "SUCCESS"
