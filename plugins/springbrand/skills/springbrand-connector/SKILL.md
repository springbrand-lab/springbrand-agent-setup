---
name: springbrand-connector
description: >
  Work with third-party systems through the unified SpringBrand MCP: discover
  an operation, inspect its current contract, manage a required account
  connection, confirm and execute, then read an asynchronous result when
  needed. Do not use for Platform artifacts, Plugins, or Action API services.
metadata:
  version: "1.2.3"
---

# SpringBrand Connector

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

SpringBrand Connector is the Domain Skill for reading or changing data in a
third-party system the user names, such as GitHub. It discovers only currently
available operations, verifies the current contract and connection state,
executes with the user's explicit confirmation for this specific run, and
reports the result honestly.

Everything uses the single SpringBrand MCP entry and the five shared Meta
Tools: `search_tools`, `get_tool_schemas`, `manage_connections`,
`execute_tools`, and `get_execution`. They are independently composable; do
not call every tool when the task already has the information it needs.

## Security boundary

Third-party account connections and Provider Credential handling belong to the
authoritative connection service, not this Skill. A Provider Credential must
never appear in Skill text, conversation output, a State Document, logs,
errors, URLs constructed by the Agent, test data, or MCP output. Never ask the
user to paste one, never read or store one, and never place one in operation
arguments.

Use only authorization links and identifiers returned by
`manage_connections`. Those are workflow pointers, not credentials. Never
construct an authorization URL or append secrets or identity fields to one.

## Entry and reuse

On entry, scan the conversation and any handed-off state:

- Existing execution ID: continue with `get_execution`; do not discover or
  execute again.
- Exact opaque Tool ID plus its current contract: reuse both.
- Exact Tool ID without a current contract: inspect it with
  `get_tool_schemas`; do not search again.
- Existing connection or authorization-attempt pointer: verify it through
  `manage_connections` only when the current task needs that connection.
- No usable pointer: begin with discovery.

Copy every Tool ID, execution ID, service ID, connection ID, authorization
attempt ID, and returned cursor exactly. Never parse an identifier for a
service, account, operation, or Capability Domain.

## The workflow

### Step 1 — Discover the third-party operation

Call `search_tools` once with one concise English query that names the target
service, operation, object, and output constraints the user actually gave.
Discovery returns one bounded list; it is not globally ranked and is not a
complete catalogue.

- Preserve returned order while rejecting candidates that violate explicit
  service or operation constraints.
- An incomplete result cannot establish no-match. Narrow or revise the query
  when an expected operation is absent; do not invent pagination.
- A transport, authentication, permission, schema, configuration, or upstream
  error is not a no-match. Report the actual failure.
- Do not advertise a service or operation that current discovery did not
  return. Code or historical documentation is not proof of user availability.
- Unified discovery may return Platform or Action API operations. Ignore them
  here and use a Domain Transition if the user's task belongs there.

Present compatible operations in plain language and let the user select or
confirm the recommendation.

### Step 2 — Inspect the current contract

Call `get_tool_schemas` with the selected opaque Tool ID unchanged. Read its
description, exact input and output schemas, risk, known cost, access
requirements, supported account selection, and current connection requirement.

- Build arguments strictly to the current input schema. Ask for missing
  business values instead of guessing or using placeholders.
- Contract lookup does not execute or authorize the operation.
- Contract or access failure does not authorize silently choosing another
  operation.
- Connection requirements come from the current contract and returned access
  information, never from a guessed service mapping.

### Step 3 — Establish or select a connection when required

Use `manage_connections` for exactly one of list, start, status, and disconnect
at a time:

- **List** when the user asks about connections or the current contract allows
  account selection and an exact active connection is not already known.
- **Start** only when the user explicitly asks to connect, or the authorized
  operation requires it. Use the exact returned service ID. If the service is
  not authorizable or operator configuration is missing, stop and report that
  boundary; this tool cannot repair service outages or configuration.
