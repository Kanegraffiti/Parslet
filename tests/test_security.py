import os
import socket

import pytest

from parslet.core import DAG, DAGRunner, parslet_task
from parslet.core.task import _TASK_REGISTRY, set_allow_redefine
from parslet.security import SecurityError, offline_guard


def test_name_collision_and_allow_redefine() -> None:
    set_allow_redefine(False)
    try:

        @parslet_task(name="dup_test")
        def first() -> int:
            return 1

        with pytest.raises(ValueError):

            @parslet_task(name="dup_test")
            def second() -> int:
                return 2

        @parslet_task(name="dup_test", allow_redefine=True)
        def third() -> int:
            return 3

    finally:
        _TASK_REGISTRY.pop("dup_test", None)
        set_allow_redefine(True)


def test_shell_guard_blocks_and_allows() -> None:
    @parslet_task(name="sh_block")
    def sh_block() -> None:
        os.system("true")

    @parslet_task(name="sh_allow", allow_shell=True)
    def sh_allow() -> int:
        return os.system("true")

    fut_block = sh_block()
    fut_allow = sh_allow()

    dag_block = DAG()
    dag_block.build_dag([fut_block])
    dag_allow = DAG()
    dag_allow.build_dag([fut_allow])

    runner = DAGRunner()
    with pytest.raises(SecurityError):
        runner.run(dag_block)

    runner = DAGRunner()
    runner.run(dag_allow)
    assert fut_allow.result() == 0

    _TASK_REGISTRY.pop("sh_block", None)
    _TASK_REGISTRY.pop("sh_allow", None)


def test_offline_guard_blocks_socket() -> None:
    with offline_guard(True):
        with pytest.raises(SecurityError):
            socket.socket()
    # And when disabled it should work
    with offline_guard(False):
        s = socket.socket()
        s.close()
