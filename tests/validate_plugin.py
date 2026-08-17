#!/usr/bin/env python3
"""Validate the shipped Plugin contract without third-party test dependencies."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AssertionError(f"invalid JSON: {path}: {exc}") from exc


def main() -> None:
    json_files = [path for path in ROOT.rglob("*.json") if ".git" not in path.parts]
    for path in json_files:
        read_json(path)

    version = (ROOT / "VERSION").read_text().strip()
    plugin = read_json(ROOT / ".codex-plugin/plugin.json")
    assert plugin["name"] == "springbrand"
    assert plugin["version"] == version
    assert plugin["skills"] == "./skills/"
    assert plugin["mcpServers"] == "./.mcp.json"
    assert plugin["repository"] == "https://github.com/springbrand-lab/springbrand-agent-setup"

    marketplace = read_json(ROOT / ".agents/plugins/marketplace.json")
    assert marketplace["name"] == "springbrand"
    entries = [entry for entry in marketplace["plugins"] if entry["name"] == "springbrand"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["source"] == {"source": "local", "path": "./"}
    assert entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}

    mcp = read_json(ROOT / ".mcp.json")
    assert mcp == {
        "mcpServers": {
            "springbrand": {"url": "https://connector.springbrand.ai/mcp"},
        },
    }

    skills = list((ROOT / "skills").glob("*/SKILL.md"))
    assert len(skills) == 1
    skill_name = re.search(r"^name:\s*(\S+)\s*$", skills[0].read_text(), re.MULTILINE)
    assert skill_name, f"missing Skill name: {skills[0]}"
    skill_name = skill_name.group(1)

    hook = ROOT / "hooks/user-prompt-submit"
    assert os.access(hook, os.X_OK)
    config = read_json(ROOT / "hooks/hooks.json")
    command = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert command == "${PLUGIN_ROOT}/hooks/user-prompt-submit"
    outputs = []
    with tempfile.TemporaryDirectory() as cwd:
        for prompt in ("build a website", "what time is it?"):
            result = subprocess.run(
                [hook], input=json.dumps({"prompt": prompt}), text=True,
                capture_output=True, cwd=cwd, env={}, timeout=1, check=True,
            )
            assert result.stderr == ""
            outputs.append(json.loads(result.stdout))
    assert outputs[0] == outputs[1]
    context = outputs[0]["hookSpecificOutput"]["additionalContext"]
    assert outputs[0]["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert f"${skill_name}" in context

    forbidden_names = {".env", ".env.local", "credentials.json", "secrets.json"}
    forbidden_suffixes = (".pem", ".key")
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path == Path(__file__):
            continue
        assert path.name not in forbidden_names
        assert not path.name.endswith(forbidden_suffixes)
        text = path.read_bytes()
        assert b"-----BEGIN " not in text
        assert not re.search(rb"\b(?:sk|ghp|github_pat|AKIA)[A-Za-z0-9_-]{12,}\b", text)


if __name__ == "__main__":
    main()
