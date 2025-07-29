# Offline Survey Flow

Collect survey responses in the field on inexpensive Android devices. The workflow stores answers locally, applies basic validation and compresses them into an archive. When connectivity is restored, the archive can be uploaded to a central server. The main constraint is the absence of constant internet access, so the tasks avoid cloud dependencies and minimize storage overhead.

**Expected output:** `Parslet_Results/<timestamp>/survey.zip` containing validated responses and diagnostics.
