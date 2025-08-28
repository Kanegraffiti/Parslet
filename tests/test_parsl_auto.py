from importlib import import_module
from pathlib import Path

from parslet import ParsletFuture
from parslet.cli import load_workflow_module


def test_load_module_auto_converts(tmp_path: Path) -> None:
    wf = tmp_path / "wf_parsl.py"
    wf.write_text(
        "from parsl import python_app\n"
        "@python_app\n"
        "def a():\n    return 1\n"
        "x = a()\n"
    )
    mod = load_workflow_module(str(wf))
    assert getattr(mod, "__converted_from_parsl__", False)
    futures = mod.main()
    assert all(isinstance(f, ParsletFuture) for f in futures)


def test_cli_run_exports_parsl(tmp_path: Path, monkeypatch) -> None:
    wf = tmp_path / "wf_parsl.py"
    wf.write_text(
        "from parsl import python_app\n"
        "@python_app\n"
        "def a():\n    return 1\n"
        "x = a()\n"
    )
    module = import_module("parslet.main_cli")
    monkeypatch.setattr(module, "sys", module.sys)
    module.sys.argv = ["parslet", "run", str(wf)]
    module.main()
    exported = tmp_path / "wf_parsl_parslet_export.py"
    assert exported.exists()
    assert "@python_app" in exported.read_text()
