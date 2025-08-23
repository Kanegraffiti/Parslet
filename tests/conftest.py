from __future__ import annotations

from parslet.core.task import set_allow_redefine


def pytest_sessionstart(session):
    """Allow task redefinition across tests by default."""
    set_allow_redefine(True)
