import sys
import types

import pytest

from parslet.core.task import parslet_task
from parslet.hybrid.executor import execute_hybrid


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
                a.result() if hasattr(a, "result") else a for a in args
            ]
            resolved_kwargs = {
                k: v.result() if hasattr(v, "result") else v
                for k, v in kwargs.items()
            }
            return DummyFuture(func(*resolved_args, **resolved_kwargs))

        return wrapper

    class Config:
        def __init__(self, executors=None):
            self.executors = executors
            self.run_dir = None

    class ThreadPoolExecutor:
        def __init__(self, label="remote"):
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


def test_execute_hybrid_mixes_local_and_remote(stub_parsl):
    parsl = stub_parsl

    @parslet_task
    def one():
        return 1

    @parslet_task(remote=True)
    def add_one(x):
        return x + 1

    results = execute_hybrid([add_one(one())])
    parsl.dfk().cleanup()
    assert results == [2]
