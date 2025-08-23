"""Runtime security sentries for Parslet.

These lightweight guards block risky behaviour unless tasks opt in
explicitly.  The module provides two context managers used by the runner:

* :func:`shell_guard` – prevents invocation of ``os.system`` and common
  ``subprocess`` helpers unless a task is decorated with
  ``@parslet_task(allow_shell=True)``.
* :func:`offline_guard` – when enabled (``--offline`` CLI flag), creation of
  sockets is blocked to keep execution fully offline.

Both guards raise :class:`SecurityError` with a clear remediation hint when
violated.
"""

from __future__ import annotations

import os
import socket
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from typing import NoReturn

__all__ = ["SecurityError", "shell_guard", "offline_guard"]


class SecurityError(RuntimeError):
    """Raised when a security sentry blocks an operation."""


@contextmanager
def shell_guard(allow: bool) -> Iterator[None]:
    """Block shell execution if ``allow`` is :data:`False`.

    The guard temporarily monkey patches :mod:`os` and :mod:`subprocess`
    helpers so that any attempt to spawn a shell raises :class:`SecurityError`.
    Tasks that genuinely require shell access must opt in via
    ``@parslet_task(allow_shell=True)``.
    """

    if allow:
        # Nothing to do when shell access is explicitly allowed.
        yield
        return

    original_os_system = os.system
    original_run = subprocess.run
    original_popen = subprocess.Popen
    original_call = subprocess.call
    original_check_output = subprocess.check_output

    def _blocked(*args: object, **kwargs: object) -> NoReturn:  # type: ignore[unused-arg]
        raise SecurityError(
            "Shell commands are disabled for this task. "
            "Use @parslet_task(allow_shell=True) to enable."
        )

    class _BlockedPopen(subprocess.Popen):  # type: ignore[type-arg]
        def __init__(self, *args: object, **kwargs: object) -> None:  # type: ignore[override]
            _blocked()

    os.system = _blocked  # type: ignore[assignment]
    subprocess.run = _blocked  # type: ignore[assignment]
    subprocess.call = _blocked  # type: ignore[assignment]
    subprocess.check_output = _blocked  # type: ignore[assignment]
    subprocess.Popen = _BlockedPopen  # type: ignore[assignment]
    try:
        yield
    finally:
        os.system = original_os_system  # type: ignore[assignment]
        subprocess.run = original_run  # type: ignore[assignment]
        subprocess.Popen = original_popen  # type: ignore[assignment]
        subprocess.call = original_call  # type: ignore[assignment]
        subprocess.check_output = original_check_output  # type: ignore[assignment]


@contextmanager
def offline_guard(enabled: bool) -> Iterator[None]:
    """Block network socket creation when ``enabled`` is :data:`True`."""

    if not enabled:
        yield
        return

    original_socket = socket.socket

    def _blocked_socket(*args: object, **kwargs: object) -> NoReturn:  # type: ignore[unused-arg]
        raise SecurityError(
            "Network access disabled via --offline. Remove flag to enable."
        )

    socket.socket = _blocked_socket  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket = original_socket  # type: ignore[assignment]
