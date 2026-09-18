# SpringBrand Agent installation protocol — Development

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

You are an AI coding or productivity Agent. A user has asked you to install or update the **SpringBrand development** environment by following this document. Identify the host and use exactly one path below:

1. **Native Plugin path** for Codex CLI/Desktop, Claude Code CLI/Desktop Code, Cursor desktop, or WorkBuddy desktop.
2. **Manual Skill-plus-MCP fallback** for unsupported hosts.

Do not run both paths. This document is the single source of truth for development installation.

SpringBrand ships five Canonical Skills (`ask-springbrand`,
`springbrand-platform`, `springbrand-action-api`, `springbrand-connector`, `springbrand-gtm`) and
one MCP entry per environment. The dev variant uses the single
`springbrand-dev` entry against `devconnector.springbrand.ai`. The four
SpringBrand Domain Skills use the shared `search_tools`, `get_tool_schemas`,
`manage_connections`, `execute_tools`, and `get_execution` Meta Tools;
`springbrand-gtm` remains a non-executing workflow router.

## Preflight

Before installing, verify the Skill URLs and MCP URL are reachable.

```text
Skill URLs:
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/ask-springbrand/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-platform/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-action-api/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-connector/SKILL.md
  https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-gtm/SKILL.md
MCP URL:
  https://devconnector.springbrand.ai/mcp
```

Check each with a five-second timeout. If a request fails:

- read the system proxy once;
- retry the same request once only when the error is retryable;
- stop and report after the retry or on a non-retryable error.

Do not start a long clone or unbounded diagnosis.

## Native `springbrand-dev` Plugin

The selected development release is described by one environment descriptor.
That descriptor is authoritative for the entry name, URL, native remote HTTP
transport, API-key credential representation, identity check, and MCP service
health check. Do not copy a credential into this repository or invent a
Host-specific representation that the selected release does not support.

The immutable internal-testing release is:

| Field | Value |
| --- | --- |
| Plugin / Marketplace ID | `springbrand-dev` |
| Display name | SpringBrand Dev |
| Version | `1.2.1-dev.2` |
| Git ref | `v1.2.1-dev.2` |
| MCP entry | `springbrand-dev` |
| MCP URL | `https://devconnector.springbrand.ai/mcp` |
| Transport | Native remote HTTP / Streamable HTTP |
| Authentication | Runtime API key through the Host's secure Bearer credential mechanism |

This development release includes `springbrand-gtm` and the four Domain Skills.
Keep production and development configuration only when the Host can distinguish
their entries and routing. Do not edit Plugin caches, override the bundled URL,
store a credential in repository files, or register extra dev MCP servers.

## Installation contract

1. Identify the Agent product, runtime Surface, version, and whether this is a
   first install or update. Keep that classification for final reporting. Do
   not guess unsupported paths or configuration.
2. Use the Host-native Plugin lifecycle when available. The native package must
   contain exactly five Canonical Skills, one Host Notice Hook or Rule, and
   one bundled `springbrand-dev` MCP entry.
3. Use manual Skill-plus-MCP installation only when the Host has no native
   Plugin lifecycle. The fallback installs no Notice adapter. Never run both
   paths.
4. Ask for the development API key only at runtime, after the target environment
   and Host are known. Configure it through the Host's secure Bearer credential
   mechanism. Never print, echo, log, hash, proxy, or place the key or its
   Authorization header in a URL, file, command history, error, or report.
5. Preserve unrelated Plugins, Skills, Hooks, Rules, MCP entries, OAuth state,
   and configuration. Ask before replacing a conflicting `springbrand-dev`
   entry; never alter the production `springbrand` entry from this guide.
6. Installation succeeds only after the authoritative identity check and the
   configured MCP service health check pass. Capability discovery, business
   execution, Plugin use, and Provider operations are separate functional
   tests, not installation gates.

Host Notice bindings for this development release are:

- Claude Code and Claude Desktop Code: `UserPromptSubmit` Hook referencing
  `/springbrand-dev:ask-springbrand` and `/springbrand-dev:springbrand-gtm`;
- Codex: `UserPromptSubmit` Hook referencing `$ask-springbrand` and `$springbrand-gtm`;
- WorkBuddy: validated `UserPromptSubmit` Hook referencing the registered
  `ask-springbrand` and `springbrand-gtm` Skills;
