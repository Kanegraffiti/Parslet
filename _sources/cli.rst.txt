Your Remote Control: The Parslet CLI
=====================================

The ``parslet`` command is your remote control for running your recipes. It's how you tell Parslet what to do. You use it right from your terminal.

The main command is simple:

.. code-block:: bash

   parslet run <your_recipe.py>

This tells Parslet to find your recipe, build the flowchart, and run all the steps. But the remote control has a bunch of other cool buttons (we call them options or flags) that you can use!

The Buttons on Your Remote Control
----------------------------------

Here are some of the most common buttons you can press:

``--max-workers <Number>``
    Lets you tell Parslet exactly how many "assistant chefs" to use. If you don't use this, Parslet will decide for you based on your device's power.

``--battery-mode``
    This is the **power-saver button**. It tells Parslet to be gentle on your battery. See :doc:`battery_mode` to learn more.

``--monitor``
    Want to watch your recipe as it runs? This button starts up a little dashboard so you can see your tasks' progress in real-time.

``--failsafe-mode``
    If a task fails because your device runs out of resources, this button tells Parslet to try again in a slower, safer way.

``--checkpoint-file <your_file.json>``
    This is the **"save my progress" button**. It's a lifesaver for long recipes.

``--simulate``
    This is the "preview" button. It will show you the flowchart for your recipe and check your device's RAM and battery, but it won't actually run any of the tasks. It's great for double-checking your work.

``--export-dot`` / ``--export-png``
    These buttons tell Parslet to take a picture of your recipe's flowchart for you. See :doc:`exporting` for more details.

``--log-level`` and ``--verbose``
    These control how much information Parslet prints to the screen while it's working. If you have the `Rich` library installed, it will even show you a beautiful, colorful report card for your tasks.

An Example
----------

Let's run our photo filter recipe and also ask for a picture of the flowchart.

.. code-block:: bash

   parslet run examples/image_filter.py --export-png dag.png

Want to see all the buttons? Just type ``parslet run --help`` into your terminal.