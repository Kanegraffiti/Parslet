Battery Mode
============

Parslet supports a battery‑saver mode designed for laptops and mobile devices.
When the CLI flag ``--battery-mode`` is provided the ``AdaptiveScheduler``
reduces the default number of worker threads.  The scheduler looks at available
CPU cores, free RAM and current battery percentage (via ``psutil`` if
installed) to choose a conservative level of parallelism.

If you do not specify ``--max-workers`` the runner often defaults to a single
worker in battery mode.  This helps prolong battery life when running workflows
on devices such as phones using Termux or lightweight laptops.

You can still override the worker count explicitly:

.. code-block:: bash

   parslet run my_workflow.py --battery-mode --max-workers 2

Battery mode does not remove any features; it simply limits concurrency while
retaining DAG export, checkpointing and logging.  See :doc:`cli` for all
available command line flags.
