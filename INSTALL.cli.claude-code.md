# SpringBrand Claude Code / Claude Desktop Cowork installation

Before any command, read and follow [the initial installation response](./INSTALL.md#initial-installation-response). Determine whether this is a first installation or an update, and keep that classification for the whole conversation.

This document configures **one Claude surface only**: either the Claude Code
CLI or Claude Desktop Cowork. Identify the active surface before changing
anything. Do not configure, update, or remove the other Claude surface or any
other client. Do not detect, configure, update, or remove any other client.
Preserve every unrelated configuration and existing MCP entry.

Claude Code CLI and Claude Desktop Cowork use different installation paths.

### Mandatory surface selection

Apply these rules before any command or UI handoff:

- If the user says **Claude Code**, **terminal**, or **CLI**, use the Claude
  Code CLI branch.
- If the user says **Claude Desktop**, **Cowork**, or **chat**, use the Claude
  Desktop Cowork branch.
- If the surface is unclear, ask which surface the user is using before
  choosing a branch. Never run both branches.

After selecting the surface, follow exactly one path:

- **Claude Code CLI:** use the SpringBrand CLI command below. This writes the
  Claude Code MCP registration and Skill.
- **Claude Desktop Cowork:** do not run `connect claude-code` and do not edit
  `claude_desktop_config.json`. Install the Plugin from Claude's native
  **Cowork → Customize → Plugins** flow, then authorize its remote Connector.
  Cowork account Plugins and remote Connectors are not installed by the local
  SpringBrand CLI.

## Claude Code CLI installation

After any required API-key preparation, run exactly one connect command. Do not run `--help`, `doctor`, an all-client command, or a second connect command first.

```sh
npx -y @springbrand/cli@latest connect claude-code --url https://connector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

The Agent must never print, log, repeat, or include the key in a report. Choose exactly one branch:

- **Key supplied:** run the command above with `--api-key {{INSTALL_KEY}}`.
- **No key supplied:** do not run the CLI yet. Show or open `https://rapp.springbrand.ai/account-settings?section=mcp-api-keys`. Ask the user to register or sign in, create or copy the key, and provide it through the secure input channel. Wait for the key. After the user provides it, run the command above with `--api-key {INSTALL_KEY}`. Do not print, log, repeat, or include the key in the report.
- **OAuth fallback:** only after the user cannot use an API key or explicitly chooses OAuth after a failed key attempt, run the native OAuth flow with `npx -y @springbrand/cli@latest connect claude-code --url https://connector.springbrand.ai/mcp` without `--api-key`. Do not run `auth login` in this branch.

Do not silently switch to another client or another environment.

If the command reports an invalid, expired, revoked, wrong-environment, or insufficient-scope key, stop and report only that stable failure category. Do not rerun the command with the same key. If the command reports an authentication or MCP authorization failure after accepting the key, stop and report the stable failure category. Retry without `--api-key` only after the user explicitly chooses the OAuth fallback. Never blind-retry.

## Claude Desktop Cowork installation

Use this branch when the active surface is Claude Desktop's **Cowork** tab:

1. Open **Cowork → Customize → Plugins**.
2. Add the SpringBrand GitHub Marketplace/repository:
   `springbrand-lab/springbrand-agent-setup`.
3. Install and enable the `springbrand` Plugin.
4. In the Plugin's Connector area, connect the remote MCP server at
   `https://connector.springbrand.ai/mcp` through Claude's native OAuth flow.
5. Start a new Cowork task and verify that the SpringBrand Skills are visible
   and the `springbrand` Connector can discover the five Meta Tools.

Do not provide an API key to the Cowork flow, run `connect claude-code`, or
write `claude_desktop_config.json`. Cowork remote Connectors are account-level
and are reached from Anthropic's cloud; local Desktop MCP configuration is a
separate mechanism and is unavailable to Cowork.

## Required verification

After the selected branch completes, report the actual status without revealing credentials. Verify all of the following for the selected surface:

1. The configured Plugin/Connector entry is named `springbrand`.
2. The MCP URL is exactly `https://connector.springbrand.ai/mcp` and uses the client's native remote HTTP transport.
3. The client identity matches the production environment.
4. The configured MCP health check passes in that surface.
5. Existing configuration and every other client remain unchanged.

If the client requires a restart, reload, or new session, report that requirement and stop. Do not claim installation success until the identity and health checks pass. Do not run capability discovery or a business operation as a substitute for installation verification.

If the Claude Code CLI cannot install its surface, report the failed phase and
continue only with the matching Plugin fallback in [INSTALL.plugin.md](./INSTALL.plugin.md).
If Cowork cannot complete its native Plugin or Connector flow, report the
failed UI/OAuth phase; do not fall back to a Claude Code CLI command.
Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.
