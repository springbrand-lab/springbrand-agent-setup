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

### Current-branch GitHub Marketplace retest — August 18, 2026

A second clean run tested the remote integration branch directly rather than a
local-directory Marketplace:

| Field | Value |
| --- | --- |
| Marketplace source | `springbrand-lab/springbrand-agent-setup@tony/multi-host-planning-docs` |
| Repository revision | `e368d47c42037216aff1d0a1cff8e339c66d406e` |
| macOS | 14.1.2 (23B92) |
| Claude Code CLI | 2.1.228 for installation; the interactive launcher reported 2.1.234 |
| Claude Desktop | 1.24012.11 |
| Configuration | Fresh isolated `CLAUDE_CONFIG_DIR`; neutral workspace outside the repository |

The GitHub branch clone, Marketplace validation, Plugin installation, component
inventory, namespaced MCP registration, and fresh browser OAuth all passed.
`claude plugin details` reported one Skill, one `UserPromptSubmit` Hook, and one
MCP server. `claude mcp list` changed from `Needs authentication` to `Connected`
for `plugin:springbrand:springbrand`; no duplicate SpringBrand MCP entry was
present.

The interactive routing run did not begin because the fresh Claude configuration
required a separate Claude account login. Eligible/ineligible model routing,
original-task preservation, and the Desktop Code checks remain pending. The
adapter is therefore proven installable from the current branch, but issue #21
and the `1.2.0` release gate remain open.

GitHub's default `main` branch still does not contain the Claude Adapter package,
so default-main installation cannot pass until this branch is merged.

### Current-branch routing retest — August 18, 2026

The first real interactive run exposed two P1 package defects that strict schema
validation had not detected:

1. Claude auto-discovered the root Codex `hooks/hooks.json` in addition to the
   explicit Claude Hook, producing a duplicate failing invocation at
   `/hooks/user-prompt-submit`. Commit `7a0de2f` moved the Codex Hook to the
   explicit non-default path `hooks/codex-hooks.json`.
2. Claude exposes Plugin Skills by namespace (`/springbrand:springbrand`), while
   the Hook named only the Canonical Skill frontmatter name. The model therefore
   skipped the Skill and followed the MCP server's shorter guidance. Commit
   `a735508` makes the Claude Hook invoke `/springbrand:springbrand` while still
   naming `springbrand-resource-discovery` as the Canonical Skill.

After reinstalling the remote branch, the final run on Claude Code 2.1.234 passed:

- the `UserPromptSubmit` Hook ran once with no Hook error;
- `/springbrand:springbrand` loaded successfully before planning or production;
- the model searched exactly for `springbrand.resources.list`;
- targeted discovery used `view=marketplace` with `query="coffee website"`;
- the empty targeted result triggered the required complete-catalog fallback;
- all 23 Marketplace Resources were evaluated, none was forced into the task,
  and the original website request continued normally;
- the task produced `index.html`, `css/style.css`, and `js/main.js`, then passed
  JavaScript syntax, HTML balance, asset-reference, and HTTP 200 checks;
- a separate `2+2` session returned only `4` and invoked no Skill or MCP tool.

The final package was also uninstalled and reinstalled from the refreshed remote
Marketplace during the fixes. The namespaced MCP OAuth remained connected, and
no unrelated Plugin or MCP entry was added or removed.

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
