import subprocess
import pytest
import importlib.util
import types
import sys
from pathlib import Path
import warnings

# Manually load modules to avoid importing parslet.__init__, which depends on
# system components not needed for these tests.
ROOT = Path(__file__).resolve().parents[1]

# Create minimal package placeholders
parslet_pkg = types.ModuleType("parslet")
parslet_pkg.__path__ = [str(ROOT / "parslet")]
sys.modules.setdefault("parslet", parslet_pkg)

core_pkg = types.ModuleType("parslet.core")
core_pkg.__path__ = [str(ROOT / "parslet" / "core")]
sys.modules.setdefault("parslet.core", core_pkg)

compat_pkg = types.ModuleType("parslet.compat")
compat_pkg.__path__ = [str(ROOT / "parslet" / "compat")]
sys.modules.setdefault("parslet.compat", compat_pkg)

# Load core.task to get ParsletFuture
spec_task = importlib.util.spec_from_file_location(
    "parslet.core.task", ROOT / "parslet" / "core" / "task.py"
)
task_module = importlib.util.module_from_spec(spec_task)
sys.modules["parslet.core.task"] = task_module
spec_task.loader.exec_module(task_module)
ParsletFuture = task_module.ParsletFuture

# Load parsl_adapter module
spec_adapter = importlib.util.spec_from_file_location(
    "parslet.compat.parsl_adapter",
    ROOT / "parslet" / "compat" / "parsl_adapter.py",
)
parsl = importlib.util.module_from_spec(spec_adapter)
sys.modules["parslet.compat.parsl_adapter"] = parsl
spec_adapter.loader.exec_module(parsl)


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
