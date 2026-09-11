# SpringBrand WorkBuddy Plugin — R2 production installation

Before validation, connectivity checks, installation commands or UI handoffs,
read and follow [Initial installation response](./INSTALL.md#initial-installation-response).
Determine first installation versus ordinary update before changing anything.
In a first-install conversation, show actual setup status and the next step,
then Welcome once at the first result report or request for user action. This
includes OAuth, restart/new-session requests, failure/blockers and existing
tasks; do not wait for verification or a new conversation. Skip ordinary
updates and later repeats. Reuse the shared template and its incomplete-setup
introduction; do not repeat installation steps when reading the shared rule.

Install through WorkBuddy's native Plugin lifecycle from the R2 release below.
Do not clone a repository, test GitHub connectivity, fetch individual Skills,
or fall back to a GitHub source. This guide covers the verified macOS native CLI
path (WorkBuddy 5.4.3 / bundled CLI 2.132.0); Windows remains unverified.

The package contains five Canonical Skills (`ask-springbrand`,
`springbrand-platform`, `springbrand-action-api`, `springbrand-connector`, `springbrand-gtm`) and
one production MCP entry, `springbrand`, at `https://connector.springbrand.ai/mcp`.
Its tool prefixes are `platform_`, `action_`, and `connector_`.

## 1. Select the published release and inspect existing state

Use the first-install/update classification established at entry. Keep it for
accurate installation reporting, including later verification after a restart;
Welcome must already have appeared at the first handoff in the original conversation.
A registered marketplace alone does not mean the Plugin was already installed.
For the manual UI fallback, inspect the existing installation in the UI.

```sh
WORKBUDDY_SOURCE="https://plugin.springbrand.ai/releases/v1.2.1/workbuddy/springbrand-workbuddy.zip"
WORKBUDDY_VERSION="1.2.1"
```

This immutable source does not follow future releases automatically. Do not
substitute a guessed latest version or an unpublished production-channel URL.
Publishing a GitHub Release alone does not update this source. A later release
needs its own verified R2 package and an explicit installation-source update.

Check the R2 ZIP and production MCP endpoint with a bounded timeout. If a
retryable request fails, inspect the system proxy once and retry once, then
stop and report. HTTP 401 from MCP can establish reachability, not successful
OAuth or tool execution. The package bundles the Skills; no separate download
is needed. R2, native WorkBuddy services and SpringBrand OAuth/MCP still require
network access.

Locate the native CLI, preferring the verified bundled macOS executable:

```sh
if [ -x "/Applications/WorkBuddy AI.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy" ]; then
  WORKBUDDY_CLI="/Applications/WorkBuddy AI.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"
elif [ -x "/Applications/WorkBuddy AI.app/Contents/Plugins/app.asar.unpacked/cli/bin/codebuddy" ]; then
  WORKBUDDY_CLI="/Applications/WorkBuddy AI.app/Contents/Plugins/app.asar.unpacked/cli/bin/codebuddy"
elif command -v codebuddy >/dev/null 2>&1; then
  WORKBUDDY_CLI="$(command -v codebuddy)"
elif command -v cbc >/dev/null 2>&1; then
  WORKBUDDY_CLI="$(command -v cbc)"
else
  WORKBUDDY_CLI=""
fi
```

If the CLI is unavailable, use the manual fallback below; do not run commands
with an empty executable. Otherwise inspect before making changes:

```sh
export CODEBUDDY_CONFIG_DIR="${CODEBUDDY_CONFIG_DIR:-$HOME/.workbuddy-ai}"
"$WORKBUDDY_CLI" plugin marketplace list
"$WORKBUDDY_CLI" plugin list --json
```

Check the registered marketplace source, not only its name. If the CLI listing
does not expose the URL, read only the SpringBrand entry of
`$CODEBUDDY_CONFIG_DIR/plugins/known_marketplaces.json`; never edit it directly.
Check for conflicting global SpringBrand MCP entries or manual Skills without
printing credentials. Preserve all unrelated configuration and OAuth state.

- No SpringBrand marketplace, plugin or conflicting legacy entry: first install.
- Same exact R2 source: use the existing-install instructions below.
- A different source, scope, manual Skill or duplicate MCP: report the conflict
  and obtain approval before replacing anything. Do not silently uninstall,
  remove a marketplace, downgrade, or refresh a GitHub source.

## 2. First install

Run only after the clean-install preflight passes:

```sh
"$WORKBUDDY_CLI" plugin marketplace add "$WORKBUDDY_SOURCE"
"$WORKBUDDY_CLI" plugin install springbrand@springbrand --scope user
"$WORKBUDDY_CLI" plugin enable springbrand@springbrand --scope user
"$WORKBUDDY_CLI" plugin list --json
```

Execute one operation at a time and inspect its result before continuing.
The native CLI may exit zero on failure: a `✘`, missing registry entry, wrong
version or wrong source means failure even if the shell exit code is zero.
Do not report success based solely on the install message.

## 3. Existing install from the same exact R2 source

Remember the existing enabled/disabled state; an update must not enable a
previously disabled Plugin unless the user explicitly requests it.

```sh
"$WORKBUDDY_CLI" plugin marketplace update springbrand
"$WORKBUDDY_CLI" plugin list --json
```

Marketplace refresh may itself update the installed Plugin. Do not run a redundant
same-version update: it can fail with `Cannot replace plugin cache in use`.

- If the Plugin is already at `WORKBUDDY_VERSION`, no plugin update is needed.
- If the marketplace exists but the Plugin is absent, run the install command
  from step 2; enable only when requested by the installation task.
- If the installed version is older, and the marketplace has refreshed to the
  intended release, run this command and check the version again:

  ```sh
  "$WORKBUDDY_CLI" plugin update springbrand@springbrand --scope user
  ```

- If a newer version is installed, stop rather than downgrade.

The pinned URL cannot fetch future release versions. Changing to a different
release URL is a source replacement, not the same-source refresh above; inspect
and obtain approval before the native replacement sequence. Do not hand-edit
marketplace or installed-plugin registries.

## 4. Reload, authorize and verify

After installation, ask the user to reload Plugins or restart WorkBuddy and
open a new task. WorkBuddy's CLI does not expose an MCP OAuth login command;
complete the native browser flow when prompted. One authorization covers the
three Capability Domains. Do not clear an existing authorization preemptively.
If an old process still shows unauthorized after browser success, restart and
check a new session before asking for authorization again.

Verify:

- exactly one `springbrand@springbrand` is installed at `WORKBUDDY_VERSION`,
  with the intended enabled state and exact R2 source;
- the five Canonical Skills are loaded in the new session;
- the bundled production MCP is connected, with no duplicate global entry;
- a real, authenticated read-only capability call succeeds; anonymous discovery
  or HTTP 401 is not sufficient;
- unrelated settings and Plugins remain unchanged.

For a read-only check, discover the current `springbrand.plugins.list` definition
through the Platform Domain Skill and obey its schema. The accepted request was
`{"name":"platform:springbrand@0:springbrand.plugins.list","body":{"view":"marketplace","page":1,"pageSize":30}}`.
Do not add `idempotency_key` to this list operation. Report actual error codes;
do not assume every `invalid_arguments` means OAuth expired. Never perform a
write operation merely to test installation.

The package retains its static, local, network-free `UserPromptSubmit` Hook;
installing and enabling the Plugin is the native trust decision for that Hook. Hook execution is not an
installation acceptance gate. Do not claim execution without runtime evidence.

Never add tokens, authorization headers, client secrets, API keys, local MCP
bridges or a second global MCP to work around installation/authentication.
Never read or print token contents. Report version, source, Skills, OAuth,
actual call result, changes made and any remaining reload requirement separately.

## Manual UI fallback

Use only when the CLI is unavailable or the user explicitly wants manual control.
Open **Experts · Skills · Connectors → Add Marketplace** and, if the installed
build accepts ZIP URLs, enter the exact `WORKBUDDY_SOURCE` above. Install/enable
SpringBrand and perform the same OAuth and verification steps.

The R2 ZIP CLI route is verified; this UI ZIP route is not separately accepted.
If the UI does not accept the ZIP URL, stop and report the unsupported path.
Do not substitute a repository source or claim successful installation.

## Disable and uninstall

Use the native CLI, with user intent confirmed:

```sh
"$WORKBUDDY_CLI" plugin disable springbrand@springbrand --scope user
"$WORKBUDDY_CLI" plugin uninstall springbrand@springbrand --scope user
```

Remove the SpringBrand marketplace only if the user also wants the source removed:

```sh
"$WORKBUDDY_CLI" plugin marketplace remove springbrand
```

Inspect the final plugin/marketplace lists. Do not delete unrelated configuration
or OAuth credentials. No GitHub access is needed for these R2 lifecycle operations.
