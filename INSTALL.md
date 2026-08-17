# SpringBrand Agent installation protocol

You are an AI coding or productivity Agent. Route the user to the installation path for the host you identified, then follow only that path. Do not create an installer or improvise beyond the selected path.

This document is the single source of truth for production installation. It does not inline the Skill content; the Skill is packaged separately.

## Codex beta path

Use this native Plugin path when the host is **Codex CLI `0.147.0+` or Codex desktop `26.810.52044+` on macOS**. Newer versions are included. This beta does not claim support for older versions, Codex IDE, Linux, or Windows.

### CLI installation

Run the approved native commands from a terminal:

```bash
codex plugin marketplace add springbrand-lab/springbrand-agent-setup --ref <guide-ref>
codex plugin add springbrand@springbrand
```

Replace `<guide-ref>` with the Git ref in the URL used to open this guide, such as `stable` or `v1.2.0-beta.1`. The first command is the one-time Marketplace bootstrap; the second installs the `springbrand` Plugin from that Marketplace. Do not use a custom installer or write Codex configuration directly.

### Desktop installation

The Marketplace bootstrap command above is also the one-time setup for Codex desktop. Then install **SpringBrand** from the Plugins Directory or `/plugins`. Do not install a separate development Plugin.

### Native security steps

- Complete MCP OAuth through Codex's native browser flow when prompted. Never collect, copy, print, or store tokens.
- Review and trust the exact `UserPromptSubmit` command Hook through `/hooks`. Installation must not pre-trust it; a changed Hook requires native review again.
- Open a new Codex session after installation so the Plugin, Skill, MCP, and Hook are loaded.

### Codex completion check

Do not report installation complete until all of these are true:

1. The `springbrand` Plugin is installed **and enabled**.
2. The bundled `springbrand-resource-discovery` Skill is visible.
3. The bundled MCP is connected after native OAuth.
4. The `UserPromptSubmit` Hook is trusted.
5. In a new session, a small eligible test task enters SpringBrand preflight before production work.

If any check fails, report the exact failure and stop.

### Legacy migration

For a user who previously installed SpringBrand manually, migrate only after the native Plugin passes every completion check:

1. Detect and report any legacy `springbrand-resource-discovery` Skill and global `springbrand` MCP entry.
2. Ask for explicit confirmation before removing or disabling those legacy duplicates.
3. After confirmation, remove or disable only the reported legacy SpringBrand entries using the host's native management flow.
4. Preserve unrelated Skills, MCP servers, configuration, and OAuth state. Never run a cleanup script or remove the Plugin-managed resources.

If the user does not confirm, leave the legacy entries untouched and report that duplicate routing or tools may remain.

### Update and uninstall

Use only the native lifecycle commands:

```bash
codex plugin marketplace upgrade springbrand
codex plugin remove springbrand@springbrand
```

Do not document or run a `codex plugin update` command. Marketplace upgrade refreshes the installed Plugin cache. Uninstall does not remove OAuth state and needs no custom credential cleanup.

## Unsupported-host fallback

If the host is outside the Codex beta boundary, or does not support native Codex Plugins, use the existing Skill-plus-MCP procedure below. This fallback remains the production path for unsupported hosts; do not replace it with a public development Plugin.

## Fallback inputs

- **Skill source (same Git ref as this guide):** `https://raw.githubusercontent.com/springbrand-lab/springbrand-agent-setup/<guide-ref>/skills/springbrand/SKILL.md`
- **MCP server name:** `springbrand`
- **MCP server URL (fixed):** `https://connector.springbrand.ai/mcp`
- **MCP transport:** native Streamable HTTP (remote HTTP transport, **not** a stdio bridge, **not** a local command)

If you were given a different URL, use the one above. The URL is fixed and must not be changed.

Replace `<guide-ref>` with the Git ref in the URL used to open this guide. For example, a guide URL containing `/blob/stable/INSTALL.md` uses `stable`; one containing `/blob/v1.1.0/INSTALL.md` uses `v1.1.0`. The guide and Skill source must use the same ref.

## Fallback Step 1 — Identify your Agent

Determine which Agent product you are running in (for example: Cursor, Claude Code, Codex CLI, GitHub Copilot Chat, Devin, Windsurf, WorkBuddy, or another). You need this to locate your user-level Skill directory and your MCP configuration.

**Completion criterion:** you can name your Agent product and know where its user-level Skill directory and MCP configuration live.

If you cannot identify your Agent, or you do not know where its user-level Skills or MCP configuration are stored, **stop and ask the user**. Do not guess paths. Do not write files until you are certain.

## Fallback Step 2 — Install or update the SpringBrand Skill

