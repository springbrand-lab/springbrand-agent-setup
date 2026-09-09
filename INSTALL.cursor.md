# SpringBrand Cursor Plugin

This guide tests the self-contained SpringBrand Host Adapter through Cursor desktop's native GitHub Marketplace flow on macOS. Package validation is not Native Evidence; the current evidence status is recorded in `docs/cursor-native-evidence.md`.

## Before installing

Before changing anything, determine whether this is a first installation or an
update of an existing SpringBrand installation. Keep that classification for
final reporting, including when verification continues in a new session.

Check Cursor for an existing global SpringBrand Skill or `springbrand` MCP entry and report duplicates before continuing. Do not delete or replace a legacy SpringBrand entry, OAuth state, or unrelated configuration without explicit user approval.

A Legacy Plugin Release using a single `springbrand` entry at `https://connector.springbrand.ai/mcp` with the Gateway's legacy mixed contract continues to work until the production release switches the `/mcp` slot to the unified endpoint; upgrading to the current Plugin with domain-prefixed tools is voluntary and there is no automatic sunset.

## Install and authenticate

1. Open **Customize → Browse Marketplace → Add Marketplace → Import from GitHub**.
2. Import `springbrand-lab/springbrand-agent-setup` and confirm it indexes exactly one **SpringBrand** Plugin.
3. Install and enable that Plugin, then restart Cursor if its components are not visible.
4. Confirm the Plugin exposes the four Canonical Skills (`ask-springbrand`, `springbrand-platform`, `springbrand-action-api`, `springbrand-connector`), the always-applied SpringBrand preflight Rule, and one bundled MCP server:
   - `springbrand` → `https://connector.springbrand.ai/mcp`
5. Authenticate the bundled MCP entry through Cursor's native browser OAuth flow. A single consent covers all three domains. Do not create a second global server or add a token, authorization header, client secret, API key, or local bridge.

Start a fresh task and confirm a covered request follows `ask-springbrand` before planning or production.

After installation verification succeeds, read and follow
[After installation](./INSTALL.md#after-installation) using the original
first-install/update classification. Apply that section's welcome rules even
when this guide was the direct entry point; do not repeat the installation steps.

## Update or remove

Use Cursor's Marketplace and Plugin UI to refresh or update the Marketplace, disable or uninstall SpringBrand, and remove the Marketplace when it is no longer needed. Confirm the bundled Skills, Rule, and MCP entries update or disappear together while unrelated Rules, Skills, Plugins, MCP servers, and configuration remain unchanged.

Record whether each lifecycle action requires a full Cursor restart. Do not report support until the clean install, OAuth, routing, update, and removal checks have Native Evidence.
