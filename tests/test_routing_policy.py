#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def hook_context(**env: str) -> str:
    result = subprocess.run(
        [str(ROOT / "hooks/user-prompt-submit")],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **env},
    )
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


def main() -> None:
    skill = (ROOT / "skills/springbrand/SKILL.md").read_text()
    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_skill = " ".join(skill.split())
    normalized_rule = " ".join(rule.split())

    assert "## Route" in skill
    for phrase in (
        "**DIRECT:**",
        "**REUSE:**",
        "**BROWSE:**",
        "**MATCH:**",
        "action_id` is `springbrand.catalog.match",
        "`limit`: `5`",
        "preserve `match_id` and Platform order",
        "Do not call List",
        "Never treat an error as `no_match`",
        "Read `user_state`",
        "List is not a Match pre-step",
        "usageMode: gateway_action",
        "reference actually returned by that search",
        "input_schema",
        "risk: high",
        "never fabricate approval",
        "`execution_id` as `executionId` to `get_execution`",
        "reuse the same reference, body, and idempotency key",
        "insufficient_credits",
        "recovery.action: add_credits",
        "`outcome_unknown`: never retry automatically",
        "Action discovery is incomplete, not that no Action matches",
        # Catalog Match contract: kind branching
        "kind = plugin",
        "kind = api_service",
        "action:springbrand@0:<actionId>",
        "bypass Plugin lifecycle",
        "Do not synthesize",
        "no `user_state`",
        "no revision",
        "no `expectedRevision`",
        "springbrand.plugins.list",
    ):
        assert phrase in normalized_skill, phrase

    assert "name: springbrand-plugin-discovery" in skill
    assert "springbrand.resources.match" not in skill
    assert "approval_required" not in skill
    assert "full-catalogue fallback" not in normalized_skill

    codex_context = hook_context(CLAUDE_PLUGIN_ROOT="")
    claude_context = hook_context(CLAUDE_PLUGIN_ROOT="/tmp/plugin")
    for context in (codex_context, claude_context):
        assert "This Notice only makes the Skill visible" in context
        assert "follow-up to an existing SpringBrand match" in context
        assert "Do not Match again" in context
        assert "does not determine fit, call MCP" in context
    assert "$springbrand-plugin-discovery" in codex_context
    assert "/springbrand:springbrand" in claude_context

    assert "alwaysApply: true" in rule
    assert "springbrand-plugin-discovery" in rule
    assert "This Notice only makes the Skill visible" in rule
    assert "Do not Match again" in normalized_rule


if __name__ == "__main__":
    main()
