# SpringBrand Dev Plugin

Internal-testing Plugin variant for SpringBrand. It packages the same Canonical Skill, routing Hook/Rule, and assets as the production Plugin, but connects only to the development MCP service.

| Field | Value |
| --- | --- |
| Plugin / Marketplace | `springbrand-dev` |
| Display name | SpringBrand Dev |
| MCP server | `springbrand-dev` |
| MCP URL | `https://devconnector.springbrand.ai/mcp` |
| Version | `1.2.0-beta.3-dev.1` |
| Immutable ref | `v1.2.0-beta.3-dev.1` |

**Testing only:** do not enable the full `springbrand` and `springbrand-dev` Plugins at the same time. They package the same Skill and routing behavior, so parallel enablement can duplicate routing and make connector selection ambiguous. Disable or uninstall production before enabling this variant.

## Install

### Codex CLI / Desktop

```sh
codex plugin marketplace add springbrand-lab/springbrand-agent-setup --ref v1.2.0-beta.3-dev.1
codex plugin add springbrand-dev@springbrand-dev
codex mcp login springbrand-dev
```

The Marketplace bootstrap also makes **SpringBrand Dev** available in the Codex desktop Plugins Directory.

### Claude Code CLI

```sh
claude plugin marketplace add springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1 --scope user
claude plugin install springbrand-dev@springbrand-dev --scope user
claude mcp login plugin:springbrand-dev:springbrand-dev
```

Claude Desktop's Code tab uses the same Plugin engine. Add the same GitHub ref in **Plugin Browser → Add Marketplace**, then install **SpringBrand Dev**.

### Cursor

Open **Customize → Browse Marketplace → Add Marketplace → Import from GitHub** and enter:

```text
springbrand-lab/springbrand-agent-setup@v1.2.0-beta.3-dev.1
```

Install **SpringBrand Dev** and complete native OAuth for `springbrand-dev`.

### WorkBuddy

Open **Plugins → Plugin URL** and enter:

```text
https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/tags/v1.2.0-beta.3-dev.1.zip
```

Install **SpringBrand Dev** and complete native OAuth for `springbrand-dev`.

## Verify

```sh
python3 tests/validate_plugin.py
python3 tests/test_validator.py
python3 tests/test_hook.py
python3 tests/test_repair_cursor_plugin.py
python3 tests/test_repair_workbuddy_plugin.py
git diff --check
```

No package contains tokens, static authorization headers, client secrets, API keys, or local MCP bridges. OAuth remains owned by each host.

Production remains available from the `stable` branch and production release tags.
