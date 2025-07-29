from parslet.core import parslet_task, ParsletFuture
from parslet.core.task import _TASK_REGISTRY, set_allow_redefine
import pytest


@parslet_task
def add(x, y):
    return x + y


@parslet_task(battery_sensitive=True)
def sensitive(x):
    return x


def test_parslet_task_decorator_returns_future():
    fut = add(1, 2)
    assert isinstance(fut, ParsletFuture)
    assert fut.func.__name__ == "add"


def test_battery_sensitive_metadata():
    assert getattr(sensitive, "_parslet_battery_sensitive", False) is True


def test_protected_task_redefinition_error():
    @parslet_task(name="prot", protected=True)
    def first():
        return 1

    with pytest.raises(ValueError):

        @parslet_task(name="prot", protected=True)
        def second():
            return 2

    _TASK_REGISTRY.pop("prot", None)


def test_force_redefine_allows_protected_task():
    @parslet_task(name="prot_force", protected=True)
    def base():
        return 1

    set_allow_redefine(True)
    try:

        @parslet_task(name="prot_force", protected=True)
        def redefine():
            return 2

    finally:
        set_allow_redefine(False)
    assert "prot_force" in _TASK_REGISTRY
    _TASK_REGISTRY.pop("prot_force", None)
