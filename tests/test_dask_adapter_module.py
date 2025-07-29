import ast
from parslet.compat.dask_adapter import DaskToParsletTranslator


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
