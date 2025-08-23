"""Adaptive scheduling utilities for Parslet."""

from __future__ import annotations

from ..utils.resource_utils import (
    ResourceSnapshot,
    get_available_ram_mb,
    get_battery_level,
    get_cpu_count,
)
from .dag import DAG
from .policy import AdaptivePolicy

__all__ = ["AdaptiveScheduler"]


class AdaptiveScheduler:
    """Simple resource-aware scheduler for DAGRunner."""

    def __init__(
        self, battery_mode: bool = False, policy: AdaptivePolicy | None = None
    ) -> None:
        self.battery_mode = battery_mode
        self.policy = policy or AdaptivePolicy()
        if battery_mode and self.policy.battery_threshold < 40:
            self.policy.battery_threshold = 40

    def calculate_worker_count(self, override: int | None = None) -> int:
        """Determine how many workers to use based on system resources."""
        if override is not None and override > 0:
            return override
        snapshot = ResourceSnapshot(
            cpu_count=get_cpu_count(),
            available_ram_mb=get_available_ram_mb(),
            battery_level=get_battery_level(),
        )
        return self.policy.decide_pool_size(snapshot)

    def schedule(self, dag: DAG) -> None:
        """Placeholder for future advanced scheduling logic."""
        del dag
        return
