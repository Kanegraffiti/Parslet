from pathlib import Path

import pytest

from parslet.cli import load_workflow_module, resolve_workflow_entry


def test_resolve_workflow_entry_from_decorator(tmp_path: Path) -> None:
    wf = tmp_path / "wf.py"
    wf.write_text(
        "from parslet import parslet_task, parslet_workflow\n"
        "@parslet_task\n"
        "def t():\n"
        "    return 1\n"
        "@parslet_workflow\n"
        "def workflow():\n"
        "    return [t()]\n"
    )
    module = load_workflow_module(str(wf))
    entry = resolve_workflow_entry(module)
    assert entry.__name__ == "workflow"


def test_resolve_workflow_entry_error_message(tmp_path: Path) -> None:
    wf = tmp_path / "wf_nom.py"
    wf.write_text("def foo():\n    return []\n")
    module = load_workflow_module(str(wf))
    with pytest.raises(ImportError, match=r"Could not find a `main\(\)` function"):
        resolve_workflow_entry(module)
