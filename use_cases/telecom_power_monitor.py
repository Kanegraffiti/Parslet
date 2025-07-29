"""Use case: monitor remote telecom tower power consumption.
Reads daily power logs, analyzes trends and predicts maintenance actions.
Results are saved into ``Parslet_Results``.
"""

# mypy: ignore-errors

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from parslet.core import DAG, DAGRunner, ParsletFuture, parslet_task
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
def read_logs(path: str, resources: Dict[str, bool]) -> List[Dict[str, float]]:
    if not resources.get("proceed", True):
        return []
    src = Path(path)
    if not src.exists():
        logger.error("Log file %s not found", path)
        return []
    records: List[Dict[str, float]] = []
    try:
        with open(src, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    records.append(
                        {
                            "battery": float(row["battery"]),
                            "generator_hours": float(row["generator_hours"]),
                            "solar_kw": float(row["solar_kw"]),
                        }
                    )
                except (KeyError, ValueError):
                    logger.warning("Malformed row: %s", row)
    except Exception as exc:  # noqa: broad-except
        logger.error("Failed to parse %s: %s", path, exc)
    return records


@parslet_task
def analyze_power(records: List[Dict[str, float]]) -> Dict[str, float]:
    if not records:
        return {"avg_battery": 0.0, "gen_hours": 0.0, "avg_solar": 0.0}
    avg_battery = sum(r["battery"] for r in records) / len(records)
    total_gen = sum(r["generator_hours"] for r in records)
    avg_solar = sum(r["solar_kw"] for r in records) / len(records)
    return {
        "avg_battery": avg_battery,
        "gen_hours": total_gen,
        "avg_solar": avg_solar,
    }


@parslet_task
def predict_action(
    metrics: Dict[str, float], battery_threshold: float = 40.0
) -> Dict[str, str]:
    actions: List[str] = []
    if metrics["avg_battery"] < battery_threshold:
        actions.append("Replace tower battery soon")
    if metrics["gen_hours"] > 5:
        actions.append("Inspect generator for excessive usage")
    return {"actions": "; ".join(actions) or "Power systems normal"}


@parslet_task
def save_report(
    metrics: Dict[str, float],
    prediction: Dict[str, str],
    out_dir: Path,
    resources: Dict[str, bool],
) -> str:
    report_path = out_dir / "tower_report.json"
    log_path = out_dir / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    payload = {
        "metrics": metrics,
        "prediction": prediction,
        "resources": resources,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    logging.info("Report saved")
    return str(report_path)


def main(log_path: str = "tower_power.csv") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    logs_f = read_logs(log_path, res_f)
    metrics_f = analyze_power(logs_f)
    pred_f = predict_action(metrics_f)
    report_f = save_report(metrics_f, pred_f, out_dir_f, res_f)
    return [report_f]


if __name__ == "__main__":
    futures = main()
    dag = DAG()
    dag.build_dag(futures)
    runner = DAGRunner(dag)
    runner.run()
