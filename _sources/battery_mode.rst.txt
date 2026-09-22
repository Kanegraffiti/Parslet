Running on Fumes? Use Battery-Saver Mode!
==========================================

We've all been there. You're in the middle of something important, and you see that dreaded "Low Battery" warning. Parslet is designed for the real world, so it has a special **battery-saver mode** built right in, perfect for when you're working on a laptop, tablet, or phone.

How Does It Work?
-----------------

Battery mode samples the device throughout a run rather than making a single
decision at startup. Its default power bands are:

.. list-table::
   :header-rows: 1

   * - Power state
     - Worker ceiling
     - Task behaviour
   * - Charging or AC power
     - Normal
     - Run normally
   * - Above 40%
     - Normal
     - Run normally
   * - 16% to 40%
     - Half
     - Defer high-energy, best-effort tasks
   * - 15% or below
     - One
     - Run light, urgent, or non-degradable work; defer optional expensive work
   * - Battery unavailable
     - Normal
     - Run normally

The last rule is important on desktops, servers, and devices that do not
provide battery telemetry: missing information never causes Parslet to slow
down unexpectedly. If the device is connected to power, even a very low
battery percentage is treated as charging and the normal worker limit is
restored.

How Do I Turn It On?
--------------------

It's super easy! Just add the ``--battery-mode`` flag when you run your recipe from the command line:

.. code-block:: bash

   parslet run my_recipe.py --battery-mode

You can customize the thresholds:

.. code-block:: bash

   parslet run my_recipe.py --battery-mode --battery-low 35 --battery-critical 10

Describe task importance with the existing energy and quality-of-service
metadata:

.. code-block:: python

   from parslet import parslet_task

   @parslet_task(energy_cost="high", qos="best_effort")
   def generate_previews():
       ...

   @parslet_task(energy_cost="high", qos="high")
   def upload_emergency_record():
       ...

The preview task may be deferred as the battery falls. The high-priority
upload remains eligible to run. Set ``degradable=False`` for work that must
not be deferred automatically.

What if I Still Need to Go a Little Faster?
-------------------------------------------

You're still in control! If you want to use battery-saver mode but still want to run, say, two tasks at a time, you can. Just tell Parslet how many "workers" (assistant chefs) you want it to use.

.. code-block:: bash

   parslet run my_recipe.py --battery-mode --max-workers 2

``--force-battery`` bypasses both battery-sensitive task checks and battery
mode rationing. Battery mode does not pause arbitrary work that is already
running; it controls worker concurrency and whether new tasks may start.

Battery mode doesn't turn off any of Parslet's other features. You can still
save progress with checkpointing, visualize the workflow, and inspect logs.

To see all the other commands you can use, check out our guide to the :doc:`cli` (the "remote control").
