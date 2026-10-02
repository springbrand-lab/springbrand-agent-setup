# SpringBrand production CLI installation protocol

CLI channel: `@springbrand/cli@latest`.

## Installation preconditions

Before starting installation, the user must be registered or signed in to the
production RApp at `https://rapp.springbrand.ai/`. New users must register;
existing users must log in. This account precondition is separate from Agent
approval and Host-native OAuth. If installation fails or remains pending,
report this precondition as `met`, `unmet`, `pending`, or `not verified` based
only on observed output; do not guess that approval mode caused the failure.

## Install workflow

1. Select exactly one Host and its CLI client. The selected client is the only
   client in scope for this run:

- Codex CLI: `codex`
- ChatGPT desktop app — Codex view: `codex`
- ChatGPT desktop app — Work Local; target Codex Local: `codex`
- ChatGPT desktop app — Work view; target Work: use the Other Agent workflow below.
- Claude Code or Claude Desktop Code tab: `claude-code`
- WorkBuddy: `workbuddy-ai`
- Cursor: `cursor`
- OpenCode: `opencode`
- Pi: `pi`
   - Any other Agent: use the Other Agent workflow below.

The current Agent surface and the installation target are separate. If the
current surface is Work Local and the target is Codex Local, select `codex` and
continue this numbered CLI workflow. If the target is Work itself, do not enter
the numbered CLI workflow; use the Other Agent workflow below.

2. Set `auth_mode` from the user's Prompt and select exactly one command:

```sh
# No API key: the CLI starts the selected Host's native OAuth flow.
npx -y @springbrand/cli@latest connect <client> --url https://connector.springbrand.ai/mcp --json

# API key supplied: the CLI validates this key and does not start OAuth.
npx -y @springbrand/cli@latest connect <client> --url https://connector.springbrand.ai/mcp --api-key <key> --json
```

   Keep the key out of commands, output, logs and reports.

3. Re-check the required capabilities, then run exactly one selected command.
   Use this control flow as the normative procedure:

   ```text
   result = RUN selected_connect_command()

   IF result.outcome == "verified":
       GOTO VERIFY_RESULT

   IF result.outcome == "auth_pending":
       GOTO OAUTH_ACTION

   OTHERWISE:
       REPORT result.failed_phase and result.nextAction
       STOP without claiming success
   ```

   Do not run another installation command or switch clients, environments, or
   authentication modes.

4. `OAUTH_ACTION`: read only `nextAction` (or `next_action`), execute it exactly
   as written, and wait for the process to finish. A pending OAuth result
   supplies the Host-specific browser action. A reload result supplies the
   exact restart/new-session action. Do not invent a login command.

   ```text
   IF exit_code == 0 AND output indicates OAuth success:
       GOTO AUTH_CONTINUATION

   IF action indicates registration_or_login_required:
       ASK user to register or log in
       WAIT for user confirmation
       RUN the same OAuth action again
       GOTO AUTH_CONTINUATION

   IF action indicates reload_required:
       REPORT the exact reload/new-session action
       WAIT for the user to complete it
       STOP

   OTHERWISE:
       REPORT the incomplete OAuth state and nextAction
       STOP
   ```

   A successful OAuth action is not a completion signal. Do not ask for a
   second confirmation, report authentication as pending, or end the task
   before entering `AUTH_CONTINUATION`.

5. `AUTH_CONTINUATION`: continue according to `auth_mode`. After OAuth
   completion, wait for Host registration with the same CLI channel. The wait
   defaults to 5 minutes with a 3-second polling interval and applies only to
   OAuth:

```sh
sp doctor --harness <client> --json --wait-for-auth
```

   ```text
   IF auth_mode == "oauth":
       RUN doctor --wait-for-auth exactly once
       WAIT up to 300 seconds
       POLL every 3 seconds

   IF auth_mode == "api-key":
       RUN doctor without --wait-for-auth exactly once

   IF OAuth wait times out:
       REPORT incomplete authentication
       ASK user to register or log in
       WAIT for confirmation
       RUN the same OAuth action
       RUN doctor --wait-for-auth exactly once
   ```

   The doctor command is the only continuation. Do not run a second doctor
   command after it succeeds.

6. `VERIFY_RESULT`: report installation state only when `verified` came from
   `connect`, or `ready: true` came from the one doctor continuation. The
   continuation must also return `hosts[].restart_required.required: true` with
   a restart/new-session action; `code: "not_required"` is invalid. Treat
   `auth_pending`, `needs_reload`, failed checks, and `unsupported` as
   incomplete: report the phase and nextAction, then stop without claiming
   success.

7. After `VERIFY_RESULT` reports `ready: true`, report only the verified facts
   below. Ask the user to restart the Host and open a new conversation, then
   wait for confirmation before claiming installation success.

## Completion report

Report only verified facts:

- Entry: `springbrand`.
- URL: `https://connector.springbrand.ai/mcp`; native Streamable HTTP transport.
- Production identity, authentication and configured MCP health: verified.
- Existing configuration and unrelated clients: unchanged.
- Host restart and a new session: required after this report; ask the user to
  complete both and wait for confirmation before claiming installation success.

Do not claim a Skill or business operation was verified unless the result says
so. Then ask the user what they would like to build first.

## Other Agent workflow

Use this section only when the installation target is ChatGPT Work or the
current Agent cannot run the local CLI. This is a separate remote/plugin branch,
not a continuation of the numbered `connect`/`doctor` workflow.

For ChatGPT desktop Work view as the installation target, do not run `sp connect`
or `connect codex`; those commands configure Codex Local, not Work. Install the
SpringBrand Plugin from the desktop Plugins tab and connect its remote MCP
server when prompted. Verify the actual Work-visible Plugin identity, MCP URL,
authentication, and health status.

If the current surface exposes only direct remote MCP configuration, configure
the fixed URL above and use either native MCP OAuth or the user-provided API
key. Follow the remote/plugin result rules; if the Host cannot configure this
safely, report the limitation and stop without changing configuration.
