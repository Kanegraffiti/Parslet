Exporting
=========

Parslet can export your workflow's DAG for inspection or documentation.

``--export-dot <file>``
    Write the DAG to a Graphviz DOT file.  Use ``-`` as the file name to print
    the DOT text to ``stdout``.

``--export-png <file>``
    Render the DAG as a PNG image.  Requires ``pydot`` and Graphviz to be
    installed.

``parslet export --dag <file> <workflow.py>``
    Save the DAG structure to a JSON ``.dag`` file without executing the
    workflow. The resulting file can be run later with ``parslet run --dag``.

Example
-------

.. code-block:: bash

   parslet run examples/hello.py --export-png hello_dag.png

Both options may be used together.  Exporting does not affect the execution of
the workflow, so it can be enabled even on resource‑constrained machines.
The underlying conversion is handled by functions in ``parslet.core.exporter``
which build a ``pydot`` representation from the internal ``networkx`` graph.
See :doc:`cli` for all available flags.
