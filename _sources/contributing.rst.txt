Contributing
============

We welcome contributions of all kinds: bug reports, new features and
documentation improvements.

If you add new tasks or examples, please update the guides in ``docs/`` so
readers know how to use them.

Style guide
-----------

* Format code with ``black`` and lint with ``flake8``.
* Keep lines under 88 characters.
* Commit messages follow the pattern ``[component] summary``.

Development workflow
--------------------

Install the required packages and run the pre‑commit hooks before submitting a
pull request:

.. code-block:: bash

   pip install -r requirements.txt
   pre-commit run --all-files

All tests under ``tests/`` should pass.  Feel free to open an issue first if you
want to discuss large changes.
