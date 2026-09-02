# SpringBrand Agent Setup

Install SpringBrand Production from the repository `main` branch through each supported Host's native Plugin lifecycle, or use the documented Skill-plus-MCP fallback on other Agents.

SpringBrand ships four Canonical Skills and three MCP Domain Entries per environment:

| Skill | Role | MCP entry |
| --- | --- | --- |
| `ask-springbrand` | Ask SpringBrand — non-executing Capability Guide | none |
| `springbrand-platform` | Platform — create/publish artifacts, Plugin lifecycle | `springbrand-platform` |
| `springbrand-action-api` | Action API — dynamic API service execution | `springbrand-action-api` |
| `springbrand-connector` | Connector — third-party systems (GitHub in v1) | `springbrand-connector` |

## Quick start

SpringBrand has two environments. Pick the one you need and paste the matching prompt into your Agent (Cursor, Claude Code, Codex, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent).

### Production

> Install or update SpringBrand Production by following https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.md. Identify this Agent, use the matching Host guide, detect whether SpringBrand is already installed, refresh the existing Marketplace/Plugin in place when updating, prefer native OAuth, preserve existing configuration, and pause only for UI or OAuth steps I must complete.

[`INSTALL.md`](./INSTALL.md) is the universal production protocol. `main` is the sole rolling production installation channel; production users should not use the legacy `stable` branch or a version tag. The production MCP servers require Host-native OAuth — up to three consents per Surface (one per entry).

### Development

> Follow the official SpringBrand development installation guide to complete setup:
> https://github.com/springbrand-lab/springbrand-agent-setup/blob/v1.2.0-beta.7-dev.1/INSTALL.dev.md
> Use the native `springbrand-dev` Plugin on Codex, Claude Code/Desktop Code, Cursor, or WorkBuddy. Use the documented Skill-plus-MCP fallback only on unsupported hosts. Preserve unrelated configuration, complete native OAuth for each of the three entries, verify the installation, and tell me whether I need to restart.

