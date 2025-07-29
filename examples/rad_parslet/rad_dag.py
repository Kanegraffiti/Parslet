from parslet.core import DAG, DAGRunner, parslet_task
from examples.utils import ensure_sample_image
from .rad_parslet import analyze

# Path to the demo image bundled with the repository
ASSET_PATH = ensure_sample_image()


@parslet_task
def run_rad(image: str, out_dir: str, ignore_battery: bool = False):
    return analyze(image, out_dir, ignore_battery=ignore_battery)


def main(image_path: str | None = None, out_dir: str = "rad_results"):
    img = image_path or str(ASSET_PATH)
    fut = run_rad(img, out_dir)
    return [fut]


if __name__ == "__main__":
    dag = DAG()
    dag.build_dag(main())
    runner = DAGRunner()
    runner.run(dag)
