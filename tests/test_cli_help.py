from importlib import import_module

import pytest


def test_run_help_shows_new_flags(
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = import_module("parslet.main_cli")
    module.sys.argv = ["parslet", "run", "--help"]
    with pytest.raises(SystemExit):
        module.main()
    out = capsys.readouterr().out
    assert "--max-workers" in out
    assert "--json-logs" in out
    assert "--export-stats" in out
