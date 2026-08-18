# SpringBrand native host integration research

> **Decision status:** Historical research input. [ADR-0001](../adr/0001-native-host-plugin-adapters.md) supersedes this document where scope or distribution recommendations differ; `1.2.0` targets Cursor desktop only and uses native GitHub Marketplace import.

- **Verified:** 2026-08-17
- **Scope:** Claude Code CLI and Claude Desktop Code tab, Cursor desktop and CLI, Tencent WorkBuddy desktop
- **Evidence policy:** official product documentation, first-party repositories, and first-party release notes only; unsupported or undocumented behavior remains `unknown` until native testing.

## Decision-ready comparison

| Host surface | Native plugin | Skill | Remote HTTP MCP + OAuth | Pre-prompt Hook | Native distribution | Research verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code CLI | Supported | Supported | Supported | `UserPromptSubmit` supported | Git/GitHub Marketplace repository, then plugin install | Ready for a single Claude Code adapter. |
| Claude Desktop **Code tab** | Same Claude Code plugin engine and core local config as CLI | Supported | Supported at engine/config level; GUI-only OAuth remains to test | Same hook model | Configured Marketplace + desktop plugin UI | Treat as a second evidence surface, not a second adapter. |
| Cursor desktop | Supported | Supported | Supported | `beforeSubmitPrompt` supported | Public or Team Marketplace; local dev plugin | Adapter is feasible. Hook behavior differs from Claude and cannot rewrite the prompt. |
| Cursor CLI | Plugin manager and Skills supported; full component parity unknown | Supported | Protocol/config supported; interactive OAuth flow unknown | CLI support for `beforeSubmitPrompt` unknown | CLI lifecycle for arbitrary repository installs unknown | Keep as a separate acceptance surface with blockers, not assumed parity. |
| Tencent WorkBuddy desktop | Supported | Supported | Supported (`type: "http"`) | Plugin Hooks supported; `UserPromptSubmit` is shared-engine evidence and needs desktop validation | WorkBuddy Marketplace; repository address syntax needs testing | Adapter is feasible, with Hook trust and exact marketplace lifecycle as blockers. |

## Package-boundary implications

1. **Claude:** one Claude Code adapter should cover CLI and the Claude Desktop Code tab because Anthropic documents the same engine, plugin system, and shared core configuration. CLI and desktop still require separate native evidence.
2. **Cursor:** desktop is the proven plugin host. Cursor CLI must not inherit desktop claims for Plugin components, MCP OAuth UX, or `beforeSubmitPrompt` until tested.
3. **WorkBuddy:** use the Tencent CodeBuddy/WorkBuddy product, not unrelated same-name projects. Target WorkBuddy 5.3.5+ for Plugin Hook availability and validate on 5.3.13.
4. **Shared implementation:** reuse the canonical SpringBrand Skill and `https://connector.springbrand.ai/mcp`; add only host-specific manifests, Marketplace metadata, and verified Hook definitions. Do not create a shared multi-host abstraction before repeated behavior exists in two implemented adapters.

## AgentKey reference repository

Inspected [`chainbase-labs/AgentKey`](https://github.com/chainbase-labs/AgentKey) at commit `efc28096918b8565d495cacb6864b17f59cc7214` (2026-08-14) and ran its full Bats suite: **29/29 passed**.

Reusable precedent:

- one canonical `skills/agentkey/` tree is referenced by separate Claude, Codex, and Cursor manifests;
- host MCP schemas remain explicit: Claude uses root `.mcp.json`, Codex uses `.codex-plugin/mcp.json`, and Cursor declares its server inline;
- all native OAuth declarations are credential-free and endpoint-only;
- version and endpoint drift are CI failures rather than a runtime abstraction;
- bundled MCP guidance authenticates the existing plugin server instead of registering a duplicate.

Limits that SpringBrand must not copy blindly:

- AgentKey has no routing Hooks, so it does not resolve SpringBrand's preflight or Hook-trust requirements;
- AgentKey's closed PR #93 records that Cursor's GitHub indexer found zero plugins when Marketplace `source` pointed at the repository root; Cursor's official template instead uses a self-contained nested plugin directory;
- AgentKey's custom all-agent installer, telemetry, update checker, and API-key fallback solve AgentKey-specific compatibility needs and are outside SpringBrand's native-Plugin scope.

The resulting architecture decision is recorded in [ADR-0001](../adr/0001-native-host-plugin-adapters.md).

## Detailed evidence

- [Claude native integration capabilities](./claude-native-integration-capabilities.md)
- [Cursor native integration capabilities](./cursor-native-integration-capabilities.md)
- [WorkBuddy native integration capabilities](./workbuddy-native-integration-capabilities.md)
