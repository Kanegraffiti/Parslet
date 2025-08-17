import hashlib
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


def test_verify_chain(tmp_path):
    sig = tmp_path / "sig.txt"
    payload = "payload"
    dag_hash = hashlib.sha256(payload.encode()).hexdigest()

    sig.write_text(payload)
    assert Defcon.verify_chain(dag_hash, sig)

    sig.write_text("tampered")
    assert not Defcon.verify_chain(dag_hash, sig)

    sig.unlink()
    assert Defcon.verify_chain(dag_hash, sig)
