from parslet.core import DAG, DAGRunner, ParsletFuture, parslet_task


def test_public_imports() -> None:
    assert all([parslet_task, ParsletFuture, DAG, DAGRunner])
