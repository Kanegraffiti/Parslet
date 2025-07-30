import sys
from parslet import main_cli


def test_rad_simulate(capsys, tmp_path, monkeypatch):
    img = tmp_path / "img.png"
    from PIL import Image

    Image.new("L", (2, 2), color=0).save(img)
    monkeypatch.setattr(
        sys,
        "argv",
        ["parslet", "rad", str(img), "--simulate", "--out-dir", str(tmp_path)],
    )
    main_cli.main()
    out = capsys.readouterr().out
    assert "RAD DAG Simulation" in out
