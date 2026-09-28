# SpringBrand production CLI installation protocol

## Installation overview

This document is the CLI-first entry point. Use this order for every install or
update:

1. **CLI with an API key (preferred).** If the setup prompt contains an
   installation key, pass it to the CLI. If it does not, run
   `npx -y @springbrand/cli@latest auth login --url https://connector.springbrand.ai/mcp`.
   Ask the user to register or sign in, create or copy an API key from the page,
   and paste it into the CLI before continuing.
2. **CLI with OAuth as an explicit fallback.** Only when the user cannot use an
   API key, or the user explicitly chooses OAuth after an API-key attempt has
   failed, ask which terminal/client is being installed and run that client's
   single-client command without `--api-key`. Native browser OAuth is scoped to
   that client and its local session; it is not a shared credential for every
   client.
3. **Plugin fallback.** Only when the CLI cannot run or a specific client fails,
   preserve successful CLI registrations and read
   [INSTALL.plugin.md](./INSTALL.plugin.md). Do not load Plugin installation
   context while the CLI path is still available.

The CLI's own summary is the installation report. Report each detected client,
auth mode, MCP and Skill status, restart requirement, and failed phase. Do not
run capability discovery or a business operation as an installation check.

## Preferred CLI installation

When an API key is supplied, detect every supported client installed on this
machine, then run exactly one command:

```sh
npx -y @springbrand/cli@latest connect --all --skip-launch --url https://connector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

If there is **no API key in the setup prompt**, run this command first:

```sh
npx -y @springbrand/cli@latest auth login --url https://connector.springbrand.ai/mcp
```

Ask the user to register or sign in, create or copy the key, and paste it into
the CLI. After `auth login` succeeds, run the API-key command above with the
runtime key supplied to `--api-key`, or omit `--api-key` so the CLI reads the
saved key. Do not print, log, repeat, or include the key in the report. The CLI
may save the key in its own credential file as part of `auth login`.

Only if the user cannot use an API key, or explicitly chooses OAuth after the
key attempt fails, ask which client is the current installation target and read
that client's single-client guide:

- [Codex](./INSTALL.cli.codex.md)
- [Claude Code](./INSTALL.cli.claude-code.md)
- [Cursor](./INSTALL.cli.cursor.md)
- [OpenCode](./INSTALL.cli.opencode.md)
- [WorkBuddy](./INSTALL.cli.workbuddy.md)

Those guides run exactly one `connect <client> --url ...` command, allowing the
selected client to trigger and store its own native browser OAuth session. Do
not enter this branch merely because the setup prompt omitted a key; offer the
API-key page first.

The CLI then uses native browser OAuth for that client. OAuth credentials are
stored by the client/session and do not authorize the other clients. If the
user wants one installation to cover every client, direct them to create an
API key at [SpringBrand account settings](https://rapp.springbrand.ai/account-settings?section=mcp-api-keys)
and rerun the API-key branch. The no-key condition includes the CLI's ambient
sources: `SPRINGBRAND_API_KEY` and `~/.springbrand/config.json`. If either
contains an old key, clear the saved key with `sp auth logout` and unset the
current shell variable before using the OAuth branch; otherwise the CLI
correctly remains in API-key mode.

If a supplied key is malformed, rejected, expired, revoked, or for the wrong
environment, the CLI blocks before writing client configuration. Replace the
key and rerun; do not silently switch that failed key attempt to OAuth. A
key-only client may be reported as failed when no key is supplied; handle only
that client through the fallback document.

The Agent must never print, log, or repeat the key. Do not run a second blind
install attempt. If the CLI requests a restart or new session, report that as
the next step and stop.

## Plugin fallback

Use [INSTALL.plugin.md](./INSTALL.plugin.md) only after the CLI failure is known.
