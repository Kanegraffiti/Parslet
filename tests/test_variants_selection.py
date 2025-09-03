from parslet.core.task import parslet_task, task_variant


@parslet_task
def process_full() -> str:
    return "full"


@task_variant("light")
@parslet_task
def process_light() -> str:
    return "light"


def test_variant_annotation_present() -> None:
    assert process_light._parslet_variant_key == "light"
    fut = process_light()
    assert fut.variant_key == "light"
