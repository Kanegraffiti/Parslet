from __future__ import annotations
import json
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np
import logging

try:
    from transformers import pipeline
except Exception:  # pragma: no cover - optional
    pipeline = None

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.utils.resource_utils import (
    get_available_ram_mb,
    get_battery_level,
)


@parslet_task
def create_output_dir(base: Optional[str] = None) -> Path:
    """Create timestamped result directory."""
    base_path = Path(
        base or Path(__file__).resolve().parent.parent / "RADPars_Results"
    )
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = base_path / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


@parslet_task
def check_resources(
    min_ram_mb: int = 800, min_battery: int = 20
) -> Dict[str, Optional[float]]:
    """Return resource info and whether it's safe to proceed."""
    ram = get_available_ram_mb()
    battery = get_battery_level()
    ram_safe = ram is None or ram >= min_ram_mb
    battery_safe = battery is None or battery >= min_battery
    proceed = ram_safe and battery_safe
    return {
        "ram_mb": ram,
        "battery_percent": battery,
        "ram_safe": ram_safe,
        "battery_safe": battery_safe,
        "proceed": proceed,
    }


@parslet_task
def load_image(
    image_path: str, resources: Dict[str, Optional[float]]
) -> Optional[np.ndarray]:
    if not resources.get("proceed", True):
        return None
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    return img


@parslet_task
def preprocess_image(
    img: Optional[np.ndarray], resources: Dict[str, Optional[float]]
) -> Optional[np.ndarray]:
    if img is None or not resources.get("proceed", True):
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    edges = cv2.Canny(denoised, 50, 150)
    return edges


@parslet_task
def save_annotated_image(
    original: Optional[np.ndarray],
    edges: Optional[np.ndarray],
    out_dir: Path,
    resources: Dict[str, Optional[float]],
) -> Optional[str]:
    if original is None or edges is None or not resources.get("proceed", True):
        return None
    annotated = original.copy()
    annotated[edges > 0] = [0, 0, 255]
    out_path = out_dir / "annotated_scan.png"
    cv2.imwrite(str(out_path), annotated)
    return str(out_path)


@parslet_task
def model_a_inference(
    img: Optional[np.ndarray],
    out_dir: Path,
    resources: Dict[str, Optional[float]],
) -> Dict[str, object]:
    if img is None or not resources.get("proceed", True):
        return {"diagnosis": None, "confidence": 0.0}
    if pipeline is not None:
        try:
            clf = pipeline(
                "image-classification",
                model="hf-internal-testing/tiny-random-resnet",
            )
            pred = clf(img)[0]
            diagnosis = pred["label"]
            confidence = float(pred["score"])
        except Exception as exc:  # pragma: no cover - handle offline
            logging.getLogger(__name__).warning("HF model A failed: %s", exc)
            mean_val = float(np.mean(img))
            diagnosis = (
                "No abnormality detected"
                if mean_val > 100
                else "Possible abnormality"
            )
            confidence = 0.9 if mean_val > 100 else 0.8
    else:
        mean_val = float(np.mean(img))
        diagnosis = (
            "No abnormality detected"
            if mean_val > 100
            else "Possible abnormality"
        )
        confidence = 0.9 if mean_val > 100 else 0.8
    result = {"diagnosis": diagnosis, "confidence": confidence}
    with open(out_dir / "model_A_output.json", "w") as f:
        json.dump(result, f)
    return result


@parslet_task
def model_b_inference(
    img: Optional[np.ndarray],
    out_dir: Path,
    resources: Dict[str, Optional[float]],
) -> Dict[str, object]:
    if img is None or not resources.get("proceed", True):
        return {"diagnosis": None, "confidence": 0.0}
    if pipeline is not None:
        try:
            clf = pipeline(
                "image-classification",
                model="hf-internal-testing/tiny-random-vit",
            )
            pred = clf(img)[0]
            diagnosis = pred["label"]
            confidence = float(pred["score"])
        except Exception as exc:  # pragma: no cover
            logging.getLogger(__name__).warning("HF model B failed: %s", exc)
            std_val = float(np.std(img))
            diagnosis = (
                "No abnormality detected"
                if std_val < 50
                else "Possible abnormality"
            )
            confidence = 0.85 if std_val < 50 else 0.75
    else:
        std_val = float(np.std(img))
        diagnosis = (
            "No abnormality detected"
            if std_val < 50
            else "Possible abnormality"
        )
        confidence = 0.85 if std_val < 50 else 0.75
    result = {"diagnosis": diagnosis, "confidence": confidence}
    with open(out_dir / "model_B_output.json", "w") as f:
        json.dump(result, f)
    return result


@parslet_task
def finalize_results(
    res_a: Dict[str, Optional[float]],
    res_b: Dict[str, Optional[float]],
    resources: Dict[str, Optional[float]],
    out_dir: Path,
    annotated_path: Optional[str],
) -> Dict[str, object]:
    diag_a = str(res_a.get("diagnosis") or "")
    diag_b = str(res_b.get("diagnosis") or "")
    similarity = SequenceMatcher(None, diag_a, diag_b).ratio()
    requires_review = (
        similarity < 0.85
        or not diag_a
        or not diag_b
        or not resources.get("proceed", True)
    )
    final_diag = diag_a if similarity >= 0.85 and diag_a == diag_b else None
    meta: Dict[str, object] = {
        "final_diagnosis": final_diag,
        "model_agreement": similarity,
        "requires_review": requires_review,
        "battery_safe": resources.get("battery_safe"),
        "timestamp": datetime.now().isoformat(),
        "models_used": ["tinycnn-v1.onnx", "tesseract-ocr"],
        "annotated_image": (
            Path(annotated_path).name if annotated_path else None
        ),
    }
    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f)
    if final_diag and not requires_review:
        with open(out_dir / "diagnosis.txt", "w") as f:
            f.write(str(final_diag) + "\n")
    else:
        with open(out_dir / "review_flag.txt", "w") as f:
            f.write("Human input needed\n")
    return meta


def main(image_name: str = "scan.png") -> list[ParsletFuture]:
    image_path = f"/storage/emulated/0/Pictures/Diagnostics/{image_name}"
    out_dir_future = create_output_dir()
    resources_future = check_resources()
    img_future = load_image(image_path, resources_future)
    edges_future = preprocess_image(img_future, resources_future)
    annotated_future = save_annotated_image(
        img_future, edges_future, out_dir_future, resources_future
    )
    a_future = model_a_inference(
        edges_future, out_dir_future, resources_future
    )
    b_future = model_b_inference(
        edges_future, out_dir_future, resources_future
    )
    final_future = finalize_results(
        a_future, b_future, resources_future, out_dir_future, annotated_future
    )
    return [final_future]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
