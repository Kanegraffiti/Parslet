# Parslet Recipes: Real-World Examples

The best way to learn Parslet is by seeing it in action. This guide breaks down the example workflows found in the `examples/` directory. Each example is a self-contained "recipe" designed to showcase a specific feature or use case.

---

### 1. The "Hello World" of Parslet

-   **File:** `examples/hello.py`
-   **Use Case:** This is the quintessential introductory example, perfect for verifying your installation and understanding the absolute basics of Parslet. It demonstrates how to define tasks and chain them together.
-   **How It Works:** The workflow performs a series of simple arithmetic operations.
    1.  Two `add` tasks are defined to run in parallel.
    2.  Two `square` tasks each take the result (the `ParsletFuture`) of one of the `add` tasks.
    3.  A final `sum_results` task takes the outputs of both `square` tasks and adds them together.
    This creates a small, diamond-shaped dependency graph.
-   **How to Run It:**
    ```bash
    parslet run examples/hello.py
    ```
-   **Expected Output:** The final result of the calculation, `100`, will be printed to your console.

---

### 2. The Offline Photo Filter

-   **File:** `examples/image_filter.py`
-   **Use Case:** Demonstrates a simple media processing pipeline that can run entirely offline on a device like a phone or Raspberry Pi. This is useful for pre-processing images before uploading them or for batch-editing tasks in areas with no connectivity.
-   **How It Works:** This recipe uses the `Pillow` library to perform a series of image manipulations.
    1.  `load_image`: Loads an image file from disk.
    2.  `convert_grayscale`: Converts the image to black and white.
    3.  `apply_blur`: Applies a Gaussian blur effect.
    4.  `save_image`: Saves the final processed image back to the disk.
-   **How to Run It:**
    1.  First, you need an input image. Create a dummy PNG file named `input.png` in the project's root directory. Any small PNG image will work.
    2.  Run the workflow from the command line:
        ```bash
        parslet run examples/image_filter.py
        ```
-   **To See the Workflow:** You can also ask Parslet to export a visual diagram of the pipeline:
    ```bash
    parslet run examples/image_filter.py --export-png pipeline.png
    ```
    This will create a file named `pipeline.png` showing the four steps connected in a line.

---

### 3. The Offline Text Cleaner

-   **File:** `examples/text_cleaner.py`
-   **Use Case:** A classic data cleaning workflow that takes a messy text file, normalizes it, and extracts useful information. This is a common first step in many natural language processing (NLP) or data analysis tasks, and Parslet allows you to do it on-device.
-   **How It Works:**
    1.  `load_text_file`: Reads the content of a text file.
    2.  `convert_to_lowercase`: Normalizes all text to be lowercase.
    3.  `remove_punctuation`: Strips out all punctuation marks.
    4.  `count_words`: Calculates the frequency of each word.
    5.  `save_word_counts`: Saves the resulting word counts as a JSON file.
-   **How to Run It:**
    1.  Create a file named `input.txt` in the project's root directory. Add some sample text, for example: `Hello Parslet! This is a test, a simple test.`
    2.  Run the workflow:
        ```bash
        parslet run examples/text_cleaner.py
        ```
-   **Expected Output:** A file named `word_counts.txt` will be created with the JSON results, and a diagram named `text_cleaner_dag.png` will be generated.

---

### 4. The Video Frame Extractor

-   **File:** `examples/video_frames.py`
-   **Use Case:** A tool for video analysis that extracts every individual frame from a video file and saves them as images. This is a foundational step for tasks like object detection in video, motion analysis, or creating GIFs.
-   **How It Works:** This workflow uses the `OpenCV` library.
    1.  `extract_frames`: Opens a video file, reads it frame by frame, and saves each frame as a separate PNG file in a `frames/` directory.
    2.  `count_frames`: Counts the total number of frames that were extracted.
-   **How to Run It:**
    1.  You need a video file. For testing, you can use the sample video provided by the utility script. The `run_all_examples.py` script can generate this for you, or you can create your own `video.mp4`.
    2.  Run the workflow, pointing it to your video file:
        ```bash
        # Make sure you have a video.mp4 file in your root directory
        parslet run examples/video_frames.py --video video.mp4
        ```
-   **Dependencies:** This example requires `opencv-python` and `numpy`, which you can install with `pip install opencv-python numpy`.

---

### 5. The RAD-Parslet Medical Imaging Pipeline

-   **Files:** `examples/rad_parslet/`, `examples/rad_pipeline.py`
-   **Use Case:** This showcases the "Radiology AI Diagnostics (RAD) by Parslet" concept. It simulates a real-world medical imaging workflow for a remote clinic where a technician can get a preliminary analysis of a scan on a local, offline device.
-   **How It Works:**
    -   The `rad_parslet.py` module contains the core logic, including two "tiny" mock AI models (`TinyMeanModel`, `TinyStdModel`) that produce a diagnosis based on simple image statistics.
    -   The `analyze` function runs both models on an image and compares their outputs. If they agree with high confidence, a diagnosis is made. If not, the image is flagged for human review.
    -   The `rad_pipeline.py` script wraps this `analyze` function in a `@parslet_task` so it can be run by the Parslet engine.
-   **How to Run It:**
    ```bash
    # This runs the simplified pipeline wrapper
    parslet run examples/rad_pipeline.py
    ```
-   **Expected Output:** A new directory `rad_pipeline_results/` will be created containing:
    -   `diagnosis.txt`: The final diagnosis ("normal", "abnormal", or "REVIEW_REQUIRED").
    -   `review_flag.txt`: `true` or `false`.
    -   `meta.json`: A file with metadata about the model versions and their agreement score.

---

### 6. Edge MCU Sensor Data Processor

-   **File:** `examples/edge_mcu_sensor_processing.py`
-   **Use Case:** Simulates a workflow for an Internet of Things (IoT) scenario. Data is collected from a low-power sensor (like a microcontroller unit), cleaned, and analyzed for anomalies. This is typical for applications in agriculture, environmental monitoring, or industrial automation.
-   **How It Works:**
    1.  `generate_sensor_data`: Creates a list of fake sensor readings with random noise and occasional spikes.
    2.  `smooth_data`: Applies a simple moving average to clean up the noise.
    3.  `detect_anomalies`: Identifies points where the data changes too abruptly.
    4.  `save_results`: Saves the cleaned data and a list of anomalies to a timestamped directory.
-   **How to Run It:**
    ```bash
    parslet run examples/edge_mcu_sensor_processing.py
    ```
-   **Expected Output:** A new directory will be created in `Parslet_Results/` containing `clean_data.csv` and `anomalies.json`.
