import ast
import importlib.util
import types
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

# Create minimal 'parslet' and 'parslet.core' packages
# to satisfy relative imports
parslet_pkg = types.ModuleType("parslet")
parslet_pkg.__path__ = [str(project_root / "parslet")]
sys.modules.setdefault("parslet", parslet_pkg)

core_pkg = types.ModuleType("parslet.core")
core_pkg.__path__ = [str(project_root / "parslet/core")]
sys.modules.setdefault("parslet.core", core_pkg)

task_spec = importlib.util.spec_from_file_location(
    "parslet.core.task", project_root / "parslet/core/task.py"
)
task_mod = importlib.util.module_from_spec(task_spec)
task_spec.loader.exec_module(task_mod)
sys.modules["parslet.core.task"] = task_mod
setattr(core_pkg, "task", task_mod)

spec = importlib.util.spec_from_file_location(
    "parslet.compat.dask_adapter",
    project_root / "parslet/compat/dask_adapter.py",
)
_dask_adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_dask_adapter)
DaskToParsletTranslator = _dask_adapter.DaskToParsletTranslator


def test_dask_translator_replaces_decorator_and_compute():
    src = """
from dask import delayed

@delayed
def inc(x):
    return x + 1

result = inc(1).compute()
"""
    tree = ast.parse(src)
    DaskToParsletTranslator().visit(tree)
    result = ast.unparse(tree)
    assert "@parslet_task" in result
    assert ".compute" not in result


def test_dask_translator_handles_module_decorator():
    src = """
import dask

@dask.delayed
def inc(x):
    return x + 1

result = inc(1).compute()
"""
    tree = ast.parse(src)
    DaskToParsletTranslator().visit(tree)
    result = ast.unparse(tree)
    assert "@parslet_task" in result
    assert ".compute" not in result


def test_dask_translator_handles_aliased_decorator():
    src = """
from dask import delayed as ddelayed

@ddelayed
def inc(x):
    return x + 1
"""
    tree = ast.parse(src)
    DaskToParsletTranslator().visit(tree)
    result = ast.unparse(tree)
    assert "@parslet_task" in result


def test_dask_translator_handles_delayed_function_call():
    src = """
import dask

def inc(x):
    return x + 1

result = dask.delayed(inc)(2)
"""
    tree = ast.parse(src)
    DaskToParsletTranslator().visit(tree)
    result = ast.unparse(tree)
    assert "parslet_task(inc)(2)" in result


def test_dask_translator_handles_aliased_delayed_function_call():
    src = """
from dask import delayed as ddelayed

def inc(x):
    return x + 1

result = ddelayed(inc)(3)
"""
    tree = ast.parse(src)
    DaskToParsletTranslator().visit(tree)
    result = ast.unparse(tree)
    assert "parslet_task(inc)(3)" in result
