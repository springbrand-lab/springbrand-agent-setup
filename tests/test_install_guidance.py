#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
GUIDES = (
    "README.md",
    "INSTALL.md",
    "INSTALL.claude.md",
    "INSTALL.cursor.md",
    "INSTALL.workbuddy.md",
    "INSTALL.dev.md",
    "docs/adr/0001-native-host-plugin-adapters.md",
    "docs/codex-plugin-distribution-plan.md",
)


def main() -> None:
    text = "\n".join((ROOT / path).read_text() for path in GUIDES)
    for stale in (
        "blob/stable",
        "refs/heads/stable",
        "v1.1.1",
        "v1.2.0-beta.1",
        "tony/multi-host-planning-docs",
        "--ref <guide-ref>",
        "update-stable.yml",
    ):
        assert stale not in text, stale

    assert not (ROOT / ".github/workflows/update-stable.yml").exists()
    workflow = (ROOT / ".github/workflows/validate-plugin.yml").read_text()
    assert "branches: [main]" in workflow
    assert "branches: [main, stable]" not in workflow

    install = (ROOT / "INSTALL.md").read_text()
    assert "codex plugin marketplace add springbrand-lab/springbrand-agent-setup" in install
    assert "--ref" not in install
    assert "springbrand-agent-setup/main/skills/ask-springbrand/SKILL.md" in install
    assert "codex plugin marketplace upgrade springbrand" in install
    assert "`codex` has no separate `plugin update` command" in install
    assert "updates the installed Plugin in place" in install

    workbuddy = (ROOT / "INSTALL.workbuddy.md").read_text()
    assert "command -v codebuddy" in workbuddy
    assert "CODEBUDDY_CONFIG_DIR" in workbuddy
    assert "plugin marketplace add springbrand-lab/springbrand-agent-setup" in workbuddy
    assert "plugin install springbrand@springbrand --scope user" in workbuddy
    assert "plugin marketplace update springbrand" in workbuddy
    assert "plugin update springbrand@springbrand --scope user" in workbuddy
    assert "Manual UI fallback" in workbuddy
    assert "Add Marketplace" in workbuddy
    assert "springbrand-lab/springbrand-agent-setup" in workbuddy
    assert "Plugin URL" not in workbuddy
    assert f"archive/refs/tags/v{VERSION}.zip" in workbuddy

    install = (ROOT / "INSTALL.md").read_text()
    assert "bundled `codebuddy`/`cbc` CLI" in install
    assert "Do not pause for manual UI" in install
    assert "Add Marketplace" in install
    assert "springbrand-lab/springbrand-agent-setup" in install

    development = (ROOT / "INSTALL.dev.md").read_text()
    assert "Add Marketplace" in development
    assert f"archive/refs/tags/v{VERSION}.zip" in development
    assert VERSION in development
    assert "## Installation contract" in development
    assert "The fallback installs no Notice adapter" in development
    assert "/springbrand-dev:ask-springbrand" in development
    assert "$ask-springbrand" in development
    assert "springbrand.plugins.match" in development
    assert "follow-ups reuse existing state" in development
    assert "<guide-ref>" not in development

    readme = (ROOT / "README.md").read_text()
    assert f"blob/v{VERSION}/INSTALL.dev.md" in readme

    drift = re.compile(r"\d+\.\d+\.\d+-beta\.\d+-dev\.\d+")
    for path in GUIDES:
        for match in drift.findall((ROOT / path).read_text()):
            assert match == VERSION, f"{path}: stale dev version {match}, VERSION is {VERSION}"


if __name__ == "__main__":
    main()
