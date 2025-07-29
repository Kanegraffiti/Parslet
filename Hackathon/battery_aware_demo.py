"""Demo workflow for the Africa Deep Tech Challenge 2025.

The tasks adjust behavior based on available battery level to show how
Parslet can thrive in resource-constrained settings.
"""

from __future__ import annotations

import logging
from pathlib import Path

from parslet.core import DAG, DAGRunner, ParsletFuture, parslet_task
from parslet.utils.resource_utils import get_battery_level

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@parslet_task
def check_battery() -> int:
    """Return detected battery level or 100 if unavailable."""
    level = get_battery_level()
    if level is None:
        logger.info("Battery level not available; assuming 100%.")
        return 100
    logger.info("Battery at %s%%", level)
    return int(level)


@parslet_task
def compute(batt: int) -> str:
    """Perform a lightweight or full computation based on battery."""
    if batt < 50:
        logger.info("Low battery; running quick analysis only.")
        result = "quick-result"
    else:
        logger.info("Sufficient battery; performing full analysis.")
        result = "full-result"
    return result


@parslet_task
def save(result: str) -> str:
    """Save results to the output directory."""
    out_dir = Path("Hackathon/Results")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "result.txt"
    path.write_text(result)
    logger.info("Saved %s", path)
    return str(path)


def main() -> list[ParsletFuture]:
    batt_f = check_battery()
    comp_f = compute(batt_f)
    save_f = save(comp_f)
    return [save_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(battery_mode_active=True)
    runner.run()
