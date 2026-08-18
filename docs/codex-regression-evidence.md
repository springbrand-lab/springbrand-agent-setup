# Codex Regression and Legacy Migration Evidence

**Status: PASS**

This record covers the final-package Codex regression and legacy migration
checks required by issue
[#24](https://github.com/springbrand-lab/springbrand-agent-setup/issues/24).
It supplements the earlier beta Desktop security-flow evidence rather than
replacing it.

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 18, 2026 |
| macOS | 14.1.2 (23B92) |
| Codex CLI | 0.147.0 |
| Codex Desktop | 26.810.52044 (`CFBundleVersion` 6662) |
| Marketplace source | `springbrand-lab/springbrand-agent-setup`, ref `tony/multi-host-planning-docs` |
| Repository revision | `e73224accb1e55a7a78598c3d894c93595f5af1f` |
| Package version | `1.2.0-beta.2` |
| Evidence bundle | `/Users/tony/Desktop/springbrand-issue24-20260818` |
| Final local state | SpringBrand Marketplace retained; Plugin reinstalled and enabled |

## Package and Hook regression

The repository validator, validator regression checks, Hook tests, Cursor mirror
repair test, WorkBuddy mirror repair test, and `git diff --check` all passed.
The installed Skill, Hook, and MCP files were byte-identical to the final branch
package, and the installed Hook remained executable.

The deterministic Hook emitted SpringBrand routing before production work for
an eligible website task and remained silent for the ineligible arithmetic
control.

## CLI and Desktop smoke

| Required evidence | Result | Record |
| --- | --- | --- |
| Remote current-branch Marketplace | **Pass** | The previous default-main Marketplace snapshot was removed and re-added with ref `tony/multi-host-planning-docs`; the checked-out revision exactly matched `e73224a`. |
| Plugin installation | **Pass** | `codex plugin add springbrand@springbrand` installed one enabled Plugin at version `1.2.0-beta.2`. |
| Plugin-owned MCP without global duplicate | **Pass** | `codex mcp list` exposed `springbrand` only while the Plugin was installed. No `[mcp_servers.springbrand]` entry was added to user `config.toml`; uninstall removed the visible MCP and reinstall restored it. |
| Fresh native OAuth | **Pass** | `codex mcp login springbrand` completed the browser OAuth flow against the production endpoint. No token or static credential was recorded. |
| Hook trust | **Pass** | The final package Hook ran without a trust error under the previously reviewed native Desktop Hook trust state. The Hook source and configuration were unchanged by the multi-host work. |
| Eligible first-action routing | **Pass** | The fresh session loaded the Plugin Skill before production, searched exactly for `springbrand.resources.list`, executed the full `platform:springbrand@0:springbrand.resources.list` reference, and used `view=marketplace`. |
| Targeted discovery | **Pass** | Query `dessert brand website`, page `1`, page size `100`, returned zero Resources. |
| Complete-catalog fallback | **Pass** | The same full capability reference was executed without a query and returned all 23 Resources. No `view=usable` discovery occurred. |
| Original-task preservation | **Pass** | After determining that no Resource fit the commercial dessert-brand website, Codex created and structurally validated `index.html`. |
| Ineligible routing | **Pass** | A fresh `2+2` session returned only `4`; its JSONL stream contained no SpringBrand event. |
| Desktop visibility/runtime | **Pass** | The eligible session metadata identified `Codex Desktop` as originator. The Desktop task displayed the running session, and its persisted event stream recorded the Skill, MCP calls, website production, validation, and final response. |
| Uninstall and reinstall | **Pass** | Native removal deleted the installed Plugin and removed its MCP from `codex mcp list`; the Marketplace remained. Reinstallation restored one enabled Plugin and one Plugin-owned MCP. |
| Unrelated Plugin preservation | **Pass** | The ten pre-existing non-SpringBrand Plugins remained installed and enabled after the full lifecycle. |

## Legacy migration matrix

Two disposable `CODEX_HOME` profiles exercised the supported legacy states.
Both contained a sentinel manual
`skills/springbrand-resource-discovery/SKILL.md`, an unrelated MCP server,
unrelated configuration, and a global SpringBrand MCP entry.

| Scenario | Result |
| --- | --- |
| Matching global SpringBrand MCP (`https://connector.springbrand.ai/mcp`) | **Pass** — install and remove left the global entry and manual Skill byte-for-byte unchanged. |
| Mismatched global SpringBrand MCP (`http://127.0.0.1:9999/mcp`) | **Pass** — install did not replace, remove, disable, or duplicate the legacy entry; the manual Skill and unrelated configuration remained unchanged. |

In both cases the Plugin added only its native Marketplace and Plugin config,
then removal deleted only the Plugin config and cache. The Marketplace remained
available for later installation. No legacy SpringBrand entry was changed
without approval.

## Configuration preservation

A parsed before/after comparison confirmed that the user's model, feature,
MCP, shell-environment, Desktop, notice, and all unrelated Plugin settings were
unchanged. Existing Marketplace sources, refs, and revisions were unchanged;
Codex refreshed one unrelated Marketplace timestamp during normal startup. The
eligible smoke session also added its temporary workspace trust entry, which is
session setup rather than Plugin migration.

## Non-blocking observations

The CLI emitted unrelated warnings for the user's existing custom provider API
key, remote curated Plugin catalog authentication, and unavailable browser
preview. These warnings did not affect SpringBrand installation, OAuth, Hook
routing, MCP execution, artifact completion, or validation.

The final SpringBrand Plugin remains installed and enabled from the current
integration branch for subsequent cross-Host evaluation.
