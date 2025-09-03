from parslet.utils.power import PowerState, get_power_state


def test_get_power_state_returns_snapshot() -> None:
    state = get_power_state()
    assert isinstance(state, PowerState)
    assert state.source in {"battery", "ac", "unknown"}
    # percent may be None but if provided it should be within 0-100
    if state.percent is not None:
        assert 0 <= state.percent <= 100
