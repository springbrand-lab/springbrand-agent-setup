#!/usr/bin/env python3
"""Check that the Stage 4 upload golden path and guardrails are present.

Issue #74: the canonical Platform Skill and both distribution mirrors must
carry the ordered upload procedure, the exact capability-reference call
shape, MCP-only transport rules, same-key retry semantics, the Host-size
failure branch, and the State Document persistence guidance — and must not
carry model-specific wording or the retired bare-name call shape.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MIRRORS = (
    "skills/springbrand-platform/SKILL.md",
    "plugins/springbrand/skills/springbrand-platform/SKILL.md",
    "plugins/springbrand-workbuddy/skills/springbrand-platform/SKILL.md",
)

REQUIRED_PHRASES = (
    # Ordered positive procedure (golden path)
    "run the normal procedure below",
    "one Creation and one initial",
    "Identify the files",
    "Self-check",
    "Prepare the key",
    "If the State Document already contains",
    "Encode",
    "base64 < FILE",
    "first command output as-is",
    "following arguments",
    "content_base64",
    "Call once",
    "Verify and record",
    # Exact capability-reference call shape (verified contract)
    "platform:springbrand@0:springbrand.creations.upload",
    'idempotency_key: "<uuid>"',
    "entry_path: \"<entry path>\"",
    "State Document `artifactId` (mapped from response `artifact_id`)",
    # Display limits are not argument limits
    "never what tool arguments may *carry*",
    # Host-size failure branch (admission limit vs Host carrying capacity)
    "Platform admission limit is 20 MiB decoded",
    "Never infer a Host limit from display truncation",
    "request-size rejection",
    # MCP-only transport
    "The MCP entry is the only sanctioned transport",
    "never extract, inspect, or reuse OAuth credentials",
    "directly over HTTP",
    "another CLI or agent",
    "never chunk or stitch",
    # Same-key bounded retry
    "replay **once** with the same",
    "same capability reference, identical body",
    "Never generate a new key for this replay",
    # Failure branches
    "ask the user to reauthorize",
    "write `upload_attempt: failed`",
    "obtain upload confirmation again",
    "never report it as a `no_match`",
    # State Document persistence
    "upload_idempotency_key",
    "upload_attempt: pending",
    "outcome_unknown",
)

RETIRED_PHRASES = (
    # Retired bare-name call shape (QA handoff error)
    'name: "springbrand.creations.upload"',
    # Invalid optional-field notation that an Agent could copy literally
    "entry_path?",
    # Rejected premise: current Hosts expose no local-file argument binding.
    "binding mechanism",
    # Model- and host-specific wording never belongs in the Skill
    "GLM",
    "Flash",
    "Devin",
    "Codex",
)


def main() -> None:
    canonical = (ROOT / MIRRORS[0]).read_bytes()
    for relative in MIRRORS:
        skill = (ROOT / relative).read_text()
        normalized = " ".join(skill.split())
        for phrase in REQUIRED_PHRASES:
            assert phrase in normalized, f"{relative}: missing {phrase!r}"
        for phrase in RETIRED_PHRASES:
            assert phrase not in normalized, f"{relative}: retired phrase {phrase!r}"
        assert (ROOT / relative).read_bytes() == canonical, f"{relative}: mirror drift"

        stage4 = skill.split("### Stage 4 — Upload", 1)[1].split("### Stage 5 — Publish", 1)[0]
        markers = (
            "Identify the files",
            "Self-check",
            "Prepare the key",
            "Encode",
            "Call once",
            "Verify and record",
        )
        positions = [stage4.index(marker) for marker in markers]
        assert positions == sorted(positions), f"{relative}: upload steps out of order"

        block_start = stage4.index("```text")
        block_end = stage4.index("```", block_start + len("```text"))
        call_block = stage4[block_start:block_end]
        assert call_block.index('name: "platform:springbrand@0:springbrand.creations.upload"') < call_block.index("body:"), f"{relative}: capability reference is misplaced"
        assert call_block.index('idempotency_key: "<uuid>"') < call_block.index("body:"), f"{relative}: idempotency key is not top-level"
        assert "entry_path?" not in call_block, f"{relative}: invalid optional-field syntax"


if __name__ == "__main__":
    main()
