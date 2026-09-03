# Skill Architecture Proposal: Ask SpringBrand + Three Domain Skills

**Status: APPROVED (main framework) by the owner, 2026-09-01. Conversion to
spec + issues in progress. Detailed workflow text (Plugin lifecycle, state
tracking, artifact publication format) is deliberately NOT designed here — it
is owned by the dedicated design issue created from this spec. Do not
implement from this file; the spec issue is the source of truth for planned
work.**

Date: 2026-09-01 (Asia/Shanghai)
Session: `/grill-with-docs` architecture interview for the three-domain MCP Gateway consumption.
Handoff input: the codex handoff file for this session (written to `/tmp`,
dated 2026-09-01).

This document records architecture discussion only. It changes no product files
(Skills, Hooks, Rules, manifests, mirrors, validators, tests, install guides,
version, or release metadata). After user review, the accepted content becomes
one spec and dependency-aware issues via the repository process.

## Sources of truth (referenced, not copied)

Gateway contract (authoritative, Issues 01–10 on `origin/dev`):

- `/Users/tony/Documents/project.nosync/cuecue/mcp-gateway/CONTEXT.md`
- `/Users/tony/Documents/project.nosync/cuecue/mcp-gateway/.scratch/mcp-domain-executors/spec.md`
- `/Users/tony/Documents/project.nosync/cuecue/mcp-gateway/docs/mcp-domain-executor-architecture.md`
- Gateway ADRs 0005, 0008, 0009, 0010, 0011, 0013
- `.scratch/mcp-domain-executors/issues/01…13` in mcp-gateway

Setup-repo baseline:

- `CONTEXT.md` (uncommitted four-Skill vocabulary — confirmed as prior grill output; kept as baseline)
- `docs/adr/0001-native-host-plugin-adapters.md` (binding for source-of-truth and Distribution Mirror rules; its one-Skill/one-endpoint scope is superseded by this proposal after approval)
- `docs/research/*-native-integration-capabilities.md` (Host capability evidence)
- GitHub Issues #16, #25, #42, #47

## Verified Gateway facts (2026-09-01)

