# Parslet: Your Pocket-Sized Workflow Assistant
**A tool for running automated to-do lists (workflows) on your Python projects. It's built to work anywhere, especially on your android phone.**

![Parsl-compatible](https://img.shields.io/badge/parsl-compatible-purple.svg)
![Termux-Ready](https://img.shields.io/badge/termux-ready-purple.svg)
![License](https://img.shields.io/github/license/Kanegraffiti/Parslet)
![PyPI version](https://img.shields.io/pypi/v/parslet)

### What is Parslet?

Parslet is a tiny workflow engine built in Python. That means it's a tool that helps you automate tasks in a specific order, especially on phones and devices that can’t run heavy-duty software. Think of it like a smart to-do list for your computer or phone, but instead of reminding you to do things, **it actually does them for you in the right order, automatically.**

Imagine this real-world example:

You run a small juice business with your best friend. Every morning you:

1.  Wash the fruits
2.  Peel them
3.  Blend them
4.  Pour into bottles
5.  Label and store

Now imagine you could automate this entire process using a small robot. You just tell it the steps once, and it does them every morning, in order. You get to spend quality time with your best friend.

**That’s what Parslet does, but for software tasks.**

---

### What Kinds of Tasks Can It Handle?

In a real-world tech setting, you could use Parslet to:

1.  Run a script to **collect data** from a website.
2.  Then, **clean up** that messy data.
3.  Then, **save** the clean data to a file.
4.  Then, **back up** that file to a server.
5.  Finally, **send you an email** confirming the job is done.

All of this, in the right order, without you needing to supervise it.

---

### Why is Parslet Special?

Most tools like this are built for powerful servers in a data center. Parslet is different. It’s designed from the ground up to:

-   **Be Super Lightweight:** It works on a Raspberry Pi or even an Android phone.
-   **Run in Termux:** It’s built and tested to work perfectly inside [Termux](https://termux.dev/en/), the command-line tool for Android.
-   **Work Offline:** No internet? No problem. Your workflows will still run.
-   **Empower Everyone:** It’s for students, creators, and developers who might not have a laptop but have a brilliant idea.

---

### How Does It Work?

It uses something called a **DAG** (Directed Acyclic Graph), which is just a technical way of saying:

> “Step B only runs after Step A is done.”

You define these steps (we call them **Tasks**) in a simple Python file. Parslet reads your file, understands the order, and handles the rest. It manages failures and runs everything as efficiently as possible.

---

## Get Started

Ready to try it? You can be up and running in less than a minute.

1.  **Install It:**

    The easiest way to install Parslet is directly from PyPI.

    ```bash
    pip install parslet
    ```

2.  **For Developers (or to get the latest changes):**

    If you want to contribute or get the very latest code, you can install it from the source.

    ```bash
    git clone https://github.com/Kanegraffiti/Parslet.git
    cd Parslet
    pip install -e .
    ```

3.  **Create Your First Workflow**

    Create a new file called `my_first_workflow.py` and paste this in. This is your recipe, telling Parslet what to do.

    ```python
    from parslet import parslet_task, ParsletFuture
    from typing import List

    # This is a "task." It's just a normal Python function
    # with a special @parslet_task note for Parslet.
    @parslet_task
    def say_hello(name: str) -> str:
        print(f"Task 1: Saying hello to {name}")
        return f"Hello, {name}!"

    # Here's a second task.
    @parslet_task
    def make_it_loud(text: str) -> str:
        print("Task 2: Making the text loud!")
        return f"{text.upper()}!"

    # This is the main "recipe" function.
    # Parslet looks for this to know how your tasks connect.
    def main() -> List[ParsletFuture]:
        # First, we tell Parslet to run the say_hello task.
        # It doesn't run yet! It just gives us an "IOU" for the result.
        greeting_iou = say_hello("Parslet")
        
        # Next, we give the "IOU" from the first task to the second task.
        # This tells Parslet: "Wait for task 1 to finish before starting task 2."
        loud_greeting_iou = make_it_loud(greeting_iou)

        # We return the very last IOU. This tells Parslet, "We're done when this is done."
        return [loud_greeting_iou]
    ```

4.  **Run It**

    Now for the fun part. Tell Parslet to run your new workflow.

    ```bash
    parslet run my_first_workflow.py
    ```

You'll see the `print` statements from your tasks as they run, in the correct order 🎉

You can also reference a workflow by module path and tweak execution:

```bash
parslet run my_package.workflow:main --max-workers 4 --json-logs --export-stats stats.json
```

---

## What Else Can It Do?

Parslet is small, but it's packed with neat features for real-world use.

-   **Works Offline:** Your automated workflows run even without an internet connection. See the [examples](docs/examples.md).
-   **Saves Battery:** Use the special `--battery-mode` to tell Parslet to take it easy and conserve power. Read about [battery mode](docs/source/battery_mode.rst).
-   **Smart About Resources:** It automatically checks your device's CPU and memory to run smoothly without crashing. The [AdaptivePolicy](docs/policy.md) adjusts workers on the fly.
-   **DEFCON:** A multi-layered defense system in Parslet that proactively blocks zero-day exploits and malicious DAG behavior using offline rules. Learn more in the [security notes](docs/technical-overview.md).
-   **Plays Well with Others:** If you ever move to a big server, Parslet has tools to convert your recipes to run on powerful systems like Parsl or Dask. See [compatibility](docs/compatibility.md).
-   **Made for Termux:** We use it and test it on Android phones, so you know it'll work. Check the [install guide](docs/install.md).

Want to see more? Check out the `use_cases/` and `examples/` folders for more advanced recipes!

---

## Visualizing Your Workflows

Parslet can generate a picture of your workflow (a "DAG") to help you see how your tasks are connected. This is great for debugging and documentation.

To use this feature, you need to have **Graphviz** installed on your system.

-   **On Linux (Debian/Ubuntu):** `sudo apt install graphviz`
-   **On Linux (Fedora):** `sudo dnf install graphviz`
-   **On Android (Termux):** `pkg install graphviz`
-   **On Windows:** Download and run the installer from the [official Graphviz website](https://graphviz.org/download/) and make sure to add it to your system's PATH.

You will also need the `pydot` Python package, which is included in `requirements.txt`.

Once Graphviz is installed, you can use the `--export-png` flag with the `run` command:

```bash
parslet run my_first_workflow.py --export-png my_workflow.png
```

This will create an image file named `my_workflow.png` showing your workflow.

---

## Want to Learn More? (Documentation)

We've written down everything you need to know in a simple, friendly way.

-   [**See All Features (Full Documentation)**](https://parslet.readthedocs.io/en/latest/)
-   [**How It Really Works (Architecture)**](https://parslet.readthedocs.io/en/latest/architecture.html)
-   [**The Remote Control (CLI Commands)**](https://parslet.readthedocs.io/en/latest/usage.html)

---

## Contributing

We'd love your help making Parslet even better. It's easy to get started. Check out our [Contributing Guide](./CONTRIBUTING.md).

## Development

Install dependencies and run the checks:

```
pip install -e .[dev]
pip install -r requirements-dev.txt
ruff parslet/core/__init__.py tests/test_imports.py
black --check parslet/core/__init__.py tests/test_imports.py
mypy
pytest -q
```

---

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for the full text.

## Acknowledgements

Inspired by the powerful [Parsl](https://github.com/Parsl/parsl) project.  
A big thank you to the Outreachy community and the Parsl maintainers.
