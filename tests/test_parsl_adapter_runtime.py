import warnings

from parslet.compat import parsl_adapter as parsl
from parslet.core import DAG, DAGRunner, ParsletFuture


def test_python_app_decorator_executes_with_parslet():
    @parsl.python_app
    def add(x, y):
        return x + y

    fut = add(1, 2)
    dag = DAG()
    dag.build_dag([fut])
    DAGRunner().run(dag)
    assert fut.result() == 3


def test_bash_app_decorator_executes_with_parslet():
    @parsl.bash_app
    def echo_message(msg):
        return msg

    fut = echo_message("hi")
    assert isinstance(fut, ParsletFuture)
    dag = DAG()
    dag.build_dag([fut])
    DAGRunner().run(dag)
    assert fut.result() == "hi"


def test_dfk_stub_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        parsl.DataFlowKernel()
        assert any("not supported" in str(wi.message) for wi in w)
