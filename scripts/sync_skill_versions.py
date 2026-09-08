#!/usr/bin/env python3
"""Stamp Canonical Skills and their Distribution Mirrors from VERSION."""

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MIRRORS = ("plugins/springbrand/skills", "plugins/springbrand-workbuddy/skills")


def stamp_version(text: str, version: str) -> str:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("SKILL.md must have YAML frontmatter")
    frontmatter, body = text[4:].split("\n---\n", 1)
    lines = frontmatter.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("metadata:")]
    field = f"  version: {json.dumps(version)}"
    if not starts:
        lines.extend(["metadata:", field])
    else:
        if len(starts) != 1 or lines[starts[0]].strip() != "metadata:":
            raise ValueError("metadata must use a single block mapping")
        start = starts[0]
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i] and not lines[i][0].isspace()
                    and not lines[i].startswith("#")), len(lines))
        fields = [i for i in range(start + 1, end) if lines[i].startswith("  version:")]
        if len(fields) > 1:
            raise ValueError("duplicate metadata.version")
        if fields:
            lines[fields[0]] = field
        else:
            lines.insert(start + 1, field)
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def sync(root: Path = ROOT, *, check: bool = False) -> list[str]:
    version = (root / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", version):
        raise ValueError("VERSION must contain a release version without a v prefix")
    sources = sorted((root / "skills").glob("*/SKILL.md"))
    if not sources:
        raise ValueError("No Canonical Skills found")
    updates = {}
    for source in sources:
        stamped = stamp_version(source.read_text(), version)
        for target in [source, *(root / mirror / source.parent.name / "SKILL.md" for mirror in MIRRORS)]:
            if target.read_text() != stamped:
                updates[target] = stamped
    if not check:
        for path, text in updates.items():
            path.write_text(text)
    return [str(path.relative_to(root)) for path in updates]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report version or mirror drift without writing")
    args = parser.parse_args()
    changed = sync(check=args.check)
    if args.check and changed:
        raise SystemExit("Skill version/mirror drift; run python3 scripts/sync_skill_versions.py:\n" + "\n".join(changed))
    print(f"Skill versions: {'checked' if args.check else 'synchronized'} with VERSION ({len(changed)} changes)")


if __name__ == "__main__":
    main()
