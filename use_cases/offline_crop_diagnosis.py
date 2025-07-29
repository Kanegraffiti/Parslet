"""Use case: offline crop disease detection.
Loads a folder of leaf images, runs a lightweight classifier and
writes predictions to ``Parslet_Results``.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from PIL import Image

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.utils.resource_utils import get_available_ram_mb, get_battery_level

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
    min_ram_mb: int = 50, min_battery: int = 20
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
def gather_images(folder: str, resources: Dict[str, bool]) -> List[Path] | None:
    if not resources.get("proceed", True):
        return None
    path = Path(folder)
    if not path.exists():
        logger.error("Image folder %s missing", folder)
        return None
    images = [
        p for p in path.iterdir() if p.suffix.lower() in {".jpg", ".png", ".jpeg"}
    ]
    return images


@parslet_task
def classify_images(paths: List[Path] | None) -> List[Dict[str, float]]:
    predictions: List[Dict[str, float]] = []
    if paths is None:
        return predictions
    for p in paths:
        try:
            img = Image.open(p)
            r, g, b = img.resize((32, 32)).convert("RGB").split()
            avg_r = sum(r.getdata()) / 1024
            avg_g = sum(g.getdata()) / 1024
            score = avg_r / (avg_g + 1)
            predictions.append(
                {"file": p.name, "disease_score": round(float(score), 3)}
            )
        except Exception as exc:  # noqa: broad-except - corrupted images possible
            logger.warning("Failed to process %s: %s", p, exc)
    return predictions


@parslet_task
def save_results(
    predictions: List[Dict[str, float]], dest: Path, resources: Dict[str, bool]
) -> str:
    report_path = dest / "diagnosis.json"
    log_path = dest / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    payload = {"predictions": predictions, "resources": resources}
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    logging.info("Diagnosis saved")
    return str(report_path)


def main(image_folder: str = "./images") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    img_f = gather_images(image_folder, res_f)
    preds_f = classify_images(img_f)
    save_f = save_results(preds_f, out_dir_f, res_f)
    return [save_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