- Cursor: `alwaysApply` Rule referencing `ask-springbrand` and `springbrand-gtm`.

Install exactly one Notice adapter on the native Plugin path. The Notice only
makes the Canonical Skills visible; discovery, acquisition, distribution, and
Plugin invocation remain in the Skills.

### Updating an existing dev install

Inspect the registered Marketplace source/ref before updating. Refreshing an
immutable older tag or ZIP does not select this release. Use the Host's native
source update or replacement flow to select the exact tag/ZIP in this guide,
then refresh the Marketplace and update the installed Plugin. Preserve OAuth
and unrelated configuration; never patch a Plugin cache. If source replacement
requires a user-only UI step, explain that step rather than claiming the
existing install has upgraded. Reload and verify the version and all five
Skills before declaring success.

### Codex CLI and Desktop

```sh
codex plugin marketplace add springbrand-lab/springbrand-agent-setup --ref v1.2.1-dev.2
codex plugin add springbrand-dev@springbrand-dev
```

The Marketplace bootstrap also exposes **SpringBrand Dev** in the Codex desktop
Plugins Directory. Install it there if using Desktop, configure the runtime API
key through the supported secure credential flow, then open a new task. If the
Host cannot safely represent the Bearer credential, stop with the exact manual
UI fields instead of launching OAuth or claiming success.

### Claude Code CLI and Desktop Code

CLI:

```sh
claude plugin marketplace add springbrand-lab/springbrand-agent-setup@v1.2.1-dev.2 --scope user
claude plugin install springbrand-dev@springbrand-dev --scope user
```

Desktop Code: open **Plugin Browser → Add Marketplace** and enter:

```text
springbrand-lab/springbrand-agent-setup@v1.2.1-dev.2
```

Install **SpringBrand Dev**, configure the runtime API key through the supported
secure credential flow, and open a new Code task. If this Surface exposes only
manual UI configuration, give the exact descriptor fields and stop for the
user. This does not apply to Claude Chat, Cowork, web sessions, or account-level
Connectors.

### Cursor desktop

Open **Customize → Browse Marketplace → Add Marketplace → Import from GitHub** and enter:

```text
springbrand-lab/springbrand-agent-setup@v1.2.1-dev.2
```

Install **SpringBrand Dev**, configure the runtime API key for the
`springbrand-dev` entry through Cursor's supported secure credential flow, and
open a new task. Do not fall back to OAuth when a valid API key was supplied.

### WorkBuddy desktop

Follow the **Development install** section in [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md).
A WorkBuddy Agent must use its bundled `codebuddy`/`cbc` CLI to add the immutable
ZIP Marketplace and install `springbrand-dev@springbrand-dev`; **Add Marketplace**
remains the manual fallback:

```text
https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.1-dev.2.zip
```

WorkBuddy does not accept the `owner/repo@tag` shorthand. Configure the runtime
API key only through its supported secure credential UI. If that UI cannot
represent the selected descriptor, stop with the exact fields and do not
launch OAuth.

### Native Plugin verification and removal

Verify that the installed Plugin shows:

- Plugin ID `springbrand-dev` and version `1.2.1-dev.2`;
- exactly one bundled `springbrand-dev` MCP entry;
- URL exactly `https://devconnector.springbrand.ai/mcp`;
- the transport is native Streamable HTTP;
- no duplicate `springbrand-dev` entry exists;
- the five Canonical Skills (`ask-springbrand`, `springbrand-platform`,
  `springbrand-action-api`, `springbrand-connector`, `springbrand-gtm`);
- exactly one host-appropriate Notice Hook or Rule;
- the authoritative identity check for the selected environment passes;
- the configured MCP service health check passes;
- all unrelated configuration is intact.

Do not call `initialize`, `tools/list`, capability discovery, a business
operation, or a Provider operation merely to prove installation. Those are
separate functional tests and must not replace either required health check.

If this path succeeds, **do not run the fallback**. Apply the initial-response
rule above if this is the first result report; do not repeat a Welcome message
already shown at an earlier handoff. Continue here only when the user also
requested removal testing. After testing, uninstall `springbrand-dev` through
the host's native Plugin lifecycle and confirm its bundled components disappear
while unrelated configuration remains intact. Re-enable production only after
the full dev Plugin is removed.

## API key and required health checks

