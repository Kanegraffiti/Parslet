from parslet import main_cli
import sys


def test_cli_convert_to_parsl(tmp_path, monkeypatch):
    wf = tmp_path / "workflow.py"
    wf.write_text("from parslet import parslet_task\n@parslet_task\ndef foo():\n    return 1\n")
    monkeypatch.setattr(sys, "argv", ["parslet", "convert", "--to-parsl", str(wf)])
    main_cli.main()
    out = wf.with_name("workflow_parsl.py")
    assert out.exists()
    text = out.read_text()
    assert "@python_app" in text
