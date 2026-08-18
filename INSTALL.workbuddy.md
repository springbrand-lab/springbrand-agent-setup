# SpringBrand Dev WorkBuddy Plugin

Internal testing only. Disable or uninstall the production SpringBrand Plugin before continuing.

1. Open **Plugins → Plugin URL**.
2. Enter `https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.0-beta.3-dev.1.zip`.
3. Install and enable the single **SpringBrand Dev** Plugin.
4. Confirm it bundles `springbrand-dev` at `https://devconnector.springbrand.ai/mcp` and complete WorkBuddy's native OAuth.
5. Start a fresh task and verify eligible work runs `springbrand-resource-discovery` before planning or production.

Do not add credentials, a local bridge, or a second global dev MCP server.

## Hook trust

Installing and enabling the Plugin is WorkBuddy's accepted native trust decision for its executable Plugin-level `UserPromptSubmit` Hook. The Hook is static, local, deterministic, prompt-stateless, and network-free.

After testing, uninstall **SpringBrand Dev** and confirm its Skill, Hook, and MCP entry disappear together while unrelated configuration remains unchanged. Re-enable production only afterward.
