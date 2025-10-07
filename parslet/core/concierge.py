"""Concierge orchestration utilities.

The Concierge surface gives Parslet a luxury-handcrafted feel. It produces
polished previews, curates contextual requirements and writes a runbook that
captures the story of a workflow execution.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from .context import ContextOracle, ContextResult
from .dag import DAG


@dataclass(slots=True)
class ConciergeSummary:
    """Bundle of useful counters about a DAG run."""

    total_tasks: int
    completed: int
    deferred: int
    failed: int
    skipped: int
    total_runtime: float
    slowest_task: str | None = None
    slowest_duration: float | None = None


class ConciergeOrchestrator:
    """Generate high-touch concierge experiences for Parslet runs."""

    def __init__(self, dag: DAG, oracle: ContextOracle) -> None:
        self._dag = dag
        self._oracle = oracle

    # ------------------------------------------------------------------
    # rendering helpers
    # ------------------------------------------------------------------
    def render_prologue(self) -> str:
        """Return a pre-flight briefing describing contexts and tasks."""

        lines: list[str] = []
        lines.append("╔═══════════════════════════════════════════════╗")
        lines.append("║   Parslet Concierge • Pre-flight Briefing    ║")
        lines.append("╚═══════════════════════════════════════════════╝")
        lines.append("")

        snapshot = self._oracle.snapshot()
        if snapshot:
            lines.append("Active Context Palette:")
            for name, state in snapshot.items():
                indicator = "✔" if state else "✘"
                lines.append(f"  {indicator} {name}")
        else:
            lines.append("No live detectors registered. All context decisions rely on manual overrides.")

        gated = self._task_context_rows()
        if gated:
            lines.append("")
            lines.append("Context-gated Tasks:")
            for title, status, detail in gated:
                lines.append(f"  {status} {title} {detail}")
        else:
            lines.append("")
            lines.append("All tasks are free to run without contextual gating.")

        lines.append("")
        lines.append(
            f"Luxury itinerary prepared for {len(self._dag.tasks)} tasks across "
            f"{self._dag.graph.number_of_edges()} dependencies."
        )
        return "\n".join(lines)

    def render_epilogue(self, summary: ConciergeSummary) -> str:
        """Return a closing report summarising execution."""

        lines: list[str] = []
        lines.append("")
        lines.append("╔═══════════════════════════════════════════════╗")
        lines.append("║    Parslet Concierge • Post-flight Ledger    ║")
        lines.append("╚═══════════════════════════════════════════════╝")
        lines.append("")
        lines.append(
            f"Tasks • total {summary.total_tasks} | success {summary.completed} | "
            f"deferred {summary.deferred} | skipped {summary.skipped} | failed {summary.failed}"
        )
        lines.append(f"Runtime • {summary.total_runtime:.2f}s shimmering wall-clock")
        if summary.slowest_task:
            lines.append(
                f"Signature moment • {summary.slowest_task} took {summary.slowest_duration:.2f}s"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # runbook utilities
    # ------------------------------------------------------------------
    def build_runbook(self, runner: "RunnerProtocol" | None = None) -> dict:
        """Return a JSON-serialisable structure describing the run."""

        tasks = []
        for task_id, future in self._dag.tasks.items():
            contexts = list(getattr(future, "contexts", []))
            eval_result: Iterable[ContextResult] = ()
            if contexts:
                _, eval_result = self._oracle.evaluate(contexts)
            tasks.append(
                {
                    "task_id": task_id,
                    "name": future.func.__name__,
                    "contexts": contexts,
                    "energy_cost": future.energy_cost,
                    "qos": future.qos,
                    "context_evaluation": [r.__dict__ for r in eval_result],
                }
            )

        runbook: dict[str, object] = {
            "contexts": self._oracle.snapshot(),
            "tasks": tasks,
        }

        if runner is not None:
            runbook["status"] = dict(runner.task_statuses)
            runbook["timings"] = {k: float(v) for k, v in runner.task_execution_times.items()}
        return runbook

    def write_runbook(self, path: str | Path, runner: "RunnerProtocol" | None = None) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(self.build_runbook(runner=runner), fh, indent=2)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _task_context_rows(self) -> list[tuple[str, str, str]]:
        rows: list[tuple[str, str, str]] = []
        for task_id, future in sorted(self._dag.tasks.items()):
            contexts = list(getattr(future, "contexts", []))
            if not contexts:
                continue
            allowed, results = self._oracle.evaluate(contexts)
            status_icon = "✔" if allowed else "⏸"
            detail = ", ".join(
                f"{res.requirement}{'' if res.satisfied else '✘'}" for res in results
            )
            rows.append((f"{future.func.__name__} [{task_id}]", status_icon, detail))
        return rows

    @staticmethod
    def summarise_runner(runner: "RunnerProtocol") -> ConciergeSummary:
        counts = Counter(runner.task_statuses.values())
        total = len(runner.task_statuses)
        completed = counts.get("SUCCESS", 0)
        deferred = counts.get("DEFERRED", 0)
        failed = counts.get("FAILED", 0)
        skipped = counts.get("SKIPPED", 0)
        durations = runner.task_execution_times
        total_runtime = sum(durations.values())
        slowest_task: str | None = None
        slowest_duration: float | None = None
        if durations:
            slowest_task, slowest_duration = max(durations.items(), key=lambda item: item[1])
        return ConciergeSummary(
            total_tasks=total,
            completed=completed,
            deferred=deferred,
            failed=failed,
            skipped=skipped,
            total_runtime=total_runtime,
            slowest_task=slowest_task,
            slowest_duration=slowest_duration,
        )


class RunnerProtocol:
    """Small protocol subset of :class:`parslet.core.runner.DAGRunner`."""

    task_statuses: dict[str, str]
    task_execution_times: dict[str, float]


__all__ = ["ConciergeOrchestrator", "ConciergeSummary"]

