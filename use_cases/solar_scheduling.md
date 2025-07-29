# Solar Scheduling

Demonstrates how Parslet can orchestrate maintenance tasks for a small solar installation. Historical power data is analyzed to estimate panel efficiency and trigger cleaning events. The DAG runs entirely offline on a Raspberry Pi with limited RAM, illustrating how battery-aware scheduling prevents long-running analytics from draining the system.

**Expected output:** `Parslet_Results/<timestamp>/schedule.json` describing the average efficiency and recommended action.