The user supplies the selected environment's API key at runtime. Ask for it
only after identifying the Host and Surface and only through a secure runtime
input. Do not launch browser OAuth when a valid API key is supplied. OAuth may
remain on an older installation as a compatibility path, but it is not a
prerequisite for this API-key-first flow.

Run only these bounded installation checks through the configured target
entry:

1. The authoritative identity check for the selected environment.
2. The configured MCP service health check for the selected environment.

Do not perform a real Provider write during installation. Do not claim success
unless both required health checks pass.

Missing, malformed, revoked, expired, wrong-environment, or insufficient-scope
keys fail closed. Report only a stable failure category; never include the key,
its hash, an Authorization header, an OAuth token, a Provider Credential, or a
raw upstream response.

### Existing OAuth migration

When the selected environment has an older OAuth-backed entry, update only
that entry if the Host can represent the API-key credential safely. Never
read, print, copy, delete, decode, revoke, or reinterpret OAuth access or
refresh tokens. Preserve every other environment and all unrelated
configuration. Never create a duplicate target entry. If the authentication
mode change is destructive or UI-only, explain the exact action and pause; do not silently start OAuth or claim migration success.

## Manual Skill-plus-MCP fallback

Use this path only when the host cannot install the native Plugin. Unlike two complete Plugins, this fallback may coexist with production because it shares the same Skill files and adds only the separately named `springbrand-dev` MCP entry.

### What this installs

Two things, both user-level (not project-level):

1. **The five SpringBrand Skills** — `SKILL.md` files that teach the Agent the
   three-domain architecture: `ask-springbrand` (the guide), and the
   `springbrand-platform`, `springbrand-action-api`, and `springbrand-connector`
   Domain Skills, plus `springbrand-gtm` for substantive growth tasks.
   Existing Skill names are shared with production; the new GTM Skill ships
   in this development release. Install the dev-tag sources as one coherent set.
2. **The SpringBrand dev MCP server** — a remote MCP server named
   `springbrand-dev` at a fixed dev URL, which exposes the five shared Meta
   Tools for the development environment.

The dev MCP server uses the runtime API key supplied for the selected
environment. Configure it only through the Host's supported secure Bearer
credential mechanism. Existing OAuth state is preserved but is not read,
deleted, or launched proactively.

### Inputs

- **Skill sources:**
  - `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/ask-springbrand/SKILL.md`
  - `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-platform/SKILL.md`
  - `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-action-api/SKILL.md`
  - `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-connector/SKILL.md`
  - `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.1-dev.2/skills/springbrand-gtm/SKILL.md`
- **MCP server name:** `springbrand-dev`
- **MCP server URL (fixed):**
  - `https://devconnector.springbrand.ai/mcp`
- **MCP transport:** native Streamable HTTP (remote HTTP transport, **not** a stdio bridge, **not** a local command)

If you were given a different URL, use the one above. The dev URL is fixed and must not be changed.

The development Plugin and fallback Skills are pinned to the same immutable dev tag. Do not use `main`, `stable`, or a production tag for development installation.

### Fallback Step 1 — Identify your Agent

Determine which Agent product you are running in (for example: Cursor, Claude Code, Codex CLI, GitHub Copilot Chat, Devin, Windsurf, WorkBuddy, or another). You need this to locate your user-level Skill directory and your MCP configuration.

**Completion criterion:** you can name your Agent product and know where its user-level Skill directory and MCP configuration live.

If you cannot identify your Agent, or you do not know where its user-level Skills or MCP configuration are stored, **stop and ask the user**. Do not guess paths. Do not write files until you are certain.

### Fallback Step 2 — Install or update the SpringBrand Skills

Install all five Canonical Skills from the selected dev tag. Keep their canonical names and matching release versions; do not create dev-suffixed Skill copies or mix sources from different tags.

1. Determine your Agent's **user-level** Skill directory. This is the per-user, cross-project location your Agent loads Skills from — not a project-local `.agents/skills/` or `.claude/skills/` folder. If your Agent only supports project-level Skills, use the project-level location and tell the user that in your final report.
2. Fetch each Skill source from the raw URLs in "Inputs" above.
3. Target paths:
   - `<your user-level Skill directory>/ask-springbrand/SKILL.md`
   - `<your user-level Skill directory>/springbrand-platform/SKILL.md`
   - `<your user-level Skill directory>/springbrand-action-api/SKILL.md`
   - `<your user-level Skill directory>/springbrand-connector/SKILL.md`
   - `<your user-level Skill directory>/springbrand-gtm/SKILL.md`
