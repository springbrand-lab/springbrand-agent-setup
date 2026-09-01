# Platform Workflow Design Record (Issue #52)

**Status: IN PROGRESS — grilling/design session record. Decisions confirmed by the owner are marked ✅. This file changes no product files (Skills, Hooks, manifests, tests, INSTALL). Final session output: `CONTEXT.md` vocabulary / ADR updates as needed, plus the #52 closing comment carrying the Platform Skill workflow-text requirements (input to #56).**

Date: 2026-09-01 (Asia/Shanghai)
Session: grill-with-docs design session for #52 (Platform workflow, state tracking, artifact publication format).
Parent spec: #51 (three-domain architecture). ADRs: `docs/adr/0002`, `docs/adr/0003`.

## Sources of truth (referenced, not copied)

- Gateway: deployed `/mcp/platform` registry — **eleven capabilities** since the 2026-09-01 dev deployment of `springbrand.creations.list` (PR #39; ten before that); `mcp-gateway/.scratch/mcp-domain-executors/spec.md`; `mcp-gateway/docs/mcp-domain-executor-architecture.md`; Gateway ADR-0013 (Public Contract Passthrough).
- Implemented contracts verified 2026-09-01 from mcp-gateway code (`src/springbrand.ts`, `src/mcp.ts`, `test/platform-domain.test.ts`) — summarized in Appendix A.
- sp-platform creation upload admission requirements: verified 2026-09-01 (Appendix B).
- Current-state references (being replaced, not the target shape): `skills/springbrand/SKILL.md`, `docs/routing-evaluation-corpus.md`.

## Confirmed decisions

### D1 ✅ Platform discovery semantics (Round 1, Q1)

- Four route classes carry over from the retired `springbrand-plugin-discovery`: DIRECT / REUSE / BROWSE / MATCH.
- `springbrand.plugins.match` is the primary natural-language Plugin discovery entry for the Platform domain. Input: `intent` (required), `normalizedIntent?`, `locale?`, `limit?` (default 5, max 8). Outcome: `matches_found` / `no_match` with `match_id`; candidates are Plugin-only (`plugin_id`, `title`, `summary`, `user_state`, `score`, `matched_on`).
- #42 outcome rules carry over: preserve Platform order and exact IDs; no reranking, no second threshold; errors ≠ `no_match`.
- **Amendment (owner, 2026-09-01)**: after a genuine `no_match`, the Skill may run one `springbrand.plugins.list` search (`query`) as a fallback while the Marketplace catalogue is small. This deliberately amends the old "List is not a Match pre-step or `no_match` fallback" rule. Transport/OAuth/service errors still never trigger the List fallback.
- No `kind` branching: the Platform match is Plugin-only; `api_service` matching belongs exclusively to the Action API domain.

### D2 ✅ Plugin lifecycle trunk and acquisition (Round 1, Q2)

- Trunk: `match` → `get` (detail) → `add` → `get_distribution` → use.
- `user_state` branches (already present in match candidates, so state is known before `get`):
  - `added` → `get_distribution` when needed for use;
  - `entitled_not_added` → ask the user, then `add`, then `get_distribution`;
  - `not_entitled` → `get` detail → the user completes acquisition on the Platform side themselves (no MCP acquire capability exists; no sp-platform changes allowed) → re-`get` to confirm `user_state` flipped → ask → `add`.
- Confirmation gates: `add` always requires explicit user confirmation; the Agent never pays or completes acquisition on the user's behalf. Acquisition details (`status`, `price?`) are read from the `add` response; `get` does not return acquisition info.

### D3 ✅ Auxiliary capabilities placement (Round 1, Q3)

- `remove` (explicit user request + confirmation gate) and `rate` (explicit user request) are user-initiated maintenance actions, never automatic.
- `get_use_case` placement: decision pending (D10); facts now available (input `useCaseId` from `plugins.get` `use_cases[]`; returns a guided conversation `{id, title, plugin, conversation}`).

### D4 ✅ Creation loop shape (Round 1, Q4)

- Two steps with independent confirmation gates: `creations.upload` (creates a **private** artifact; confirm first) → `creations.publish` (always public — the contract has no visibility field; explicit confirmation, never automatic).
- "Uploaded but not published" is a valid resting state.
- Versioning: `publish` takes `{artifactId, versionNumber}`; the upload response carries `current_version` / `latest_version` / `publication_version`. **Verified (sp-platform, 2026-09-01, see Appendix B)**: the MCP upload route is create-only — a new `idempotency-key` creates a new artifact at v1; the same key deterministically replays the same artifact. There is no MCP path to append a version to an existing artifact (version appending exists only on the Chat `save_creation` path) and no MCP withdraw capability (withdraw is not in the eleven-capability registry). Consequence for the Skill: "update" = produce the new content, upload as a **new artifact**, publish the new artifact; the previous public link remains live; the Skill must say this plainly. `publish` `versionNumber` is always 1 for MCP-created artifacts.
- `idempotency_key` is accepted for `creations.upload` only.

## Confirmed decisions — Rounds 2–3 (2026-09-01)

### D5 ✅ Creation pipeline (Q7, refined Round 3)

Five stages, each ending in a plain-language checkpoint; the user confirms/chooses/reviews, the Agent does the heavy lifting (semi-automatic pipeline):

1. **明确目标** — the Agent restates the task and the deliverable in plain language.
2. **资源展示（必经）** — the Agent searches Plugins with the user's intent: `plugins.match` (preserve Platform order, present the best match plus alternatives); on a genuine `no_match`, one `plugins.list` search as fallback (per D1). Results are presented so the user sees which Marketplace resources could complete the task; the user chooses to adopt one or decline. If the user declines — or opts out upfront — generation proceeds natively. This stage always runs once the Platform pipeline is engaged; it does not change when the Platform Skill triggers (routing stays #51's table: ordinary creation with no SpringBrand intent is native and never reaches this pipeline).
3. **生成产物** — the Agent generates in the standard format (D9) from the start; if a Plugin was adopted, `get_use_case` may be fetched (optional, D10) to turn the Plugin's capability into generation guidance; the user reviews and requests changes. Stage exit = the pre-upload self-check gate (D9) passes.
4. **上传**（确认门）— `creations.upload` → `artifact_id`, artifact is private.
5. **发布**（确认门）— `creations.publish` → `public_url`. Two entry paths into this stage: (a) the artifact just uploaded in stage 4 (pointers come from the upload response / State Document); (b) **an existing Creation from the user's account** (D15): `creations.list` → present the user's Creations with versions and publication status in plain language → user selects → confirm → publish.

