#!/usr/bin/env python3
"""Focused Action API workflow, alias, and mirror checks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/springbrand-action-api/SKILL.md"
REFERENCE = ROOT / "skills/springbrand-action-api/references/action-discovery.md"
ALIASES = ROOT / "skills/springbrand-action-api/references/action-aliases.md"
MIRRORS = (
    ROOT / "plugins/springbrand/skills/springbrand-action-api",
    ROOT / "plugins/springbrand-workbuddy/skills/springbrand-action-api",
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
        assert (mirror / "references/action-aliases.md").read_bytes() == ALIASES.read_bytes()


def test_action_uses_unified_contract_without_legacy_paths() -> None:
    combined = SKILL.read_text() + REFERENCE.read_text() + ALIASES.read_text()
    for name in ("search_tools", "get_tool_schemas", "execute_tools", "get_execution"):
        assert f"`{name}`" in combined
    for phrase in ("English", "one bounded list", "opaque Tool ID", "current contract", "not globally ranked", "incomplete", "error is not a no-match"):
        assert phrase in combined, phrase
    for phrase in LEGACY:
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


def test_alias_map_keeps_compatibility_constraints() -> None:
    aliases = normalized(ALIASES)
    for phrase in (
        "Xiaohongshu", "Text to Image", "Image to Image", "Text to Video",
        "Image to Video", "hard compatibility constraint", "Do not invent",
    ):
        assert phrase in aliases, phrase


def main() -> None:
    test_mirrors_are_byte_equivalent()
    test_action_uses_unified_contract_without_legacy_paths()
    test_execution_safety_and_reuse_survive()
    test_alias_map_keeps_compatibility_constraints()
    print("action discovery fixtures: ok")


if __name__ == "__main__":
    main()
