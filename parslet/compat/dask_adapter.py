"""Dask compatibility helpers and AST translators for Parslet.

This module provides lightweight substitutes for common ``dask`` entry points
so that code using ``dask.delayed`` can be executed by Parslet.  It also
contains AST transformers for programmatic translation of source code from Dask
syntax to Parslet syntax.
"""

from __future__ import annotations

import ast

from ..core.task import parslet_task, ParsletFuture


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
                node.decorator_list[idx] = ast.Name(
                    id="parslet_task", ctx=ast.Load()
                )
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Strip ``.compute()`` calls so Parslet's runner manages execution."""
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "compute"
        ):
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


# ---------------------------------------------------------------------------
# Runtime compatibility shims
# ---------------------------------------------------------------------------


def delayed(_func=None, **kwargs):
    """Dask ``delayed`` decorator mapped to :func:`parslet_task`."""

    def wrapper(func):
        return parslet_task(func, **kwargs)

    if _func is None:
        return wrapper
    return wrapper(_func)


def compute(*futures: ParsletFuture):
    """Evaluate one or more ``ParsletFuture`` objects like ``dask.compute``."""

    results = [f.result() for f in futures]
    if len(results) == 1:
        return results[0]
    return tuple(results)


__all__ = [
    "DaskToParsletTranslator",
    "convert_dask_to_parslet",
    "delayed",
    "compute",
    "ParsletFuture",
]
