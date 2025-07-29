import ast
import warnings
from parslet.compat.parsl_adapter import ParslToParsletTranslator


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
