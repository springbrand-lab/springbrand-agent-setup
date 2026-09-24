#!/usr/bin/env python3
"""Focused generic Action API framework and mirror checks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/springbrand-action-api/SKILL.md"
REFERENCE = ROOT / "skills/springbrand-action-api/references/action-discovery.md"
MIRRORS = (
    ROOT / "plugins/springbrand/skills/springbrand-action-api",
    ROOT / "plugins/springbrand-workbuddy/skills/springbrand-action-api",
)
ALIAS_FILES = (
    ROOT / "skills/springbrand-action-api/references/action-aliases.md",
    *(mirror / "references/action-aliases.md" for mirror in MIRRORS),
)
LEGACY = (
    "action_match_capabilities", "action_list_capabilities", "action_get_capability",
    "action_execute_capability", "action_get_execution", "action_render_execution_image",
    "action:springbrand@0:", "normalized_intent", "next_cursor",
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


def test_mirrors_are_byte_equivalent() -> None:
    for mirror in MIRRORS:
        assert (mirror / "SKILL.md").read_bytes() == SKILL.read_bytes()
        assert (mirror / "references/action-discovery.md").read_bytes() == REFERENCE.read_bytes()


def test_action_uses_unified_contract_without_legacy_paths() -> None:
    combined = SKILL.read_text() + REFERENCE.read_text()
    for name in ("search_tools", "get_tool_schemas", "execute_tools", "get_execution"):
        assert f"`{name}`" in combined
    for phrase in ("English", "one bounded list", "opaque Tool ID", "current contract", "not globally ranked", "incomplete", "error is not a no-match"):
        assert phrase in combined, phrase
    for phrase in LEGACY:
        assert phrase not in combined, phrase


def test_search_rules_are_explicit() -> None:
    for path in (SKILL, REFERENCE):
        document = normalized(path)
        for phrase in (
            "Call `search_tools` once",
            "one concise English query",
            "one bounded list",
            "incomplete",
            "opaque Tool ID",
            "`get_tool_schemas`",
        ):
            assert phrase in document, f"{path}: {phrase}"

    discovery = normalized(REFERENCE)
    for phrase in (
        "preserve every explicit constraint",
        "Do not send synonyms as multiple searches",
        "Ask one focused question",
        "service or supplier",
        "local alias table",
        "not a complete inventory",
        "Incomplete result",
        "cannot establish no-match",
        "preserve its opaque Tool ID exactly",
        "get_tool_schemas",
        "Never construct, edit, decode, or classify the Tool ID",
    ):
        assert phrase in discovery, phrase

    skill = normalized(SKILL)
    for phrase in (
        "`search_tools` returns one bounded result",
        "`get_tool_schemas` returns `{ tools: [...] }`",
        "`inputSchema` and `outputSchema` are the current JSON Schemas",
    ):
        assert phrase in skill, phrase


def test_static_alias_catalogue_is_removed() -> None:
    for path in ALIAS_FILES:
        assert not path.exists(), path
    combined = SKILL.read_text() + REFERENCE.read_text()
    for phrase in (
        "supplier.frank.", "action.kie-ai", "Xiaohongshu note search",
        "Seedance 2.0 image to video",
    ):
        assert phrase not in combined, phrase


def test_execution_safety_and_reuse_survive() -> None:
    skill = normalized(SKILL)
    for phrase in (
        "explicit confirmation for this specific run", "stable idempotency key",
        "revision", "insufficient credits", "outcome unknown",
        "Only `succeeded` counts as complete", "lookup failure, not an execution status",
        "Do not search again", "Do not execute again",
    ):
        assert phrase in skill, phrase


def test_image_presentation_prefers_declared_ui_then_content_then_url() -> None:
    skill = normalized(SKILL)
    phrases = (
        "MCP App/UI",
        "Never invent or guess a renderer tool name",
        "prefer an `image` content block",
        "embed the exact saved preview URL as a Markdown image",
        "Never print base64",
    )
    for phrase in phrases:
        assert phrase in skill, phrase
    assert skill.index(phrases[0]) < skill.index(phrases[2]) < skill.index(phrases[3])


def main() -> None:
    test_mirrors_are_byte_equivalent()
    test_action_uses_unified_contract_without_legacy_paths()
    test_search_rules_are_explicit()
    test_static_alias_catalogue_is_removed()
    test_execution_safety_and_reuse_survive()
    test_image_presentation_prefers_declared_ui_then_content_then_url()
    print("action discovery fixtures: ok")


if __name__ == "__main__":
    main()
