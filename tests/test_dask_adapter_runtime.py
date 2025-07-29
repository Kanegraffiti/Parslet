from parslet.compat import dask_adapter as dask
from parslet.core import DAG, DAGRunner


def test_delayed_decorator_and_compute():
    @dask.delayed
    def inc(x):
        return x + 1

    fut = inc(3)
    dag = DAG()
    dag.build_dag([fut])
    DAGRunner().run(dag)
    result = dask.compute(fut)
    assert result == 4


def test_compute_multiple_tasks():
    @dask.delayed
    def inc(x):
        return x + 1

    fut1 = inc(3)
    fut2 = inc(5)

    dag = DAG()
    dag.build_dag([fut1, fut2])
    DAGRunner().run(dag)

    result = dask.compute(fut1, fut2)
    assert result == (fut1.result(), fut2.result())
