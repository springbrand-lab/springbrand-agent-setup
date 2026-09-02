---
name: springbrand-connector
description: >
  Execute SpringBrand Connector workflows: search published Connector
  capabilities (GitHub in version one) and execute them through the
  springbrand-connector MCP entry. Use when the task names a third-party
  system such as GitHub. Do not use for Platform artifact or Plugin work, or
  dynamic API services.
---

# SpringBrand Connector

SpringBrand Connector is the Domain Skill for working directly with a
third-party system the user names — GitHub in version one. It owns one small
workflow: see what the user's connections authorize, pick the capability that
fits, run it with the user's explicit confirmation, and report the result
honestly.

Everything runs through the `springbrand-connector` MCP Domain Entry. Use only
that entry's two tools — `search_capabilities` and `execute_capability` — and
always name the entry in instructions. Never infer a tool by its name alone:
other SpringBrand entries expose tools with the same names, and picking by
name alone can reach the wrong domain.

## How to use this Skill

There are three ways into this Skill. Identify which one applies, then follow
the two-step workflow.

1. **Direct request** — the user asks to read or change something in a named
   third-party system ("list my open GitHub issues"). Start at
   [Step 1](#step-1--see-what-the-connection-authorizes).
2. **Ask SpringBrand handoff** — the guide has already selected this domain
   and handed over a restated task plus known state pointers. Scan the
   handoff for reusable state: an exact `connector:` reference whose match
   details (risk, schemas) are also in hand means
   [skip ahead](#step-2--execute-with-confirmation); a reference without
   them, or no reference at all, means start at
   [Step 1](#step-1--see-what-the-connection-authorizes).
3. **Domain Transition from another Domain Skill** — the user's goal turned
   out to need a third-party system. Start at
   [Step 1](#step-1--see-what-the-connection-authorizes) with the task state
   that was handed over.

On every entry, scan the conversation and any state pointers for reusable
work before searching again. Reuse beats rediscovery; never search anew when
an exact reference from this domain is already in hand and still applies.

## What this Skill can reach

Version one publishes exactly one connector: **GitHub**. The Gateway's
publish list is `github` and nothing else.

- If the user names GitHub, proceed with the workflow.
- If the user names any other service (email, chat, documents, anything
  else), say plainly that SpringBrand does not connect to it yet. Never
  advertise, hint at, or attempt an unpublished connector — code existing
  behind the scenes is not something the user can reach, and pretending
  otherwise produces failures the user cannot debug.
- If the user's task only *mentions* GitHub in passing but really creates,
  publishes, or manages SpringBrand artifacts or Plugins, that is the
  Platform domain — see [Domain boundaries](#domain-boundaries).

## The two-step workflow

### Step 1 — See what the connection authorizes

Call `search_capabilities` on the `springbrand-connector` MCP entry. It has
two modes:

- **No query** — returns the complete capability inventory the user's active
  Connector Connections authorize. Use this when the user wants to see what
  is possible, or when you need the full picture before choosing.
- **With a query** — searches within that same authorized inventory. Use
  this when the goal is specific ("issues", "pull requests"). The search is
  bounded: it never reaches beyond what the user's connections authorize.

Rules that are not optional:

- The response carries `matches`, `total`, `complete`, and `next_cursor`.
  **Paginate through `next_cursor` until `complete` is true.** A single page
  is never the whole answer; stopping early can silently hide later
  capabilities.
- **Preserve the returned order exactly.** Never rerank, never re-sort,
  never apply a threshold of your own.
- An **empty result can be genuine**: if the user has not connected the
  service, the search returns empty and complete. That is not an error —
  tell the user to connect the service first, in plain language, and stop.
- An **error is not a no-match.** If the call fails, report the failure and
  stop or retry; never tell the user "nothing fits" because a call errored.

Each match carries everything needed for Step 2, and nothing needs to be
invented:

- **`name`** — the exact capability reference, in the form
  `connector:<connection_id>:<release>:<action_id>`. Execution accepts this
  reference and nothing else. Never construct, edit, or synthesize a
  reference from memory, from a title, or from a description; use exactly
  what `search_capabilities` returned.
- **`risk`** — how consequential the capability is. A `high` risk capability
  must be disclosed to the user before any confirmation is requested (see
  Step 2).
- **`input_schema`** and **`output_schema`** — what to send and what comes
  back, so you can build the input strictly and deliver the result in the
  user's terms.

Present what you found to the user in plain language: what the capability
does, and which one you recommend. Let the user pick, or confirm your
recommendation, before going further.

### Step 2 — Execute with confirmation

Execution changes real things in the user's third-party system. Never execute
without the user's explicit confirmation for this specific run.

1. **Disclose before confirming.** In plain language, tell the user what the
   capability will do, in which system, and with what input — and if `risk`
   is `high`, say plainly that this is a consequential action before asking
   to proceed.
2. **Reference the capability exactly.** Pass the `name` exactly as
   `search_capabilities` returned it, with a `body` built strictly to the
   match's `input_schema` — every required field present, no invented fields.
3. **Send no idempotency key.** Connector capabilities reject one
   (`invalid_arguments`). This is different from the Action API domain; do
   not carry that habit over.
4. Call `execute_capability` on the `springbrand-connector` MCP entry.

Handle the outcome honestly:

- **Success** — deliver the result by its output schema, wrapped in plain
  language the user can act on. Never claim success that did not happen.
- **`missing_scope`** — the user's connection lacks a permission this
  capability needs. Tell the user plainly which permission is missing and
  that the connection needs to be re-authorized with more permissions; do
  not retry.
- **`credential_invalid`** — the connection's authorization is unavailable.
  Tell the user the connection needs to be re-established; do not retry.
- **`invalid_capability_reference`** — the reference was not an exact,
  authorized match. Go back to Step 1 and search again; never hand-assemble
  a reference.
- **A write whose outcome is unknown** — never auto-retry. Report honestly
  that the result could not be confirmed and let the user decide. A safe
  read may be retried; a write may have already taken effect.

## Domain boundaries

- **`capability_domain_mismatch`** — a reference from another domain was
  sent here. Surface the error's `recovery.domain` to the user, announce the
  switch in plain language, preserve the task state, and hand over to that
  domain's Skill (`springbrand-platform` or `springbrand-action-api`) as an
  explicit Domain Transition. Never forward automatically, never run another
  domain's workflow here, and never treat this error as a no-match.
- **Outgoing:** if the user's goal turns out to need another domain —
  creating or publishing a SpringBrand artifact, managing Plugins, or a
  dynamic API service — say so and hand off explicitly to that one Domain
  Skill. Never via Ask SpringBrand, never a merged search across entries.
- One executor at a time: end this domain's workflow before another domain's
  begins.

## Talking to the user

All user-visible text is plain, step-by-step English. The user may not be a
developer.

- Say what will happen before it happens: "This will list the issues in your
  connected GitHub repository. Shall I go ahead?"
- Report outcomes in everyday words: "Done — here is what it found", "It
  didn't work because the connection is missing a permission".
- Keep technical vocabulary — MCP, capability, schema, reference, connection
  ID — inside these Agent-facing instructions. The user sees outcomes and
  choices, not mechanics.
- Never claim success that did not happen, and never hide a failure.

## Hard rules

- Always name the `springbrand-connector` MCP entry in instructions. No
  tool-name inference, ever.
- Version one publishes GitHub only. Never advertise or attempt any other
  connector.
- Never construct, edit, or synthesize a `connector:` reference; use exactly
  what `search_capabilities` returned, and paginate until `complete`.
- Never execute without the user's explicit confirmation for this specific
  run; disclose `high` risk first.
- Never send an idempotency key to a Connector capability.
- Errors are never no-matches; an empty authorized inventory means "connect
  the service first", not "nothing fits".
- An unknown write outcome is never auto-retried.
- Use only this entry's tools. Cross-domain work is an explicit Domain
  Transition, announced and state-preserving, one executor at a time.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the workflow above —
     search modes and pagination completeness, the exact-reference execute
     contract, scope and credential error handling, and the no-idempotency
     rule — is derived from the dev Gateway contract and stays unfrozen
     until the Gateway's real-OAuth end-to-end verification lands. -->
