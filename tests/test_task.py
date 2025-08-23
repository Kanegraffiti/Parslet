import pytest

from parslet.core import ParsletFuture, parslet_task
from parslet.core.task import _TASK_REGISTRY, set_allow_redefine


@parslet_task
def add(x: int, y: int) -> int:
    return x + y


@parslet_task(battery_sensitive=True)
def sensitive(x: int) -> int:
    return x


def test_parslet_task_decorator_returns_future() -> None:
    fut = add(1, 2)
    assert isinstance(fut, ParsletFuture)
    assert fut.func.__name__ == "add"


def test_battery_sensitive_metadata() -> None:
    assert getattr(sensitive, "_parslet_battery_sensitive", False) is True


def test_protected_task_redefinition_error() -> None:
    set_allow_redefine(False)
    try:

        @parslet_task(name="prot", protected=True)
        def first() -> int:
            return 1

        with pytest.raises(ValueError):

            @parslet_task(name="prot", protected=True)
            def second() -> int:
                return 2

    finally:
        _TASK_REGISTRY.pop("prot", None)
        set_allow_redefine(True)


def test_force_redefine_allows_protected_task() -> None:
    set_allow_redefine(False)

    @parslet_task(name="prot_force", protected=True)
    def base() -> int:
        return 1

    set_allow_redefine(True)
    try:

        @parslet_task(name="prot_force", protected=True)
        def redefine() -> int:
            return 2

    finally:
        set_allow_redefine(True)
    assert "prot_force" in _TASK_REGISTRY
    _TASK_REGISTRY.pop("prot_force", None)
