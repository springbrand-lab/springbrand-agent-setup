#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
GUIDES = (
    "README.md",
    "INSTALL.md",
    "INSTALL.claude.md",
    "INSTALL.cli.cursor.md",
    "INSTALL.workbuddy.md",
    "INSTALL.cli.workbuddy.md",
    "INSTALL.dev.md",
    "INSTALL.cli.codex.md",
    "INSTALL.cli.claude-code.md",
    "INSTALL.cli.opencode.md",
    "INSTALL.cli.dev.codex.md",
    "INSTALL.cli.dev.claude-code.md",
    "INSTALL.cli.dev.cursor.md",
    "INSTALL.cli.dev.opencode.md",
    "INSTALL.cli.dev.workbuddy.md",
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
    plugin = (ROOT / "INSTALL.plugin.md").read_text()
    assert "npx -y @springbrand/cli@latest connect --all" in install
    assert "no API key" in install
    assert "native browser OAuth" in install
    assert "ask which terminal/client" in install
    assert "run this command first" in install
    assert "auth login --url https://connector.springbrand.ai/mcp" in install
    assert "OAuth as an explicit fallback" in install
    assert "account-settings?section=mcp-api-keys" in install
    assert "INSTALL.cli.codex.md" in install
    assert "single-client guide" in install
    assert "Plugin fallback" in install
    assert "INSTALL.plugin.md" in install
    assert "INSTALL.cli.codex.md" in plugin
    assert "Host-native OAuth" in plugin
    assert "https://connector.springbrand.ai/mcp" in plugin

    # Plugin Host-guide entry points load the Plugin-only welcome contract.
    for name, target in (
        ("INSTALL.claude.md", "INSTALL.plugin.md"),
        ("INSTALL.cursor.md", "INSTALL.plugin.md"),
        ("INSTALL.workbuddy.md", "INSTALL.plugin.md"),
    ):
        guide = (ROOT / name).read_text()
        assert f"[Initial installation response](./{target}#initial-installation-response)" in guide, name

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
    assert "channels/production/workbuddy.zip" not in workbuddy
    assert "plugin install springbrand@springbrand --scope user" in workbuddy
    assert "plugin marketplace update springbrand" in workbuddy
    assert "plugin update springbrand@springbrand --scope user" in workbuddy
    assert "Manual UI fallback" in workbuddy
    assert "Add Marketplace" in workbuddy

    assert "Plugin URL" not in workbuddy

    development = (ROOT / "INSTALL.dev.md").read_text()
    dev_plugin = (ROOT / "INSTALL.plugin.dev.md").read_text()
    assert "v1.2.1-dev.2" in development
    assert "https://devconnector.springbrand.ai/mcp" in development
    assert "npx -y @springbrand/cli@alpha connect --all" in development
    assert "no API key" in development
    assert "native browser OAuth" in development
    assert "ask which terminal/client" in development
    assert "run this command first" in development
    assert "auth login --url https://devconnector.springbrand.ai/mcp" in development
    assert "OAuth as an explicit fallback" in development
    assert "INSTALL.cli.dev.codex.md" in development
    assert "single-client development guide" in development
    assert "INSTALL.plugin.dev.md" in development
    assert "springbrand-dev" in dev_plugin
    assert "Host-native OAuth" in dev_plugin
    assert "https://devconnector.springbrand.ai/mcp" in dev_plugin
    assert "Do not launch OAuth" not in development
    development_flat = " ".join(development.split())
    for secret_phrase in (
        "Authorization: Bearer", "Authorization header:", "access_token=",
        "refresh_token=", "api_key=", "raw upstream body",
    ):
        assert secret_phrase not in development_flat, secret_phrase

    # Welcome is Plugin-only; CLI entry points must stay focused on the CLI summary.
    for guide in (install, development):
        assert "## Initial installation response" not in guide
        assert "### Welcome message" not in guide
        assert "Try a task with free credits" not in guide
    for guide in (plugin, dev_plugin):
        assert guide.count("## Initial installation response\n") == 1
        assert guide.count("### Welcome message\n") == 1
        assert "Try a task with free credits—copy a prompt below." in guide
        assert "Close the report with a one-sentence capability note" in guide

    readme = (ROOT / "README.md").read_text()
    assert "https://plugin.springbrand.ai/INSTALL.dev.md" in readme
    assert "| Authentication | Runtime API key preferred; host-native OAuth fallback | Runtime API key preferred; host-native OAuth fallback |" in readme
    assert "Do not launch OAuth when the API key is valid" in readme

    for environment, endpoint, tag in (("production", "https://connector.springbrand.ai/mcp", "latest"), ("development", "https://devconnector.springbrand.ai/mcp", "alpha")):
        prefix = "INSTALL.cli.dev." if environment == "development" else "INSTALL.cli."
        for client, client_id in (("codex", "codex"), ("claude-code", "claude-code"), ("cursor", "cursor"), ("opencode", "opencode"), ("workbuddy", "workbuddy-ai")):
            path = f"{prefix}{client}.md"
            if environment == "production" and client in {"cursor", "workbuddy"}:
                path = f"INSTALL.cli.{client}.md"
            if environment == "development":
                path = f"INSTALL.cli.dev.{client}.md"
            guide = (ROOT / path).read_text()
            assert f"connect {client_id} --url {endpoint} --api-key {{{{INSTALL_KEY}}}}" in guide
            assert f"@springbrand/cli@{tag}" in guide
            title = "OpenCode" if client == "opencode" else ("WorkBuddy" if client == "workbuddy" else client.replace('-', ' ').title())
            assert f"configures **{title} only**" in guide
            assert "Do not detect, configure, update, or remove any other client" in guide
            assert "OAuth flow" in guide
            assert "Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub." in guide
            assert "Then ask the user what they would like to build first." in guide
            if environment == "development":
                assert "v1.2.1-dev.2" in guide
                assert "https://connector.springbrand.ai/mcp" not in guide
            else:
                assert "devconnector.springbrand.ai" not in guide

    assert "archive/refs/tags/" not in workbuddy

    drift = re.compile(r"\d+\.\d+\.\d+-beta\.\d+-dev\.\d+")
    for path in GUIDES:
        for match in drift.findall((ROOT / path).read_text()):
            assert match == DEV_VERSION, f"{path}: dev version {match} drifts from the dev guide ref {DEV_VERSION}"


if __name__ == "__main__":
    main()
