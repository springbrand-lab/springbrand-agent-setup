#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
    assert "springbrand-agent-setup/main/skills/springbrand/SKILL.md" in install

    workbuddy = (ROOT / "INSTALL.workbuddy.md").read_text()
    assert "Add Marketplace" in workbuddy
    assert "springbrand-lab/springbrand-agent-setup" in workbuddy
    assert "Plugin URL" not in workbuddy
    assert "archive/refs/tags/v1.2.0-beta.4-dev.1.zip" in workbuddy

    install = (ROOT / "INSTALL.md").read_text()
    assert "Add Marketplace" in install
    assert "springbrand-lab/springbrand-agent-setup" in install
    assert "Plugin URL flow for production" in install

    development = (ROOT / "INSTALL.dev.md").read_text()
    assert "Add Marketplace" in development
    assert "archive/refs/tags/v1.2.0-beta.4-dev.1.zip" in development
    assert "v1.2.0-beta.4-dev.1" in development
    assert "<guide-ref>" not in development


if __name__ == "__main__":
    main()
