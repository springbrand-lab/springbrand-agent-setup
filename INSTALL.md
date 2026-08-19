# SpringBrand production installation protocol

Install or update SpringBrand Production from the repository default branch
`main`. `main` is the sole rolling production installation channel. Do not use
the legacy `stable` branch, a dev tag, or the `springbrand-dev` Plugin.

Identify the current Agent and use exactly one path below. Prefer the native
Plugin/Marketplace lifecycle when supported; use the fallback only for other
Agents.

## Codex CLI and Desktop

Supported on Codex CLI `0.147.0+` and Codex Desktop `26.810.52044+` on macOS.

```sh
codex plugin marketplace add springbrand-lab/springbrand-agent-setup
codex plugin add springbrand@springbrand
codex mcp login springbrand
```

The Marketplace bootstrap also exposes **SpringBrand** in the Desktop Plugins
Directory. Review and trust the exact `UserPromptSubmit` Hook, then open a new
session.

## Claude Code CLI and Desktop Code

Follow [`INSTALL.claude.md`](./INSTALL.claude.md). The Marketplace source is:

```text
springbrand-lab/springbrand-agent-setup
```

This applies to Claude Code CLI and the Claude Desktop Code tab, not Claude
Chat, Cowork, web sessions, or account-level Connectors.

## Cursor Desktop

Follow [`INSTALL.cursor.md`](./INSTALL.cursor.md). Import this GitHub Marketplace:

```text
springbrand-lab/springbrand-agent-setup
```

## WorkBuddy Desktop

Follow [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md). A WorkBuddy Agent must
use its bundled `codebuddy`/`cbc` CLI to add or update the repository Marketplace
and install or update `springbrand@springbrand`. Do not pause for manual UI
installation when that CLI is available.

The manual **Add Marketplace** fallback uses:

```text
springbrand-lab/springbrand-agent-setup
```

WorkBuddy reads the production Plugin from repository `main`. OAuth remains a
native browser step when WorkBuddy prompts the user.

## Other Agents: Skill-plus-MCP fallback

Use this path only when the Agent cannot install the native Plugin.

1. Identify the Agent's user-level Skill directory and MCP configuration.
2. Fetch the Canonical Skill from:

   ```text
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand/SKILL.md
   ```

3. Install it as:

   ```text
   <user Skill directory>/springbrand-plugin-discovery/SKILL.md
   ```

4. Add or update exactly one native remote HTTP MCP entry:

   ```text
   Name: springbrand
   URL:  https://connector.springbrand.ai/mcp
   Auth: native OAuth
   ```

Read and merge structured configuration instead of overwriting it. Preserve
all unrelated configuration. If an existing SpringBrand Skill or MCP entry
differs, report the difference and wait for approval before replacing it.

## Safety and verification

- Do not install or enable `springbrand-dev` alongside the production Plugin.
- Do not add API keys, tokens, static authorization headers, client secrets, or
  local MCP bridges.
- Authenticate the Plugin-bundled `springbrand` entry instead of creating a
  second global server.
- Preserve unrelated Plugins, Skills, Rules, Hooks, MCP servers, OAuth state,
  and configuration.
- If a required step is UI-only, give the user the exact menu path and value;
  do not claim completion until the user confirms it.

Verify before reporting success:

- Plugin ID is `springbrand` and its source is repository `main`;
- `springbrand-plugin-discovery` is visible;
- the Host-specific Hook or Rule is loaded;
- exactly one Plugin-managed `springbrand` MCP entry points to
  `https://connector.springbrand.ai/mcp` and is connected through OAuth;
- a clear external/specialized capability-gap task routes through Plugin
  Discovery, while summarizing supplied material does not call SpringBrand;
- unrelated configuration remains unchanged.

Report the Agent and Surface, installation path, Plugin version, MCP status,
OAuth status, conflicts found, changes made, and whether restart or a new
session is required.
