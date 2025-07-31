"""Simple file relay helper for federated Parslet runs."""

from __future__ import annotations
import logging

import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class FileRelay:
    """Copy result files to a remote destination using ``scp`` if available."""

    def __init__(self, destination: str) -> None:
        self.destination = destination

    def send(self, *paths: str | Path) -> None:
        for p in paths:
            self._copy_file(Path(p))

    def _copy_file(self, path: Path) -> None:
        try:
            subprocess.run(
                ["scp", str(path), self.destination],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("Relayed %s to %s", path, self.destination)
        except (
            Exception
        ) as exc:  # pragma: no cover - network/scp may be absent
            logger.warning("Could not relay %s: %s", path, exc)


__all__ = ["FileRelay"]
