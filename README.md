# SpringBrand Agent Setup

Install SpringBrand Production from the repository `main` branch through each supported Host's native Plugin lifecycle, or use the documented Skill-plus-MCP fallback on other Agents.

## Quick start

SpringBrand has two environments. Pick the one you need and paste the matching prompt into your Agent (Cursor, Claude Code, Codex, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent).

### Production

> Install or update SpringBrand Production from https://github.com/springbrand-lab/springbrand-agent-setup using the latest `main` branch. Identify this Agent, follow the matching Host guide, prefer native Plugin/Marketplace and OAuth, preserve existing configuration, and give me exact instructions for any UI steps you cannot perform.

[`INSTALL.md`](./INSTALL.md) is the universal production protocol. `main` is the sole rolling production installation channel; production users should not use the legacy `stable` branch or a version tag. The production MCP server requires Host-native OAuth.

### Development

> Follow the official SpringBrand development installation guide to complete setup:
> https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.dev.md
> Use the native `springbrand-dev` Plugin on Codex, Claude Code/Desktop Code, Cursor, or WorkBuddy. Use the documented Skill-plus-MCP fallback only on unsupported hosts. Preserve unrelated configuration, complete native OAuth, verify the installation, and tell me whether I need to restart.

The native development Plugin is the immutable prerelease [`v1.2.0-beta.4-dev.1`](https://github.com/springbrand-lab/springbrand-agent-setup/releases/tag/v1.2.0-beta.4-dev.1). It is identified as `springbrand-dev`, displays as **SpringBrand Dev**, and bundles one `springbrand-dev` MCP server at `https://devconnector.springbrand.ai/mcp`. Authentication is host-native OAuth.

Disable or uninstall the full production `springbrand` Plugin before enabling the full development Plugin. Both package the same Canonical Skill and routing behavior, so enabling both can duplicate routing and make connector selection ambiguous. The manual fallback remains available for unsupported hosts and may coexist with production because it shares one Skill file and adds only the separately named `springbrand-dev` MCP entry.

### Production vs Development

| | Production | Development |
| --- | --- | --- |
| Install guide | [`INSTALL.md`](./INSTALL.md) | [`INSTALL.dev.md`](./INSTALL.dev.md) |
| MCP server name | `springbrand` | `springbrand-dev` |
| MCP server URL | `https://connector.springbrand.ai/mcp` | `https://devconnector.springbrand.ai/mcp` |
| Purpose | Everyday use | Testing only |
| Full Plugins can coexist | No | No — disable one before enabling the other |
| Manual Skill-plus-MCP fallback can coexist | Yes | Yes — it shares one Skill and uses a separate MCP name |

Both environments share the same SpringBrand Resource Discovery Skill (`springbrand-resource-discovery`). Development is for testing only and should not be used as a production configuration.

## What gets installed

- **Codex Plugin (beta)** — packages the `springbrand-resource-discovery` Skill, production MCP declaration, and static preflight Hook for supported macOS Codex hosts.
- **Claude Code Plugin (beta)** — packages the same Canonical Skill, native OAuth-backed production MCP, and static preflight Hook for Claude Code CLI and the Claude Desktop Code tab; see [`INSTALL.claude.md`](./INSTALL.claude.md).
- **Cursor Plugin (beta)** — packages generated, verified Distribution Mirrors with native OAuth-backed production MCP and an always-applied preflight Rule for Cursor desktop; see [`INSTALL.cursor.md`](./INSTALL.cursor.md).
- **WorkBuddy Plugin (beta)** — installs from the repository through WorkBuddy's native **Add Marketplace** flow; see [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md).
- **SpringBrand Dev Plugin (prerelease)** — packages the same behavior for internal testing against `https://devconnector.springbrand.ai/mcp`; see [`INSTALL.dev.md`](./INSTALL.dev.md).
- **Skill-plus-MCP fallback** — the existing user-level Skill and remote MCP setup for unsupported hosts.

Both MCP environments require native OAuth before normal use. No Plugin contains static credentials or authorization headers.

## Distribution channels

| Environment | Installation channel |
| --- | --- |
| Production | `https://github.com/springbrand-lab/springbrand-agent-setup` (`main`) |
| Development | `springbrand-lab/springbrand-agent-setup@v1.2.0-beta.4-dev.1` |

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
    └── springbrand/
        └── SKILL.md                   # the SpringBrand Skill source (shared by both environments)
```

`INSTALL.md` and `INSTALL.dev.md` are the core product. They are written to be read and executed by an Agent. The Skill source lives in `skills/springbrand/SKILL.md` and is fetched by the Agent during installation; both environments use this same Skill.

## Requirements

Your Agent must support:

- Reading a remote URL and writing a file to your user-level Skill directory.
- Remote **Streamable HTTP** MCP servers with OAuth (not just stdio/local-command MCP).

If either is missing, `INSTALL.md` tells the Agent to stop and report the limitation. Some desktop Agents can only add MCP servers through their UI; in that case the Agent will give you the exact values to enter by hand.

## Safety

- The installer never collects, stores, or prints OAuth tokens. It only writes the Skill file and MCP configuration.
- The production MCP URL is fixed at `https://connector.springbrand.ai/mcp`; the development MCP URL is fixed at `https://devconnector.springbrand.ai/mcp`.
- Existing MCP configuration is preserved. The manual dev fallback merges only the `springbrand-dev` entry; native Plugin lifecycle operations remove only their own bundled components.
- The installer does not execute any external third-party scripts.
- No credentials or tokens are placed in Skill files, Agent configuration, logs, or URLs.

## Updating

Use each host's native Marketplace update flow for Plugins. For the manual fallback, send the same prompt again; `INSTALL.md` / `INSTALL.dev.md` updates the existing entry rather than adding duplicates.

## Future: deterministic installer

A programmatic installer (`npx @springbrand/setup@latest`) is planned as a deterministic alternative for environments where prompt-based installation is unreliable. It is not required for the current flow.
