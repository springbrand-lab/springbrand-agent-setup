#!/usr/bin/env python3
"""Guard: packaging manifests on main must carry the production identity.

The dev variant rewrite (scripts/build_dev_variant.py) changes manifests in
place. If a dev-rewritten file is ever merged back into the production
channel, installs from main would silently target the development MCP
environment. This test fails fast when that happens.

See AGENTS.md ("Release identity: dev vs production").
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_DEV = "-dev." in (ROOT / "VERSION").read_text()

PROD_MCP_ENTRY = "springbrand"
PROD_MCP_URL = "https://connector.springbrand.ai/mcp"
DEV_MARKERS = ("springbrand-dev", "devconnector.springbrand.ai", "SpringBrand Dev")

# Every packaging manifest that ships to users from the production channel.
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
        expected = "https://devconnector.springbrand.ai/mcp" if IS_DEV else PROD_MCP_URL
        wrong = PROD_MCP_URL if IS_DEV else "https://devconnector.springbrand.ai/mcp"
        text = (ROOT / rel).read_text()
        if expected not in text or wrong in text:
            failures.append(f"{rel}: MCP manifest does not exclusively point at {expected}")
    if IS_DEV:
        for rel in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".codebuddy-plugin/marketplace.json"):
            if '"springbrand-dev"' not in (ROOT / rel).read_text():
                failures.append(f"{rel}: missing dev identity")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        raise SystemExit(
            "production channel carries development identity; "
            "see AGENTS.md 'Release identity: dev vs production'"
        )
    print("release identity: ok")


if __name__ == "__main__":
    main()
