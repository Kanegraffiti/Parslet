Architecture
============

The core of Parslet is designed to be compact and easy to understand.  Workflows
are defined as a graph of tasks and executed locally by a lightweight runner.
Each element is loosely coupled so you can run small examples on laptops or
mobile devices while still scaling up on desktops.

.. image:: ../visuals/architecture.png
   :alt: Architecture diagram

* **Tasks** – functions decorated with ``@parslet_task`` which return
  ``ParsletFuture`` objects.  Dependencies are created by passing futures to
  other tasks.
* **DAG** – constructed from the futures returned by ``main()`` and backed by
  ``networkx`` for cycle detection and topological sorting.
* **DAGRunner** – runs tasks using a ``ThreadPoolExecutor``.  It relies on the
  ``AdaptiveScheduler`` which inspects CPU count, available RAM and battery
  level to decide on a worker count.
* **Exporter** – optional helpers for writing the DAG to DOT or PNG files.
* **Parsl bridge** – utilities that allow the same tasks to be executed with the
  Parsl runtime when needed.

The example workflows under ``examples/`` show how these pieces fit together in
practice. ``hello.py`` demonstrates the basics while ``image_filter.py`` builds
a small image processing pipeline. ``rad_pipeline.py`` showcases the **RAD by
Parslet** workflow used on resource-constrained devices. You can export any DAG
using :doc:`exporting`.
For a step-by-step guide on writing your own workflow see :doc:`usage`.

