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
