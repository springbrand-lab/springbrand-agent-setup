# SpringBrand Cursor single-client CLI installation

Before any command, read and follow [the initial installation response](./INSTALL.md#initial-installation-response). Determine whether this is a first installation or an update, and keep that classification for the whole conversation.

This document configures **Cursor only**. Do not detect, configure, update, or remove any other client. Preserve every unrelated configuration and existing MCP entry.

## Preferred CLI installation

Follow [INSTALL.md](./INSTALL.md) steps 0 and 3 with `cursor` as the only client. The Cursor-specific commands are below; the mode check, report handling, OAuth wait and completion report are the same as `INSTALL.md`.

1. Install the latest CLI, then verify that the installed command runs:

   ```sh
   npm install -g @springbrand/cli@latest
   sp --version
   ```

   Continue only after npm succeeds and `sp --version` runs successfully.

2. Connect SpringBrand to Cursor. If the user's prompt includes an API key, run:

   ```sh
   sp connect cursor --url https://connector.springbrand.ai/mcp --api-key <key> --json
   ```

   Otherwise, ask the user to obtain a key from the production RApp or continue with OAuth. A production SpringBrand account is required; if the user does not have one, ask them to register at https://rapp.springbrand.ai/. Once they provide a key, run the command above. If they choose OAuth, run:

   ```sh
   sp connect cursor --url https://connector.springbrand.ai/mcp --json
   ```

   Keep the selected authentication mode as `auth_mode` for the following steps. Never include the API key in reports. Substitute the key only when executing the command; never print, log or repeat it.

3. Read the connection result and handle `status` exactly as in [INSTALL.md section 3.2](./INSTALL.md#32-read-the-connection-result). Exit code `4` means pending, not failure; read the JSON even when the command exits nonzero. Do not repeat connect merely because it is pending.

4. For OAuth, run the returned login command once and wait for authorization as in [INSTALL.md section 3.3](./INSTALL.md#33-run-oauth-and-wait-for-authorization).

5. On OAuth success, immediately run the returned `continuation` once. If an older CLI omits it, use:

   ```sh
   sp doctor --harness cursor --json --url https://connector.springbrand.ai/mcp
   ```

6. Confirm configuration and authorization, then output the installation report from [INSTALL.md section 3.5](./INSTALL.md#35-confirm-configuration-and-authorization) with Entry `springbrand`, URL `https://connector.springbrand.ai/mcp`, native Streamable HTTP transport, and the next action to restart Cursor and open a new conversation.

Do not silently switch to another client or another environment.

If the command reports an invalid, expired, revoked, wrong-environment, or insufficient-scope key, stop and report only that stable failure category. Do not rerun the command with the same key. If the command reports an authentication or MCP authorization failure after accepting the key, stop and report the stable failure category. Never blind-retry.

## Required verification

After the command completes, report the actual status without revealing credentials. Verify that the configured MCP entry is named `springbrand`, the URL is exactly `https://connector.springbrand.ai/mcp`, the client identity matches production, the configured MCP health check passes, and every other client and unrelated configuration remains unchanged.

If the client requires a restart, reload, or new session, report that requirement and stop. Do not claim installation success until the identity and health checks pass. Do not run capability discovery or a business operation as a substitute for installation verification.

If the CLI cannot install this client, report the failed phase and continue only
with the [Cursor manual MCP installation guide](https://springbrand.ai/developers/docs/connect/cursor-desktop#manual-mcp-install)
or the matching host-specific fallback in [INSTALL.md](./INSTALL.md). Keep the
single-client scope when using that fallback.
Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.
