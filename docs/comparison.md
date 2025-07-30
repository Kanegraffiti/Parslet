# Parslet vs. Other Tools (Parsl, Dask)

Parslet is one of many workflow tools available for Python. This guide helps you understand when to choose Parslet versus more complex tools like Parsl or Dask.

The main takeaway: **Parslet is designed for simplicity and reliability on single, often resource-constrained devices.** Parsl and Dask are designed for power and scale on clusters of machines.

### When to Use Parslet
Choose Parslet when:
- Your workflow needs to run **offline**.
- You are working on a device with **limited power**, like a laptop on battery, a Raspberry Pi, or a phone.
- You need a simple, lightweight tool with **very few dependencies**.
- You are teaching or learning the concepts of workflow automation.

### When to Use Parsl or Dask
Consider graduating to Parsl or Dask when:
- You need to distribute your workflow across **multiple computers** (i.e., a cluster or the cloud).
- You are working with **massive datasets** that don't fit into your computer's memory.
- You need to connect to specialized hardware or schedulers in a High-Performance Computing (HPC) environment.

### Feature Comparison

The table below outlines some key differences.

| Feature           | Parslet                                       | Parsl                                              | Dask                                               |
| ----------------- | --------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| **Best For**      | Simple, offline pipelines on a single device  | Large-scale scientific workflows on HPC clusters   | Parallelizing large-scale data analysis            |
| **Execution**     | Locally, on your device's thread pool         | Can execute on remote machines (HPC, cloud)        | Schedulers and workers on local or remote machines |
| **Installation**  | Minimal dependencies, no cluster needed       | Requires a backend (e.g., HTCondor, Kubernetes)    | Often used with a distributed scheduler            |
| **Task Definition** | `@parslet_task` decorator                     | `@python_app` or `@bash_app` decorators            | `dask.delayed` or high-level APIs (DataFrame)      |

Parslet is a great starting point. It even includes utilities to help you convert your Parslet workflows to Parsl if you ever need to scale up!
