# Telecom Tower Power Monitor

This workflow focuses on remote telecom sites that rely on hybrid power setups.
Daily logs from the tower are analyzed to measure battery health, generator run
time and average solar output. A simple rule-based predictor recommends
maintenance actions such as battery replacement or generator inspection.
The DAG can run entirely offline on a low-power computer located at the tower.

**Expected output:** `Parslet_Results/<timestamp>/tower_report.json` summarizing
metrics and recommended actions.