- Dev deployed: `springbrand-connector-gateway-dev` at `devconnector.springbrand.ai`,
  version `5a7f8684-0dde-49b4-8224-49e7216c5a34`, commit `6e46cc0` (merge of PR #38).
- All four MCP paths live and require standard MCP OAuth (`401` + `WWW-Authenticate: Bearer` without token):
  `/mcp/platform`, `/mcp/action-api`, `/mcp/connectors`, `/mcp` (legacy).
- `PUBLISHED_CONNECTORS: "github"` confirmed in dev bindings.
- Issue 10 remaining checklist (real-OAuth initialize, tools/list, safe reads,
  Legacy compatibility, log secret scan) still open — Skill workflow text stays
  unfrozen until that verification lands.
- Tool surfaces (from implemented spec):
  - `/mcp/platform`: `list_capabilities` (static 10-capability registry:
    `springbrand.plugins.{match,list,get,add,remove,rate,get_use_case,get_distribution}`,
    `springbrand.creations.{upload,publish}`), `execute_capability`; prefix `platform:`.
  - `/mcp/action-api`: `match_capabilities` (returns only `kind=api_service`),
    `list_capabilities`, `get_capability`, `execute_capability`, `get_execution`;
    prefix `action:`; reference `action:springbrand@0:<actionId>`.
  - `/mcp/connectors`: `search_capabilities`, `execute_capability`; prefix `connector:`; v1 = `github@0` only.
  - `/mcp` legacy: mixed search/match/aliases + Action execute/status; no automatic retirement; new manifests must not select it.
- Cross-domain reference → `capability_domain_mismatch`, `retryable: false`,
  `recovery.action: switch_mcp`, `recovery.domain: platform|action-api|connectors`. No auto-forward.
- Platform/Action API responses use Public Contract Passthrough (additive upstream
  fields stay visible; no over-strict validation, no opaque `invalid_response`).
- All four entries authenticate with standard SpringBrand MCP OAuth; UA Runtime
  Grant product paths are retired (Gateway Issue 08).

## Confirmed decisions — Round 1 (2026-09-01)

1. **Vocabulary baseline.** The uncommitted `CONTEXT.md` four-Skill vocabulary is
   the recording baseline for this discussion (prior grill output; kept).
2. **MCP Domain Entry names (Host-visible server names):**
   `springbrand-platform`, `springbrand-action-api`, `springbrand-connector`.
   Aligned with Capability Domain vocabulary (singular Connector). Gateway URL
   paths stay `/mcp/platform`, `/mcp/action-api`, `/mcp/connectors`; the
   name↔path mapping is documented, not encoded.
3. **Skill machine names / display names:**
   | Machine name | Display name | Role |
   | --- | --- | --- |
   | `ask-springbrand` | Ask SpringBrand | Capability Guide (non-executing router) |
   | `springbrand-platform` | SpringBrand Platform | Domain Skill → `/mcp/platform` |
   | `springbrand-action-api` | SpringBrand Action API | Domain Skill → `/mcp/action-api` |
   | `springbrand-connector` | SpringBrand Connector | Domain Skill → `/mcp/connectors` |

   `springbrand-plugin-discovery` is retired as a name; the Plugin lifecycle
   workflow it carried moves into the Platform Skill. Canonical layout:
   `skills/<machine-name>/SKILL.md` × 4.
4. **Invocation policy and recursion guards.** All four Skills are both
   user-invocable and model-invocable. Ask SpringBrand selects at most one
   Capability Domain, reports position, recommends the next Domain Skill, and
   stops — it never activates multiple Domain Skills, never calls MCP, never
   executes. Domain Skills never call Ask SpringBrand back (exception: the user
   explicitly asks what else SpringBrand can do). Cross-domain work is an
   explicit Domain Transition handed directly from one Domain Skill to another,
   preserving relevant task state and ending the prior domain workflow.
5. **Intent routing table (minimum intent map):**
   | User request | Initial domain | Actor |
   | --- | --- | --- |
   | Create artifact and publish / upload creation / Plugin lifecycle (find, add, remove, rate, browse Marketplace) | Platform | Platform Skill → `/mcp/platform` |
   | "Use an available API to do X" (dynamic API intent) | Action API | Action API Skill → `/mcp/action-api` |
   | Read/write a named third-party system (GitHub etc.) | Connector | Connector Skill → `/mcp/connectors` |
   | "What can SpringBrand do for me?" | Ask SpringBrand | Navigate only, no execution |
   | "Continue the earlier Action execution" | Action API | Reuse execution state; do not rematch |
   | Create → publish → update GitHub | Platform first, then explicit Domain Transition | One executor at a time |
   | Platform reference sent to Action API | Surface `capability_domain_mismatch` + `recovery.domain`, switch deliberately | No auto-forward |
   | Factual/analysis-only, supplied-content transformation, ordinary writing/coding, planning without execution, provider-only, user opt-out | None | Continue natively |
6. **Updated Plugin registers only the three Domain Entries.** No legacy `/mcp`
   declaration in any new manifest (ADR-0009: new manifests must not select
   `/mcp`). Already-installed Plugin versions keep using `/mcp` via the Gateway
   Legacy Adapter until the user upgrades or the owner explicitly retires it.
7. **Dev coverage.** The architecture covers `springbrand-dev` isomorphically:
   one set of canonical assets; the dev Adapter points at
   `devconnector.springbrand.ai/mcp/{platform,action-api,connectors}`; dev tags
   verify first, `main` follows.

## Open questions (frontier)

### Round 2 decisions (confirmed by user, 2026-09-01)

- **Q9 Routing Notice budget**: target ≤ ~700 characters. Contents: one-line
  three-domain map + "when uncertain or asked what SpringBrand can do → use
  Ask SpringBrand first" + notice-only disclaimer. All old Match/REUSE
  workflow detail moves out of the Hook into Skill bodies. Host-specific
  reference syntax stays in Host Adapters. Exact wording drafted at proposal
  stage.
- **Q10 Issue reconciliation**: #42 close as superseded (still-valid
  requirements — `springbrand.plugins.match` outcome interpretation, no
  reranking, errors ≠ no_match — feed the new Platform Skill spec); #47 close
  as superseded; #16 stays open as packaging-principles owner (new spec
  amends it, explicitly rewriting the single-Skill/single-endpoint clauses);
  #25 stays open with amended scoring dimensions (router accuracy, domain
  selection, tool isolation, workflow completion, duplicate discovery).
  Actual close/comment/link actions execute at spec time.
