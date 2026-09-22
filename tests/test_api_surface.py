import parslet


def test_top_level_public_api() -> None:
    expected = {
        "parslet_task",
        "parslet_workflow",
        "ParsletFuture",
        "DAG",
        "DAGRunner",
        "task_variant",
        "EnergyAwarePolicy",
        "BatteryAwarePolicy",
        "PowerState",
        "get_power_state",
        "watch",
        "ContextOracle",
        "ConciergeOrchestrator",
    }
    assert set(parslet.__all__) == expected
