#!/usr/bin/env python3
"""Check that package contract failures identify the broken artifact."""

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_plugin", ROOT / "tests/validate_plugin.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def copy_package(destination: Path) -> None:
    for name in (
        "VERSION",
        ".claude-plugin",
        ".codex-plugin",
        ".agents",
        ".cursor-plugin",
        ".codebuddy-plugin",
        ".mcp.json",
        "assets",
        "hooks",
        "INSTALL.workbuddy.md",
        "plugins",
        "rules",
        "skills",
    ):
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def expect_failure(change, message: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        package = Path(directory)
        copy_package(package)
        change(package)
        try:
            VALIDATOR.validate_package(package)
        except AssertionError as exc:
            assert message in str(exc), exc
        else:
            raise AssertionError(f"expected validation failure containing: {message}")


def edit_json(path: Path, edit) -> None:
    value = json.loads(path.read_text())
    edit(value)
    path.write_text(json.dumps(value))


def _add_legacy_skill(root: Path) -> None:
    legacy = root / "skills/springbrand-plugin-discovery"
    legacy.mkdir()
    (legacy / "SKILL.md").write_text("---\nname: springbrand-plugin-discovery\n---\n")


def main() -> None:
    expect_failure(
        lambda root: (root / "VERSION").write_text("01.2.3\n"),
        "invalid repository version",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".mcp.json",
            lambda value: value["mcpServers"]["springbrand-dev-platform"].update(url="https://example.com/mcp"),
        ),
        "must register exactly the three development MCP Domain Entries",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".mcp.json",
            lambda value: value["mcpServers"].update({"springbrand": {"url": "https://connector.springbrand.ai/mcp"}}),
        ),
        "must register exactly the three development MCP Domain Entries",
    )
    expect_failure(
        lambda root: _add_legacy_skill(root),
        "Canonical Skill Set must be exactly the named four-Skill list",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".codex-plugin/plugin.json",
            lambda value: value.update(skills="./missing-skills/"),
        ),
        "Codex skills component must reference ./skills/",
    )
    expect_failure(
        lambda root: (root / ".env").write_text("SPRINGBRAND_TOKEN=secret\n"),
        "forbidden credential file",
    )
    expect_failure(
        lambda root: [
            (root / path).write_text("#!/bin/sh\ncurl https://example.com\n")
            for path in ("hooks/user-prompt-submit", "plugins/springbrand-workbuddy/hooks/user-prompt-submit")
        ],
        "Canonical Hook must remain a static, network-free routing command",
    )
    expect_failure(
        lambda root: [
            (root / path).write_text(
                (root / "hooks/user-prompt-submit").read_text().replace(
                    "authorize side effects", "authorize side effects. Do not Match again"
                )
            )
            for path in ("hooks/user-prompt-submit", "plugins/springbrand-workbuddy/hooks/user-prompt-submit")
        ],
        "Routing Notice must not use retired phrasing: Do not Match again",
    )
    expect_failure(
        lambda root: (root / "hooks/user-prompt-submit").chmod(0o644),
        "Codex Hook is not executable",
    )
    expect_failure(
        lambda root: shutil.copy2(root / "hooks/codex-hooks.json", root / "hooks/hooks.json"),
        "Claude Adapter must not auto-discover the Codex Hook config",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".claude-plugin/plugin.json",
            lambda value: value["mcpServers"]["springbrand-dev-platform"].update(url="https://example.com/mcp"),
        ),
        "Claude MCP server must register exactly the three development MCP Domain Entries",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".claude-plugin/plugin.json",
            lambda value: value["mcpServers"]["springbrand-dev-platform"].update(headers={"Authorization": "Bearer token"}),
        ),
        "Claude MCP server must register exactly the three development MCP Domain Entries",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".cursor-plugin/marketplace.json",
            lambda value: value["plugins"][0].update(source="./"),
        ),
        "Cursor Marketplace source must reference ./plugins/springbrand",
    )
    expect_failure(
        lambda root: (root / "plugins/springbrand/skills/springbrand-platform/SKILL.md").write_text("drift\n"),
        "Cursor Skill mirror for springbrand-platform must be byte-equivalent",
    )
    expect_failure(
        lambda root: (root / "plugins/springbrand/rules/springbrand-preflight.mdc").write_text(
            "---\ndescription: broken\nalwaysApply: false\n---\n"
            "Before planning or production, follow springbrand-plugin-discovery.\n"
            "Delegate eligibility and Marketplace behavior.\nalwaysApply: true\n"
        ),
        "Cursor Rule must always apply",
    )
    expect_failure(
        lambda root: (root / "plugins/springbrand/rules/springbrand-preflight.mdc").write_text(
            (root / "rules/springbrand-preflight.mdc").read_text().replace("ask-springbrand", "ask-springbrand-drift")
        ),
        "Cursor Rule mirror must be byte-equivalent",
    )
    expect_failure(
        lambda root: edit_json(
            root / "plugins/springbrand/mcp.json",
            lambda value: value["mcpServers"]["springbrand-dev-platform"].update(token="secret"),
        ),
        "Cursor MCP endpoint must register exactly the three development MCP Domain Entries",
    )
    expect_failure(
        lambda root: (root / "plugins/springbrand/hooks").mkdir(),
        "Cursor Adapter must not ship Hooks",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".codebuddy-plugin/marketplace.json",
            lambda value: value["plugins"][0].update(source="./"),
        ),
        "WorkBuddy Marketplace source must reference ./plugins/springbrand-workbuddy",
    )
    expect_failure(
        lambda root: (root / "plugins/springbrand-workbuddy/skills/ask-springbrand/SKILL.md").write_text("drift\n"),
        "WorkBuddy Skill mirror for ask-springbrand must be byte-equivalent",
    )
    expect_failure(
        lambda root: (root / "plugins/springbrand-workbuddy/hooks/user-prompt-submit").write_text("drift\n"),
        "WorkBuddy Hook mirror must be byte-equivalent",
    )
    expect_failure(
        lambda root: edit_json(
            root / "plugins/springbrand-workbuddy/.mcp.json",
            lambda value: value["mcpServers"]["springbrand-dev-connector"].update(token="secret"),
        ),
        "WorkBuddy MCP server must register exactly the three development MCP Domain Entries",
    )


if __name__ == "__main__":
    main()
