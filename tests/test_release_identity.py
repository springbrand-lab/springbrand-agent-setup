#!/usr/bin/env python3
"""Guard: packaging manifests must match the identity their VERSION implies.

Per AGENTS.md ("Release identity: dev vs production"), the VERSION dev
marker decides the environment: `-dev.N` versions carry the development
identity (springbrand-dev / devconnector.springbrand.ai); all other versions
carry the production identity (springbrand / connector.springbrand.ai).
This fails fast when a dev-rewritten file reaches the production channel, or
when a release branch forgot the dev rewrite.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text().strip()
IS_DEV = "-dev." in VERSION

PROD_MCP_URL = "https://connector.springbrand.ai/mcp"
DEV_MCP_URL = "https://devconnector.springbrand.ai/mcp"
DEV_MARKERS = ("springbrand-dev", "devconnector.springbrand.ai", "SpringBrand Dev")

# Every packaging manifest that ships to users.
PACKAGING_MANIFESTS = (
    ".mcp.json",
    "plugins/springbrand/mcp.json",
    "plugins/springbrand-workbuddy/.mcp.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/marketplace.json",
    "plugins/springbrand/.cursor-plugin/plugin.json",
    ".codebuddy-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
    "plugins/springbrand-workbuddy/.workbuddy-plugin/plugin.json",
    "hooks/user-prompt-submit",
    "plugins/springbrand-workbuddy/hooks/user-prompt-submit",
    ".github/workflows/validate-plugin.yml",
)

# Manifests that embed the MCP URL inline (others reference ./.mcp.json by path).
INLINE_MCP_MANIFESTS = (
    ".mcp.json",
    "plugins/springbrand/mcp.json",
    "plugins/springbrand-workbuddy/.mcp.json",
    ".claude-plugin/plugin.json",
)


def main() -> None:
    failures = []
    for rel in PACKAGING_MANIFESTS:
        text = (ROOT / rel).read_text()
        if IS_DEV:
            continue
        for marker in DEV_MARKERS:
            if marker in text:
                failures.append(f"{rel}: contains dev identity marker {marker!r}")
    for rel in INLINE_MCP_MANIFESTS:
        text = (ROOT / rel).read_text()
        expected_url = DEV_MCP_URL if IS_DEV else PROD_MCP_URL
        if expected_url not in text:
            failures.append(f"{rel}: MCP manifest does not point at {expected_url}")
        wrong_url = PROD_MCP_URL if IS_DEV else DEV_MCP_URL
        if wrong_url in text:
            failures.append(f"{rel}: MCP manifest points at the wrong environment ({wrong_url})")

    if not IS_DEV:
        # Production channel must name the production Plugin everywhere.
        for rel in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".codebuddy-plugin/marketplace.json"):
            text = (ROOT / rel).read_text()
            if '"springbrand-dev"' in text or "SpringBrand Dev" in text:
                failures.append(f"{rel}: production marketplace carries dev identity")
    else:
        # Dev branch: the dev rewrite must actually have been applied.
        for rel in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".codebuddy-plugin/marketplace.json"):
            text = (ROOT / rel).read_text()
            if '"springbrand-dev"' not in text:
                failures.append(f"{rel}: dev branch is missing the dev identity rewrite")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        raise SystemExit(
            "release identity mismatch; see AGENTS.md 'Release identity: dev vs production'"
        )
    print(f"release identity: ok ({'development' if IS_DEV else 'production'})")


if __name__ == "__main__":
    main()
