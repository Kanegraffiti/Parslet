import pytest

from parslet.core.policy import AdaptivePolicy
from parslet.utils import resource_utils


def test_policy_shrinks_on_low_battery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(resource_utils, "get_cpu_count", lambda: 8)
    monkeypatch.setattr(resource_utils, "get_available_ram_mb", lambda: 4096)
    monkeypatch.setattr(resource_utils, "get_battery_level", lambda: 10)
    policy = AdaptivePolicy(max_workers=8)
    snapshot = resource_utils.probe_resources()
    assert policy.decide_pool_size(snapshot) == 4


def test_policy_expands_to_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resource_utils, "get_cpu_count", lambda: 8)
    monkeypatch.setattr(resource_utils, "get_available_ram_mb", lambda: 4096)
    monkeypatch.setattr(resource_utils, "get_battery_level", lambda: 80)
    policy = AdaptivePolicy(max_workers=8)
    snapshot = resource_utils.probe_resources()
    assert policy.decide_pool_size(snapshot) == 8
