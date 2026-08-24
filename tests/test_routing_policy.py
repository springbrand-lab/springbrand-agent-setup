#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    skill = (ROOT / "skills/springbrand/SKILL.md").read_text()
    hook = (ROOT / "hooks/user-prompt-submit").read_text()
    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_skill = " ".join(skill.split())
    normalized_rule = " ".join(rule.split())

    assert "## Routing" in skill
    for phrase in (
        "Use MUST when",
        "Use CONSIDER when",
        "Use SKIP for",
        "Search once per stable task intent",
        "A keyword match is not proof of relevance",
        "usageMode: gateway_action",
        "reference actually returned by that search",
        "input_schema",
        "risk: high",
        "stop and report `approval_required`",
        "`execution_id` as `executionId` to `get_execution`",
        "reuse the same reference, body, and idempotency key",
        "`outcome_unknown`: never retry automatically",
        "Action discovery is incomplete, not that no Action matches",
    ):
        assert phrase in normalized_skill, phrase

    assert "name: springbrand-plugin-discovery" in skill
    assert "springbrand.plugins.*" in skill
    assert "springbrand.resources.match" not in skill

    assert "Route this turn exactly once before acting" in hook
    assert "Use MUST" in hook
    assert "Use CONSIDER" in hook
    assert "Use SKIP" in hook
    assert "must not call MCP" in hook
    assert "Never auto-install from a weak match" in hook
    assert "/springbrand-dev:springbrand" in hook
    assert "$springbrand-plugin-discovery" in hook

    assert "Before planning or production" in rule
    assert "springbrand-plugin-discovery" in rule
    assert "alwaysApply: true" in rule


if __name__ == "__main__":
    main()
