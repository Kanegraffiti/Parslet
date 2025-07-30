import subprocess

from parslet.hybrid.relay import FileRelay


def test_file_relay_calls_scp(monkeypatch, tmp_path):
    called = {}

    def fake_run(cmd, check, stdout, stderr):
        called["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    dest = "user@host:/tmp"
    relay = FileRelay(dest)
    test_file = tmp_path / "out.txt"
    test_file.write_text("data")
    relay.send(test_file)
    assert called["cmd"][0] == "scp"
    assert called["cmd"][2] == dest
