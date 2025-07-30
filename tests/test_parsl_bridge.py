import os
import sys
import types

import pytest

from parslet.core import parslet_task
from parslet.core.parsl_bridge import convert_task_to_parsl, execute_with_parsl


class DummyFuture:
    def __init__(self, value):
        self._value = value

    def result(self):
        return self._value


def make_stub_parsl():
    parsl_mod = types.ModuleType("parsl")

    def python_app(func):
        def wrapper(*args, **kwargs):
            resolved_args = [
                a.result() if isinstance(a, DummyFuture) else a for a in args
            ]
            resolved_kwargs = {
                k: v.result() if isinstance(v, DummyFuture) else v
                for k, v in kwargs.items()
            }
            return DummyFuture(func(*resolved_args, **resolved_kwargs))

        return wrapper

    class Config:
        def __init__(self, executors=None, run_dir=None):
            self.executors = executors
            self.run_dir = run_dir

    class ThreadPoolExecutor:
        def __init__(self, label="local"):
            self.label = label

    class DFK:
        def cleanup(self):
            pass

    def dfk():
        return DFK()

    def clear():
        pass

    def load(config):
        parsl_mod.loaded_config = config
        return config

    config_mod = types.ModuleType("config")
    config_mod.Config = Config
    executors_mod = types.ModuleType("executors")
    threads_mod = types.ModuleType("threads")
    threads_mod.ThreadPoolExecutor = ThreadPoolExecutor
    executors_mod.threads = threads_mod

    parsl_mod.python_app = python_app
    parsl_mod.config = config_mod
    parsl_mod.executors = executors_mod
    parsl_mod.dfk = dfk
    parsl_mod.clear = clear
    parsl_mod.load = load

    return parsl_mod


@pytest.fixture()
def stub_parsl(monkeypatch):
    stub = make_stub_parsl()
    monkeypatch.setitem(sys.modules, "parsl", stub)
    monkeypatch.setitem(sys.modules, "parsl.config", stub.config)
    monkeypatch.setitem(sys.modules, "parsl.executors", stub.executors)
    monkeypatch.setitem(
        sys.modules, "parsl.executors.threads", stub.executors.threads
    )
    return stub


def test_convert_task_to_parsl_executes(tmp_path, stub_parsl):
    parsl = stub_parsl
    parsl.clear()
    config = parsl.config.Config(
        executors=[parsl.executors.threads.ThreadPoolExecutor(label="local")],
        run_dir=str(tmp_path),
    )
    parsl.load(config)

    def add(x, y):
        return x + y

    parsl_add = convert_task_to_parsl(add)
    result = parsl_add(1, 2).result()
    parsl.dfk().cleanup()
    assert result == 3


def test_execute_with_parsl_creates_run_dir(stub_parsl):
    parsl = stub_parsl

    @parslet_task
    def one():
        return 1

    @parslet_task
    def add_one(x):
        return x + 1

    futures = [add_one(one())]

    config = parsl.config.Config(
        executors=[parsl.executors.threads.ThreadPoolExecutor(label="local")]
    )
    results = execute_with_parsl(futures, parsl_config=config)

    assert results == [2]
    assert config.run_dir is not None
    assert os.path.isdir(config.run_dir)

    if os.path.isdir(config.run_dir):
        import shutil

        shutil.rmtree(config.run_dir)
