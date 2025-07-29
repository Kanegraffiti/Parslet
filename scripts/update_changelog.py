#!/usr/bin/env python3
"""Auto-update CHANGELOG.md with new commit messages."""
import subprocess
import re
from pathlib import Path

changelog = Path("CHANGELOG.md")
existing = changelog.read_text().splitlines()
# Extract existing bullet lines
existing_entries = [
    re.sub(r"^- ", "", line) for line in existing if line.startswith("- ")
]
existing_set = set(existing_entries)

# Find last commit that touched CHANGELOG
last_commit = (
    subprocess.check_output(["git", "log", "-1", "--format=%H", "--", "CHANGELOG.md"])
    .decode()
    .strip()
)

# Collect commit subjects since last changelog update
log = (
    subprocess.check_output(["git", "log", f"{last_commit}..HEAD", "--pretty=%s"])
    .decode()
    .splitlines()
)
new_entries = [
    msg
    for msg in reversed(log)
    if msg not in existing_set and not msg.startswith("Merge")
]

if not new_entries:
    exit(0)

with changelog.open("a") as f:
    for msg in new_entries:
        f.write(f"- {msg}\n")
