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
> Identify the current Agent, install or update the Skill, and configure the SpringBrand dev MCP server. Preserve existing configuration, including any production install. Verify when done and tell me whether I need to restart.

Your Agent will read [`INSTALL.dev.md`](./INSTALL.dev.md), identify itself, install the shared Skill, configure the `springbrand-dev` MCP server, verify, and tell you whether to restart. The dev MCP server requires OAuth before normal use; complete authorization when your Agent prompts you. The Agent decides when to trigger that flow.

### Production vs Development

| | Production | Development |
| --- | --- | --- |
| Install guide | [`INSTALL.md`](./INSTALL.md) | [`INSTALL.dev.md`](./INSTALL.dev.md) |
| MCP server name | `springbrand` | `springbrand-dev` |
| MCP server URL | `https://connector.springbrand.ai/mcp` | `https://devconnector.springbrand.ai/mcp` |
| Purpose | Everyday use | Testing only |
| Can coexist | Yes — the two environments use different MCP entry names and can be installed side by side | Yes |

Both environments share the same SpringBrand Resource Discovery Skill (`springbrand-resource-discovery`); installing dev does not create a second Skill. Development is for testing only and should not be used as a production configuration.

## What gets installed

- **Codex Plugin (beta)** — packages the `springbrand-resource-discovery` Skill, production MCP declaration, and static preflight Hook for supported macOS Codex hosts.
- **Skill-plus-MCP fallback** — the existing user-level Skill and remote MCP setup for unsupported hosts.

The production MCP server is `https://connector.springbrand.ai/mcp` and requires native OAuth before normal use.

## Version pinning

Production can track the latest stable release or be pinned to a tagged release; development tracks `main`.

| Use case | URL |
| --- | --- |
| Always install the latest stable production version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/stable/INSTALL.md |
| Pin a stable, reproducible production version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/v1.1.1/INSTALL.md |
| Always install the latest development version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.dev.md |

Use the `stable` URL for everyday production installs, `main` for the latest development environment, and a tagged URL when every install must be identical (for example, across a team or an enterprise baseline). Each guide fetches the Skill from its own Git ref, so the protocol and Skill always stay on the same version. The current version is in [`VERSION`](./VERSION).

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
- Existing MCP configuration is always preserved — the installer merges, it never overwrites. A dev install never touches the production `springbrand` entry, and vice versa.
- The installer does not execute any external third-party scripts.
- No credentials or tokens are placed in Skill files, Agent configuration, logs, or URLs.

## Updating

Send the same prompt again. `INSTALL.md` / `INSTALL.dev.md` detects an existing install and updates it in place rather than adding duplicates.

## Future: deterministic installer

A programmatic installer (`npx @springbrand/setup@latest`) is planned as a deterministic alternative for environments where prompt-based installation is unreliable. It is not required for the current flow.
