CLI
===

The ``parslet`` command line interface is the main entry point for running
workflows.  It loads your workflow module, builds the DAG and executes the
tasks.  Most options mirror functionality described in :doc:`usage` and can be
combined freely.

Use ``parslet run <workflow.py>`` to start a run. You can also execute a DAG
saved to a ``.dag`` or ``.json`` file with ``parslet run --dag path`` and
create such a file using ``parslet export --dag path <workflow.py>``.

Common options
--------------

``--max-workers <N>``
    Override the number of worker threads.  If omitted, Parslet chooses a value
    based on CPU cores and available RAM.

``--battery-mode``
    Reduce concurrency to conserve power.  When used without
    ``--max-workers`` this often results in a single worker thread.  See
    :doc:`battery_mode` for more about how the scheduler reacts to low battery.

``--monitor``
    Start a lightweight web dashboard on the given port to monitor progress.

``--failsafe-mode``
    If tasks hit resource limits they are retried serially in a fallback executor.

``--checkpoint-file <FILE>``
    Save completed tasks so interrupted runs can continue.

``--simulate``
    Build the DAG and display an ASCII representation together with
    current RAM and battery levels. No tasks are executed.

``--export-dot`` / ``--export-png``
    Export the DAG for visualization.  See :doc:`exporting` for details.

``--log-level`` and ``--verbose``
    Control console logging verbosity. If the `Rich` library is installed the
    CLI displays colourful tables of task benchmarks.

Example
-------

Run the image filter example and export a PNG of the DAG:

.. code-block:: bash

   parslet run examples/image_filter.py --export-png dag.png

For a full list of options run ``parslet run --help``.  You can also consult
:doc:`tasks` for how to define functions the CLI can execute. The ``export``
subcommand has its own help text available via ``parslet export --help``.
