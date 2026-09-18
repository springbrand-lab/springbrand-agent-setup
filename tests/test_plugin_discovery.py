#!/usr/bin/env python3
"""Focused Platform workflow and mirror checks for the unified Meta Tools."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/springbrand-platform/SKILL.md"
REFERENCE = ROOT / "skills/springbrand-platform/references/plugin-discovery.md"
MIRRORS = (
    ROOT / "plugins/springbrand/skills/springbrand-platform",
    ROOT / "plugins/springbrand-workbuddy/skills/springbrand-platform",
)
LEGACY = (
    "platform_list_capabilities", "platform_execute_capability",
    "springbrand.plugins.match", "springbrand.plugins.list", "platform:springbrand@0:",
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


def test_mirrors_are_byte_equivalent() -> None:
    for mirror in MIRRORS:
        assert (mirror / "SKILL.md").read_bytes() == SKILL.read_bytes()
        assert (mirror / "references/plugin-discovery.md").read_bytes() == REFERENCE.read_bytes()


def test_platform_uses_unified_contract_without_legacy_paths() -> None:
    combined = SKILL.read_text() + REFERENCE.read_text()
    for name in ("search_tools", "get_tool_schemas", "execute_tools"):
        assert f"`{name}`" in combined
    for phrase in ("one bounded list", "English", "opaque Tool ID", "current contract", "incomplete", "error is not a no-match"):
        assert phrase in combined, phrase
    for phrase in LEGACY:
        assert phrase not in combined, phrase


def test_platform_business_and_confirmation_rules_survive() -> None:
    skill = normalized(SKILL)
    for phrase in (
        "match → get → add → get distribution → use",
        "without asking for separate user confirmation", "Paid and already entitled",
        "Paid and not entitled", "Unknown cost", "do not bypass a Host-enforced approval",
        "upload", "publish", "springbrand-state.md",
        "Never present an update as an in-place revision.",
        "never pay or complete an acquisition on the user's behalf",
    ):
        assert phrase in skill, phrase


def main() -> None:
    test_mirrors_are_byte_equivalent()
    test_platform_uses_unified_contract_without_legacy_paths()
    test_platform_business_and_confirmation_rules_survive()
    print("platform discovery fixtures: ok")


if __name__ == "__main__":
    main()
