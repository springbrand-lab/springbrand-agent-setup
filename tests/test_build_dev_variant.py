#!/usr/bin/env python3
"""Check that the dev variant build rewrites the package deterministically."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIED = (
    "VERSION",
    ".agents",
    ".claude-plugin",
    ".codebuddy-plugin",
    ".codex-plugin",
    ".cursor-plugin",
    ".github",
    ".mcp.json",
    "hooks",
    "plugins",
    "scripts",
)
DEV_VERSION = "1.2.0-beta.7-dev.1"
DEV_URL = "https://devconnector.springbrand.ai/mcp"
DEV_ENTRY = "springbrand-dev"
DEV_DESCRIPTION = "Discover and use SpringBrand Plugins through the development connector. Internal testing only."


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        package = Path(directory)
        for name in COPIED:
            source = ROOT / name
            target = package / name
            shutil.copytree(source, target) if source.is_dir() else shutil.copy2(source, target)

        command = ["python3", "scripts/build_dev_variant.py", "--version", DEV_VERSION]
        subprocess.run(command, cwd=package, check=True)
        snapshot = {path: path.read_bytes() for path in sorted(package.rglob("*")) if path.is_file()}
        subprocess.run(command, cwd=package, check=True)
        assert snapshot == {path: path.read_bytes() for path in package.rglob("*") if path.is_file()}

        assert (package / "VERSION").read_text() == DEV_VERSION + "\n"

        for name in (".mcp.json", "plugins/springbrand/mcp.json"):
            servers = json.loads((package / name).read_text())["mcpServers"]
            assert servers == {DEV_ENTRY: {"url": DEV_URL}}, servers

        for name in (".claude-plugin/plugin.json", "plugins/springbrand-workbuddy/.mcp.json"):
            servers = json.loads((package / name).read_text())["mcpServers"]
            assert servers == {DEV_ENTRY: {"type": "http", "url": DEV_URL}}, servers

        for name in (
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            "plugins/springbrand/.cursor-plugin/plugin.json",
            "plugins/springbrand-workbuddy/.workbuddy-plugin/plugin.json",
        ):
            manifest = json.loads((package / name).read_text())
            assert manifest["name"] == "springbrand-dev", manifest
            assert manifest["version"] == DEV_VERSION, manifest
            assert manifest["description"] == (
                "Discover and use SpringBrand Plugins through the development connector. Internal testing only."
            ), manifest

        cursor_marketplace = json.loads((package / ".cursor-plugin/marketplace.json").read_text())
        assert cursor_marketplace["metadata"]["version"] == DEV_VERSION, cursor_marketplace
        assert cursor_marketplace["plugins"][0]["version"] == DEV_VERSION, cursor_marketplace

        codex = json.loads((package / ".codex-plugin/plugin.json").read_text())["interface"]
        assert codex["displayName"] == "SpringBrand Dev", codex
        assert codex["defaultPrompt"] == ["Find a SpringBrand Plugin using the development environment."], codex

        cursor = json.loads((package / "plugins/springbrand/.cursor-plugin/plugin.json").read_text())
        assert cursor["displayName"] == "SpringBrand Dev", cursor
        assert "dev" in cursor["keywords"], cursor

        for name in (
            ".agents/plugins/marketplace.json",
            ".claude-plugin/marketplace.json",
            ".codebuddy-plugin/marketplace.json",
            ".cursor-plugin/marketplace.json",
        ):
            marketplace = json.loads((package / name).read_text())
            assert marketplace["name"] == "springbrand-dev", marketplace
            assert all(plugin["name"] == "springbrand-dev" for plugin in marketplace["plugins"]), marketplace

        for name in ("hooks/user-prompt-submit", "plugins/springbrand-workbuddy/hooks/user-prompt-submit"):
            hook_path = package / name
            hook = hook_path.read_text()
            assert "`/springbrand-dev:ask-springbrand`" in hook, name
            assert "`/springbrand:" not in hook, name
            assert "`$ask-springbrand` Skill" in hook, name
            assert hook_path.stat().st_mode & 0o111, name
        assert (package / "hooks/user-prompt-submit").read_bytes() == (
            package / "plugins/springbrand-workbuddy/hooks/user-prompt-submit"
        ).read_bytes()

        workflow = (package / ".github/workflows/validate-plugin.yml").read_text()
        assert "codex plugin add springbrand-dev --marketplace springbrand-dev" in workflow
        assert '== "springbrand",' not in workflow


if __name__ == "__main__":
    main()
