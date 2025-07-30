"""Security sentry utilities for Parslet."""

from __future__ import annotations

import ast
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_pr_changes(paths: list[Path]) -> bool:
    """Defcon 1: basic validation of changed Python files.

    Rejects files containing `exec` or `os.system` calls.
    Returns ``True`` if all files are safe.
    """

    for path in paths:
        try:
            tree = ast.parse(path.read_text())
        except Exception as exc:  # pragma: no cover - malformed file
            logger.error("Failed parsing %s: %s", path, exc)
            return False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"exec", "eval", "system"}:
                    logger.warning(
                        "Unsafe call %s found in %s", node.func.id, path
                    )
                    return False
    return True


def sandbox_task(func):
    """Defcon 2: decorator to prevent unsafe operations."""

    def wrapper(*args, **kwargs):
        for name in ("os", "subprocess"):
            if name in func.__code__.co_names:
                raise RuntimeError(f"Usage of {name} is not allowed")
        return func(*args, **kwargs)

    return wrapper


def trap_exceptions(runner):
    """Defcon 3: attach a handler to freeze the DAG and log errors."""

    def handle(exc: Exception) -> None:
        runner.logger.error("Uncaught exception: %s", exc)
        runner.dag.freeze()
        (runner.dag.root_dir / "crash.log").write_text(str(exc))

    runner.exception_handler = handle
