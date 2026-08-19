# SpringBrand Agent installation protocol — Development

You are an AI coding or productivity Agent. A user has asked you to install or update the **SpringBrand development** environment by following this document. Identify the host and use exactly one path below:

1. **Native Plugin path** for Codex CLI/Desktop, Claude Code CLI/Desktop Code, Cursor desktop, or WorkBuddy desktop.
2. **Manual Skill-plus-MCP fallback** for unsupported hosts.

Do not run both paths. This document is the single source of truth for development installation.

## Native `springbrand-dev` Plugin

The immutable internal-testing release is:

| Field | Value |
| --- | --- |
| Plugin / Marketplace ID | `springbrand-dev` |
| Display name | SpringBrand Dev |
| Version | `1.2.0-beta.4-dev.1` |
| Git ref | `v1.2.0-beta.4-dev.1` |
| MCP server name | `springbrand-dev` |
| MCP URL | `https://devconnector.springbrand.ai/mcp` |
| Transport | Native remote HTTP / Streamable HTTP |
| Authentication | Host-native OAuth |

The Plugin contains the same Canonical Skill and routing behavior as production. **Disable or uninstall the full production `springbrand` Plugin before enabling the full `springbrand-dev` Plugin.** Do not edit Plugin caches, override the bundled URL, add static credentials, or register a second dev MCP server.

### Codex CLI and Desktop

```sh
codex plugin marketplace add springbrand-lab/springbrand-agent-setup --ref v1.2.0-beta.4-dev.1
codex plugin add springbrand-dev@springbrand-dev
codex mcp login springbrand-dev
```

The Marketplace bootstrap also exposes **SpringBrand Dev** in the Codex desktop Plugins Directory. Install it there if using Desktop, then open a new task.

### Claude Code CLI and Desktop Code

CLI:

```sh
claude plugin marketplace add springbrand-lab/springbrand-agent-setup@v1.2.0-beta.4-dev.1 --scope user
claude plugin install springbrand-dev@springbrand-dev --scope user
claude mcp login plugin:springbrand-dev:springbrand-dev
```

Desktop Code: open **Plugin Browser → Add Marketplace** and enter:

```text
springbrand-lab/springbrand-agent-setup@v1.2.0-beta.4-dev.1
```

Install **SpringBrand Dev**, complete OAuth, and open a new Code task. This does not apply to Claude Chat, Cowork, web sessions, or account-level Connectors.

### Cursor desktop

Open **Customize → Browse Marketplace → Add Marketplace → Import from GitHub** and enter:

```text
springbrand-lab/springbrand-agent-setup@v1.2.0-beta.4-dev.1
```

Install **SpringBrand Dev**, complete OAuth for `springbrand-dev`, and open a new task.

### WorkBuddy desktop

Open **Experts · Skills · Connectors → Add Marketplace** and enter this
immutable development ZIP source:

```text
https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.0-beta.4-dev.1.zip
```

WorkBuddy does not accept the `owner/repo@tag` shorthand. Install **SpringBrand Dev**,
complete OAuth for `springbrand-dev`, and open a new task.

### Native Plugin verification and removal

Verify that the installed Plugin shows:

- Plugin ID `springbrand-dev` and version `1.2.0-beta.4-dev.1`;
- exactly one bundled `springbrand-dev` MCP entry;
- URL exactly `https://devconnector.springbrand.ai/mcp`;
- the `springbrand-resource-discovery` Canonical Skill;
- the host-appropriate routing Hook or Rule.

After testing, uninstall `springbrand-dev` through the host's native Plugin lifecycle and confirm its bundled components disappear while unrelated configuration remains intact. Re-enable production only after the full dev Plugin is removed. If this path succeeds, **stop here and do not run the fallback**.

## Manual Skill-plus-MCP fallback

Use this path only when the host cannot install the native Plugin. Unlike two complete Plugins, this fallback may coexist with production because it shares one Skill file and adds only the separately named `springbrand-dev` MCP entry.

### What this installs

Two things, both user-level (not project-level):

