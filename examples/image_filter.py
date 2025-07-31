from PIL import Image, ImageFilter
from typing import List
from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.core.exporter import save_dag_to_png


@parslet_task
def load_image(image_path: str) -> Image.Image:
    """Loads an image using Pillow and returns an Image object."""
    try:
        img = Image.open(image_path)
        return img
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        raise
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        raise


@parslet_task
def convert_grayscale(image: Image.Image) -> Image.Image:
    """Converts a Pillow Image object to grayscale."""
    if image is None:
        # This handles the case where load_image might have failed and
        # returned None or if a previous task in a chain failed.
        print("Error: Input image to convert_grayscale is None.")
        # Depending on desired behavior, could raise an error or return None
        raise ValueError("Input image to convert_grayscale is None.")
    try:
        return image.convert("L")
    except Exception as e:
        print(f"Error converting image to grayscale: {e}")
        raise


@parslet_task
def apply_blur(image: Image.Image, radius: int = 2) -> Image.Image:
    """Applies a Gaussian blur to a Pillow Image object."""
    if image is None:
        print("Error: Input image to apply_blur is None.")
        raise ValueError("Input image to apply_blur is None.")
    try:
        return image.filter(ImageFilter.GaussianBlur(radius))
    except Exception as e:
        print(f"Error applying blur to image: {e}")
        raise


@parslet_task
def save_image(image: Image.Image, output_path: str) -> None:
    """Saves a Pillow Image object to the specified path."""
    if image is None:
        print("Error: Input image to save_image is None. Cannot save.")
        raise ValueError("Input image to save_image is None.")
    try:
        image.save(output_path)
        print(f"Image saved to {output_path}")
    except Exception as e:
        print(f"Error saving image to {output_path}: {e}")
        raise


def main() -> List[ParsletFuture]:
    """Defines the image filtering DAG and returns terminal futures."""
    input_image_path = "input.png"  # Dummy input image path

    # Define the DAG
    loaded_image_future = load_image(input_image_path)
    grayscale_future = convert_grayscale(loaded_image_future)
    blurred_future = apply_blur(grayscale_future, radius=3)
    save_future = save_image(blurred_future, "output_filtered.png")

    return [save_future]


if __name__ == "__main__":
    print("Parslet Image Filter Example")
    print("----------------------------")
    print(
        "This script defines a DAG to load an image, convert it to "
        "grayscale,"
    )
    print("apply a blur, and save the result.")
    print("\nIMPORTANT:")
    print(
        "To run this example, you need to create a dummy input image named "
        "'input.png'"
    )
    print("in the same directory as this script. Any PNG image will do.")
    print("For example, you can create a simple 100x100 black PNG.")
    print("----------------------------\n")

    # It's good practice to ensure Pillow is installed if this script is run
    # directly
    try:
        from PIL import Image
    except ImportError:
        print("Pillow library is not installed. Please install it by running:")
        print("pip install Pillow")
        exit(1)

    entry_futures = main()

    # Build and run the DAG
    dag = DAG(entry_futures)
    print("DAG built. Visualizing DAG...")
    save_dag_to_png(dag, "image_filter_dag.png")
    print("DAG visualization saved to image_filter_dag.png")

    print("\nRunning DAG...")
    runner = DAGRunner(dag, num_workers=2)  # Using 2 workers as an example
    results = runner.run()

    print("\nDAG Execution Results:")
    for future, result_info in results.items():
        if (
            future in entry_futures
        ):  # Typically, we are interested in the results of terminal nodes
            print(f"  Task {future.name} (Terminal Node):")
            print(f"    Status: {result_info['status']}")
            if result_info["status"] == "completed":
                print("    Output Path (if applicable): output_filtered.png")
            elif result_info["status"] == "failed":
                print(f"    Error: {result_info['error']}")
                # If load_image failed, we might not have an output.
                # The error for load_image itself will be printed by the task.
                if (
                    future.name != "load_image"
                ):  # Avoid redundant error for load_image
                    pass
            elif result_info["status"] == "skipped":
                print("    Reason: A dependency failed.")

    print("\nImage filtering workflow execution finished.")
    if all(
        res["status"] == "completed"
        for future, res in results.items()
        if future in entry_futures
    ):
        print(
            "Output image 'output_filtered.png' should be generated if all "
            "tasks succeeded."
        )
    else:
        print(
            "One or more tasks failed. 'output_filtered.png' might not be "
            "generated or complete."
        )
