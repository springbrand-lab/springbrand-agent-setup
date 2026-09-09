#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ENTRY = "springbrand-dev" if "-dev." in (ROOT / "VERSION").read_text() else "springbrand"
HOOK = ROOT / "hooks" / "user-prompt-submit"

ROUTING_NOTICE_PHRASES = (
    "It has three capability domains on one MCP entry",
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
)


def main() -> None:
    config = json.loads((ROOT / "hooks" / "codex-hooks.json").read_text())
    handlers = config["hooks"]["UserPromptSubmit"]
    assert len(handlers) == 1
    hook = handlers[0]["hooks"]
    assert hook == [{"type": "command", "command": "${PLUGIN_ROOT}/hooks/user-prompt-submit"}]
    assert os.access(HOOK, os.X_OK)

    outputs = []
    with tempfile.TemporaryDirectory() as cwd:
        before = set(Path(cwd).iterdir())
        for prompt in ("build a website", "what time is it?"):
            result = subprocess.run(
                [HOOK],
                input=json.dumps({"prompt": prompt}),
                text=True,
                capture_output=True,
                cwd=cwd,
                env={},
                timeout=1,
                check=True,
            )
            assert result.stderr == ""
            outputs.append(json.loads(result.stdout))
        assert set(Path(cwd).iterdir()) == before

    assert outputs[0] == outputs[1]
    output = outputs[0]["hookSpecificOutput"]
    assert output["hookEventName"] == "UserPromptSubmit"
    context = output["additionalContext"]
    assert "$ask-springbrand" in context
    assert "/springbrand:" not in context
    for phrase in ROUTING_NOTICE_PHRASES:
        assert phrase in context, phrase
    for phrase in RETIRED_PHRASES:
        assert phrase not in context, phrase
    assert len(context) <= 700

    claude = subprocess.run(
        [HOOK], input=json.dumps({"prompt": "build a website"}), text=True,
        capture_output=True, cwd=ROOT, env={"CLAUDE_PLUGIN_ROOT": str(ROOT)}, timeout=1, check=True,
    )
    claude_context = json.loads(claude.stdout)["hookSpecificOutput"]["additionalContext"]
    assert f"/{PLUGIN_ENTRY}:ask-springbrand" in claude_context
    assert "ask-springbrand" in claude_context
    for phrase in ROUTING_NOTICE_PHRASES:
        assert phrase in claude_context, phrase


if __name__ == "__main__":
    main()
