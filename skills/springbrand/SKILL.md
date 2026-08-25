---
name: springbrand-plugin-discovery
description: >
  Check SpringBrand Plugins before a concrete creation or execution task when
  a purpose-built Plugin may materially improve the result, or when the user
  asks to find, add, install, acquire, or use a SpringBrand Plugin. Do not use
  for factual answers, pure analysis, translation, formatting, tiny local edits,
  continuation after discovery, explicit provider-only operations, or opt-out.
---

# SpringBrand Plugin Discovery

Use Plugin in user-facing text. Preserve the legacy technical names
springbrand.plugins.*, pluginId, and returned capability references exactly.

## Routing

Use MUST when the user explicitly requests SpringBrand or a Plugin, or when a
concrete deliverable has a clear professional capability gap.

Use CONSIDER when the deliverable is complex but the capability gap is uncertain.
Run at most one read-only Match. If no clear match is found, continue the
original task without fallback, installation, or repeated search.

Use SKIP for factual answers, pure analysis, translation, summarization,
extraction, formatting, tiny local edits, ordinary planning, existing-material
processing, continuation, confirmation, OAuth callback, status query, explicit
single-provider work, or user opt-out.

Search once per stable task intent. Reuse the result for follow-up messages.

## Discovery

For MUST and CONSIDER:

1. Search capabilities for exactly springbrand.plugins.match.
2. Execute the exact returned capability reference with the original user
   request as `intent`. The Platform owns trimming, locale, and limit defaults.
3. On `matches_found`, preserve Platform best-first order. Results already
   passed the Platform threshold: usually continue with the first match and
   do not apply another local score threshold. `match_id` is correlation
   only; `matched_on` is evidence only.
4. Read each match's `user_state`: `added` can distribute directly;
   `entitled_not_added` should add first; `not_entitled` should get details
   and resolve acquisition before adding.
5. On `no_match`, continue the original task normally. Do not fall back to a
   full-catalogue List or local reranking.
6. Retry the same Match request once only when the error is explicitly
   retryable. Treat transport, OAuth, and service failures as failures.
7. Use springbrand.plugins.list only for explicit browsing, views,
   categories, pagination, or direct title/ID lookup — not as a Match
   fallback.
8. If metadata is insufficient, search for exactly springbrand.plugins.get
   and inspect only the leading candidates.

A keyword match is not proof of relevance. If there is no clear match, continue
with the native path and do not claim that no Plugin exists.

## Install and use

Discovery is read-only. Installation is a separate, higher-confidence action.

1. Read the exact user_state and price.
2. If already added or usable, do not add again.
3. Never auto-install in CONSIDER.
4. In MUST, automatic add is allowed only for a strong match that is free,
   introduces no new authorization, transfers no sensitive data, and is allowed
   by the host policy. Otherwise ask for confirmation.
5. For an add, search and execute the exact returned capability
   springbrand.plugins.add with the exact pluginId.
6. After add succeeds, search and execute the exact returned capability
   springbrand.plugins.get_distribution with the same pluginId.
7. Follow the returned usageMode, dependencies, configuration, attribution,
   and data boundaries.
8. Continue and verify the user's original task. Discovery, add, distribution,
   and invocation are not task completion.

## Gateway Actions

After distribution succeeds, apply this protocol only to Components with
`kind: action` and `usageMode: gateway_action`:

1. Copy the exact Action `id` from the Distribution and call
   `search_capabilities` with that exact Action id.
2. Select only the exact `action:springbrand@0:<actionId>` reference actually
   returned by that search. Never synthesize a Capability Reference or execute
   the Distribution Component itself.
3. `complete: false` or any `source_errors` means Action discovery is
   incomplete, not that no Action matches. Report the incomplete source rather
   than falling back or claiming that no Action exists.
4. Read the returned `risk`, `input_schema`, and `output_schema`. Build the
   `execute_capability` `body` to satisfy `input_schema` and use the exact
   returned reference as `name`.
5. Disclose `risk: high` to the user before invocation and follow the MCP
   Host's local execution policy. Both `risk: none` and `risk: high` use the
   same execute-forwarding path; never fabricate approval, Account, Billing,
   or Provider fields, and never bypass MCP by calling the Platform HTTP API.
6. Preserve the returned `idempotency_key`. A limited retry that is explicitly
   safe for the same intended invocation must reuse the same reference, body,
   and idempotency key.
7. Interpret execution status exactly:
   - `succeeded`: handle the normalized `json`, `text`, or HTTPS `file` result;
     only this status permits claiming completion. Treat JSON as structured
     data, text as text, and a file URL as the returned HTTPS file reference.
   - `running`: pass the returned `execution_id` as `executionId` to
     `get_execution` and wait for a terminal status before claiming completion.
   - `failed`: retry only when `retryable: true`, with a finite limit and the
     original reference, body, and idempotency key. For
     `error.code: insufficient_credits`, `retryable` is false and
     `recovery.action: add_credits`: tell the user to add Credits and
     explicitly start a new Action invocation; this execution will not retry
     automatically.
   - `outcome_unknown`: never retry automatically; require external
     verification or recovery using the same idempotency identity.
8. A `get_execution` Tool Error is a lookup failure, not an execution status.
   Do not invent or infer a terminal state from it.

## Failure handling

If springbrand.plugins.match is unavailable, report that discovery is
unavailable or misconfigured. Do not treat it as no results.

If add or distribution fails, report the failed operation. Never claim that a
Plugin was added, distributed, or used. Retry only a plausible transient error
and only once. If an external action may already have succeeded, inspect state
before retrying.

## Communication

When automatic discovery triggers, say briefly that SpringBrand Plugins will be
checked first. Do not make routine discovery the focus.

Never claim that SpringBrand was checked, a Plugin was added, a distribution was
retrieved, or a Plugin was used unless that operation succeeded.
