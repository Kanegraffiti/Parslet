from __future__ import annotations

from dask import compute, delayed


@delayed
def add(x: int, y: int) -> int:
    return x + y


def main() -> int:
    return compute(add(1, 2))[0]
