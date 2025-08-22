"""Visualization and export utilities for Parslet DAGs.

Public API: :func:`dag_to_pydot`, :func:`dag_to_dot_string`,
``save_dag_to_png`` and related exceptions.
"""

import logging
import networkx as nx
from typing import TYPE_CHECKING, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "dag_to_pydot",
    "dag_to_dot_string",
    "save_dag_to_png",
    "PydotImportError",
    "GraphvizExecutableNotFoundError",
]

if TYPE_CHECKING:
    from .dag import (
        DAG,
    )  # To avoid circular import at runtime if DAG imports exporter

# Attempt to import pydot. This is a soft dependency.
# If pydot is not available, export functions will raise PydotImportError.
try:
    import pydot

    PYDOT_AVAILABLE = True
except ImportError:
    PYDOT_AVAILABLE = False
    pydot = None  # Assign to None to satisfy linters


class PydotImportError(ImportError):
    """
    Custom exception raised when `pydot` library is required but not found.

    This typically occurs when trying to use DOT or PNG export functionalities
    without having `pydot` installed.
    """

    def __init__(
        self,
        message: str = (
            "pydot library is not installed. Please install it to use "
            "DOT/PNG export features (e.g., 'pip install pydot')."
        ),
    ):
        super().__init__(message)


class GraphvizExecutableNotFoundError(RuntimeError):
    """
    Custom exception raised when Graphviz executable (e.g., 'dot') is not
    found by `pydot`.

    This error indicates that while `pydot` might be installed, the underlying
    Graphviz tools (which `pydot` calls to render images) are not in the
    system's PATH or are not installed.
    """

    def __init__(
        self,
        message: str = (
            "Graphviz executables (like 'dot') not found in system PATH. "
            "Graphviz is required for PNG export. Please install Graphviz "
            "and ensure it's in your PATH."
        ),
    ):
        super().__init__(message)


def dag_to_pydot(dag: "DAG") -> "Optional[pydot.Dot]":
    """
    Converts a Parslet DAG to a `pydot.Dot` object using NetworkX.

    This function serves as the core conversion utility for generating
    visual representations of the DAG.

    Args:
        dag (DAG): The Parslet DAG object to convert.

    Returns:
        Optional[pydot.Dot]: A `pydot.Dot` object representing the graph if
                             `pydot` is available. Returns `None` if `pydot`
                             is not installed (though it typically raises
                             PydotImportError first). The type hint reflects
                             that `pydot` itself might be `None` if not
                             imported.

    Raises:
        PydotImportError: If the `pydot` library is not installed.
        TypeError: If the graph object within the DAG is not a NetworkX
                   DiGraph.
        RuntimeError: If `nx.drawing.nx_pydot.to_pydot` fails for other
                      reasons.
    """
    if not PYDOT_AVAILABLE or pydot is None:
        # This check ensures pydot was imported successfully at the module
        # level.
        raise PydotImportError()

    if not isinstance(dag.graph, nx.DiGraph):
        raise TypeError(
            "DAG's internal graph must be a NetworkX DiGraph. "
            f"Got: {type(dag.graph)}"
        )

    # Convert the NetworkX graph (dag.graph) to a pydot graph.
    # Custom node attributes (shape, color, etc.) or edge attributes can be
    # defined in the NetworkX graph nodes/edges and would be translated by
    # to_pydot. For Parslet, node labels are typically their task IDs.
    try:
        # nx.drawing.nx_pydot.to_pydot handles the conversion.
        pydot_graph: pydot.Dot = nx.drawing.nx_pydot.to_pydot(dag.graph)
    except Exception as e:
        # Catch potential errors during the conversion process itself.
        raise RuntimeError(f"Failed to convert DAG to pydot graph: {e}") from e

    return pydot_graph


