# SpringBrand Dev Claude Plugin

This internal-testing Host Adapter supports the Claude Code CLI and Claude Desktop Code tab on macOS. It does not support Claude Chat, Cowork, web sessions, or account-level Connectors.

## Install

First disable or uninstall the production `springbrand` Plugin. Then run:

```sh
claude plugin marketplace add springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1 --scope user
claude plugin install springbrand-dev@springbrand-dev --scope user
claude mcp login plugin:springbrand-dev:springbrand-dev
```

Confirm:

```sh
claude plugin details springbrand-dev@springbrand-dev
claude mcp list
```

The Plugin must show one `springbrand-dev` MCP server at `https://devconnector.springbrand.ai/mcp`. Authentication uses Claude's native OAuth; do not add credentials or a second global MCP server.

Start a fresh session and verify that eligible work invokes `/springbrand-dev:springbrand` before planning or production.

## Claude Desktop Code

Open **Plugin Browser → Add Marketplace** and enter:

```text
springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1
```

Install **SpringBrand Dev**, complete OAuth, then open a new Code task. CLI success is not Desktop evidence; verify routing and lifecycle in Desktop separately.

## Remove

```sh
claude plugin uninstall springbrand-dev@springbrand-dev --scope user
```

Confirm the bundled `springbrand-dev` entry disappears while unrelated configuration remains intact. Re-enable production only after the dev Plugin is removed.
