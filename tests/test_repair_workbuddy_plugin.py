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

        canonical = sorted((package / "skills").glob("*/SKILL.md"))
        assert len(canonical) == 4, canonical
        mirrors = [
            package / "plugins/springbrand-workbuddy/skills" / skill.parent.name / "SKILL.md"
            for skill in canonical
        ]
        hook = package / "plugins/springbrand-workbuddy/hooks/user-prompt-submit"
        for mirror in mirrors:
            mirror.unlink()
        hook.write_text("drift\n")

        command = ["python3", "scripts/repair_workbuddy_plugin.py"]
        subprocess.run(command, cwd=package, check=True)
        first = [(mirror.read_bytes(), hook.read_bytes()) for mirror in mirrors]
        subprocess.run(command, cwd=package, check=True)

        assert first == [(mirror.read_bytes(), hook.read_bytes()) for mirror in mirrors]
        for mirror, skill in zip(mirrors, canonical):
            assert mirror.read_bytes() == skill.read_bytes()
        assert sorted(path.name for path in (package / "plugins/springbrand-workbuddy/skills").glob("*")) == [
            skill.parent.name for skill in canonical
        ]
        assert hook.read_bytes() == (package / "hooks/user-prompt-submit").read_bytes()
        assert hook.stat().st_mode & 0o111


if __name__ == "__main__":
    main()
