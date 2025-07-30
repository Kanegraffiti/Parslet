Security Sentries
=================

Parslet includes lightweight security checks called *Defcons*.

Defcon 1
  Validates changed Python files in pull requests to ensure they do not use
  dangerous functions like ``exec`` or ``os.system``.

Defcon 2
  Provides a ``sandbox_task`` decorator that prevents tasks from using modules
  such as ``os`` or ``subprocess`` at runtime.

Defcon 3
  Attaches a trap to the ``DAGRunner`` that freezes the DAG and writes a
  ``crash.log`` if an uncaught exception bubbles up.