def dag_to_dot_string(dag: "DAG") -> str:
    """
    Generates a DOT language string representation of the Parslet DAG.

    The DOT language is a plain text graph description language. This string
    can be used with Graphviz tools or other compatible software.

    Args:
        dag (DAG): The Parslet DAG object.

    Returns:
        str: A string in DOT language format representing the DAG.

    Raises:
        PydotImportError: If the `pydot` library is not installed (propagated
                          from `dag_to_pydot`).
        RuntimeError: If conversion to the `pydot.Dot` object fails
                      (propagated).
    """
    pydot_graph = dag_to_pydot(dag)  # This will raise if pydot is not available.
    if pydot_graph is None:  # Should not happen if PydotImportError is raised correctly
        raise RuntimeError(
            "pydot graph generation failed unexpectedly, returning None."
        )
    return pydot_graph.to_string()


def save_dag_to_png(dag: "DAG", output_path: str) -> None:
    """
    Saves the Parslet DAG as a PNG image file.

    This function requires both the `pydot` library and a functional Graphviz
    installation (specifically, the 'dot' executable must be in the system
    PATH).

    Args:
        dag (DAG): The Parslet DAG object.
        output_path (str): The file path where the PNG image will be saved.
                           The path should include the '.png' extension.

    Raises:
        PydotImportError: If `pydot` is not installed (propagated from
                          `dag_to_pydot`).
        GraphvizExecutableNotFoundError: If Graphviz 'dot' executable is not
                                         found by `pydot`.
        RuntimeError: If any other error occurs during PNG creation or writing,
                      such as file permission issues or unexpected `pydot`
                      errors.
    """
    pydot_graph = dag_to_pydot(dag)  # Handles pydot import and initial conversion.
    if pydot_graph is None:  # Defensive check
        raise RuntimeError(
            "pydot graph generation failed unexpectedly, returning None, "
            "cannot save to PNG."
        )

    try:
        # The write_png method of pydot.Dot calls the Graphviz 'dot'
        # executable to render the graph and save it as a PNG.
        logger.info("Attempting to write PNG to: %s", output_path)
        pydot_graph.write_png(output_path)
        logger.info("DAG visualization successfully saved to %s", output_path)
    except FileNotFoundError as e:
        # This can occur if 'dot' executable is not found or if the
        # output_path is invalid. We try to distinguish based on the error
        # message.
        if "dot" in str(e).lower() or "No such file or directory" in str(
            e
        ):  # Heuristic
            raise GraphvizExecutableNotFoundError() from e
        # Otherwise, assume it's a path/permission issue for the output file.
        raise RuntimeError(
            f"Failed to write PNG file at '{output_path}': {e}. "
            "Check path and permissions."
        ) from e
    except (pydot.InvocationException, Exception) as e:
        # pydot.InvocationException is common if 'dot' fails or is not found.
        # Check common error messages indicating 'dot' executable issues.
        error_message = str(e).lower()
        if (
            "failed to execute" in error_message
            or "program dot not found" in error_message
            or '"dot" not found' in error_message
            or "could not execute" in error_message
        ):
            raise GraphvizExecutableNotFoundError() from e
        # For other errors, raise a generic RuntimeError.
        raise RuntimeError(
            f"Failed to create or write PNG file at '{output_path}': "
            f"{type(e).__name__} - {e}"
        ) from e


