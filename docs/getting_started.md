# Getting Started: Your First Parslet Recipe

> **Are you brand new to Parslet?** We recommend reading our friendly [Introduction to Parslet](./introduction.md) first to get the big picture!

This guide will walk you through creating your very first automated recipe (we call it a "workflow").

### Step 1: Installing Parslet

Before you can write a recipe, you need to install Parslet. The recommended way is using `pip`. For detailed, platform-specific instructions, please see our complete [Installation Guide](./install.html).

### Step 2: Writing Your First Recipe

A Parslet recipe is just a plain Python file. The magic happens with a special note called a decorator (`@parslet_task`) that you add to your functions.

Every recipe also needs a `main()` function. This is the starting point that tells Parslet how all your steps connect.

Let's create a file called `my_recipe.py` and add the following:

```python
from parslet import parslet_task, ParsletFuture
from typing import List

# This is our first task. It's just a Python function
# with a @parslet_task note on top.
@parslet_task
def add_one(number: int) -> int:
    print(f"Running task: add_one({number})")
    return number + 1

# Here's a second task.
@parslet_task
def multiply_by_five(number: int) -> int:
    print(f"Running task: multiply_by_five({number})")
    return number * 5

# This is our main recipe function. Parslet looks for this!
def main() -> List[ParsletFuture]:
    # We call our first task. It doesn't run yet!
    # It just gives us an "IOU" for the result.
    iou_from_add = add_one(1) # This will eventually be 2

    # Now, we give the IOU from the first task to the second task.
    # This tells Parslet: "Wait for add_one to finish before you start."
    iou_from_multiply = multiply_by_five(iou_from_add) # This will eventually be 10

    # We return the very last IOU. This tells Parslet the recipe is done
    # when this final step is complete.
    return [iou_from_multiply]
```

When you run this with `parslet run my_recipe.py`, Parslet will read the file, see the connections, and run the tasks in the right order.

### Step 3: Playing Well with the Big Kids (Parsl & Dask)

One of Parslet's superpowers is that it helps you "graduate" to bigger tools when you need more power. Parslet ships with a compatibility layer and a source-code converter so that your work can move in either direction.

-   **Using Parsl:** When a workflow outgrows your laptop, translate it to a Parsl script and run it on a cluster.

    ```bash
    # Convert a Parslet recipe to Parsl
    parslet convert --from-parslet my_recipe.py --to-parsl my_recipe_parsl.py
    python my_recipe_parsl.py  # executed with a Parsl executor
    ```

-   **Converting from Parsl or Dask:** If you are handed a Parsl or Dask workflow, Parslet can import it so you can run it offline.

    ```bash
    # Parsl -> Parslet
    parslet convert --from-parsl their_cool_script.py --to-parslet local_script.py

    # Dask -> Parslet
    parslet convert --from-dask another_cool_script.py --to-parslet local_script.py

    # You can also export back to Dask if needed
    parslet convert --from-parslet my_recipe.py --to-dask my_recipe_dask.py
    ```

    Each command performs an AST rewrite and produces a new file with a `_parslet.py`, `_parsl.py`, or `_dask.py` suffix. The converter currently supports pure Python `@python_app` tasks and `dask.delayed` graphs and is intended for local execution—complex data staging or provider settings are out of scope.

### Never Lose Your Work! (Resuming Recipes)

Imagine you're running a recipe that takes a long time, and your battery dies halfway through. So frustrating!

Parslet has a "checkpoint" feature to save you. Just add `--checkpoint-file` when you run your recipe:

```bash
parslet run my_long_recipe.py --checkpoint-file my_progress.json
```

Parslet will now keep a record of every step it finishes. If it gets interrupted, just run the exact same command again. Parslet will read your progress file and cleverly skip all the steps that are already done, picking up right where it left off. It's a real lifesaver!