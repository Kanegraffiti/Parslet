# Parsl and Dask Compatibility

Parslet ships with a small compatibility layer that enables two kinds of
interoperability:

1. **Runtime shims** that mimic parts of the Parsl and Dask APIs so that
   lightweight scripts can execute under Parslet with little or no modification.
2. **Source-to-source converters** that translate code between frameworks using
   abstract syntax tree (AST) rewriting.

## Parsl

### Runtime wrappers

`parslet.compat.python_app` and `parslet.compat.bash_app` behave like
Parsl's decorators but schedule tasks on Parslet's `DAGRunner`:

```python
from parslet.compat import python_app

@python_app
def hello(name):
    return f"Hello {name}"
```

### Converting Parsl to Parslet

```bash
parslet convert --from-parsl in.py --to-parslet out.py
```

The converter rewrites `@python_app` functions as `@parslet_task` and wraps
top-level invocations into a `main()` function returning `ParsletFuture` objects.
See `examples/compat/parsl_demo.py` for a minimal workflow.

### Exporting Parslet to Parsl

```bash
parslet convert --from-parslet recipe.py --to-parsl recipe_parsl.py
```

Each node in the Parslet DAG is rendered as a Parsl `@python_app` and connected
with the same edges.

## Dask

### Runtime wrappers

Drop-in replacements for `dask.delayed` and `dask.compute` live in
`parslet.compat.delayed` and `parslet.compat.compute`:

```python
from parslet.compat import delayed, compute

@delayed
def add(a, b):
    return a + b

total = compute(add(1, 2))[0]
```

### Converting Dask to Parslet

```bash
parslet convert --from-dask pipeline.py --to-parslet pipeline_parslet.py
```

### Exporting Parslet to Dask

```bash
parslet convert --from-parslet recipe.py --to-dask recipe_dask.py
```

`examples/compat/dask_demo.py` provides a tiny workflow that round-trips through the converter.

## Caveats

* Only pure Python task bodies are handled; Bash apps, staging directives and
  provider configurations are ignored.
* The generated code targets local execution. Additional tuning is required for
  distributed or HPC environments.
* This compatibility layer is **experimental**—always review the output before
  relying on it for production work.
