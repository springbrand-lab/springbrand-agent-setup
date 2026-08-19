# SpringBrand Agent Setup

Install SpringBrand as a native Codex Plugin on macOS, or use the existing Skill-plus-MCP fallback on unsupported hosts. You give your Agent one short prompt; it reads the installation protocol and uses the host-native lifecycle.

## Quick start

SpringBrand has two environments. Pick the one you need and paste the matching prompt into your Agent (Cursor, Claude Code, Codex, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent).

### Production

> Follow the official SpringBrand installation guide to complete setup:
> https://github.com/springbrand-lab/springbrand-agent-setup/blob/stable/INSTALL.md
> If this is Codex CLI 0.147.0+ or Codex desktop 26.810.52044+ on macOS, use the native Marketplace and Plugin flow in the guide. Otherwise, use the documented Skill-plus-MCP fallback. Preserve existing configuration, verify every completion check, and tell me whether I need to restart.

For Codex, [`INSTALL.md`](./INSTALL.md) uses native Marketplace, Plugin, OAuth, Hook review, update, uninstall, and confirmed legacy migration flows. Unsupported hosts retain the existing fallback. The production MCP server requires OAuth before normal use; complete authorization when the host prompts you.

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
- **WorkBuddy Plugin (beta)** — packages generated, verified Distribution Mirrors with native OAuth-backed production MCP for WorkBuddy; Native Evidence remains tracked in #23; see [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md).
- **SpringBrand Dev Plugin (prerelease)** — packages the same behavior for internal testing against `https://devconnector.springbrand.ai/mcp`; see [`INSTALL.dev.md`](./INSTALL.dev.md).
- **Skill-plus-MCP fallback** — the existing user-level Skill and remote MCP setup for unsupported hosts.

Both MCP environments require native OAuth before normal use. No Plugin contains static credentials or authorization headers.

## Version pinning

Production can track the latest stable release or be pinned to a tag. The full development Plugin is pinned to an immutable prerelease; `main` carries its current installation guide and the manual fallback.

| Use case | URL / ref |
| --- | --- |
| Always install the latest stable production version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/stable/INSTALL.md |
| Pin a stable, reproducible production version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/v1.1.1/INSTALL.md |
| Install the native development Plugin | `springbrand-lab/springbrand-agent-setup@v1.2.0-beta.4-dev.1` |
| Use the development guide or manual fallback | https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.dev.md |

Use `stable` for everyday production installs and the immutable dev tag for internal Plugin testing. The current production package version remains in [`VERSION`](./VERSION); the dev Plugin reports its own version from its tagged package.

## Repository layout

```
springbrand-agent-setup/
├── README.md                          # this file — for humans
├── INSTALL.md                         # the production installation protocol — for Agents
├── INSTALL.dev.md                     # the development installation protocol — for Agents
├── VERSION                            # current release version
├── .github/workflows/update-stable.yml # advances stable to the latest release tag
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
