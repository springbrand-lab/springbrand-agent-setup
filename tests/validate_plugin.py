#!/usr/bin/env python3
"""Validate the shipped package contract without third-party dependencies."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_MCP_BASE = "https://connector.springbrand.ai/mcp"
PRODUCTION_ENTRIES = {
    "springbrand-platform": f"{PRODUCTION_MCP_BASE}/platform",
    "springbrand-action-api": f"{PRODUCTION_MCP_BASE}/action-api",
    "springbrand-connector": f"{PRODUCTION_MCP_BASE}/connectors",
}
CANONICAL_SKILLS = (
    "ask-springbrand",
    "springbrand-platform",
    "springbrand-action-api",
    "springbrand-connector",
)
ROUTING_NOTICE_MAX_LENGTH = 700
ROUTING_NOTICE_PHRASES = (
    "It has three capability domains",
    "- Platform: create and publish artifacts, manage Plugins, and browse the Marketplace",
    "- Action API: use dynamic API services for tasks",
    "- Connector: work with third-party systems such as GitHub",
    "recommends exactly one Domain Skill and stops",
    "This Notice only makes the Skills visible",
    "does not determine fit, call MCP",
)
RETIRED_PHRASES = (
    "Do not Match again",
    "springbrand-plugin-discovery",
    "springbrand.catalog.match",
    "follow-up to an existing SpringBrand match",
)
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


def validate_routing_notice(context: str, reference: str) -> None:
    require(len(context) <= ROUTING_NOTICE_MAX_LENGTH, f"Routing Notice must stay under {ROUTING_NOTICE_MAX_LENGTH} characters")
    require(reference in context, "Routing Notice must reference the Host-visible Ask SpringBrand Skill")
    for phrase in ROUTING_NOTICE_PHRASES:
        require(phrase in context, f"Routing Notice must carry the three-domain map and Ask SpringBrand pointer (missing: {phrase})")
    for phrase in RETIRED_PHRASES:
        require(phrase not in context, f"Routing Notice must not use retired phrasing: {phrase}")


def validate_routing_hook(hook: Path) -> None:
    require(os.access(hook, os.X_OK), "Codex Hook is not executable")
    source = hook.read_text()
    require(source.startswith("#!/bin/sh\n"), "Canonical Hook must be a POSIX shell command")
    for forbidden in ("curl ", "wget ", "http://", "https://", "$@", "${1"):
        require(forbidden not in source, "Canonical Hook must remain a static, network-free routing command")

    for claude_root, reference in (
        ("", "`$ask-springbrand` Skill"),
        ("/tmp/plugin", "`/springbrand:ask-springbrand`"),
    ):
        result = subprocess.run(
            [str(hook)],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PLUGIN_ROOT": claude_root},
        )
        try:
            output = json.loads(result.stdout)["hookSpecificOutput"]
            context = output["additionalContext"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise AssertionError("Canonical Hook must emit valid UserPromptSubmit JSON") from exc
        require(output.get("hookEventName") == "UserPromptSubmit", "Canonical Hook must emit UserPromptSubmit context")
        validate_routing_notice(context, reference)
        if claude_root:
            require("/springbrand:ask-springbrand" in context, "Claude Hook must use the namespaced Ask SpringBrand reference")
        else:
            require("/springbrand:" not in context, "Codex Hook must not use a Claude Plugin namespace")


def validate_mcp_entries(servers, label: str, entry_type: None | str) -> None:
    expected = {
        name: ({"type": entry_type, "url": url} if entry_type else {"url": url})
        for name, url in PRODUCTION_ENTRIES.items()
    }
    require(servers == expected, f"{label} must register exactly the three production MCP Domain Entries (platform, action-api, connectors) at {PRODUCTION_MCP_BASE} with no credentials or extra fields")


def validate_canonical_package(root: Path) -> str:
    try:
        version = (root / "VERSION").read_text().strip()
    except OSError as exc:
        raise AssertionError(f"cannot read repository VERSION: {exc}") from exc
    require(VERSION_PATTERN.fullmatch(version), f"invalid repository version: {version!r}")

    mcp = read_json(root / ".mcp.json")
    validate_mcp_entries(mcp.get("mcpServers"), "production MCP manifest", entry_type=None)

    skill_names = sorted(path.parent.name for path in (root / "skills").glob("*/SKILL.md"))
    require(
        skill_names == sorted(CANONICAL_SKILLS),
        f"Canonical Skill Set must be exactly the named four-Skill list {sorted(CANONICAL_SKILLS)}, found {skill_names}",
    )
    for name in CANONICAL_SKILLS:
        frontmatter = (root / f"skills/{name}/SKILL.md").read_text().split("\n---\n", 1)[0]
        require(
            re.search(rf"^name:\s*{re.escape(name)}\s*$", frontmatter, re.MULTILINE),
            f"Canonical Skill {name} frontmatter name must match its directory",
        )

    validate_routing_hook(root / "hooks/user-prompt-submit")
    return version


def validate_codex_adapter(root: Path, version: str) -> None:
    plugin = read_json(root / ".codex-plugin/plugin.json")
    require(plugin.get("name") == "springbrand", "Codex manifest name must be springbrand")
    require(plugin.get("version") == version, f"Codex manifest version must match VERSION ({version})")
    require(plugin.get("repository") == "https://github.com/springbrand-lab/springbrand-agent-setup", "Codex repository URL is invalid")
    require(plugin.get("skills") == "./skills/", "Codex skills component must reference ./skills/")
    require(component(root, plugin["skills"], "Codex skills component").is_dir(), "Codex skills component must be a directory")
    require(plugin.get("mcpServers") == "./.mcp.json", "Codex MCP component must reference ./.mcp.json")
    require(component(root, plugin["mcpServers"], "Codex MCP component").is_file(), "Codex MCP component must be a file")
    require(plugin.get("hooks") == "./hooks/codex-hooks.json", "Codex Hook component must reference ./hooks/codex-hooks.json")
    require(component(root, plugin["hooks"], "Codex Hook component").is_file(), "Codex Hook component must be a file")

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
    config = read_json(root / "hooks/codex-hooks.json")
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
    require("$ask-springbrand" in output.get("additionalContext", ""), "Codex Hook must route to $ask-springbrand")


def validate_claude_adapter(root: Path, version: str) -> None:
    require(not (root / "hooks/hooks.json").exists(), "Claude Adapter must not auto-discover the Codex Hook config")
    plugin = read_json(root / ".claude-plugin/plugin.json")
    require(plugin.get("name") == "springbrand", "Claude manifest name must be springbrand")
    require(plugin.get("version") == version, f"Claude manifest version must match VERSION ({version})")
    require(plugin.get("description") == "Discover and use SpringBrand Plugins through the production connector.", "Claude manifest description is invalid")
    require(plugin.get("author") == {"name": "SpringBrand"}, "Claude manifest author is invalid")
    require(plugin.get("repository") == "https://github.com/springbrand-lab/springbrand-agent-setup", "Claude repository URL is invalid")
    require(plugin.get("skills") == "./skills/", "Claude skills component must reference ./skills/")
    require(component(root, plugin["skills"], "Claude skills component").is_dir(), "Claude skills component must be a directory")
    validate_mcp_entries(plugin.get("mcpServers"), "Claude MCP server", entry_type="http")

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

    result = subprocess.run(
        [root / "hooks/user-prompt-submit"], input=json.dumps({"prompt": "build a website"}),
        text=True, capture_output=True, cwd=root, env={"CLAUDE_PLUGIN_ROOT": str(root)}, timeout=5, check=True,
    )
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    require(
        "/springbrand:ask-springbrand" in context and "ask-springbrand" in context,
        "Claude Hook must invoke the namespaced Ask SpringBrand Skill",
    )

    marketplace = read_json(root / ".claude-plugin/marketplace.json")
    require(marketplace.get("name") == "springbrand", "Claude Marketplace name must be springbrand")
    require(marketplace.get("description") == "SpringBrand plugins for discovering and using reusable Plugins.", "Claude Marketplace description is invalid")
    require(marketplace.get("owner") == {"name": "SpringBrand"}, "Claude Marketplace owner is invalid")
    require(marketplace.get("plugins") == [{"name": "springbrand", "source": "./"}], "Claude Marketplace must contain exactly one root springbrand entry")
    require(component(root, marketplace["plugins"][0]["source"], "Claude Marketplace source").is_dir(), "Claude Marketplace source must be a directory")


def validate_skill_mirrors(root: Path, package: Path, host: str) -> None:
    for name in CANONICAL_SKILLS:
        canonical_skill = root / f"skills/{name}/SKILL.md"
        mirrored_skill = package / f"skills/{name}/SKILL.md"
        require(mirrored_skill.is_file(), f"{host} Skill mirror does not exist: {name}")
        require(mirrored_skill.read_bytes() == canonical_skill.read_bytes(), f"{host} Skill mirror for {name} must be byte-equivalent to the Canonical Skill")
        require(re.search(rf"^name:\s*{re.escape(name)}\s*$", mirrored_skill.read_text(), re.MULTILINE), f"{host} Skill mirror name must match the Canonical Skill: {name}")


def validate_cursor_adapter(root: Path, version: str) -> None:
    marketplace = read_json(root / ".cursor-plugin/marketplace.json")
    require(marketplace.get("name") == "springbrand", "Cursor Marketplace name must be springbrand")
    require(marketplace.get("metadata", {}).get("version") == version, f"Cursor Marketplace version must match VERSION ({version})")
    entries = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == "springbrand"]
    require(len(entries) == 1, "Cursor Marketplace must contain exactly one springbrand entry")
    require(entries[0].get("source") == "./plugins/springbrand", "Cursor Marketplace source must reference ./plugins/springbrand")
    package = component(root, entries[0]["source"], "Cursor Marketplace source")
    require(package.is_dir(), "Cursor Marketplace source must be a directory")

    plugin = read_json(package / ".cursor-plugin/plugin.json")
    require(plugin.get("name") == "springbrand", "Cursor manifest name must be springbrand")
    require(plugin.get("version") == version, f"Cursor manifest version must match VERSION ({version})")
    require(plugin.get("logo") == "assets/springbrand-icon.svg", "Cursor logo must reference assets/springbrand-icon.svg")
    require((package / plugin["logo"]).is_file(), "Cursor logo does not exist")

    validate_skill_mirrors(root, package, "Cursor")
    require((package / "assets/springbrand-icon.svg").read_bytes() == (root / "assets/springbrand-icon.svg").read_bytes(), "Cursor logo mirror must be byte-equivalent to the canonical logo")

    rule = (package / "rules/springbrand-preflight.mdc")
    require(rule.is_file(), "Cursor Rule mirror does not exist")
    frontmatter = rule.read_text().split("\n---\n", 1)
    require(len(frontmatter) == 2 and frontmatter[0].startswith("---\n"), "Cursor Rule must have frontmatter")
    require(re.search(r"^alwaysApply:\s*true\s*$", frontmatter[0][4:], re.MULTILINE), "Cursor Rule must always apply")
    require(rule.read_bytes() == (root / "rules/springbrand-preflight.mdc").read_bytes(), "Cursor Rule mirror must be byte-equivalent to the canonical Rule")
    normalized_rule = " ".join(rule.read_text().split())
    require("ask-springbrand" in normalized_rule, "Cursor Rule must point uncertain routing at Ask SpringBrand")
    require("This Notice only makes the Skills visible" in normalized_rule, "Cursor Rule must remain a Notice-only adapter")
    for phrase in RETIRED_PHRASES:
        require(phrase not in normalized_rule, f"Cursor Rule must not use retired phrasing: {phrase}")

    validate_mcp_entries(read_json(package / "mcp.json").get("mcpServers"), "Cursor MCP endpoint", entry_type=None)
    require(not (package / "hooks").exists(), "Cursor Adapter must not ship Hooks")


def validate_workbuddy_adapter(root: Path, version: str) -> None:
    marketplace = read_json(root / ".codebuddy-plugin/marketplace.json")
    require(marketplace.get("name") == "springbrand", "WorkBuddy Marketplace name must be springbrand")
    entries = marketplace.get("plugins", [])
    require(len(entries) == 1 and entries[0].get("name") == "springbrand", "WorkBuddy Marketplace must contain exactly one springbrand entry")
    require(entries[0].get("source") == "./plugins/springbrand-workbuddy", "WorkBuddy Marketplace source must reference ./plugins/springbrand-workbuddy")
    package = component(root, entries[0]["source"], "WorkBuddy Marketplace source")
    require(package.is_dir(), "WorkBuddy Marketplace source must be a directory")

    plugin = read_json(package / ".workbuddy-plugin/plugin.json")
    require(plugin.get("name") == "springbrand", "WorkBuddy manifest name must be springbrand")
    require(plugin.get("version") == version, f"WorkBuddy manifest version must match VERSION ({version})")
    for field, reference in (("skills", "./skills/"), ("hooks", "./hooks/hooks.json"), ("mcpServers", "./.mcp.json")):
        require(plugin.get(field) == reference, f"WorkBuddy {field} component must reference {reference}")
        component(package, reference, f"WorkBuddy {field} component")

    validate_skill_mirrors(root, package, "WorkBuddy")

    hook = package / "hooks/user-prompt-submit"
    require(hook.read_bytes() == (root / "hooks/user-prompt-submit").read_bytes(), "WorkBuddy Hook mirror must be byte-equivalent to the canonical Hook")
    require(os.access(hook, os.X_OK), "WorkBuddy Hook is not executable")
    expected_hooks = [{"hooks": [{"type": "command", "command": "${CODEBUDDY_PLUGIN_ROOT}/hooks/user-prompt-submit"}]}]
    try:
        hooks = read_json(package / "hooks/hooks.json")["hooks"]["UserPromptSubmit"]
    except (KeyError, TypeError) as exc:
        raise AssertionError("WorkBuddy Hook config must declare hooks.UserPromptSubmit") from exc
    require(hooks == expected_hooks, "WorkBuddy Hook config must reference ${CODEBUDDY_PLUGIN_ROOT}/hooks/user-prompt-submit")

    validate_mcp_entries(read_json(package / ".mcp.json").get("mcpServers"), "WorkBuddy MCP server", entry_type="http")

    guide = (root / "INSTALL.workbuddy.md").read_text().lower()
    require("installing and enabling" in guide and "trust decision" in guide, "WorkBuddy installation guide must disclose the Plugin Hook trust decision")


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
    version = validate_canonical_package(root)
    validate_secrets(root)
    validate_codex_adapter(root, version)
    validate_claude_adapter(root, version)
    validate_cursor_adapter(root, version)
    validate_workbuddy_adapter(root, version)


def main() -> None:
    try:
        validate_package()
    except AssertionError as exc:
        raise SystemExit(f"package validation failed: {exc}") from exc


if __name__ == "__main__":
    main()