1. **The SpringBrand Skill** — a `SKILL.md` file that teaches you to check SpringBrand Resources before building or recommending a solution. This is the **same Skill** used by the production environment; dev and production share one Skill file and do not create a second copy.
2. **The SpringBrand dev MCP server** — a remote MCP server named `springbrand-dev` at a fixed dev URL, which exposes SpringBrand capabilities and connected providers in the development environment.

The SpringBrand dev MCP server requires OAuth authorization before it can be used normally. Follow your Agent's normal MCP setup and connection flow; your Agent decides when to trigger OAuth. If authorization is completed during installation, leave it intact.

### Inputs

- **Skill source:** `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/v1.2.0-beta.4-dev.1/skills/springbrand/SKILL.md`
- **MCP server name:** `springbrand-dev`
- **MCP server URL (fixed):** `https://devconnector.springbrand.ai/mcp`
- **MCP transport:** native Streamable HTTP (remote HTTP transport, **not** a stdio bridge, **not** a local command)

If you were given a different URL, use the one above. The dev URL is fixed and must not be changed.

The development Plugin and fallback Skill are pinned to the same immutable dev tag. Do not use `main`, `stable`, or a production tag for development installation.

### Fallback Step 1 — Identify your Agent

Determine which Agent product you are running in (for example: Cursor, Claude Code, Codex CLI, GitHub Copilot Chat, Devin, Windsurf, WorkBuddy, or another). You need this to locate your user-level Skill directory and your MCP configuration.

**Completion criterion:** you can name your Agent product and know where its user-level Skill directory and MCP configuration live.

If you cannot identify your Agent, or you do not know where its user-level Skills or MCP configuration are stored, **stop and ask the user**. Do not guess paths. Do not write files until you are certain.

### Fallback Step 2 — Install or update the SpringBrand Skill

The development environment uses the **same Skill** as production. Do not create a second Skill, do not rename it, and do not copy its content into a dev-specific file.

1. Determine your Agent's **user-level** Skill directory. This is the per-user, cross-project location your Agent loads Skills from — not a project-local `.agents/skills/` or `.claude/skills/` folder. If your Agent only supports project-level Skills, use the project-level location and tell the user that in your final report.
2. Fetch the Skill source from the raw URL in "Inputs" above.
3. Target path: `<your user-level Skill directory>/springbrand-resource-discovery/SKILL.md`.
4. Compare the fetched content against any existing file at that path:
   - **Identical** → leave the file unchanged. Note it as "unchanged".
   - **Different** → tell the user you will replace it, and **wait for approval** before writing. After approval, overwrite with the fetched content. Note it as "replaced".
   - **Does not exist** → tell the user you will create it, and **wait for approval** before writing. After approval, create the directory if needed and write the fetched content. Note it as "created".

A dev install must never silently overwrite a Skill whose content differs from the fetched source. Always tell the user first and wait for approval.

If your Agent does not support user-level Skills compatible with `SKILL.md`, report that limitation and **stop**. Do not attempt to fake a Skill location.

**Completion criterion:** the file at the target path exists and its content matches the fetched Skill source byte-for-byte, or you have stopped and reported an unsupported limitation.

### Fallback Step 3 — Configure the SpringBrand dev MCP server

1. Locate your Agent's MCP configuration. Determine its format and location (for example: a JSON file, a TOML file, a settings UI, or a CLI-managed registry). Use the Agent's documented native representation of Streamable HTTP; it may be selected through a UI or inferred from the remote URL rather than stored in a field named `transport`.
2. **Read and parse** the existing configuration before modifying it. Never overwrite a config file without first parsing its current contents. Merge your change into the parsed structure; do not replace the whole file.
3. Look for an existing MCP server entry named `springbrand-dev`:
   - **Not present** → add a new entry: name `springbrand-dev`, URL `https://devconnector.springbrand.ai/mcp`, native Streamable HTTP transport.
   - **Present and already matches** (name `springbrand-dev`, URL exactly `https://devconnector.springbrand.ai/mcp`, native HTTP transport) → leave it unchanged. Note it as "unchanged".
   - **Present but different** (wrong URL, or using a stdio bridge / local command instead of native HTTP) → tell the user you will replace the old `springbrand-dev` entry, and **wait for approval**. After approval, remove the old entry and add the correct one. Note it as "replaced".
