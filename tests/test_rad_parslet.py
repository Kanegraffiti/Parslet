from pathlib import Path

import pytest
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.abspath("examples/rad_parslet"))  # noqa: E402
import rad_parslet  # noqa: E402


def _make_image(path: Path, color: int) -> None:
    img = Image.new("L", (2, 2), color=color)
    img.save(path)


def test_analysis_success(tmp_path, monkeypatch):
    monkeypatch.setattr(rad_parslet, "get_battery_level", lambda: 100)
    monkeypatch.setattr(rad_parslet, "get_available_ram_mb", lambda: 2048)

    img_path = tmp_path / "img.png"
    _make_image(img_path, 50)

    meta, diag, review = rad_parslet.analyze(img_path, tmp_path)

    assert diag.read_text() == "normal"
    assert review.read_text() == "false"


def test_analysis_disagreement(tmp_path, monkeypatch):
    monkeypatch.setattr(rad_parslet, "get_battery_level", lambda: 100)
    monkeypatch.setattr(rad_parslet, "get_available_ram_mb", lambda: 2048)

    class FakeModel(rad_parslet.TinyStdModel):
        def predict(self, image):
            return rad_parslet.ModelResult("abnormal", 0.9)

    monkeypatch.setattr(
        rad_parslet, "_DEF_MODELS", (rad_parslet.TinyMeanModel(), FakeModel())
    )

    img_path = tmp_path / "img.png"
    _make_image(img_path, 50)

    _, diag, review = rad_parslet.analyze(img_path, tmp_path)

    assert diag.read_text() == "REVIEW_REQUIRED"
    assert review.read_text() == "true"


def test_analysis_low_battery(tmp_path, monkeypatch):
    monkeypatch.setattr(rad_parslet, "get_battery_level", lambda: 10)
    monkeypatch.setattr(rad_parslet, "get_available_ram_mb", lambda: 2048)

    img_path = tmp_path / "img.png"
    _make_image(img_path, 50)

    with pytest.raises(rad_parslet.BatteryLevelLowError):
        rad_parslet.analyze(img_path, tmp_path)
