from parslet.core import AdaptiveScheduler


def test_battery_mode_reduces_workers(monkeypatch):
    def fake_cpu():
        return 4

    def fake_ram():
        return 2048

    def fake_batt():
        return 10

    monkeypatch.setattr("parslet.core.scheduler.get_cpu_count", fake_cpu)
    monkeypatch.setattr(
        "parslet.core.scheduler.get_available_ram_mb", fake_ram
    )
    monkeypatch.setattr("parslet.core.scheduler.get_battery_level", fake_batt)

    sched = AdaptiveScheduler(battery_mode=True)
    actual = sched.calculate_worker_count(None)
    expected = 2
    assert actual == expected, f"Expected {expected} workers, got {actual}."
