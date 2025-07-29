# Contributing to Parslet

Thank you for considering contributing to Parslet!

## Style Guide

* Use `black` for code formatting and `flake8` for linting.
* Lines should not exceed 88 characters.
* Commit messages follow the pattern `[component] summary`.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests and linters with `pre-commit`:

```bash
pre-commit run --all-files
```

Before opening a pull request make sure to:

1. Format your code with `black`.
2. Run `flake8`, `mypy`, and `pytest` locally.
3. Avoid committing binaries or large files.
4. Clearly describe your change in the PR body.
