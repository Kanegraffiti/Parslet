import importlib.util
import types
import sys
from pathlib import Path
import pytest

pytest.importorskip("dask")

project_root = Path(__file__).resolve().parents[1]

# Create minimal 'parslet' and 'parslet.core' packages to avoid executing
# the package ``__init__`` (which depends on heavy runtime components).
parslet_pkg = types.ModuleType("parslet")
parslet_pkg.__path__ = [str(project_root / "parslet")]
sys.modules.setdefault("parslet", parslet_pkg)

core_pkg = types.ModuleType("parslet.core")
core_pkg.__path__ = [str(project_root / "parslet/core")]
sys.modules.setdefault("parslet.core", core_pkg)

task_spec = importlib.util.spec_from_file_location(
    "parslet.core.task", project_root / "parslet/core/task.py"
)
task_mod = importlib.util.module_from_spec(task_spec)
task_spec.loader.exec_module(task_mod)
sys.modules["parslet.core.task"] = task_mod
setattr(core_pkg, "task", task_mod)

bridge_spec = importlib.util.spec_from_file_location(
    "parslet.core.dask_bridge", project_root / "parslet/core/dask_bridge.py"
)
bridge_mod = importlib.util.module_from_spec(bridge_spec)
bridge_spec.loader.exec_module(bridge_mod)
sys.modules["parslet.core.dask_bridge"] = bridge_mod
setattr(core_pkg, "dask_bridge", bridge_mod)

parslet_task = task_mod.parslet_task
execute_with_dask = bridge_mod.execute_with_dask


def test_execute_with_dask_threads():
    @parslet_task
    def one():
        return 1

    @parslet_task
    def add_one(x):
        return x + 1

    futures = [add_one(one())]
    results = execute_with_dask(futures)
    assert results == [2]


def test_execute_with_dask_client():
    dask = pytest.importorskip("dask.distributed")

    @parslet_task
    def one():
        return 1

    @parslet_task
    def add_one(x):
        return x + 1

    futures = [add_one(one())]

    client = dask.Client(processes=False, n_workers=1, threads_per_worker=1)
    try:
        results = execute_with_dask(futures, scheduler=client)
        assert results == [2]
    finally:
        client.close()
