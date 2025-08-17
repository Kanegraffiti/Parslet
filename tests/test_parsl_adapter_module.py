import ast
import warnings
import importlib.util
import types
import sys
from pathlib import Path

# Manually load the translator to avoid importing parslet.__init__
ROOT = Path(__file__).resolve().parents[1]

parslet_pkg = types.ModuleType("parslet")
parslet_pkg.__path__ = [str(ROOT / "parslet")]
sys.modules.setdefault("parslet", parslet_pkg)

core_pkg = types.ModuleType("parslet.core")
core_pkg.__path__ = [str(ROOT / "parslet" / "core")]
sys.modules.setdefault("parslet.core", core_pkg)

compat_pkg = types.ModuleType("parslet.compat")
compat_pkg.__path__ = [str(ROOT / "parslet" / "compat")]
sys.modules.setdefault("parslet.compat", compat_pkg)

spec_task = importlib.util.spec_from_file_location(
    "parslet.core.task", ROOT / "parslet" / "core" / "task.py"
)
task_module = importlib.util.module_from_spec(spec_task)
sys.modules["parslet.core.task"] = task_module
spec_task.loader.exec_module(task_module)

spec_adapter = importlib.util.spec_from_file_location(
    "parslet.compat.parsl_adapter",
    ROOT / "parslet" / "compat" / "parsl_adapter.py",
)
parsl_module = importlib.util.module_from_spec(spec_adapter)
sys.modules["parslet.compat.parsl_adapter"] = parsl_module
spec_adapter.loader.exec_module(parsl_module)

ParslToParsletTranslator = parsl_module.ParslToParsletTranslator


def test_parsl_translator_replaces_decorators():
    src = """
@python_app
def foo():
    return 1
"""
    tree = ast.parse(src)
    ParslToParsletTranslator().visit(tree)
    result = ast.unparse(tree)
    assert "@parslet_task" in result


def test_parsl_translator_warns_dfk():
    src = "DataFlowKernel()"
    tree = ast.parse(src)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        ParslToParsletTranslator().visit(tree)
        assert any("DataFlowKernel" in str(warn.message) for warn in w)
