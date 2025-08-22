"""Adaptive scheduling utilities for Parslet.

Public API: :class:`AdaptiveScheduler` used by :class:`~parslet.core.runner.DAGRunner`.
"""

from __future__ import annotations

from typing import Optional

from .dag import DAG
from ..utils.resource_utils import (
    get_cpu_count,
    get_available_ram_mb,
    get_battery_level,
)

__all__ = ["AdaptiveScheduler"]


class AdaptiveScheduler:
    """Simple resource-aware scheduler for DAGRunner."""

    def __init__(self, battery_mode: bool = False) -> None:
        self.battery_mode = battery_mode

    def calculate_worker_count(self, override: Optional[int] = None) -> int:
        """Determine how many workers to use based on system resources."""
        if override is not None and override > 0:
            workers = override
        else:
            cpu_based = get_cpu_count()
            ram = get_available_ram_mb()
            ram_based = cpu_based
            if ram is not None:
                ram_based = max(1, int(ram // 512))
            workers = min(cpu_based, ram_based)
            batt = get_battery_level()
            if self.battery_mode or (batt is not None and batt < 20):
                workers = max(1, workers // 2)
        return max(1, workers)

    def schedule(self, dag: DAG) -> None:
        """Placeholder for future advanced scheduling logic."""
        # Currently handled directly in DAGRunner
        pass