### D6 ✅ State record: Markdown state document (Q8)

- A dedicated **Markdown** state document travels with the artifact in its workspace (proposed convention, owner may veto: `springbrand-state.md` next to the artifact files; never included in upload `files[]`).
- Rationale: human-readable for ordinary users (they can read their own progress), and file-access only — Ask SpringBrand can read it without violating non-execution.
- Required content (owner-specified): which Plugin was used, current step, uploaded or not, and the post-upload publish parameters (`artifactId`, `versionNumber`).
- Additional fields (delegated by owner): `match_id`, `public_url` (after publish), `next_action`, `updated_at`, artifact shape (single-file / website bundle), `entry_path`, `title`, pointer to the workspace file list.
- #51/ADR-0002 wording amendment: "state records embedded in the user's artifact documents" → "state records carried in the artifact workspace (a Markdown state document alongside the artifact files)". Substance unchanged: Ask reads files, never MCP.

### D7 ✅ State model + Ask position mapping (Q9)

- Steps — creation: `created` → `uploaded` → `published`; plugin lifecycle: `matched` → `selected` → `added` → `distributed` → `in_use`.
- Ask SpringBrand: reads the state document + conversation context → reports position and the next step in plain language → recommends one Domain Skill → stops. No state document and no conversation pointers → quick-start mode or at most one clarifying question. Ask never verifies via MCP (verification is the Platform Skill's job, via `plugins.get` / `plugins.list view=my` / `creations.list` for publish-pointer recovery, D15).
- Exact Markdown shape is #56's detail.

### D8 ✅ No fifth Skill (Q10)

- Option (a): standard-format generation guidance lives inside the Platform Skill; pure creation with no SpringBrand intent stays native and triggers nothing. The list-based Canonical Skill Set validator keeps headroom for a future fifth Skill without a package-contract change.

### D9 ✅ Artifact standard format + pre-upload self-check (Q12)

- The two admissible shapes + whitelists + safety rules (Appendix B) are written into the Platform Skill as **generation-time hard requirements**: produce compliant artifacts from the start instead of discovering non-compliance at upload.
- **Pre-upload self-check gate**: before upload, the Agent checks the finished artifact against the admission checklist; safe mechanical problems are auto-fixed (e.g., add the declared `content_type: text/html` for a lone HTML file; materialize `data:` URLs into real bundle files); anything not auto-fixable gets a concrete, executable fix suggestion from the Agent. The user never has to debug admission errors themselves.

### D10 ✅ `get_use_case` placement (Q7)

- Optional, after a Plugin is adopted and before generation: fetch the use-case conversation to turn the Plugin's capability into generation guidance.

### D12 ✅ Update story presentation (Q13)

- Option (a): full support — new content → upload as a **new artifact** → publish the new artifact; plainly tell the user: this is a new entry, the previous public link remains live, and taking the old link down is a platform-web action (not reachable via MCP).

### D11 ✅ Plugin distribution action components → Domain Transition (Q14)

- When `get_distribution` returns components with `kind: "action"` and `usageMode: "gateway_action"`, the Platform Skill performs an explicit Domain Transition to the Action API Skill, which executes them as `action:springbrand@0:<id>` references. The Platform Skill never executes them itself (the Platform executor rejects `action:` references with `capability_domain_mismatch`) and never leaves the user to figure it out.
- The Gateway-side materialization of distribution-driven action references is not yet implemented (action-component-gateway planning); the Skill text for this path stays unfrozen until mcp-gateway Issue 10 real-OAuth E2E lands and must be marked accordingly for #56.

### D14 ✅ Skill authoring standard (Q15)

- Combined standard (option a), goal: the agent understands the system without confusion:
  - **agentskills.io open spec as the format base**: minimal frontmatter (`name`, `description` only), folder layout, progressive disclosure, body < 500 lines.
  - **skill-creator process + tooling as dev-time aid only**: init → draft → test → eval → iterate; `evals/evals.json` with/without comparisons; `package_skill.py` / `quick_validate.py` / eval-viewer. Never shipped in canonical assets.
  - **Codex-style descriptions**: concise, boundary-aware, front-loaded triggers; the "pushy description" advice (Anthropic skill-creator, agentskills.io) is rejected — routing precision outweighs under-triggering (#51).
  - **writing-for-agents as the writing-discipline layer**: context pointers, information hierarchy, completion criteria; its router-skill invocation model is not copied (Ask SpringBrand stays model-invocable per #51).
  - **Four custom hard rules no standard covers**: audience split (plain user-facing text vs agent-facing operational instructions); explicit MCP entry naming + no tool-name inference; workflow text derived only from verified contracts with unfrozen sections marked; Ask SpringBrand never executes.
- Recorded for #56's authoring requirements; no separate ADR (follows the #51 precedent of keeping the authoring-aid decision in the proposal record).

### D13 ✅ Action API Skill brief guidance (Q16, Q17)

- **User-visible flow (plain language)**: say what you want done → pick from available API services → confirm to execute (high risk disclosed first) → get the result.
- **Agent trunk (five steps)**:
  1. **Clarify intent** — restate the task in plain language; "continue the earlier execution" → REUSE, never rematch.
  2. **Find capability** — `match_capabilities` (faithful intent; `api_service` candidates only; preserve Platform order, no second threshold; **`complete: false` is reported honestly as "there may be more", never treated as `no_match`**); `list_capabilities` only for explicit browsing; REUSE over rediscovery.
  - **Read the contract** — `get_capability`: read `risk`, `input_schema`, `output_schema`; revision is informational only (no `expectedRevision`, none invented).
  - **Execute** (confirmation gate; `risk: high` disclosed first) — `execute_capability`: exact `action:springbrand@0:<actionId>` reference + schema-valid input + idempotency key; safe retries reuse the same reference, body, and idempotency key.
  - **Status and delivery** — only `succeeded` permits claiming completion (deliver json/text/file URL by type); `running` → poll `get_execution`; `failed` → retry only when `retryable: true`, finitely; `insufficient_credits` → tell the user to add Credits and start a new invocation (no auto-retry); `outcome_unknown` → never auto-retry; a `get_execution` tool error is a lookup failure, not an execution status.
- **Three entries**: direct / Ask handoff / **Platform Domain Transition** (D11 — arrives carrying the distribution component's action id, skips match, goes straight to contract → execute).
- **State policy**: conversation context is primary; cross-session = user restates pointers (`action_id` / `execution_id`) or a state document in a related artifact workspace (if one exists); Ask reads only, never queries; the Action API Skill verifies a known pointer via `get_execution`.
- Recorded in the #52 closing comment as a section labeled as input for #54 (Action API Skill authoring) as well.

### D15 ✅ `springbrand.creations.list` — account Creation listing (owner addition, 2026-09-01 dev deployment)

- **Verified contract (mcp-gateway dev, PR #39, deployed to `devconnector.springbrand.ai`)**: the Platform registry now has **eleven** capabilities — `springbrand.creations.list` joins `upload`/`publish`. Input is a **strict empty object** (any parameter → `invalid_arguments`); it calls the existing sp-platform `GET /api/creations` with no sp-platform changes. Output: `creations[]` — each item carries `artifact_id` (uuid) plus the projection fields (`title?`, `category?`, `status?`, `access_mode?`, `current_version?`, `latest_version?`, `versions[]`, timestamps) with safe passthrough; `risk: none`; 2 MiB response bound, never truncated; identity and secret-exclusion checks preserved; **excluded from Legacy `/mcp` discovery** (old Plugins unaffected); no DB migration, no deploy-config change.
- **Use 1 — publish-pointer recovery**: before publishing, if the necessary parameters (`artifactId` / `versionNumber`) are missing — no State Document, lost state doc, or a foreign artifact — the Platform Skill lists the user's Creations and identifies the target by title/category/time instead of blocking.
- **Use 2 — publish an existing Creation**: the user wants to publish something already in their account (created earlier via MCP or the Chat path) → `creations.list` → plain-language presentation of Creations, versions, and publication status → user selects the exact `artifactId` + `versionNumber` → confirmation gate → `creations.publish`.
- Boundaries: List is a `risk: none` authenticated read of the user's own Creations; it never substitutes for the State Document as Ask SpringBrand's position source (Ask still reads files only); the Creation flow is now **List / Upload / Publish**; the create-only update story (D12) is unchanged — List exposes versions for selection but MCP still cannot append one.

## Open decisions

- None. All design decisions for #52 are confirmed (D1–D15). Remaining session work: closing-comment update for D15, owner confirmation, then close.

## Appendix A: verified `/mcp/platform` contract facts (2026-09-01, from mcp-gateway implementation)

Reference format: `platform:springbrand@0:<actionId>`; only exact Registry references pass; foreign well-formed references return `capability_domain_mismatch` with `recovery: {action: switch_mcp, domain: action-api | connectors}` (`src/mcp.ts:4910-4932`).

| Capability | Key input facts | Key output facts |
| --- | --- | --- |
| `plugins.match` | `intent` required (≤4000), `normalizedIntent?`, `locale?`, `limit?` default 5 max 8 | `match_id` + `matches_found`/`no_match`; items: `plugin_id`, `title`, `summary`, `user_state` (`not_entitled`/`added`/`entitled_not_added`), `score`, `matched_on`; Plugin-only |
| `plugins.list` | `view` enum `usable` (default) / `marketplace` / `my` / `featured`, `query?`, `category?`, `page?`, `pageSize?` | `plugins[]` (id, title, summary, usage_count, user_state?), total/page metadata; `view=my` lists the user's own added/entitled Plugins |
| `plugins.get` | `pluginId` | id, title, summary, description, publisher, usage_count, `user_state`, price, tags, rating, my_rating?, usage_guide, `components[]`, `use_cases[]`; **no acquisition info** |
| `plugins.add` | `pluginId` | `user_state`, `acquisition: {status, price?} \| null`; risk high |
| `plugins.remove` | `pluginId` | `user_state`; risk high |
| `plugins.rate` | `pluginId`, `score` 1–5 | `user_state`, `my_rating`, `rating`; risk high |
| `plugins.get_use_case` | `useCaseId` | `{id, title, plugin, conversation}` — guided conversation |
| `plugins.get_distribution` | `pluginId` | id, version, title, summary, description, usage_guide, `components[]` (passthrough, not deeply validated), `package {format, version, url, expires_at}` |
| `creations.list` | **strict empty object** — any parameter → `invalid_arguments`; `risk: none`; excluded from Legacy `/mcp` discovery | `{creations[]}` — per item `artifact_id` (uuid), `source?`, `title?`, `category?`, `status?`, `access_mode?`, `current_version?`, `latest_version?`, `versions[]`, timestamps, passthrough + safe additive fields; 2 MiB response bound, never truncated; secret/identity checks preserved; actionable upstream errors preserved (`creation_list_unavailable`, `sp_session_expired`) |
| `creations.upload` | `title` (≤200), `files[]` 1–500 × `{filename, content_base64, content_type?}`, `entry_path?`; 30 MiB encoded / 20 MiB decoded; `idempotency_key` accepted here only | projection: `artifact_id`, `source`, `title`, `category` (platform-assigned), `status`, `access_mode` (initially private), `public_url`, `contact_enabled`, `will_watermark`, `current_version`, `latest_version`, `publication_version`, `saved_workspace_revisions`, `versions[]`, timestamps, `platform_response` + safe additive fields |
| `creations.publish` | `{artifactId (uuid), versionNumber (positive int)}` — no visibility field | `{artifact_id, access_mode: "public", `public_url`, publication_version, contact_cue}` |

Known distribution component shape (from `.scratch/action-component-gateway` design, not yet product code): `kind: "action"`, `usageMode: "gateway_action"`, bare action `id`, `revision`, `name`, `summary`, `inputSchema`, `outputSchema`, `risk`. Execution intent: build `action:springbrand@0:<id>` and execute via the **Action API entry**; distribution-driven materialization of `action:` references is not yet implemented.

## Appendix B: verified sp-platform creation admission facts (2026-09-01, from the sp-platform main repo)

MCP upload backs onto `POST /api/creations` — multipart form with exactly `file` (1–500 binary parts), `title`, `entryPath?`, plus a required `idempotency-key` header (`api/src/routes/inbox/inbox.routes.ts`, `inbox.handlers.ts`). Limits: aggregate decoded content ≤ 20 MiB, multipart overhead ≤ 512 KiB (`creation-upload-limit.ts`); the Gateway additionally bounds the encoded request at 30 MiB.

**Two admissible shapes:**

- **Single file** (`files.length == 1`; `entryPath` rejected). Extension decides category (`packages/creation/src/admission.ts` admission matrix): `md`/`txt` → document (strict UTF-8), `csv` → spreadsheet, `pdf` → document, `svg` → image (safe subset), `png`/`jpg`/`jpeg`/`gif`/`webp`/`avif` → image, `mp3`/`wav`/`ogg` + `mp4`/`webm` → audioVideo, `docx` → document, `xlsx` → spreadsheet. Legacy `doc`/`xls` deliberately unsupported. A lone `.html` is admitted only via the legacy HTML branch, which requires the declared MIME `text/html` (the Gateway per-file `content_type`).
- **Website bundle** (`files.length > 1`; `entryPath` required, must name a submitted `.html`/`.htm`, and becomes the bundle entry/content key). Text resources: `css`, `js`/`mjs`/`cjs`, `json` (must parse), `map`, `xml` (well-formed, no DTD/processing instruction), `docx`, `xlsx`. Binary resources: `woff`, `woff2`, `ttf`, `otf`, `ico`, `wasm`. Top-level image/audio/video formats are also allowed inside bundles with the same validators. Text files (`html`/`htm`/`css`/`js`/`mjs`/`cjs`/`svg`/`json`/`map`/`xml`) must **not contain `data:` URLs** — assets must be real bundle files referenced by relative path (`website-security.ts`). Path rules: relative, no leading `/`, no Windows drive prefix, no `\`, no `.`/`..` segments, NFC-normalized, per-segment ≤ 255 bytes, full path ≤ 768 bytes, case-insensitive duplicate paths rejected, no empty files.

**Safety validators:** SVG safe subset — single root `<svg>` in the SVG namespace; rejected elements include `script`, `iframe`, `foreignObject`, `image`, `embed`, `object`, `animate*`, `audio`, `video`, `set`, `style`; no `style` attribute, no `on*` handlers, `href`/`url(...)` only same-document fragments, no DOCTYPE/PI. OOXML strict-ZIP — required parts per kind (`docx`: `[Content_Types].xml`, `_rels/.rels`, `word/document.xml`; `xlsx`: plus `xl/workbook.xml`, `xl/_rels/workbook.xml.rels`), no macro/VBA/ActiveX/OLE/encryption markers, relative relationship targets only, zip limits 2048 entries / 64 MiB per entry / 200 MiB expanded / compression ratio 1000 (`admission.ts`, `packages/utils/src/strict-zip.ts`).

**Versioning/update (verified):** MCP upload is create-only — new `idempotency-key` ⇒ new artifact at v1; same key ⇒ deterministic replay (`mcpArtifactId = deterministicUuid(userId:mcp:key)`, `api/src/models/creation/index.ts`). Version appending exists only on the Chat `save_creation` path (same `workingCopyPath` ⇒ new version). MCP has no update and no withdraw (withdraw = `DELETE /api/creations/{id}/publication`, not in the ten-capability registry).

**Access/publish facts:** creations are born `access_mode=private`, `status=ready` (MCP always creates `ready`; statuses are `draft|ready`). Publish sets `access_mode=public` + `public_id`/`public_url`, gated only by ownership + version existence; publication is person-authorised by design (sp-platform ADR-0014, ADR-0018). Withdraw flips back to private and the old public link answers `410` (ADR-0014) — but withdraw is not reachable via MCP. `will_watermark` is derived at projection time: true when the owner is not subscribed. `contact_enabled`/`contact_cue` are not stored fields in sp-platform (Gateway projection passthrough only). No credit/metering cost is attached to upload or publish in the current main repo.

**Style reference (not contract):** the Chat `save_creation` tool description (`agent/src/runtime/tools/platform-tools.ts`) shows the platform's own plain-language creator contract ("Save one existing Workspace deliverable as an immutable Creation Version…"). The MCP path has no `workingCopyPath`; do not copy its semantics into the Platform Skill.
