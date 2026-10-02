# SpringBrand development CLI installation protocol

CLI channel: `@springbrand/cli@alpha`.
Development release identity: `v1.2.1-dev.2`; entry `springbrand-dev`, endpoint
`https://devconnector.springbrand.ai/mcp`.

## Required environment authorization

This installation changes the selected Host's local MCP, Plugin, and Skill
configuration and requires outbound network access.

Authorization is required separately for each installation stage. Approval for
one stage is not proof that a later stage has the required access.

Before each external operation, check the capabilities required by that stage:

- access to the local user configuration directories used by the selected Host;
- writing the selected Host's MCP configuration and SpringBrand Plugin/Skill files;
- outbound network access to the npm registry and the SpringBrand endpoint;
- executing `npx` and the selected Host integration or CLI;
- a writable npm cache owned by the current user.

Treat the execution mode as an installation precondition. Before installation
begins, choose one mode and use it for every operation:

1. Switch the session to full access, re-check the mode, then execute the
   planned commands directly.
2. Keep the sandbox, and run every command through Codex's approval-aware
   execution path with `ask approval` enabled. Codex asks for permission before
   a protected filesystem write, package download, or network call; the command
   must not start until that approval is granted.

Before each command, inspect the selected mode and classify the command's
required capabilities. Do not replace the sandbox executor's approval prompt
with an Agent-authored question, and do not run a command first and ask about a
permission failure afterward. A permission grant does not guarantee that the
operating system will allow the requested write.

For the `npx` stage, inspect the configured cache before running the command:

```sh
npm_cache="$(npm config get cache)"
test -d "$npm_cache" && test -w "$npm_cache"
```

If the configured cache is unavailable or not writable, use a new cache owned
by the current user for this installation instead of changing ownership of a
whole home directory:

```sh
export NPM_CONFIG_CACHE="$(mktemp -d /tmp/springbrand-npm-cache.XXXXXX)"
```

After each operation, read its result before beginning the next operation.

If the user cannot grant the required access, report that installation is
blocked and stop without claiming success.

## Install workflow

Do not infer a client.
Do not run `connect` without a client.
Do not run `connect --all`.
Do not retry with another client.
Do not open an OAuth URL yourself.
Do not use browser, Computer Use, or Cua automation for OAuth.
Do not start a parallel or duplicate OAuth session. Re-run the same OAuth
action only after the previous action has exited and the user confirms that
registration or login is complete.
Do not run `auth login`.
Do not invent a login command.
Do not read another installation guide.
Do not run a business operation as an installation check.

0. Follow the selected execution mode above. Before every operation, re-check
   the capabilities required by that operation and use the corresponding
   executor path. The operation must not start until any required Codex approval
   has been granted.

1. Identify exactly one supported Host integration and select its client ID.
   The selected client is the only client in scope for this run:

   - Codex CLI: `codex`
   - ChatGPT desktop app — Codex view: `codex`

2. Set `auth_mode` from the user's Prompt and select exactly one command.
   Never print, log, repeat, or include the key in a report.

   ```sh
   # No key: the CLI starts the selected Host's native OAuth flow.
   npx -y @springbrand/cli@alpha connect <client> --url https://devconnector.springbrand.ai/mcp --json

   # Key supplied: the CLI validates this key and does not start OAuth.
   npx -y @springbrand/cli@alpha connect <client> --url https://devconnector.springbrand.ai/mcp --api-key <key> --json
   ```

   `npx` executes the latest package published under the `alpha` channel for
   this run.

3. Re-check the network, npm cache, and Host capabilities, then run exactly one
   selected command. Use this control flow as the normative procedure:

   ```text
   result = RUN selected_connect_command()

   IF result.outcome == "verified":
       IF auth_mode == "api-key":
           GOTO AUTH_CONTINUATION
       GOTO VERIFY_RESULT

   IF result.outcome == "auth_pending":
       IF auth_mode == "api-key":
           GOTO API_KEY_VALIDATION_FAILURE
       GOTO OAUTH_ACTION

   IF result.outcome == "needs_reload":
       IF result.auth.status == "verified" AND result.health.status == "verified":
           NEXT TOOL CALL MUST be the API-key doctor continuation below.
           Do not execute result.nextAction, pause for restart, or send a
           user-facing final response before that doctor call returns.
           GOTO AUTH_CONTINUATION
       IF auth_mode == "api-key":
           GOTO API_KEY_VALIDATION_FAILURE
       REPORT result.failed_phase and result.nextAction
       STOP without claiming success

   IF result.error.code == "invalid_config" OR result.failed_phase IN
      {"host_configuration", "cli_install", "skill_install"}:
       REPORT that installation is blocked by Host/configuration permissions,
       include the exact blocked capability and nextAction when present, and
       stop. Resume only after the selected execution mode provides the
       capability and the same command can be run through its required executor
       path. Do not have the Agent ask for approval in prose.
       STOP without asking for a different API key or switching auth modes.

   OTHERWISE:
       IF auth_mode == "api-key":
           GOTO API_KEY_VALIDATION_FAILURE
       REPORT result.failed_phase and result.nextAction
       STOP without claiming success
   ```

   For an API-key install, `verified` from `connect` means the key was written;
   it still requires the one API-key continuation below to verify the persisted
   credential and MCP health. Do not start OAuth automatically.

   If API-key validation fails, report that the entered API key is incorrect or
   not accepted, without exposing it. Ask the user to confirm or re-enter the
   key and then continue with the same API-key install, or explicitly choose
   OAuth and continue with the OAuth branch. Wait for that choice before
   running another command.

   Do not switch clients or environments, and do not retry an API key without
   the user's confirmation.

