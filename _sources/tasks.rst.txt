What Are Parslet Tasks?
=======================

Tasks are the heart of Parslet. They are the individual steps or "building blocks" of your automated workflow.

A task is just a regular Python function that you give a special ``@parslet_task`` decorator.

When you call a task function, it doesn't run right away. Instead, it returns a ``ParsletFuture`` object (think of it as an IOU for the result). You create your workflow by passing these IOUs into other tasks, which tells Parslet the order of operations.

A Simple Example
----------------

Let's build a simple workflow with a few tasks.

.. code-block:: python

   from parslet import parslet_task, ParsletFuture

   # This task squares a number.
   @parslet_task
   def square(x: int) -> int:
       return x * x

   # This task adds two numbers.
   @parslet_task
   def add(a: int, b: int) -> int:
       return a + b

   # Our main function defines the workflow.
   def main() -> list[ParsletFuture]:
       # Create two IOUs by calling the square task.
       # Parslet can run these at the same time!
       first = square(4)
       second = square(2)

       # Create a final IOU that depends on the first two.
       # Parslet will wait for them to finish before running this.
       return [add(first, second)]

The ``ParsletFuture`` objects are like little promises. The ``DAGRunner`` (Parslet's engine) figures out the right order to resolve these promises and runs the tasks on a thread pool.

It's also smart about your device's resources. It looks at your CPU, memory, and even your battery level to decide how many tasks to run at once. To learn more, see :doc:`battery_mode`.

What Happens When Things Go Wrong? (Error Handling)
---------------------------------------------------

If a task runs into an error and crashes, Parslet is designed to handle it gracefully.

Any tasks that were waiting for the failed task's result will be automatically skipped. You won't get a messy crash for the whole workflow.

If you try to get the result of a skipped task, Parslet will raise a friendly ``UpstreamTaskFailedError`` to let you know what happened.

**Pro-Tip:** If you're running a long workflow, use the ``--checkpoint-file`` option. This tells Parslet to save a record of every task that finishes successfully. If the workflow gets interrupted, you can just run it again, and it will pick up right where it left off.

For a friendly, step-by-step example, check out ``examples/hello.py``. For a more real-world pipeline, see ``examples/text_cleaner.py``.