# SpringBrand production installation protocol

## Initial installation response

Before changing anything, determine whether this is a first installation or an
update of an existing SpringBrand installation. Keep that classification for
this installation conversation, including any handoff to another Host guide.

Show the welcome message once at the first installation wrap-up or request
for user action, regardless of setup status or an existing task. Do not wait
for verification or a new conversation. Skip ordinary updates. Do not repeat
it in later replies of the same installation conversation.

This includes setup complete, waiting for OAuth, a required restart or new
session, and installation failure or a blocker. State the actual setup status
and next step first, then show the Welcome message and example tasks. Showing
the Welcome message does not mean that installation succeeded; keep the normal
verification requirements before reporting success.

If setup is incomplete, replace the prompt introduction with:
"Once setup is complete, try a task with free credits—copy a prompt below."

If the user already has a task underway, still show the Welcome message once,
then continue the parts of that task that can be performed. Use only the current
conversation to avoid repeats; do not defer delivery to a new session, add a
Skill, persist a welcome flag, or inject Welcome into a per-prompt Hook.

Keep the free-credit wording general: do not promise an amount, quantity, or
validity period. Do not check the website or a balance API during installation,
and do not present the copy as the user's current balance.

### Welcome message

**Everything your agent needs for go-to-market.**

GTM workflow Plugins and research, social-data, and media APIs—all through
SpringBrand, in the Agent you already use.

Try a task with free credits—copy a prompt below.

- **Research your market**
  “Use SpringBrand to research my product's competitors, compare their
  positioning, and identify opportunities to stand out. Include sources.”
- **Find customer signals**
  “Use SpringBrand to find public discussions about the problem my product
  solves. Summarize recurring pain points and buying signals, with links.”
- **Find creators**
  “Use SpringBrand to find creators who reach my target audience, explain
  why they fit my product, and draft personalized outreach.”
- **Create campaign assets**
  “Use SpringBrand to develop three creative directions for my next campaign,
  then turn my chosen direction into copy and visuals for the target channel.”

## Installation overview

Identify the Host before any network preflight. WorkBuddy installs the published
production release from R2. Codex, Claude Code, Cursor and the other-Agent
fallback retain their existing GitHub `main` paths until separately adapted.
Do not use the legacy `stable` branch, a dev tag, or the `springbrand-dev` Plugin.
The public entry is https://plugin.springbrand.ai/INSTALL.md; a document hosted
on R2 does not imply that every Host's package is already distributed by R2.

The GitHub source installation ships five Canonical Skills and one MCP entry. The entry's tools carry frozen domain prefixes, so each Domain Skill is served by its own tool namespace:

| Skill | Role | Tool prefix |
| --- | --- | --- |
| `springbrand-gtm` | GTM business entry; hands off to one Domain Skill | none (never calls MCP) |
| `ask-springbrand` | Ask SpringBrand — non-executing Capability Guide | none (never calls MCP) |
| `springbrand-platform` | Platform — create/publish artifacts, Plugin lifecycle | `platform_` |
| `springbrand-action-api` | Action API — dynamic API service execution | `action_` |
| `springbrand-connector` | Connector — authorized third-party systems (GitHub, Gmail, GSC) | `connector_` |

The MCP entry is:

| Entry name | URL |
| --- | --- |
| `springbrand` | `https://connector.springbrand.ai/mcp` |

## Identify the Agent

Use the first-install/update classification already established above and
select exactly one Host path before testing connectivity:

| Host | Current installation source | Guide |
| --- | --- | --- |
| WorkBuddy on macOS | Published R2 release ZIP; no GitHub preflight | [WorkBuddy](./INSTALL.workbuddy.md) |
| Codex CLI / Desktop | GitHub `main` | Codex section below |
| Claude Code / Desktop Code | GitHub `main` | [Claude](./INSTALL.claude.md) |
| Cursor | GitHub `main` | [Cursor](./INSTALL.cursor.md) |
| Other Agents | GitHub Skill files plus native MCP | Fallback section below |

For WorkBuddy, go directly to its guide. Do not run another Host's commands,
fetch raw Skill files, or silently fall back to GitHub when R2 is unavailable.
The initial-response rule above applies at the first result report or request
for user action, including when a linked Host guide blocks or asks for OAuth
or a restart. Returning from a Host guide does not show Welcome a second time.

## Preflight

**WorkBuddy: skip the GitHub Skill URL checks** and use only the R2/MCP
preflight in its guide. The checks below apply only to the retained GitHub
installation paths for the other Hosts.

For those Hosts, verify the Skill URLs and MCP URL are reachable.

```text
Skill URLs:
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/ask-springbrand/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-platform/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-action-api/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-connector/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-gtm/SKILL.md
MCP URL:
  https://connector.springbrand.ai/mcp
```

Check each with a five-second timeout. If a request fails:

- read the system proxy once;
- retry the same request once only when the error is retryable;
- stop and report after the retry or on a non-retryable error.

Do not start a long clone or unbounded diagnosis.

## Codex CLI and Desktop

