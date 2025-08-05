"""Example: Processing sensor data from a low-power MCU.
This demo shows how Parslet can clean noisy sensor readings and flag
anomalies. Results are saved in a timestamped directory under
``Parslet_Results``.
"""

from __future__ import annotations

import csv
import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.utils.resource_utils import (
    get_available_ram_mb,
    get_battery_level,
)

logger = logging.getLogger(__name__)


@parslet_task
def create_output_dir(base: str | None = None) -> Path:
    """Create a timestamped results directory."""
    base_path = Path(base or "Parslet_Results")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out = base_path / timestamp
    out.mkdir(parents=True, exist_ok=True)
    return out


@parslet_task
def check_resources(
    min_ram_mb: int = 50, min_battery: int = 20
) -> Dict[str, int | float | None | bool]:
    """Check available RAM and battery level."""
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
def generate_sensor_data(points: int = 50) -> List[float]:
    """Simulate raw sensor readings with occasional spikes."""
    data = []
    val = 25.0
    for _ in range(points):
        val += random.uniform(-0.5, 0.5)
        if random.random() < 0.05:
            val += random.uniform(-10, 10)
        data.append(round(val, 2))
    return data


@parslet_task
def smooth_data(data: List[float]) -> List[float]:
    """Simple moving average smoothing."""
    smoothed: List[float] = []
    for i, val in enumerate(data):
        window = data[max(0, i - 2) : i + 1]
        smoothed.append(round(sum(window) / len(window), 2))
    return smoothed


@parslet_task
def detect_anomalies(data: List[float], threshold: float = 5.0) -> List[int]:
    """Return indices where a spike/drop occurs."""
    anomalies = []
    for i in range(1, len(data)):
        if abs(data[i] - data[i - 1]) > threshold:
            anomalies.append(i)
    return anomalies


@parslet_task
def save_results(
    clean: List[float],
    anomalies: List[int],
    out_dir: Path,
    resources: Dict[str, bool],
) -> str:
    """Save cleaned data and anomaly info."""
    log_path = out_dir / "diagnostics.log"
    json_path = out_dir / "anomalies.json"
    csv_path = out_dir / "clean_data.csv"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info("Saving results...")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "value"])
        for idx, val in enumerate(clean):
            writer.writerow([idx, val])
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {"anomaly_indices": anomalies, "resources": resources}, f, indent=2
        )
    logging.info("Results saved")
    return str(csv_path)


def main() -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    raw_f = generate_sensor_data()
    smooth_f = smooth_data(raw_f)
    anomalies_f = detect_anomalies(smooth_f)
    final_f = save_results(smooth_f, anomalies_f, out_dir_f, res_f)
    return [final_f]


if __name__ == "__main__":
    dag = DAG()
    dag.build_dag(main())
    runner = DAGRunner()
    runner.run(dag)
