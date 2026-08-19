#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "user-prompt-submit"


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
    assert "$springbrand-resource-discovery" in context
    assert "capability-gap gate" in context
    assert "SpringBrand is optional" in context
    assert "continue without calling SpringBrand MCP" in context

    claude = subprocess.run(
        [HOOK], input=json.dumps({"prompt": "build a website"}), text=True,
        capture_output=True, cwd=ROOT, env={"CLAUDE_PLUGIN_ROOT": str(ROOT)}, timeout=1, check=True,
    )
    claude_context = json.loads(claude.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "/springbrand-dev:springbrand" in claude_context
    assert "springbrand-resource-discovery" in claude_context
    assert "capability-gap gate" in claude_context


if __name__ == "__main__":
    main()
