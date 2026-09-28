# SpringBrand Cursor single-client CLI installation

Before any command, read and follow [the initial installation response](./INSTALL.md#initial-installation-response). Determine whether this is a first installation or an update, and keep that classification for the whole conversation.

This document configures **Cursor only**. Do not detect, configure, update, or remove any other client. Preserve every unrelated configuration and existing MCP entry.

## Preferred CLI installation

After any required API-key preparation, run exactly one connect command. Do not run `--help`, `doctor`, an all-client command, or a second connect command first.

```sh
npx -y @springbrand/cli@latest connect cursor --url https://connector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

The Agent must never print, log, repeat, or include the key in a report. Choose exactly one branch:

- **Key supplied:** run the command above with `--api-key {{INSTALL_KEY}}`.
- **No key supplied:** do not run the CLI yet. Show or open `https://rapp.springbrand.ai/account-settings?section=mcp-api-keys`. Ask the user to register or sign in, create or copy the key, and provide it through the secure input channel. Wait for the key. After the user provides it, run the command above with `--api-key {INSTALL_KEY}`. Do not print, log, repeat, or include the key in the report.
- **OAuth fallback:** only after the user cannot use an API key or explicitly chooses OAuth after a failed key attempt, run the native OAuth flow with `npx -y @springbrand/cli@latest connect cursor --url https://connector.springbrand.ai/mcp` without `--api-key`. Do not run `auth login` in this branch.

Do not silently switch to another client or another environment.

If the command reports an invalid, expired, revoked, wrong-environment, or insufficient-scope key, stop and report only that stable failure category. Do not rerun the command with the same key. If the command reports an authentication or MCP authorization failure after accepting the key, stop and report the stable failure category. Retry without `--api-key` only after the user explicitly chooses the OAuth fallback. Never blind-retry.

## Required verification

After the command completes, report the actual status without revealing credentials. Verify that the configured MCP entry is named `springbrand`, the URL is exactly `https://connector.springbrand.ai/mcp`, the client identity matches production, the configured MCP health check passes, and every other client and unrelated configuration remains unchanged.

If the client requires a restart, reload, or new session, report that requirement and stop. Do not claim installation success until the identity and health checks pass. Do not run capability discovery or a business operation as a substitute for installation verification.

If the CLI cannot install this client, report the failed phase and continue only with the matching host-specific fallback in [INSTALL.md](./INSTALL.md). Keep the single-client scope when using that fallback.
Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.
