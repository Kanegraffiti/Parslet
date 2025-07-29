"""Utility helpers exposed at package level."""

import logging

try:
    from rich.logging import RichHandler
except Exception:  # pragma: no cover - rich is optional
    RichHandler = None

from .resource_utils import (
    get_cpu_count,
    get_available_ram_mb,
    get_battery_level,
)


def get_parslet_logger(
    name: str = "parslet", level: int = logging.INFO
) -> logging.Logger:
    """Return a logger configured for Parslet CLI and library use.

    If ``rich`` is available, logs will be pretty-printed using ``RichHandler``;
    otherwise a basic ``logging`` configuration is used. Handlers are added only
    once per logger to avoid duplicate messages when the function is called
    multiple times.
    """

    logger = logging.getLogger(name)

    if not logger.handlers:
        if RichHandler is not None:
            handler = RichHandler(rich_tracebacks=True)
            formatter = logging.Formatter("%(message)s", datefmt="[%X]")
        else:  # Fallback to simple logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    logger.setLevel(level)
    return logger


__all__ = [
    "get_cpu_count",
    "get_available_ram_mb",
    "get_battery_level",
    "get_parslet_logger",
]
