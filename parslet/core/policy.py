"""Resource-aware worker pool policy."""

from dataclasses import dataclass

from ..utils.power import PowerState
from ..utils.resource_utils import ResourceSnapshot
from .task import ParsletFuture


@dataclass
class AdaptivePolicy:
    """Decide worker pool size based on system resources."""

    max_workers: int | None = None
    min_free_ram_mb: int = 256
    battery_threshold: int = 30

    def decide_pool_size(self, probes: ResourceSnapshot) -> int:
        """Return desired worker count given current resource probes."""

        workers = probes.cpu_count
        if self.max_workers is not None:
            workers = min(workers, self.max_workers)
        if probes.available_ram_mb is not None:
            ram_based = max(1, int(probes.available_ram_mb // self.min_free_ram_mb))
            workers = min(workers, ram_based)
        if (
            probes.battery_level is not None
            and probes.battery_level < self.battery_threshold
        ):
            workers = max(1, workers // 2)
        return max(1, workers)


@dataclass
class EnergyAwarePolicy:
    """Hybrid policy that considers task metadata and power state."""

    low_battery_threshold: int = 40

    def _energy_rank(self, cost: str) -> int:
        return {"low": 0, "med": 1, "high": 2}.get(cost, 1)

    def _qos_rank(self, qos: str) -> int:
        return {"high": 0, "standard": 1, "best_effort": 2}.get(qos, 1)

    def task_priority(self, fut: ParsletFuture, power: PowerState) -> tuple:
        deadline = fut.deadline_s if fut.deadline_s is not None else float("inf")
        energy = self._energy_rank(fut.energy_cost)
        qos = self._qos_rank(fut.qos)
        if (
            power.source == "battery"
            and power.percent is not None
            and power.percent < self.low_battery_threshold
        ):
            return (deadline, energy, qos)
        return (deadline, qos, energy)

    def order(
        self, futures: list[ParsletFuture], power: PowerState
    ) -> list[ParsletFuture]:
        """Return tasks sorted by priority for the given power state."""

        return sorted(futures, key=lambda f: self.task_priority(f, power))

    def decide_max_workers(self, power: PowerState, current: int) -> int:
        """Adjust the worker pool based on power level."""

        if power.source == "battery" and power.percent is not None:
            if power.percent < self.low_battery_threshold:
                return max(1, current // 2)
        return current
