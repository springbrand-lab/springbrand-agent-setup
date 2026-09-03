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

    development = (ROOT / "INSTALL.dev.md").read_text()
    dev_ref = re.search(r"\| Git ref \| `v([^`]+)` \|", development)
    assert dev_ref, "INSTALL.dev.md must declare its Git ref"
    DEV_VERSION = dev_ref.group(1)
    assert "-dev." in DEV_VERSION, f"dev guide must reference an immutable dev tag, found {DEV_VERSION}"
    assert "Add Marketplace" in development
    assert f"archive/refs/tags/v{DEV_VERSION}.zip" in development
    assert DEV_VERSION in development
    assert "## Installation contract" in development
    assert "The fallback installs no Notice adapter" in development
    assert "/springbrand-dev:ask-springbrand" in development
    assert "$ask-springbrand" in development
    assert "springbrand.plugins.match" in development
    assert "follow-ups reuse existing state" in development
    assert "<guide-ref>" not in development

    readme = (ROOT / "README.md").read_text()
    assert f"blob/v{DEV_VERSION}/INSTALL.dev.md" in readme

    assert f"archive/refs/tags/v{DEV_VERSION}.zip" in workbuddy

    drift = re.compile(r"\d+\.\d+\.\d+-beta\.\d+-dev\.\d+")
    for path in GUIDES:
        for match in drift.findall((ROOT / path).read_text()):
            assert match == DEV_VERSION, f"{path}: dev version {match} drifts from the dev guide ref {DEV_VERSION}"


if __name__ == "__main__":
    main()
