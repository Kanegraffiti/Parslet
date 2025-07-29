# Triage Tool

A small medical triage assistant designed for clinics with spotty internet. Patient symptoms are entered through a simple form, scored using a local rules engine and saved to a CSV file. When a connection is present, the data can be synchronized with a larger EMR system. The pipeline must run on low-power tablets and remain functional entirely offline.

**Expected output:** `Parslet_Results/<timestamp>/triage.csv` listing the forms with an assigned severity score.
