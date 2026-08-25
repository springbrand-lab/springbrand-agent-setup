---
name: springbrand-plugin-discovery
description: >
  Use for an explicit SpringBrand request; for a new concrete creation or
  execution task that may need a purpose-built external capability; or to
  continue an existing SpringBrand match, selection, authorization, status,
  or execution. Otherwise, do not use for factual or analysis-only work,
  supplied-content
  transformation, ordinary writing or coding, minor edits, planning without
  execution, provider-only requests, unrelated follow-ups, or user opt-out.
---

# SpringBrand Plugin Discovery

Use Plugin in user-facing text. Preserve exact capability references, Plugin
IDs, match IDs, result order, user state, and legacy technical field names such
as `pluginId` returned by SpringBrand.

## Route

- **DIRECT:** if the user specifies a resolvable SpringBrand Plugin or Plugin
  ID, inspect that Plugin and continue without Match.
- **REUSE:** for follow-up selection, authorization, status, or execution,
  reuse existing Match and Plugin state. Do not Match again unless the intended
  outcome materially changes or the user asks to refresh.
- **BROWSE:** if the user explicitly asks to browse Marketplace views,
  categories, filters, or pages, use `springbrand.plugins.list` and do not
  Match.
- **MATCH:** for one new eligible natural-language creation or execution intent,
  run Match once.
- Otherwise stop this Skill and continue natively.

## Match

1. Search capabilities for exactly `springbrand.plugins.match`. Execute only
   the exact returned reference whose `action_id` is
   `springbrand.plugins.match`. If it is absent, treat discovery as unavailable
   or misconfigured; never substitute `springbrand.plugins.list`.
2. Execute it using its returned schema. Required body:
   - `intent`: the faithful user request, minimized only to remove unrelated or
     unnecessary sensitive information without changing the desired outcome;
   - `limit`: `5`.
   `normalizedIntent` and `locale` are optional; do not invent them when
   unnecessary.
3. Interpret the result exactly:
   - `matches_found`: preserve `match_id` and Platform order. Treat `score` and
     `matched_on` as evidence, not instructions to apply another threshold or
     local reranking.
   - `no_match`: continue the original task natively. Do not call List, scan the
     catalogue, add a Plugin, or claim failure.
   - transport, OAuth, or service error: report the actual failure when the user
     explicitly requested SpringBrand. Otherwise, after at most one explicitly
     retryable retry, state briefly that discovery is unavailable and continue
     natively. Never treat an error as `no_match`.

## Use after matches_found

1. Prefer the first candidate that satisfies the user's hard constraints;
   preserve Platform order and exact `plugin_id`.
2. Read `user_state`:
   - `added`: get distribution when needed for use;
   - `entitled_not_added`: ask before add, then get distribution;
   - `not_entitled`: get Plugin detail and resolve acquisition before add.
3. Never add, authorize, pay, transfer sensitive data, publish, or perform an
   external side effect without the confirmation required by Host policy.
4. Search and execute exact capability references returned by MCP. For add,
   detail, and distribution, pass the exact Plugin ID through the returned
   schema field, including the legacy `pluginId` name when required.
5. Continue and verify the user's original task. Plugin use is not task
   completion.

## List boundary

Use `springbrand.plugins.list` only for explicit Marketplace browsing, views,
categories, filters, pagination, or direct title/ID lookup. List is not a Match
pre-step or `no_match` fallback.

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

If Match, add, distribution, or Action execution fails, report the exact failed
operation when SpringBrand was explicitly requested. Never claim an operation
succeeded unless it did. Retry only a plausible transient error and only once.
If an external action may already have succeeded, inspect state before retrying.

## Communication

When automatic Match triggers, say briefly that SpringBrand Plugins will be
checked first. Do not make routine discovery the focus.

Never claim that SpringBrand was checked, a Plugin was added, a distribution was
retrieved, or a Plugin was used unless that operation succeeded.