The native development Plugin is the immutable prerelease [`v1.2.0-beta.7-dev.1`](https://github.com/springbrand-lab/springbrand-agent-setup/releases/tag/v1.2.0-beta.7-dev.1). It is identified as `springbrand-dev`, displays as **SpringBrand Dev**, and bundles three `springbrand-dev-*` MCP servers at `https://devconnector.springbrand.ai/mcp/{platform,action-api,connectors}`. Authentication is host-native OAuth — up to three consents per Surface (one per entry).

Disable or uninstall the full production `springbrand` Plugin before enabling the full development Plugin. Both package the same four Canonical Skills and three-domain routing behavior, so enabling both can duplicate routing and make connector selection ambiguous. The manual fallback remains available for unsupported hosts and may coexist with production because it shares the same Skill files and adds only the separately named `springbrand-dev-*` MCP entries.

### Production vs Development

| | Production | Development |
| --- | --- | --- |
| Install guide | [`INSTALL.md`](./INSTALL.md) | [`INSTALL.dev.md`](./INSTALL.dev.md) |
| MCP entry names | `springbrand-platform`, `springbrand-action-api`, `springbrand-connector` | `springbrand-dev-platform`, `springbrand-dev-action-api`, `springbrand-dev-connector` |
| MCP URLs | `https://connector.springbrand.ai/mcp/{platform,action-api,connectors}` | `https://devconnector.springbrand.ai/mcp/{platform,action-api,connectors}` |
| OAuth consents per Surface | up to 3 | up to 3 |
| Purpose | Everyday use | Testing only |
| Full Plugins can coexist | No | No — disable one before enabling the other |
| Manual Skill-plus-MCP fallback can coexist | Yes | Yes — it shares the same Skills and uses separate MCP names |

Both environments share the same four Canonical Skills (`ask-springbrand`, `springbrand-platform`, `springbrand-action-api`, `springbrand-connector`). Development is for testing only and should not be used as a production configuration.

## What gets installed

- **Codex Plugin (beta)** — packages the four Canonical Skills, three production MCP declarations, and static preflight Hook for supported macOS Codex hosts.
- **Claude Code Plugin (beta)** — packages the same four Skills, three native OAuth-backed production MCP entries, and static preflight Hook for Claude Code CLI and the Claude Desktop Code tab; see [`INSTALL.claude.md`](./INSTALL.claude.md).
- **Cursor Plugin (beta)** — packages generated, verified Distribution Mirrors of all four Skills with three native OAuth-backed production MCP entries and an always-applied preflight Rule for Cursor desktop; see [`INSTALL.cursor.md`](./INSTALL.cursor.md).
- **WorkBuddy Plugin (beta)** — a WorkBuddy Agent installs it through the bundled CLI; **Add Marketplace** remains the manual fallback; see [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md).
- **SpringBrand Dev Plugin (prerelease)** — packages the same four Skills and three `springbrand-dev-*` MCP entries for internal testing against `https://devconnector.springbrand.ai/mcp/{platform,action-api,connectors}`; see [`INSTALL.dev.md`](./INSTALL.dev.md).
- **Skill-plus-MCP fallback** — the four user-level Skills and three remote MCP entries for unsupported hosts.

Both MCP environments require native OAuth before normal use. No Plugin contains static credentials or authorization headers.

## Distribution channels

| Environment | Installation channel |
| --- | --- |
| Production | `https://github.com/springbrand-lab/springbrand-agent-setup` (`main`) |
| Development | `springbrand-lab/springbrand-agent-setup@v1.2.0-beta.7-dev.1` |

Production always follows `main`. Immutable production tags remain release and
evidence records, not the default installation channel. Development Plugins
are published only as immutable dev tags and are never merged into `main`.

## Repository layout

```
springbrand-agent-setup/
├── README.md                          # this file — for humans
├── INSTALL.md                         # the production installation protocol — for Agents
├── INSTALL.dev.md                     # the development installation protocol — for Agents
├── VERSION                            # current release version
└── skills/
    ├── ask-springbrand/SKILL.md       # Ask SpringBrand — non-executing Capability Guide
    ├── springbrand-platform/SKILL.md  # Platform Domain Skill
    ├── springbrand-action-api/SKILL.md # Action API Domain Skill
    └── springbrand-connector/SKILL.md # Connector Domain Skill
```

`INSTALL.md` and `INSTALL.dev.md` are the core product. They are written to be read and executed by an Agent. The Skill sources live in `skills/<machine-name>/SKILL.md` and are fetched by the Agent during installation; both environments use the same four Skills.

## Requirements

Your Agent must support:

- Reading a remote URL and writing files to your user-level Skill directory.
- Remote **Streamable HTTP** MCP servers with OAuth (not just stdio/local-command MCP).

If either is missing, `INSTALL.md` tells the Agent to stop and report the limitation. Some desktop Agents can only add MCP servers through their UI; in that case the Agent will give you the exact values to enter by hand.

## Safety

- The installer never collects, stores, or prints OAuth tokens. It only writes the Skill files and MCP configuration.
- The production MCP URLs are fixed at `https://connector.springbrand.ai/mcp/{platform,action-api,connectors}`; the development MCP URLs are fixed at `https://devconnector.springbrand.ai/mcp/{platform,action-api,connectors}`.
- Existing MCP configuration is preserved. The manual dev fallback merges only the `springbrand-dev-*` entries; native Plugin lifecycle operations remove only their own bundled components.
- The installer does not execute any external third-party scripts.
- No credentials or tokens are placed in Skill files, Agent configuration, logs, or URLs.

## Updating

Use each host's native Marketplace update flow for Plugins. For the manual fallback, send the same prompt again; `INSTALL.md` / `INSTALL.dev.md` updates the existing entries rather than adding duplicates.

## Migration from the legacy single-entry install

Older SpringBrand installs use a single `springbrand` MCP entry at `https://connector.springbrand.ai/mcp` (the Gateway Legacy Aggregate Entry). These installs continue to work; the Gateway keeps serving `/mcp` until the owner explicitly retires it. Upgrading to the three-entry architecture is voluntary — there is no automatic sunset.

## Future: deterministic installer

A programmatic installer (`npx @springbrand/setup@latest`) is planned as a deterministic alternative for environments where prompt-based installation is unreliable. It is not required for the current flow.
