#!/usr/bin/env python3
"""Run the production PR sync step against a temporary local Git remote."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_dev_variant as dev
from test_validator import copy_package
from test_release_identity import PACKAGING_MANIFESTS


def main():
    workflow = (ROOT / ".github/workflows/validate-plugin.yml").read_text()
    step = workflow.split("      - name: Synchronize production Skills before merge\n", 1)[1]
    script = textwrap.dedent(step.split("        run: |\n", 1)[1].split("\n  package-contract:", 1)[0])
    version = "9.8.7-beta.6"
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        package = temp / "package"
        package.mkdir()
        copy_package(package)
        for name in ("scripts", "tests", ".github"):
            shutil.copytree(ROOT / name, package / name, ignore=shutil.ignore_patterns("__pycache__"))
        old_version = (package / "VERSION").read_text().strip()
        replacements = [(value, getattr(dev, "PROD_" + name[4:]))
                        for name, value in vars(dev).items()
                        if name.startswith("DEV_") and isinstance(value, str)
                        and hasattr(dev, "PROD_" + name[4:])]
        # Use production fixture identities on both dev and production checkouts.
        for rel in PACKAGING_MANIFESTS:
            path = package / rel
            text = path.read_text()
            for before, after in sorted(replacements, key=lambda pair: len(pair[0]), reverse=True):
                text = text.replace(before, after)
            path.write_text(text.replace(old_version, version))
        (package / "VERSION").write_text(version + "\n")

        def git(*args):
            return subprocess.check_output(["git", *args], cwd=package, stderr=subprocess.PIPE, text=True).strip()

        remote = temp / "remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        git("init", "--initial-branch", "production-release")
        git("config", "user.name", "Release test")
        git("config", "user.email", "release-test@example.invalid")
        git("config", "commit.gpgsign", "false")
        git("config", "core.hooksPath", "/dev/null")
        git("add", ".")
        git("commit", "-m", "Production release with stale Skill metadata")
        git("remote", "add", "origin", str(remote))
        git("push", "-u", "origin", "production-release")

        shims = temp / "bin"
        shims.mkdir()
        (shims / "python3").symlink_to(sys.executable)
        gh = shims / "gh"
        gh.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$PROBE_DISPATCH_LOG"\n')
        gh.chmod(0o755)
        output, dispatch = temp / "outputs", temp / "dispatches"
        env = {**os.environ, "PATH": str(shims) + os.pathsep + os.environ["PATH"],
               "HEAD_BRANCH": "production-release", "GITHUB_OUTPUT": str(output),
               "PROBE_DISPATCH_LOG": str(dispatch)}

        def run():
            return subprocess.run(["bash", "-c", script], cwd=package, env=env, capture_output=True, text=True)

        result = run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert output.read_text() == "changed=true\n"
        assert dispatch.read_text() == "workflow run validate-plugin.yml --ref production-release\n"
        assert git("rev-list", "--count", "HEAD") == "2"
        assert git("rev-parse", "HEAD") == git("rev-parse", "origin/production-release")
        changed = git("diff", "--name-only", "HEAD^", "HEAD").splitlines()
        assert len(changed) == 12 and all(p.endswith("/SKILL.md") for p in changed), changed
        assert git("status", "--porcelain") == ""

        result = run()
        assert result.returncode == 0, result.stdout + result.stderr
        assert git("rev-list", "--count", "HEAD") == "2", "No-op must not create another commit"
        assert len(dispatch.read_text().splitlines()) == 1, "No-op must not dispatch again"

        (package / "VERSION").write_text(version + "-dev.1\n")
        result = run()
        assert result.returncode != 0 and "must not be merged into main" in result.stderr
        assert git("rev-list", "--count", "HEAD") == "2"
        assert len(dispatch.read_text().splitlines()) == 1
    print("Production PR synchronization: commit, push, validation dispatch, no-op and dev rejection passed")


if __name__ == "__main__":
    main()