4. `OAUTH_ACTION`: read only `nextAction` (or `next_action`), re-check its
   required capabilities, execute it exactly as written, and wait for the
   process to finish. For Codex, let Codex open its native system browser and
   let the user complete authorization there. Never copy the printed URL into
   another browser or use Computer Use/Cua for OAuth.

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

5. `AUTH_CONTINUATION`: choose the continuation by `auth_mode`. This step is
   mandatory after a successful OAuth action, after an API-key `connect` returns
   `verified`, and after a `needs_reload` result whose authentication and health
   statuses are both `verified`. For the latter case, the doctor call must be
   the next tool call; the connect result's restart `nextAction` is deferred
   until doctor reports `restart_required`.

   - For OAuth, immediately after the action succeeds, run the following command
     in the same turn. It waits up to 5 minutes and checks every 3 seconds:

     ```sh
     npx -y @springbrand/cli@alpha doctor --harness <client> --url https://devconnector.springbrand.ai/mcp --json --wait-for-auth
     ```

   - For an API-key install, run the same command without `--wait-for-auth`.
     This is the post-write validation and must run exactly once; do not
     execute an OAuth action or wait:

     ```sh
     npx -y @springbrand/cli@alpha doctor --harness <client> --url https://devconnector.springbrand.ai/mcp --json
     ```

   ```text
   IF auth_mode == "oauth":
       RUN doctor --wait-for-auth exactly once
       WAIT up to 300 seconds
       POLL every 3 seconds

   IF auth_mode == "api-key":
       RUN doctor without --wait-for-auth exactly once

   IF API-key doctor validation fails:
       GOTO API_KEY_VALIDATION_FAILURE

   IF OAuth wait times out:
       REPORT incomplete authentication
       ASK user to register or log in
       WAIT for confirmation
       RUN the same OAuth action
       RUN doctor --wait-for-auth exactly once
   ```

   The doctor command is the only continuation. Do not run a second doctor
   command after it succeeds.
   If `connect` was run through `npx`, use the same
   `@springbrand/cli@alpha` package for doctor instead of an older global `sp`.

   `API_KEY_VALIDATION_FAILURE` applies only when the CLI explicitly reports
   rejected, invalid, expired, revoked, or otherwise unaccepted API-key
   authentication. Report the observed `outcome`, `failed_phase`, auth/health
   status, and exact `nextAction` without exposing the key. Ask the user to
   confirm/re-enter the key or explicitly choose OAuth, and wait before running
   another command. Configuration, permission, CLI-install, and Skill-install
   errors must use the environment-blocked path above instead.

   6. `FINAL_STATUS_REPORT`: immediately produce one structured status report
   after the doctor continuation; do not end with only a prose restart prompt.

   - If `ready: true`, output the completion report below and ask what the user
     would like to build first.
   - If `ready: false` and the checks show authentication, MCP health, identity,
     and configuration are verified while
     `hosts[].restart_required.required: true`, output a pending report stating
     that installation is configured, list the exact restart/reload and new
     session action, and ask the user to confirm when it is complete. Do not
     claim final installation success. After confirmation, run doctor again and
     return to this same status-report step; only `ready: true` may produce the
     completion report.
   - For `auth_pending`, failed checks, unsupported targets, or unverified
     credentials, output the incomplete/failed status, exact `nextAction`, and
     required user action. Do not output the completion report.

## Completion report

Report only verified facts:

- Entry: `springbrand-dev`.
- URL: `https://devconnector.springbrand.ai/mcp`; native Streamable HTTP transport.
- Development identity, authentication and configured MCP health: verified.
- Existing configuration and unrelated clients: unchanged.
- Host restart/reload and a new session: completed before this completion report.

Do not claim a Skill or business operation was verified unless the result says
so. Then ask the user what they would like to build first.
Close the report with a one-sentence capability note: SpringBrand Dev gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

## Other Agent workflow

This section applies only to ChatGPT desktop Work view. Do not run `sp connect`
or `connect codex`; those commands configure Codex Local, not Work. Install the
SpringBrand Dev Plugin from the desktop Plugins tab and connect its remote MCP
server when prompted. Verify the actual Work-visible Plugin identity, MCP URL,
authentication, and health status.

Use either native MCP OAuth or the user-provided development API key. If the
API-key validation fails, tell the user the entered key is incorrect or not
accepted, then wait for the user to confirm a corrected key or choose OAuth.
Do not use Browser, Computer Use, or Cua to simulate a configuration UI or OAuth
consent. Report the actual MCP, authentication, identity, and health status;
do not claim a Skill or business operation was verified unless the result says
so.
