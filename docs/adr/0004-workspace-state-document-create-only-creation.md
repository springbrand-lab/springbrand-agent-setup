# Carry creation workflow state in a workspace State Document; treat MCP creation as create-only

The Platform Skill runs a five-stage creation pipeline (goal → resource showcase → generation → upload → publish) whose state must survive across sessions for ordinary users, while Ask SpringBrand must report workflow position without ever calling MCP. Verified sp-platform contracts make MCP creation create-only: each upload with a new idempotency key creates a new Creation at v1, the same key replays the same Creation, and no MCP capability appends a version to an existing Creation or withdraws a publication.

## Decisions

- **State Document.** Workflow state lives in a human-readable Markdown record inside the Artifact Workspace (proposed convention `springbrand-state.md`), never included in upload files. It records the current step, the Plugin used, upload/publication pointers (`artifactId`, `versionNumber`, `public_url`), and the next action. This amends ADR-0002's "state records embedded in the user's artifact documents" wording to "carried in the Artifact Workspace"; the substance is unchanged — Ask SpringBrand reads files and never calls MCP.
- **Creation List as recovery and selection, not a substitute for state.** `springbrand.creations.list` (added to the dev registry 2026-09-01, eleventh capability) lets the Platform Skill re-derive publish pointers (`artifactId`, `versionNumber`, publication status) from the user's account and lets the user publish an existing Creation directly. Ask SpringBrand still never calls it; the State Document remains Ask's artifact-side position source.
- **Ask SpringBrand stays non-executing.** Position reporting reads the conversation and the State Document only. Pointer verification (entitlement, added state, execution status) is always the owning Domain Skill's job via MCP.
- **Update story.** Via the Platform domain, "update a published Creation" means: generate the new content, upload it as a new Creation, publish the new Creation — and say plainly that the previous public link remains live and withdrawal is a platform-web action. The Skill never presents an update as an in-place revision.
- **Pre-upload self-check.** The Agent validates the finished Artifact against the upload admission rules before upload, auto-fixes safe mechanical problems, and gives concrete fix suggestions for the rest; users never debug admission errors themselves.

## Consequences

- Ask SpringBrand gains a second position source (the State Document) without gaining any execution ability; ADR-0002's non-execution contract is unchanged in substance.
- The Canonical Skill Set validator keeps its named-list form, so a future artifact-creation helper Skill could be added without a package-contract change; this design deliberately ships none (standard-format guidance lives inside the Platform Skill).
- Plugin-distribution action components (`usageMode: gateway_action`) are handed to the Action API Skill by explicit Domain Transition; the Skill text for that path stays unfrozen until the Gateway implements distribution-driven action references and mcp-gateway Issue 10 real-OAuth E2E lands.
