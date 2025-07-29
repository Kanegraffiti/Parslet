"""Parslet DEFCON security checks."""

import ast
import hashlib
import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


class Defcon:
    """Security layer with multiple levels."""

    @staticmethod
    def scan_code(paths: Iterable[Path]) -> bool:
        """DEFCON1: scan for dangerous calls."""
        bad = {"eval", "exec"}
        for path in paths:
            try:
                tree = ast.parse(path.read_text())
            except Exception as exc:
                logger.error("parse error %s: %s", path, exc)
                return False
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in bad:
                        logger.error("Forbidden call %s in %s", node.func.id, path)
                        return False
        return True

    @staticmethod
    def verify_chain(dag_hash: str, signature_file: Path) -> bool:
        """DEFCON2: verify DAG hash against signature."""
        if not signature_file.exists():
            return True
        sig = signature_file.read_text().strip()
        return hashlib.sha256(sig.encode()).hexdigest() == dag_hash

    @staticmethod
    def tamper_guard(watched: Iterable[Path]) -> bool:
        """DEFCON3: ensure files unchanged."""
        hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}

        def unchanged() -> bool:
            for p, h in hashes.items():
                if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != h:
                    logger.error("Tamper detected for %s", p)
                    return False
            return True

        return unchanged
