# Security Sentries

Parslet ships with a small set of *sentries* that keep workflows honest. Each
sentry is opt‑out: behaviour is locked down by default and tasks must
explicitly request more power.

## Task name sovereignty

Tasks are registered under their function name. Registering a second task with
the same name now raises an error to prevent accidental collisions. If a
redefinition is intentional use `@parslet_task(..., allow_redefine=True)`.

## Shell guard

Invoking `os.system` or `subprocess` helpers is blocked when tasks run. To run
shell commands add `allow_shell=True` to the task decorator. Without it a
helpful `SecurityError` is raised.

## Offline lock

Running the CLI with `--offline` prevents creation of sockets so that no
network traffic occurs. Any attempted network access will raise a
`SecurityError` suggesting removing the flag.

These sentries aim to provide sensible defaults while still allowing expert
users to override them when necessary.
