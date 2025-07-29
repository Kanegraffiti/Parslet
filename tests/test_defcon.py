from pathlib import Path
from parslet.security.defcon import Defcon


def test_scan_code():
    p = Path("tmp_test.py")
    p.write_text("a=1")
    assert Defcon.scan_code([p])
    p.write_text('eval("2+2")')
    assert not Defcon.scan_code([p])
    p.unlink()


def test_tamper_guard_detection(tmp_path):
    file = tmp_path / "watch.txt"
    file.write_text("hello")
    guard = Defcon.tamper_guard([file])
    assert guard()
    file.write_text("changed")
    assert not guard()
