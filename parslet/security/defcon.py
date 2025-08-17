"""Parslet DEFCON security checks.

These lightweight guards are intentionally self‑contained so they operate
reliably in offline environments.
"""

import ast
import hashlib
import hmac
import logging
from pathlib import Path
from typing import Callable, Iterable

logger = logging.getLogger(__name__)


class Defcon:
    """Security layer with multiple levels."""

    #: Calls that are considered unsafe for :meth:`scan_code`.
    BAD_CALLS = frozenset({"eval", "exec"})

    @staticmethod
    def scan_code(paths: Iterable[Path]) -> bool:
        """DEFCON1: scan for dangerous calls."""
        for path in paths:
            try:
                tree = ast.parse(path.read_text())
            except Exception as exc:
                logger.error("parse error %s: %s", path, exc)
                return False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(
                    node.func, ast.Name
                ):
                    if node.func.id in Defcon.BAD_CALLS:
                        logger.error(
                            "Forbidden call %s in %s", node.func.id, path
                        )
                        return False
        return True

    @staticmethod
    def verify_chain(dag_hash: str, signature_file: Path) -> bool:
        """DEFCON2: verify DAG hash against signature."""
        if not signature_file.exists():
            return True
        sig = signature_file.read_text().strip()
        calc = hashlib.sha256(sig.encode()).hexdigest()
        return hmac.compare_digest(calc, dag_hash)

    @staticmethod
    def tamper_guard(watched: Iterable[Path]) -> Callable[[], bool]:
        """DEFCON3: ensure files unchanged."""
        hashes = {
            p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched
        }

        def unchanged() -> bool:
            for p, h in hashes.items():
                if (
                    not p.exists()
                    or hashlib.sha256(p.read_bytes()).hexdigest() != h
                ):
                    logger.error("Tamper detected for %s", p)
                    return False
            return True

        return unchanged
