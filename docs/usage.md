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
