# Consume five shared Meta Tools while preserving three Domain Skills

The SpringBrand MCP now exposes five stable Meta Tools instead of registered
tools grouped under Platform, Action API, and Connector name prefixes. The
SpringBrand Skill Set will consume that shared interface while retaining its
three user-facing Capability Domains.

This decision supersedes ADR-0005's frozen domain-prefix contract and the
tool-selection portions of ADR-0002. ADR-0002's four-Skill architecture,
non-executing Ask SpringBrand guide, one-Domain-Skill-at-a-time rule, and
explicit Domain Transition remain binding. ADR-0004's Artifact Workspace,
State Document, create-only Creation, and publication rules also remain
binding.

## Decisions

- **Shared interface, separate responsibilities.** Platform, Action API, and
  Connector use the same discovery, contract lookup, execution, and saved
  result tools. A Domain Skill selects only operations that serve its own
  user-facing workflow; a shared MCP interface does not merge the domains.
- **Connector owns connections.** Only the Connector Domain Skill lists,
  starts, checks, repairs, or disconnects third-party account connections.
  Platform eligibility, Plugin acquisition, Action billing, and service
  outages are not connection-management problems.
- **Opaque identifiers.** Skills copy Tool, execution, connection, and
  authorization-attempt identifiers exactly. They do not construct, edit,
  parse, or classify identifiers, and old readable capability references are
  not a compatibility execution path.
- **No mandatory pipeline.** The five tools are independently composable.
  Discovery, contract inspection, connection management, execution, and
  saved-result reads occur only when the user's task needs them. An existing
  current contract or execution pointer is reused rather than rediscovered.
- **Execution safety.** Execution uses the current operation contract,
  schema-valid arguments, and a stable idempotency key for one logical run.
  Action API and Connector executions keep their per-run confirmation gate;
  Platform keeps its existing operation-specific risk, cost, upload,
  publication, removal, acquisition, and Host approval rules. Unknown writes
  are never automatically repeated.
- **Ask remains non-executing.** Ask SpringBrand chooses a Capability Domain
  from user intent and local workflow state, hands off, and stops. It does not
  call any Meta Tool or validate an opaque identifier.
- **Generated mirrors only.** Canonical Skills and references remain the
  semantic source. Cursor and WorkBuddy copies are regenerated with the
  repository repair scripts and remain byte-equivalent.
- **Maintenance posture.** This migration uses focused changes and the
  smallest necessary regression tests. It does not anticipate a future CLI
  with abstractions, dual paths, or compatibility layers.

## Consequences

The repository's manifests keep one SpringBrand MCP entry and retain their
existing production/development identity rules. Skills no longer teach
domain-prefixed registered tool names or readable capability-reference
formats. A unified search may return operations outside the active Domain;
the current Domain Skill ignores those results or performs an explicit,
state-preserving Domain Transition instead of executing across domains.

The Gateway remains authoritative for Meta Tool inputs, outputs, identifiers,
runtime routing, access checks, costs, and execution status. This public
repository records Agent behavior and references that authority; it does not
duplicate endpoint details, wire schemas, response projections, or internal
collection contracts.
