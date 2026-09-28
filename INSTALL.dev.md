# SpringBrand development CLI installation protocol

## Development release identity

This guide installs immutable development release `v1.2.1-dev.2` from
`springbrand-dev` at `https://devconnector.springbrand.ai/mcp`.

## Installation overview

This document is the CLI-first entry point. Use this order for every install or
update:

1. **CLI with an API key (preferred).** If the setup prompt contains a
   development key, pass it to the CLI. If it does not, do not run the CLI
   yet. Show or open the development API-key page at
   `https://devrapp.springbrand.ai/account-settings?section=mcp-api-keys`, ask
   the user to register or sign in and create or copy a development API key,
   then wait for the user to provide the key before continuing.
2. **CLI with OAuth as an explicit fallback.** Only when the user cannot use an
   API key, or the user explicitly chooses OAuth after an API-key attempt has
   failed, ask which terminal/client is being installed and run that client's
   single-client command without `--api-key`. Native browser OAuth is scoped to
   that client and its local session; it is not a shared credential for every
   client.
3. **Plugin fallback.** Only when the CLI cannot run or a specific client fails,
   preserve successful CLI registrations and read
   [INSTALL.plugin.dev.md](./INSTALL.plugin.dev.md). Do not load Plugin
   installation context while the CLI path is still available.

The CLI's own summary is the installation report. Report each detected client,
auth mode, MCP and Skill status, restart requirement, and failed phase. Do not
run capability discovery or a business operation as an installation check.

## Installation completion report

After the command completes, report the actual status without revealing credentials:

1. The configured MCP entry is named `springbrand-dev`.
2. The MCP URL is exactly `https://devconnector.springbrand.ai/mcp` and uses the client's native remote HTTP transport.
3. The client identity matches the development environment.
4. The configured MCP health check passes.
5. Existing configuration and every other client remain unchanged.

If any item is not true, report that item as failed and do not claim installation success.

Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

## Preferred CLI installation

When a development API key is supplied, detect every supported client installed
on this machine, then run exactly one command:

```sh
npx -y @springbrand/cli@alpha connect --all --skip-launch --url https://devconnector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

If there is **no API key in the setup prompt**, do not run `connect --all` and
do not run `auth login`. Show or open
`https://devrapp.springbrand.ai/account-settings?section=mcp-api-keys`. Ask the
user to register or sign in, create or copy the development key, and provide it
through the secure input channel. Wait for the key. Only after the key is
provided, run the API-key command above with `--api-key {{INSTALL_KEY}}`. Do
not print, log, repeat, or include the key in the report.

Only if the user cannot use an API key, or explicitly chooses OAuth after the
key attempt fails, ask which client is the current installation target and read
that client's single-client development guide:

- [Codex](./INSTALL.cli.dev.codex.md)
- [Claude Code](./INSTALL.cli.dev.claude-code.md)
- [Cursor](./INSTALL.cli.dev.cursor.md)
- [OpenCode](./INSTALL.cli.dev.opencode.md)
- [WorkBuddy](./INSTALL.cli.dev.workbuddy.md)

Those guides run exactly one `connect <client> --url ...` command, allowing the
selected client to trigger and store its own native browser OAuth session. Do
not enter this branch merely because the setup prompt omitted a key; offer the
development API-key page first.

The CLI then uses native browser OAuth for that client. OAuth credentials are
stored by the client/session and do not authorize the other clients. If the
user wants one installation to cover every client, they need a development API
key from [SpringBrand development account settings](https://devrapp.springbrand.ai/account-settings?section=mcp-api-keys)
and must rerun the API-key branch. The no-key condition includes the CLI's
ambient sources: `SPRINGBRAND_API_KEY` and `~/.springbrand/config.json`. If
either contains an old key, clear the saved key with `sp auth logout` and unset
the current shell variable before using the OAuth branch; otherwise the CLI
correctly remains in API-key mode.

If a supplied key is malformed, rejected, expired, revoked, or for the wrong
environment, the CLI blocks before writing client configuration. Replace the
key and rerun; do not silently switch that failed key attempt to OAuth. A
key-only client may be reported as failed when no key is supplied; handle only
that client through the fallback document.

The Agent must never print, log, or repeat the key. Do not treat the missing-key
pause as an installation failure. Do not run a second blind install attempt. If
the CLI requests a restart or new session, report that as the next step and
stop.

## Plugin fallback

Use [INSTALL.plugin.dev.md](./INSTALL.plugin.dev.md) only after the CLI failure
is known.
