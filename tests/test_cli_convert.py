import sys
from pathlib import Path

from pytest import MonkeyPatch

from parslet import main_cli


def test_cli_convert_to_parsl(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    wf = tmp_path / "workflow.py"
    wf.write_text(
        "from parslet import parslet_task\n"
        "@parslet_task\n"
        "def foo():\n"
        "    return 1\n"
        "def main():\n"
        "    f = foo()\n"
        "    return [f]\n"
    )
    out = tmp_path / "out.py"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "parslet",
            "convert",
            "--from-parslet",
            str(wf),
            "--to-parsl",
            str(out),
        ],
    )
    main_cli.main()
    assert out.exists()
    assert "@python_app" in out.read_text()


def test_cli_convert_from_parsl(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    wf = tmp_path / "workflow_parsl.py"
    wf.write_text(
        "from parsl import python_app\n"
        "@python_app\n"
        "def foo():\n"
        "    return 1\n"
        "x = foo()\n"
    )
    out = tmp_path / "out_parslet.py"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "parslet",
            "convert",
            "--from-parsl",
            str(wf),
            "--to-parslet",
            str(out),
        ],
    )
    main_cli.main()
    assert out.exists()
    text = out.read_text()
    assert "@parslet_task" in text
    assert "def main" in text
