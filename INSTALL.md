# SpringBrand production CLI installation protocol

## Initial installation response

Execute one branch only. Do not infer a client, run `connect` without a client,
run `connect --all`, retry with another client, open an OAuth URL yourself, run
`auth login`, read another installation guide, or run a business operation.

Identify exactly one Host:

- Codex CLI or ChatGPT Desktop: use `codex`.
- Claude Code or Claude Desktop Code tab: use `claude-code`.
- WorkBuddy: use `workbuddy-ai`.
- Any other Agent: use the standard MCP branch below.

For a supported Host, run exactly one matching command:

```sh
# Codex CLI or ChatGPT Desktop
npx -y @springbrand/cli@latest connect codex --url https://connector.springbrand.ai/mcp

# Claude Code or Claude Desktop Code tab
npx -y @springbrand/cli@latest connect claude-code --url https://connector.springbrand.ai/mcp

# WorkBuddy
npx -y @springbrand/cli@latest connect workbuddy-ai --url https://connector.springbrand.ai/mcp
```

If the user explicitly provides an API key, append `--api-key <key>` to the
same command. Never print, log, repeat, or include the key in a report.

Wait for the command to exit. Let the user complete the browser flow opened by
the client, then continue waiting for the same command. On exit code `0`, report
the CLI status and any restart or new-session requirement it prints. On any
non-zero exit code, report the failed phase and stop. Do not run another
installation command.

For any other Agent, do not run `sp connect`. Configure the Agent's standard
remote MCP client with:

```text
URL: https://connector.springbrand.ai/mcp
Authentication: native MCP OAuth, or Authorization: Bearer <user-provided API key>
```

If the Agent cannot configure a remote MCP server, report that it is unsupported
and stop.
