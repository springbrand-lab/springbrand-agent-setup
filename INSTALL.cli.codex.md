# SpringBrand production single-client installation for ChatGPT desktop app and Codex CLI

Before any command, read and follow [the production installation protocol](./INSTALL.md). This document is the client-specific variant for exactly one selected target: **Codex CLI** or **ChatGPT desktop app**. Determine whether this is a first installation or an update, and keep that classification for the whole conversation.

Configure only the target named in the user's Prompt. Do not detect, configure, update, or remove the other target or any unrelated client. Preserve every unrelated configuration and existing MCP entry.

CLI release: `@springbrand/cli@0.1.5-alpha.1`.

## Target selection

Select exactly one target before running a command:

- **Codex CLI**: use client ID `codex`.
- **ChatGPT desktop app** in Codex view, or ChatGPT desktop app Work Local targeting Codex Local: use client ID `codex`. The shared client ID does not expand the installation scope to Codex CLI; modify only the selected ChatGPT desktop app target.
- **ChatGPT desktop app** Work view targeting Work: do not run `connect codex`; use the Other Agent workflow below.

The current Agent surface and installation target are separate. Never infer the target from the shell, editor, or browser that happens to be active.

## Install workflow

Do not run `connect` without the selected client ID. Do not run `connect --all`, `auth login`, a business operation, or a second installation command. Do not switch clients or environments. An authentication-mode switch is allowed only when the user explicitly chooses the compatible OAuth fallback described below.

Before each external operation, confirm that the selected Host can write its local configuration, that the npm cache is writable, and that the npm registry and SpringBrand endpoint are reachable. If the current Agent is restricted, ask the user to switch to full-access or unrestricted execution before continuing. For a non-writable cache, use a user-owned temporary cache; do not change ownership of a home directory.

The normal entry point is the logged-in installation guide, whose Prompt includes an API key. Treat a supplied API key as the preferred authentication mode and run exactly one API-key command; do not start OAuth first. If the Prompt has no key, use native OAuth. Keep the key out of output, logs, and reports:

```sh
# No API key: start the selected Host's native OAuth flow.
npx -y @springbrand/cli@0.1.5-alpha.1 connect codex --url https://connector.springbrand.ai/mcp --json

# API key supplied: validate it without starting OAuth.
npx -y @springbrand/cli@0.1.5-alpha.1 connect codex --url https://connector.springbrand.ai/mcp --api-key {{INSTALL_KEY}} --json
```

When `{{INSTALL_KEY}}` is present, use the exact supplied value through the Host's secure credential flow; never print, log, repeat, or include it in a report. When it is absent, omit `--api-key` and use the native OAuth command.

Use the command result as the only control flow:

```text
IF result.outcome == "verified":
    GOTO VERIFY_RESULT

IF result.outcome == "auth_pending":
    GOTO OAUTH_ACTION

OTHERWISE:
    REPORT installation incomplete/failed, result.failed_phase,
           authentication/health status, and result.nextAction
    STOP without claiming success
```

If the key is invalid, expired, revoked, for the wrong environment, or lacks scope, stop and report only that stable failure category. Do not blind-retry with the same key. After reporting the failure, use the no-key OAuth command only if the user explicitly chooses OAuth; never fall back silently.

## OAuth and verification continuation

`OAUTH_ACTION`: read only `nextAction` or `next_action`, execute it exactly as written, and wait for it to finish. For Codex, let Codex open its native system browser and let the user complete authorization there. Never copy an OAuth URL into another browser and never use Browser, Computer Use, or Cua for OAuth.

If the action says that registration or login is required, ask the user to register or sign in to `https://rapp.springbrand.ai/`, wait for confirmation, and run the same OAuth action again. If it requires a reload or new session, report the exact action and wait for the user. Otherwise report the incomplete OAuth state and its `nextAction`.

After OAuth succeeds, immediately run the same package's one continuation; do not end the task or report authentication success between these steps:

```sh
npx -y @springbrand/cli@0.1.5-alpha.1 doctor --harness codex --url https://connector.springbrand.ai/mcp --json --wait-for-auth
```

For an API-key installation, run the same command without `--wait-for-auth` exactly once. The continuation is the only continuation command. An OAuth wait may poll up to 300 seconds at 3-second intervals. If it times out, report incomplete authentication, ask the user to register or sign in, then repeat the same OAuth action and one doctor continuation only after confirmation.

Report success only when `verified` came from `connect`, or `ready: true` came from the one doctor continuation. A successful continuation must also return `hosts[].restart_required.required: true` with a restart/new-session action; `code: "not_required"` is invalid. Treat `auth_pending`, `needs_reload`, failed checks, unsupported targets, and missing precondition status as incomplete. Report the observed `outcome`, `failed_phase`, authentication/health status, relevant preconditions as `met`, `unmet`, `pending`, or `not verified`, and the exact `nextAction` when present. Do not infer that approval mode caused an MCP authorization failure.

## Completion report

Report only verified facts:

- Entry: `springbrand`.
- URL: `https://connector.springbrand.ai/mcp`; native Streamable HTTP transport.
- Production identity, authentication, and configured MCP health: verified.
- Existing configuration and unrelated clients: unchanged.
- The selected Host must be restarted and opened in a new conversation; ask the user to complete that action before claiming installation success.

Do not claim a Skill or business operation was verified unless the result says so. Close the report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

## Other Agent workflow

Use this section only for ChatGPT desktop app Work view targeting Work, or when the current Agent cannot run the local CLI. This is a separate remote/plugin branch, not a continuation of `connect`/`doctor`.

For ChatGPT desktop app Work view, do not run `sp connect` or `connect codex`; those commands configure Codex Local, not Work. Install the SpringBrand Plugin from the desktop Plugins tab and connect its remote MCP server when prompted. Verify the actual Work-visible Plugin identity, production MCP URL, authentication, and health status. If the Host cannot configure this safely, report the limitation and stop without changing configuration.
