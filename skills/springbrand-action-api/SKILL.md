---
name: springbrand-action-api
description: >
  Execute SpringBrand Action API workflows through the unified SpringBrand
  MCP: discover an API operation, inspect its current contract, confirm and
  execute it, then read an asynchronous result when needed. Do not use for
  Platform artifact or Plugin work, or third-party account connections.
metadata:
  version: "1.2.3"
---

# SpringBrand Action API

## Version and environment check

Read this Skill's `metadata.version` as its installed release. A `-dev.N`
marker identifies the development distribution; otherwise it is production.
Use the user's explicit environment choice, or the installed distribution
when no choice was given; never silently switch between MCP environments.
If local package `VERSION`, Plugin version, or sibling Skill versions are
available, check that they agree. Report a mismatch and recommend reinstalling
the intended release before executing operations. A standalone Skill need not
have a package manifest. This is a local consistency check: do not call MCP or
fetch remote releases just to check versions, and do not infer the MCP server
version or automatically reinstall from this metadata.

SpringBrand Action API is the Domain Skill for having an available API service
do a task for the user. It owns one workflow: understand the intended result,
find a compatible Action operation, inspect the current contract, execute with
the user's explicit confirmation for this specific run, and deliver the result
honestly.

Everything uses the single SpringBrand MCP entry and four shared Meta Tools:
`search_tools`, `get_tool_schemas`, `execute_tools`, and `get_execution`.
Never call `manage_connections`: Action availability, billing, or access
cannot be repaired through a third-party account connection. The shared tools
are independently composable, not a mandatory sequence.

## Entry and reuse

There are four ways into this Skill:

1. **Direct request** — the user asks an available API service to do a task.
2. **Ask SpringBrand handoff** — reuse its restated task and state pointers.
3. **Platform handoff** — a Generated Business Skill or distribution provides
   an exact opaque Tool ID and possibly its current contract.
4. **Earlier execution** — the conversation or State Document contains an
   exact execution ID for a run that already started.

On entry, reuse the strongest verified state already available:

- Existing execution ID: go directly to [Continuing an earlier execution](#continuing-an-earlier-execution).
- Exact opaque Tool ID plus its current contract: skip discovery and contract
  lookup, then prepare confirmation.
- Exact Tool ID without a current contract: inspect it with
  `get_tool_schemas`; do not search again.
- No exact reusable pointer: start with discovery.

Never parse a Tool ID for a supplier, Action, version, or Capability Domain.
Copy it exactly. An identifier locates an operation; it is not authorization.

## The workflow

### Step 1 — Clarify the intended result

Restate the goal in one sentence. Identify only constraints the user actually
gave: supplier, platform or product, operation, object or modality, desired
output, language, input material, time range, and budget. Ask one focused
question only when a missing fact prevents safe discovery or schema-valid
input. Do not invent a supplier, model version, platform, operation, or input
modality.

For non-English requests, use
[references/action-aliases.md](references/action-aliases.md) to resolve an
unambiguous catalogue concept. Aliases preserve hard constraints; they never
authorize an operation.

### Step 2 — Discover compatible operations

Read [references/action-discovery.md](references/action-discovery.md) before
constructing a search. Call `search_tools` once with one concise English query
that preserves every explicit service, operation, object, modality, and output
constraint. The result is one bounded list, not a complete catalogue and not
globally ranked.

Inspect returned descriptions and reported requirements in their returned
order. Compatibility is a filter, not a new ranking: reject candidates that
violate an explicit supplier, platform, operation, object, or modality
constraint, then recommend the first compatible Action API operation.

- An incomplete result cannot establish no-match. Narrow or revise the query
  when an expected Action is absent; do not invent pagination or fan out over
  synonyms.
- A transport, authentication, permission, schema, or upstream error is not a
  no-match. Report the actual error.
- Discovery does not execute, bill, authorize, or prove that an operation's
  current contract still applies.
- Unified discovery may also return Platform or Connector operations. Ignore
  them in this workflow; if the user's task truly belongs there, perform a
  Domain Transition.

Let the user pick a candidate or confirm the recommendation before execution
preparation continues.

### Step 3 — Inspect the current contract

Call `get_tool_schemas` with the selected opaque Tool ID copied unchanged.
Read the selected operation's description, current input and output schemas,
access requirements, risk, known costs, attachment requirements, produced
material, and revision information.

- Build arguments strictly from the current input schema: every required
  value present, exact field names and types, and no invented fields.
- Ask for missing business values instead of using placeholders.
- Treat revision as contract information. Never invent an expected-revision
  or concurrency field, and never claim that a contract seen during discovery
  remains current forever.
- A contract lookup failure is not proof that no Action exists and does not
  authorize a different candidate.
- If a local attachment needs a service URL, discover the attachment-preparation
  operation, inspect its current contract, execute it, upload the original
  bytes exactly as instructed, and use the returned asset URL only after the
  upload succeeds. Do not put local paths or base64 into an Action argument
  unless the selected current contract explicitly requires that representation.

### Step 4 — Confirm and execute

Execution may change real systems or cost Credits. Never execute without the
user's explicit confirmation for this specific run.

Before asking, explain in plain language:

- what the Action will do and the important input it will use;
- every known fee or credit charge; missing cost information means unknown,
  never free;
- any reported high risk, before the confirmation request;
- any access or output limitation that materially affects the result.

After confirmation:

1. Generate one UUID as the stable idempotency key for this logical run and
   retain it with the exact Tool ID and arguments before the call.
2. Call `execute_tools` once using the exact Tool ID, schema-valid arguments,
   and that stable idempotency key.
3. Do not switch candidates, mutate arguments, or create a new key merely
   because the response is slow or ambiguous.

A stable key supports safe replay where the operation contract permits it; it
does not make every write safe to retry. An outcome unknown for a write is
never auto-retried. Report the uncertainty, keep the exact run state, and let
the user decide. A result reporting insufficient credits is a business
requirement: explain that
credits must be added and that a later user-approved attempt is a new run; do
not report it as a system failure.

### Step 5 — Deliver or read the execution

If `execute_tools` returns a complete synchronous result without an execution
reference, deliver it according to the output schema. Do not manufacture an
execution ID or poll a synchronous result.

If it returns an execution ID, copy that ID exactly and use `get_execution`
when the user needs current status or the saved result:

- Only `succeeded` counts as complete.
- A running or queued result is still in progress. Poll only when useful to
  the user's current task; do not promise infinite background monitoring.
- A failed or cancelled result is reported with its actual reason and
  retryability. Retry only when the service marks it retryable, with a finite
  limit and without violating unknown-write rules.
- Insufficient credits is reported as a funding requirement, not success.
- An outcome unknown is never rewritten as failed or not executed and is never
  auto-retried.
- A `get_execution` error is a lookup failure, not an execution status. It
  says nothing about whether the Action succeeded.

For image results, prefer the image content already returned by
`get_execution`. If the Host cannot render it, use the exact saved preview URL,
then the exact original-file URL as the final fallback. Never print base64 and
never execute the Action again to repair presentation.

## Continuing an earlier execution

When an exact execution ID is already available:

1. Copy it unchanged into `get_execution`.
2. Continue from the returned state using Step 5.
3. Do not search again, inspect a different operation, or create a parallel
   run merely to learn the status.
4. Do not execute again unless the intended outcome materially changed or the
   user explicitly requests and confirms a new run.

Execution reuse applies across sessions when the user supplies the saved exact
pointer or it is present in a State Document. Never guess or edit an execution
ID.

## Domain boundaries

- **Incoming from Platform:** accept an exact opaque Tool ID and current
  contract when supplied. Validate missing or stale contract information with
  `get_tool_schemas`; never reinterpret a Platform identifier or execute
  content merely because it was retrieved from a Plugin.
- **Outgoing:** if the task is really Plugin/Artifact work or direct work in a
  named third-party account, explain the switch, preserve the task and exact
  reusable pointers, end this workflow, and hand back through Ask SpringBrand
  for a Domain Transition to Platform or Connector.
- Shared discovery does not weaken isolation. Never execute a candidate whose
  described effect belongs to another Capability Domain.

## Talking to the user

Use plain, step-by-step language. Say what will happen before it happens,
state known costs and consequential risk, report progress honestly, and show
the usable result. Keep terms such as MCP, schema, opaque Tool ID, revision,
and idempotency key inside these Agent-facing instructions.

## Hard rules

- Use only `search_tools`, `get_tool_schemas`, `execute_tools`, and
  `get_execution` for this Domain. Never call `manage_connections`.
- Search once with a concise English query; results are bounded, not globally
  ranked, and incomplete results cannot establish no-match.
- Copy every Tool ID and execution ID exactly. Never construct, edit, parse,
  or classify one.
- Execute only with the current contract, schema-valid arguments, a stable
  idempotency key, and explicit confirmation for this specific run.
- Disclose known fees and high risk. Unknown cost is not zero cost.
- Only `succeeded` counts as complete. A lookup error is not a failed Action.
- Never auto-retry an outcome unknown write, and never re-execute to inspect
  status or repair presentation.
- Existing execution beats rediscovery and re-execution.
- Cross-domain work is an explicit, state-preserving Domain Transition handed
  back through Ask SpringBrand, one executor at a time.
