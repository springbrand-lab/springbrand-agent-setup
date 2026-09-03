#!/usr/bin/env python3
"""Behavior and packaging fixtures for Action API discovery.

The agent-facing contract lives in the canonical Action API Skill and its
on-demand reference. These fixtures pin the English normalized_intent
contract (snake_case, unlike the Platform's camelCase normalizedIntent), the
malformed-body rematch rule, the empty-result semantics, and the mirror
byte-equivalence.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/springbrand-action-api/SKILL.md"
REFERENCE = ROOT / "skills/springbrand-action-api/references/action-discovery.md"
CURSOR_MIRROR = ROOT / "plugins/springbrand/skills/springbrand-action-api"
WORKBUDDY_MIRROR = ROOT / "plugins/springbrand-workbuddy/skills/springbrand-action-api"

QA_INTENT = "用springbrand帮我生成土豆番茄大战的漫画"
QA_NORMALIZED = "generate comic image from text"


def normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


def json_blocks(text: str) -> list:
    return [json.loads(block) for block in re.findall(r"```json\n(.*?)```", text, re.DOTALL)]


def validate_match_input(body: dict) -> None:
    assert isinstance(body, dict)
    assert set(body) <= {"intent", "normalized_intent", "locale"}, body
    assert set(body) >= {"intent"}
    assert isinstance(body["intent"], str) and 1 <= len(body["intent"].strip()) <= 4000
    if "normalized_intent" in body:
        value = body["normalized_intent"]
        assert isinstance(value, str) and 1 <= len(value.strip()) <= 1000
    if "locale" in body:
        value = body["locale"]
        assert isinstance(value, str) and 2 <= len(value.strip()) <= 35


def test_mirrors_are_byte_equivalent() -> None:
    canonical_skill = SKILL.read_bytes()
    canonical_reference = REFERENCE.read_bytes()
    for mirror in (CURSOR_MIRROR, WORKBUDDY_MIRROR):
        assert (mirror / "SKILL.md").read_bytes() == canonical_skill
        assert (mirror / "references/action-discovery.md").read_bytes() == canonical_reference


def test_skill_points_to_reference_before_any_body() -> None:
    skill = normalized(SKILL)
    assert "Before constructing any match body, read [references/action-discovery.md](references/action-discovery.md)" in skill


def test_chinese_intent_produces_one_normalized_match_body() -> None:
    blocks = json_blocks(REFERENCE.read_text())
    qa_examples = [body for body in blocks if body.get("intent") == QA_INTENT]
    assert len(qa_examples) == 3, "one valid and two rejected bodies for the QA request"
    valid = [body for body in qa_examples if body.get("normalized_intent") == QA_NORMALIZED]
    rejected = [body for body in qa_examples if "normalized_intent" not in body]
    brand = [body for body in qa_examples if "springbrand" in body.get("normalized_intent", "").lower()]
    assert len(valid) == 1 and len(rejected) == 1 and len(brand) == 1
    for body in qa_examples:
        validate_match_input(body)
    body = valid[0]
    assert body["normalized_intent"] == QA_NORMALIZED
    assert body["normalized_intent"].isascii(), "normalized_intent must be English"
    assert "springbrand" not in body["normalized_intent"].lower()
    assert body["locale"] == "zh-CN"
    skill = normalized(SKILL)
    assert "faithful restatement from Step 1 unchanged" in skill
    assert "never the brand word" in skill


def test_field_name_is_snake_case_not_camel_case() -> None:
    reference = normalized(REFERENCE)
    assert "normalized_intent" in reference
    assert "takes **camelCase** `normalizedIntent`" in reference, "the field-name trap must name both casings explicitly"
    assert "Never carry the field name across domains" in reference
    skill = normalized(SKILL)
    assert "normalized_intent" in skill
    assert "normalizedIntent" not in skill


def test_empty_result_semantics_are_pinned() -> None:
    skill = normalized(SKILL)
    assert "malformed body, not a no-match" in skill
    assert "fix the body and rematch once" in skill
    reference = normalized(REFERENCE)
    for outcome in ("Malformed body", "Genuine no-match", "Provider failure"):
        assert outcome in reference, outcome
    assert "Never tell the user nothing fits from a malformed body" in reference
    assert "Exactly one well-formed rematch is the ceiling" in reference
    assert "`action_list_capabilities` stays browse-only" in reference or "action_list_capabilities` stays browse-only" in reference


def test_complete_semantics_are_documented() -> None:
    reference = normalized(REFERENCE)
    assert "complete: false" in reference
    assert "sourceLimitation" in reference
    assert "upstream_mixed_result_truncated" in reference
    assert "not proof that the catalogue lacks the capability" in reference


def test_output_contract_is_exact() -> None:
    reference = REFERENCE.read_text()
    for field in ("`matchId`", "`apiServiceId`", "`actionId`", "`score`", "`matchedOn`", "`outcome`"):
        assert field in reference, field
    assert "`matches_found`" in reference and "`no_match`" in reference


def test_action_verb_guidance_is_present() -> None:
    reference = normalized(REFERENCE)
    assert "verb-first" in reference
    assert "text-to-image" in reference and "image-to-image" in reference
    assert "presentation, not reranking" in reference


def main() -> None:
    test_mirrors_are_byte_equivalent()
    test_skill_points_to_reference_before_any_body()
    test_chinese_intent_produces_one_normalized_match_body()
    test_field_name_is_snake_case_not_camel_case()
    test_empty_result_semantics_are_pinned()
    test_complete_semantics_are_documented()
    test_output_contract_is_exact()
    test_action_verb_guidance_is_present()
    print("action discovery fixtures: ok")


if __name__ == "__main__":
    main()
