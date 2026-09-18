# Platform and Plugin discovery through the unified Meta Tools

Read this reference when the Platform Skill needs to find a Plugin or Platform
operation. It records Agent behavior only; the runtime MCP schema and returned
current contract are authoritative.

## One bounded search

Use `search_tools` with one concise English query. Translate a non-English
request yourself while preserving explicit Artifact type, subject, workflow,
audience, and desired output constraints. Remove SpringBrand host names,
courtesy language, and generic words that do not distinguish the needed Plugin
or Platform operation.

Issue one search, not a synonym fan-out. The response is one bounded list. It
is not globally ranked, not a complete Marketplace, and has no search
pagination for the Agent to invent.

Useful query shapes include:

- `[artifact type] [subject] [workflow]`
- `retrieve SpringBrand Plugin for [specific task]`
- `upload SpringBrand Creation`
- `publish SpringBrand Creation version`
- `list my SpringBrand Creations`

Use only constraints the user actually supplied. Do not inject a category,
format, audience, or publication intent merely to improve recall.

## Interpret results

Preserve returned order while checking actual fit. A result is compatible only
when its description and requirements can satisfy the user's explicit task.
Scores or list position are not task-success probabilities.

Keep these outcomes distinct:

- **Fitting result** — preserve its opaque Tool ID exactly and inspect the
  current contract with `get_tool_schemas`.
- **Complete empty or incompatible result** — report no fit for this query, or
  revise it once when a more precise version follows directly from the user's
  stated constraints.
- **Incomplete result** — it cannot establish no-match. Narrow or revise the
  query; do not claim that the Marketplace has no fit.
- **Provider or tool failure** — report the actual transport, authentication,
  permission, schema, or upstream failure. An error is not a no-match and must
  not trigger a fallback presented as success.

Unified discovery can include Action API and Connector operations. Ignore them
inside Platform. If the user's real task belongs there, use an explicit Domain
Transition rather than executing across domains.

## Plugin retrieval is not Plugin use

A discovered Plugin operation may retrieve instructions, components, or files.
That effect does not:

- install or run the Plugin;
- add or purchase it;
- execute a Generated Business Skill or Action;
- upload or publish the user's Artifact;
- complete the task described by the retrieved content.

Follow retrieved usage instructions only within the user's authorized task and
the Platform Skill's cost, risk, and Domain boundaries.

## Current contract and related operations

Send exact discovered Tool IDs to `get_tool_schemas`. The current contract is
the authority for description, input/output schemas, risk, known cost, access
state, and related operations.

The Plugin lifecycle may need distinct effects: inspect current Plugin facts,
add, retrieve a distribution, remove, or rate. Upload, list Creations, and
publish a selected version are also distinct Platform effects. Use the exact
opaque Tool ID returned for each effect; never derive one ID from another,
from a Plugin title, or from this reference.

Contract inspection does not execute or authorize an operation. A failed
lookup does not prove the Plugin or operation is absent and does not authorize
silently switching to another candidate.

## Execute within the lifecycle

Call `execute_tools` only after the Platform Skill has applied the selected
operation's current schema, access, cost, risk, and confirmation rules. Every
logical invocation uses one stable idempotency key retained before the call.
The current operation description defines success: retrieving content is not
equivalent to applying it, adding is not purchasing, upload is private, and
publication is a separate public action.

Only use `get_execution` when execution returns an exact non-null execution
ID. A synchronous Platform result cannot be polled. Reading a saved result does
not repeat the operation or authorize a follow-up action.
