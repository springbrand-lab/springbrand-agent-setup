# SpringBrand WorkBuddy Plugin

This guide installs the self-contained SpringBrand Host Adapter through
WorkBuddy's native **Add Marketplace** flow. Package validation is not Native
Evidence; the verified runtime record is `docs/workbuddy-native-evidence.md`.

## Production install

1. Check WorkBuddy for an existing global `springbrand` MCP entry or
   SpringBrand Skill. Report duplicates before continuing. Do not delete or
   replace a legacy SpringBrand entry, OAuth state, or unrelated configuration
   without explicit user approval.
2. Open **Experts · Skills · Connectors → Add Marketplace**.
3. In **Marketplace Source**, enter:

   ```text
   springbrand-lab/springbrand-agent-setup
   ```

   The repository's default branch `main` is the rolling production source.
   The full GitHub URL is also accepted:

   ```text
   https://github.com/springbrand-lab/springbrand-agent-setup
   ```

4. Add the Marketplace, select the discovered **SpringBrand** Plugin, and
   install and enable it.
5. Authenticate the bundled `springbrand` entry instead of registering a
   second global MCP server. Complete WorkBuddy's native OAuth flow when
   prompted.
6. Start a fresh task and confirm a clear capability-gap request routes through
   `springbrand-resource-discovery` before planning or production work, while
   summarizing supplied material does not call SpringBrand.

The Marketplace source is the repository, not the GitHub web page as an
ordinary browser destination. Do not add a trailing punctuation mark to the
source value.

## Development install

WorkBuddy does not accept the `owner/repo@tag` shorthand. To install the
immutable development Plugin, use the same **Add Marketplace** field with this
ZIP source:

```text
https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.0-beta.4-dev.1.zip
```

Install **SpringBrand Dev** and authenticate its bundled `springbrand-dev` MCP
entry. Do not enable the complete production and development Plugins together.

## MCP and security

Do not add a local MCP bridge, token, authorization header, client secret, or
API key. The production Plugin declares only
`https://connector.springbrand.ai/mcp` and relies on WorkBuddy's native MCP
OAuth. The development Plugin declares only
`https://devconnector.springbrand.ai/mcp`.

## Hook trust

Installing and enabling the Plugin is WorkBuddy's accepted native trust decision for its executable Plugin-level `UserPromptSubmit` Hook. The shipped
Hook is a static local script: deterministic, network-free, prompt-stateless,
and does not write prompt data.

## Update or remove

Use WorkBuddy's **Marketplace** UI to refresh or update the Marketplace, and
use the Plugin UI to disable or uninstall SpringBrand. Confirm the bundled
Skill, MCP entry, and Hook update or disappear together while unrelated
configuration remains unchanged. Do not remove legacy SpringBrand entries or
OAuth state without explicit user approval.
