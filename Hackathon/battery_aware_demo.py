"""
Demo workflow for the Africa Deep Tech Challenge 2025.

This workflow adjusts task behavior based on battery level to show
how Parslet adapts in resource-constrained environments.
"""

from __future__ import annotations

import logging
from pathlib import Path

from parslet import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.utils.resource_utils import get_battery_level

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@parslet_task
def check_battery() -> int:
    """Return detected battery level or assume 100% if unavailable."""
    level = get_battery_level()
    if level is None:
        logger.info("Battery level unavailable; defaulting to 100%%.")
        return 100
    logger.info("Battery at %d%%", level)
    return int(level)


@parslet_task
def compute_task(battery: int) -> str:
    """Simulate computation depending on battery level."""
    if battery < 50:
        logger.info("Low battery detected. Running lightweight analysis.")
        result = "quick-result"
    else:
        logger.info("Sufficient battery. Running full analysis.")
        result = "full-result"
    return result


@parslet_task
def save_result(result: str) -> str:
    """Save result to file."""
    out_dir = Path("Hackathon/Results")
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "result.txt"
    result_path.write_text(result)
    logger.info("Result saved to %s", result_path)
    return str(result_path)


def main() -> list[ParsletFuture]:
    """Build the DAG task list."""
    battery_future = check_battery()
    compute_future = compute_task(battery_future)
    save_future = save_result(compute_future)
    return [save_future]


if __name__ == "__main__":
    dag = DAG()
    dag.add_tasks(*main())  # Add task list to DAG
    runner = DAGRunner(dag, battery_mode_active=True)
    runner.run()
