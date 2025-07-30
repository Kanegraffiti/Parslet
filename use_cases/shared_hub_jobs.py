"""Use case: process queued jobs on a shared hub.
Loads a JSON queue, performs simple work and stores results
inside ``Parslet_Results``.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

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
    min_ram_mb: int = 30, min_battery: int = 20
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
def load_jobs(path: str, resources: Dict[str, bool]) -> List[int]:
    if not resources.get("proceed", True):
        return []
    src = Path(path)
    if not src.exists():
        logger.error("Job queue %s not found", path)
        return []
    try:
        with open(src, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # noqa: broad-except
        logger.error("Failed to load %s: %s", path, exc)
        return []


@parslet_task
def process_jobs(jobs: List[int]) -> List[int]:
    return [j * j for j in jobs]


@parslet_task
def save_results(
    results: List[int], dest: Path, resources: Dict[str, bool]
) -> str:
    out_path = dest / "results.json"
    log_path = dest / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "resources": resources}, f, indent=2)
    logging.info("Results saved")
    return str(out_path)


def main(queue_path: str = "jobs.json") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    jobs_f = load_jobs(queue_path, res_f)
    proc_f = process_jobs(jobs_f)
    save_f = save_results(proc_f, out_dir_f, res_f)
    return [save_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
