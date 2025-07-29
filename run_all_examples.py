"""Run a set of Parslet example workflows and print their results."""

from importlib import import_module
from typing import List

from termux.helpers import is_running_in_termux

from parslet.core import DAG, DAGRunner
from examples.utils import ensure_sample_image, ensure_sample_video

MODULES: List[str] = [
    "examples.edge_mcu_sensor_processing",
    "examples.mobile_edge_inference",
    "examples.rad_parslet.rad_dag",
    "examples.rad_pipeline",
    "use_cases.offline_edu_content_builder",
    "use_cases.smart_grid_maintenance",
]

if not is_running_in_termux():
    MODULES.append("examples.video_frames")

# Path to shared assets used across examples
ASSET_PATH = ensure_sample_image()


def run_example(module_name: str) -> None:
    """Load ``module_name`` and execute its ``main()`` function."""
    try:
        module = import_module(module_name)
    except Exception as exc:  # noqa: broad-except
        print(f"Skipping {module_name}: {exc}")
        return

    if not hasattr(module, "main"):
        print(f"Skipping {module_name}: no main() function")
        return

    kwargs = {}
    if module_name in (
        "examples.mobile_edge_inference",
        "examples.rad_parslet.rad_dag",
        "examples.rad_pipeline",
    ):
        kwargs["image_path"] = str(ASSET_PATH)
    if module_name == "examples.video_frames":
        try:
            kwargs["video_path"] = str(ensure_sample_video())
        except Exception as exc:
            print(f"Skipping {module_name}: {exc}")
            return

    entry_futures = module.main(**kwargs)
    dag = DAG()
    dag.build_dag(entry_futures)
    dag.validate_dag()
    runner = DAGRunner()
    runner.run(dag)

    print(f"Results for {module_name}:")
    for future in entry_futures:
        try:
            result = future.result()
            print(f"  {future.func.__name__}: {result}")
        except Exception as exc:  # noqa: broad-except
            print(f"  {future.func.__name__}: FAILED ({exc})")

    benchmarks = runner.get_task_benchmarks()
    if benchmarks:
        print("  Benchmarks:")
        for task_id, data in benchmarks.items():
            exec_time = data.get("execution_time_s")
            time_str = f"{exec_time:.4f}s" if exec_time is not None else "N/A"
            print(f"    {task_id}: {data['status']}, {time_str}")
    print()


def run_all() -> None:
    for module_name in MODULES:
        run_example(module_name)


if __name__ == "__main__":
    run_all()
