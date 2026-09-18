#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ENTRY = "springbrand-dev" if "-dev." in (ROOT / "VERSION").read_text() else "springbrand"

SKILL_PHRASES = {
    "ask-springbrand": (
        "name: ask-springbrand", "## The three domains (user-facing wording)",
        "**Platform** —", "**Action API** —", "**Connector** —",
        "exactly one Domain Skill, and stop", "It never calls an MCP tool",
        "springbrand-state.md", "Ask at most **one** clarifying question",
        "`springbrand-platform`", "`springbrand-action-api`", "`springbrand-connector`",
        "**The selected domain**", "**A one-line reason**", "**The task, restated**",
        "**Known state pointers**",
    ),
    "springbrand-platform": (
        "name: springbrand-platform", "`search_tools`", "`get_tool_schemas`",
        "`execute_tools`", "`get_execution`", "Never call `manage_connections`",
        "opaque Tool ID", "current contract", "match → get → add → get distribution → use",
        "### Step 3 — Add according to cost", "without asking for separate user confirmation",
        "do not bypass a Host-enforced approval", "### Stage 4 — Upload (confirmation gate)",
        "### Stage 5 — Publish (confirmation gate)", "springbrand-state.md",
        "Never present an update as an in-place revision.", "Domain Transition",
        "handed back through Ask SpringBrand",
    ),
    "springbrand-action-api": (
        "name: springbrand-action-api", "`search_tools`", "`get_tool_schemas`",
        "`execute_tools`", "`get_execution`", "Never call `manage_connections`",
        "current contract", "stable idempotency key", "explicit confirmation for this specific run",
        "revision", "insufficient credits", "outcome unknown",
        "Only `succeeded` counts as complete", "lookup failure, not an execution status",
        "Domain Transition", "handed back through Ask SpringBrand",
    ),
    "springbrand-connector": (
        "name: springbrand-connector", "`search_tools`", "`get_tool_schemas`",
        "`manage_connections`", "`execute_tools`", "`get_execution`",
        "Provider Credential", "list, start, status, and disconnect",
        "explicit confirmation for this specific run", "stable idempotency key",
        "outcome unknown", "## Domain boundaries", "Domain Transition",
        "handed back through Ask SpringBrand",
    ),
}

LEGACY_TOOL_NAMES = (
    "platform_list_capabilities", "platform_execute_capability",
    "action_match_capabilities", "action_list_capabilities", "action_get_capability",
    "action_execute_capability", "action_get_execution", "action_render_execution_image",
    "connector_search_capabilities", "connector_execute_capability",
)
LEGACY_REFERENCE_FORMS = (
    "platform:springbrand@0:", "action:springbrand@0:", "connector:<connection_id>",
)
ROUTING_NOTICE_PHRASES = (
    "For substantive go-to-market, marketing, or growth tasks",
    "springbrand-gtm",
    "even when SpringBrand is not mentioned",
    "It has three capability domains on one MCP entry",
    "- Platform: create and publish artifacts, manage Plugins, and browse the Marketplace",
    "- Action API: use dynamic API services for tasks",
    "- Connector: work with third-party systems such as GitHub",
    "recommends exactly one Domain Skill and stops",
    "This Notice only makes the Skills visible", "does not determine fit, call MCP",
)


def hook_context(**env: str) -> str:
    result = subprocess.run(
        [str(ROOT / "hooks/user-prompt-submit")], check=True, capture_output=True,
        text=True, env={**os.environ, **env},
    )
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


def main() -> None:
    for name, phrases in SKILL_PHRASES.items():
        skill = (ROOT / f"skills/{name}/SKILL.md").read_text()
        normalized = " ".join(skill.split())
        for phrase in phrases:
            assert phrase in normalized, f"{name}: {phrase}"
        for phrase in (*LEGACY_TOOL_NAMES, *LEGACY_REFERENCE_FORMS):
            assert phrase not in skill, f"{name}: legacy contract {phrase!r}"

    for package in (ROOT / "plugins/springbrand", ROOT / "plugins/springbrand-workbuddy"):
        for skill in package.glob("skills/*/SKILL.md"):
            text = skill.read_text()
            for phrase in (*LEGACY_TOOL_NAMES, *LEGACY_REFERENCE_FORMS):
                assert phrase not in text, f"{skill}: legacy contract {phrase!r}"

    codex_context = hook_context(CLAUDE_PLUGIN_ROOT="")
    claude_context = hook_context(CLAUDE_PLUGIN_ROOT="/tmp/plugin")
    for context in (codex_context, claude_context):
        for phrase in ROUTING_NOTICE_PHRASES:
            assert phrase in context, phrase
    assert "$ask-springbrand" in codex_context
    assert f"/{PLUGIN_ENTRY}:ask-springbrand" in claude_context

    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_rule = " ".join(rule.split())
    assert "alwaysApply: true" in rule
    for phrase in ROUTING_NOTICE_PHRASES:
        assert phrase in normalized_rule, phrase

    context = (ROOT / "CONTEXT.md").read_text()
    assert "**Meta Tool**" in context
    assert "**Opaque Tool ID**" in context
    assert "The Platform Domain Skill ends before this Skill activates" in context


if __name__ == "__main__":
    main()
