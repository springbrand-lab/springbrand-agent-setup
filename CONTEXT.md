# SpringBrand Agent Plugin Distribution

This context defines how SpringBrand guidance and capability access are packaged and verified across native agent hosts without duplicating their behavior.

## Language

**Canonical Skill**:
One authoritative member of the SpringBrand Skill Set whose instructions all supported Hosts package without semantic divergence.
_Avoid_: Host Skill, Skill fork, maintained copy

**SpringBrand Skill Set**:
The four Canonical Skills shipped together: Ask SpringBrand and the Platform, Action API, and Connector Domain Skills.
_Avoid_: Monolithic Skill, Skill bundle, mixed workflow

**Ask SpringBrand**:
The user-facing Capability Guide that selects one Capability Domain, reports the current workflow position, recommends the next Domain Skill, and then stops without discovering or executing a capability.
_Avoid_: Executor, global discovery Skill, orchestrator

**Capability Domain**:
One SpringBrand application scenario with its own discovery, execution, and guidance authority: Platform, Action API, or Connector.
_Avoid_: Mode, global capability pool, mixed MCP surface

**Domain Skill**:
The Canonical Skill that owns the Agent workflow for exactly one Capability Domain and uses only that domain's MCP Domain Entry.
_Avoid_: Helper Skill, shared executor, cross-domain Skill

**MCP Domain Entry**:
A Host-visible MCP server registration connected to exactly one Gateway Domain Executor and named so the Agent can select that domain without relying on tool-name inference.
_Avoid_: MCP mode, aggregate server, global executor

**Domain Transition**:
An explicit handoff from one Domain Skill and MCP Domain Entry to another while preserving relevant task state and ending the prior domain workflow.
_Avoid_: Automatic forwarding, simultaneous discovery, multi-Skill activation

**Routing Notice**:
The short, static, network-free domain map delivered through a Host's Hook or Rule so an Agent can invoke Ask SpringBrand when the domain is uncertain.
_Avoid_: Prompt classifier, workflow instructions, execution Hook

**Host Adapter**:
The smallest host-native package that connects the SpringBrand Skill Set, MCP Domain Entries, Routing Notice, and lifecycle metadata to one plugin engine and configuration contract.
_Avoid_: Host implementation, generic plugin wrapper

**Surface**:
A user-facing runtime or UI that requires its own installation and behavior evidence but may share a Host Adapter with another Surface.
_Avoid_: Adapter, when only the UI or launch path differs

**Distribution Mirror**:
A generated, verified copy of Canonical Skills or other canonical assets required only when a Host marketplace demands a self-contained package directory.
_Avoid_: Source of truth, maintained copy

**Legacy Plugin Release**:
An already-installed SpringBrand Plugin version that continues to use the Gateway's Legacy Aggregate Entry until the user upgrades or explicitly chooses another migration action.
_Avoid_: Fourth domain, current Plugin, automatic sunset cohort

**Native Evidence**:
A recorded test performed through the host's own install, authentication, trust, update, and removal lifecycle.
_Avoid_: Schema validation, inferred support

**Artifact**:
The standard-format deliverable a user produces in the Platform workflow, shaped to pass Platform upload admission.
_Avoid_: Creation (that is the Platform-side resource), deliverable, output file

**Creation**:
The Platform-side resource that exists once an Artifact is uploaded; born private, made public only by an explicit publish, and never updated in place through the Platform domain.
_Avoid_: Artifact, upload copy, post

**Artifact Workspace**:
The local directory holding an Artifact's files together with its State Document; the source an upload is built from.
_Avoid_: Temp directory, project repo, scratch folder

**State Document**:
The human-readable Markdown record in an Artifact Workspace that names the current workflow step, the pointers gathered so far, and the next action; readable as plain file access, never through MCP.
_Avoid_: Journal, hidden metadata, embedded comment block

**Creation Pipeline**:
The Platform Skill's guided, user-checked flow from a stated goal to a published Creation: goal, resource showcase, generation, upload, publish.
_Avoid_: Auto-pipeline, wizard, background job

**Distribution Action Component**:
A Plugin distribution component that carries an executable dynamic Action rather than static content; it executes only through the Action API domain, reached by an explicit Domain Transition.
_Avoid_: Plugin feature, Platform capability, bundled tool
