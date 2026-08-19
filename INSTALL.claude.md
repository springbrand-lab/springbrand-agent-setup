# SpringBrand Claude Code Plugin

This guide verifies the Claude Code Host Adapter for the Claude Code CLI and the Claude Desktop Code tab on macOS. It does not claim support for Claude Chat, Cowork, web sessions, or account-level Connectors.

## Validate the package

From a checkout of this repository:

```sh
claude plugin validate --strict .
claude plugin validate --strict .claude-plugin/plugin.json
python3 tests/validate_plugin.py
```

The first command validates Marketplace metadata, the second validates the Plugin manifest, and the package-contract check rejects credential files and static authentication material. The package contains one Canonical Skill at `skills/springbrand/SKILL.md`, one static `UserPromptSubmit` routing Hook, and one remote HTTP MCP declaration. The MCP declaration is exactly:

```json
{"type":"http","url":"https://connector.springbrand.ai/mcp"}
```

It contains no token, header, client secret, API key, or extra OAuth resource parameter. Authentication is handled by Claude's native MCP OAuth flow.

## Before installing

Check Claude for an existing global `springbrand` MCP entry or SpringBrand Skill and report duplicates before continuing. Do not delete or replace a legacy SpringBrand entry, OAuth state, or unrelated configuration without explicit user approval.

## Install and authenticate

```sh
claude plugin marketplace add springbrand-lab/springbrand-agent-setup --scope user
claude plugin install springbrand@springbrand --scope user
claude mcp login plugin:springbrand:springbrand
```

Approve the Plugin and MCP server when Claude prompts. Do not run `claude mcp add` for `springbrand`; the Plugin already bundles that MCP entry. Confirm the install with:

```sh
claude plugin list
claude plugin details springbrand@springbrand
claude mcp list
```

Start a fresh session and verify that a covered request invokes `/springbrand:springbrand` (the `springbrand-plugin-discovery` Canonical Skill) before planning or production work. The Hook is local, static, deterministic, prompt-stateless, and network-free; it only injects the routing instruction. Discovery itself happens through the Canonical Skill and MCP.

## Reload, update, and uninstall

For a running CLI session, run:

```text
/reload-plugins
```

Restart Claude when a Hook or MCP path change is not picked up by reload. Update and remove through the native lifecycle:

```sh
claude plugin update springbrand@springbrand --scope user
claude plugin uninstall springbrand@springbrand --scope user
```

After uninstalling, confirm the Plugin and its bundled `springbrand` MCP entry are gone. Existing unrelated Plugins, MCP servers, Skill files, and OAuth state must remain unchanged. A pre-existing global SpringBrand entry is not removed automatically; remove it only with explicit user approval.

## Claude Desktop Code tab

The Claude Code Plugin engine is shared with the Desktop Code tab. Add the Marketplace and install the Plugin with the native CLI commands above, then open a new Desktop Code session. Verify Skill visibility, native OAuth, routing-before-work, update/reload behavior, and uninstall cleanup separately in Desktop. Do not treat CLI evidence as Desktop Native Evidence.
