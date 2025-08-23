Running on Fumes? Use Battery-Saver Mode!
==========================================

We've all been there. You're in the middle of something important, and you see that dreaded "Low Battery" warning. Parslet is designed for the real world, so it has a special **battery-saver mode** built right in, perfect for when you're working on a laptop, tablet, or phone.

How Does It Work?
-----------------

When you tell Parslet to run in battery-saver mode, an :class:`AdaptivePolicy` kicks in. It looks at your device's CPU, available memory, and most importantly, your current battery percentage.

Based on what it sees, the policy decides how many worker threads to keep alive. If the battery drops below about 40%, the pool is automatically cut in half; when the battery recovers, it can grow again up to its cap. Often, it will slow down to running just one task at a time. This is like putting your phone into "Low Power Mode"—it helps your battery last as long as possible so you can finish your work.

How Do I Turn It On?
--------------------

It's super easy! Just add the ``--battery-mode`` flag when you run your recipe from the command line:

.. code-block:: bash

   parslet run my_recipe.py --battery-mode

What if I Still Need to Go a Little Faster?
-------------------------------------------

You're still in control! If you want to use battery-saver mode but still want to run, say, two tasks at a time, you can. Just tell Parslet how many "workers" (assistant chefs) you want it to use.

.. code-block:: bash

   parslet run my_recipe.py --battery-mode --max-workers 2

Battery mode doesn't turn off any of Parslet's other cool features. You can still save your progress with checkpointing, get pictures of your workflow, and see all the logs. It just tells Parslet to be a little more gentle on your device.

To see all the other commands you can use, check out our guide to the :doc:`cli` (the "remote control").