from ..core import parslet_task


@parslet_task
def ping() -> str:
    return "pong"
