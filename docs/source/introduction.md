# Introduction to Parslet

Welcome to Parslet! This guide will introduce you to what Parslet is, why it's useful, and the basic concepts behind it.

## What is Parslet?

Imagine you have a recipe with several steps. Some steps you can do at the same time (like chopping vegetables while the oven preheats), while others must be done in a specific order (you have to bake the cake before you can frost it).

**Parslet is a tool that helps you write down your "recipe" of computational steps as a Python script and then runs it for you as efficiently as possible.**

Each step in your recipe is a **Task**. Parslet automatically figures out the correct order to run your tasks and can even run independent tasks in parallel to save time. The entire recipe, with all its steps and their connections, is called a **DAG** (Directed Acyclic Graph).

## What Problem Does Parslet Solve?

Parslet is designed specifically for devices that have **limited power and unreliable internet access**, like:

*   A tablet used for collecting survey data in a remote village.
*   A Raspberry Pi monitoring a solar panel installation.
*   A smartphone analyzing crop photos directly in the field.

In these environments, you can't rely on a powerful cloud server. Workflows need to run entirely offline and be mindful of battery life. Parslet is lightweight, works offline-first, and even has a **battery-saver mode** to reduce power consumption.

## How Does It Work? The Core Concepts

There are three key ideas in Parslet:

#### 1. Task (`@parslet_task`)

A task is just a regular Python function that you decorate with `@parslet_task`. This tells Parslet that the function is a step in your workflow.

```python
from parslet import parslet_task

@parslet_task
def add(a, b):
    return a + b
```

#### 2. Future (`ParsletFuture`)

When you *call* a task function, it doesn't run right away. Instead, it immediately returns a **`ParsletFuture`** object. This object is a placeholder, like an IOU, for the result that will be available *in the future* once the task actually runs.

```python
# This does NOT calculate 3+4 yet.
# It returns a future object that represents the eventual result.
future_result = add(3, 4) 
```

#### 3. DAG (The Workflow)

You create a workflow (a DAG) by passing the `ParsletFuture` from one task as an input to another. This is how you create dependencies.

```python
@parslet_task
def square(x):
    return x * x

# The `square` task depends on the `add` task.
# Parslet knows it must wait for `add` to finish before it can run `square`.
future_sum = add(3, 4)
future_squared = square(future_sum) 
```

The `DAGRunner` is the engine that looks at your chain of futures, builds the graph of dependencies, and executes the tasks in the correct order.

## How is Parslet Different?

| Feature           | Parslet                                       | Parsl / Dask                                       |
| ----------------- | --------------------------------------------- | -------------------------------------------------- |
| **Best For**      | Offline, low-power devices (phones, R-Pi)     | HPC clusters, cloud servers, big data analytics    |
| **Main Goal**     | Reliability and efficiency in any environment | Maximum performance on powerful, connected systems |
| **Dependencies**  | Very few, lightweight                         | More complex, designed for distributed computing   |

Parslet is your go-to tool for simple, reliable automation on the edge. When your project grows and you have access to high-performance computing (HPC) resources, Parslet includes tools to help you convert your workflows to run on powerful systems like Parsl.

Ready to get started? Head over to the [Getting Started](./getting_started.md) guide!
