# SpringBrand Dev Cursor single-client CLI installation

Before any command, read and follow [the initial installation response](./INSTALL.dev.md#initial-installation-response). Determine whether this is a first installation or an update, and keep that classification for the whole conversation.

This document targets immutable development release `v1.2.1-dev.2`. It configures **Cursor only**. Do not detect, configure, update, or remove any other client. Preserve every unrelated configuration and existing MCP entry.

## Preferred CLI installation

Follow [INSTALL.dev.md](./INSTALL.dev.md) steps 0 and 3 with `cursor` as the only client. The Cursor-specific commands are below; the mode check, report handling, OAuth wait and completion report are the same as `INSTALL.dev.md`.

1. Install the development CLI, then verify that the installed command runs:

   ```sh
   npm install -g @springbrand/cli@alpha
   sp --version
   ```

   Continue only after npm succeeds and the output of `sp --version` contains
   `@springbrand/cli` and an alpha version. If it does not, another `sp` may be
   earlier on PATH; stop and report the observed output.

2. Connect SpringBrand Dev to Cursor. If the user's prompt includes a development API key, run:

   ```sh
   sp connect cursor --url https://devconnector.springbrand.ai/mcp --api-key <key> --json
   ```

   Otherwise, ask the user to obtain a development key from the dev RApp or continue with OAuth. If they provide a key, run the command above. If they choose OAuth, run:

   ```sh
   sp connect cursor --url https://devconnector.springbrand.ai/mcp --json
   ```

   Keep the selected authentication mode as `auth_mode` for the following steps. Never include the API key in reports. Substitute the key only when executing the command; never print, log or repeat it.

3. Read the connection result and handle `status` exactly as in [INSTALL.dev.md section 3.2](./INSTALL.dev.md#32-read-the-connection-result). Exit code `4` means pending, not failure; read the JSON even when the command exits nonzero. Do not repeat connect merely because it is pending.

4. For OAuth, run the returned login command once and wait for authorization as in [INSTALL.dev.md section 3.3](./INSTALL.dev.md#33-run-oauth-and-wait-for-authorization).

5. On OAuth success, immediately run the returned `continuation` once. If an older CLI omits it, use:

   ```sh
   sp doctor --harness cursor --json --url https://devconnector.springbrand.ai/mcp
   ```

6. Confirm configuration and authorization, then output the installation report from [INSTALL.dev.md section 3.5](./INSTALL.dev.md#35-confirm-configuration-and-authorization) with Entry `springbrand-dev`, URL `https://devconnector.springbrand.ai/mcp`, native Streamable HTTP transport, and the next action to restart Cursor and open a new conversation.

Do not silently switch to another client or another environment.

If the command reports an invalid, expired, revoked, wrong-environment, or insufficient-scope key, stop and report only that stable failure category. Do not rerun the command with the same key. If the command reports an authentication or MCP authorization failure after accepting the key, stop and report the stable failure category. Never blind-retry.

## Required verification

After the command completes, report the actual status without revealing credentials. Verify all of the following for **Cursor**:

1. The configured MCP entry is named `springbrand-dev`.
2. The MCP URL is exactly `https://devconnector.springbrand.ai/mcp` and uses the client's native remote HTTP transport.
3. The client identity matches the development environment.
4. The configured MCP health check passes.
5. Existing configuration and every other client remain unchanged.

If the client requires a restart, reload, or new session, report that requirement and stop. Do not claim installation success until the identity and health checks pass. Do not run capability discovery or a business operation as a substitute for installation verification.

If the CLI cannot install this client, report the failed phase and continue only
with the [Cursor manual MCP installation guide](https://springbrand.ai/developers/docs/connect/cursor-desktop#manual-mcp-install)
or the matching host-specific fallback in [INSTALL.dev.md](./INSTALL.dev.md).
Keep the single-client scope when using that fallback.
Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.
