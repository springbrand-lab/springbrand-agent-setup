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
        "tony/multi-host-planning-docs",
        "--ref <guide-ref>",
        "update-stable.yml",
    ):
        assert stale not in text, stale

    assert not re.search(r"v1\.2\.0-beta\.1(?![0-9])", text)

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
    assert "whether this is a first installation or an\nupdate" in install
    assert "Returning from a Host guide does not show Welcome a second time" in install

    # Direct Host-guide entry points must reach the shared welcome contract too.
    for name, install_heading in (
        ("INSTALL.claude.md", "## Install and authenticate"),
        ("INSTALL.cursor.md", "## Install and authenticate"),
        ("INSTALL.workbuddy.md", "## 2. First install"),
    ):
        guide = (ROOT / name).read_text()
        classification = "Determine first installation versus ordinary update"
        assert classification in guide, name
        assert guide.index(classification) < guide.index(install_heading), name
        welcome_link = "[Initial installation response](./INSTALL.md#initial-installation-response)"
        assert welcome_link in guide, name
        # Load the shared rule before even a validation command can return early.
        assert guide.index(welcome_link) < guide.index("\n## "), name
        if "```" in guide:
            assert guide.index(welcome_link) < guide.index("```"), name
        assert "actual setup status and the next step" in guide, name
        assert "failure/blockers and existing" in guide, name
        assert "Skip ordinary\nupdates and later repeats" in guide, name
        assert "Try a task with free credits" not in guide, name
        assert "After installation verification succeeds" not in guide, name
        assert "#after-installation" not in guide, name

    workbuddy = (ROOT / "INSTALL.workbuddy.md").read_text()
    assert "command -v codebuddy" in workbuddy
    assert "CODEBUDDY_CONFIG_DIR" in workbuddy
    assert 'plugin marketplace add "$WORKBUDDY_SOURCE"' in workbuddy
    assert "plugin marketplace add springbrand-lab/springbrand-agent-setup" not in workbuddy
    assert "raw.githubusercontent.com" not in workbuddy
    assert "Contents/Resources/app.asar.unpacked/cli/bin/codebuddy" in workbuddy
    assert "not follow future releases automatically" in workbuddy
    assert "Do not run a redundant" in workbuddy
    assert "Hook execution is not an installation acceptance gate" in " ".join(workbuddy.split())
    source = re.search(r'WORKBUDDY_SOURCE="(https://plugin\.springbrand\.ai/releases/[^" ]+/workbuddy/springbrand-workbuddy\.zip)"', workbuddy)
    assert source, "WorkBuddy must name an immutable R2 release source"
    assert source.group(1) in install
    assert "channels/production/workbuddy.zip" not in workbuddy
    assert install.index("## Identify the Agent") < install.index("## Preflight")
    assert "WorkBuddy: skip the GitHub Skill URL checks" in install
    section = install.split("## WorkBuddy Desktop", 1)[1].split("## Other Agents", 1)[0]
    assert "springbrand-lab/springbrand-agent-setup" not in section
    assert "repository `main`" not in section
    assert "plugin install springbrand@springbrand --scope user" in workbuddy
    assert "plugin marketplace update springbrand" in workbuddy
    assert "plugin update springbrand@springbrand --scope user" in workbuddy
    assert "Manual UI fallback" in workbuddy
    assert "Add Marketplace" in workbuddy

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
    assert "Keep that classification for final reporting" in development
    initial_heading = "## Initial installation response\n"
    overview_heading = "## Installation overview\n"
    initial_sections = []
    for guide in (install, development):
        assert guide.count(initial_heading) == 1
        assert guide.count("### Welcome message\n") == 1
        assert guide.index(initial_heading) < guide.index(overview_heading)
        assert guide.index(initial_heading) < guide.index("## Preflight")
        assert guide.index(initial_heading) < guide.index("```"), "Preflight can block before Welcome is loaded"
        initial_sections.append(guide.split(initial_heading, 1)[1].split(overview_heading, 1)[0])
        for retired in ("## After installation", "#after-installation", "first successful installation", "before installation\nverification succeeds", "briefly confirm setup and continue that task instead"):
            assert retired not in guide, retired
    assert initial_sections[0] == initial_sections[1], "Production/dev initial-response contract drift"
    initial = " ".join(initial_sections[0].split())
    # Cover each first-handoff outcome and the once/update constraints without
    # pretending document checks prove a model's native runtime behavior.
    for expected in (
        "first installation wrap-up or request for user action",
        "regardless of setup status or an existing task",
        "Do not wait for verification or a new conversation",
        "Skip ordinary updates",
        "Do not repeat it in later replies of the same installation conversation",
        "setup complete",
        "waiting for OAuth",
        "required restart or new session",
        "installation failure or a blocker",
        "State the actual setup status and next step first",
        "does not mean that installation succeeded",
        "If setup is incomplete, replace the prompt introduction",
        "Once setup is complete, try a task with free credits—copy a prompt below.",
        "already has a task underway, still show the Welcome message once",
        "Do not check the website or a balance API",
        "do not promise an amount, quantity, or validity period",
        "Research your market", "Find customer signals", "Find creators", "Create campaign assets",
    ):
        assert expected in initial, expected
    template = initial_sections[0].split("### Welcome message\n", 1)[1]
    assert template.count("Try a task with free credits—copy a prompt below.") == 1
    assert template.count('“Use SpringBrand') == 4
    for retired in ("$10", "New Free accounts start", "Copy a prompt to get started:"):
        assert retired not in template, retired

    readme = (ROOT / "README.md").read_text()
    assert f"blob/v{DEV_VERSION}/INSTALL.dev.md" in readme

    assert "archive/refs/tags/" not in workbuddy
    assert "## WorkBuddy development CLI installation" in development

    drift = re.compile(r"\d+\.\d+\.\d+-beta\.\d+-dev\.\d+")
    for path in GUIDES:
        for match in drift.findall((ROOT / path).read_text()):
            assert match == DEV_VERSION, f"{path}: dev version {match} drifts from the dev guide ref {DEV_VERSION}"


if __name__ == "__main__":
    main()
