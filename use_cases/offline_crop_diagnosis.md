# Offline Crop Diagnosis

This workflow targets farmers operating in remote fields with little or no connectivity. A lightweight CNN model analyzes leaf photos to detect common diseases entirely offline. The steps capture an image, run the classifier and store a JSON report that can be synchronized when a connection becomes available. Power usage is kept low so it can run on a small battery-powered computer. The expected outcome is a local diagnosis file with probability scores for each captured image.

**Expected output:** `Parslet_Results/<timestamp>/diagnosis.json` containing predictions and resource information.
