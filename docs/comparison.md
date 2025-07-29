# Comparison: Parslet, Parsl and Dask

The table below outlines some key differences between Parslet, Parsl and Dask. The goal is to highlight where each tool excels and how they might complement one another.

| Feature | Parslet | Parsl | Dask |
|---------|--------|-------|------|
| Focus | Lightweight, local DAG execution | Large-scale, distributed workflows | Distributed computation and collections |
| Installation | Few dependencies, runs without a cluster | Requires Parsl and an executor backend | Often used with distributed clusters or `dask.distributed` |
| Task Definition | `@parslet_task` decorator returning `ParsletFuture` objects | `@python_app` or `@bash_app` decorators | `dask.delayed` or high-level APIs like Dask DataFrame |
| Execution | Thread pool on local machine | Flexible execution backends (HTCondor, Kubernetes, etc.) | Scheduler processes and workers (local or distributed) |
| Best For | Simple offline pipelines and education | HPC and large-scale scientific workflows | Parallelizing Python analytics and data engineering |
| Parslet Compatibility | Native | Supported via `parslet.core.parsl_bridge` | Manual conversion required |

Use Parslet when you need a minimal dependency DAG runner. Move to Parsl if you require remote execution or integration with HPC resources. Dask is often chosen for large-scale data analysis but can work alongside Parsl or Parslet when needed.
