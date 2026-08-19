#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    skill = (ROOT / "skills/springbrand/SKILL.md").read_text()
    hook = (ROOT / "hooks/user-prompt-submit").read_text()
    rule = (ROOT / "plugins/springbrand/rules/springbrand-preflight.mdc").read_text()
    normalized_skill = " ".join(skill.split())
    normalized_rule = " ".join(rule.split())

    assert "## 0. Capability-gap gate" in skill
    for phrase in (
        "supplied material",
        "general planning without execution",
        "diagnosis of SpringBrand, MCP",
        "do not by themselves establish a capability gap",
        "do not enter complete-catalog fallback",
    ):
        assert phrase in normalized_skill, phrase

    assert "SpringBrand is optional" in hook
    assert "capability-gap gate" in hook
    assert "continue without calling SpringBrand MCP" in hook
    assert "/springbrand:springbrand" in hook
    assert "$springbrand-resource-discovery" in hook
    assert "For requests eligible under its description" not in hook

    assert "SpringBrand is optional" in rule
    assert "capability-gap gate" in rule
    assert "do not alone establish a capability gap" in normalized_rule
    assert "For an explicit SpringBrand request or a clear" in normalized_rule
    assert "alwaysApply: true" in rule


if __name__ == "__main__":
    main()
