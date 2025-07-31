# Visual Assets Guide

This table lists the image placeholders that will be referenced throughout the
documentation. Create your own diagrams with the same filenames so that the
examples work without modification.  See ``../assets/README.md`` for the actual
images included in this repository.

| Filename | Suggested Content | Size |
|----------|------------------|------|
| `dag_overview.png` | A simple DAG showing three tasks connected in sequence. Use clear node labels. | 800x400px |
| `image_pipeline.png` | Illustration of the image processing example (load → grayscale → blur → save). | 800x300px |
| `text_pipeline.png` | Diagram of the text_cleaner workflow with four steps. | 800x300px |
| `parsl_bridge.png` | Conceptual graphic showing Parslet tasks being converted to Parsl apps. | 800x300px |
| `architecture.png` | High‑level view of Parslet's core components (tasks, DAG, runner). | 800x400px |

All images should have a transparent background when possible and use a consistent colour scheme. Save them under this `docs/visuals/` directory so the documentation can reference them uniformly.
