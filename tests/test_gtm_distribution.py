#!/usr/bin/env python3
"""Verify GTM reaches each native adapter and the manual dev installation path."""
from pathlib import Path
import shutil
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

    guide = (ROOT / "INSTALL.dev.md").read_text()
    plugin_guide = (ROOT / "INSTALL.plugin.dev.md").read_text()
    assert "GitHub capabilities only" not in guide
    assert "v1.2.1-dev.2" in guide
    assert "## Other Agent workflow" in guide
    assert "INSTALL.plugin.dev.md" not in guide
    assert "immutable release" in plugin_guide
    assert "springbrand-dev" in plugin_guide
    assert "https://devconnector.springbrand.ai/mcp" in plugin_guide
    assert "### Welcome message" in plugin_guide
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
    print("GTM distribution: five Skills, implicit entry and missing-mirror rejection passed")


if __name__ == "__main__":
    main()
