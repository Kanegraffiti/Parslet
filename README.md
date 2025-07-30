# Parslet
**A lightweight workflow engine for offline-first and edge computing.**

![Parsl-compatible](https://img.shields.io/badge/parsl-compatible-blue.svg)
![Termux-Ready](https://img.shields.io/badge/termux-ready-brightgreen.svg)
![License](https://img.shields.io/github/license/Kanegraffiti/Parslet)

Parslet is a Python library for running automated workflows, especially in environments with limited power and unreliable internet. It allows you to define a series of tasks and the dependencies between them, and it executes them as efficiently as possible—even on a Raspberry Pi or an Android phone via Termux.

**Built with Africa in mind—scalable everywhere.**

## Documentation

**The best place to start is the new [Introduction to Parslet](https://kanegraffiti.github.io/Parslet/introduction.html).**

The full documentation is published via GitHub Pages and includes a getting started guide, architecture overview, and more.

[**View the Docs**](https://kanegraffiti.github.io/Parslet/)


## Quickstart

Clone and install:

```bash
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
pip install .
```

Create a file named `my_workflow.py`:

```python
from parslet import parslet_task, ParsletFuture
from typing import List

@parslet_task
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@parslet_task
def emphasize(text: str) -> str:
    return f"{text.upper()}!"

def main() -> List[ParsletFuture]:
    # This workflow says hello, then emphasizes the greeting.
    greeting = say_hello("Parslet")
    emphasized_greeting = emphasize(greeting)
    
    # Return the final task's future
    return [emphasized_greeting]
```

Run it from your terminal:

```bash
parslet run my_workflow.py
```

---

## Use Cases & Features

Parslet is ideal for running automated pipelines on edge devices.

**Key Features:**

- **Offline-First:** No cloud connection required. Workflows run locally.
- **Power-Aware:** A `--battery-mode` reduces concurrency to save power.
- **Resource-Conscious:** Adapts to available CPU and memory.
- **Parsl & Dask Compatible:** Includes tools to convert workflows from Parsl or Dask syntax.
- **Termux Ready:** Designed and tested for use on Android devices.

See the [`use_cases/`](./use_cases) and [`examples/`](./examples) directories for real-world applications like:
- Analyzing telecom tower power logs.
- Scheduling solar panel maintenance.
- Running offline image classification for crop diagnosis.


## Docs & Architecture

- [Full Documentation](https://kanegraffiti.github.io/Parslet/)
- [Architecture Overview](https://kanegraffiti.github.io/Parslet/architecture.html)
- [CLI Commands & Usage](https://kanegraffiti.github.io/Parslet/usage.html)
- [Benchmark Results](https://kanegraffiti.github.io/Parslet/benchmark_results.html)

To rebuild the docs locally:

```bash
cd docs
make html
```

Then open `docs/build/html/index.html`.


## Contributing

We welcome contributions!

To get started:

```bash
# Install dependencies
pip install -r docs/requirements.txt
make install-dev

# Run tests
make test
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for coding guidelines.


## PyPI Installation (Coming Soon)

Once published:

```bash
pip install parslet
```


## Run All Examples

To run all examples:

```bash
python run_all_examples.py
```

Tested on:
- Android 12/14 via Termux
- Linux Mint XFCE (July 2025)


## Project Structure

```
parslet/            → Core DAG engine, hybrid plugins, scheduler
docs/               → Sphinx docs + visuals
examples/           → Minimal and advanced use cases
tests/              → Unit tests
use_cases/          → Real-world deployment DAGs
termux/             → CLI helpers for Android
scripts/            → Automation tools
```


## License

This project is licensed under the MIT License.  
See [LICENSE](./LICENSE) for full details.


## Acknowledgements

Built by [Kelechi Nwankwo](https://github.com/Kanegraffiti) during the **Africa Deep Tech Challenge 2025**  
Inspired by [Parsl](https://github.com/Parsl/parsl)  
Gratitude to the Outreachy community and the Parsl core maintainers.
