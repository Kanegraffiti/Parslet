from __future__ import annotations

"""RAD by Parslet pipeline example."""

from pathlib import Path
from typing import List

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from examples.rad_parslet.rad_parslet import analyze
from examples.utils import ensure_sample_image

ASSET_PATH = ensure_sample_image()


@parslet_task
def run_analysis(
    image_path: str, out_dir: str = "rad_pipeline_results"
) -> List[Path]:
    """Run the RAD analysis on ``image_path``."""
    meta, diag, review = analyze(image_path, out_dir, ignore_battery=True)
    return [meta, diag, review]


def main(image_path: str | None = None) -> List[ParsletFuture]:
    img = image_path or str(ASSET_PATH)
    fut = run_analysis(img)
    return [fut]


if __name__ == "__main__":
    dag = DAG()
    dag.build_dag(main())
    runner = DAGRunner()
    runner.run(dag)