1. Determine your Agent's **user-level** Skill directory. This is the per-user, cross-project location your Agent loads Skills from — not a project-local `.agents/skills/` or `.claude/skills/` folder. If your Agent only supports project-level Skills, use the project-level location and tell the user that in your final report.
2. Fetch the Skill source from the raw URL in "Inputs" above.
3. Target path: `<your user-level Skill directory>/springbrand-resource-discovery/SKILL.md`.
4. Compare the fetched content against any existing file at that path:
   - **Identical** → leave the file unchanged. Note it as "unchanged".
   - **Different** → tell the user you will replace it, and **wait for approval** before writing. After approval, overwrite with the fetched content. Note it as "replaced".
   - **Does not exist** → tell the user you will create it, and **wait for approval** before writing. After approval, create the directory if needed and write the fetched content. Note it as "created".

If your Agent does not support user-level Skills compatible with `SKILL.md`, report that limitation and **stop**. Do not attempt to fake a Skill location.

**Completion criterion:** the file at the target path exists and its content matches the fetched Skill source byte-for-byte, or you have stopped and reported an unsupported limitation.

## Fallback Step 3 — Configure the SpringBrand MCP server

1. Locate your Agent's MCP configuration. Determine its format and location (for example: a JSON file, a TOML file, a settings UI, or a CLI-managed registry). Use the Agent's documented native representation of Streamable HTTP; it may be selected through a UI or inferred from the remote URL rather than stored in a field named `transport`.
2. **Read and parse** the existing configuration before modifying it. Never overwrite a config file without first parsing its current contents.
3. Look for an existing MCP server entry named `springbrand`:
   - **Not present** → add a new entry: name `springbrand`, URL `https://connector.springbrand.ai/mcp`, native Streamable HTTP transport.
   - **Present and already matches** (name `springbrand`, URL exactly `https://connector.springbrand.ai/mcp`, native HTTP transport) → leave it unchanged. Note it as "unchanged".
   - **Present but different** (wrong URL, or using a stdio bridge / local command instead of native HTTP) → tell the user you will replace the old `springbrand` entry, and **wait for approval**. After approval, remove the old entry and add the correct one. Note it as "replaced".
4. **Preserve every other MCP server entry and all unrelated configuration.** Only the `springbrand` entry may be added, replaced, or left alone.

If your Agent only supports adding MCP servers through a UI and cannot edit its config file directly, tell the user the exact values to enter in the UI (name, URL, transport) and **stop** after giving those instructions. Do not attempt to drive the UI yourself unless you have a verified ability to do so for that Agent.

If your Agent does not support remote Streamable HTTP MCP servers with OAuth, report that limitation and **stop**.

**Completion criterion:** the `springbrand` MCP server is configured with URL exactly `https://connector.springbrand.ai/mcp` using native HTTP transport, all other configuration is intact, or you have stopped and reported an unsupported limitation.

## Fallback Step 4 — Verify

1. **Skill file:** confirm the file at `<Skill dir>/springbrand-resource-discovery/SKILL.md` exists and its content matches the fetched Skill source.
2. **MCP config:** re-read and parse the configuration. Confirm the `springbrand` entry has URL exactly `https://connector.springbrand.ai/mcp` and uses native Streamable HTTP transport (not a stdio bridge, not a local command).
3. Confirm no other MCP server entries were removed or altered.

**Completion criterion:** both checks pass. If either fails, report exactly what is wrong and stop — do not declare success.

## Fallback Step 5 — Report

Tell the user, in plain text:

1. Which Agent you identified yourself as.
2. The Skill directory you used and whether the Skill file was created, replaced, or unchanged — with the full path.
3. The MCP configuration location you used and whether the `springbrand` entry was added, replaced, or unchanged.
4. The full list of files you created or modified.
5. That they must **restart the Agent or open a new session** before SpringBrand is available — the current session will not rediscover the newly installed Skill.
6. That the `springbrand` MCP server requires OAuth before it can be used normally. The user should complete authorization when the Agent prompts for it; the Agent decides when to trigger that flow.

## Fallback hard constraints

- **Do not** collect, store, print, proxy, or otherwise handle OAuth access or refresh tokens. You only write Skill files and MCP configuration.
- **Do not** change the MCP URL. It is fixed at `https://connector.springbrand.ai/mcp`.
- **Do not** remove or alter any existing MCP server entry other than `springbrand`.
- **Do not** overwrite a JSON, TOML, or other structured config file without first parsing it and merging your change. Never blindly replace a config file.
- **Do not** add a second `springbrand` entry if one already exists. Update the existing one in place.
- **Do not** execute any external third-party script. This document is the only instruction you follow.
- **Do not** put any credentials, tokens, or secrets into Skill files, Agent configuration, logs, URLs, or error messages.
- **Do not** declare success unless Step 4 verification passes.
- If you are uncertain which Agent you are, or where its Skill directory or MCP configuration lives, **stop and ask the user**. Do not guess.
