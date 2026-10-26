#!/usr/bin/env python3
"""Validate the shipped package contract without third-party dependencies."""

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_MCP_URL = "https://connector.springbrand.ai/mcp"
DEVELOPMENT_MCP_URL = "https://devconnector.springbrand.ai/mcp"
CANONICAL_SKILLS = (
    "ask-springbrand",
    "springbrand-platform",
    "springbrand-action-api",
    "springbrand-connector",
    "springbrand-gtm",
)


def identity_for(version: str) -> dict:
    """Resolve the expected release identity from the VERSION dev marker.

    See AGENTS.md ("Release identity: dev vs production"): tags with a
    `-dev.N` marker carry the development identity; all other tags carry the
    production identity.
    """
    if "-dev." in version:
        return {
            "entry": "springbrand-dev",
            "url": DEVELOPMENT_MCP_URL,
            "claude_description": "Discover and use SpringBrand Plugins through the development connector. Internal testing only.",
            "claude_marketplace_description": "SpringBrand development Plugin for internal Plugin testing.",
        }
    return {
        "entry": "springbrand",
        "url": PRODUCTION_MCP_URL,
        "claude_description": "Discover and use SpringBrand Plugins through the production connector.",
        "claude_marketplace_description": "SpringBrand plugins for discovering and using reusable Plugins.",
    }
VERSION_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)

def require(condition, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"invalid JSON: {path}: {exc}") from exc


def component(root: Path, reference: str, label: str) -> Path:
    require(isinstance(reference, str) and reference.startswith("./"), f"{label} must use a ./ relative path")
    path = (root / reference).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise AssertionError(f"{label} escapes the package root: {reference}") from exc
    require(path.exists(), f"{label} does not exist: {reference}")
    return path


def validate_mcp_entries(servers, label: str, entry_type: None | str, entry: str, url: str) -> None:
    expected = {
        entry: ({"type": entry_type, "url": url} if entry_type else {"url": url})
    }
    require(servers == expected, f"{label} must register exactly one MCP entry ({entry}) at {url} — a single URL and a single OAuth client — with no credentials, extra fields, or extra entries (legacy three-entry manifests are rejected)")


def validate_canonical_package(root: Path) -> str:
    try:
        version = (root / "VERSION").read_text().strip()
    except OSError as exc:
        raise AssertionError(f"cannot read repository VERSION: {exc}") from exc
    require(VERSION_PATTERN.fullmatch(version), f"invalid repository version: {version!r}")

    mcp = read_json(root / ".mcp.json")
    identity = identity_for(version)
    validate_mcp_entries(mcp.get("mcpServers"), "root MCP manifest", entry_type=None, entry=identity["entry"], url=identity["url"])

    skill_names = sorted(path.parent.name for path in (root / "skills").glob("*/SKILL.md"))
    require(
        skill_names == sorted(CANONICAL_SKILLS),
        f"Canonical Skill Set must be exactly the named Skill list {sorted(CANONICAL_SKILLS)}, found {skill_names}",
    )
    for name in CANONICAL_SKILLS:
        frontmatter = (root / f"skills/{name}/SKILL.md").read_text().split("\n---\n", 1)[0]
        require(
            re.search(rf"^name:\s*{re.escape(name)}\s*$", frontmatter, re.MULTILINE),
            f"Canonical Skill {name} frontmatter name must match its directory",
        )
        metadata = re.search(r"^metadata:\n((?:[ \t]+[^\n]*\n?|\n)*)", frontmatter, re.MULTILINE)
        versions = re.findall(r'^  version: "([^"\n]+)"$', metadata.group(1), re.MULTILINE) if metadata else []
        require(versions == [version], f"Canonical Skill {name} metadata.version must match VERSION ({version})")

    require(not (root / "hooks").exists(), "Routing Hooks must not ship")
    require(not (root / "rules").exists(), "Routing Rules must not ship")
    return version


