#!/usr/bin/env python3
"""Check that the WorkBuddy Distribution Mirrors are repaired deterministically."""

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        package = Path(directory)
        for name in ("VERSION", "hooks", "plugins", "scripts", "skills"):
            source = ROOT / name
            target = package / name
            shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)

        skill = package / "plugins/springbrand-workbuddy/skills/springbrand/SKILL.md"
        hook = package / "plugins/springbrand-workbuddy/hooks/user-prompt-submit"
        skill.unlink()
        hook.write_text("drift\n")

        command = ["python3", "scripts/repair_workbuddy_plugin.py"]
        subprocess.run(command, cwd=package, check=True)
        first = (skill.read_bytes(), hook.read_bytes())
        subprocess.run(command, cwd=package, check=True)

        assert first == (skill.read_bytes(), hook.read_bytes())
        assert skill.read_bytes() == (package / "skills/springbrand/SKILL.md").read_bytes()
        assert hook.read_bytes() == (package / "hooks/user-prompt-submit").read_bytes()
        assert hook.stat().st_mode & 0o111


if __name__ == "__main__":
    main()
