from parslet.compat import (
    convert_parsl_to_parslet,
    convert_dask_to_parslet,
    convert_parslet_to_parsl,
)


def test_parsl_conversion_simple():
    src = """
@python_app
def hello():
    return 'hi'
"""
    expected = """
@parslet_task
def hello():
    return 'hi'
"""
    assert convert_parsl_to_parslet(src).strip() == expected.strip()


def test_dask_conversion_simple():
    src = """
from dask import delayed

@delayed
def inc(x):
    return x + 1

result = inc(1).compute()
"""
    expected_contains = "@parslet_task"
    converted = convert_dask_to_parslet(src)
    assert expected_contains in converted
    assert "compute" not in converted


def test_parslet_to_parsl_conversion_simple():
    src = """\n@parslet_task\ndef foo():\n    return 42\n"""
    expected = """\n@python_app\ndef foo():\n    return 42\n"""
    assert convert_parslet_to_parsl(src).strip() == expected.strip()
