"""Diagnostic helpers for Parslet."""

import logging
import socket

logger = logging.getLogger(__name__)


def find_free_port(start_port: int = 6000, max_tries: int = 50) -> int:
    """Finds an available port starting from ``start_port``.

    Args:
        start_port: Initial port to try.
        max_tries: Maximum number of incremental ports to test.

    Returns:
        An available port number.

    Raises:
        RuntimeError: If no free port is found within the specified range.
    """
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(
        f"No free port found in range {start_port}-{start_port + max_tries}"
    )
