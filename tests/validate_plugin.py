#!/usr/bin/env python3
"""Validate the shipped package contract without third-party dependencies."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_MCP_URL = "https://connector.springbrand.ai/mcp"
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


def validate_canonical_package(root: Path) -> tuple[str, str]:
    try:
        version = (root / "VERSION").read_text().strip()
    except OSError as exc:
        raise AssertionError(f"cannot read repository VERSION: {exc}") from exc
    require(VERSION_PATTERN.fullmatch(version), f"invalid repository version: {version!r}")

    mcp = read_json(root / ".mcp.json")
    expected_mcp = {"mcpServers": {"springbrand": {"url": PRODUCTION_MCP_URL}}}
    require(mcp == expected_mcp, f"production MCP endpoint must be {PRODUCTION_MCP_URL} with no credentials or extra fields")

    skills = list((root / "skills").glob("*/SKILL.md"))
    require(len(skills) == 1, "Canonical Skill must contain exactly one skills/*/SKILL.md")
    skill_name = re.search(r"^name:\s*(\S+)\s*$", skills[0].read_text(), re.MULTILINE)
    require(skill_name, f"Canonical Skill is missing a name: {skills[0]}")
    return version, skill_name.group(1)


def validate_codex_adapter(root: Path, version: str, skill_name: str) -> None:
    plugin = read_json(root / ".codex-plugin/plugin.json")
    require(plugin.get("name") == "springbrand", "Codex manifest name must be springbrand")
    require(plugin.get("version") == version, f"Codex manifest version must match VERSION ({version})")
    require(plugin.get("repository") == "https://github.com/springbrand-lab/springbrand-agent-setup", "Codex repository URL is invalid")
    require(plugin.get("skills") == "./skills/", "Codex skills component must reference ./skills/")
    require(component(root, plugin["skills"], "Codex skills component").is_dir(), "Codex skills component must be a directory")
    require(plugin.get("mcpServers") == "./.mcp.json", "Codex MCP component must reference ./.mcp.json")
    require(component(root, plugin["mcpServers"], "Codex MCP component").is_file(), "Codex MCP component must be a file")

    interface = plugin.get("interface", {})
    require(interface.get("brandColor") == "#FF8A2C", "Codex brandColor must be #FF8A2C")
    for field in ("composerIcon", "logo", "logoDark"):
        reference = interface.get(field)
        require(reference == "./assets/springbrand-icon.svg", f"Codex {field} must reference ./assets/springbrand-icon.svg")
        require(component(root, reference, f"Codex {field}").is_file(), f"Codex {field} must be a file")

    marketplace = read_json(root / ".agents/plugins/marketplace.json")
    require(marketplace.get("name") == "springbrand", "Codex Marketplace name must be springbrand")
    entries = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == "springbrand"]
    require(len(entries) == 1, "Codex Marketplace must contain exactly one springbrand entry")
    entry = entries[0]
    require(entry.get("source") == {"source": "local", "path": "./"}, "Codex Marketplace source must reference the package root")
    require(component(root, entry["source"]["path"], "Codex Marketplace source").is_dir(), "Codex Marketplace source must be a directory")
    require(entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "Codex Marketplace policy is invalid")

    hook = root / "hooks/user-prompt-submit"
    require(hook.is_file(), "Codex Hook does not exist: hooks/user-prompt-submit")
    require(os.access(hook, os.X_OK), "Codex Hook is not executable: hooks/user-prompt-submit")
    config = read_json(root / "hooks/hooks.json")
    try:
        hooks = config["hooks"]["UserPromptSubmit"]
    except (KeyError, TypeError) as exc:
        raise AssertionError("Codex Hook config must declare hooks.UserPromptSubmit") from exc
    expected_hook = [{"hooks": [{"type": "command", "command": "${PLUGIN_ROOT}/hooks/user-prompt-submit"}]}]
    require(hooks == expected_hook, "Codex Hook config must reference ${PLUGIN_ROOT}/hooks/user-prompt-submit")

    outputs = []
    with tempfile.TemporaryDirectory() as cwd:
        for prompt in ("build a website", "what time is it?"):
            try:
                result = subprocess.run(
                    [hook], input=json.dumps({"prompt": prompt}), text=True,
                    capture_output=True, cwd=cwd, env={}, timeout=5, check=True,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                raise AssertionError(f"Codex Hook failed for prompt {prompt!r}: {exc}") from exc
            require(result.stderr == "", f"Codex Hook wrote to stderr for prompt {prompt!r}: {result.stderr.strip()}")
            try:
                outputs.append(json.loads(result.stdout))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"Codex Hook returned invalid JSON for prompt {prompt!r}: {exc}") from exc
    require(outputs[0] == outputs[1], "Codex Hook output must not vary by prompt")
    output = outputs[0].get("hookSpecificOutput", {})
    require(output.get("hookEventName") == "UserPromptSubmit", "Codex Hook must return UserPromptSubmit output")
    require(f"${skill_name}" in output.get("additionalContext", ""), f"Codex Hook must route to ${skill_name}")


def validate_claude_adapter(root: Path, version: str, skill_name: str) -> None:
    plugin = read_json(root / ".claude-plugin/plugin.json")
    require(plugin.get("name") == "springbrand", "Claude manifest name must be springbrand")
    require(plugin.get("version") == version, f"Claude manifest version must match VERSION ({version})")
    require(plugin.get("description") == "Discover and use SpringBrand Resources through the production connector.", "Claude manifest description is invalid")
    require(plugin.get("author") == {"name": "SpringBrand"}, "Claude manifest author is invalid")
    require(plugin.get("repository") == "https://github.com/springbrand-lab/springbrand-agent-setup", "Claude repository URL is invalid")
    require(plugin.get("skills") == "./skills/", "Claude skills component must reference ./skills/")
    require(component(root, plugin["skills"], "Claude skills component").is_dir(), "Claude skills component must be a directory")
    require(plugin.get("mcpServers") == {"springbrand": {"type": "http", "url": PRODUCTION_MCP_URL}}, "Claude MCP server must contain only the production HTTP endpoint")

    hooks_reference = plugin.get("hooks")
    require(hooks_reference == "./hooks/claude-hooks.json", "Claude Hook component must reference ./hooks/claude-hooks.json")
    hooks_path = component(root, hooks_reference, "Claude Hook component")
    require(hooks_path.is_file(), "Claude Hook component must be a file")
    config = read_json(hooks_path)
    expected_hook = [{"hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit"}]}]
    try:
        hooks = config["hooks"]["UserPromptSubmit"]
    except (KeyError, TypeError) as exc:
        raise AssertionError("Claude Hook config must declare hooks.UserPromptSubmit") from exc
    require(hooks == expected_hook, "Claude Hook config must reference ${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit")

    marketplace = read_json(root / ".claude-plugin/marketplace.json")
    require(marketplace.get("name") == "springbrand", "Claude Marketplace name must be springbrand")
    require(marketplace.get("description") == "SpringBrand plugins for discovering and using reusable Resources.", "Claude Marketplace description is invalid")
    require(marketplace.get("owner") == {"name": "SpringBrand"}, "Claude Marketplace owner is invalid")
    require(marketplace.get("plugins") == [{"name": "springbrand", "source": "./"}], "Claude Marketplace must contain exactly one root springbrand entry")
    require(component(root, marketplace["plugins"][0]["source"], "Claude Marketplace source").is_dir(), "Claude Marketplace source must be a directory")


def validate_secrets(root: Path) -> None:
    forbidden_names = {".env", ".env.local", "credentials.json", "secrets.json"}
    forbidden_suffixes = (".pem", ".key")
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.resolve() == Path(__file__).resolve():
            continue
        relative = path.relative_to(root)
        require(path.name not in forbidden_names, f"forbidden credential file: {relative}")
        require(not path.name.endswith(forbidden_suffixes), f"forbidden private-key file: {relative}")
        text = path.read_bytes()
        require(b"-----BEGIN " not in text, f"private key material found in: {relative}")
        require(not re.search(rb"\b(?:sk|ghp|github_pat|AKIA)[A-Za-z0-9_-]{12,}\b", text), f"credential-like token found in: {relative}")


def validate_package(root: Path = ROOT) -> None:
    for path in root.rglob("*.json"):
        if ".git" not in path.parts:
            read_json(path)
    version, skill_name = validate_canonical_package(root)
    validate_secrets(root)
    validate_codex_adapter(root, version, skill_name)
    validate_claude_adapter(root, version, skill_name)
    # Add future explicit validate_*_adapter calls here.


def main() -> None:
    try:
        validate_package()
    except AssertionError as exc:
        raise SystemExit(f"package validation failed: {exc}") from exc


if __name__ == "__main__":
    main()
