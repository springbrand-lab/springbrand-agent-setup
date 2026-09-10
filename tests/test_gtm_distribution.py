#!/usr/bin/env python3
"""Verify GTM reaches each native adapter and the manual dev installation path."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from validate_plugin import CANONICAL_SKILLS, validate_package, validate_skill_mirrors

ROOT = Path(__file__).resolve().parents[1]


def main():
    assert len(CANONICAL_SKILLS) == 5
    assert "springbrand-gtm" in CANONICAL_SKILLS
    validate_package(ROOT)
    source = ROOT / "skills/springbrand-gtm/SKILL.md"
    frontmatter = source.read_text().split("\n---\n", 1)[0]
    assert "disable-model-invocation: true" not in frontmatter
    assert "user-invocable: false" not in frontmatter
    assert 'allow_implicit_invocation: false' not in frontmatter
    assert len(frontmatter.split("description:", 1)[1].split("metadata:", 1)[0].strip()) > 0

    for namespace, extra in (("$springbrand-gtm", {}), ("/springbrand-dev:springbrand-gtm" if "-dev." in (ROOT / "VERSION").read_text() else "/springbrand:springbrand-gtm", {"CLAUDE_PLUGIN_ROOT": "/tmp/plugin"})):
        env = {**os.environ, "CLAUDE_PLUGIN_ROOT": "", **extra}
        notices = []
        for prompt in ("帮我的产品做竞品分析", "GTM 是什么意思？", "fix a parser"):
            result = subprocess.run([ROOT / "hooks/user-prompt-submit"], input=json.dumps({"prompt": prompt}), env=env, capture_output=True, text=True, check=True, timeout=1)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            assert namespace in context
            notices.append(context)
        assert len(set(notices)) == 1, "The hook must not classify prompt content"

    guide = (ROOT / "INSTALL.dev.md").read_text()
    assert "GitHub capabilities only" not in guide
    assert "immutable older tag or ZIP does not select this release" in guide
    assert "/skills/springbrand-gtm/SKILL.md" in guide
    assert "<your user-level Skill directory>/springbrand-gtm/SKILL.md" in guide
    for adapter in ("plugins/springbrand", "plugins/springbrand-workbuddy"):
        assert (ROOT / adapter / "skills/springbrand-gtm/SKILL.md").read_bytes() == source.read_bytes()
    with tempfile.TemporaryDirectory() as temp:
        package = Path(temp) / "package"
        shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns(".git", "__pycache__", ".secrets", ".DS_Store"))
        (package / "plugins/springbrand/skills/springbrand-gtm/SKILL.md").unlink()
        try:
            validate_skill_mirrors(package, package / "plugins/springbrand", "Cursor")
        except AssertionError as error:
            assert "springbrand-gtm" in str(error)
        else:
            raise AssertionError("Missing GTM adapter mirror passed validation")
    print("GTM distribution: five Skills, implicit entry, static host notices and missing-mirror rejection passed")


if __name__ == "__main__":
    main()
