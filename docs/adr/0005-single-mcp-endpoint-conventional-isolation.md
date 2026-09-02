# Register one MCP entry per Host manifest with domain-prefixed tool namespaces

The Gateway exposes one user-connectable MCP endpoint, `/mcp`, backed by a unified server that re-publishes all three Domain Executor registries under frozen tool-name prefixes (Gateway ADR-0014). Each Host Adapter declares exactly one named OAuth MCP entry — `springbrand` → `https://connector.springbrand.ai/mcp` (production), `springbrand-dev` → `https://devconnector.springbrand.ai/mcp` (development) — whose `tools/list` carries all three domains under the frozen prefixes: `platform_list_capabilities`, `platform_execute_capability`, `action_match_capabilities`, `action_list_capabilities`, `action_get_capability`, `action_execute_capability`, `action_get_execution`, `connector_search_capabilities`, `connector_execute_capability`. Capability references are unchanged (`platform:` / `action:springbrand@0:` / `connector:`). Domain isolation is conventional: Skill constraints plus the prefix naming, not separate servers.

## Decision context and QA evidence

Hosts walk OAuth per MCP server, not per user. With three connectable entries per manifest, every install ran three full browser authorizations: 2026-09-02, `v1.2.0-beta.7-dev.1` — Codex desktop consented three times from a clean install, and Devin (cloud-isolated authorization context, no reusable session carrier) still consented three times even after the Gateway's shared-consent fixes. No Plugin-side or Gateway-side mechanism can reduce the flow count while the external surface is three MCP servers. The OAuth UX cost of three entries exceeds the structural isolation benefit of exposing them separately.

## Decisions

- **One entry per manifest.** This amends ADR-0003: the three named per-domain entries (`springbrand-platform` / `springbrand-action-api` / `springbrand-connector` and their `springbrand-dev-*` dev variants) are replaced by the single entry above. No extra SpringBrand entries are declared.
- **Frozen prefixes.** Tool selection is by domain prefix; a Domain Skill names its prefix in instructions and never calls another domain's prefixed tools. The Ask SpringBrand router maps intent to exactly one prefix.
- **Conventional isolation.** A cross-domain need is served by an explicit Domain Transition — announced, state-preserving, handed back through Ask SpringBrand — never by calling another domain's prefixed tool. `capability_domain_mismatch` keeps its `recovery.domain` semantics.
- **One OAuth consent.** Install guides disclose a single consent per Surface; the per-entry consent counts are removed.
- **Companion decision.** Gateway ADR-0014 records the Gateway-side unification, the QA evidence, and the deprecation of the three per-domain subroutes; the internal executor boundaries are unchanged.

## Consequences

- Package validators assert exactly one MCP entry per manifest (single URL, single OAuth client); legacy three-entry manifests and any extra entry fail validation.
- The Cursor duplicate-tool-name risk is structurally reduced: tool names are unique across domains, so the former cross-entry name-collision mitigation (per-entry naming) is replaced by prefix-based tool-isolation scoring (target zero violations in the routing corpus).
- The three per-domain subroutes remain available but deprecated during the transition; manifests no longer reference them, and their retirement follows the Gateway release flow.
- The routing corpus's DOMAIN_SELECT and TOOL_ISOLATION classes are redefined on the prefix model; TRANSITION keeps its scored semantics (announcement, state preservation, prior workflow ended, one executor at a time).
