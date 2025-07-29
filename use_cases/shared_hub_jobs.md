# Shared Hub Jobs

Edge sensors occasionally connect to a shared hub to offload heavy computation. This workflow queues incoming jobs, processes them when power is available and stores results on disk. Key constraints include unpredictable connectivity between sensors and the hub along with tight resource budgets on the hub itself.

**Expected output:** `Parslet_Results/<timestamp>/results.json` with processed job data and diagnostics.
