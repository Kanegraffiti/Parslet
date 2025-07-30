# Getting the Best of Both Worlds (Hybrid Recipes)

Imagine you're cooking a big meal. You can chop the vegetables on your own kitchen counter (your phone or laptop), but you have access to a giant, super-fast pizza oven at your friend's house for the main course.

Wouldn't it be great if you could write one recipe that says, "Chop these veggies here, but send the pizza over to the fast oven"?

That's exactly what **Hybrid Orchestration** is!

Parslet lets you create a single recipe where some tasks run locally on your device, while others are sent off to be run by its "big brother," Parsl, on a more powerful computer.

### How Does It Work?

We have a special helper tool called `execute_hybrid`. You just give it your list of tasks and tell it the names of the ones you want to send to the "fast oven" (Parsl).

Here’s what that looks like:

```python
from parslet import parslet_task, execute_hybrid

# This is a simple task we want to run on our own device.
@parslet_task
def chop_veggies():
    print("Chopping veggies on my local device...")
    return 1

# This is a bigger task we want to send to the powerful computer.
@parslet_task
def bake_pizza(ingredient):
    # This part of the code will actually run on the remote machine!
    print("Baking the pizza in the super-fast oven!")
    return ingredient + 1

if __name__ == "__main__":
    # We create our recipe as usual...
    veggies_iou = chop_veggies()
    pizza_iou = bake_pizza(veggies_iou)

    # ...but when we run it, we tell execute_hybrid which task is the "remote" one.
    results = execute_hybrid(
        [pizza_iou],
        remote_tasks=["bake_pizza"] # <-- The magic instruction!
    )

    print(f"The final result is: {results}")
```

The `execute_hybrid` tool is intentionally simple. It handles sending the right tasks to the right place for you. It's the perfect starting point for creating amazing recipes that span from your phone all the way to the cloud!