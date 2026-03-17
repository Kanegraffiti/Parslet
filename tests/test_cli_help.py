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
    assert "--force-battery" in out


def test_cli_top_level_help_shows_contexts_and_cache(capsys: pytest.CaptureFixture[str]) -> None:
    module = import_module("parslet.main_cli")
    module.sys.argv = ["parslet", "--help"]
    with pytest.raises(SystemExit):
        module.main()
    out = capsys.readouterr().out
    assert "contexts" in out
    assert "cache" in out
