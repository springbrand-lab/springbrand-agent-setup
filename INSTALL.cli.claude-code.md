# SpringBrand Claude Code single-client installation

Before any command, read and follow [the initial installation response](./INSTALL.md#initial-installation-response). Determine whether this is a first installation or an update, and keep that classification for the whole conversation.

This document configures **Claude Code only**. Do not detect, configure, update, or remove any other client. Preserve every unrelated configuration and existing MCP entry.

## Preferred CLI installation

Run exactly one command. Do not run `--help`, `doctor`, `auth status`, an all-client command, or a second install command first.

```sh
npx -y @springbrand/cli@latest connect claude-code --url https://connector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

The API key is supplied at runtime. Never print, log, save, repeat, or include it in a report. If no valid API key is available, omit `--api-key` and use the supported native OAuth flow for this client when prompted. Do not silently switch to another client or another environment.

If the command reports an invalid, expired, revoked, wrong-environment, or insufficient-scope key, stop and report only that stable failure category. Do not rerun the command with the same key. If the command reports an authentication or MCP authorization failure after accepting the key, retry once without `--api-key` only when the client explicitly offers its native OAuth flow. Never blind-retry.

## Required verification

After the command completes, report the actual status without revealing credentials. Verify all of the following for **Claude Code**:

1. The configured MCP entry is named `springbrand`.
2. The MCP URL is exactly `https://connector.springbrand.ai/mcp` and uses the client's native remote HTTP transport.
3. The client identity matches the production environment.
4. The configured MCP health check passes.
5. Existing configuration and every other client remain unchanged.

If the client requires a restart, reload, or new session, report that requirement and stop. Do not claim installation success until the identity and health checks pass. Do not run capability discovery or a business operation as a substitute for installation verification.

If the CLI cannot install this client, report the failed phase and continue only with the matching host-specific fallback in [INSTALL.md](./INSTALL.md). Keep the single-client scope when using that fallback.
Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.
