# SpringBrand Dev Plugin installation protocol

Install the `springbrand-dev` Plugin only for internal testing. It uses the same Canonical Skill and routing behavior as production, but bundles only:

```text
MCP name: springbrand-dev
MCP URL:  https://devconnector.springbrand.ai/mcp
Git ref:  v1.2.0-beta.3-dev.1
```

Before installation, disable or uninstall the full production `springbrand` Plugin. Do not enable both complete Plugins together because they duplicate the Skill and routing behavior.

Use the host-native path:

- Codex: `codex plugin marketplace add springbrand-lab/springbrand-agent-setup --ref v1.2.0-beta.3-dev.1`, then `codex plugin add springbrand-dev@springbrand-dev`.
- Claude CLI: `claude plugin marketplace add springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1 --scope user`, then `claude plugin install springbrand-dev@springbrand-dev --scope user`.
- Claude Desktop Code: **Plugin Browser → Add Marketplace**, using `springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1`.
- Cursor: **Customize → Browse Marketplace → Add Marketplace → Import from GitHub**, using `springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1`.
- WorkBuddy: **Plugins → Plugin URL**, using `https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.0-beta.3-dev.1.zip`.

Complete native OAuth for the bundled `springbrand-dev` MCP entry. Never add a token, static header, client secret, API key, local bridge, or second manually configured dev server.

After testing, uninstall `springbrand-dev`, confirm its Skill/Hook/Rule/MCP components disappear, then re-enable or reinstall production. Preserve unrelated configuration and OAuth state.
