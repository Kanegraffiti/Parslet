import pytest

pytest.importorskip("dask")

from parslet.core.dask_bridge import execute_with_dask
from parslet.core.task import parslet_task


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