- **Q11 Migration sequence**: Gateway Issue 10 real-OAuth E2E → setup repo
  implementation + dev tag + four-Surface Native Evidence → Gateway Issue 11
  production deploy → setup production release to `main` (three entries
  only) → existing installs stay on `/mcp`; retirement = Gateway Issue 12,
  explicit owner decision. New Plugin release hard-depends on Issue 11.
- **Q12 Test/evaluation rewrite scope**: validators move to exactly four
  named Canonical Skills + three-entry assertions + mirror equivalence
  extended to 4 Skills + Hook + Rule; `test_routing_policy.py` rewritten for
  the four-Skill graph; corpus gains ROUTER / DOMAIN_SELECT / TOOL_ISOLATION
  / TRANSITION classes, keeps NO_FIT / SKIP / FAILURE semantics, retires the
  mixed MATCH/REUSE/BROWSE classes; secret checks, static network-free Hook
  checks, and marketplace structure checks are kept.

### Authoring aid decision

**skill-creator** (anthropics/claude-plugins-official) may be used during
implementation as an authoring/eval aid for drafting and iterating the four
Skills. Constraints:

- It is a development-time tool, never a shipped asset or part of the
  SpringBrand Skill Set.
- Canonical SKILL.md frontmatter stays minimal (`name`, `description`) —
  skill-creator's Claude-specific extras (e.g. `compatibility`) must not
  enter canonical assets without per-Host verification.
- Its "pushy description" advice is **rejected** for this repo: routing
  precision (false-trigger rate ≤ 10% per #25) outweighs under-triggering;
  visibility comes from the Routing Notice + Ask SpringBrand instead.
- Its draft → test prompts → eval → iterate loop is compatible with the
  routing corpus work and may inform Skill authoring issues.

### Round 3 decisions (confirmed by user, 2026-09-01)

- **Cursor duplicate-tool-name mitigation**: (1) every Domain Skill names its
  MCP entry in instructions and forbids tool-name inference; (2) Cursor Native
  Evidence adds an explicit cross-entry tool-selection test (a Platform task
  must not reach `springbrand-connector`'s `execute_capability`); (3) residual
  risk is accepted and recorded in Cursor evidence. Gateway tool names stay
  unchanged (contract already deployed).
- **Distribution Mirror mapping**: canonical `skills/<name>/SKILL.md` × 4 →
  `plugins/springbrand/skills/<name>/` × 4 (Cursor) and
  `plugins/springbrand-workbuddy/skills/<name>/` × 4 (WorkBuddy), all
  byte-equivalent, generated, drift-checked (ADR-0001 mechanism, extended
  from one Skill to four). Hook and Rule mirror rules unchanged in kind.
- **Dev MCP entry names**: `springbrand-dev-platform`,
  `springbrand-dev-action-api`, `springbrand-dev-connector` — distinct from
  production names, preserving the "manual fallback coexists by distinct
  names" principle.
- **Manual Skill-plus-MCP fallback**: same shape as the production Plugin
  (4 Skills + 3 entries, same entry names; Hosts namespace plugin-bundled
  servers separately). "Do not enable a full Plugin and the fallback
  together" carries over. Verify against current INSTALL text at spec time.

## Clarified in grilling (confirmed by user, 2026-09-01)

### Ask SpringBrand is a wizard for non-developers (answers Q7, refines Q8)

Two scenarios define Ask SpringBrand's job:

1. **Quick start / first use**: the user (possibly a non-developer) meets the
   SpringBrand Plugin for the first time; Ask SpringBrand introduces what the
   Plugin does and the three MCP capability modules.
2. **Mid-workflow guidance**: the user has used SpringBrand partway and does
   not know the next step; Ask SpringBrand reports the current position and
   the next step.

Implications:

- **Target audience is ordinary, possibly non-developer users.** All four
  Skills and the Routing Notice must read as strong, plain-language process
  guidance; otherwise the user's agent gets lost. (New constraint beyond the
  handoff.)
- **Style reference**: the ask-matt router pattern (persistent guide, main
  flow + on-ramps, explicit phase boundaries, router points to one
  authoritative workflow then stops). Borrow the guidance method only; do not
  copy content or assume its engineering lifecycle.
- **State tracking is a separate future discussion**: the detailed
  creation → upload → publish flow and its state-tracking design will be
  discussed separately. This session fixes only Ask SpringBrand's role as
  guide.

**Position sources (user-corrected, 2026-09-01)**: Ask SpringBrand determines
"current position" from two sources:

1. Conversation context (what the user and Agent already did in this thread);
2. The state record embedded in the user's current artifact document (planned:
   a future workflow discussion will add a skill that helps users create
   standard-format artifacts meeting upload requirements, with state records
   carried in the artifact file itself).

