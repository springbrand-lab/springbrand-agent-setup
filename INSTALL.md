# SpringBrand production CLI installation protocol

## Installation overview

This document is the CLI-first entry point. Use this order for every first
install or update:

1. Detect the supported clients installed on this machine.
2. Run the CLI without `--api-key` so each client uses its native OAuth flow.
3. If the browser asks the user to sign in, let the user sign in. If the user
   has no account, let the user register, then continue the same OAuth flow.
4. Wait for every OAuth flow to finish before reporting the result.
5. Use an API key only when OAuth is unavailable, unsupported, or explicitly
   requested by the user.

Run exactly one CLI command for the all-client installation:

```sh
npx -y @springbrand/cli@latest connect --all --skip-launch --url https://connector.springbrand.ai/mcp
```

The CLI summary is the installation report. Report each detected client, auth
mode, MCP and Skill status, restart requirement, and failed phase. Do not run
capability discovery or a business operation as an installation check.

## Installation completion report

After the command completes, report the actual status without revealing credentials:

1. The configured MCP entry is named `springbrand`.
2. The MCP URL is exactly `https://connector.springbrand.ai/mcp` and uses the client's native remote HTTP transport.
3. The client identity matches the production environment.
4. The configured MCP health check passes.
5. Existing configuration and every other client remain unchanged.

If any item is not true, report that item as failed and do not claim installation success.

Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

OAuth is client-local. Each detected client may open its own browser
authorization flow, and one client's OAuth session does not authorize the other
clients. Continue the installation after registration or sign-in redirects to
the client. If a client defers OAuth until first use, report that exact next
step instead of claiming that client is authenticated.

Do not run `auth login` for this flow. That command obtains an API key and is
not part of the default installation path.

## API-key fallback

Use this branch only when the user cannot complete OAuth, the client does not
support native OAuth, or the user explicitly asks for API-key authentication.
Show or open the API-key page:

https://rapp.springbrand.ai/account-settings?section=mcp-api-keys

Ask the user to register or sign in, create or copy an API key, and provide it
through the secure input channel. Wait for the key, then rerun:

```sh
npx -y @springbrand/cli@latest connect --all --skip-launch --url https://connector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

Do not print, log, repeat, or include the key in the report. If a supplied key
is malformed, rejected, expired, revoked, or for the wrong environment, report
the failure and ask the user to replace it; do not silently switch auth modes.

## Plugin fallback

Use [INSTALL.plugin.md](./INSTALL.plugin.md) only after the CLI cannot run or a
specific client registration fails. Preserve successful CLI registrations and
follow the plugin document for the failed client only.
