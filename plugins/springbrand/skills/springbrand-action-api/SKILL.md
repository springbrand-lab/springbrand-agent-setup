---
name: springbrand-action-api
description: >
  Execute SpringBrand Action API workflows: match a user intent to available
  API services, inspect an Action contract, execute it, and track execution
  status through the springbrand-action-api MCP entry. Use for "use an
  available API to do X" tasks and for continuing an earlier Action execution.
  Do not use for Platform artifact or Plugin work, or third-party system
  connections.
---

# SpringBrand Action API

SpringBrand Action API is the Domain Skill for having an available API service
do a task for the user. It owns one workflow: understand what the user wants,
find the API service that fits, read its contract, run it with the user's
explicit confirmation, and report the result honestly.

Everything runs through the `springbrand-action-api` MCP Domain Entry. Use
only that entry's tools — `match_capabilities`, `list_capabilities`,
`get_capability`, `execute_capability`, `get_execution` — and always name the
entry in instructions. Never infer a tool by its name alone: other SpringBrand
entries expose similarly named tools, and picking by name can reach the wrong
domain.

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

## The five-step trunk

### Step 1 — Clarify the intent

Restate the user's goal in one sentence and keep it faithful. The match is
only as good as the intent: do not broaden, narrow, or embellish it.

- If the user is **continuing an earlier Action execution**, do not rematch.
  Follow [Continuing an earlier execution](#continuing-an-earlier-execution).
- If the goal is genuinely ambiguous, ask the user one plain-language
  question about what they want done. Do not guess into execution.
- If the request is not about using an API service at all (creating or
  publishing artifacts, managing Plugins, working with a named third-party
  system), this is the wrong domain — see
  [Domain boundaries](#domain-boundaries).

### Step 2 — Match the intent to API services

Call `match_capabilities` on the `springbrand-action-api` MCP entry, passing
the faithful restatement from Step 1 unchanged — not a paraphrase, not an
embellished version.

**Keyword construction.** Build the match input before calling:

- **`intent`** — the user's request verbatim. Never translated, paraphrased,
  or stripped (Gateway Issue #48 contract).
- **`normalized_intent`** — required for non-trivial intents. Translate the
  user's intent into English and distill it into 1–3 English keywords or a
  short English phrase. Example: 「用springbrand帮我做电子礼物」→
  `normalized_intent: "digital gift"`.
- **Never put the brand word `springbrand` in `normalized_intent`** (or rely
  on it matching from `intent`): every capability title contains it, so it
  matches everything and drowns the semantic signal.
- **`locale`** — the detected user language.

Rules that are not optional:

- The match returns **API Service candidates only**. There is nothing else to
  filter in this domain.
- **Preserve the returned order exactly.** Never rerank, never re-sort, never
  apply a second threshold of your own.
- If the response says the result may be incomplete (`complete: false`), say
  so honestly — "these are the best matches, there may be more" — and never
  treat it as a definitive no-match.
- An error is **not** a no-match. If the call fails, report the failure and
  stop or retry; never tell the user "nothing fits" because a call errored.
- `list_capabilities` is for **explicit browsing only** — when the user wants
  to see what is available rather than get a task done. It is not a fallback
  for a failed or empty match.

Present the candidates to the user in plain language: what each service does,
and which one you recommend. Let the user pick, or confirm your
recommendation, before going further.

### Step 3 — Read the contract

Call `get_capability` on the `springbrand-action-api` MCP entry for the
selected Action. Read three things before proposing execution:

- **`risk`** — how consequential the Action is. A `high` risk Action must be
  disclosed to the user before any confirmation is requested (see Step 4).
- **`input_schema`** — what the Action needs. Build the input strictly to
  this schema; every required field present, no invented fields.
- **`output_schema`** — what comes back, so you can deliver the result in
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
   `get_capability` returned it, in the form
   `action:springbrand@0:<actionId>`. Never construct, edit, or synthesize a
   reference from memory or from a match summary alone.
3. **Send schema-valid input** built in Step 3, plus an **idempotency key**
   so an accidental duplicate cannot run the Action twice.
4. Call `execute_capability` on the `springbrand-action-api` MCP entry.

If a retry is safe and needed — for example a transport error where you know
the request may not have been received — retry with **the same reference,
the same input body, and the same idempotency key**. A new idempotency key
means a new execution; never generate one on retry.

### Step 5 — Track status and deliver

An execution is not done because it was sent. It is done only when its
status says so.

- **`succeeded`** — the only status that counts as complete. Deliver the
  result by its type — JSON, text, or a file URL — as the output schema
  describes it, wrapped in plain language the user can act on.
- **`running`** — poll `get_execution` on the `springbrand-action-api` MCP
  entry until it finishes. Tell the user it is in progress.
- **`failed`** — retry only when the failure is marked retryable, and only a
  finite number of times. A non-retryable failure is reported, not retried.
- **`insufficient_credits`** — stop and tell the user plainly: they need to
  add Credits, and once they have, the Action is invoked again as a new
  run. Never describe this as a system failure.
- **`outcome_unknown`** — never auto-retry. Report honestly that the outcome
  could not be confirmed and let the user decide what to do.
- A **`get_execution` tool error is a lookup failure, not a status.** It
  says nothing about whether the execution succeeded. Never report an
  execution as failed because the status lookup itself errored.

## Continuing an earlier execution

When the user returns to an Action that already ran or is running — in this
conversation or a later one:

1. Find the existing **execution ID**: from the conversation, from a pointer
   the user restates, or from a State Document in the user's artifact
   workspace if one references it.
2. Verify it with `get_execution` on the `springbrand-action-api` MCP entry.
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
  go to Step 3. Never execute a Platform reference on this entry, and never
  leave the execution to the user to do by hand.

  <!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the
       distribution-component (gateway_action) handoff path additionally
       awaits Gateway implementation; the exact payload shape may adjust
       when both land. -->

- **`capability_domain_mismatch`** — a reference from another domain was
  sent here. Surface the error's `recovery.domain` to the user, announce the
  switch in plain language, preserve the task state, and hand over to that
  domain's Skill (`springbrand-platform` or `springbrand-connector`) as an
  explicit Domain Transition. Never forward automatically, never run another
  domain's workflow here, and never treat this error as a no-match.
- **Outgoing:** if the user's goal turns out to need another domain, say so
  and hand off explicitly to that one Domain Skill — never via Ask
  SpringBrand, never a merged search across entries.

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

- Always name the `springbrand-action-api` MCP entry in instructions. No
  tool-name inference, ever.
- Never synthesize, edit, or guess an Action reference; use exactly what
  `get_capability` or a verified handoff provided.
- Never invent or send `expectedRevision`.
- Never rematch when an existing execution can be reused; never re-execute
  to check a status.
- Errors are never no-matches; incomplete results are reported as
  incomplete; only `succeeded` counts as done.
- `outcome_unknown` is never auto-retried; a status-lookup error is never
  reported as an execution failure.
- Use only this entry's tools. Cross-domain work is an explicit Domain
  Transition, announced and state-preserving, one executor at a time.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the trunk above —
     match completeness reporting, contract fields, execution and status
     semantics, and error recovery — is derived from the dev Gateway
     contract and stays unfrozen until the Gateway's real-OAuth
     end-to-end verification lands. -->
