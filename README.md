# Parslet   
**Power-Aware, Android-Native Workflow Automation Framework**

![Parsl-compatible](https://img.shields.io/badge/parsl-compatible-blue.svg)
![Termux-Ready](https://img.shields.io/badge/termux-ready-brightgreen.svg)
![License](https://img.shields.io/github/license/Kanegraffiti/Parslet)


Parslet is a lightweight, offline-friendly workflow automation engine inspired by [Parsl](https://parsl-project.org/) and optimized for constrained environments like Android tablets, solar-powered stations, and remote telecom sites.  
It supports DAG-based execution, dynamic plugin loading, offline failover strategies, and compatibility layers for both Parsl and Dask.

**Built with Africa in mind — scalable everywhere.**


## Live Documentation

[View the Docs](https://kanegraffiti.github.io/Parslet/)

Published via GitHub Pages using Sphinx.


## Quickstart

Clone and install:

```bash
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
pip install .
```

Run a minimal workflow:

```python
from parslet import Task, DAG

def hello(name):
    return f"Hello, {name}!"

greet = Task(fn=hello, inputs=["Parsl"])
dag = DAG(tasks=[greet])
dag.run()
```

---

## Deep Tech Use Case: Power + Telecom Innovation

> Submitted under the **IHS Challenge category** for Africa Deep Tech Challenge 2025.

**Highlights:**

- **Solar Scheduling DAGs**  
  Automate energy distribution based on sunlight, battery state, and load priority.

- **Remote Monitoring for Power Infrastructure**  
  Build intelligent pipelines for telecom towers using battery, inverter, and grid metrics.

- **Failover & Power-Conscious Mode**  
  Pause/resume DAGs based on low battery conditions to protect uptime.

- **Hybrid Orchestration**  
  Relay DAGs between mobile and cloud intelligently via plugin adapters.

 See examples: [`/use_cases`](./use_cases)  
 Related doc section: [Challenge](https://kanegraffiti.github.io/Parslet/challenge.html)


## Features

- Offline-first CLI and plugin architecture
- Termux + Android support out-of-the-box
- Power-aware and voltage-triggered DAG pausing
- Hybrid cloud/mobile orchestration plugins
- Export compatibility with Parsl and Dask
- SVG flowchart auto-generation from DAGs
- Strong test suite and linting


## Docs & Architecture

- [ Full Documentation](https://kanegraffiti.github.io/Parslet/)
- [ Architecture Overview](https://kanegraffiti.github.io/Parslet/architecture.html)
- [ CLI Commands & Usage](https://kanegraffiti.github.io/Parslet/usage.html)
- [ Benchmark Results](https://kanegraffiti.github.io/Parslet/benchmark_results.html)

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
