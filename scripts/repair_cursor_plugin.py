#!/usr/bin/env python3
"""Repair generated Cursor Distribution Mirror assets from canonical sources."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    ROOT / "skills/springbrand/SKILL.md": ROOT / "plugins/springbrand/skills/springbrand/SKILL.md",
    ROOT / "assets/springbrand-icon.svg": ROOT / "plugins/springbrand/assets/springbrand-icon.svg",
}

for source, destination in COPIES.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
