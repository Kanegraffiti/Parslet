# The Story of Parslet: How and Why We Built It

### The Problem We Wanted to Solve

We noticed a gap. Many of the world's most powerful software tools are built for people with powerful computers and constant, fast internet. But what about everyone else? What about the student in a village trying to analyze data on her phone, or the farmer in a remote field using a tiny Raspberry Pi to monitor his crops?

These are the people who often need automation the most, but the existing tools weren't built for their world. They were too big, too complicated, and required a connection to the cloud.

We wanted to build something for *them*. A tool that was:
- **Lightweight:** It had to run on a simple, low-cost device.
- **Offline-First:** It had to work perfectly without any internet.
- **Power-Smart:** It had to be gentle on the battery.

That's how the idea for Parslet was born.

### The Path We Chose: Keep It Simple!

When we started, we looked at using the "big kid" tools like Dask and Parsl as our foundation. They are amazing and powerful, but they came with a lot of baggage—tons of extra libraries and a design that assumed you were always online.

So, we decided to take a different path. We chose to build our own small, simple "engine" (we call it a `DAGRunner`) from scratch. This way, we could make sure it was lean, fast, and perfectly suited for the offline world.

We made sure to include a bridge back to the bigger tools. We added simple converters so that if you ever *do* get access to a supercomputer, you can easily translate your Parslet recipes to run on Parsl or Dask. It's the best of both worlds!

### The Tools We Used to Build It

We built Parslet using a handful of great, open-source tools:

-   **Python 3.11+:** The amazing and easy-to-learn language that Parslet is written in.
-   **networkx:** A fantastic library for drawing and working with graphs. This is the "magic" behind how Parslet understands the connections in your recipes.
-   **psutil:** A handy tool that lets Parslet peek at your device's memory and battery level so it can be smart about how it runs.
-   **pydot & Graphviz:** These are optional tools that let you create cool pictures of your recipes (like a flowchart).
-   **Rich:** This is what makes the output in your terminal look so nice and colorful!

### So, How Fast Is It?

We wanted to make sure Parslet was not just simple, but also efficient. The `DAGRunner` keeps a "report card" of how long each task takes.

Here's a sample from running our simple `hello.py` recipe on a basic computer:

| Task ID              | Status  | Time (seconds) |
| -------------------- | ------- | -------------- |
| add_08238910         | SUCCESS | 0.5020         |
| add_98364266         | SUCCESS | 0.5030         |
| square_dd1225c2      | SUCCESS | 0.5007         |
| square_f8a9c459      | SUCCESS | 0.5005         |
| sum_results_99bd7600 | SUCCESS | 0.5009         |

Even on a small device, each step takes about half a second.

#### What About a Raspberry Pi?

We tested the same recipe on a tiny Raspberry Pi 4, and it was still impressively efficient!

-   **Total Time to Run:** ~2.1 seconds
-   **Memory Used:** ~15 MB

This is what Parslet is all about: providing real power without needing a powerful machine.

### Want to See It in Action?

The easiest way to see what Parslet can do is to run our collection of example recipes. Just run this command from the main project folder:

```bash
python run_all_examples.py
```

This script will run several different recipes and show you their results and how fast they ran. Don't worry if you're missing some of the extra libraries; the script is smart enough to just skip the examples you can't run.