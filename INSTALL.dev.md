# SpringBrand development CLI installation protocol

CLI channel: `@springbrand/cli@alpha`.
Development release identity: `v1.2.1-dev.2`; entry `springbrand-dev`, endpoint
`https://devconnector.springbrand.ai/mcp`.

## Initial installation response

First inspect the current execution mode and whether commands can reach the
user's local machine. If the session is already in the Host's unrestricted mode
(for example **Full access**) and is not sandbox-isolated, continue directly
with the installation workflow below. Do not show the permission explanation
or ask the user to choose a mode again. Always show the key-storage disclosure
below before a keyed install; Full access does not skip it.

If the session is restricted, sandbox-isolated, or the first installation probe
is blocked, this is a mandatory user-choice gate. Stop before running any
installation probe, package command, connect command, or retry. First show the
user the following two options and the complete installation summary, then wait
for the user's choice:

SpringBrand CLI installs on the user's local machine. The user can choose one
of two options:

1. Run the exact commands in the user's local terminal and report each result.
2. Switch to **Full access** so the Agent can continue the installation.

The summary of installation will do the following:

- install `@springbrand/cli@alpha` globally through the npm registry and use a
  user-owned npm cache;
- write only the selected Host's MCP, Plugin, and Skill configuration (for
  example under `~/.codex`, `~/.agents/plugins`, or the Host's own config
  directory);
- when API-key authentication is selected, store the key in plaintext in
  `~/.springbrand/config.json`, the selected client's MCP configuration, and a
  managed `SPRINGBRAND_DEV_API_KEY` block in the user's shell profile; the user
  can remove it with `sp auth logout --env dev`;
- execute `npm`, `sp`, and the selected Host integration or CLI;
- connect to the SpringBrand MCP server at
  `https://devconnector.springbrand.ai/mcp`;
- authenticate the MCP connection with an API key or browser-based OAuth.

The CLI prints these storage locations after `connect`. Relay them to the user
without the key value.

Do not present installation commands, ask for command output, run a probe, or
continue to the install workflow until the user chooses one of these options.
If the user chooses local execution, provide the exact command only after that
choice and wait for the result. If the user chooses Full access, wait for the
mode change and then re-check that the session is unrestricted before
continuing.

MCP connection and account authentication are separate from the local file
changes, and require the user's development account plus either an API key or
native OAuth.

In restricted mode, report each requested operation using this summary before
running it. If the user chooses to stay restricted, provide the exact command
for the user to run locally and wait for its result before continuing. If the
user denies a required write, package installation, command execution, or
network request, report that exact blocked capability and stop; offer Full
access as the faster recovery path.

## Installation preconditions

The following are installation preconditions. They are not optional hints, and
approval for the Agent session does not prove that every precondition is met:

- the selected Host can read and write its local MCP and Plugin/Skill
  configuration, or, for the Other Agent workflow, exposes remote MCP
  connector settings the user or Agent can configure;
- the npm cache and global installation location are writable by the current user;
- the npm registry and `https://devconnector.springbrand.ai/mcp` are reachable;
- the selected Host integration or CLI can execute;

## Execution boundary rule

This rule applies to every command and interactive action in the installation
workflow, including `npm install`, `sp --version`, `sp connect`, OAuth login,
and `doctor`.

If the Agent cannot execute an action because its sandbox or restricted
execution environment cannot reach the user's machine, npm cache, global
installation location, Host configuration, network, browser callback, or
secret, stop retrying in that environment. Report the blocked capability and
give the user the exact command or action to perform on their own machine. Wait
for the user to report the result before continuing. Do not replace the action
with a manual MCP edit, another client, another cache, or another auth command.

For an error confirmed to come from the user's machine, follow the returned
recovery action. Do not label an ordinary command error as a sandbox block
without evidence; do not suggest changing cache ownership or using another
cache unless the error is confirmed to be a real local permission problem.

Account and authentication requirements are handled from step 3 onward; they
are not prerequisites for installing the CLI in step 2.

Changing the Agent's approval mode only changes what the Agent may attempt.
It does not move execution onto the user's machine, complete OAuth, log the
development account in, or make an unauthorized MCP session authorized.

## Recovery paths

Use these paths in order when the preferred CLI workflow cannot complete. Keep
the selected Host and development environment unchanged, and do not create a
second `springbrand-dev` entry.

