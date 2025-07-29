from pathlib import Path
import time
from PIL import Image, ImageFilter
from parslet.core import parslet_task, DAG, DAGRunner
from parslet.utils.resource_utils import get_battery_level


@parslet_task
def delay_if_low(threshold: int = 20):
    level = get_battery_level()
    if level is not None and level < threshold:
        time.sleep(1)  # simulate waiting for charge
    return True


@parslet_task
def load_image(path: str):
    return Image.open(path)


@parslet_task
def enhance(img: Image.Image):
    return img.filter(ImageFilter.SHARPEN)


@parslet_task
def save(img: Image.Image, out: str):
    p = Path(out)
    img.save(p)
    return str(p)


def main():
    _ = delay_if_low()
    img = load_image("photo.jpg")
    enhanced = enhance(img)
    saved = save(enhanced, "enhanced.jpg")
    return [saved]


if __name__ == "__main__":
    dag = DAG()
    dag.build_dag(main())
    runner = DAGRunner()
    runner.run(dag)
