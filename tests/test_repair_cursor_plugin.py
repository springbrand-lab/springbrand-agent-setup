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

        skill = package / "plugins/springbrand/skills/springbrand/SKILL.md"
        logo = package / "plugins/springbrand/assets/springbrand-icon.svg"
        skill.unlink()
        logo.write_text("drift\n")

        command = ["python3", "scripts/repair_cursor_plugin.py"]
        subprocess.run(command, cwd=package, check=True)
        first = (skill.read_bytes(), logo.read_bytes())
        subprocess.run(command, cwd=package, check=True)

        assert first == (skill.read_bytes(), logo.read_bytes())
        assert skill.read_bytes() == (package / "skills/springbrand/SKILL.md").read_bytes()
        assert logo.read_bytes() == (package / "assets/springbrand-icon.svg").read_bytes()


if __name__ == "__main__":
    main()
