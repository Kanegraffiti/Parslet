"""
Parslet Resource Utilities
--------------------------

This module provides utility functions for querying system resources, such as
CPU count and available RAM. These utilities help Parslet make informed
decisions, for example, when determining default concurrency levels for the
`DAGRunner`.

The module attempts to use `psutil` for detailed information like RAM, but
gracefully handles its absence by returning `None` or default values,
ensuring `psutil` is a soft dependency.
"""

import logging  # For logging errors in resource queries
import os
from typing import NamedTuple

# Initialize a logger for this module.
# This allows for more controlled logging than print statements, especially if
# used as a library.
logger = logging.getLogger(__name__)

# Attempt to import psutil. If not available, relevant functions will indicate
# this. PSUTIL_AVAILABLE acts as a flag for conditional logic.
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # Assign to None so type hints and checks work cleanly.

BATTERY_AVAILABLE = False
try:
    if PSUTIL_AVAILABLE and hasattr(psutil, "sensors_battery"):
        BATTERY_AVAILABLE = True
except Exception:
    BATTERY_AVAILABLE = False


class ResourceSnapshot(NamedTuple):
    """Lightweight container for system resource metrics."""

    cpu_count: int
    available_ram_mb: float | None
    battery_level: int | None


def get_cpu_count() -> int:
    """
    Returns the number of logical CPUs available to the system.

    This function uses `os.cpu_count()`. It is designed to always return a
    positive integer, defaulting to 1 if `os.cpu_count()` returns an
    unexpected value (e.g., `None` or non-positive), although this is
    highly unlikely in modern Python environments.

    Returns:
        int: The number of logical CPUs, or 1 as a fallback.
    """
    try:
        cpu_count = os.cpu_count()
    except NotImplementedError:
        # Some platforms might not implement os.cpu_count().
        logger.warning(
            "os.cpu_count() is not implemented on this platform. "
            "Defaulting to 1 CPU."
        )
        return 1

    if cpu_count is not None and cpu_count > 0:
        return cpu_count
    else:
        # This case should be rare with modern Python versions.
        logger.warning(
            f"os.cpu_count() returned an unexpected value: {cpu_count}. "
            "Defaulting to 1 CPU."
        )
        return 1


def get_available_ram_mb() -> float | None:
    """
    Returns the available system RAM in Megabytes (MB).

    This function relies on the `psutil` library. If `psutil` is not
    installed or if an error occurs during the call (e.g., due to
    permissions or OS issues), it returns `None`.

    The "available" memory is defined by `psutil.virtual_memory().available`,
    which represents the memory that can be given instantly to processes
    without the system going into swap.

    Returns:
        Optional[float]: The available system RAM in MB, or `None` if
                         `psutil` is not available or an error occurs.
    """
    if not PSUTIL_AVAILABLE or psutil is None:
        # Log this information once or at a higher debug level if it becomes
        # noisy. For now, a debug log is appropriate as this is expected if
        # psutil isn't a hard dependency.
        logger.debug(
            "psutil library not found or not imported. "
            "Cannot retrieve available RAM."
        )
        return None

    try:
        # psutil.virtual_memory() returns a named tuple with memory stats.
        # '.available' gives the memory immediately available for processes.
        available_ram_bytes: int = psutil.virtual_memory().available
        # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes).
        available_ram_mb = available_ram_bytes / (1024 * 1024)
        return float(available_ram_mb)
    except Exception as e:
        # Catch any exception that might occur during the psutil call.
        logger.error(f"Error retrieving available RAM using psutil: {e}", exc_info=True)
        return None


def get_battery_level() -> int | None:
    """Return the current battery percentage if available."""
    # 1) Try psutil if it is available
    if BATTERY_AVAILABLE and psutil is not None:
        try:
            batt = psutil.sensors_battery()
            if batt is not None and batt.percent is not None:
                return int(batt.percent)
        except Exception as e:  # pragma: no cover - psutil may fail in CI
            logger.debug(
                "Battery level via psutil not available: %s", e, exc_info=False
            )

    # 2) Try Termux command on Android devices
    try:
        import json
        import shutil
        import subprocess

        termux_cmd = shutil.which("termux-battery-status")
        if termux_cmd:
            output = subprocess.check_output([termux_cmd], text=True)
            data = json.loads(output)
            percent = data.get("percentage")
            if percent is not None:
                return int(percent)
    except Exception as e:  # pragma: no cover - Termux not usually in CI
        logger.debug(
            "Battery level via termux-battery-status not available: %s",
            e,
            exc_info=False,
        )

    # 3) Fallback to reading from /sys/class/power_supply (common on Linux)
    try:
        import glob

        for path in glob.glob("/sys/class/power_supply/BAT*/capacity"):
            try:
                with open(path, encoding="utf-8") as f:
                    val = f.read().strip()
                    return int(val)
            except Exception:
                continue
    except Exception as e:  # pragma: no cover - path may not exist
        logger.debug(
            "Battery level via /sys/class/power_supply not available: %s",
            e,
            exc_info=False,
        )

    logger.debug("Battery level could not be determined with available methods.")
    return None


def probe_resources() -> ResourceSnapshot:
    """Collect a snapshot of current CPU, RAM and battery metrics."""

    return ResourceSnapshot(
        cpu_count=get_cpu_count(),
        available_ram_mb=get_available_ram_mb(),
        battery_level=get_battery_level(),
    )


# This block allows testing the functions when the script is run directly.
if __name__ == "__main__":
    # Basic logging setup for __main__ to see messages from this module.
    logging.basicConfig(level=logging.DEBUG)

    logger.info("--- Resource Utilities Test ---")

    cpu_cores = get_cpu_count()
    logger.info(f"Detected CPU Count: {cpu_cores}")

    available_ram = get_available_ram_mb()
    if available_ram is not None:
        logger.info(f"Detected Available RAM: {available_ram:.2f} MB")
    else:
        if not PSUTIL_AVAILABLE:
            logger.warning(
                "Available RAM: Information unavailable because 'psutil' is "
                "not installed."
            )
            logger.info(
                "Consider installing psutil for RAM details: " "pip install psutil"
            )
        else:
            # This case implies psutil is imported but the call failed for
            # other reasons.
            logger.error(
                "Available RAM: Could not be determined due to an error "
                "during psutil call (see logs above)."
            )

    logger.info("--- End of Test ---")
