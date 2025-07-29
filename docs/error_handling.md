# Error Handling Guide

This document highlights common issues reported by users of Parsl and Dask and explains how Parslet addresses them.

## Parsl Issues
- **HTEX hangs due to incorrect `run_dir` references** ([Parsl issue #3874](https://github.com/Parsl/parsl/issues/3874))
  - Parslet's `execute_with_parsl` helper now creates a unique `run_dir` by default to avoid stale path references when multiple workflows are run sequentially in the same process.
- **Usage tracking prevents clean shutdown** ([Parsl issue #3831](https://github.com/Parsl/parsl/issues/3831))
  - Telemetry is disabled by default using the environment variable `PARSL_TELEMETRY_ENABLED=false`.

## Dask Issues
The core of Parslet does not depend on Dask, but users may integrate Dask for heavy computation. Some common Dask issues include confusing warning messages or APIs with surprising behavior. When using Dask within Parslet tasks:
- prefer explicit array/dataframe operations to `apply` to avoid [design pitfalls](https://github.com/dask/dask/issues/11961).
- check the output of `warn_dtype_mismatch()` for clarity ([#11978](https://github.com/dask/dask/issues/11978)).

## General Recommendations
- Always capture exceptions within tasks and re-raise with context if appropriate.
- Use `DAGRunner.get_task_benchmarks()` to inspect task status and execution times after a run.
- Run workflows with `--checkpoint-file <file>` to save progress. Parslet also logs a warning if no network connection or an active VPN is detected so you can troubleshoot network-related failures.
