# SpringBrand Agent Setup

Install SpringBrand into any AI coding or productivity Agent that supports user-level Skills and remote Streamable HTTP MCP servers with OAuth.

You don't run an installer. You give your Agent one short prompt; it reads the installation protocol and does the rest.

## Quick start

SpringBrand has two environments. Pick the one you need and paste the matching prompt into your Agent (Cursor, Claude Code, Codex, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent).

### Production

> Follow the official SpringBrand installation guide to complete setup:
> https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.md
> Identify the current Agent, install or update the Skill, and configure the SpringBrand MCP server. Preserve existing configuration. Verify when done and tell me whether I need to restart.

Your Agent will read [`INSTALL.md`](./INSTALL.md), identify itself, install the Skill, configure the `springbrand` MCP server, verify, and tell you whether to restart. The MCP server requires OAuth before normal use; complete authorization when your Agent prompts you. The Agent decides when to trigger that flow.

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

- **SpringBrand Skill** (`springbrand-resource-discovery`) — teaches your Agent to check SpringBrand Resources before building or recommending a solution, so it reuses existing plugins, components, templates, and capabilities instead of rebuilding them.
- **SpringBrand MCP server** — a single remote MCP server at `https://connector.springbrand.ai/mcp` that exposes SpringBrand Resources and connected provider capabilities (GitHub, Gmail, etc.). You authorize once with your SpringBrand account.

Both are installed at the **user level**, so they apply across all your projects.

## Version pinning

Each environment can be installed from `main` (always the latest) or pinned to a tagged release for reproducible installs.

| Use case | URL |
| --- | --- |
| Always install the latest production version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.md |
| Pin a stable, reproducible production version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/v1.1.0/INSTALL.md |
| Always install the latest development version | https://github.com/springbrand-lab/springbrand-agent-setup/blob/main/INSTALL.dev.md |

Use the `main` URL for everyday installs. Use the tagged URL when you need every install to be identical (for example, across a team or an enterprise baseline). The current version is in [`VERSION`](./VERSION).

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
- Existing MCP configuration is always preserved — the installer merges, it never overwrites. A dev install never touches the production `springbrand` entry, and vice versa.
- The installer does not execute any external third-party scripts.
- No credentials or tokens are placed in Skill files, Agent configuration, logs, or URLs.

## Updating

Send the same prompt again. `INSTALL.md` / `INSTALL.dev.md` detects an existing install and updates it in place rather than adding duplicates.

## Future: deterministic installer

A programmatic installer (`npx @springbrand/setup@latest`) is planned as a deterministic alternative for environments where prompt-based installation is unreliable. It is not required for the current flow.