4. **Preserve every other MCP server entry and all unrelated configuration.** Only the `springbrand-dev` entry may be added, replaced, or left alone. In particular, do **not** delete or modify the production `springbrand` entry if it exists — the two environments are meant to coexist, and the production entry is managed exclusively by `INSTALL.md`.

If your Agent only supports adding MCP servers through a UI and cannot edit its config file directly, tell the user the exact values to enter in the UI (name `springbrand-dev`, URL `https://devconnector.springbrand.ai/mcp`, native HTTP transport) and **stop** after giving those instructions. Do not attempt to drive the UI yourself unless you have a verified ability to do so for that Agent.

If your Agent does not support remote Streamable HTTP MCP servers with OAuth, report that limitation and **stop**.

**Completion criterion:** the `springbrand-dev` MCP server is configured with URL exactly `https://devconnector.springbrand.ai/mcp` using native HTTP transport, all other configuration (including any production `springbrand` entry) is intact, or you have stopped and reported an unsupported limitation.

### Fallback Step 4 — Verify

1. **Skill file:** confirm the file at `<Skill dir>/springbrand-resource-discovery/SKILL.md` exists and its content matches the fetched Skill source.
2. **MCP config:** re-read and parse the configuration. Confirm the `springbrand-dev` entry has URL exactly `https://devconnector.springbrand.ai/mcp` and uses native Streamable HTTP transport (not a stdio bridge, not a local command).
3. Confirm no other MCP server entries were removed or altered — including the production `springbrand` entry, which must remain untouched.

**Completion criterion:** both checks pass. If either fails, report exactly what is wrong and stop — do not declare success.

### Fallback Step 5 — Report

Tell the user, in plain text:

1. Which Agent you identified yourself as.
2. The Skill directory you used and whether the Skill file was created, replaced, or unchanged — with the full path. Note that this is the shared Skill used by both production and development.
3. The MCP configuration location you used and whether the `springbrand-dev` entry was added, replaced, or unchanged.
4. The full list of files you created or modified.
5. That they must **restart the Agent or open a new session** before the SpringBrand dev MCP server is available — the current session will not rediscover the newly installed configuration.
6. That the `springbrand-dev` MCP server requires OAuth before it can be used normally. The user should complete authorization when the Agent prompts for it; the Agent decides when to trigger that flow.
7. That this installed the **development** environment (`springbrand-dev`), which is for testing only and is separate from any production `springbrand` install. The manual fallback and production can coexist.

### Fallback hard constraints

- **Do not** collect, store, print, proxy, or otherwise handle OAuth access or refresh tokens. You only write Skill files and MCP configuration.
- **Do not** change the MCP URL. It is fixed at `https://devconnector.springbrand.ai/mcp` for the dev environment.
- **Do not** name the MCP entry `springbrand`. The dev entry must be named `springbrand-dev` so it can coexist with the production `springbrand` entry.
- **Do not** remove or alter any existing MCP server entry other than `springbrand-dev`. In particular, do **not** delete or modify the production `springbrand` entry.
- **Do not** add a second `springbrand-dev` entry if one already exists. Update the existing one in place.
- **Do not** overwrite a JSON, TOML, or other structured config file without first parsing it and merging your change. Never blindly replace a config file.
- **Do not** create a second, dev-specific Skill. Dev and production share the single `springbrand-resource-discovery` Skill fetched from the official repository.
- **Do not** silently overwrite a Skill whose content differs from the fetched source. Tell the user first and wait for approval.
- **Do not** execute any external third-party script. This document is the only instruction you follow.
- **Do not** put any credentials, tokens, or secrets into Skill files, Agent configuration, logs, URLs, or error messages.
- **Do not** declare success unless Step 4 verification passes.
- If you are uncertain which Agent you are, or where its Skill directory or MCP configuration lives, **stop and ask the user**. Do not guess.
