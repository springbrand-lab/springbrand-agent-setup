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
ALIASES = ROOT / "skills/springbrand-action-api/references/action-aliases.md"
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


def markdown_section(text: str, heading: str) -> str:
    marker = f"## {heading}\n"
    assert marker in text, f"missing Markdown section: {heading}"
    section = text.partition(marker)[2]
    return section.partition("\n## ")[0]


def alias_rows(heading: str) -> dict[str, dict[str, set[str]]]:
    section = markdown_section(ALIASES.read_text(), heading)
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        canonical = re.findall(r"`([^`]+)`", cells[0])[0]
        rows[canonical] = {
            "aliases": set(re.findall(r"`([^`]+)`", cells[1])),
            "scope": set(re.findall(r"`([^`]+)`", cells[2])),
        }
    return rows


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
    canonical_aliases = ALIASES.read_bytes()
    for mirror in (CURSOR_MIRROR, WORKBUDDY_MIRROR):
        assert (mirror / "SKILL.md").read_bytes() == canonical_skill
        assert (mirror / "references/action-discovery.md").read_bytes() == canonical_reference
        assert (mirror / "references/action-aliases.md").read_bytes() == canonical_aliases


def test_skill_points_to_reference_before_any_body() -> None:
    skill = normalized(SKILL)
    assert "Before constructing any match body, read [references/action-discovery.md](references/action-discovery.md)" in skill
    assert "supplier, platform/product, model, object, or operation alias" in skill
    alias_pointer = "[references/action-aliases.md](references/action-aliases.md)"
    first_match_body = "For a clear task, call `action_match_capabilities` once"
    assert alias_pointer in skill
    assert skill.index(alias_pointer) < skill.index(first_match_body)


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


def test_alias_inventory_snapshot_is_complete_and_honest() -> None:
    aliases = normalized(ALIASES)
    assert "2026-09-05" in aliases
    assert "52" in aliases and "complete: true" in aliases
    assert "public Action Inventory fields" in aliases
    assert "does not expose private aliases or tags" in aliases
    assert "temporary Agent-side" in aliases

    coverage = markdown_section(ALIASES.read_text(), "Inventory coverage")
    counts = {
        match.group(1): int(match.group(2))
        for match in re.finditer(r"\| `([^`]+)` \| (\d+) \|", coverage)
    }
    assert counts == {
        "supplier.frank.apify": 9,
        "supplier.frank.apollo-io": 2,
        "supplier.frank.elevenlabs": 1,
        "supplier.frank.exa": 2,
        "supplier.frank.firecrawl": 3,
        "supplier.frank.kie-ai-image": 5,
        "supplier.frank.kie-ai-video": 3,
        "supplier.frank.people-data-labs": 2,
        "supplier.frank.serper": 5,
        "supplier.frank.tikhub": 20,
    }
    assert sum(counts.values()) == 52


def test_alias_table_covers_every_current_service_family() -> None:
    rows = alias_rows("Service and supplier aliases")
    supplier_ids = set().union(*(row["scope"] for row in rows.values()))
    assert supplier_ids == {
        "supplier.frank.apify",
        "supplier.frank.apollo-io",
        "supplier.frank.elevenlabs",
        "supplier.frank.exa",
        "supplier.frank.firecrawl",
        "supplier.frank.kie-ai-image",
        "supplier.frank.kie-ai-video",
        "supplier.frank.people-data-labs",
        "supplier.frank.serper",
        "supplier.frank.tikhub",
    }
    assert rows["Apollo"]["aliases"] >= {"Apollo.io", "Apollo IO"}
    assert rows["ElevenLabs"]["aliases"] >= {"Eleven Labs", "11Labs"}
    assert rows["People Data Labs"]["aliases"] >= {"PDL", "PeopleDataLabs"}
    assert rows["TikHub"]["aliases"] >= {"Tik Hub"}


def test_platform_aliases_emit_catalogue_canonical_forms() -> None:
    rows = alias_rows("Platform and product aliases")
    assert rows["Xiaohongshu"]["aliases"] >= {
        "xhs",
        "小红书",
        "RedNote",
        "Red Note",
        "little red book",
    }
    assert rows["X"]["aliases"] >= {"Twitter", "推特", "X.com"}
    assert rows["Instagram"]["aliases"] >= {"IG", "Insta"}
    assert rows["YouTube"]["aliases"] >= {"YT", "油管"}
    assert rows["Google Maps"]["aliases"] >= {"Google Map", "GMaps", "谷歌地图"}


def test_douyin_and_tiktok_are_not_collapsed() -> None:
    rows = alias_rows("Platform and product aliases")
    assert "抖音" in rows["Douyin"]["aliases"]
    assert "抖音" not in rows["TikTok"]["aliases"]
    assert "抖音国际版" in rows["TikTok"]["aliases"]
    aliases = normalized(ALIASES)
    assert "no dedicated Douyin Action" in aliases
    assert "never silently rewrite `douyin` to `tiktok`" in aliases.lower()


def test_model_and_operation_aliases_cover_current_modalities() -> None:
    models = alias_rows("Model and vendor aliases")
    assert models["Seedream"]["aliases"] >= {"即梦", "即梦AI"}
    assert models["Seedream 5 Lite"]["aliases"] >= {"Seedream5 Lite"}
    assert models["Nano Banana 2"]["aliases"] >= {"NanoBanana2", "Nano Banana"}
    assert models["GPT Image 2"]["aliases"] >= {"GPT-Image-2", "GPT Image2"}
    assert models["Seedance 2.0"]["aliases"] >= {"Seedance 2", "Seedance2"}

    vocabulary = alias_rows("Object, modality, and operation aliases")
    assert vocabulary["Text to Speech"]["aliases"] >= {"TTS", "text2speech", "文本转语音"}
    assert vocabulary["Text to Image"]["aliases"] >= {"T2I", "txt2img", "文生图"}
    assert vocabulary["Image to Image"]["aliases"] >= {"I2I", "img2img", "图生图"}
    assert vocabulary["Text to Video"]["aliases"] >= {"T2V", "txt2vid", "文生视频"}
    assert vocabulary["Image to Video"]["aliases"] >= {"I2V", "img2vid", "图生视频"}
    assert vocabulary["Search"]["aliases"] >= {"find", "lookup", "搜索", "检索"}

    aliases = normalized(ALIASES).lower()
    assert "emit one canonical form" in aliases
    assert "do not fan out multiple match calls" in aliases
    assert "longest, most specific alias" in aliases


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
    test_alias_inventory_snapshot_is_complete_and_honest()
    test_alias_table_covers_every_current_service_family()
    test_platform_aliases_emit_catalogue_canonical_forms()
    test_douyin_and_tiktok_are_not_collapsed()
    test_model_and_operation_aliases_cover_current_modalities()
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
