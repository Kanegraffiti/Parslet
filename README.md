<div id="top"></div>

<p align="center">
  <img src="docs/assets/parslet_banner.svg" alt="Parslet" width="70%" />
</p>

<p align="center">
  <em>Simplify Python workflows with a minimal DAG engine.</em>
</p>

<p align="center">
  <a href="https://github.com/Kanegraffiti/Parslet/actions/workflows/ci.yml">
    <img src="https://github.com/Kanegraffiti/Parslet/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
  </a>
  <a href="https://github.com/Kanegraffiti/Parslet/actions/workflows/docs.yml">
    <img src="https://github.com/Kanegraffiti/Parslet/actions/workflows/docs.yml/badge.svg" alt="Docs Status" />
  </a>
  <img src="https://img.shields.io/badge/version-0.5.0-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge" alt="Python Versions" />
  <a href="https://opensource.org/license/mit/">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License" />
  </a>
</p>

<img src="https://raw.githubusercontent.com/eli64s/readme-ai/main/docs/docs/assets/svg/line-gradient.svg" width="100%" height="3px" alt="line" />

## Quick Links
- [Introduction](#introduction)
- [Features](#features)
- [Quickstart](#quickstart)
- [Optional Extras](#optional-extras)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

<img src="https://raw.githubusercontent.com/eli64s/readme-ai/main/docs/docs/assets/svg/line-gradient.svg" width="100%" height="3px" alt="line" />

## Introduction
Parslet lets you describe tasks as Python functions and arrange them into Directed Acyclic Graphs (DAGs). It executes tasks in the right order, handles parallelism where possible and runs entirely offline. Perfect for small automation scripts or edge devices. When you need to scale out, the same tasks can be run under Parsl thanks to a lightweight bridge module.

## Features
- **Simple decorators.** Turn functions into tasks with `@parslet_task`.
- **Automatic dependencies.** Pass future results between tasks and let Parslet build the DAG.
- **Thread-based execution.** Parallelize independent tasks with adaptive worker counts.
- **Battery aware.** Optional scheduler reduces workers on low-power systems.
- **Exportable DAGs.** Output to DOT or PNG for easy visualization.
- **Compatibility adapters.** Interoperate with Parsl and Dask using
  `convert_task_to_parsl` and `parslet.compat.dask_adapter`. The
  `parslet convert` command translates existing workflows. See the
  [docs](docs/getting_started.md#converting-existing-parsl-or-dask-workflows)
  for details.
- **Hybrid execution.** Combine local runs with Parsl-managed tasks via `execute_hybrid`.
- **Federated relay.** Use `FileRelay` to copy results to a remote gateway.

## Quickstart
Clone this repository and install Parslet in editable mode:
```bash
git clone https://github.com/Kanegraffiti/Parslet.git
cd Parslet
pip install -e .
parslet run examples/hello.py --battery-mode
```
The last command runs a tiny demo workflow with battery-saver settings.

## Optional Extras
Install compatibility packages as needed:
```bash
pip install parslet[dask]
pip install parslet[parsl]
```

## Examples
Explore the `examples/` folder for small demos like image processing and text cleaning. Some examples such as `mobile_edge_inference` and `multi_ai_diagnosis` will try to load lightweight models from [Hugging Face](https://huggingface.co/) using the `transformers` library. If the models cannot be downloaded (e.g. in an offline environment) these scripts gracefully fall back to deterministic stub behaviour. Real-world use cases live in `use_cases/`.
See `docs/project_report.md` for a detailed project report including sample benchmarks.

## Testing
Install the development requirements and run the unit tests:
```bash
pip install -r requirements.txt
pytest
```
All tests should pass. Running `flake8` ensures the code style matches the project's guidelines.

## Contributing
Pull requests are welcome! Please format with `black` and run `flake8` and `pytest` before submitting.

## License
Parslet is distributed under the [MIT License](LICENSE).

