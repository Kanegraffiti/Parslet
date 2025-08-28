from importlib import import_module
from pathlib import Path

import pytest


def test_cli_help(capsys, monkeypatch):
    module = import_module("parslet.main_cli")
    monkeypatch.setattr(module, "sys", module.sys)
    monkeypatch.setattr(module.sys, "argv", ["parslet"])
    module.cli()
    out = capsys.readouterr().out
    assert "Parslet command line" in out or "Parslet CLI" in out


def test_cli_examples_listing(capsys):
    module = import_module("parslet.main_cli")
    module.sys.argv = ["parslet", "examples"]
    try:
        module.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "offline_crop_diagnosis.py" in out


def test_cli_help_option(capsys):
    module = import_module("parslet.main_cli")
    module.sys.argv = ["parslet", "--help"]
    with pytest.raises(SystemExit):
        module.main()
    out = capsys.readouterr().out
    assert "Parslet command line" in out or "Parslet CLI" in out


def test_cli_invalid_argument(capsys):
    module = import_module("parslet.main_cli")
    module.sys.argv = ["parslet", "nonexistent"]
    with pytest.raises(SystemExit):
        module.main()
    err = capsys.readouterr().err
    assert "invalid choice" in err


def test_cli_examples_all_files(capsys):
    module = import_module("parslet.main_cli")
    module.sys.argv = ["parslet", "examples"]
    try:
        module.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    out_lines = out.strip().splitlines()
    lines = [line for line in out_lines if "Plugins loaded" not in line]
    listed = sorted(lines)
    expected = sorted(f.name for f in Path("use_cases").glob("*.py"))
    assert listed == expected
