#!/usr/bin/env python3
"""Behavior and packaging fixtures for Action API discovery.

The agent-facing contract lives in the canonical Action API Skill and its
on-demand reference. These fixtures pin catalogue-facing discovery terms,
hard compatibility selection, bounded inventory recovery, the snake_case
Action Match contract, and Distribution Mirror byte-equivalence.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/springbrand-action-api/SKILL.md"
REFERENCE = ROOT / "skills/springbrand-action-api/references/action-discovery.md"
ROUTING_CORPUS = ROOT / "docs/routing-evaluation-corpus.md"
CURSOR_MIRROR = ROOT / "plugins/springbrand/skills/springbrand-action-api"
WORKBUDDY_MIRROR = ROOT / "plugins/springbrand-workbuddy/skills/springbrand-action-api"

QA_INTENT = "生成土豆番茄大战的漫画"
QA_NORMALIZED = "Text to Image"
XHS_QA_INTENT = "用XHS搜索最近一个月关于人机恋的热门笔记"
XHS_QA_NORMALIZED = "Xiaohongshu Note Search"


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
    assert "cleaned, faithful task-level `intent`" in skill
    assert "never the brand word" in skill


def test_field_name_is_snake_case_not_camel_case() -> None:
    reference = normalized(REFERENCE)
    assert "normalized_intent" in reference
    assert "takes **camelCase** `normalizedIntent`" in reference, "the field-name trap must name both casings explicitly"
    assert "Never carry the field name across domains" in reference
    skill = normalized(SKILL)
    assert "normalized_intent" in skill
    assert "normalizedIntent" not in skill


def test_xhs_request_uses_catalog_facing_discovery_terms() -> None:
    blocks = json_blocks(REFERENCE.read_text())
    matches = [body for body in blocks if body.get("intent") == XHS_QA_INTENT]
    assert matches == [
        {
            "intent": XHS_QA_INTENT,
            "normalized_intent": XHS_QA_NORMALIZED,
            "locale": "zh-CN",
        }
    ]
    body = matches[0]
    validate_match_input(body)
    normalized_intent = body["normalized_intent"].lower()
    for excluded in ("springbrand", "api", "人机恋", "month", "summar", "keyword"):
        assert excluded not in normalized_intent


def test_platform_aliases_emit_one_canonical_form() -> None:
    fixtures = [body for body in json_blocks(REFERENCE.read_text()) if body.get("fixture") == "alias_cases"]
    assert len(fixtures) == 1
    cases = fixtures[0]["cases"]
    assert {case["input"]: case["canonical"] for case in cases} == {
        "xhs": "Xiaohongshu",
        "XHS": "Xiaohongshu",
        "小红书": "Xiaohongshu",
        "RedNote": "Xiaohongshu",
    }
    for case in cases:
        assert case["normalized_intent"] == "Xiaohongshu Note Search"
    reference = normalized(REFERENCE).lower()
    assert "emit one canonical form" in reference
    assert "do not fan out multiple match calls" in reference


def test_candidate_selection_uses_hard_compatibility_constraints() -> None:
    reference = normalized(REFERENCE)
    for constraint in (
        "supplier, only when explicitly requested",
        "platform/product",
        "operation",
        "object or modality",
    ):
        assert constraint in reference
    assert "first candidate in the returned order that satisfies every applicable hard constraint" in reference
    assert "do not invent a second score" in reference
    fixtures = [body for body in json_blocks(REFERENCE.read_text()) if body.get("fixture") == "xhs_candidate_compatibility"]
    assert len(fixtures) == 1
    fixture = fixtures[0]
    assert fixture["constraints"] == {"platform": "Xiaohongshu", "operation": "search", "object": "note"}
    candidates = fixture["ordered_candidates"]
    compatible = [candidate for candidate in candidates if candidate["compatible"]]
    assert compatible[0]["actionId"] == "action.tikhub.xhs-search-notes"
    assert [candidate["title"] for candidate in candidates if not candidate["compatible"]] == [
        "TikHub TikTok Search",
        "TikHub X Search",
        "Apify Keyword Search Volume",
        "TikHub Xiaohongshu User Profile",
        "TikHub Xiaohongshu Note Comments",
        "TikHub Xiaohongshu Note Details",
    ]


def test_list_contract_and_bounded_inventory_recovery_are_pinned() -> None:
    reference = normalized(REFERENCE)
    for contract in (
        "optional `cursor` | string | 1–2048 characters",
        "optional `limit` | integer | 1–100; default 20",
        "`capabilities[]`",
        "`total`",
        "`complete`",
        "`next_cursor`",
        "exact API Service, Supplier, and Action IDs",
    ):
        assert contract in reference
    assert "`action_list_capabilities({ limit: 100 })`" in reference
    assert "continue with `next_cursor` page by page" in reference
    assert "until a compatible candidate is found or the inventory is complete" in reference
    assert "call `action_get_capability` with the entry's exact `actionId`" in reference
    assert "do not invent relevance scores" in reference
    assert "does not authorize execution" in reference


def test_skill_routes_every_discovery_entry_and_recovery_outcome() -> None:
    skill = normalized(SKILL)
    for route in (
        "existing execution ID → `action_get_execution`",
        "exact Action ID → `action_get_capability`",
        "explicit inventory browsing → `action_list_capabilities`",
        "clear task → one `action_match_capabilities` call",
        "compatible candidate → exact Get",
        "malformed non-English body → repair and rematch once",
        "tool or provider failure → report the failure",
        "well-formed `no_match` or no compatible candidate → one bounded inventory-recovery traversal",
    ):
        assert route in skill
    assert "A compatible candidate prevents List recovery even when `complete: false`" in skill


def test_routing_corpus_covers_compatibility_and_inventory_recovery() -> None:
    corpus = normalized(ROUTING_CORPUS)
    assert "SpringBrand 用xhs有关的api给我查查人机恋最近一个月比较火的在讨论什么，总结" in corpus
    assert "Xiaohongshu Note Search" in corpus
    assert "action.tikhub.xhs-search-notes" in corpus
    assert "higher-ranked incompatible" in corpus
    assert "one bounded Action Inventory recovery traversal" in corpus
    assert "compatible candidate prevents List recovery" in corpus
    assert "Malformed normalization repairs Match once" in corpus
    assert "transport, OAuth, permission, schema, and provider errors never trigger List" in corpus


def test_empty_result_semantics_are_pinned() -> None:
    skill = normalized(SKILL)
    assert "malformed body, not a no-match" in skill
    assert "fix the body and rematch once" in skill
    reference = normalized(REFERENCE)
    for outcome in ("Malformed body", "Genuine no-match", "Provider failure"):
        assert outcome in reference, outcome
    assert "Never tell the user nothing fits from a malformed body" in reference
    assert "Exactly one well-formed rematch is the ceiling" in reference
    assert "one recovery traversal, not a second semantic Match" in reference
    assert "stays browse-only" not in reference
    assert "proceed to bounded inventory recovery" in reference


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


def test_capability_label_and_modality_guidance_is_present() -> None:
    reference = normalized(REFERENCE)
    assert "compact catalogue label" in reference
    assert "text-to-image" in reference and "image-to-image" in reference
    assert "compatibility filtering, not a new ranking" in reference


def main() -> None:
    test_mirrors_are_byte_equivalent()
    test_skill_points_to_reference_before_any_body()
    test_chinese_intent_produces_one_normalized_match_body()
    test_field_name_is_snake_case_not_camel_case()
    test_xhs_request_uses_catalog_facing_discovery_terms()
    test_platform_aliases_emit_one_canonical_form()
    test_candidate_selection_uses_hard_compatibility_constraints()
    test_list_contract_and_bounded_inventory_recovery_are_pinned()
    test_skill_routes_every_discovery_entry_and_recovery_outcome()
    test_routing_corpus_covers_compatibility_and_inventory_recovery()
    test_empty_result_semantics_are_pinned()
    test_complete_semantics_are_documented()
    test_output_contract_is_exact()
    test_capability_label_and_modality_guidance_is_present()
    print("action discovery fixtures: ok")


if __name__ == "__main__":
    main()
