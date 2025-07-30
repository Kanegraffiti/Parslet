Tasks
=====

Tasks are the fundamental units of work in Parslet.  A task is simply a Python
function decorated with ``@parslet_task``.  Calling the function does not run it
immediately; instead it returns a ``ParsletFuture`` object.  Passing those
futures into other tasks defines the edges of the DAG.

Basic usage
-----------

.. code-block:: python

   from parslet import parslet_task, ParsletFuture

   @parslet_task
   def square(x: int) -> int:
       return x * x

   @parslet_task
   def add(a: int, b: int) -> int:
       return a + b

   def main() -> list[ParsletFuture]:
       first = square(4)
       second = square(2)
       return [add(first, second)]

The returned ``ParsletFuture`` objects can be inspected for their ``task_id``
and passed around like lightweight promises.  The ``DAGRunner`` resolves them in
topological order and schedules ready tasks on a thread pool.  Concurrency is
decided by the ``AdaptiveScheduler`` which looks at available CPU cores, memory
and battery level.  See :doc:`battery_mode` for details on how this influences
execution when power is limited.

Error handling
--------------

If a task raises an exception all downstream tasks are skipped.  Attempting to
retrieve the result of a skipped task raises ``UpstreamTaskFailedError``.
Running the workflow with ``--checkpoint-file`` records completed tasks so the
run can resume after the issue is fixed.

See ``examples/hello.py`` for an annotated introduction and
``examples/text_cleaner.py`` for a more realistic pipeline.
