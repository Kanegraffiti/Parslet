"""Example: Offline image classification on a mobile device.
Simulates loading an image, running a tiny CNN and saving the result.
Results are written into ``Parslet_Results``.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from PIL import Image

from examples.utils import ensure_sample_image
from parslet.core import DAG, DAGRunner, ParsletFuture, parslet_task
from parslet.utils.resource_utils import (
    get_available_ram_mb,
    get_battery_level,
)

try:
    from transformers import pipeline
except Exception:  # pragma: no cover - transformers optional
    pipeline = None

# Default image used for the example workflows
ASSET_PATH = ensure_sample_image()

logger = logging.getLogger(__name__)


@parslet_task
def create_output_dir(base: str | None = None) -> Path:
    base_path = Path(base or "Parslet_Results")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out = base_path / timestamp
    out.mkdir(parents=True, exist_ok=True)
    return out


@parslet_task
def check_resources(
    min_ram_mb: int = 100, min_battery: int = 20
) -> Dict[str, int | float | None | bool]:
    ram = get_available_ram_mb()
    batt = get_battery_level()
    ram_ok = ram is None or ram >= min_ram_mb
    batt_ok = batt is None or batt >= min_battery
    return {
        "ram": ram,
        "battery": batt,
        "ram_ok": ram_ok,
        "battery_ok": batt_ok,
        "proceed": ram_ok and batt_ok,
    }


@parslet_task
def load_image(path: str, resources: Dict[str, bool]) -> Image.Image | None:
    if not resources.get("proceed", True):
        return None
    try:
        return Image.open(path)
    except Exception as e:
        logger.error("Failed to load image %s: %s", path, e)
        return None


@parslet_task
def run_model(img: Image.Image | None) -> Dict[str, object]:
    if img is None:
        return {"object": None, "confidence": 0.0}

    if pipeline is not None:
        try:
            clf = pipeline(
                "image-classification",
                model="hf-internal-testing/tiny-random-resnet",
            )
            pred = clf(img)[0]
            return {
                "object": pred["label"],
                "confidence": float(pred["score"]),
            }
        except Exception as exc:  # pragma: no cover - network or torch issues
            logger.warning("HuggingFace inference failed: %s", exc)

    # Fallback deterministic output for offline/demo usage
    return {"object": "leaf", "confidence": 0.92}


@parslet_task
def apply_fallback(
    result: Dict[str, object], threshold: float = 0.8
) -> Dict[str, object]:
    if float(result.get("confidence", 0)) < threshold:
        result["object"] = "unknown"
    return result


@parslet_task
def save_result(
    result: Dict[str, object], out_dir: Path, resources: Dict[str, bool]
) -> str:
    log_path = out_dir / "diagnostics.log"
    res_path = out_dir / "classification.json"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info("Saving classification result")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump({"result": result, "resources": resources}, f, indent=2)
    return str(res_path)


def main(image_path: str | None = None) -> List[ParsletFuture]:
    image_path = image_path or str(ASSET_PATH)
    out_dir_f = create_output_dir()
    res_f = check_resources()
    img_f = load_image(image_path, res_f)
    model_f = run_model(img_f)
    final_res_f = apply_fallback(model_f)
    save_f = save_result(final_res_f, out_dir_f, res_f)
    return [save_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
