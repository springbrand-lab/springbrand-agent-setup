# SpringBrand WorkBuddy Plugin

Install SpringBrand through WorkBuddy's native Plugin lifecycle. A WorkBuddy
Agent must use the bundled CLI first; the UI steps remain a manual fallback.
Package validation is not Native Evidence; runtime evidence is recorded in
`docs/workbuddy-native-evidence.md`.

## Preflight

Check for an existing SpringBrand Plugin, Marketplace, global MCP entry, or
manual Skill. Preserve unrelated configuration and OAuth state. Report a
conflicting legacy SpringBrand entry and wait for approval before replacing or
removing it.

## Agent-first production install

Locate WorkBuddy's native CLI:

```sh
if command -v codebuddy >/dev/null 2>&1; then
  WORKBUDDY_CLI="$(command -v codebuddy)"
elif command -v cbc >/dev/null 2>&1; then
  WORKBUDDY_CLI="$(command -v cbc)"
elif [ -x "/Applications/WorkBuddy AI.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy" ]; then
  WORKBUDDY_CLI="/Applications/WorkBuddy AI.app/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"
else
  WORKBUDDY_CLI=""
fi
```

If `WORKBUDDY_CLI` is non-empty, install or update in WorkBuddy's user config:

```sh
export CODEBUDDY_CONFIG_DIR="${CODEBUDDY_CONFIG_DIR:-$HOME/.workbuddy-ai}"

if "$WORKBUDDY_CLI" plugin marketplace list | grep -q '"name": "springbrand"'; then
  "$WORKBUDDY_CLI" plugin marketplace update springbrand
else
  "$WORKBUDDY_CLI" plugin marketplace add springbrand-lab/springbrand-agent-setup
fi

if "$WORKBUDDY_CLI" plugin list --json | grep -q '"id": "springbrand@springbrand"'; then
  "$WORKBUDDY_CLI" plugin update springbrand@springbrand --scope user
else
  "$WORKBUDDY_CLI" plugin install springbrand@springbrand --scope user
fi

"$WORKBUDDY_CLI" plugin enable springbrand@springbrand --scope user
"$WORKBUDDY_CLI" plugin list --json
```

Do not stop before running these commands merely because installation is also
available in the UI. After they succeed, tell the user to run
`/reload-plugins` or open a new task. WorkBuddy's CLI does not expose an MCP
OAuth login command, so the user must complete native browser OAuth when
WorkBuddy prompts for the bundled `springbrand` server.

## Manual UI fallback

Use this only when the native CLI is unavailable, or when the user explicitly
wants to install manually:

1. Open **Experts · Skills · Connectors → Add Marketplace**.
2. In **Marketplace Source**, enter:

   ```text
   springbrand-lab/springbrand-agent-setup
   ```

   The full GitHub URL is also accepted:

   ```text
   https://github.com/springbrand-lab/springbrand-agent-setup
   ```

3. Add the Marketplace, then install and enable **SpringBrand**.
4. Complete native OAuth for the bundled `springbrand` MCP server.

The repository default branch `main` is the rolling production source. Do not
add trailing punctuation to the Marketplace source.

## Development install

Do not enable the complete production and development Plugins together.
WorkBuddy does not accept `owner/repo@tag`, so use the immutable dev ZIP as the
Marketplace source.

With the CLI located above:

```sh
export CODEBUDDY_CONFIG_DIR="${CODEBUDDY_CONFIG_DIR:-$HOME/.workbuddy-ai}"

if "$WORKBUDDY_CLI" plugin marketplace list | grep -q '"name": "springbrand-dev"'; then
  "$WORKBUDDY_CLI" plugin marketplace update springbrand-dev
else
  "$WORKBUDDY_CLI" plugin marketplace add \
    https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.0-beta.4-dev.1.zip
fi

if "$WORKBUDDY_CLI" plugin list --json | grep -q '"id": "springbrand-dev@springbrand-dev"'; then
  "$WORKBUDDY_CLI" plugin update springbrand-dev@springbrand-dev --scope user
else
  "$WORKBUDDY_CLI" plugin install springbrand-dev@springbrand-dev --scope user
fi

"$WORKBUDDY_CLI" plugin enable springbrand-dev@springbrand-dev --scope user
```

For manual development installation, paste the same ZIP into **Add
Marketplace**, install **SpringBrand Dev**, and complete OAuth for
`springbrand-dev`.

## Security and verification

Do not add a second global MCP server, local bridge, token, authorization
header, client secret, or API key. Installing and enabling the Plugin is
WorkBuddy's accepted native trust decision for its executable Plugin-level
`UserPromptSubmit` Hook. The Hook is deterministic, local, network-free,
prompt-stateless, and does not write prompt data.

After reload or a new task, verify:

- exactly one `springbrand@springbrand` Plugin is installed and enabled;
- its version matches repository `main`;
- `springbrand-resource-discovery` is visible;
- the bundled `springbrand` MCP points only to
  `https://connector.springbrand.ai/mcp` and is OAuth-connected;
- the Plugin-level Hook is loaded;
- a clear capability-gap request triggers discovery, while summarizing supplied
  material does not call SpringBrand;
- unrelated configuration remains unchanged.

Use the CLI `plugin marketplace update`, `plugin update`, `plugin disable`, and
`plugin uninstall` commands for lifecycle operations. Use the corresponding UI
only as fallback or when the user prefers manual control.
