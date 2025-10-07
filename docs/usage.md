# Basic Usage

Import the core symbols directly from the package:

```python
from parslet import parslet_task, DAG, DAGRunner, ParsletFuture
```

These four names form Parslet's stable public API.

## Command-line execution

Run a workflow script directly:

```bash
parslet run path/to/workflow.py --max-workers 2
```

Workflows installed as modules are also supported:

```bash
parslet run pkg.workflow:main --json-logs --export-stats stats.json
```

Watch tasks live with ``--monitor``:

```bash
parslet run path/to/workflow.py --monitor
```

And turn exported stats into an ASCII heatmap:

```bash
python examples/tools/plot_stats.py stats.json
```

## Concierge Mode and Context Scenes

Parslet 0.6.1 ships with a concierge experience and declarative context scenes. Gate tasks with the new ``contexts`` parameter:

```python
@parslet_task(contexts=["network.online", "battery>=50"], name="evening_sync")
def evening_sync(payload):
    push_to_vault(payload)
```

Run with ``--concierge`` to receive a pre-flight briefing and post-run ledger, or ``--concierge-runbook runbook.json`` to capture the full itinerary in JSON. Manually activate scenes with repeated ``--context`` flags or via the ``PARSLET_CONTEXTS`` environment variable.