Supported on Codex CLI `0.147.0+` and Codex Desktop `26.810.52044+` on macOS.

For a first install, run:

```sh
codex plugin marketplace add springbrand-lab/springbrand-agent-setup
codex plugin add springbrand@springbrand
codex mcp login springbrand
```

For an existing install, do **not** assume that repeating the install prompt
automatically fetches the latest `main`. Refresh the configured Marketplace,
then reinstall the same Plugin from the refreshed snapshot:

```sh
codex plugin marketplace upgrade springbrand
codex plugin add springbrand@springbrand
codex mcp login springbrand
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

Follow [INSTALL.workbuddy.md](./INSTALL.workbuddy.md), using the bundled native
CLI and this published, immutable R2 production source:

```text
https://plugin.springbrand.ai/releases/v1.2.0-beta.12/workbuddy/springbrand-workbuddy.zip
```

Expected version: `1.2.0-beta.12`. The package already contains all four Skills
and the production MCP declaration. Do not fetch individual Skills or run a
GitHub connectivity check. Prefer the native CLI; the guide documents the
manual fallback's limitations. OAuth remains a native browser step.

This source is pinned, not a moving production channel. It does not automatically
follow new releases or repository commits. Use only the source published in the
current guide; never guess a future version or channel URL.

## Other Agents: Skill-plus-MCP fallback

Use this path only when the Agent cannot install the native Plugin.

1. Identify the Agent's user-level Skill directory and MCP configuration.
2. Fetch the five Canonical Skills from:

   ```text
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/ask-springbrand/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-platform/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-action-api/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-connector/SKILL.md
   https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/main/skills/springbrand-gtm/SKILL.md
   ```

3. Install them as:

   ```text
   <user Skill directory>/ask-springbrand/SKILL.md
   <user Skill directory>/springbrand-platform/SKILL.md
   <user Skill directory>/springbrand-action-api/SKILL.md
   <user Skill directory>/springbrand-connector/SKILL.md
   <user Skill directory>/springbrand-gtm/SKILL.md
   ```

4. Add or update exactly one native remote HTTP MCP entry:

   ```text
   Name:      springbrand
   URL:       https://connector.springbrand.ai/mcp
   Transport: native Streamable HTTP (never stdio or a local command)
   Auth:      native OAuth
   ```

Read and merge structured configuration instead of overwriting it. Preserve
all unrelated configuration. If an existing SpringBrand Skill or MCP entry
differs, report the difference and wait for approval before replacing it.

## OAuth

Use the Agent's native OAuth flow. Pause only when the user must complete a
browser, UI, or authorization action.

The MCP entry requires a single OAuth consent per install: one authorization
covers all SpringBrand capabilities — Platform, Action API, and Connector.
Say this to the user before starting.

Never collect, store, print, proxy, or write access tokens, refresh tokens,
authorization codes, secrets, or credentials.

OAuth completion does not prove that a Plugin was used.

## Migration from a Legacy Plugin Release

A Legacy Plugin Release — an already-installed SpringBrand Plugin version that
uses a single `springbrand` MCP entry at
`https://connector.springbrand.ai/mcp` with the Gateway's legacy mixed
contract (unprefixed tool names) — continues to work until the owner's
production release switches the `/mcp` slot to the unified endpoint
(Gateway ADR-0014; retirement is Gateway Issue 12, owner-controlled).
Upgrading to the current single-entry Plugin with domain-prefixed tools is
voluntary — there is no automatic sunset.

To upgrade, follow the selected Host guide above: WorkBuddy uses its published
R2 release; the other Hosts retain GitHub `main`. Obtain approval before any
source replacement or conflicting legacy entry removal. The new Plugin bundles
the same single `springbrand` entry, now serving
the unified endpoint's `platform_`- / `action_`- / `connector_`-prefixed
tools, plus the Canonical Skills included in the selected release. The entry name and URL are unchanged, so the
upgrade replaces the toolset in place; no second SpringBrand entry is created.

## Safety and verification

- Do not install or enable `springbrand-dev` alongside the production Plugin.
- Do not add API keys, tokens, static authorization headers, client secrets, or
  local MCP bridges.
- Authenticate the Plugin-bundled entry instead of creating a second global
  server.
- Preserve unrelated Plugins, Skills, Rules, Hooks, MCP servers, OAuth state,
  and configuration.
- If a required step is UI-only, give the user the exact menu path and value;
  do not claim completion until the user confirms it.

Verify before reporting success:

- the complete Skill set exists and matches the selected source (five for GitHub main; four for the pinned WorkBuddy beta.12 package);
- the MCP entry is named `springbrand`;
- the URL is exactly `https://connector.springbrand.ai/mcp`;
- the transport is native Streamable HTTP;
- no duplicate SpringBrand entry exists;
- all unrelated configuration is intact.

If any check fails, report the exact failure and do not declare success.

Report the Agent and Surface, installation path, Plugin version, MCP status,
OAuth status, conflicts found, changes made, and whether restart or a new
session is required.
