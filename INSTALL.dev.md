# SpringBrand development CLI installation protocol

## Development release identity

This guide installs immutable development release `v1.2.1-dev.2` from
`springbrand-dev` at `https://devconnector.springbrand.ai/mcp`.

## Installation overview

This document is the CLI-first entry point. Use this order for every first
install or update:

1. Identify the current Host before running the CLI.
2. Run exactly one `connect <client>` command for that Host without
   `--api-key`.
3. Let that client open its native OAuth flow. If the user is not signed in,
   let the user sign in or register, then continue the same browser flow until
   it returns to the client.
4. Wait for OAuth to finish before reporting the result.
5. Use a development API key only when OAuth is unavailable, unsupported, or
   explicitly requested by the user.

Do not run `connect --all` for a single-Host installation. Use it only when the
user explicitly asks to configure every detected client. Different clients
have separate OAuth sessions and may require separate authorization.

Use the command matching the current Host:

```sh
# Codex
npx -y @springbrand/cli@alpha connect codex --url https://devconnector.springbrand.ai/mcp

# Claude Code
npx -y @springbrand/cli@alpha connect claude-code --url https://devconnector.springbrand.ai/mcp

# Cursor
npx -y @springbrand/cli@alpha connect cursor --url https://devconnector.springbrand.ai/mcp

# OpenCode
npx -y @springbrand/cli@alpha connect opencode --url https://devconnector.springbrand.ai/mcp

# WorkBuddy
npx -y @springbrand/cli@alpha connect workbuddy-ai --url https://devconnector.springbrand.ai/mcp
```

If the current Host cannot be identified, ask the user which client is running
before executing a command. Do not guess from the first client detected on the
machine.

The CLI summary is the installation report. Report the selected client, auth
mode, MCP and Skill status, restart requirement, and failed phase. Do not run
capability discovery or a business operation as an installation check.

## Installation completion report

After the command completes, report the actual status without revealing credentials:

1. The configured MCP entry is named `springbrand-dev`.
2. The MCP URL is exactly `https://devconnector.springbrand.ai/mcp` and uses the selected client's native remote HTTP transport.
3. The client identity matches the development environment.
4. The configured MCP health check passes.
5. Existing configuration and every other client remain unchanged.

If any item is not true, report that item as failed and do not claim installation success.

Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

Do not run `auth login` for this flow. That command obtains an API key and is
not part of the default installation path.

## API-key fallback

Use this branch only when the user cannot complete OAuth, the client does not
support native OAuth, or the user explicitly asks for API-key authentication.
Show or open the development API-key page:

https://devrapp.springbrand.ai/account-settings?section=mcp-api-keys

Ask the user to register or sign in, create or copy a development API key, and
provide it through the secure input channel. Wait for the key, then rerun the
matching single-client command with `--api-key {{INSTALL_KEY}}`.

Do not print, log, repeat, or include the key in the report. If a supplied key
is malformed, rejected, expired, revoked, or for the wrong environment, report
the failure and ask the user to replace it; do not silently switch auth modes.

## Plugin fallback

Use [INSTALL.plugin.dev.md](./INSTALL.plugin.dev.md) only after the CLI cannot
run or a specific client registration fails. Preserve successful CLI
registrations and follow the plugin document for the failed client only.