Reading local artifact files is file access, not MCP execution, so it is
compatible with Ask SpringBrand staying non-executing. Cross-session state
persistence design, the artifact standard format, and the possible new
artifact-creation helper Skill are all deferred to the future workflow/state
discussion. Consequence: the Canonical Skill Set validator must check an
explicit named list of Skills (currently four), not a hardcoded count, so the
set can grow without re-litigating the package contract.

**Audience (user-corrected)**: the Plugin targets ordinary people — not only
developers. All user-facing text across the four Skills and the Routing
Notice must be plain-language, step-by-step process guidance; technical
vocabulary (MCP, capability, endpoint) stays inside Agent-facing operational
instructions and never leaks into user-facing explanations.

## Host multi-MCP research findings (2026-09-01, doc-verified)

All four Hosts support multiple named remote HTTP MCP servers per plugin via
the same `mcpServers` map (named keys → `{type: "http", url}`):

| Host | Multi-server | Model-visible tool namespace | OAuth | Duplicate-tool behavior |
| --- | --- | --- | --- | --- |
| Claude Code | Yes (doc-verified) | `mcp__plugin_<plugin>_<server>__<tool>` for plugin servers; OAuth scoped `plugin:<plugin>:<server>` | Per endpoint | Unique via full prefix |
| Codex | Yes (doc + source verified) | `mcp__<server>__<tool>`; collisions get deterministic hash suffix; 64-char cap | `codex mcp login <name>` per server | Hash-suffix disambiguation |
| Cursor | Yes (doc) | UNVERIFIED; observed `mcp_<server>_<tool>`; **community-reported misrouting when two servers expose the same raw tool name** | Per entry (`auth` block or discovery) | **Unreliable — known misrouting risk** |
| WorkBuddy | Yes (doc-verified, official two-server example) | `mcp__<server>__<tool>` | Per server | Unique via server prefix |

Consequences for this architecture:

- Three named entries (`springbrand-platform`, `springbrand-action-api`,
  `springbrand-connector`) fit every Host's `mcpServers` map without schema
  changes; only the Cursor package needs its generated `mcp.json` extended.
