---
name: springbrand-platform
description: >
  Execute the SpringBrand Platform workflow: create and upload artifacts,
  publish creations, and manage the Plugin lifecycle (find, add, remove, rate,
  browse Marketplace) through the `platform_`-prefixed tools of the SpringBrand
  MCP entry. Use for explicit SpringBrand Platform requests, artifact creation
  or publication, and Plugin lifecycle tasks. Do not use for dynamic API
  services (Action API) or third-party systems (Connector).
---

# SpringBrand Platform

SpringBrand Platform is the Domain Skill for two jobs: taking an Artifact
from idea to a published Creation (create → upload → publish), and managing
the user's Plugins (find, add, use, remove, rate, browse the Marketplace).

Everything runs through the single SpringBrand MCP entry. Use only the
Platform-prefixed tools — `platform_list_capabilities` and
`platform_execute_capability` — and always name the `platform_` prefix in
instructions. The same entry also exposes the `action_`- and
`connector_`-prefixed tools of the other domains: never call them, never
infer a tool by its name alone. A cross-domain need is an explicit Domain
Transition (see [Domain boundaries](#domain-boundaries)), never a direct call
to another domain's prefix.

Capability references on this entry have the form
`platform:springbrand@0:<capabilityId>`. Use references exactly as
`platform_list_capabilities` or a verified handoff provided them; never
construct, edit, or synthesize one.

**The registry has eleven capabilities** — the eight `springbrand.plugins.*`
capabilities, plus `springbrand.creations.list`, `springbrand.creations.upload`,
and `springbrand.creations.publish` (`creations.list` joined on 2026-09-01).
Any older count written anywhere is outdated: treat the actual
`platform_list_capabilities` return as the truth.

## How to use this Skill

There are three ways into this Skill. Identify which one applies.

1. **Direct request** — the user asks to create or publish something, upload
   an Artifact, or manage Plugins ("publish my notes as a page", "find a
   Plugin for charts"). Start at
   [The creation pipeline](#the-creation-pipeline) for artifact work, or
   [The Plugin lifecycle](#the-plugin-lifecycle) for Plugin work.
2. **Ask SpringBrand handoff** — the guide has already selected this domain
   and handed over a restated task plus known state pointers. Scan the
   handoff for reusable state (a `match_id`, `plugin_id`, or `artifact_id`
   already in hand means continue from it); otherwise start at the section
   matching the task.
3. **Domain Transition from another Domain Skill** — the user's goal turned
   out to need Platform work. Start at the section matching the task with
   the state that was handed over.

On every entry, scan the conversation, the handoff, and any State Document
(see [The State Document](#the-state-document)) for reusable work before
discovering anything new. **Reuse beats rediscovery**: never rematch a Plugin
or re-list Creations when a usable pointer is already in hand and still
applies. Rematch only when the intended outcome materially changes or the
user asks to start fresh.

## The two tools

- **`platform_list_capabilities`** — returns the static capability registry.
  Use it for explicit browsing ("what can Platform do?") or to confirm a
  reference before executing. It is not a fallback for a failed call.
- **`platform_execute_capability`** — runs one capability by its exact
  `platform:springbrand@0:<capabilityId>` reference with input built strictly
  to that capability's schema: every required field present, no invented
  fields. Every workflow step below goes through it.

## The Plugin lifecycle

The trunk is: **match → get → add → get_distribution → use**. Each step calls
`platform_execute_capability` with the named capability.

### Step 1 — Find Plugins (`springbrand.plugins.match`)

Pass the user's intent faithfully — unchanged, not paraphrased or
embellished. Optional inputs: `normalizedIntent`, `locale`, `limit`
(default 5, max 8).

Rules that are not optional:

- Candidates are **Plugin-only** (`plugin_id`, `title`, `summary`,
  `user_state`, `score`, `matched_on`). There is no API-service kind here —
  that belongs exclusively to the Action API domain.
- **Preserve the returned order exactly.** Never rerank, never re-sort,
  never apply a second threshold of your own. Keep every ID exact.
- A genuine `no_match` (with its `match_id`) means the Marketplace has
  nothing fitting. As a one-time fallback while the catalogue is small, you
  may then run **one** `springbrand.plugins.list` search (`query`) before
  telling the user nothing fits.
- An **error is not a no-match.** Transport, OAuth, or service failures are
  reported as failures — never tell the user "nothing fits" because a call
  errored, and never trigger the List fallback for one.

For explicit browsing without a goal, use `springbrand.plugins.list` via
`platform_execute_capability`: `view` is `usable` (default),
`marketplace`, `my` (the user's own added and entitled Plugins), or
`featured`, with optional `query`, `category`, `page`, `pageSize`.

Present the candidates in plain language and let the user pick, or confirm
your recommendation, before going further.

### Step 2 — Read the Plugin (`springbrand.plugins.get`)

Fetch the chosen Plugin's detail: description, publisher, price, tags,
rating, usage guide, `components[]`, and `use_cases[]`. The response carries
`user_state`, which decides the next step — so state is known before any
commitment:

- **`added`** — the Plugin is already the user's. Go to
  [Step 4](#step-4--get-the-distribution-and-use-it) when needed.
- **`entitled_not_added`** — the user owns it but has not added it. Ask,
  then [add it](#step-3--add-with-confirmation).
- **`not_entitled`** — see
  [Not entitled](#not-entitled-acquisition-belongs-to-the-user).

`get` returns **no acquisition information**. Price and acquisition status
come only from the `add` response.

### Step 3 — Add with confirmation

`springbrand.plugins.add` is a confirmation gate. Never add without the
user's explicit yes for this specific Plugin, and **never pay or complete an
acquisition on the user's behalf** — the Agent has no capability for it, by
design.

**Not entitled: acquisition belongs to the user.** When `user_state` is
`not_entitled`: show the Plugin's detail (price included) and tell the user
plainly to complete the purchase or acquisition themselves on the Platform's
own site. Then re-run `springbrand.plugins.get` to confirm `user_state` has
flipped to `entitled_not_added`, ask, and add. Never pretend to buy, never
retry in a loop, and never describe waiting on the user as a failure.

### Step 4 — Get the distribution and use it

`springbrand.plugins.get_distribution` returns the Plugin's `components[]`
and its `package` (`format`, `version`, `url`, `expires_at`). This is what
"using" a Plugin means: reading its distribution and turning it into
guidance for the work at hand.

Optionally, `springbrand.plugins.get_use_case` (input: a `useCaseId` from
`get`'s `use_cases[]`) returns a guided conversation for the Plugin — fetch
it after adoption, before generation, when its guidance would help (see
[Stage 3](#stage-3--generate-the-artifact)).

If a distribution component carries an executable Action rather than static
content, stop this workflow and hand over — see
[Distribution Action Components](#distribution-action-components).

### Maintenance: remove and rate

`springbrand.plugins.remove` (confirmation gate) and
`springbrand.plugins.rate` (`score` 1–5) are **user-initiated only**. Run
them when the user asks, never automatically, never as cleanup.

## The creation pipeline

Five stages, each ending in a plain-language checkpoint: the user confirms,
chooses, and reviews; the Agent does the heavy lifting. Ordinary creation
with no SpringBrand intent never reaches this pipeline — it stays native.

### Stage 1 — Restate the goal

Say back, in one or two plain sentences, what the user wants made and what
the finished Artifact is. Get it right before anything else.

### Stage 2 — Show the resources (always runs)

Once the pipeline is engaged, this stage always runs. Search Plugins with
the user's intent (`springbrand.plugins.match`, rules above; on a genuine
`no_match`, one `springbrand.plugins.list` search as fallback) and present
the best match plus the alternatives, in Platform order, so the user sees
which Marketplace resources could complete the task.

- The user adopts one → continue with it.
- The user declines, or opted out upfront → generate natively; no Plugin.

This stage never changes when the Skill itself triggers — routing stays the
responsibility of Ask SpringBrand and the Routing Notice.

### Stage 3 — Generate the Artifact

Generate in the standard format from the start
([The Artifact standard format](#the-artifact-standard-format)) — do not
produce something non-compliant and fix it later. If a Plugin was adopted,
optionally fetch its use-case conversation
(`springbrand.plugins.get_use_case`) and turn it into generation guidance.

The user reviews and requests changes. Stage exit: the
[pre-upload self-check](#pre-upload-self-check) passes.

### Stage 4 — Upload (confirmation gate)

Say what will happen — "this uploads your file to SpringBrand as a private
draft" — and get the user's explicit yes. Then call
`springbrand.creations.upload` via `platform_execute_capability`.

- Input: `title` (1–200 characters), `files[]` (1–500 files, each
  `filename` + `content_base64`, optional `content_type`), optional
  `entry_path` for a website bundle, and an `idempotency_key`.
- The `idempotency_key` is accepted **here only**. A new key creates a new
  Creation; the same key deterministically replays the same one. On a safe
  retry (transport error, outcome unknown), reuse the same key — never
  generate a new one mid-retry.
- Success returns `artifact_id` and the Creation's projection. The Creation
  is born **private** and `ready`. Upload and publish currently cost no
  Credits; `will_watermark` is true when the owner is unsubscribed (a
  display fact, not an action item).

Record the pointers in the State Document
([below](#the-state-document)).

### Stage 5 — Publish (confirmation gate)

Publishing makes the Creation **public** — there is no visibility field; the
call is all-or-nothing. Never publish automatically. Say what will happen —
"this makes it publicly visible on the Platform, with a shareable link" —
and get the user's explicit yes.

Call `springbrand.creations.publish` with `{artifactId, versionNumber}`.
For MCP-created Creations, `versionNumber` is always **1**. Success returns
`public_url` — deliver it to the user, and record it in the State Document.

"Uploaded but not published" is a valid resting state. If the user stops
here, say so plainly and record it.

#### Publishing an existing Creation (`springbrand.creations.list`)

The publish stage has a second entry path: the user wants to publish
something already in their account. Call `springbrand.creations.list` via
`platform_execute_capability`, present the user's Creations — title,
category, publication status, current and latest version, and the version
list — in plain language, let the user
select the exact `artifactId` + `versionNumber`, confirm, and publish.

`creations.list` takes a **strict empty object** — any parameter returns
`invalid_arguments`. It is a `risk: none` read of the user's own Creations.

It also serves **publish-pointer recovery**: before publishing, if the
needed parameters are missing — no State Document, a lost one, or a foreign
artifact — list the account's Creations and identify the target by title,
category, or time instead of blocking or guessing.

### Updating a published Creation

Via the Platform domain, an update is **create-only**: generate the new
content, upload it as a **new Creation** (new `idempotency_key`), publish
the new Creation. There is no MCP path to append a version to an existing
Creation and none to withdraw one.

Say this plainly to the user: the update appears as a new entry, the
previous public link stays live, and taking the old link down is an action
on the Platform's own website — not something this workflow can do. Never
present an update as an in-place revision. `creations.list` exposes versions
for selection, but selecting one does not create one.

## The Artifact standard format

These are generation-time hard requirements: produce compliant Artifacts
from the start. An **Artifact** is the thing being made; a **Creation** is what
exists on the Platform once it is uploaded.

**Two admissible shapes:**

- **Single file** (exactly one file; `entry_path` rejected). The extension
  decides the category: `md`/`txt` (strict UTF-8), `csv`, `pdf`, `svg`
  (safe subset, below), `png`/`jpg`/`jpeg`/`gif`/`webp`/`avif`,
  `mp3`/`wav`/`ogg`, `mp4`/`webm`, `docx`, `xlsx`. Legacy `doc`/`xls` are
  unsupported — convert first. A lone `.html` is admitted only with the
  declared `content_type: text/html`.
- **Website bundle** (2–500 files; `entry_path` required, must name a
  submitted `.html`/`.htm`). Text resources: `css`, `js`/`mjs`/`cjs`,
  `json` (must parse), `map`, `xml` (well-formed), `docx`, `xlsx`. Binary
  resources: `woff`, `woff2`, `ttf`, `otf`, `ico`, `wasm`. Top-level
  image/audio/video formats are allowed inside bundles with the same
  validators. Text files (`html`/`htm`/`css`/`js`/`mjs`/`cjs`/`svg`/`json`/
  `map`/`xml`) must **not contain `data:` URLs** — assets are real bundle
  files referenced by relative path.

**Universal rules:** `title` 1–200 characters; decoded total ≤ 20 MiB; safe
relative paths (no leading `/`, no drive prefix, no `\`, no `.`/`..`
segments, NFC-normalized, ≤ 255 bytes per segment, ≤ 768 bytes per path,
case-insensitive duplicates rejected, no empty files); SVG safe subset
(single root `<svg>` in the SVG namespace; no `script`, `iframe`,
`foreignObject`, `image`, `embed`, `object`, `animate*`, `audio`, `video`,
`set`, or `style` elements; no `style` attribute; no `on*` handlers;
references only same-document fragments; no DOCTYPE); OOXML strict-ZIP
(`docx` requires `[Content_Types].xml`, `_rels/.rels`, `word/document.xml`;
`xlsx` additionally `xl/workbook.xml` and `xl/_rels/workbook.xml.rels`; no
macros, VBA, OLE, or encryption).

## Pre-upload self-check

Before every upload, check the finished Artifact against the format rules
above. This gate exists so the user never debugs admission errors.

- **Safe mechanical problems: auto-fix them.** Add the missing
  `content_type: text/html` declaration; materialize `data:` URLs into real
  bundle files; normalize unsafe paths.
- **Anything else: give a concrete, executable fix suggestion** ("convert
  the `.doc` to `.docx`", "split the bundle — it exceeds 20 MiB"), then let
  the user choose.

## The State Document

Workflow state lives in `springbrand-state.md`, a human-readable Markdown
file inside the Artifact Workspace next to the artifact files — **never**
inside the upload's `files[]`, and never merely embedded in a reply. The
user can read it; Ask SpringBrand reads it as plain file access; it is the
record that survives across sessions.

Keep it current. Required content:

- which Plugin was used (if any), with its `plugin_id`;
- the current step — creation: `created` → `uploaded` → `published`;
  Plugin lifecycle: `matched` → `selected` → `added` → `distributed` →
  `in_use`;
- uploaded or not, and after upload the publish parameters (`artifactId`,
  `versionNumber`).

Additional fields when known: `match_id`, `public_url` (after publish),
`next_action`, `updated_at`, the artifact shape (single file / website
bundle), `entry_path`, `title`, and a pointer to the workspace file list.

The Platform Skill verifies pointers itself through MCP
(`springbrand.plugins.get`, `springbrand.creations.list`); Ask SpringBrand
only reads the file and never executes. Pointer recovery from the account
is this Skill's job, never Ask's.

## Distribution Action Components

When `springbrand.plugins.get_distribution` returns components with
`kind: "action"` and `usageMode: "gateway_action"`, they are executable
dynamic Actions — and they execute **only through the Action API domain**.
The `platform_` tools reject `action:` references with
`capability_domain_mismatch`, and the user is never left to run them by
hand.

Perform an explicit Domain Transition to the `springbrand-action-api` Skill:
announce it in plain language, preserve the component's exact Action ID —
which the Action API Skill executes as an `action:springbrand@0:<id>`
reference — plus the task state, end the Platform workflow, and hand back
through Ask SpringBrand, which selects Action API and hands off. The Action
API Skill skips matching and goes straight to contract → execute.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the gateway_action
     handoff path additionally awaits Gateway implementation of
     distribution-driven action references; the exact payload handed over
     may adjust when both land. -->

## Domain boundaries

- **`capability_domain_mismatch`** — a reference from another domain was
  sent here. Surface the error's `recovery.domain` to the user — it is
  `action-api` or `connectors` — announce the switch in plain language,
  preserve the task state, end this workflow, and hand back through Ask
  SpringBrand for an explicit Domain Transition into that domain's Skill
  (`recovery.domain: action-api` → `springbrand-action-api`;
  `recovery.domain: connectors` → `springbrand-connector`). Never forward
  automatically, never call another domain's prefixed tool here, and never
  treat this error as a no-match.
- **Outgoing:** if the user's goal turns out to need another domain — a
  dynamic API service, or a named third-party system — say so, end this
  workflow, and hand back through Ask SpringBrand for the explicit Domain
  Transition. Never call another domain's prefixed tool, never a merged
  search across domains.
- One executor at a time: end this domain's workflow before another
  domain's begins.

## Talking to the user

All user-visible text is plain, step-by-step English. The user may not be a
developer.

- Say what will happen before it happens: "This will upload your page as a
  private draft on SpringBrand. Shall I go ahead?" — then "This makes it
  public with a shareable link. Publish it?"
- Report outcomes in everyday words: "Done — here is your public link",
  "It's uploaded but not published yet", "The Marketplace has nothing that
  fits — here's what I found browsing instead".
- Keep technical vocabulary — MCP, capability, reference, schema,
  idempotency key, artifact, Creation — inside these Agent-facing
  instructions. The user sees outcomes and choices, not mechanics.
- Never claim success that did not happen, and never hide a failure. An
  error is never reported as "nothing fits".

## Hard rules

- Call only `platform_`-prefixed tools on the SpringBrand MCP entry, and
  name the `platform_` prefix in instructions. Never call an `action_`- or
  `connector_`-prefixed tool; no tool-name inference, ever.
- Cross-domain work is an explicit Domain Transition — announced,
  state-preserving, handed back through Ask SpringBrand, one executor at a
  time — never auto-forward, never another domain's prefixed tool.
- Reuse beats rediscovery: never rematch or re-list when a usable pointer
  is in hand; rematch only when the outcome materially changes or the user
  asks.
- Preserve Platform order and exact IDs in match and list results; never
  rerank, never apply a second threshold.
- Errors are never no-matches. The one-time List fallback runs only after a
  genuine `no_match`, never after a transport, OAuth, or service error.
- `add`, `remove`, and every upload and publish run behind an explicit user
  confirmation for that specific action. The Agent never pays or acquires
  on the user's behalf.
- `remove` and `rate` are user-initiated only, never automatic.
- `creations.list` takes a strict empty object — send no parameters.
- The `idempotency_key` belongs to `creations.upload` alone; safe retries
  reuse the same key; a new key means a new Creation.
- Updates are create-only: new Creation, new publish, old public link stays
  live, withdrawal is a platform-web action. Never present an update as an
  in-place revision.
- The State Document (`springbrand-state.md`) lives in the Artifact
  Workspace, is never uploaded, and is the cross-session record; the Skill
  verifies pointers itself via MCP.
- Generate Artifacts in the standard format from the start, and run the
  pre-upload self-check so the user never debugs admission errors.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the workflow above —
     the eleven-capability registry, match/list semantics and the List
     fallback, the Plugin lifecycle and its user_state branches, the
     creation pipeline and upload/publish contracts, and the State Document
     shape — is derived from the dev Gateway and sp-platform contracts and
     stays unfrozen until the Gateway's real-OAuth end-to-end verification
     lands. -->
