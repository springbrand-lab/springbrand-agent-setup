#!/usr/bin/env python3
"""Repair generated WorkBuddy Distribution Mirrors from canonical assets."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    ROOT / "skills/springbrand/SKILL.md": ROOT / "plugins/springbrand-workbuddy/skills/springbrand/SKILL.md",
    ROOT / "hooks/user-prompt-submit": ROOT / "plugins/springbrand-workbuddy/hooks/user-prompt-submit",
}

for source, destination in COPIES.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
