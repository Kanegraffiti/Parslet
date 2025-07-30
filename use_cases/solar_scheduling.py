"""Use case: schedule solar panel maintenance.
Reads power statistics, computes average efficiency and creates a
cleaning schedule saved in ``Parslet_Results``.
"""

from __future__ import annotations

import csv
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
    min_ram_mb: int = 40, min_battery: int = 20
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
def load_power_log(path: str, resources: Dict[str, bool]) -> List[float]:
    if not resources.get("proceed", True):
        return []
    src = Path(path)
    if not src.exists():
        logger.error("Power log %s missing", path)
        return []
    values: List[float] = []
    try:
        with open(src, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                try:
                    values.append(float(row[0]))
                except Exception:
                    continue
    except Exception as exc:  # noqa: broad-except
        logger.error("Failed to read %s: %s", path, exc)
    return values


@parslet_task
def generate_schedule(values: List[float]) -> Dict[str, float | str]:
    if not values:
        return {"average": 0.0, "action": "inspect"}
    avg = sum(values) / len(values)
    action = "clean" if avg < 70 else "ok"
    return {"average": round(avg, 2), "action": action}


@parslet_task
def save_schedule(
    result: Dict[str, float | str], dest: Path, resources: Dict[str, bool]
) -> str:
    out_path = dest / "schedule.json"
    log_path = dest / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"result": result, "resources": resources}, f, indent=2)
    logging.info("Schedule saved")
    return str(out_path)


def main(log_path: str = "power.csv") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    values_f = load_power_log(log_path, res_f)
    sched_f = generate_schedule(values_f)
    save_f = save_schedule(sched_f, out_dir_f, res_f)
    return [save_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
