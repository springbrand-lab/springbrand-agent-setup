---
name: springbrand-action-api
description: >
  Execute SpringBrand Action API workflows: match a user intent to available
  API services, inspect an Action contract, execute it, and track execution
  status through the `action_`-prefixed tools of the SpringBrand MCP entry.
  Use for "use an available API to do X" tasks and for continuing an earlier
  Action execution. Do not use for Platform artifact or Plugin work, or
  third-party system connections.
metadata:
  version: "1.2.0-beta.12-dev.7"
---

# SpringBrand Action API

## Version and environment check

Read this Skill's `metadata.version` as its installed release. A `-dev.N`
marker identifies the development distribution; otherwise it is production.
Use the user's explicit environment choice, or the installed distribution
when no choice was given; never silently switch between MCP environments.
If local package `VERSION`, Plugin version, or sibling Skill versions are
available, check that they agree. Report a mismatch and recommend reinstalling
the intended release before executing capabilities. A standalone Skill need
not have a package manifest. This is a local consistency check: do not call
MCP or fetch remote releases just to check versions, and do not infer the MCP
server version or automatically reinstall from this metadata.

SpringBrand Action API is the Domain Skill for having an available API service
do a task for the user. It owns one workflow: understand what the user wants,
find the API service that fits, read its contract, run it with the user's
explicit confirmation, and report the result honestly.

