#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKILL_PHRASES = {
    "ask-springbrand": (
        "name: ask-springbrand",
        "## The three domains (user-facing wording)",
        "**Platform** —",
        "**Action API** —",
        "**Connector** —",
        "exactly one Domain Skill, and stop",
        "It never discovers or executes a capability",
        "It never calls an MCP tool",
        "It never activates more than one Domain Skill",
        "springbrand-state.md",
        "Ask at most **one** clarifying question",
        "`springbrand-platform`",
        "`springbrand-action-api`",
        "`springbrand-connector`",
        "## Choosing the domain",
        "**The selected domain**",
        "**A one-line reason**",
        "**The task, restated**",
        "**Known state pointers**",
    ),
    "springbrand-platform": (
        "name: springbrand-platform",
        "`springbrand-platform` MCP Domain Entry",
        "## Domain boundaries",
        "match → get → add → get_distribution → use",
        "springbrand.plugins.match",
        "Plugin-only",
        "Preserve the returned order exactly.",
        "error is not a no-match",
        "`springbrand.plugins.list` search",
        "springbrand.creations.list",
        "springbrand.creations.upload",
        "springbrand.creations.publish",
        "strict empty object",
        'usageMode: "gateway_action"',
        "action:springbrand@0:<id>",
        "capability_domain_mismatch",
        "recovery.domain",
        "Domain Transition",
        "springbrand-state.md",
        "Never present an update as an in-place revision.",
        "never pay or complete an acquisition on the user's behalf",
    ),
    "springbrand-action-api": (
        "name: springbrand-action-api",
        "`springbrand-action-api` MCP Domain Entry",
        "## Domain boundaries",
        "`match_capabilities`",
        "`list_capabilities`",
        "`get_capability`",
        "`execute_capability`",
        "`get_execution`",
        "complete: false",
        "action:springbrand@0:<actionId>",
        "expectedRevision",
        "the same reference, the same input body, and the same idempotency key",
        "insufficient_credits",
        "outcome_unknown",
        "`succeeded`",
        "lookup failure, not a status",
        "capability_domain_mismatch",
        "Domain Transition",
    ),
    "springbrand-connector": (
        "name: springbrand-connector",
        "`springbrand-connector` MCP Domain Entry",
        "## Domain boundaries",
        "`search_capabilities`",
        "`execute_capability`",
        "GitHub",
        "next_cursor",
        "connector:<connection_id>:<release>:<action_id>",
        "missing_scope",
        "credential_invalid",
        "Send no idempotency key.",
        "capability_domain_mismatch",
        "Domain Transition",
    ),
}

RETIRED_PHRASES = (
    "springbrand.catalog.match",
    "springbrand.resources.match",
    "springbrand-plugin-discovery",
    "Do not Match again",
    "follow-up to an existing SpringBrand match",
    "kind = plugin",
    "kind = api_service",
)

ROUTING_NOTICE_PHRASES = (
    "It has three capability domains",
    "- Platform: create and publish artifacts, manage Plugins, and browse the Marketplace",
    "- Action API: use dynamic API services for tasks",
    "- Connector: work with third-party systems such as GitHub",
    "recommends exactly one Domain Skill and stops",
    "This Notice only makes the Skills visible",
    "does not determine fit, call MCP",
)


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
    for name, phrases in SKILL_PHRASES.items():
        skill = (ROOT / f"skills/{name}/SKILL.md").read_text()
        normalized = " ".join(skill.split())
        for phrase in phrases:
            assert phrase in normalized, f"{name}: {phrase}"
        for phrase in RETIRED_PHRASES:
            assert phrase not in normalized, f"{name}: retired phrase {phrase!r}"

    codex_context = hook_context(CLAUDE_PLUGIN_ROOT="")
    claude_context = hook_context(CLAUDE_PLUGIN_ROOT="/tmp/plugin")
    for context in (codex_context, claude_context):
        for phrase in ROUTING_NOTICE_PHRASES:
            assert phrase in context, phrase
        for phrase in RETIRED_PHRASES:
            assert phrase not in context, phrase
    assert "$ask-springbrand" in codex_context
    assert "/springbrand:ask-springbrand" in claude_context

    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_rule = " ".join(rule.split())
    assert "alwaysApply: true" in rule
    assert "ask-springbrand" in normalized_rule
    for phrase in ROUTING_NOTICE_PHRASES:
        assert phrase in normalized_rule, phrase
    for phrase in RETIRED_PHRASES:
        assert phrase not in normalized_rule, phrase


if __name__ == "__main__":
    main()
