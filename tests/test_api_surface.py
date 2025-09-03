import parslet


def test_top_level_public_api() -> None:
    expected = {
        "parslet_task",
        "ParsletFuture",
        "DAG",
        "DAGRunner",
        "task_variant",
        "EnergyAwarePolicy",
        "PowerState",
        "get_power_state",
        "watch",
    }
    assert set(parslet.__all__) == expected
