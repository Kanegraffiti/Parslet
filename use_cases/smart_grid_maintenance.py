"""Use case: analyze solar mini-grid maintenance logs.
Detects outages from a log file and plots uptime statistics.
Results are saved into ``Parslet_Results``.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt

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
def parse_log(log_path: str, resources: Dict[str, bool]) -> Dict[str, float] | None:
    if not resources.get("proceed", True):
        return None
    data: Dict[str, float] = {}
    path = Path(log_path)
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        try:
            day, uptime = line.split(",")
            data[day.strip()] = float(uptime.strip())
        except ValueError:
            logger.warning("Malformed line: %s", line)
    return data


@parslet_task
def evaluate(
    data: Dict[str, float] | None, threshold: float = 80.0
) -> Dict[str, object]:
    if not data:
        return {"average_uptime": 0.0, "below_threshold": True}
    avg = sum(data.values()) / len(data)
    return {"average_uptime": avg, "below_threshold": avg < threshold}


@parslet_task
def plot_chart(data: Dict[str, float] | None, dest: Path) -> str | None:
    if not data:
        return None
    days = list(data.keys())
    uptimes = list(data.values())
    colors = ["green" if u >= 80 else "red" for u in uptimes]
    fig, ax = plt.subplots()
    ax.bar(days, uptimes, color=colors)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Uptime %")
    fig.tight_layout()
    out_path = dest / "uptime.png"
    fig.savefig(out_path)
    plt.close(fig)
    return str(out_path)


@parslet_task
def save_report(
    result: Dict[str, object],
    chart: str | None,
    out_dir: Path,
    resources: Dict[str, bool],
) -> str:
    report_path = out_dir / "report.json"
    log_path = out_dir / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    payload = {"summary": result, "chart": chart, "resources": resources}
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    logging.info("Report saved")
    return str(report_path)


def main(log_path: str = "grid.log") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    data_f = parse_log(log_path, res_f)
    eval_f = evaluate(data_f)
    chart_f = plot_chart(data_f, out_dir_f)
    report_f = save_report(eval_f, chart_f, out_dir_f, res_f)
    return [report_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
