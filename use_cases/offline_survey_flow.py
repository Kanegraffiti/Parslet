"""Use case: offline survey collection.
Loads survey responses, validates them and writes a compressed archive
under ``Parslet_Results``.
"""

from __future__ import annotations

import csv
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.utils.resource_utils import (
    get_available_ram_mb,
    get_battery_level,
)

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
    min_ram_mb: int = 30, min_battery: int = 15
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
def load_responses(
    path: str, resources: Dict[str, bool]
) -> List[Dict[str, str]]:
    if not resources.get("proceed", True):
        return []
    src = Path(path)
    if not src.exists():
        logger.error("Survey file %s not found", path)
        return []
    if src.suffix.lower() == ".json":
        try:
            with open(src, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:  # noqa: broad-except
            logger.error("Failed to load %s: %s", path, exc)
            return []
    responses: List[Dict[str, str]] = []
    try:
        with open(src, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                responses.append(dict(row))
    except Exception as exc:  # noqa: broad-except
        logger.error("Failed to parse %s: %s", path, exc)
    return responses


@parslet_task
def validate_responses(
    items: Iterable[Dict[str, str]],
) -> List[Dict[str, str]]:
    valid: List[Dict[str, str]] = []
    for item in items:
        if item.get("id") and item.get("answer"):
            valid.append(item)
    return valid


@parslet_task
def archive_responses(
    responses: List[Dict[str, str]], dest: Path, resources: Dict[str, bool]
) -> str:
    json_path = dest / "survey.json"
    zip_path = dest / "survey.zip"
    log_path = dest / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {"responses": responses, "resources": resources}, f, indent=2
        )
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(json_path, arcname="survey.json")
    logging.info("Survey archived")
    return str(zip_path)


def main(file_path: str = "survey.csv") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    loaded_f = load_responses(file_path, res_f)
    valid_f = validate_responses(loaded_f)
    arch_f = archive_responses(valid_f, out_dir_f, res_f)
    return [arch_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
