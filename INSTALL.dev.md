# SpringBrand development CLI installation protocol

Development release identity: `v1.2.1-dev.2`, entry `springbrand-dev`, endpoint
`https://devconnector.springbrand.ai/mcp`.

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
   - ChatGPT Web or Cowork Web: use the Other Agent install workflow below.
   - Any other Agent: use the Other Agent install workflow below.

2. Check whether the user's Prompt contains a development API key and select one command:

   ```sh
   # No API key
   npx -y @springbrand/cli@alpha connect <client> --url https://devconnector.springbrand.ai/mcp

   # API key supplied
   npx -y @springbrand/cli@alpha connect <client> --url https://devconnector.springbrand.ai/mcp --api-key <key>
   ```

   Never print, log, repeat, or include the key in a report.

3. Run the selected command exactly once.

4. Wait for the command to exit. Let the user complete the browser flow opened
   by the client, then continue waiting for the same command.

5. Finish the supported-client flow:

   - Exit code `0`: report the CLI status and any restart or new-session requirement it prints.
   - Any non-zero exit code: report the failed phase and stop.
   - Do not run another installation command.

6. Installation completion report

   After the command completes, report the actual status without revealing credentials:

   1. The configured MCP entry is named `springbrand-dev`.
   2. The MCP URL is exactly `https://devconnector.springbrand.ai/mcp` and uses the selected client's native remote HTTP transport.
   3. The client identity matches the development environment.
   4. The configured MCP health check passes.
   5. Existing configuration and every other client remain unchanged.

   Close the report with a one-sentence capability note: SpringBrand Dev gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

## Other Agent install workflow

1. Do not run `sp connect`. Configure the Agent's standard remote MCP client
   with:

   ```text
   URL: https://devconnector.springbrand.ai/mcp
   Authentication: native MCP OAuth, or Authorization: Bearer <user-provided development API key>
   ```

2. If standard remote MCP configuration or authentication fails, report:

   - Status: failed; phase: MCP configuration or authentication.
   - Host limitation, if applicable: standard remote MCP is unsupported.
   - SpringBrand configuration: unchanged; credentials not displayed.

   Stop. Do not run another installation command.

3. Installation completion report

   Report the actual status without revealing credentials:

   - MCP entry: `springbrand-dev`.
   - URL: `https://devconnector.springbrand.ai/mcp`; native Streamable HTTP transport.
   - Authentication: OAuth or development API key; development identity.
   - MCP health check: passed, failed, or unverified.
   - Existing configuration and every other client: unchanged.
   - Restart or new-session requirement; Skill status, if any.

   Close with a one-sentence note about the capabilities available through SpringBrand Dev MCP. Do not claim a Skill was installed unless verified. Then ask the user what they would like to build first.
