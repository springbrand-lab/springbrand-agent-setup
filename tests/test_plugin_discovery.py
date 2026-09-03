#!/usr/bin/env python3
"""Behavior and packaging fixtures for Platform Plugin discovery (Issue #77).

The agent-facing contract lives in the canonical Platform Skill and its
on-demand reference. These fixtures pin the routing decision tree, the English
normalizedIntent contract, the one-Match rule, List view selection, error
semantics, the catalog.match boundary, and the mirror byte-equivalence.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/springbrand-platform/SKILL.md"
REFERENCE = ROOT / "skills/springbrand-platform/references/plugin-discovery.md"
CURSOR_MIRROR = ROOT / "plugins/springbrand/skills/springbrand-platform"
WORKBUDDY_MIRROR = ROOT / "plugins/springbrand-workbuddy/skills/springbrand-platform"

RETIRED_PHRASES = (
    "springbrand.catalog.match",
    "springbrand.resources.match",
    "springbrand-plugin-discovery",
    "Do not Match again",
    "follow-up to an existing SpringBrand match",
    "kind = plugin",
    "kind = api_service",
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text().split())


def json_blocks(text: str) -> list:
    return [json.loads(block) for block in re.findall(r"```json\n(.*?)```", text, re.DOTALL)]


def validate_match_input(body: dict) -> None:
    assert isinstance(body, dict)
    assert set(body) <= {"intent", "normalizedIntent", "locale", "limit"}, body
    assert set(body) >= {"intent"}
    assert isinstance(body["intent"], str) and 1 <= len(body["intent"].strip()) <= 4000
    if "normalizedIntent" in body:
        value = body["normalizedIntent"]
        assert isinstance(value, str) and 1 <= len(value.strip()) <= 1000
    if "locale" in body:
        value = body["locale"]
        assert isinstance(value, str) and 2 <= len(value.strip()) <= 35
    if "limit" in body:
        value = body["limit"]
        assert isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 8


def validate_list_input(body: dict) -> None:
    assert isinstance(body, dict)
    assert set(body) <= {"view", "query", "category", "page", "pageSize"}, body
    if "view" in body:
        assert body["view"] in {"usable", "marketplace", "my", "featured"}
    if "query" in body:
        assert isinstance(body["query"], str) and len(body["query"].strip()) <= 200
    if "category" in body:
        assert isinstance(body["category"], str) and len(body["category"].strip()) <= 128
    if "page" in body:
        assert isinstance(body["page"], int) and not isinstance(body["page"], bool) and body["page"] >= 1
    if "pageSize" in body:
        value = body["pageSize"]
        assert isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 100


def test_mirrors_are_byte_equivalent() -> None:
    canonical_skill = SKILL.read_bytes()
    canonical_reference = REFERENCE.read_bytes()
    for mirror in (CURSOR_MIRROR, WORKBUDDY_MIRROR):
        assert (mirror / "SKILL.md").read_bytes() == canonical_skill
        assert (mirror / "references/plugin-discovery.md").read_bytes() == canonical_reference


def test_skill_points_to_reference_before_any_body() -> None:
    skill = normalized(SKILL)
    assert "Before constructing any Match or List body, read [references/plugin-discovery.md](references/plugin-discovery.md)" in skill
    assert "## Match or List: the routing decision tree" in normalized(SKILL) or "### Match or List: the routing decision tree" in skill


def test_chinese_brand_prefixed_intent_produces_one_match_body() -> None:
    blocks = json_blocks(REFERENCE.read_text())
    qa_examples = [body for body in blocks if body.get("intent") == "用springbrand帮我做电子礼物"]
    assert len(qa_examples) == 2, "one valid and one rejected body for the QA request"
    valid = [body for body in qa_examples if body.get("normalizedIntent") == "digital gift"]
    rejected = [body for body in qa_examples if body.get("normalizedIntent") == "电子礼物"]
    assert len(valid) == 1 and len(rejected) == 1
    body = valid[0]
    validate_match_input(body)
    validate_match_input(rejected[0])
    assert rejected[0]["normalizedIntent"] == "电子礼物", "the rejected example must carry untranslated Chinese"
    assert body["normalizedIntent"] == "digital gift"
    assert "springbrand" not in body["normalizedIntent"].lower()
    assert body["normalizedIntent"].isascii(), "normalizedIntent must be English"
    assert body["locale"] == "zh-CN"
    assert body["limit"] == 5
    skill = normalized(SKILL)
    assert "intent` carries the user's request faithfully" in skill
    assert "never the brand word, never untranslated Chinese" in skill


def test_clear_english_request_produces_one_match_call() -> None:
    skill = normalized(SKILL)
    assert "exactly **one** `springbrand.plugins.match` request" in skill
    assert "Never split the intent into multiple Match requests" in skill
    assert "never fire a second Match to try another keyword" in skill
    assert "One request, no keyword fan-out." in skill
    reference = normalized(REFERENCE)
    assert "Issue **exactly one** Match request per user request" in reference
    assert "no defined union semantics" in reference


def test_list_examples_respect_bounds() -> None:
    skill = normalized(SKILL)
    assert "view=marketplace" in skill
    assert "view=featured" in skill
    assert "view=my" in skill
    assert "Never use `view=usable` for Plugin discovery" in skill
    assert "it is a **mixed view**" in normalized(REFERENCE)
    blocks = [body for body in json_blocks(REFERENCE.read_text()) if "view" in body]
    schema_valid = []
    for body in blocks:
        try:
            validate_list_input(body)
        except AssertionError:
            continue
        schema_valid.append(body)
    marketplace_valid = [body for body in schema_valid if body["view"] == "marketplace"]
    assert len(marketplace_valid) == 1, "exactly one valid marketplace List body"
    body = marketplace_valid[0]
    assert body["page"] == 1
    assert 1 <= body["pageSize"] <= 100
    usable_examples = [body for body in blocks if body.get("view") == "usable"]
    assert len(usable_examples) == 1, "usable appears only as the rejected policy example"
    out_of_bounds = {"view": "marketplace", "page": 0, "pageSize": 500}
    try:
        validate_list_input(out_of_bounds)
    except AssertionError:
        pass
    else:
        raise AssertionError("out-of-bounds List body must fail the contract")


def test_invented_match_fields_are_rejected() -> None:
    invented = {"intent": "digital gift", "keyword": "gift", "limit": 20}
    try:
        validate_match_input(invented)
    except AssertionError:
        pass
    else:
        raise AssertionError("invented Match fields must fail the contract")


def test_match_list_and_error_outcomes_stay_distinct() -> None:
    skill = normalized(SKILL)
    assert "Preserve the returned order exactly." in skill
    assert "Keep every ID exact." in skill
    assert "error is not a no-match" in skill
    reference = normalized(REFERENCE)
    assert "Keep it exact." in reference
    assert "Preserve the returned order exactly" in reference
    for outcome in ("matches_found", "no_match", "Valid empty List page", "Provider failure"):
        assert outcome in reference, outcome
    assert "never report a failure as \"nothing fits\"" in reference or "Never report a failure as \"nothing fits\"" in reference
    assert "never trigger the List fallback for one" in reference


def test_catalog_match_boundary_is_documented_without_aliasing() -> None:
    reference = normalized(REFERENCE)
    assert "springbrand.plugins.match" in reference
    assert "springbrand.catalog.match" in reference
    assert "never alias one to the other" in reference
    assert 'kind: "plugin"' in reference
    assert 'kind: "api_service"' in reference
    assert "nested under `access`" in reference
    assert "Domain Transition to the `springbrand-action-api` Skill" in reference
    skill = normalized(SKILL)
    for phrase in RETIRED_PHRASES:
        assert phrase not in skill, f"retired phrase in canonical Skill: {phrase!r}"
    assert "mixed-Catalog Match boundary" in skill


def test_match_output_contract_is_exact() -> None:
    reference = REFERENCE.read_text()
    for field in ("`match_id`", "`plugin_id`", "`user_state`", "`score`", "`matched_on`"):
        assert field in reference, field
    assert "`matches_found`" in reference and "`no_match`" in reference


def main() -> None:
    test_mirrors_are_byte_equivalent()
    test_skill_points_to_reference_before_any_body()
    test_chinese_brand_prefixed_intent_produces_one_match_body()
    test_clear_english_request_produces_one_match_call()
    test_list_examples_respect_bounds()
    test_invented_match_fields_are_rejected()
    test_match_list_and_error_outcomes_stay_distinct()
    test_catalog_match_boundary_is_documented_without_aliasing()
    test_match_output_contract_is_exact()
    print("plugin discovery fixtures: ok")


if __name__ == "__main__":
    main()
