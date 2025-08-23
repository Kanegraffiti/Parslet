from pathlib import Path

from parslet import ParsletFuture
from parslet.cli import load_workflow_module
from parslet.compat.parsl_adapter import export_parsl_dag, import_parsl_script


def test_round_trip(tmp_path: Path) -> None:
    parsl_src = tmp_path / "wf_parsl.py"
    parsl_src.write_text(
        "from parsl import python_app\n"
        "@python_app\n"
        "def a():\n    return 1\n"
        "@python_app\n"
        "def b(x):\n    return x + 1\n"
        "@python_app\n"
        "def c(x):\n    return x * 2\n"
        "x = a()\n"
        "y = b(x)\n"
        "z = c(y)\n"
    )
    parslet_out = tmp_path / "wf_parslet.py"
    import_parsl_script(str(parsl_src), str(parslet_out))
    mod = load_workflow_module(str(parslet_out))
    futures = mod.main()
    assert all(isinstance(f, ParsletFuture) for f in futures)
    parsl_round = tmp_path / "wf_round.py"
    export_parsl_dag(futures, str(parsl_round))
    text = parsl_round.read_text()
    assert text.count("@python_app") == 3
    assert "b(" in text and "c(" in text
