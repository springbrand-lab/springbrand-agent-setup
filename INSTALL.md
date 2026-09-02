# SpringBrand production installation protocol

Install or update SpringBrand Production from the repository default branch
`main`. `main` is the sole rolling production installation channel. Do not use
the legacy `stable` branch, a dev tag, or the `springbrand-dev` Plugin.

SpringBrand ships four Canonical Skills and three MCP Domain Entries:

| Skill | Role | MCP entry |
| --- | --- | --- |
| `ask-springbrand` | Ask SpringBrand — non-executing Capability Guide | none |
| `springbrand-platform` | Platform — create/publish artifacts, Plugin lifecycle | `springbrand-platform` |
| `springbrand-action-api` | Action API — dynamic API service execution | `springbrand-action-api` |
| `springbrand-connector` | Connector — third-party systems (GitHub in v1) | `springbrand-connector` |

The three MCP Domain Entries are:

| Entry name | URL |
| --- | --- |
| `springbrand-platform` | `https://connector.springbrand.ai/mcp/platform` |
| `springbrand-action-api` | `https://connector.springbrand.ai/mcp/action-api` |
| `springbrand-connector` | `https://connector.springbrand.ai/mcp/connectors` |

## Preflight

Before installing, verify the Skill URLs and MCP URLs are reachable.

```text
Skill URLs:
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/ask-springbrand/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-platform/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-action-api/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-connector/SKILL.md
MCP URLs:
  https://connector.springbrand.ai/mcp/platform
  https://connector.springbrand.ai/mcp/action-api
  https://connector.springbrand.ai/mcp/connectors
```

Check each with a five-second timeout. If a request fails:

- read the system proxy once;
- retry the same request once only when the error is retryable;
- stop and report after the retry or on a non-retryable error.

Do not start a long clone or unbounded diagnosis.

## Identify the Agent

Identify the current Agent and use exactly one path below. Prefer the native
Plugin/Marketplace lifecycle when supported; use the fallback only for other
Agents.

## Codex CLI and Desktop

Supported on Codex CLI `0.147.0+` and Codex Desktop `26.810.52044+` on macOS.

For a first install, run:

```sh
codex plugin marketplace add springbrand-lab/springbrand-agent-setup
codex plugin add springbrand@springbrand
codex mcp login springbrand-platform
codex mcp login springbrand-action-api
codex mcp login springbrand-connector
```

For an existing install, do **not** assume that repeating the install prompt
automatically fetches the latest `main`. Refresh the configured Marketplace,
then reinstall the same Plugin from the refreshed snapshot:

```sh
codex plugin marketplace upgrade springbrand
codex plugin add springbrand@springbrand
codex mcp login springbrand-platform
codex mcp login springbrand-action-api
codex mcp login springbrand-connector
```

`codex` has no separate `plugin update` command in the supported CLI. The
Marketplace `upgrade` refreshes the repository snapshot; `plugin add` then
updates the installed Plugin in place rather than creating a second
`springbrand@springbrand` entry. Run `codex plugin marketplace list` and
`codex plugin list --json` first if you need to distinguish first install from
update. If the Marketplace is not configured yet, use the first-install
commands.

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
2. Fetch the four Canonical Skills from:

   ```text
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/ask-springbrand/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-platform/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-action-api/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-connector/SKILL.md
   ```

3. Install them as:

   ```text
   <user Skill directory>/ask-springbrand/SKILL.md
   <user Skill directory>/springbrand-platform/SKILL.md
   <user Skill directory>/springbrand-action-api/SKILL.md
   <user Skill directory>/springbrand-connector/SKILL.md
   ```

4. Add or update exactly three native remote HTTP MCP entries:

   ```text
   Name:      springbrand-platform
   URL:       https://connector.springbrand.ai/mcp/platform
   Transport: native Streamable HTTP (never stdio or a local command)
   Auth:      native OAuth

   Name:      springbrand-action-api
   URL:       https://connector.springbrand.ai/mcp/action-api
   Transport: native Streamable HTTP (never stdio or a local command)
   Auth:      native OAuth

   Name:      springbrand-connector
   URL:       https://connector.springbrand.ai/mcp/connectors
   Transport: native Streamable HTTP (never stdio or a local command)
   Auth:      native OAuth
   ```

Read and merge structured configuration instead of overwriting it. Preserve
all unrelated configuration. If an existing SpringBrand Skill or MCP entry
differs, report the difference and wait for approval before replacing it.

## OAuth

Use the Agent's native OAuth flow. Pause only when the user must complete a
browser, UI, or authorization action.

Each of the three MCP Domain Entries requires its own OAuth consent. A full
production install therefore involves up to three consents per Surface (one
per entry). Disclose this to the user before starting.

Never collect, store, print, proxy, or write access tokens, refresh tokens,
authorization codes, secrets, or credentials.

OAuth completion does not prove that a Plugin was used.

## Migration from a Legacy Plugin Release

A Legacy Plugin Release — an already-installed SpringBrand Plugin version that
uses a single `springbrand` MCP entry at
`https://connector.springbrand.ai/mcp` (the Gateway Legacy Aggregate Entry) —
continues to work; the Gateway keeps serving `/mcp` until the owner explicitly
retires it. Upgrading to the three-entry architecture is voluntary — there is
no automatic sunset.

To upgrade, install or update the production Plugin from `main` as described
above. The new Plugin bundles the three Domain Entries and the four Skills.
The Legacy Plugin Release's `springbrand` entry may remain alongside the three
new entries until the user removes it; removing it is optional and does not
affect the new entries.

## Safety and verification

- Do not install or enable `springbrand-dev` alongside the production Plugin.
- Do not add API keys, tokens, static authorization headers, client secrets, or
  local MCP bridges.
- Authenticate the Plugin-bundled entries instead of creating second global
  servers.
- Preserve unrelated Plugins, Skills, Rules, Hooks, MCP servers, OAuth state,
  and configuration.
- If a required step is UI-only, give the user the exact menu path and value;
  do not claim completion until the user confirms it.

Verify before reporting success:

- the four Skills exist and match the fixed source;
- the three MCP entries are named `springbrand-platform`,
  `springbrand-action-api`, and `springbrand-connector`;
- the URLs are exactly `https://connector.springbrand.ai/mcp/platform`,
  `https://connector.springbrand.ai/mcp/action-api`, and
  `https://connector.springbrand.ai/mcp/connectors`;
- the transport is native Streamable HTTP for every entry;
- no duplicate SpringBrand entry exists;
- all unrelated configuration is intact.

If any check fails, report the exact failure and do not declare success.

Report the Agent and Surface, installation path, Plugin version, MCP status,
OAuth status, conflicts found, changes made, and whether restart or a new
session is required.