# Example usage block for direct testing (mainly for development).
if __name__ == "__main__":
    # This block is for basic testing if the module is run directly.
    # It requires creating a dummy DAG and tasks, which means Parslet's core
    # components (DAG, ParsletFuture, @parslet_task) must be importable.

    # Setup a basic logger for testing this module directly
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Attach logger to this module for save_dag_to_png to use if needed
    # (by making it part of a class or passing)
    # For this standalone script test, we'd ideally pass a logger to
    # save_dag_to_png or handle logging internally.
    # Let's simulate by setting a module-level logger for the test.
    # Note: The `save_dag_to_png` function would need modification to use
    # `logger` directly without `self`.
    # For simplicity, the logger lines in `save_dag_to_png` are illustrative.

    logger.info("Parslet Exporter Module - Direct Run Test")
    logger.info("-----------------------------------------")
    if not PYDOT_AVAILABLE:
        logger.warning(
            "pydot library not found. Export functions will raise " "PydotImportError."
        )
        logger.warning("Please install it: pip install pydot")
    else:
        logger.info("pydot library found.")

    # --- Dummy DAG construction for testing ---
    # This requires Parslet's task and DAG mechanisms.
    try:
        from parslet.core.task import (
            parslet_task,
        )  # Assuming relative import works from here

        # Define some dummy tasks
        @parslet_task
        def ex_task_a():
            return "A"

        @parslet_task
        def ex_task_b(dep_a):
            return f"B after {dep_a}"

        @parslet_task
        def ex_task_c(dep_b):
            return f"C after {dep_b}"

        if PYDOT_AVAILABLE:
            logger.info("\nSimulating DAG for export tests...")
            try:
                # Create futures
                future_a = ex_task_a()
                future_b = ex_task_b(future_a)
                future_c = ex_task_c(future_b)

                # Build DAG
                test_dag = DAG()
                test_dag.build_dag([future_c])  # Build with the terminal future
                test_dag.validate_dag()  # Ensure it's valid
                logger.info("Dummy DAG created successfully for testing.")

                # Test dag_to_dot_string
                logger.info("\nTesting dag_to_dot_string():")
                try:
                    dot_str = dag_to_dot_string(test_dag)
                    logger.info(
                        "DOT String generated (first 100 chars): " f"{dot_str[:100]}..."
                    )
                    # Example: save to a file
                    with open("test_dag_output.dot", "w", encoding="utf-8") as f:
                        f.write(dot_str)
                    logger.info("Full DOT string saved to test_dag_output.dot")
                except Exception as e_dot:
                    logger.error(
                        "Error in dag_to_dot_string test: %s",
                        e_dot,
                        exc_info=True,
                    )

                # Test save_dag_to_png
                logger.info("\nTesting save_dag_to_png():")
                png_output_path = "test_dag_output.png"
                try:
                    # Modify save_dag_to_png to accept a logger for this
                    # test, or use a global one.
                    # For this test, we'll rely on its internal error raising.
                    save_dag_to_png(test_dag, png_output_path)
                    # save_dag_to_png now uses the module logger, so it works
                    # correctly when called outside of a class.
                    logger.info(
                        "DAG visualization attempt to save to " f"{png_output_path}."
                    )
                    logger.info(
                        "If Graphviz 'dot' is installed and in PATH, "
                        "%s should be created.",
                        png_output_path,
                    )
                except GraphvizExecutableNotFoundError as gne:
                    logger.error(
                        "PNG EXPORT FAILED: Graphviz 'dot' executable not "
                        "found. PNG not created."
                    )
                    logger.error("Details: %s", gne)
                    logger.error(
                        "Please install Graphviz "
                        "(from https://graphviz.org/download/) "
                        "and ensure 'dot' is in your system PATH."
                    )
                except (
                    PydotImportError
                ) as pie:  # Should be caught earlier by PYDOT_AVAILABLE
                    logger.error(f"PNG EXPORT FAILED: Pydot library not found. {pie}")
                except Exception as e_viz:
                    logger.error(
                        "Error in save_dag_to_png test: "
                        f"{type(e_viz).__name__} - {e_viz}",
                        exc_info=True,
                    )

            except Exception:
                logger.error(
                    "Error during dummy DAG creation or export tests: {e}",
                    exc_info=True,
                )
        else:
            logger.warning("\nSkipping DAG export tests as pydot is not available.")

    except ImportError:
        logger.error(
            "Failed to import Parslet core components for testing exporter. "
            "Ensure PYTHONPATH is set correctly if running directly."
        )

    logger.info("\nExporter module direct run test finished.")
