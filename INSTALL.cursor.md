# SpringBrand Dev Cursor Plugin

Internal testing only. Disable or uninstall the production SpringBrand Plugin before continuing.

1. Open **Customize → Browse Marketplace → Add Marketplace → Import from GitHub**.
2. Enter `springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1`.
3. Install and enable **SpringBrand Dev**.
4. Confirm the Plugin exposes `springbrand-resource-discovery`, the always-applied preflight Rule, and one `springbrand-dev` MCP server at `https://devconnector.springbrand.ai/mcp`.
5. Complete Cursor's native browser OAuth. Do not add credentials, a local bridge, or a second global dev server.
6. Start a fresh task and verify eligible work runs Resource Discovery before planning or production.

After testing, uninstall **SpringBrand Dev** and confirm its Skill, Rule, and MCP entry disappear together while unrelated configuration remains unchanged. Re-enable production only afterward.
