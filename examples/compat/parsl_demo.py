from __future__ import annotations

from parsl import python_app


@python_app
def add(x: int, y: int) -> int:
    return x + y


def main() -> int:
    fut = add(1, 2)
    return fut.result()