- Shared generic tool names (`list_capabilities`, `execute_capability`) are
  disambiguated by server prefix on Claude, Codex, and WorkBuddy. **Cursor is
  the least-safe Host for duplicate raw tool names** — Native Evidence for
  Cursor must explicitly test cross-entry tool selection, and Skill text must
  name the MCP entry (not rely on tool-name inference), per the MCP Domain
  Entry vocabulary.
- OAuth is per endpoint on every Host: three entries likely mean three OAuth
  consents per Host (token reuse across same-issuer endpoints is unverified).
  Install guides must disclose this; Native Evidence must record the real
  consent count per Surface.

## Skill graph (design)

### Ask SpringBrand contract

- **Entry**: user-invoked, or model-invoked when the domain is uncertain, the
  user asks what SpringBrand can do, the user is new to SpringBrand, or the
  user is lost mid-workflow.
- **Behavior — two scenarios**:
  1. *Quick start*: introduce what the Plugin offers and the three capability
     domains in plain language; end by recommending the one Domain Skill that
     matches the user's goal.
  2. *Mid-workflow guidance*: determine current position from conversation
     context and artifact-document state records; report position and the
     next step; recommend the one Domain Skill to continue in.
- **Clarifying budget**: at most one clarifying question, only when the
  domain cannot be selected safely; if still unclear, present the three-domain
  map and let the user choose. Never guess into execution.
