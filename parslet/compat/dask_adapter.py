"""Dask compatibility helpers and AST translators for Parslet.

This module provides lightweight substitutes for common ``dask`` entry points
so that code using ``dask.delayed`` can be executed by Parslet.  It also
contains AST transformers for programmatic translation of source code from Dask
syntax to Parslet syntax.
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Callable
from pathlib import Path
from textwrap import dedent

from ..core.dag import DAG
from ..core.task import ParsletFuture, parslet_task


class DaskToParsletTranslator(ast.NodeTransformer):
    """Replace Dask delayed constructs with Parslet equivalents."""

    def __init__(self) -> None:
        super().__init__()
        # Track aliases for ``delayed`` so we can recognise them later. The
        # default set contains the bare name but additional aliases may be
        # added when encountering ``from dask import delayed as <alias>``
        # statements.
        self.delayed_aliases: set[str] = {"delayed"}

    # ------------------------------------------------------------------
    # Import handling
    # ------------------------------------------------------------------
    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:  # noqa: D401
        """Record any aliases of ``dask.delayed``."""
        if node.module == "dask":
            for alias in node.names:
                if alias.name == "delayed":
                    self.delayed_aliases.add(alias.asname or alias.name)
        return self.generic_visit(node)

    # ------------------------------------------------------------------
    # Function definitions and calls
    # ------------------------------------------------------------------
    def _is_delayed(self, expr: ast.AST) -> bool:
        """Return ``True`` if *expr* refers to ``dask.delayed``."""

        if isinstance(expr, ast.Name):
            return expr.id in self.delayed_aliases
        if isinstance(expr, ast.Attribute):
            return expr.attr == "delayed"
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Convert ``@delayed`` (or alias) decorators to ``@parslet_task``."""

        for idx, decorator in enumerate(node.decorator_list):
            if self._is_delayed(decorator):
                node.decorator_list[idx] = ast.Name(id="parslet_task", ctx=ast.Load())
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Strip ``.compute()`` calls so Parslet's runner manages execution."""
        if isinstance(node.func, ast.Attribute) and node.func.attr == "compute":
            # Convert obj.compute() -> obj
            return self.visit(node.func.value)

        # ``dask.delayed(func)(...)`` pattern
        if isinstance(node.func, ast.Call) and self._is_delayed(node.func.func):
            inner = node.func
            node.func = ast.Call(
                func=ast.Name(id="parslet_task", ctx=ast.Load()),
                args=inner.args,
                keywords=inner.keywords,
            )
            return self.generic_visit(node)

        if self._is_delayed(node.func):
            node.func = ast.Name(id="parslet_task", ctx=ast.Load())
        return self.generic_visit(node)


def convert_dask_to_parslet(code: str) -> str:
    """Convert Dask-based code string to Parslet syntax."""
    tree = ast.parse(code)
    transformed = DaskToParsletTranslator().visit(tree)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed)


def import_dask_script(src: str, dest: str) -> None:
    """Convert a simple Dask workflow file to Parslet syntax."""

    code = Path(src).read_text()
    tree = ast.parse(code)
    tree = DaskToParsletTranslator().visit(tree)
    ast.fix_missing_locations(tree)

    task_names: set[str] = set()
    new_body: list[ast.stmt] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == "parslet_task":
                    task_names.add(node.name)
            new_body.append(node)

    call_stmts: list[ast.stmt] = []
    assigned: list[str] = []
    used: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign | ast.Expr):
            value = node.value if isinstance(node, ast.Assign) else node.value
            if (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id in task_names
            ):
                if isinstance(node, ast.Expr):
                    tmp = f"tmp_{len(assigned)}"
                    node = ast.Assign(
                        targets=[ast.Name(id=tmp, ctx=ast.Store())], value=value
                    )
                    assigned.append(tmp)
                else:
                    if isinstance(node.targets[0], ast.Name):
                        assigned.append(node.targets[0].id)
                for arg in value.args:
                    if isinstance(arg, ast.Name):
                        used.add(arg.id)
                call_stmts.append(node)
                continue
        if isinstance(node, ast.ImportFrom) and node.module == "dask":
            continue
        if isinstance(node, ast.Import) and any(
            alias.name == "dask" for alias in node.names
        ):
            continue

    sinks = [name for name in assigned if name not in used]
    main_body = call_stmts + [
        ast.Return(
            value=ast.List(
                elts=[ast.Name(id=s, ctx=ast.Load()) for s in sinks], ctx=ast.Load()
            )
        )
    ]
    main_fn = ast.FunctionDef(
        name="main",
        args=ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
        ),
        body=main_body,
        decorator_list=[],
        returns=None,
    )
    imports = [
        ast.ImportFrom(
            module="parslet", names=[ast.alias(name="parslet_task")], level=0
        )
    ]
    mod = ast.Module(body=imports + new_body + [main_fn], type_ignores=[])
    ast.fix_missing_locations(mod)
    Path(dest).write_text(ast.unparse(mod) + "\n")


def export_dask_dag(futures: list[ParsletFuture], dest: str) -> None:
    """Export a Parslet DAG to a Dask-style Python script."""

    dag = DAG()
    dag.build_dag(futures)

    lines: list[str] = ["from dask import delayed", "", ""]

    seen_funcs: set[object] = set()
    for fut in dag.tasks.values():
        if fut.func in seen_funcs:
            continue
        seen_funcs.add(fut.func)
        src = dedent(inspect.getsource(fut.func))
        func_lines = [ln for ln in src.splitlines() if not ln.strip().startswith("@")]
        lines.append("@delayed")
        lines.extend(func_lines)
        lines.append("")

    lines.append("def main():")
    import networkx as nx

    order = list(nx.topological_sort(dag.graph))
    name_map: dict[str, str] = {}
    used_names: set[str] = set()
    for idx, tid in enumerate(order):
        fut = dag.tasks[tid]
        base = fut.func.__name__
        name = base if base not in used_names else f"{base}_{idx}"
        used_names.add(name)
        name_map[tid] = name
        args: list[str] = []
        for arg in fut.args:
            if isinstance(arg, ParsletFuture):
                args.append(name_map[arg.task_id])
            else:
                args.append(repr(arg))
        lines.append(f"    {name} = {fut.func.__name__}({', '.join(args)})")

    sinks = [name_map[n] for n in dag.graph.nodes if dag.graph.out_degree(n) == 0]
    lines.append(f"    return [{', '.join(sinks)}]")

    Path(dest).write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Runtime compatibility shims
# ---------------------------------------------------------------------------


def delayed(_func: Callable | None = None, **kwargs: object) -> Callable:
    """Dask ``delayed`` decorator mapped to :func:`parslet_task`."""

    def wrapper(func: Callable) -> Callable:
        return parslet_task(func, **kwargs)

    if _func is None:
        return wrapper
    return wrapper(_func)


def compute(*futures: ParsletFuture) -> object:
    """Evaluate one or more ``ParsletFuture`` objects like ``dask.compute``."""

    results = [f.result() for f in futures]
    if len(results) == 1:
        return results[0]
    return tuple(results)


__all__ = [
    "DaskToParsletTranslator",
    "convert_dask_to_parslet",
    "import_dask_script",
    "export_dask_dag",
    "delayed",
    "compute",
    "ParsletFuture",
]
