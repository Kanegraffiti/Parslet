from pathlib import Path

from parslet import ParsletFuture
from parslet.cli import load_workflow_module
from parslet.compat.dask_adapter import export_dask_dag, import_dask_script


def test_round_trip(tmp_path: Path) -> None:
    dask_src = tmp_path / "wf_dask.py"
    dask_src.write_text(
        "from dask import delayed\n"
        "@delayed\n"
        "def a():\n    return 1\n"
        "@delayed\n"
        "def b(x):\n    return x + 1\n"
        "x = a()\n"
        "y = b(x)\n"
        "res = y.compute()\n"
    )
    parslet_out = tmp_path / "wf_parslet.py"
    import_dask_script(str(dask_src), str(parslet_out))
    mod = load_workflow_module(str(parslet_out))
    futures = mod.main()
    assert all(isinstance(f, ParsletFuture) for f in futures)
    dask_round = tmp_path / "wf_round.py"
    export_dask_dag(futures, str(dask_round))
    text = dask_round.read_text()
    assert text.count("@delayed") == 2
    assert "b(" in text
