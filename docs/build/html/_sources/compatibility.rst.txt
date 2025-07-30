Compatibility Layer
===================

Parslet includes lightweight adapters allowing you to reuse familiar
Dask and Parsl style syntax. The :mod:`parslet.compat` package provides
AST transformers for converting existing scripts as well as runtime
shims that mimic a subset of each API.

Dask compatibility
------------------
Use ``parslet.compat.delayed`` and ``parslet.compat.compute`` in place
of Dask's ``dask.delayed`` and ``dask.compute``.  You can also convert a
script programmatically:

.. code-block:: python

   from parslet.compat import convert_dask_to_parslet

   new_code = convert_dask_to_parslet(open("workflow.py").read())

Parsl compatibility
-------------------
``parslet.compat.python_app`` and ``parslet.compat.bash_app`` wrap
functions similar to Parsl's decorators.  The ``convert_parsl_to_parslet``
function converts source code in bulk.

See ``examples/`` for scripts that mirror typical Dask and Parsl DAGs
running under Parslet.
