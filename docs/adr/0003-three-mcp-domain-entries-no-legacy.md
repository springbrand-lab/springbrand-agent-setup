# Register three MCP Domain Entries per Host manifest and no legacy entry

> Amended 2026-09-02 by ADR-0005: Host manifests now register a single MCP
> entry whose tools carry frozen domain prefixes; the three-entry rule below
> is superseded. This record is kept for the naming rationale and the legacy
> decision history.

The Gateway serves three Domain Executors plus a deprecated-but-functional Legacy Aggregate entry (`/mcp`). Each Host Adapter declares exactly three named OAuth MCP entries mapped one-to-one to the Executors — `springbrand-platform` → `/mcp/platform`, `springbrand-action-api` → `/mcp/action-api`, `springbrand-connector` → `/mcp/connectors` — and never declares or selects the legacy entry. Dev Adapters use `springbrand-dev-platform`, `springbrand-dev-action-api`, `springbrand-dev-connector` against `devconnector.springbrand.ai`.

## Decisions

- **Naming.** Entry names follow the Capability Domain vocabulary (singular Connector), not the Gateway path segments; the name↔path mapping is documented, not encoded. Names must let the Agent select a domain without tool-name inference (CONTEXT.md: MCP Domain Entry).
- **No legacy entry in new manifests.** Already-installed Plugin versions keep using `/mcp` via the Gateway Legacy Adapter until the user upgrades or the owner explicitly retires it (Gateway ADR-0009; retirement is Gateway Issue 12, owner-controlled, no automatic sunset).
- **Considered and rejected:** keeping a fourth legacy entry in new manifests (forbidden by Gateway ADR-0009; legacy service is Gateway-side, not Plugin-side); renaming Gateway tools per entry to avoid cross-entry tool-name collisions (the tool contract is already deployed).
- **OAuth.** All entries use standard SpringBrand MCP OAuth. OAuth is per endpoint on every Host: three entries mean up to three consents per Surface; install guides disclose this and Native Evidence records the real consent count.

## Consequences

- Claude, Codex, and WorkBuddy disambiguate shared tool names (`list_capabilities`, `execute_capability`) by server prefix; **Cursor's tool namespace is undocumented and has community-reported duplicate-tool-name misrouting**. Mitigation: Domain Skills always name their MCP entry in instructions, and Cursor Native Evidence adds an explicit cross-entry tool-selection test. The residual risk is accepted and recorded in Cursor evidence.
- Package validators assert exactly the three production entries (and the three `springbrand-dev-*` entries for the dev Adapter) with no extra servers and no credentials.
