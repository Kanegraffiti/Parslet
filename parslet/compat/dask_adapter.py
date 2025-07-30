"""Dask compatibility helpers and AST translators for Parslet.

This module provides lightweight substitutes for common ``dask`` entry points
so that code using ``dask.delayed`` can be executed by Parslet.  It also
contains AST transformers for programmatic translation of source code from Dask
syntax to Parslet syntax.
"""

from __future__ import annotations

import ast

from ..core import parslet_task, ParsletFuture


class DaskToParsletTranslator(ast.NodeTransformer):
    """Replace Dask delayed constructs with Parslet equivalents."""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Convert ``@delayed`` decorators to ``@parslet_task``."""
        for idx, decorator in enumerate(node.decorator_list):
            # ``@delayed`` imported directly
            if isinstance(decorator, ast.Name) and decorator.id == "delayed":
                node.decorator_list[idx] = ast.Name(
                    id="parslet_task", ctx=ast.Load()
                )
            # ``@dask.delayed`` style
            elif (
                isinstance(decorator, ast.Attribute)
                and decorator.attr == "delayed"
            ):
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
        if isinstance(node.func, ast.Name) and node.func.id == "delayed":
            node.func.id = "parslet_task"
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "delayed"
        ):
            node.func.attr = "parslet_task"
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