4. Compare each fetched content against any existing file at that path:
   - **Identical** → leave the file unchanged. Note it as "unchanged".
   - **Different** → tell the user you will replace it, and **wait for approval** before writing. After approval, overwrite with the fetched content. Note it as "replaced".
   - **Does not exist** → tell the user you will create it, and **wait for approval** before writing. After approval, create the directory if needed and write the fetched content. Note it as "created".

A dev install must never silently overwrite a Skill whose content differs from the fetched source. Always tell the user first and wait for approval.

If your Agent does not support user-level Skills compatible with `SKILL.md`, report that limitation and **stop**. Do not attempt to fake a Skill location.

**Completion criterion:** the files at the target paths exist and their content matches the fetched Skill sources byte-for-byte, or you have stopped and reported an unsupported limitation.

### Fallback Step 3 — Configure the SpringBrand dev MCP server

1. Locate your Agent's MCP configuration. Determine its format and location (for example: a JSON file, a TOML file, a settings UI, or a CLI-managed registry). Use the Agent's documented native representation of Streamable HTTP; it may be selected through a UI or inferred from the remote URL rather than stored in a field named `transport`.
2. **Read and parse** the existing configuration before modifying it. Never overwrite a config file without first parsing its current contents. Merge your changes into the parsed structure; do not replace the whole file.
3. Look for an existing MCP server entry named `springbrand-dev`:
   - **Not present** → add a new entry with the name, URL, native Streamable HTTP transport, and the descriptor's secure Bearer credential representation.
   - **Present and already matches** (correct name, URL exactly as above, native HTTP transport, and API-key credential mode) → leave it unchanged. Note it as "unchanged".
   - **Present but different** (wrong URL, transport, or authentication mode) → explain the exact conflict and **wait for approval** before replacing only that entry. Note it as "replaced" after the change.
4. **Preserve every other MCP server entry and all unrelated configuration.** Only the `springbrand-dev` entry may be added, replaced, or left alone. In particular, do **not** delete or modify the production `springbrand` entry if it exists — the two environments are meant to coexist, and the production entry is managed exclusively by `INSTALL.md`.
5. Ask for the API key only through the Host's secure runtime credential flow. Never put it in a URL, repository file, Skill, manifest, shell argument, log, error, or report.

If your Agent only supports adding MCP servers through a UI and cannot edit its config file directly, tell the user the exact values to enter in the UI (the name, URL, native HTTP transport, and Bearer credential mode from the selected descriptor) and **stop** after giving those instructions. Do not attempt to drive the UI yourself unless you have a verified ability to do so for that Agent.

If your Agent does not support remote Streamable HTTP MCP servers with a safe
Bearer credential mechanism, report that limitation and **stop**. Do not fall
back to OAuth or claim success.

**Completion criterion:** the `springbrand-dev` MCP server is configured with its exact URL using native HTTP transport, all other configuration (including any production `springbrand` entry) is intact, or you have stopped and reported an unsupported limitation.

### Fallback Step 4 — Verify

1. **Skill files:** confirm each of the five files at `<Skill dir>/{ask-springbrand,springbrand-platform,springbrand-action-api,springbrand-connector,springbrand-gtm}/SKILL.md` exists and its content matches the fetched Skill source.
2. **MCP config:** re-read and parse the configuration. Confirm the `springbrand-dev` entry has its exact URL from "Inputs" above, uses native Streamable HTTP transport, and uses the selected descriptor's API-key credential mode.
3. Confirm no duplicate `springbrand-dev` entry exists.
4. Confirm no other MCP server entries were removed or altered — including the production `springbrand` entry, which must remain untouched.
5. Run the authoritative identity check and configured MCP service health check. Do not substitute capability discovery or a business call.

**Completion criterion:** all checks pass. If any fails, report exactly what is wrong and stop — do not declare success.

### Fallback Step 5 — Report

Tell the user, in plain text:

