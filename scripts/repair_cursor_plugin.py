#!/usr/bin/env python3
"""Repair generated Cursor Distribution Mirror assets from canonical sources."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
REFERENCES = sorted((ROOT / "skills").glob("*/references/*.md"))
COPIES = {
    ROOT / "assets/springbrand-icon.svg": ROOT / "plugins/springbrand/assets/springbrand-icon.svg",
    ROOT / "rules/springbrand-preflight.mdc": ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc",
}
COPIES.update({
    skill: ROOT / "plugins/springbrand/skills" / skill.parent.name / "SKILL.md"
    for skill in SKILLS
})
COPIES.update({
    reference: ROOT / "plugins/springbrand/skills" / reference.parent.parent.name / "references" / reference.name
    for reference in REFERENCES
})

if not SKILLS:
    raise SystemExit("no canonical skills found under skills/*/SKILL.md")

for source, destination in COPIES.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
