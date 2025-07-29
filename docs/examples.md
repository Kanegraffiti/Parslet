# Parslet Case Studies

This page highlights a few small workflows that demonstrate how Parslet can be used in practice. Each example ships with the repository under `examples/`.

## 1. Hello Workflow

File: `examples/hello.py`

This introductory workflow consists of three small tasks that perform basic arithmetic. It illustrates how to declare tasks, link them through dependencies and run the resulting DAG using the CLI.

Run it with:

```bash
parslet run examples/hello.py
```

## 2. Image Processing Pipeline

File: `examples/image_filter.py`

This case study shows how Parslet can orchestrate image manipulation using the Pillow library. The pipeline loads an image, converts it to grayscale, blurs it and then writes the result back to disk. Because each step is a task, operations that do not depend on one another can run in parallel.

```
load_image --> to_grayscale --> blur_image --> save_image
```

Use `--export-png` to visualize the DAG:

```bash
parslet run examples/image_filter.py --export-png pipeline.png
```

## 3. Text Cleaning and Analysis

File: `examples/text_cleaner.py`

This workflow ingests plain text, removes punctuation, performs basic normalization and counts word frequencies. The final counts are stored as JSON. It is a good template for building data-cleaning pipelines that run entirely offline.

Execute it with:

```bash
parslet run examples/text_cleaner.py
```

## 4. RAD Pipeline

File: `examples/rad_pipeline.py`

This workflow showcases the **RAD by Parslet** pipeline used on edge devices. It runs two lightweight models on an image and stores the metadata and diagnosis.

```bash
parslet run examples/rad_pipeline.py
```

## 5. Video Frame Extraction

File: `examples/video_frames.py`

Extracts frames from a video file using OpenCV (if installed) and counts them.

```bash
parslet run examples/video_frames.py --video my_video.mp4
```

## 6. CSV Cleaning and Classification

File: `examples/csv_clean_classify/workflow.py`

Loads a local CSV file, removes empty rows, classifies them with a simple rule
and writes the cleaned data to a new CSV.

```bash
parslet run examples/csv_clean_classify/workflow.py
```

## 7. Edge Sensor Processing

File: `examples/edge_mcu_sensor_processing.py`

Simulates sensor readings on a microcontroller, smooths the data, detects
anomalies and stores diagnostic logs.

```bash
parslet run examples/edge_mcu_sensor_processing.py
```

## 8. Mobile Edge Inference

File: `examples/mobile_edge_inference.py`

Runs a lightweight image classification model offline. If the optional
`transformers` package is available it will be used; otherwise a fallback result
is produced.

```bash
parslet run examples/mobile_edge_inference.py
```

## 9. Multi-AI Diagnosis

File: `examples/multi_ai_diagnosis.py`

Combines outputs from two models to analyze a medical scan. The final diagnosis
is only accepted if the models agree, otherwise a human review flag is written.

```bash
parslet run examples/multi_ai_diagnosis.py
```

## 10. Photo Enhancer

File: `examples/photo_enhancer/workflow.py`

Sharpens a photo with Pillow. If the device battery is low the workflow waits
briefly before proceeding.

```bash
parslet run examples/photo_enhancer/workflow.py
```

## 11. RAD Parslet DAG

File: `examples/rad_parslet/rad_dag.py`

Wrapper around the radiology helper utilities. It runs two tiny models on an
image and saves metadata, diagnosis and a review flag.

```bash
parslet run examples/rad_parslet/rad_dag.py
```

## 12. Telecom Tower Power Monitor

File: `use_cases/telecom_power_monitor.py`

Analyzes power logs from a remote telecom tower to forecast maintenance needs.
The workflow computes average battery level, generator runtime and solar output
to recommend actions like battery replacement or generator inspection. It is
designed to run offline at the tower site.

```bash
parslet run use_cases/telecom_power_monitor.py
```

These examples are intentionally small so they remain approachable for newcomers. Inspect the source code for each example to see how tasks pass their results to subsequent tasks using `ParsletFuture` objects.

## Running all examples

A helper script `run_all_examples.py` executes several workflows sequentially and prints both their results and timing information.

```bash
python run_all_examples.py
```

Any example requiring optional dependencies will be skipped automatically so the rest can still run.
\nExample outputs can be found in `docs/assets/example_logs/`.