Everything runs through the single SpringBrand MCP entry. Use only the
Action-API-prefixed tools — `action_match_capabilities`,
`action_list_capabilities`, `action_get_capability`,
`action_execute_capability`, `action_get_execution`,
`action_render_execution_image` — and always name the `action_` prefix in
instructions. The same entry also exposes the
`platform_`- and `connector_`-prefixed tools of the other domains: never call
them, never infer a tool by its name alone. A cross-domain need is an
explicit Domain Transition (see [Domain boundaries](#domain-boundaries)),
never a direct call to another domain's prefix.

## How to use this Skill

There are three ways into this Skill. Identify which one applies, then follow
the five-step trunk.

1. **Direct request** — the user asks to use an available API to do something
   ("use an API to summarize this file"). Start at
   [Step 1](#step-1--clarify-the-intent).
2. **Ask SpringBrand handoff** — the guide has already selected this domain
   and handed over a restated task plus known state pointers. Scan the
   handoff for reusable state (an existing execution ID means
   [continue, do not rematch](#continuing-an-earlier-execution)); otherwise
   start at [Step 1](#step-1--clarify-the-intent).
3. **Domain Transition from the Platform Skill** — a Plugin's distribution
   component carries an executable Action and arrives with its exact Action
   ID. Skip matching entirely: go straight to
   [Step 3](#step-3--read-the-contract) with the ID that was handed over.

On every entry, scan the conversation and any state pointers for reusable
work before discovering anything new. Reuse beats rediscovery; never rematch
unless the intended outcome materially changes or the user asks to start
fresh.

Use this discovery decision tree:

- existing execution ID → `action_get_execution`
- exact Action ID → `action_get_capability`
- explicit inventory browsing → `action_list_capabilities`
- clear task → one `action_match_capabilities` call
  - compatible candidate → exact Get
  - malformed non-English body → repair and rematch once
  - tool or provider failure → report the failure
  - well-formed `no_match` or no compatible candidate → one bounded
    inventory-recovery traversal

List recovery ends at the first compatible inventory entry or at complete
inventory traversal. It never authorizes execution.

## The five-step trunk

### Step 1 — Clarify the intent

Restate the user's task-level goal in one sentence and keep it faithful. Do
not broaden, narrow, or embellish the requested outcome. Step 2 turns this
goal into catalogue-facing discovery text without changing its business
meaning.

- If the user is **continuing an earlier Action execution**, do not rematch.
  Follow [Continuing an earlier execution](#continuing-an-earlier-execution).
- If the goal is genuinely ambiguous, ask the user one plain-language
  question about what they want done. Do not guess into execution.
- If the request is not about using an API service at all (creating or
  publishing artifacts, managing Plugins, working with a named third-party
  system), this is the wrong domain — see
  [Domain boundaries](#domain-boundaries).

### Step 2 — Match the intent to API services

Before constructing any match body, read
[references/action-discovery.md](references/action-discovery.md) — the exact
Match and List schemas, discovery-intent construction, hard compatibility
constraints, and bounded recovery semantics live there.
If the request contains a supplier, platform/product, model, object, or
operation alias, abbreviation, alternative spelling, or non-English name,
also read [references/action-aliases.md](references/action-aliases.md) before
constructing the body.

Action Match uses keyword matching, not semantic understanding. Translate
the complete task into English and resolve relevant aliases before extracting
capability keywords. For a clear task, call `action_match_capabilities` once
with English capability keywords in `intent`, the canonical catalogue label
in `normalized_intent`, and the user's original `locale`. Keep the complete
business requirement in `intent_spec`; search wording does not replace it.
Rules that are not optional:

- A non-English intent **always** carries an English `normalized_intent`
  (for example `Xiaohongshu Note Search` or `Text to Image`). New calls use
  English in both search fields. A legacy non-English match body without an
  English label is malformed for matching purposes and
  produces false empty results.
- Strip unrelated invocation brands, environment names, and sentence filler,
  while retaining business platforms, explicit suppliers, model variants,
  operations, and modalities. Preserve canonical names such as `Text to Image`
  and `Image to Video` intact: their `to` expresses direction, not filler.
- The match returns **API Service candidates only**. Apply the hard
  compatibility constraints within that candidate kind.
- **Preserve the returned order exactly.** Derive the user's explicit
  supplier, platform/product, operation, and object/modality constraints;
  recommend the first candidate in that order satisfying all applicable
  constraints. Never invent another score, rerank, re-sort, or apply a second
  threshold.
- An empty result from a body lacking an English `normalized_intent` is a
  **malformed body, not a no-match**: fix the body and rematch once. Only a
  repaired, well-formed Match may proceed to compatibility evaluation.
- A compatible candidate prevents List recovery even when `complete: false`.
  Continue to exact Get and disclose only that additional alternatives may
  exist.
- A well-formed `no_match`, or a result with no compatible candidate, enters
  the reference's single bounded `action_list_capabilities` recovery only
  when the request has enough hard-constraint signal for safe inspection.
- An error is **not** a no-match. If the call fails, report the failure and
  stop or retry; transport, OAuth, permission, schema, and provider failures
  never enter List recovery.
- For explicit inventory browsing, use `action_list_capabilities` directly;
  do not Match first.
- When the tool's declared input schema exposes `observation`, attach it at
  the top level of the Match input — a sibling of the match fields, never
  inside them. It is the structured requirement context for this discovery:
  `schema_version: 1`, the task's `task_id`, and an `intent_spec` stating
  the user's task goal, expected output, material types, explicit
  constraints, and what is still undecided (material types only; never
  content, transcripts, or credentials). Keep the returned
  `observation.discovery_id` with the task state — Step 4 associates the
  execution with it. The field never changes the match: same body rules,
  same returned order, no extra call because of it.

Present compatible candidates to the user in their returned order and plain
language: what each service does, which requirements remain unverified, and
which one you recommend. Scores measure keyword matching, not task-success
probability; hard compatibility checks still apply even to the highest score. Let the user
pick, or confirm your recommendation, before going further. Every selected
candidate, including one found through inventory recovery, goes through exact
Get before execution is proposed.

### Step 3 — Read the contract

Call `action_get_capability` for the
selected Action. Read three things before proposing execution:

- **`risk`** — how consequential the Action is. A `high` risk Action must be
  disclosed to the user before any confirmation is requested (see Step 4).
- **`inputSchema`** — what the Action needs. Build the input strictly to
  this schema; every required field present, no invented fields.
- **`outputSchema`** — what comes back, so you can deliver the result in
  the user's terms later.

The revision information in the response is informational only. Never invent
or send an `expectedRevision` — revision-bound references are not part of
this contract.

### Step 4 — Execute with confirmation

Execution changes real things and may cost Credits. Never execute without
the user's explicit confirmation for this specific run.

1. **Disclose before confirming.** In plain language, tell the user what the
   Action will do, what input it will use, and — if `risk` is `high` — say
   plainly that this is a consequential action before asking to proceed.
2. **Reference the Action exactly.** Use the reference exactly as
   `action_get_capability` returned it, in the form
   `action:springbrand@0:<actionId>`. Never construct, edit, or synthesize a
   reference from memory or from a match summary alone.
3. **Send schema-valid input** built in Step 3, plus an **idempotency key**
   so an accidental duplicate cannot run the Action twice.
4. **Associate the discovery.** If the Match that produced this Action
   returned an `observation.discovery_id`, pass
   `observation: { schema_version: 1, discovery_id, api_service_id }` at the
   top level of the execute call — a sibling of `name` and `body`, never
   inside the Action input. Without a discovery ID in hand, send no
   `observation` and never invent one. Field rules live in the reference.
5. Call `action_execute_capability`.

If a retry is safe and needed — for example a transport error where you know
the request may not have been received — retry with **the same reference,
the same input body, the same idempotency key, and the same `observation`**.
A new idempotency key means a new execution; never generate one on retry.

### Step 5 — Track status and deliver

An execution is not done because it was sent. It is done only when its
status says so.

- **`succeeded`** — the only status that counts as complete. Deliver JSON and
  text in plain language. For an image result, follow
  [Image result presentation](#image-result-presentation); for another file,
  provide its usable file URL as the output schema describes it.
- **`running`** — poll `action_get_execution` until it finishes. Tell the
  user it is in progress.
- **`failed`** — retry only when the failure is marked retryable, and only a
  finite number of times. A non-retryable failure is reported, not retried.
- **`insufficient_credits`** — stop and tell the user plainly: they need to
  add Credits, and once they have, the Action is invoked again as a new
  run. Never describe this as a system failure.
- **`outcome_unknown`** — never auto-retry. Report honestly that the outcome
  could not be confirmed and let the user decide what to do.
- A **`action_get_execution` tool error is a lookup failure, not a status.**
  It says nothing about whether the execution succeeded. Never report an
  execution as failed because the status lookup itself errored.

### Image result presentation

After `action_get_execution` verifies a successful image result, use this
presentation order without starting another Action execution:

1. **MCP App UI first.** When `action_render_execution_image` is available,
   call `action_render_execution_image` exactly once with the verified
   `executionId`. It rereads the existing execution and does not execute or
   charge the Action again. Its MCP App UI is the preferred presentation.
2. **Existing image attachment second.** The status or render result may also
   carry an `image` content block. When the host does not render the MCP App
   UI, refer to that already-rendered image as the attachment above. Never
   print base64, and do not add a duplicate Markdown image when an `image`
   content block is present.
3. **Markdown URL last.** Only when neither the MCP App UI nor an `image`
   content block is available, embed the exact saved preview URL as a Markdown
   image. If there is no preview URL, use the exact original image URL. Keep
   the original file URL as a normal download link when one exists.

A render-tool lookup error does not change the already verified execution
status. Fall back to the existing attachment or URL; never re-execute the
Action to repair presentation.

## Continuing an earlier execution

When the user returns to an Action that already ran or is running — in this
conversation or a later one:

1. Find the existing **execution ID**: from the conversation, from a pointer
   the user restates, or from a State Document in the user's artifact
   workspace if one references it.
2. Verify it with `action_get_execution`.
   The Skill verifies pointers itself; it never asks the user to interpret
   raw status data.
3. Continue from the verified status using
   [Step 5](#step-5--track-status-and-deliver). Do not rematch, do not
   re-execute, and do not start a parallel run — unless the intended
   outcome has materially changed or the user explicitly asks to run it
   again.

## Domain boundaries

- **Incoming:** a Platform distribution component that carries an executable
  Action arrives with its exact Action ID. Use it as-is — skip matching and
  go to Step 3. Never execute a Platform reference with an `action_` tool,
  and never leave the execution to the user to do by hand.

  <!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the
       distribution-component (gateway_action) handoff path additionally
       awaits Gateway implementation; the exact payload shape may adjust
       when both land. -->

- **`capability_domain_mismatch`** — a reference from another domain was
  sent here. Surface the error's `recovery.domain` to the user, announce the
  switch in plain language, preserve the task state, end this workflow, and
  hand back through Ask SpringBrand for an explicit Domain Transition into
  that domain's Skill (`springbrand-platform` or `springbrand-connector`).
  Never forward automatically, never call another domain's prefixed tool
  here, and never treat this error as a no-match.
- **Outgoing:** if the user's goal turns out to need another domain, say so,
  end this workflow, and hand back through Ask SpringBrand for the explicit
  Domain Transition — never by calling another domain's prefixed tool,
  never a merged search across domains.

## Talking to the user

All user-visible text is plain, step-by-step English. The user may not be a
developer.

- Say what will happen before it happens: "This will ask the service to
  summarize your file. Shall I go ahead?"
- Report status in everyday words: "It's running", "It finished — here is
  the result", "It didn't work, and retrying won't help".
- Keep technical vocabulary — MCP, capability, schema, idempotency key,
  reference — inside these Agent-facing instructions. The user sees
  outcomes and choices, not mechanics.
- Never claim success that did not happen, and never hide a failure.

## Hard rules

- Call only `action_`-prefixed tools on the SpringBrand MCP entry, and name
  the `action_` prefix in instructions. Never call a `platform_`- or
  `connector_`-prefixed tool; no tool-name inference, ever.
- Never synthesize, edit, or guess an Action reference; use exactly what
  `action_get_capability` or a verified handoff provided.
- Never invent or send `expectedRevision`.
- Discovery context rides only the tool arguments the schema declares
  (`observation` on Match and execute): never inside a match body, never
  inside Action input, and never with an invented or borrowed
  `discovery_id`.
- Never rematch when an existing execution can be reused; never re-execute
  to check a status.
- Errors are never no-matches; incomplete results are reported as
  incomplete; only `succeeded` counts as done.
- A non-English match intent always carries an English `normalized_intent`;
  an empty result from a body without one is a malformed body — fix it and
  rematch once, never report it as "nothing fits".
- `outcome_unknown` is never auto-retried; a status-lookup error is never
  reported as an execution failure.
- A successful image uses MCP App UI, then its existing image attachment, then
  Markdown URL fallback in that order. Presentation failure never authorizes
  another Action execution.
- Cross-domain work is an explicit Domain Transition — announced and
  state-preserving, handed back through Ask SpringBrand, one executor at a
  time — never another domain's prefixed tool.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the trunk above —
     match completeness reporting, contract fields, execution and status
     semantics, and error recovery — is derived from the dev Gateway
     contract and stays unfrozen until the Gateway's real-OAuth
     end-to-end verification lands. -->
