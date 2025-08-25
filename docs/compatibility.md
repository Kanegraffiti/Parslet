# Parsl Compatibility

Parslet can import simple Parsl workflows and export Parslet DAGs back to
Parsl. This feature is **experimental** and currently supports only
pure-Python `@python_app` tasks without data staging.

## Import from Parsl

```
parslet convert --from-parsl in.py --to-parslet out.py
```

Parsl `@python_app` functions are rewritten as `@parslet_task` and any top
level task invocations are wrapped into a `main()` function returning a list of
`ParsletFuture` objects.

See `examples/compat/parsl_demo.py` for a minimal workflow that can be
converted.

## Export to Parsl

```
parslet convert --from-parslet in.py --to-parsl out.py
```

A Parslet workflow's `main()` is executed to build a DAG. Each node is rendered
as a Parsl `@python_app` with a small driver that recreates the same task
edges.

## Caveats

* Only pure Python task bodies are handled; Bash apps or staging directives are
  ignored.
* The generated code is intended for local execution and does not configure
  providers.

# Dask Compatibility

Parslet can also import basic Dask `delayed` workflows and export Parslet DAGs
back to Dask. This is **experimental** and mirrors the Parsl caveats above.

## Import from Dask

```
parslet convert --from-dask in.py --to-parslet out.py
```

## Export to Dask

```
parslet convert --from-parslet in.py --to-dask out.py
```

The `examples/compat/dask_demo.py` script shows a tiny Dask workflow that
works with the converter.
