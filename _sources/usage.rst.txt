Usage: Your First Parslet Workflow
===================================

This guide will walk you through writing and running your first Parslet workflow. For a hands-on example, you can also check out the ``examples/hello.py`` file in this project.

If you want the bigger picture of how all the pieces fit together, see our :doc:`architecture` guide.

Defining Your Tasks
-------------------

Think of tasks as the individual steps in a recipe. In Parslet, a task is just a normal Python function with a special ``@parslet_task`` decorator on top.

When you call a decorated function, it doesn't run right away. Instead, it gives you back a ``ParsletFuture`` object—think of it as an IOU or a ticket for a result that will be ready later. You then create your workflow by passing these IOUs from one task to another.

Every workflow script needs a ``main()`` function that tells Parslet where the workflow ends. It should return a list of the final IOUs you care about.

Here’s what a super simple workflow looks like:

.. code-block:: python

   from typing import List
   from parslet import parslet_task, ParsletFuture

   # Here's our first task. It just adds two numbers.
   @parslet_task
   def add(a: int, b: int) -> int:
       return a + b

   # This is the main entry point for Parslet.
   def main() -> List[ParsletFuture]:
       # We call our task, and it returns an IOU for the result.
       future = add(1, 2)
       # We return a list containing our final IOU.
       return [future]

Running Your Workflow
---------------------

To bring your workflow to life, you use the ``parslet run`` command from your terminal:

.. code-block:: bash

   parslet run path/to/your/workflow.py

When you run this, Parslet:
1.  Reads your Python file.
2.  Calls your ``main()`` function to understand the workflow.
3.  Figures out the right order to run the tasks.
4.  Runs the tasks and prints the final result for you.

**Did your workflow get interrupted?** No worries. If you run it with the ``--checkpoint-file`` option, Parslet remembers which tasks finished, so you can resume right where you left off.

Being Smart with Resources
--------------------------

Parslet is designed for devices that might not be very powerful.

By default, it looks at your device's CPU cores and available memory to pick a sensible number of tasks to run at once.

If you're on a laptop or phone and want to save battery, just add the ``--battery-mode`` flag. This tells Parslet to take it easy and run fewer tasks at the same time. You can always override this with ``--max-workers`` if you know best.

Want to see what's happening in real-time? Use the ``--monitor`` flag:

.. code-block:: bash

   parslet run my_flow.py --monitor

To analyze performance, export execution stats and plot an ASCII heatmap:

.. code-block:: bash

   parslet run my_flow.py --export-stats stats.json
   python examples/tools/plot_stats.py stats.json

For more command-line options, like exporting a picture of your workflow, check out the :doc:`cli` guide. To learn more about how battery mode works, see :doc:`battery_mode`.
