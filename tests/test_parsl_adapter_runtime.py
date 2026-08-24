import subprocess
import warnings

import pytest

from parslet.compat import parsl_adapter as parsl
from parslet.core.task import ParsletFuture


def test_python_app_decorator_executes_with_parslet():
    @parsl.python_app
    def add(x, y):
        return x + y

    fut = add(1, 2)
    assert isinstance(fut, ParsletFuture)
    # Simulate execution by calling underlying function
    result = fut.func(*fut.args, **fut.kwargs)
    fut.set_result(result)
    assert fut.result() == 3


def test_bash_app_decorator_executes_with_parslet():
    @parsl.bash_app
    def echo_message(msg):
        return f"echo {msg}"

    fut = echo_message("hi")
    assert isinstance(fut, ParsletFuture)
    # Command executes immediately; result() returns stdout
    assert fut.result().strip() == "hi"


def test_bash_app_decorator_handles_errors():
    @parsl.bash_app
    def fail():
        return "false"

    fut = fail()
    assert isinstance(fut, ParsletFuture)
    # result() should raise the underlying CalledProcessError
    with pytest.raises(subprocess.CalledProcessError):
        fut.result()


def test_dfk_stub_warns():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        parsl.DataFlowKernel()
        assert any("not supported" in str(wi.message) for wi in w)