def validate_codex_adapter(root: Path, version: str, identity: dict) -> None:
    entry = identity["entry"]
    plugin = read_json(root / ".codex-plugin/plugin.json")
    require(plugin.get("name") == entry, f"Codex manifest name must be {entry}")
    require(plugin.get("version") == version, f"Codex manifest version must match VERSION ({version})")
    require(plugin.get("repository") == "https://github.com/springbrand-lab/springbrand-agent-setup", "Codex repository URL is invalid")
    require(plugin.get("skills") == "./skills/", "Codex skills component must reference ./skills/")
    require(component(root, plugin["skills"], "Codex skills component").is_dir(), "Codex skills component must be a directory")
    require(plugin.get("mcpServers") == "./.mcp.json", "Codex MCP component must reference ./.mcp.json")
    require(component(root, plugin["mcpServers"], "Codex MCP component").is_file(), "Codex MCP component must be a file")
    require("hooks" not in plugin, "Codex manifest must not declare Hooks")

    interface = plugin.get("interface", {})
    require(interface.get("brandColor") == "#FF8A2C", "Codex brandColor must be #FF8A2C")
    for field in ("composerIcon", "logo", "logoDark"):
        reference = interface.get(field)
        require(reference == "./assets/springbrand-icon.svg", f"Codex {field} must reference ./assets/springbrand-icon.svg")
        require(component(root, reference, f"Codex {field}").is_file(), f"Codex {field} must be a file")

    marketplace = read_json(root / ".agents/plugins/marketplace.json")
    require(marketplace.get("name") == entry, f"Codex Marketplace name must be {entry}")
    entries = [entry_ for entry_ in marketplace.get("plugins", []) if entry_.get("name") == entry]
    require(len(entries) == 1, f"Codex Marketplace must contain exactly one {entry} entry")
    entry = entries[0]
    require(entry.get("source") == {"source": "local", "path": "./"}, "Codex Marketplace source must reference the package root")
    require(component(root, entry["source"]["path"], "Codex Marketplace source").is_dir(), "Codex Marketplace source must be a directory")
    require(entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "Codex Marketplace policy is invalid")


def validate_claude_adapter(root: Path, version: str, identity: dict) -> None:
    entry = identity["entry"]
    require(not (root / "hooks").exists(), "Claude Adapter must not ship Hooks")
    plugin = read_json(root / ".claude-plugin/plugin.json")
    require(plugin.get("name") == entry, f"Claude manifest name must be {entry}")
    require(plugin.get("version") == version, f"Claude manifest version must match VERSION ({version})")
    require(plugin.get("description") == identity["claude_description"], "Claude manifest description is invalid")
    require(plugin.get("author") == {"name": "SpringBrand"}, "Claude manifest author is invalid")
    require(plugin.get("repository") == "https://github.com/springbrand-lab/springbrand-agent-setup", "Claude repository URL is invalid")
    require(plugin.get("skills") == "./skills/", "Claude skills component must reference ./skills/")
    require(component(root, plugin["skills"], "Claude skills component").is_dir(), "Claude skills component must be a directory")
    validate_mcp_entries(plugin.get("mcpServers"), "Claude MCP server", entry_type="http", entry=entry, url=identity["url"])

    require("hooks" not in plugin, "Claude manifest must not declare Hooks")

    marketplace = read_json(root / ".claude-plugin/marketplace.json")
    require(marketplace.get("name") == entry, f"Claude Marketplace name must be {entry}")
    require(marketplace.get("description") == identity["claude_marketplace_description"], "Claude Marketplace description is invalid")
    require(marketplace.get("owner") == {"name": "SpringBrand"}, "Claude Marketplace owner is invalid")
    require(marketplace.get("plugins") == [{"name": entry, "source": "./"}], f"Claude Marketplace must contain exactly one root {entry} entry")
    require(component(root, marketplace["plugins"][0]["source"], "Claude Marketplace source").is_dir(), "Claude Marketplace source must be a directory")


def validate_skill_mirrors(root: Path, package: Path, host: str) -> None:
    for name in CANONICAL_SKILLS:
        canonical_skill = root / f"skills/{name}/SKILL.md"
        mirrored_skill = package / f"skills/{name}/SKILL.md"
        require(mirrored_skill.is_file(), f"{host} Skill mirror does not exist: {name}")
        require(mirrored_skill.read_bytes() == canonical_skill.read_bytes(), f"{host} Skill mirror for {name} must be byte-equivalent to the Canonical Skill")
        require(re.search(rf"^name:\s*{re.escape(name)}\s*$", mirrored_skill.read_text(), re.MULTILINE), f"{host} Skill mirror name must match the Canonical Skill: {name}")
        for reference in sorted((root / f"skills/{name}/references").glob("*.md")):
            mirrored_reference = package / f"skills/{name}/references/{reference.name}"
            require(mirrored_reference.is_file(), f"{host} Skill reference mirror does not exist: {name}/{reference.name}")
            require(mirrored_reference.read_bytes() == reference.read_bytes(), f"{host} Skill reference mirror for {name}/{reference.name} must be byte-equivalent to the Canonical reference")


