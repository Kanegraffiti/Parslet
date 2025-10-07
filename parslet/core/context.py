"""Context orchestration primitives for Parslet.

The :class:`ContextOracle` is a small, battery-friendly decision engine that
helps Parslet decide if a task should be allowed to execute. Tasks can declare
context guards via ``@parslet_task(contexts=[...])`` and the oracle evaluates
those declarations against live system conditions and user supplied overrides.

The goal is to provide a declarative alternative to the rule builders that
mobile automation suites expose while keeping the implementation lightweight
enough to run happily on single board computers and Android devices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import re
from typing import Callable, Iterable, Sequence

from ..utils.network_utils import is_network_available, is_vpn_active
from ..utils.power import get_power_state
from ..utils.resource_utils import get_battery_level


@dataclass(slots=True)
class ContextResult:
    """Structured result describing a context evaluation."""

    requirement: str
    satisfied: bool
    actual: bool
    origin: str
    detail: str | None = None


class ContextOracle:
    """Evaluate declarative context requirements for Parslet tasks.

    Parameters
    ----------
    enabled : Iterable[str] | None, optional
        Manual context tags that should be forced to ``True``. This mirrors the
        behaviour of toggling scenes in phone automation apps. Users can supply
        these via CLI flags or the ``PARSLET_CONTEXTS`` environment variable.
    """

    def __init__(self, enabled: Iterable[str] | None = None) -> None:
        env_contexts = os.getenv("PARSLET_CONTEXTS", "")
        env_values = [c.strip() for c in env_contexts.split(",") if c.strip()]
        manual = list(enabled or []) + env_values
        self._manual_overrides: set[str] = {self._normalise_name(c) for c in manual}
        self._detectors: dict[str, Callable[[], bool]] = {}
        self._aliases: dict[str, str] = {
            "online": "network.online",
            "offline": "network.offline",
            "wifi": "network.online",
            "vpn": "security.vpn",
            "plugged": "power.ac",
        }
        self._register_builtin_detectors()

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def register_detector(self, name: str, detector: Callable[[], bool]) -> None:
        """Register a custom boolean detector."""

        self._detectors[self._normalise_name(name)] = detector

    def enable(self, name: str) -> None:
        """Manually enable a context tag for the lifetime of the oracle."""

        self._manual_overrides.add(self._normalise_name(name))

    def evaluate(self, requirements: Sequence[str]) -> tuple[bool, list[ContextResult]]:
        """Return ``True`` if *all* requirements are satisfied."""

        results: list[ContextResult] = []
        allow = True
        for requirement in requirements:
            result = self._evaluate_single(requirement)
            results.append(result)
            if not result.satisfied:
                allow = False
        return allow, results

    def snapshot(self) -> dict[str, bool]:
        """Return the current view of all known detectors and overrides."""

        state: dict[str, bool] = {}
        for name, detector in self._detectors.items():
            try:
                state[name] = bool(detector())
            except Exception:
                state[name] = False
        for manual in self._manual_overrides:
            state[manual] = True
        return dict(sorted(state.items()))

    def available_contexts(self) -> list[str]:
        """Return a sorted list of known context names."""

        names = set(self._detectors) | set(self._manual_overrides)
        names.update(self._aliases.keys())
        return sorted(names)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    def _register_builtin_detectors(self) -> None:
        self._detectors["network.online"] = is_network_available
        self._detectors["network.offline"] = lambda: not is_network_available()
        self._detectors["security.vpn"] = is_vpn_active
        self._detectors["power.ac"] = lambda: get_power_state().source == "ac"
        self._detectors["power.battery"] = lambda: get_power_state().source == "battery"
        self._detectors["time.night"] = self._is_night
        self._detectors["time.day"] = lambda: not self._is_night()
        self._detectors["time.weekend"] = lambda: datetime.now().weekday() >= 5
        self._detectors["time.office_hours"] = lambda: 9 <= datetime.now().hour < 18

    def _is_night(self) -> bool:
        hour = datetime.now().hour
        return hour < 7 or hour >= 22

    def _evaluate_single(self, requirement: str) -> ContextResult:
        negate = requirement.startswith("!")
        name = requirement[1:] if negate else requirement
        normalised = self._normalise_name(name)

        value, origin, detail = self._resolve_context(normalised)
        actual = bool(value)
        satisfied = not actual if negate else actual

        # Provide a friendly detail for negated contexts.
        if negate and detail is None:
            detail = "negated requirement"

        if value is None:
            actual = False
            satisfied = False if not negate else True
            origin = "unknown"
            detail = detail or "no detector registered"

        return ContextResult(
            requirement=requirement,
            satisfied=satisfied,
            actual=actual,
            origin=origin,
            detail=detail,
        )

    def _resolve_context(self, name: str) -> tuple[bool | None, str, str | None]:
        if name in self._manual_overrides:
            return True, "manual", "enabled by override"

        detector = self._detectors.get(name)
        if detector:
            try:
                return bool(detector()), "detector", None
            except Exception as exc:  # pragma: no cover - defensive
                return False, "detector", f"detector error: {exc}"

        dyn_value = self._resolve_dynamic(name)
        if dyn_value is not None:
            return dyn_value

        alias = self._aliases.get(name)
        if alias:
            return self._resolve_context(alias)

        return None, "unknown", None

    def _resolve_dynamic(self, name: str) -> tuple[bool, str, str | None] | None:
        battery_match = re.fullmatch(r"battery>=(\d{1,3})", name)
        if battery_match:
            threshold = int(battery_match.group(1))
            level = get_battery_level()
            if level is None:
                return False, "battery", "battery level unavailable"
            detail = f"battery at {level}%"
            return (level >= threshold, "battery", detail)

        if name == "battery.comfort":
            level = get_battery_level()
            if level is None:
                return False, "battery", "battery level unavailable"
            return (level >= 60, "battery", f"battery at {level}%")

        if name == "battery.survival":
            level = get_battery_level()
            if level is None:
                return False, "battery", "battery level unavailable"
            return (level >= 15, "battery", f"battery at {level}%")

        return None

    @staticmethod
    def _normalise_name(name: str) -> str:
        return name.strip().lower()


__all__ = ["ContextOracle", "ContextResult"]

