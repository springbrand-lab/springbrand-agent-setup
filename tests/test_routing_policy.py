#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    skill = (ROOT / "skills/springbrand/SKILL.md").read_text()
    hook = (ROOT / "hooks/user-prompt-submit").read_text()
    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_skill = " ".join(skill.split())
    normalized_rule = " ".join(rule.split())

    assert "## Trigger timing" in skill
    for phrase in (
        "A vague request is sufficient",
        "Run it before",
        "before",
    ):
        assert phrase in normalized_skill, phrase

    assert "For requests eligible under its description" in hook
    assert "capability-gap gate" not in hook
    assert "/springbrand:springbrand" in hook
    assert "$springbrand-plugin-discovery" in hook

    assert "Before planning or production" in rule
    assert "springbrand-plugin-discovery" in rule
    assert "alwaysApply: true" in rule


if __name__ == "__main__":
    main()
