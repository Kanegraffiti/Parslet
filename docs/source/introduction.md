# Introduction: What is Parslet, Really?

Welcome to Parslet! If you've ever wished you had a personal assistant for your computer or phone that could run a bunch of tasks for you automatically, you've come to the right place.

## Let's Start with a Story

Imagine you have a recipe for your favorite smoothie. It has several steps:

1.  **Chop** the bananas and strawberries.
2.  **Pour** in the milk.
3.  **Add** a scoop of protein powder.
4.  **Blend** everything together.

Some steps have to happen in order (you can't blend before you add the milk), but others could happen at the same time (you could chop the fruits while you get the milk).

**Parslet is a tool that helps you write down this "recipe" of computer tasks in a Python script and then runs it for you as smartly as possible.**

Each step in your recipe is a **Task**. Parslet automatically figures out the correct order to run your tasks and can even run independent tasks in parallel to save time. The entire recipe, with all its steps and their connections, is called a **DAG** (a fancy term for a workflow path).

## What Problem Does Parslet Solve?

Parslet is designed for a world where not everyone has a supercomputer or a perfect internet connection. It’s for:

*   A student in a rural area using a tablet to collect and analyze survey data.
*   A farmer using a Raspberry Pi to monitor a solar-powered irrigation system.
*   A developer in a bustling city, prototyping an app on their phone while on the go.

In these situations, you can't rely on the cloud. Workflows need to run **offline** and be **mindful of battery life**. Parslet is lightweight, works offline by default, and even has a **battery-saver mode** to keep you running longer.

## The Three Big Ideas in Parslet

There are just three core concepts you need to know.

#### 1. The Task (`@parslet_task`)

A task is just a regular Python function. You just add `@parslet_task` on top to let Parslet know it's a step in your workflow.

```python
from parslet import parslet_task

@parslet_task
def add(a, b):
    # This is a simple task that adds two numbers.
    return a + b
```

#### 2. The "IOU" Note (`ParsletFuture`)

Here's the cool part. When you *call* a task, it doesn't run right away. Instead, it gives you back a placeholder, like an IOU note. We call this a **`ParsletFuture`**.

This IOU note is a promise that the result will be available *in the future*, once the task actually runs.

```python
# This does NOT calculate 3 + 4 yet.
# It just gives you an IOU for the result.
future_result = add(3, 4)
```

#### 3. The Workflow (Connecting the Dots)

You create your workflow by passing the IOU from one task as an input to another. This is how you tell Parslet the order of your steps.

```python
@parslet_task
def square(x):
    return x * x

# We give the `square` task the IOU from our `add` task.
# Parslet now knows it must wait for `add` to finish
# before it can run `square`.
future_sum = add(3, 4)
future_squared = square(future_sum)
```

The **`DAGRunner`** is the engine that looks at your chain of IOUs, builds the map of your workflow, and runs everything in the right order.

## How is Parslet Different from the Big Guys?

You might have heard of other workflow tools like **Parsl** or **Dask**. They are amazing, but they're built for a different job.

| Feature        | Parslet                                     | Parsl / Dask                                     |
| -------------- | ------------------------------------------- | ------------------------------------------------ |
| **Best For**   | Offline, low-power devices (phones, R-Pi)   | Supercomputers, cloud servers, big data analysis |
| **Main Goal**  | Reliability and simplicity, anywhere        | Maximum power on high-performance systems        |
| **Complexity** | Very few dependencies, easy to install      | More complex, designed for distributed computing |

Parslet is your go-to tool for automation on the edge. And when your project gets big enough for the supercomputers, Parslet gives you tools to "graduate" your workflow to run on Parsl.

Ready to build your first workflow? Let's get started!