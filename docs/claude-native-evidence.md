# Claude CLI and Desktop Code Native Evidence

**Status: CLI pass; Desktop Code tab pending native UI verification**

This record covers the Claude Code Host Adapter from issue #21. CLI and Desktop
Code are recorded as separate Surfaces even though they share the Claude Plugin
engine. No Desktop result is inferred from the CLI result.

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 17, 2026 |
| macOS | 14.1.2 (23B92) |
| Claude Code CLI | 2.1.228 |
| Claude Desktop | 1.24012.11 (`CFBundleVersion` 1.24012.11) |
| Repository revision | `afa138c` (`codex/issue-21-claude-evidence`) |
| Test configuration | Fresh `CLAUDE_CONFIG_DIR` temporary directory; no user Plugin, Marketplace, MCP, or OAuth configuration was reused |

## Claude Code CLI

The following native commands were run against the clean temporary configuration:

```sh
claude plugin marketplace add ./ --scope user
claude plugin install springbrand@springbrand --scope user
claude plugin list
claude plugin details springbrand@springbrand
claude mcp login plugin:springbrand:springbrand
claude mcp list
claude plugin disable springbrand@springbrand --scope user
claude plugin enable springbrand@springbrand --scope user
claude plugin update springbrand@springbrand --scope user
claude plugin uninstall springbrand@springbrand --scope user
```

| Required evidence | Result | Record |
| --- | --- | --- |
| Clean native Marketplace installation exposes the Plugin | **Pass** | `springbrand@springbrand`, version `1.2.0-beta.2`, installed and enabled in the fresh user scope. |
| Canonical Skill visibility | **Pass** | `claude plugin details springbrand@springbrand` reported one Skill named `springbrand`; the package contains the unchanged `springbrand-resource-discovery` Canonical Skill. |
| Namespaced SpringBrand MCP entry | **Pass** | `claude mcp list` reported `plugin:springbrand:springbrand` at `https://connector.springbrand.ai/mcp` as HTTP. |
| Fresh browser OAuth without static credentials or duplicate registration | **Pass** | `claude mcp login plugin:springbrand:springbrand` completed native browser OAuth; `claude mcp list` then reported `✔ Connected`. No token or API key was recorded. The unnamespaced `claude mcp login springbrand` command correctly failed because the Plugin-owned entry is namespaced. |
| Eligible/ineligible routing before work and original-task preservation | **Partial** | The static Hook was executed for both an eligible and an ineligible prompt through `tests/test_hook.py`; both outputs were prompt-independent and contained the Canonical Skill routing instruction. A full Claude model transcript proving task planning order was not captured. |
| Update, disable, uninstall, and unrelated-configuration preservation | **Pass** | Disable, enable, update (“already at latest”), and uninstall all completed in the fresh scope. After uninstall, no Plugin or MCP server remained; the Marketplace and unrelated config files remained. |

The repository and strict Claude manifest checks also passed:

```text
claude plugin validate --strict .                         PASS
claude plugin validate --strict .claude-plugin/plugin.json PASS
python3 tests/validate_plugin.py                           PASS
python3 tests/test_hook.py                                 PASS
```

### GitHub Marketplace limitation

`claude plugin marketplace add springbrand-lab/springbrand-agent-setup` was
also attempted. It failed because GitHub's default `main` branch does not yet
contain the Claude Adapter package (`.claude-plugin/marketplace.json`). The
local-directory Marketplace flow above verifies the same native install
lifecycle without pretending that an unmerged branch is available from the
repository's default branch.

## Claude Desktop Code tab

The installed Desktop build was identified from
`/Applications/Claude.app/Contents/Info.plist`, but the following Desktop-only
checks remain **pending**:

- fresh Desktop restart and Code-tab Plugin loading;
- independent Skill visibility and SpringBrand OAuth state;
- routing-before-work transcript in a Desktop Code session;
- Desktop update, disable, uninstall, and unrelated-configuration preservation.

The native macOS UI control service was unavailable during this run, so these
checks are recorded as pending rather than inferred from CLI evidence. This is
an explicit host limitation, not a Desktop pass.
