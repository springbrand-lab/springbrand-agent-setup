#!/usr/bin/env python3
"""Check the unified-Meta-Tool upload sequence and its write guardrails."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = (
    "skills/springbrand-platform/SKILL.md",
    "plugins/springbrand/skills/springbrand-platform/SKILL.md",
    "plugins/springbrand-workbuddy/skills/springbrand-platform/SKILL.md",
)

REQUIRED_PHRASES = (
    "Discover or reuse the upload operation",
    "Inspect its current contract",
    "Build from the current schema",
    "Prepare durable run state",
    "upload_idempotency_key",
    "upload_attempt: pending",
    "exact opaque Tool ID",
    "stable idempotency key",
    "Execute once",
    "Verify and record",
    "upload_attempt: outcome_unknown",
    "outcome unknown is never auto-retried",
    "one Creation per file",
    "only sanctioned Platform transport",
    "direct HTTP request",
    "never as no-match",
)

RETIRED_PHRASES = (
    "platform_execute_capability",
    "platform:springbrand@0:",
    'name: "springbrand.creations.upload"',
    "replay **once**",
    "same capability reference",
    "entry_path?",
    "GLM",
    "Devin",
    "Codex",
)


def main() -> None:
    canonical = (ROOT / COPIES[0]).read_bytes()
    for relative in COPIES:
        skill = (ROOT / relative).read_text()
        normalized = " ".join(skill.split())
        for phrase in REQUIRED_PHRASES:
            assert phrase in normalized, f"{relative}: missing {phrase!r}"
        for phrase in RETIRED_PHRASES:
            assert phrase not in normalized, f"{relative}: retired phrase {phrase!r}"
        assert (ROOT / relative).read_bytes() == canonical, f"{relative}: mirror drift"

        stage4 = skill.split("### Stage 4 — Upload", 1)[1].split("### Stage 5 — Publish", 1)[0]
        markers = (
            "Discover or reuse the upload operation",
            "Build from the current schema",
            "Prepare durable run state",
            "Execute once",
            "Verify and record",
        )
        positions = [stage4.index(marker) for marker in markers]
        assert positions == sorted(positions), f"{relative}: upload steps out of order"


if __name__ == "__main__":
    main()
