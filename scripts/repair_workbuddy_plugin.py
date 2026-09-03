#!/usr/bin/env python3
"""Repair generated WorkBuddy Distribution Mirrors from canonical assets."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
REFERENCES = sorted((ROOT / "skills").glob("*/references/*.md"))
COPIES = {
    ROOT / "hooks/user-prompt-submit": ROOT / "plugins/springbrand-workbuddy/hooks/user-prompt-submit",
}
COPIES.update(
    {
        skill: ROOT / "plugins/springbrand-workbuddy/skills" / skill.parent.name / "SKILL.md"
        for skill in SKILLS
    }
)
COPIES.update(
    {
        reference: ROOT
        / "plugins/springbrand-workbuddy/skills"
        / reference.parent.parent.name
        / "references"
        / reference.name
        for reference in REFERENCES
    }
)

if not SKILLS:
    raise SystemExit("no canonical skills found under skills/*/SKILL.md")

for source, destination in COPIES.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
