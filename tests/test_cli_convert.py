from parslet import main_cli
import sys


def test_cli_convert_to_parsl(tmp_path, monkeypatch):
    wf = tmp_path / "workflow.py"
    wf.write_text(
        "from parslet import parslet_task\n"
        "@parslet_task\n"
        "def foo():\n"
        "    return 1\n"
    )
    monkeypatch.setattr(
        sys, "argv", ["parslet", "convert", "--to-parsl", str(wf)]
    )
    main_cli.main()
    out = wf.with_name("workflow_parsl.py")
    assert out.exists()
    text = out.read_text()
    assert "@python_app" in text


def test_cli_convert_stdout(tmp_path, monkeypatch, capsys):
    wf = tmp_path / "workflow.py"
    wf.write_text(
        "from parslet import parslet_task\n"
        "@parslet_task\n"
        "def foo():\n"
        "    return 1\n"
    )
    monkeypatch.setattr(
        sys, "argv", ["parslet", "convert", "--to-parsl", str(wf), "--stdout"]
    )
    main_cli.main()
    out = wf.with_name("workflow_parsl.py")
    assert not out.exists()
    captured = capsys.readouterr()
    assert "@python_app" in captured.out


def test_cli_convert_recursive(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.py").write_text("@python_app\n" "def foo():\n" "    return 1\n")
    sub = root / "sub"
    sub.mkdir()
    (sub / "b.py").write_text("@python_app\n" "def bar():\n" "    return 2\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["parslet", "convert", "--from-parsl", str(root), "--recursive"],
    )
    main_cli.main()
    out_a = root / "a_parslet.py"
    out_b = sub / "b_parslet.py"
    assert out_a.exists()
    assert out_b.exists()
    assert "@parslet_task" in out_a.read_text()
    assert "@parslet_task" in out_b.read_text()
