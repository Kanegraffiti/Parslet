# RAD by Parslet Example

This example demonstrates the "RAD" (Radiology AI Diagnostics) module running with Parslet.

## What it does
- Applies two lightweight image models to detect abnormalities.
- Generates a `diagnosis.txt` and a `review_flag.txt` indicating confidence agreement.
- Saves metadata including model hashes to `meta.json`.

## Input format
Place input images (PNG/JPEG) in this directory and update the path when calling `analyze()`.

## Result meaning
 - `diagnosis.txt` contains the final label (`normal`, `abnormal`, or `REVIEW_REQUIRED`).
   Results are only accepted automatically when both models output the same label
   and their agreement score is **85%** or higher; otherwise `REVIEW_REQUIRED` is
   recorded.
 - `review_flag.txt` becomes `true` if predictions disagree or fall below the 85%
   threshold.
 - `meta.json` stores model versions and the computed agreement score for auditing.

## Offline usage
Run the analysis locally without network access or use the Parslet DAG wrapper:

```bash
python rad_parslet.py /path/to/image.png results/ --ignore-battery
```

Or run the DAG version:

```bash
parslet run examples/rad_parslet/rad_dag.py
```
