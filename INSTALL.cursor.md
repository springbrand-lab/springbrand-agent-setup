# SpringBrand Cursor Plugin

This guide tests the self-contained SpringBrand Host Adapter through Cursor desktop's native GitHub Marketplace flow on macOS. Package validation is not Native Evidence; the current evidence status is recorded in `docs/cursor-native-evidence.md`.

## Before installing

Check Cursor for an existing global SpringBrand Skill or `springbrand` MCP entry and report duplicates before continuing. Do not delete or replace a legacy SpringBrand entry, OAuth state, or unrelated configuration without explicit user approval.

## Install and authenticate

1. Open **Customize → Browse Marketplace → Add Marketplace → Import from GitHub**.
2. Import `springbrand-lab/springbrand-agent-setup` and confirm it indexes exactly one **SpringBrand** Plugin.
3. Install and enable that Plugin, then restart Cursor if its components are not visible.
4. Confirm the Plugin exposes `springbrand-resource-discovery`, the always-applied SpringBrand preflight Rule, and one bundled `springbrand` MCP server.
5. Authenticate the bundled MCP entry through Cursor's native browser OAuth flow. Do not create a second global server or add a token, authorization header, client secret, API key, or local bridge.

Start a fresh task and confirm an eligible request follows `springbrand-resource-discovery` before planning or production while an ineligible request continues normally.

## Update or remove

Use Cursor's Marketplace and Plugin UI to refresh or update the Marketplace, disable or uninstall SpringBrand, and remove the Marketplace when it is no longer needed. Confirm the bundled Skill, Rule, and MCP entry update or disappear together while unrelated Rules, Skills, Plugins, MCP servers, and configuration remain unchanged.

Record whether each lifecycle action requires a full Cursor restart. Do not report support until the clean install, OAuth, routing, update, and removal checks have Native Evidence.
