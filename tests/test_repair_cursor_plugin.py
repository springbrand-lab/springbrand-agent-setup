#!/usr/bin/env python3
"""Check that the Cursor Distribution Mirror is repaired deterministically."""

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        package = Path(directory)
        for name in ("VERSION", "assets", "plugins", "scripts", "skills"):
            source = ROOT / name
            target = package / name
            shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)

        canonical = sorted((package / "skills").glob("*/SKILL.md"))
        assert len(canonical) == 4, canonical
        mirrors = [
            package / "plugins/springbrand/skills" / skill.parent.name / "SKILL.md"
            for skill in canonical
        ]
        logo = package / "plugins/springbrand/assets/springbrand-icon.svg"
        for mirror in mirrors:
            mirror.unlink()
        logo.write_text("drift\n")

        command = ["python3", "scripts/repair_cursor_plugin.py"]
        subprocess.run(command, cwd=package, check=True)
        first = [(mirror.read_bytes(), logo.read_bytes()) for mirror in mirrors]
        subprocess.run(command, cwd=package, check=True)

        assert first == [(mirror.read_bytes(), logo.read_bytes()) for mirror in mirrors]
        for mirror, skill in zip(mirrors, canonical):
            assert mirror.read_bytes() == skill.read_bytes()
        assert sorted(path.name for path in (package / "plugins/springbrand/skills").glob("*")) == [
            skill.parent.name for skill in canonical
        ]
        assert logo.read_bytes() == (package / "assets/springbrand-icon.svg").read_bytes()


if __name__ == "__main__":
    main()