1. Which Agent you identified yourself as.
2. The Skill directory you used and whether each Skill file was created, replaced, or unchanged — with the full paths. These Skill files belong to the selected dev release; preserve their canonical names.
3. The MCP configuration location you used and whether the `springbrand-dev` entry was added, replaced, or unchanged.
4. The full list of files you created or modified.
5. That they must **restart the Agent or open a new session** before the SpringBrand dev MCP server is available — the current session will not rediscover the newly installed configuration.
6. That the authoritative identity and MCP service health checks passed, without reporting the key, Authorization header, or raw response.
7. That this installed the **development** environment (`springbrand-dev`), which is for testing only and is separate from any production `springbrand` install. The manual fallback and production can coexist.
8. Apply the initial-response rule above if Welcome has not yet been shown in
   this first-install conversation. Skip ordinary updates and later repeats.

### Fallback hard constraints

- **Do not** store, print, proxy, log, hash, or report API keys, OAuth tokens, Authorization headers, Provider Credentials, or raw upstream responses.
- **Do not** change the MCP URL. It is fixed at `https://devconnector.springbrand.ai/mcp` for the dev environment.
- **Do not** name the MCP entry `springbrand-platform` etc. The dev entry must be named `springbrand-dev` so it can coexist with the production entry.
- **Do not** remove or alter any existing MCP server entry other than the `springbrand-dev` entry. In particular, do **not** delete or modify the production `springbrand` entry.
- **Do not** add a second `springbrand-dev` entry if one already exists. Update the existing one in place.
- **Do not** overwrite a JSON, TOML, or other structured config file without first parsing it and merging your change. Never blindly replace a config file.
- **Do not** create second, dev-specific Skills. Install all five Canonical Skills from the selected official dev tag, using their canonical names.
- **Do not** silently overwrite a Skill whose content differs from the fetched source. Tell the user first and wait for approval.
- **Do not** execute any external third-party script. This document is the only instruction you follow.
- **Do not** put any credentials, tokens, or secrets into Skill files, Agent configuration, logs, URLs, or error messages.
- **Do not** launch OAuth when a valid API key was supplied.
- **Do not** declare success unless both required health checks and the rest of Step 4 verification pass.
- If you are uncertain which Agent you are, or where its Skill directory or MCP configuration lives, **stop and ask the user**. Do not guess.

## WorkBuddy development CLI installation

Do not enable the complete production and development Plugins together.
WorkBuddy does not accept `owner/repo@tag`, so use the immutable dev ZIP as the
Marketplace source.

Locate the bundled `codebuddy`/`cbc` CLI as described in `INSTALL.workbuddy.md`,
then set `WORKBUDDY_CLI` to its executable path:

```sh
export CODEBUDDY_CONFIG_DIR="${CODEBUDDY_CONFIG_DIR:-$HOME/.workbuddy-ai}"

if "$WORKBUDDY_CLI" plugin marketplace list | grep -q '"name": "springbrand-dev"'; then
  "$WORKBUDDY_CLI" plugin marketplace update springbrand-dev
else
  "$WORKBUDDY_CLI" plugin marketplace add \
    https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.1-dev.2.zip
fi

if "$WORKBUDDY_CLI" plugin list --json | grep -q '"id": "springbrand-dev@springbrand-dev"'; then
  "$WORKBUDDY_CLI" plugin update springbrand-dev@springbrand-dev --scope user
else
  "$WORKBUDDY_CLI" plugin install springbrand-dev@springbrand-dev --scope user
fi

"$WORKBUDDY_CLI" plugin enable springbrand-dev@springbrand-dev --scope user
```

For manual development installation, paste the same ZIP into **Add
Marketplace**, install **SpringBrand Dev**, and configure the runtime API key
through WorkBuddy's secure credential UI for the bundled `springbrand-dev` MCP
entry. If WorkBuddy cannot safely represent the Bearer credential, stop with
the exact manual fields instead of launching OAuth. After reload, verify version
`1.2.1-dev.2`, the five Canonical Skills, one Plugin-level Notice Hook,
one bundled `springbrand-dev` MCP entry, the authoritative identity check, and
the configured MCP service health check. Capability discovery remains a
separate functional test.

For GTM acceptance after restarting, use an unbranded growth request such as
“Analyze competitors for my AI product and recommend a positioning strategy.”
Verify `springbrand-gtm` enters Plugin discovery; use a direct GSC or Gmail
account request to exercise the Connector path. See
[the GTM dev evaluation cases](./docs/gtm-routing-evaluation.md).

Apply the initial-response rule above at the first result report or request
for user action; do not repeat Welcome if it was already shown.
