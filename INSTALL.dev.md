# SpringBrand development CLI installation protocol

## Development release identity

This guide installs immutable development release `v1.2.1-dev.2` from
`springbrand-dev` at `https://devconnector.springbrand.ai/mcp`.

## Installation overview

This document is the CLI-first entry point. Use this order for every install or
update:

1. **CLI with an API key.** If the setup prompt contains a development key,
   pass it to the CLI.
2. **CLI with OAuth for the current client.** If the setup prompt contains no
   key, ask which terminal/client the user is installing into, then run the
   single-client command for that client without `--api-key`. Native browser
   OAuth is scoped to that client and its local session; it is not a shared
   credential for every client.
3. **Plugin fallback.** Only when the CLI cannot run or a specific client fails,
   preserve successful CLI registrations and read
   [INSTALL.plugin.dev.md](./INSTALL.plugin.dev.md). Do not load Plugin
   installation context while the CLI path is still available.

The CLI's own summary is the installation report. Report each detected client,
auth mode, MCP and Skill status, restart requirement, and failed phase. Do not
run capability discovery or a business operation as an installation check.

## Preferred CLI installation

When a development API key is supplied, detect every supported client installed
on this machine, then run exactly one command:

```sh
npx -y @springbrand/cli@alpha connect --all --skip-launch --url https://devconnector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}
```

If there is **no API key**, do not run `connect --all`. First ask the user which
client is the current installation target, then read and follow that client's
single-client development guide:

- [Codex](./INSTALL.cli.dev.codex.md)
- [Claude Code](./INSTALL.cli.dev.claude-code.md)
- [Cursor](./INSTALL.cli.dev.cursor.md)
- [OpenCode](./INSTALL.cli.dev.opencode.md)
- [WorkBuddy](./INSTALL.cli.dev.workbuddy.md)

Those guides run exactly one `connect <client> --url ...` command, allowing the
selected client to trigger and store its own native browser OAuth session.
In this branch, do not run `sp auth login` and do not open the API-key page:
OAuth belongs to the selected client and is completed by that client's native
MCP flow.

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

Never print, store, or repeat the key. Do not run a second blind install
attempt. If the CLI requests a restart or new session, report that as the next
step and stop.

## Plugin fallback

Use [INSTALL.plugin.dev.md](./INSTALL.plugin.dev.md) only after the CLI failure
is known.
