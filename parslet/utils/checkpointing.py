import json
from pathlib import Path
from typing import Set
import logging

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manage task checkpoints using a simple JSON file."""

    def __init__(self, filepath: str) -> None:
        """Create a new manager for ``filepath``.

        The file is loaded if it already exists so that previously completed
        task IDs are remembered.
        """
        self.filepath = Path(filepath)
        self.completed: Set[str] = set()
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.completed = {
                        tid
                        for tid, status in data.items()
                        if status == "SUCCESS"
                    }
            except Exception as e:  # pragma: no cover - file may be malformed
                logger.warning(
                    f"Could not read checkpoint file {self.filepath}: {e}"
                )

    def mark_complete(self, task_id: str, status: str) -> None:
        """Record a successfully finished task.

        Parameters
        ----------
        task_id:
            The unique identifier of the task.
        status:
            The final status reported for the task. Only ``"SUCCESS"`` values
            are persisted.
        """
        if status != "SUCCESS":
            return

        self.completed.add(task_id)
        data = {tid: "SUCCESS" for tid in self.completed}
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:  # pragma: no cover - disk write error
            logger.warning(
                f"Failed to update checkpoint file {self.filepath}: {e}"
            )