- **Status** uses the exact authorization attempt ID returned by start. Show
  the returned authorization link to the user when provided, then pause for
  their Provider-side action. Pending is not connected. Continue only after
  the authoritative status says the connection is active.
- **Disconnect** uses the exact connection ID and runs only after the user
  explicitly requests and confirms disconnection. Never disconnect as cleanup
  or as an error-recovery guess.

When a connection lacks required permission or is invalid, explain that the
user must repair or reauthorize it. Do not retry execution first and do not ask
for a Provider Credential. Reconnect only through returned connection
management guidance and preserve account choice when the contract supports it.

### Step 4 — Confirm and execute

Never execute a third-party operation without the user's explicit confirmation
for this specific run. Before asking, state the target service and account when
known, the operation, important inputs, every known cost, and any reported high
risk. Unknown cost is not free.

After confirmation:

1. Generate and retain one UUID as the stable idempotency key for this logical
   run, together with the exact Tool ID, arguments, and selected connection ID
   when the current contract supports account selection.
2. Call `execute_tools` once with the exact values required by its runtime
   schema.
3. Never invent identity, Project, Session, credential, approval, or connection
   fields.

A stable key does not make every write safe to retry. If a write has an outcome
unknown, never auto-retry. Report that the effect could not be confirmed,
preserve the exact run state, and let the user decide. A safe read may be
retried only when the service marks the failure retryable and the operation's
current contract permits it.

### Step 5 — Deliver or read the execution

Deliver a complete synchronous result using its output schema. When execution
returns an exact execution ID, use `get_execution` to read current status or a
saved result without executing or charging again.

- Only `succeeded` confirms completion.
- Running or queued remains in progress; poll only when useful to the current
  task.
- Failure, cancellation, access loss, or other terminal state is reported as
  returned, not hidden or rewritten as no-match.
- An outcome unknown remains uncertain and is never auto-retried.
- A result lookup error is a lookup failure, not proof of execution failure.
- A synchronous result without an execution ID cannot be polled.

## Connection repair boundary

Connection repair is a user authorization workflow, not an execution retry:

1. Explain the missing or invalid access in plain language.
2. Use `manage_connections` with the exact returned identifier and action only
   after the user agrees to repair it.
3. Present the returned authorization link and pause while the user acts in the
   Provider UI.
4. Verify the exact attempt with status. Do not infer success from the user's
   browser returning or from elapsed time.
5. Ask for a fresh execution confirmation after repair; do not reuse an old
   confirmation for a new invocation.

## Domain boundaries

- Connector owns third-party operations and their connection lifecycle. It
  does not acquire Plugins, upload or publish Artifacts, or select dynamic API
  services from the Action API catalogue.
- Platform and Action API eligibility, billing, or failures are not repaired
  with `manage_connections`.
- If the task belongs to another domain, explain why, preserve the task and
  exact reusable pointers, end this workflow, and hand back through Ask
  SpringBrand for an explicit Domain Transition.
- One executor at a time: never execute another domain's operation from this
  Skill even when unified discovery returned it.

## Talking to the user

Use plain language: name the service and effect, explain when authorization is
needed, pause for Provider-side action, and report success only when confirmed.
Keep MCP, schema, opaque identifiers, and idempotency details inside these
Agent-facing instructions.

## Hard rules

- Use the five shared Meta Tools only for Connector work.
- Search with one English query. Results are bounded, not globally ranked, and
  incomplete results cannot establish no-match.
- Copy exact opaque identifiers; never construct, edit, parse, or classify
  them.
- Use `manage_connections` only from an explicit user request or a current
  operation requirement. Pending authorization is not an active connection.
- Provider Credential data is never requested, handled, logged, placed in a
  URL, or surfaced to the user.
- Execute only with the current contract, schema-valid arguments, a stable
  idempotency key, and explicit confirmation for this specific run.
- Disclose high risk and known cost. Never auto-retry an outcome unknown write.
- Use `get_execution` only for an exact existing execution ID; never re-execute
  to inspect status.
- Cross-domain work is an explicit, state-preserving Domain Transition handed
  back through Ask SpringBrand.
