# SpringBrand production CLI installation protocol

## Install workflow

Do not infer a client.
Do not run `connect` without a client.
Do not run `connect --all`.
Do not retry with another client.
Do not open an OAuth URL yourself.
Do not run `auth login`.
Do not read another installation guide.
Do not run a business operation.

1. Identify exactly one Host and select its CLI client:

   - Codex CLI or ChatGPT Desktop: `codex`
   - Claude Code or Claude Desktop Code tab: `claude-code`
   - WorkBuddy: `workbuddy-ai`
   - Cursor: `cursor`
   - OpenCode: `opencode`
   - Pi: `pi`
   - Any other Agent: go to step 6.

2. Run exactly one command for the selected CLI client:

   ```sh
   npx -y @springbrand/cli@latest connect <client> --url https://connector.springbrand.ai/mcp
   ```

3. If the user explicitly provides an API key, append `--api-key <key>` to the
   same command. Never print, log, repeat, or include the key in a report.

4. Wait for the command to exit. Let the user complete the browser flow opened
   by the client, then continue waiting for the same command.

5. Finish the supported-client flow:

   - Exit code `0`: report the CLI status and any restart or new-session requirement it prints.
   - Any non-zero exit code: report the failed phase and stop.
   - Do not run another installation command.

6. For any other Agent, do not run `sp connect`. Configure its standard remote
   MCP client with:

   ```text
   URL: https://connector.springbrand.ai/mcp
   Authentication: native MCP OAuth, or Authorization: Bearer <user-provided API key>
   ```

7. If the Agent cannot configure a remote MCP server, report that it is
   unsupported and stop.
