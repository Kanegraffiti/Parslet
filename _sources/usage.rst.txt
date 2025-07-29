Usage
=====

This section gives a quick overview of how to write and run a Parslet
workflow.  For a hands on example consult ``examples/hello.py`` in the
repository.  The bigger picture of how the pieces fit together is covered in
:doc:`architecture`.

Defining tasks
--------------

Tasks are ordinary Python functions decorated with ``@parslet_task``.  Calling
a decorated function does not immediately execute it.  Instead it returns a
``ParsletFuture`` that represents the eventual result and is used to create the
Directed Acyclic Graph (DAG).

Every workflow script must expose a ``main()`` function which returns the list
of terminal ``ParsletFuture`` objects.  A minimal workflow looks like the
following:

.. code-block:: python

   from typing import List
   from parslet import parslet_task, ParsletFuture

   @parslet_task
   def add(a: int, b: int) -> int:
       return a + b

   def main() -> List[ParsletFuture]:
       future = add(1, 2)
       return [future]

Running a workflow
------------------

Use the ``parslet run`` command to execute a workflow script:

.. code-block:: bash

   parslet run path/to/workflow.py

Parslet loads the module, builds the DAG from ``main()``, chooses a sensible
number of worker threads based on CPU count and available RAM, and then runs the
tasks.  The results of the entry futures are printed when execution finishes.

You can resume interrupted runs by specifying ``--checkpoint-file`` which stores
completed tasks in a JSON file.

Resource awareness
------------------

By default the runner selects a worker count that balances CPU cores and
available memory.  If ``--battery-mode`` is used, concurrency is reduced (often
to a single worker) unless ``--max-workers`` overrides the value.  This is
useful on laptops or mobile devices where conserving power is important.

The ``--monitor`` option starts a small web server to view task status while the
workflow runs. Use ``--failsafe-mode`` if tasks may exceed memory limits; it
will retry them one by one instead of failing the entire run.

For additional options such as exporting the DAG or adjusting logging see
:doc:`cli`.  Details on how ``--battery-mode`` influences scheduling are in
:doc:`battery_mode`.
