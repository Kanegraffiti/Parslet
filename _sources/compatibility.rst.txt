Compatibility Layer
===================

Parslet includes a small compatibility layer so that simple Parsl and Dask
workflows can be exchanged with Parslet. It provides two mechanisms:

* **Runtime shims** that mimic portions of each library's API.
* **Source-to-source converters** implemented as abstract syntax tree (AST)
  transforms.

.. note::

   These features are experimental and focus on pure Python code intended
   for local execution. Data staging directives, provider configuration and
   advanced Dask scheduler settings are not translated.

Dask compatibility
------------------

Drop-in replacements for :func:`dask.delayed` and :func:`dask.compute` live in
:mod:`parslet.compat`:

.. code-block:: python

   from parslet.compat import delayed, compute

   @delayed
   def add(x, y):
       return x + y

   total = compute(add(1, 2))[0]

Existing Dask scripts can be translated either programmatically or via the CLI:

.. code-block:: python

   from parslet.compat import convert_dask_to_parslet

   rewritten = convert_dask_to_parslet(open("workflow.py").read())

.. code-block:: bash

   parslet convert --from-dask workflow.py --to-parslet workflow_parslet.py

To move in the opposite direction:

.. code-block:: bash

   parslet convert --from-parslet recipe.py --to-dask recipe_dask.py

Parsl compatibility
-------------------

Parsl interoperability mirrors the Dask bridge. Parslet provides
``python_app`` and ``bash_app`` decorators as well as conversion utilities.

.. code-block:: python

   from parslet.compat import python_app

   @python_app
   def hello():
       return "hi"

.. code-block:: bash

   parslet convert --from-parsl app.py --to-parslet app_parslet.py
   parslet convert --from-parslet recipe.py --to-parsl recipe_parsl.py

Each exported script recreates the original DAG by rendering every node as a
Parsl ``@python_app`` and wiring the dependencies.

Caveats
-------

* Only pure Python task bodies are handled; Bash apps and staging directives are
  ignored.
* The generated code targets local execution and requires further tuning for
  distributed or HPC environments.
* Always review the converted source before relying on it in production.