def validate_cursor_adapter(root: Path, version: str, identity: dict) -> None:
    entry = identity["entry"]
    marketplace = read_json(root / ".cursor-plugin/marketplace.json")
    require(marketplace.get("name") == entry, f"Cursor Marketplace name must be {entry}")
    require(marketplace.get("metadata", {}).get("version") == version, f"Cursor Marketplace version must match VERSION ({version})")
    entries = [entry_ for entry_ in marketplace.get("plugins", []) if entry_.get("name") == entry]
    require(len(entries) == 1, f"Cursor Marketplace must contain exactly one {entry} entry")
    require(entries[0].get("source") == "./plugins/springbrand", "Cursor Marketplace source must reference ./plugins/springbrand")
    package = component(root, entries[0]["source"], "Cursor Marketplace source")
    require(package.is_dir(), "Cursor Marketplace source must be a directory")

    plugin = read_json(package / ".cursor-plugin/plugin.json")
    require(plugin.get("name") == entry, f"Cursor manifest name must be {entry}")
    require(plugin.get("version") == version, f"Cursor manifest version must match VERSION ({version})")
    require(plugin.get("logo") == "assets/springbrand-icon.svg", "Cursor logo must reference assets/springbrand-icon.svg")
    require((package / plugin["logo"]).is_file(), "Cursor logo does not exist")

    validate_skill_mirrors(root, package, "Cursor")
    require((package / "assets/springbrand-icon.svg").read_bytes() == (root / "assets/springbrand-icon.svg").read_bytes(), "Cursor logo mirror must be byte-equivalent to the canonical logo")

    validate_mcp_entries(read_json(package / "mcp.json").get("mcpServers"), "Cursor MCP endpoint", entry_type=None, entry=entry, url=identity["url"])
    require(not (package / "hooks").exists(), "Cursor Adapter must not ship Hooks")
    require(not (package / "rules").exists(), "Cursor Adapter must not ship Rules")


def validate_workbuddy_adapter(root: Path, version: str, identity: dict) -> None:
    entry = identity["entry"]
    marketplace = read_json(root / ".codebuddy-plugin/marketplace.json")
    require(marketplace.get("name") == entry, f"WorkBuddy Marketplace name must be {entry}")
    entries = marketplace.get("plugins", [])
    require(len(entries) == 1 and entries[0].get("name") == entry, f"WorkBuddy Marketplace must contain exactly one {entry} entry")
    require(entries[0].get("source") == "./plugins/springbrand-workbuddy", "WorkBuddy Marketplace source must reference ./plugins/springbrand-workbuddy")
    package = component(root, entries[0]["source"], "WorkBuddy Marketplace source")
    require(package.is_dir(), "WorkBuddy Marketplace source must be a directory")

    plugin = read_json(package / ".workbuddy-plugin/plugin.json")
    require(plugin.get("name") == entry, f"WorkBuddy manifest name must be {entry}")
    require(plugin.get("version") == version, f"WorkBuddy manifest version must match VERSION ({version})")
    for field, reference in (("skills", "./skills/"), ("mcpServers", "./.mcp.json")):
        require(plugin.get(field) == reference, f"WorkBuddy {field} component must reference {reference}")
        component(package, reference, f"WorkBuddy {field} component")
    require("hooks" not in plugin, "WorkBuddy manifest must not declare Hooks")

    validate_skill_mirrors(root, package, "WorkBuddy")

    validate_mcp_entries(read_json(package / ".mcp.json").get("mcpServers"), "WorkBuddy MCP server", entry_type="http", entry=entry, url=identity["url"])

    require(not (package / "hooks").exists(), "WorkBuddy Adapter must not ship Hooks")
    require(not (package / "rules").exists(), "WorkBuddy Adapter must not ship Rules")


def validate_secrets(root: Path) -> None:
    forbidden_names = {".env", ".env.local", "credentials.json", "secrets.json"}
    forbidden_suffixes = (".pem", ".key")
    for path in root.rglob("*"):
        if (
            ".git" in path.parts
            or "__pycache__" in path.parts
            or path.suffix == ".pyc"
            or not path.is_file()
            or path.resolve() == Path(__file__).resolve()
        ):
            continue
        relative = path.relative_to(root)
        require(path.name not in forbidden_names, f"forbidden credential file: {relative}")
        require(not path.name.endswith(forbidden_suffixes), f"forbidden private-key file: {relative}")
        text = path.read_bytes()
        require(b"-----BEGIN " not in text, f"private key material found in: {relative}")
        require(not re.search(rb"\b(?:sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{12,}|github_pat_[A-Za-z0-9_]{12,}|AKIA[A-Z0-9]{12,})\b", text), f"credential-like token found in: {relative}")


def validate_package(root: Path = ROOT) -> None:
    for path in root.rglob("*.json"):
        if ".git" not in path.parts:
            read_json(path)
    version = validate_canonical_package(root)
    identity = identity_for(version)
    validate_secrets(root)
    validate_codex_adapter(root, version, identity)
    validate_claude_adapter(root, version, identity)
    validate_cursor_adapter(root, version, identity)
    validate_workbuddy_adapter(root, version, identity)


def main() -> None:
    try:
        validate_package()
    except AssertionError as exc:
        raise SystemExit(f"package validation failed: {exc}") from exc


if __name__ == "__main__":
    main()
