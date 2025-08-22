"""Deterministic task result caching utilities."""

from __future__ import annotations

import hashlib
import json
import os
import pickle
from pathlib import Path

__all__ = ["compute_cache_key", "load_from_cache", "save_to_cache", "get_cache_dir"]


def _safe_serialize(obj: object) -> object:
    """Serialize ``obj`` into JSON-friendly structures.

    Non-JSON-serializable objects fall back to ``repr`` strings. Collections
    are processed recursively to ensure deterministic ordering.
    """
    if isinstance(obj, str | int | float | bool) or obj is None:
        return obj
    if isinstance(obj, list | tuple):
        return [_safe_serialize(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) for k, v in sorted(obj.items())}
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return repr(obj)


def compute_cache_key(
    task_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    version: str = "1",
) -> str:
    """Compute a deterministic hash for a task invocation.

    Parameters
    ----------
    task_name:
        Registered name of the task.
    args:
        Positional arguments supplied to the task.
    kwargs:
        Keyword arguments supplied to the task.
    version:
        Optional manual version string to bust caches when the implementation
        changes.
    """
    payload = {
        "task": task_name,
        "version": version,
        "args": _safe_serialize(args),
        "kwargs": _safe_serialize(kwargs),
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def get_cache_dir() -> Path:
    """Return the directory used for storing cache files."""
    base = os.environ.get("PARSLET_CACHE_DIR", os.path.expanduser("~/.parslet/cache"))
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_from_cache(key: str) -> object:
    """Load a cached value for ``key`` if present."""
    cache_file = get_cache_dir() / f"{key}.pkl"
    if cache_file.exists():
        with cache_file.open("rb") as fh:
            return pickle.load(fh)
    raise FileNotFoundError(key)


def save_to_cache(key: str, value: object) -> None:
    """Persist ``value`` for ``key`` to the cache."""
    cache_file = get_cache_dir() / f"{key}.pkl"
    with cache_file.open("wb") as fh:
        pickle.dump(value, fh)
