from __future__ import annotations

"""Radiology diagnosis helper utilities."""

from dataclasses import dataclass
from difflib import SequenceMatcher
import hashlib
import inspect
import json
import logging
from pathlib import Path
from typing import Tuple

from parslet.utils.resource_utils import (
    get_available_ram_mb,
    get_battery_level,
)
from PIL import Image

logger = logging.getLogger(__name__)

# --- Constants ---
MEAN_THRESHOLD = 100
STD_THRESHOLD = 50
BATTERY_THRESHOLD = 20
RAM_THRESHOLD_MB = 512
# Models must agree by at least 85% before results are auto-accepted
AGREEMENT_THRESHOLD = 0.85


class BatteryLevelLowError(RuntimeError):
    """Raised when system battery is below threshold."""

    def __init__(self, level: int) -> None:
        super().__init__(f"Battery level {level}% is too low for analysis")
        self.level = level


class LowMemoryError(RuntimeError):
    """Raised when system RAM is below threshold."""

    def __init__(self, ram_mb: float) -> None:
        super().__init__(
            f"Available RAM {ram_mb:.1f}MB below required minimum"
        )
        self.ram_mb = ram_mb


@dataclass
class ModelResult:
    """Result of model prediction."""

    diagnosis: str
    confidence: float


class TinyMeanModel:
    """Stub model predicting based on pixel mean."""

    VERSION = "0.1"

    def predict(self, image: Image.Image) -> ModelResult:
        pixels = list(image.getdata())
        mean_val = sum(pixels) / len(pixels)
        diagnosis = "abnormal" if mean_val > MEAN_THRESHOLD else "normal"
        confidence = abs(mean_val - MEAN_THRESHOLD) / 255
        return ModelResult(diagnosis, confidence)


class TinyStdModel:
    """Stub model predicting based on pixel standard deviation."""

    VERSION = "0.1"

    def predict(self, image: Image.Image) -> ModelResult:
        pixels = list(image.getdata())
        if not pixels:
            std_val = 0.0
        else:
            mean_val = sum(pixels) / len(pixels)
            variance = sum((p - mean_val) ** 2 for p in pixels) / len(pixels)
            std_val = variance**0.5
        diagnosis = "abnormal" if std_val > STD_THRESHOLD else "normal"
        confidence = abs(std_val - STD_THRESHOLD) / 255
        return ModelResult(diagnosis, confidence)


_DEF_MODELS = (TinyMeanModel(), TinyStdModel())


def _compute_model_hash(model: object) -> str:
    src = inspect.getsource(model.__class__)
    return hashlib.md5(src.encode()).hexdigest()


def analyze(
    image_path: str | Path,
    output_dir: str | Path,
    *,
    ignore_battery: bool = False,
) -> Tuple[Path, Path, Path]:
    """Analyze an image with tiny models.

    Args:
        image_path: Path to input image.
        output_dir: Directory to store outputs.
        ignore_battery: If ``True`` skip battery checks.

    Returns:
        Paths to ``meta.json``, ``diagnosis.txt`` and ``review_flag.txt``.

    Raises:
        BatteryLevelLowError: If battery is below ``BATTERY_THRESHOLD``.
        LowMemoryError: If available RAM is below ``RAM_THRESHOLD_MB``.
        ValueError: If ``image_path`` attempts path traversal.
    """

    image_path = Path(image_path)
    if ".." in image_path.parts:
        raise ValueError("Path traversal detected in image_path")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    batt = get_battery_level()
    if not ignore_battery and batt is not None and batt < BATTERY_THRESHOLD:
        logger.warning("Battery below threshold: %s%%", batt)
        raise BatteryLevelLowError(batt)

    ram = get_available_ram_mb()
    if ram is not None and ram < RAM_THRESHOLD_MB:
        logger.warning("RAM below threshold: %.1fMB", ram)
        raise LowMemoryError(ram)

    with Image.open(image_path) as img:
        gray = img.convert("L")
        results = [model.predict(gray) for model in _DEF_MODELS]

    diag1, diag2 = results[0].diagnosis, results[1].diagnosis
    ratio = SequenceMatcher(None, diag1, diag2).ratio()
    agree = ratio >= AGREEMENT_THRESHOLD and diag1 == diag2
    final_diag = diag1 if agree else "REVIEW_REQUIRED"

    meta = {
        "tiny_mean_model_version": _DEF_MODELS[0].VERSION,
        "tiny_std_model_version": _DEF_MODELS[1].VERSION,
        "tiny_mean_model_hash": _compute_model_hash(_DEF_MODELS[0]),
        "tiny_std_model_hash": _compute_model_hash(_DEF_MODELS[1]),
        "agreement_score": ratio,
    }

    meta_path = output_dir / "meta.json"
    diagnosis_path = output_dir / "diagnosis.txt"
    review_flag_path = output_dir / "review_flag.txt"

    meta_path.write_text(json.dumps(meta))
    diagnosis_path.write_text(final_diag)
    review_flag_path.write_text(str(not agree).lower())

    logger.info(
        "Diagnosis %s (agreement %.2f) written to %s",
        final_diag,
        ratio,
        output_dir,
    )

    return meta_path, diagnosis_path, review_flag_path
