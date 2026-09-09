#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ENTRY = "springbrand-dev" if "-dev." in (ROOT / "VERSION").read_text() else "springbrand"

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
        "`platform_` for Platform",
        "`action_` for Action API",
        "`connector_` for Connector",
        "## Choosing the domain",
        "**The selected domain**",
        "**A one-line reason**",
        "**The task, restated**",
        "**Known state pointers**",
    ),
    "springbrand-platform": (
        "name: springbrand-platform",
        "single SpringBrand MCP entry",
        "`platform_list_capabilities`",
        "`platform_execute_capability`",
        "Never call an `action_`- or",
        "## Domain boundaries",
        "match → get → add → get_distribution → use",
        "### Match or List: the routing decision tree",
        "references/plugin-discovery.md",
        "exactly **one** `springbrand.plugins.match` request",
        "One request, no keyword fan-out.",
        "Never use `view=usable` for Plugin discovery",
        "never inside the Match body",
        "observation.discovery_id",
        "springbrand.plugins.match",
        "Plugin-only",
        "Preserve the returned order exactly.",
        "error is not a no-match",
        "`springbrand.plugins.list`",
        "springbrand.creations.list",
        "springbrand.creations.upload",
        "springbrand.creations.publish",
        "strict empty object",
        'usageMode: "gateway_action"',
        "action:springbrand@0:<id>",
        "capability_domain_mismatch",
        "recovery.domain",
        "Domain Transition",
        "handed back through Ask SpringBrand",
        "springbrand-state.md",
        "Never present an update as an in-place revision.",
        "never pay or complete an acquisition on the user's behalf",
        'target: "mcp"',
        "mcp-skill-package-v1",
        "render_version",
        "distribution.json",
        "never perform a second marker replacement",
        "end this Platform Domain Skill workflow",
    ),
    "springbrand-action-api": (
        "name: springbrand-action-api",
        "single SpringBrand MCP entry",
        "`action_match_capabilities`",
        "`action_list_capabilities`",
        "`action_get_capability`",
        "`action_execute_capability`",
        "`action_get_execution`",
        "Never call a `platform_`- or",
        "complete: false",
        "action:springbrand@0:<actionId>",
        "expectedRevision",
        "the same reference, the same input body, the same idempotency key, and the same `observation`",
        "observation.discovery_id",
        "insufficient_credits",
        "outcome_unknown",
        "`succeeded`",
        "lookup failure, not a status",
        "capability_domain_mismatch",
        "structured requirement context",
        "Domain Transition",
        "handed back through Ask SpringBrand",
        "`inputSchema`",
        "`outputSchema`",
    ),
    "springbrand-connector": (
        "name: springbrand-connector",
        "single SpringBrand MCP entry",
        "`connector_search_capabilities`",
        "`connector_execute_capability`",
        "Never call a `platform_`- or",
        "## Domain boundaries",
        "GitHub",
        "next_cursor",
        "connector:<connection_id>:<release>:<action_id>",
        "missing_scope",
        "credential_invalid",
        "Send no idempotency key.",
        "observation.discovery_id",
        "capability_domain_mismatch",
        "Domain Transition",
        "handed back through Ask SpringBrand",
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
    "It has three capability domains on one MCP entry",
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
    assert f"/{PLUGIN_ENTRY}:ask-springbrand" in claude_context

    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_rule = " ".join(rule.split())
    assert "alwaysApply: true" in rule
    assert "ask-springbrand" in normalized_rule
    for phrase in ROUTING_NOTICE_PHRASES:
        assert phrase in normalized_rule, phrase
    for phrase in RETIRED_PHRASES:
        assert phrase not in normalized_rule, phrase

    context = (ROOT / "CONTEXT.md").read_text()
    design = (ROOT / "docs/platform-workflow-design.md").read_text()
    assert "**Generated Business Skill**" in context
    assert "The Platform Domain Skill ends before this Skill activates" in context
    assert "Amendment (2026-09-07)" in design
    action = (ROOT / "skills/springbrand-action-api/SKILL.md").read_text()
    assert "**`input_schema`**" not in action
    assert "**`output_schema`**" not in action


if __name__ == "__main__":
    main()
