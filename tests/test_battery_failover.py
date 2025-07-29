from parslet.core.scheduler import AdaptiveScheduler
from parslet.utils.resource_utils import get_cpu_count


def test_scheduler_low_battery(monkeypatch):
    monkeypatch.setattr("parslet.core.scheduler.get_battery_level", lambda: 10)
    sched = AdaptiveScheduler()
    workers = sched.calculate_worker_count(None)
    assert workers < get_cpu_count()
