from __future__ import annotations

import json
import sys
from typing import Any


def ascii_heatmap(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    times: dict[str, float] = data.get("task_execution_times", {})
    if not times:
        print("no timing data found")
        return
    max_time = max(times.values()) or 1.0
    for task, t in times.items():
        bar = "#" * max(1, int(t / max_time * 40))
        print(f"{task:20} {bar} {t:.2f}s")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python plot_stats.py stats.json")
        raise SystemExit(1)
    ascii_heatmap(sys.argv[1])
