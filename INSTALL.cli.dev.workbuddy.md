# SpringBrand development CLI installation protocol

CLI channel: `@springbrand/cli@alpha`.
Development release identity: `v1.2.1-dev.2`; entry `springbrand-dev`, endpoint
`https://devconnector.springbrand.ai/mcp`.

## Required environment authorization

This installation changes the selected Host's local MCP, Plugin, and Skill
configuration and requires outbound network access.

WorkBuddy's default permission mode stops at
high-risk operations and asks the user to confirm each one; that confirmation
path is the intended way to run this installation.

The user will see confirmation prompts for expected operations, including:

- installing the CLI globally through the npm registry and using a user-owned
  npm cache;
- writing the WorkBuddy MCP configuration at `~/.workbuddy-ai/mcp.json` and the
  Skill files under `~/.workbuddy-ai/skills`;
- writing the CLI's own configuration at `~/.springbrand/config.json` and, when
  API-key authentication is selected, a managed `SPRINGBRAND_API_KEY` block in
  the user's shell profile;
- executing `npm`, `sp`, and the WorkBuddy integration or CLI;
- reaching the SpringBrand MCP endpoint and the applicable RApp for account or
  OAuth setup.


## Installation preconditions

The following are installation preconditions. They are not optional hints, and
approving the session's confirmation prompts does not prove that every
precondition is met:

- the selected Host can read and write its local MCP and Plugin/Skill configuration;
- the npm cache and global installation location are writable by the current user;
- the npm registry and `https://devconnector.springbrand.ai/mcp` are reachable;
- the selected Host integration or CLI can execute;

Account and authentication requirements are handled from step 3 onward; they
are not prerequisites for installing the CLI in step 2. Connection requires a
development SpringBrand account and either an accepted development API key or
completed native OAuth for the `springbrand-dev` MCP entry.


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
Do not read another installation guide.
Do not run a business operation as an installation check.

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
   - Any other Agent: use the Other Agent workflow below.

   The current Agent surface and the installation target are separate. If the
   current surface is Work Local and the target is Codex Local, select `codex`
   and continue this numbered CLI workflow. If the target is Work itself, do not
   enter the numbered CLI workflow; use the Other Agent workflow below.

2. Install the alpha CLI, then verify that the installed command runs. Execute
   these commands separately and check each result before continuing:

   ```sh
   npm install -g @springbrand/cli@alpha
   sp --version
   ```

   Continue only after npm succeeds and `sp --version` reports an alpha
   version.

3. Connect SpringBrand to the selected client.

   ### 3.1 Select authentication and run connect

   If the user's prompt includes an API key, run:

   ```sh
   sp connect <client> --url https://devconnector.springbrand.ai/mcp --api-key <key> --json
   ```

   Otherwise, ask the user to obtain an API key from the development RApp
   or continue with OAuth. A development SpringBrand account is required. If the user does not have
   one, ask them to register at https://devrapp.springbrand.ai/.
   Once they provide a key, run the command above.
   If they choose OAuth, run:

   ```sh
   sp connect <client> --url https://devconnector.springbrand.ai/mcp --json
   ```

   Keep the selected authentication mode as `auth_mode` for the following
   steps. Never include the API key in reports.

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

   For an agent-owned native OAuth action, run the returned login command
   once and retain the connect report's `continuation`.

   Keep the current agent turn active while the native OAuth process runs.
   When the execution tool returns a running session/job ID, retain it and
   use that tool's wait/poll operation on the same process until it exits.
   Use bounded waits and brief progress updates while the user authorizes in
   the browser. A tool yielding control or printing an authorization URL is
   not an OAuth timeout and does not require a user reply. Do not send a
   final answer asking the user to say "done" or "authorization complete"
   while the process is running.

   Exit code `0` with `Successfully logged in` confirms OAuth authorization.
   Immediately continue verification in the same turn; no additional user
   confirmation is needed. Only pause for cancellation, an actual process
   timeout/failure, or an explicit request for information the agent lacks.
   Report the observed state and keep the selected Host and environment.

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
   - Trust step: WorkBuddy requires the user to trust a newly installed MCP
     entry; tell the user to approve the `springbrand-dev` trust prompt when
     WorkBuddy shows it.
   - API-key storage: when API-key authentication was selected, disclose that
     the key is stored in plaintext in `~/.workbuddy-ai/mcp.json`, in
     `~/.springbrand/config.json`, and in a managed `SPRINGBRAND_API_KEY` block
     in the user's shell profile; never include the key value.
   - MCP tool access: report it will be available to check/use in the new session.
   - Existing configuration and unrelated clients: unchanged, only if verified.
   - Next action: restart the Host and open a new conversation to begin using
     SpringBrand Dev. End this installation conversation after the report;
     no restart confirmation or return here for another check is required.


## Other Agent workflow

For other Agents or Hosts that cannot run the local CLI, connect directly to
`https://devconnector.springbrand.ai/mcp` using the Host's remote MCP settings.
Use `springbrand-dev` as the entry name where supported. No CLI or Plugin
installation is required.

If the user supplied an API key, configure it as a Bearer credential. Otherwise,
ask them to obtain a key from https://devrapp.springbrand.ai/ or choose native
OAuth. New users must register there first. Complete authentication through
the Host's supported flow without including credentials in reports.

Send an authenticated `tools/list` request. A successful response containing
SpringBrand tools confirms completion. If the Host cannot configure or verify
the connection, report the limitation and the next action.