1. **Downgrade to the native Plugin flow.** If the CLI cannot run, cannot reach
   the user's machine, or reports a client installation failure, use the
   [Codex Desktop manual Plugin installation guide](https://devsite.springbrand.ai/developers/docs/connect/codex-desktop#manual-plugin-install)
   for ChatGPT Desktop (Codex). For Cursor, use the
   [Cursor manual MCP installation guide](https://springbrand.ai/developers/docs/connect/cursor-desktop#manual-mcp-install).
   For WorkBuddy, use the
   [WorkBuddy manual MCP installation guide](https://springbrand.ai/developers/docs/connect/workbuddy-desktop#manual-mcp-install).
   For another supported Host, use its matching native Plugin fallback
   instructions. Install only the failed client and complete that Host's native
   OAuth and verification.
   Do not report success from a manually edited MCP entry.
2. **Support fallback.** If the native Plugin path or its OAuth/verification
   still fails, stop making configuration changes and contact
   [SpringBrand Support](https://devsite.springbrand.ai/contact) or email
   [`contact@springbrand.ai`](mailto:contact@springbrand.ai).

For an Other Agent (generic) target the Plugin flow does not apply: when its
CLI workflow cannot complete, use the direct-connect recovery at the end of
the Other Agent workflow.

## CLI result

`connect --json` and `doctor --json` return installation report schema version 2:

| Field | Meaning |
| --- | --- |
| `schema_version` | Report format version: `2`. |
| `status` | `ready`: CLI installation checks passed; `pending`: an action or verification remains; `failed`: an explicit error occurred. |
| `message` | A short explanation for the Agent; do not match this text to decide the workflow. |
| `steps.cli` | Whether the CLI can run. |
| `steps.mcp` | MCP configuration, authentication and connection readiness. |
| `next_action` | One action with `actor` (`agent` or `user`) and `instruction`; `null` when ready. |
| `error_code` | Optional stable failure code. |
| `diagnostics` | Additional evidence included only with `--verbose`. |

Use `status`, `error_code` and `next_action` to interpret the result. Pending
is not failure. When reporting a blocker, include the observed status, concise
reason and returned next action without exposing credentials. Do not require
legacy fields such as `outcome`, `failed_phase`, `ready` or `nextAction` in the
default report.

Do not infer a cause that the result does not establish. If the CLI does not
return a precondition status, say that the relevant precondition is **not
verified** and ask the user to check or complete it. In particular, an
unauthorized MCP response must be reported as an unmet or pending OAuth/API-key
precondition; do not describe it as an approval-mode block unless the command
explicitly reports an approval denial.

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
Do not read another installation guide during the preferred CLI workflow.
Do not run a business operation as an installation check.
Follow **Recovery paths** when that workflow cannot complete.

0. Apply the mode check in **Initial installation response**: if already
   unrestricted, continue; otherwise show the summary, then use the Host's
   per-command approval flow and stop when a required operation is denied.

1. Identify exactly one supported Host integration and select its client ID.
   The selected client is the only client in scope for this run:

   - Codex CLI: `codex`
   - ChatGPT desktop app — Codex view: `codex`
   - ChatGPT desktop app — Work Local; target Codex Local: `codex`
   - ChatGPT desktop app — Work view; target Work: use the Other Agent workflow below.
   - Claude Code or Claude Desktop Code tab: `claude-code`
   - WorkBuddy: `workbuddy-ai`
   - Cursor: `cursor`
   - OpenCode: `opencode`
   - Pi: `pi`
   - Devin Desktop or Devin CLI: `devin`
   - Any other Agent: use the Other Agent workflow below.

   The current Agent surface and the installation target are separate. If the
   current surface is Work Local and the target is Codex Local, select `codex`
   and continue this numbered CLI workflow. If the target is Work itself, do not
   enter the numbered CLI workflow; use the Other Agent workflow below.

2. Confirm where commands run, then install the alpha CLI. Every command in
   this workflow must run on the user's own machine — never in a sandbox,
   remote shell, or CI job. When the Agent's own command execution is on that
   machine, it runs `npm`, `sp connect`, and `doctor` itself; otherwise it
   presents each command for the user to run locally and works from the
   reported output. The OAuth login command in step 3.3 always runs in the
   user's own local interactive terminal.

   Execute these commands separately and check each result before continuing:

   ```sh
   npm install -g @springbrand/cli@alpha
   sp --version
   ```

   Continue only after npm succeeds and the output of `sp --version` contains
   `@springbrand/cli` and an alpha version. If it does not, another `sp` may be
   earlier on PATH; stop and report the observed output.

3. Connect SpringBrand to the selected client.

   `sp connect <client>` is the required installation step. It is the only
   supported path that installs the selected Host's SpringBrand Plugin/Skill,
   writes the MCP registration, and completes the selected authentication.

   If the Agent cannot execute `sp connect`, apply the Execution boundary rule
   above. Do not bypass the connect step or report installation success from a
   manually created MCP entry.

   ### 3.1 Select authentication and run connect

   Choose one authentication path and run `sp connect` exactly once:

   - **API key:** when the user supplied a development API key, pass it to the
     supported CLI flag:

     ```sh
     sp connect <client> --url https://devconnector.springbrand.ai/mcp --api-key <key> --json
     ```

     Do not print the key or include it in the installation report. If the
     execution environment cannot safely substitute the key into this command,
     have the user run the same command in their local terminal.
   - **OAuth:** when no API key is supplied, run:

     ```sh
     sp connect <client> --url https://devconnector.springbrand.ai/mcp --json
     ```

     A development SpringBrand account is required; users without one can
     register at `https://devrapp.springbrand.ai/`.

   With an API key, the CLI verifies it before writing configuration. After a
   successful verification it persists a managed `SPRINGBRAND_DEV_API_KEY` block
   in the user's shell profile and saves the key in
   `~/.springbrand/config.json` with owner-only permissions. The
   CLI also keeps the key in the current process environment. Never include
   the key in a report. If verification fails, follow the returned recovery
   action and do not treat the installation as complete.

   ### 3.2 Read the connection result

   Run the selected command once. Read its JSON report and handle `status`:

   - `ready`: CLI checks passed. Continue to the completion report in section 3.5.
   - `pending`: follow `next_action.instruction`, except for session-only
     verification after configuration and authentication are confirmed below.
     If `next_action.actor` is `agent`, continue in the same turn; if it is
     `user`, present the action and wait for completion.
   - `failed`: report the concise reason and `error_code`, if present, then
     follow the returned recovery action. Ask for user input only when that
     action requires it.

   Exit code `4` means pending, not failure; read the JSON even when the
   command exits nonzero. Do not repeat connect merely because it is pending.

   ### 3.3 Run OAuth and wait for authorization

   When the result returns a native OAuth action, show the exact returned
   command to the user; they run it once in their own local interactive
   terminal, where it opens the browser and receives the OAuth callback on
   localhost. Wait for the user to finish, then continue with the returned
   verification command.

   Exit code `0` with `Successfully logged in` confirms OAuth authorization.
   If the command cannot discover OAuth metadata, open the browser, or
   receive its localhost callback, the execution environment is wrong; ask
   the user to rerun the same command in their local interactive terminal.

   ### 3.4 Automatically run doctor after OAuth succeeds

   On OAuth success, immediately run the returned `continuation` once. If an
   older CLI omits it, use:

   ```sh
   sp doctor --harness <client> --json --url https://devconnector.springbrand.ai/mcp
   ```

   ### 3.5 Confirm configuration and authorization

   Confirm that the continuation preserves the selected client and development
   URL. Read its JSON even on exit code `4`. If configuration is confirmed,
   the MCP entry and URL match the selected environment, and `auth.status`
   is `verified`, authorization has succeeded.

   Finally, output the installation report using each item below:
   - Entry: `springbrand-dev`.
   - URL: `https://devconnector.springbrand.ai/mcp`; native Streamable HTTP transport.
   - Installation/configuration and authorization: complete when confirmed above.
   - API-key storage: when API-key authentication was selected, relay the
     locations printed by the CLI (`~/.springbrand/config.json`, the
     `SPRINGBRAND_DEV_API_KEY` block in the shell profile, and the selected
     client's MCP configuration); never include the key value.
   - MCP tool access: report it will be available to check/use in the new session.
   - Existing configuration and unrelated clients: unchanged, only if verified.
   - Next action: restart the Host and open a new conversation to begin using
     SpringBrand Dev. End this installation conversation after the report;
     no restart confirmation or return here for another check is required.


## Other Agent workflow

For any other Agent or Host, install the CLI first, then connect with the
`generic` client. The CLI cannot write this Host's MCP configuration, so the
connect report ends `pending` with the connector add as `next_action`. Apply
the mode check in **Initial installation response** before running anything.

1. Install the CLI as in step 2, on the user's own machine:

   ```sh
   npm install -g @springbrand/cli@alpha
   sp --version
   ```

   Continue only after npm succeeds and the output of `sp --version` contains
   `@springbrand/cli` and an alpha version. If it does not, another `sp` may be
   earlier on PATH; stop and report the observed output.

2. Run connect once and read its JSON report; exit code `4` is pending, not
   failure:

   ```sh
   sp connect generic --url https://devconnector.springbrand.ai/mcp --json
   ```

   With `--api-key <key>` the report shows `auth.status: verified`. Without a
   key, `next_action` sends the user to https://devrapp.springbrand.ai/ for a
   key (new users register there first) or to the Host's own OAuth.

3. Follow `next_action`: add a remote MCP connector named `springbrand-dev`
   pointing at the report's `mcp_url` (Streamable HTTP) in the Host's
   connector settings — with an `Authorization: Bearer <key>` header for
   API-key authentication (never echo the key), or the Host's own OAuth flow
   otherwise. Do not open an OAuth URL yourself or automate the browser for it.

4. Verify: run the report's `continuation` (`sp auth status --verify`) on the
   CLI side. The Host side is the authority: an authenticated `tools/list`
   request returning SpringBrand tools confirms completion, since the CLI
   cannot see the Host's internal configuration.

5. Output the installation report using the items in section 3.5.

**Recovery.** When the CLI cannot be installed or run, connect directly:
configure `https://devconnector.springbrand.ai/mcp` in the Host's remote MCP
settings as `springbrand-dev`, authenticate with a Bearer key or the Host's
OAuth, and verify with an authenticated `tools/list` request. If the Host
cannot configure or verify the connection, report the limitation and the next
action.
