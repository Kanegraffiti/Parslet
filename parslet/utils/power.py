"""Cross-platform power telemetry helpers.

This module exposes a small dataclass :class:`PowerState` and a
``get_power_state`` function that attempts to gather battery and thermal
information from the running system.  The implementation intentionally keeps
its dependencies light so it can operate in constrained environments such as
Android/Termux or Raspberry Pi.  When no information is available the function
falls back to conservative defaults instead of raising errors.
"""

from __future__ import annotations

import subprocess
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

try:  # psutil is part of the base requirements
    import psutil
except Exception:  # pragma: no cover - psutil always available in tests
    psutil = None  # type: ignore


@dataclass
class PowerState:
    """Snapshot of the system's current power conditions."""

    source: Literal["battery", "ac", "unknown"] = "unknown"
    percent: int | None = None
    is_charging: bool | None = None
    est_time_to_empty_min: int | None = None
    est_time_to_full_min: int | None = None
    temperature_c: float | None = None
    cpu_freq_hint: int | None = None  # kHz
    thermal_throttle: bool = False
    ts: float = 0.0


def _psutil_provider() -> PowerState | None:
    """Return power information using :mod:`psutil` if available."""

    if psutil is None:
        return None
    try:
        batt = psutil.sensors_battery()
    except Exception:
        return None
    if batt is None:
        return None

    secs = batt.secsleft
    mins = None
    if secs not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
        mins = int(secs // 60)

    return PowerState(
        source="ac" if batt.power_plugged else "battery",
        percent=int(batt.percent) if batt.percent is not None else None,
        is_charging=batt.power_plugged,
        est_time_to_empty_min=mins if not batt.power_plugged else None,
        est_time_to_full_min=mins if batt.power_plugged else None,
        ts=time.time(),
    )


def _sysfs_provider() -> PowerState | None:
    """Attempt to gather battery info from ``/sys`` paths."""

    base = Path("/sys/class/power_supply")
    if not base.exists():
        return None
    bat_paths = list(base.glob("BAT*"))
    if not bat_paths:
        return None
    try:
        status = (bat_paths[0] / "status").read_text().strip().lower()
        percent = int((bat_paths[0] / "capacity").read_text().strip())
    except Exception:
        return None
    return PowerState(
        source="battery",
        percent=percent,
        is_charging=status == "charging",
        ts=time.time(),
    )


def _termux_provider() -> PowerState | None:
    """Use ``termux-battery-status`` if available on the PATH."""

    try:
        out = subprocess.check_output(["termux-battery-status"], text=True, timeout=2)
    except Exception:
        return None
    try:
        import json

        data = json.loads(out)
    except Exception:
        return None
    return PowerState(
        source="battery" if data.get("status") != "AC" else "ac",
        percent=data.get("percentage"),
        is_charging=data.get("status") == "CHARGING",
        temperature_c=data.get("temperature"),
        ts=time.time(),
    )


_PROVIDERS = [_termux_provider, _psutil_provider, _sysfs_provider]


def get_power_state() -> PowerState:
    """Return the best effort :class:`PowerState` for the system.

    Providers are tried in order and the first non-``None`` result is used.
    If every provider fails, a ``PowerState`` with ``source='unknown'`` is
    returned.  All provider errors are swallowed so callers can use this
    function without defensive ``try`` blocks.
    """

    for provider in _PROVIDERS:
        state = provider()
        if state is not None:
            return state
    # fall back to conservative defaults
    return PowerState(ts=time.time())


def watch(
    interval_s: int = 20, on_change: Callable[[PowerState], None] | None = None
) -> Iterator[PowerState]:
    """Yield :class:`PowerState` snapshots at a fixed interval.

    The generator yields the latest :class:`PowerState` and optionally calls
    ``on_change`` with the new value.  This is a simple building block used by
    higher level scheduling components.
    """

    while True:
        state = get_power_state()
        if on_change is not None:
            on_change(state)
        yield state
        time.sleep(interval_s)