- **Output contract (handoff payload, four elements)**: selected domain + a
  one-line reason + the task restated (preserving the user's intent) + known
  state pointers (existing match/plugin/action/execution IDs, connection
  names). It names the one Domain Skill to take over, then stops.
- **Never**: call MCP, execute, acquire, authorize, upload, publish, or
  activate more than one Domain Skill.

### Domain Skill common rules

- **Entry**: entered directly (explicit domain request) or via Ask's handoff.
  On entry, scan the conversation for reusable state; REUSE over
  rediscovery; never rematch unless the intended outcome materially changes
  or the user asks to refresh.
- **Execution**: use only the tools of its own MCP Domain Entry; instructions
  always name the entry (no tool-name inference).
- **Cross-domain**: on `capability_domain_mismatch` (or a recognized need),
  perform an explicit Domain Transition — announce it to the user, preserve
  relevant state, end the prior domain workflow, and hand to the target
  Domain Skill directly (never via Ask, never a merged search).
- **Exit**: report the result when the task completes; the only path back to
  Ask SpringBrand is the user explicitly asking what else SpringBrand can do.
- **Workflow text**: derived from verified Gateway contracts only; stays
  unfrozen until Gateway Issue 10's real-OAuth E2E verification lands.

### Domain Skill scopes

| Skill | MCP entry | Tools | Scope |
| --- | --- | --- | --- |
| `springbrand-platform` | `springbrand-platform` | `list_capabilities`, `execute_capability` | Artifact creation → upload → publication; Plugin lifecycle (`plugins.match/list/get/add/remove/rate/get_use_case/get_distribution`); `creations.upload/publish` |
| `springbrand-action-api` | `springbrand-action-api` | `match_capabilities`, `list_capabilities`, `get_capability`, `execute_capability`, `get_execution` | Intent → API Service match → contract → execute → status; reuse execution state |
| `springbrand-connector` | `springbrand-connector` | `search_capabilities`, `execute_capability` | Published Connector capabilities (GitHub only in v1); deliberately small guidance surface |

## Routing Notice draft (≤ ~700 characters, for review)

```text
SpringBrand is available through the installed <reference>. It has three
capability domains:
- Platform: create and publish artifacts, manage Plugins, browse the
  Marketplace
- Action API: use dynamic API services for tasks
- Connector: work with third-party systems such as GitHub
When the right domain is unclear, or the user asks what SpringBrand can do,
follow the `ask-springbrand` Skill first; it routes to exactly one domain
Skill. This Notice only makes the Skills visible. It does not determine fit,
call MCP, or authorize side effects.
```

`<reference>` is Host-specific adapter syntax (e.g. `$ask-springbrand` on
Codex, `/springbrand:ask-springbrand` on Claude). Final wording is polished
with `/writing-for-agents` at spec time.

## Skill description drafts (frontmatter, for review)

Precise, not pushy (routing precision outweighs under-triggering; visibility
comes from the Routing Notice + Ask SpringBrand):

- **ask-springbrand**: "Guide the user through SpringBrand: introduce what
  the Plugin and its three capability domains (Platform, Action API,
  Connector) do, or report the current workflow position and the next step.
  Use when the user asks what SpringBrand can do, is new to SpringBrand, is
  unsure which domain fits, or is lost mid-workflow. It never discovers or
  executes capabilities; it recommends exactly one domain Skill and stops."
- **springbrand-platform**: "Execute the SpringBrand Platform workflow:
  create and upload artifacts, publish creations, and manage the Plugin
  lifecycle (find, add, remove, rate, browse Marketplace) through the
  springbrand-platform MCP entry. Use for explicit SpringBrand Platform
  requests, artifact creation or publication, and Plugin lifecycle tasks. Do
  not use for dynamic API services (Action API) or third-party systems
  (Connector)."
- **springbrand-action-api**: "Execute SpringBrand Action API workflows:
  match a user intent to available API services, inspect an Action contract,
  execute it, and track execution status through the springbrand-action-api
  MCP entry. Use for 'use an available API to do X' tasks and for continuing
  an earlier Action execution. Do not use for Platform artifact or Plugin
  work, or third-party system connections."
- **springbrand-connector**: "Execute SpringBrand Connector workflows: search
  published Connector capabilities (GitHub in version one) and execute them
  through the springbrand-connector MCP entry. Use when the task names a
  third-party system such as GitHub. Do not use for Platform artifact or
  Plugin work, or dynamic API services."

## Proposed spec boundary (no implementation diff in this session)

The post-approval spec covers, as one spec with dependency-aware issues:

1. Canonical assets: four `skills/<name>/SKILL.md` files (workflow text
   derived from verified Gateway contracts), canonical Routing Notice text,
   Host Adapter mapping rules.
2. Host Adapters: Codex, Claude, Cursor, WorkBuddy manifests with the three
   Domain Entries; generated byte-equivalent mirrors for Cursor and WorkBuddy
   (4 Skills + Hook + Rule); dev Adapter variants with `springbrand-dev-*`
   entries.
3. Package contract rewrite: validators (named Skill list, three-entry
   assertions, mirror equivalence), `test_routing_policy.py`, hook tests.
4. Routing corpus rewrite + #25 amendment (new scoring dimensions).
5. Install guides: three-entry OAuth disclosure (consent count per Host),
   fallback shape, migration notes.
6. Release/migration plan per the confirmed sequence (dev tag → Native
   Evidence → Gateway Issue 11 → production release).
7. Issue reconciliation actions for #42, #47, #16, #25.

Out of scope (explicitly deferred): artifact standard format + embedded state
records + possible artifact-creation helper Skill (future workflow
discussion); legacy `/mcp` retirement (Gateway Issue 12, owner-controlled);
any sp-platform or universal-agent change; UA Runtime Grant work.

## Deferred to later sessions (recorded, not designed here)

- Creation → upload → publish workflow detail and its state-tracking design
  (including the artifact standard format, state records inside artifact
  files, and the possible new artifact-creation helper Skill).
- Detailed domain workflow text (frozen only after Gateway Issue 10 E2E).
- Final Hook/Rule wording and Skill descriptions (drafts above; polished at
  spec time).

## ADR candidates (drafted at proposal approval, not before)

- ADR-0002: Four-Skill set with a non-executing router (supersedes ADR-0001's
  single Canonical Skill scope; keeps its mirror/source-of-truth rules).
- ADR-0003: Three MCP Domain Entries per Host manifest; no legacy entry in
  new manifests; dev entries named `springbrand-dev-*`.
- ADR-0004: Distribution Mirror extension to the four-Skill set.
