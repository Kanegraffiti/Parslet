"""Resource-aware worker pool policy."""

from dataclasses import dataclass

from ..utils.resource_utils import ResourceSnapshot


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
