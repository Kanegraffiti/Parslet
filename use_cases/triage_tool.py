"""Use case: offline medical triage tool.
Processes symptom forms, assigns a severity score and writes
results to ``Parslet_Results``.
"""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

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
    min_ram_mb: int = 20, min_battery: int = 10
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
def load_forms(path: str, resources: Dict[str, bool]) -> List[Dict[str, str]]:
    if not resources.get("proceed", True):
        return []
    src = Path(path)
    if not src.exists():
        logger.error("Form file %s not found", path)
        return []
    forms: List[Dict[str, str]] = []
    try:
        with open(src, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                forms.append(dict(row))
    except Exception as exc:  # noqa: broad-except
        logger.error("Failed to read %s: %s", path, exc)
    return forms


@parslet_task
def score_forms(forms: List[Dict[str, str]]) -> List[Dict[str, str | int]]:
    scored: List[Dict[str, str | int]] = []
    for form in forms:
        severity = 0
        if "fever" in form.get("symptom", "").lower():
            severity += 2
        if "cough" in form.get("symptom", "").lower():
            severity += 1
        scored.append({**form, "score": severity})
    return scored


@parslet_task
def save_scores(
    scores: List[Dict[str, str | int]], dest: Path, resources: Dict[str, bool]
) -> str:
    csv_path = dest / "triage.csv"
    log_path = dest / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    if scores:
        headers = list(scores[0].keys())
    else:
        headers = []
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(scores)
    logging.info("Scores saved")
    return str(csv_path)


def main(forms_path: str = "forms.csv") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    forms_f = load_forms(forms_path, res_f)
    scores_f = score_forms(forms_f)
    save_f = save_scores(scores_f, out_dir_f, res_f)
    return [save_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
