Testing
=======

This guide explains how to run Parslet's test suite and verify your environment.
It is aimed at newcomers who may not have used ``pytest`` or the ``pre-commit``
tooling before.

Running the tests
-----------------

The project uses ``pytest`` for all unit tests located under the ``tests/``
directory.  Install the development requirements and run ``pytest`` from the
repository root:

.. code-block:: bash

   pip install -r requirements.txt
   pip install -r docs/requirements.txt  # for docs tests if any
   pytest

The command will discover and execute all tests.  A ``.pytest_cache`` directory
may be created to speed up subsequent runs.

Pre-commit hooks
----------------

Before submitting a pull request, run the ``pre-commit`` hooks to check code
style and linting.  Install ``pre-commit`` once:

.. code-block:: bash

   pip install pre-commit
   pre-commit install

Then run all hooks:

.. code-block:: bash

   pre-commit run --all-files

This formats your code with ``black`` and lints with ``flake8`` to ensure it
matches the repository's style guidelines.

Continuous integration
----------------------

All pushes and pull requests automatically run the test suite in continuous
integration.  Make sure tests pass locally so CI succeeds.
