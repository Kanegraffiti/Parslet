from parslet.core.policy import EnergyAwarePolicy
from parslet.core.task import parslet_task
from parslet.utils.power import PowerState


@parslet_task(energy_cost="high", deadline_s=10, qos="standard")
def expensive() -> str:
    return "expensive"


@parslet_task(energy_cost="low", deadline_s=10, qos="standard")
def cheap() -> str:
    return "cheap"


def test_low_battery_prefers_low_energy() -> None:
    futures = [expensive(), cheap()]
    policy = EnergyAwarePolicy(low_battery_threshold=40)
    power = PowerState(source="battery", percent=20)
    ordered = policy.order(futures, power)
    assert ordered[0].func.__name__ == "cheap"
