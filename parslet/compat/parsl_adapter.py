"""Parsl compatibility helpers and AST translators for Parslet.

This module exposes lightweight shims that mimic a subset of the ``parsl``
API so that existing code written for Parsl can run on top of Parslet with
minimal changes.  It also provides AST transformers for converting source code
from Parsl syntax to Parslet syntax.
"""

# ruff: noqa: ANN001,ANN201,ANN202,ANN204,ANN003,ANN002
# mypy: ignore-errors

from __future__ import annotations

import ast
import functools
import inspect
import subprocess
import uuid
import warnings
from pathlib import Path
from textwrap import dedent

from ..core.dag import DAG
from ..core.task import ParsletFuture, parslet_task


class ParslToParsletTranslator(ast.NodeTransformer):
    """Replace Parsl decorators and APIs with Parslet equivalents."""

    PARSL_DECORATORS = {"python_app", "bash_app"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Replace ``@python_app``/``@bash_app`` with ``@parslet_task``."""
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and decorator.id in self.PARSL_DECORATORS
            ):
                decorator.id = "parslet_task"
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Emit a warning when ``DataFlowKernel`` is used."""
        if isinstance(node.func, ast.Name) and node.func.id == "DataFlowKernel":
            warnings.warn(
                "Parsl DataFlowKernel is not supported; Parslet manages "
                "scheduling internally.",
                stacklevel=2,
            )
        return self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "DataFlowKernel"
        ):
            # drop assignment
            return ast.Pass()
        return self.generic_visit(node)


def convert_parsl_to_parslet(code: str) -> str:
    """Convert Parsl-based code string to Parslet syntax."""
    tree = ast.parse(code)
    transformed = ParslToParsletTranslator().visit(tree)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed)


class ParsletToParslTranslator(ast.NodeTransformer):
    """Replace Parslet decorators with Parsl equivalents."""

    PARSLET_DECORATORS = {"parslet_task"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Name)
                and decorator.id in self.PARSLET_DECORATORS
            ):
                decorator.id = "python_app"
        return self.generic_visit(node)


def convert_parslet_to_parsl(code: str) -> str:
    """Convert Parslet-based code string to Parsl syntax."""
    tree = ast.parse(code)
    transformed = ParsletToParslTranslator().visit(tree)
    ast.fix_missing_locations(transformed)
    return ast.unparse(transformed)


def import_parsl_script(src: str, dest: str) -> None:
    """Convert a simple Parsl workflow file to Parslet syntax.

    Parameters
    ----------
    src : str
        Path to the Parsl script.
    dest : str
        Destination path for the generated Parslet workflow.
    """

    code = Path(src).read_text()
    tree = ast.parse(code)

    task_names: set[str] = set()
    new_body: list[ast.stmt] = []

    # First pass: rename decorators and collect task names
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == "python_app":
                    dec.id = "parslet_task"
                    task_names.add(node.name)
            new_body.append(node)

    # Second pass: gather task invocations and keep other statements
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
        if isinstance(node, ast.ImportFrom) and node.module == "parsl":
            continue
        if isinstance(node, ast.Import) and any(
            alias.name == "parsl" for alias in node.names
        ):
            continue
        if node not in new_body:
            new_body.append(node)

    sinks = [name for name in assigned if name not in used]

    main_body = call_stmts + [
        ast.Return(
            value=ast.List(
                elts=[ast.Name(id=s, ctx=ast.Load()) for s in sinks], ctx=ast.Load()
            )
        )
    ]
    main_def = ast.FunctionDef(
        name="main",
        args=ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
        ),
        body=main_body,
        decorator_list=[],
        returns=ast.Subscript(
            value=ast.Name(id="List", ctx=ast.Load()),
            slice=ast.Name(id="ParsletFuture", ctx=ast.Load()),
            ctx=ast.Load(),
        ),
    )

    imports = [
        ast.ImportFrom(module="typing", names=[ast.alias(name="List")], level=0),
        ast.ImportFrom(
            module="parslet",
            names=[ast.alias(name="parslet_task"), ast.alias(name="ParsletFuture")],
            level=0,
        ),
    ]

    tree.body = imports + new_body + [main_def]
    ast.fix_missing_locations(tree)
    Path(dest).write_text(ast.unparse(tree) + "\n")


def export_parsl_dag(futures: list[ParsletFuture], dest: str) -> None:
    """Export a Parslet DAG to a Parsl-style Python script."""

    dag = DAG()
    dag.build_dag(futures)

    lines: list[str] = ["from parsl import python_app", "", ""]

    seen_funcs: set[object] = set()
    for fut in dag.tasks.values():
        if fut.func in seen_funcs:
            continue
        seen_funcs.add(fut.func)
        src = dedent(inspect.getsource(fut.func))
        func_lines = [ln for ln in src.splitlines() if not ln.strip().startswith("@")]
        lines.append("@python_app")
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


def python_app(_func=None, **kwargs):
    """Parsl ``python_app`` decorator mapped to :func:`parslet_task`."""

    def wrapper(func):
        return parslet_task(func, **kwargs)

    if _func is None:
        return wrapper
    return wrapper(_func)


def bash_app(_func=None, **kwargs):
    """Parsl ``bash_app`` decorator executed via :mod:`subprocess`.

    The decorated function must return a string representing the shell
    command to execute. When the decorated function is called, the command is
    run immediately using :func:`subprocess.run` with ``shell=True`` and both
    stdout and stderr captured. The resulting stdout is stored in a
    :class:`ParsletFuture`. If the command exits with a non-zero return code,
    a :class:`subprocess.CalledProcessError` is recorded as the future's
    exception. This mirrors Parsl's ``bash_app`` which returns a future whose
    ``result()`` yields the command's output.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kw):
            cmd = func(*args, **kw)
            task_id = uuid.uuid4().hex
            future = ParsletFuture(task_id, wrapped, args, kw)
            try:
                completed = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True
                )
                if completed.returncode != 0:
                    raise subprocess.CalledProcessError(
                        completed.returncode,
                        cmd,
                        completed.stdout,
                        completed.stderr,
                    )
                future.set_result(completed.stdout)
            except Exception as exc:  # pragma: no cover - exception path
                future.set_exception(exc)
            return future

        return wrapped

    if _func is None:
        return decorator
    return decorator(_func)


class DataFlowKernel:  # pragma: no cover - simple shim
    """Minimal stub of Parsl's ``DataFlowKernel``.

    Instantiating this class issues a warning since Parslet manages task
    scheduling internally.
    """

    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "Parsl DataFlowKernel is not supported; Parslet manages "
            "scheduling internally.",
            stacklevel=2,
        )

    def __getattr__(self, attr):
        raise AttributeError("DataFlowKernel is only a compatibility stub in Parslet")


__all__ = [
    "ParslToParsletTranslator",
    "convert_parsl_to_parslet",
    "ParsletToParslTranslator",
    "convert_parslet_to_parsl",
    "import_parsl_script",
    "export_parsl_dag",
    "python_app",
    "bash_app",
    "DataFlowKernel",
    "ParsletFuture",
]
