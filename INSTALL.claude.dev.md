# SpringBrand Dev Claude Plugin

Before validation, connectivity checks, installation commands or UI handoffs,
read and follow [Initial installation response](./INSTALL.plugin.dev.md#initial-installation-response).
Determine first installation versus ordinary update before changing anything.

This guide targets immutable development release `v1.2.1-dev.2`. It configures
the Claude Code CLI or the Claude Desktop Code tab for the development Plugin
only. Do not install the production Plugin or configure any other client.

## Install and authenticate

The development package uses the `springbrand-dev` Plugin and one remote MCP
entry at `https://devconnector.springbrand.ai/mcp`. It contains no token,
header, client secret, or API key; authentication uses Claude's native OAuth.

```sh
claude plugin marketplace add springbrand-lab/springbrand-agent-setup@v1.2.1-dev.2 --scope user
claude plugin install springbrand-dev@springbrand-dev --scope user
claude mcp login plugin:springbrand-dev:springbrand-dev
```

Approve the development Plugin and MCP server when Claude prompts. Do not run
`claude mcp add`; the Plugin already bundles the MCP entry. Confirm with:

```sh
claude plugin list
claude plugin details springbrand-dev@springbrand-dev
claude mcp list
```

Start a fresh Desktop Code session and verify the development Plugin, five
development Skills, native OAuth, and the `springbrand-dev` MCP entry before
using SpringBrand.

## Reload, update, and uninstall

For a running CLI session, run `/reload-plugins`. Restart Claude when a Hook or
MCP path change is not picked up by reload.

```sh
claude plugin update springbrand-dev@springbrand-dev --scope user
claude plugin uninstall springbrand-dev@springbrand-dev --scope user
```

After uninstalling, confirm the development Plugin and its bundled MCP entry
are gone. Existing unrelated Plugins, MCP servers, Skills, and OAuth state must
remain unchanged.

## Claude Desktop Code tab

The Claude Code Plugin engine is shared with the Desktop Code tab. Add the
development Marketplace and install the development Plugin with the commands
above, then open a new Desktop Code session. Do not treat production Plugin or
CLI evidence as development Desktop evidence.
