# WorkBuddy Plugin Native Evidence

**Status: STALE — `1.2.0-beta.4` routing and lifecycle rerun required**

**Current distribution note (August 19, 2026):** WorkBuddy 5.3.13 exposes **Add Marketplace** with a Marketplace Source field accepting `owner/repo` and full GitHub URLs. Production guidance now uses `springbrand-lab/springbrand-agent-setup`; the historical Plugin URL run below remains evidence for the old branch and is not current installation guidance.

**CLI verification (August 19, 2026):** the WorkBuddy-bundled `codebuddy` CLI successfully added `springbrand-lab/springbrand-agent-setup` as a GitHub Marketplace and installed `springbrand@springbrand` version `1.2.0-beta.4` from `main` in an isolated `CODEBUDDY_CONFIG_DIR`. Current Agent guidance therefore uses CLI first and keeps Add Marketplace as the manual fallback.

The `1.2.0-beta.4` capability-gap gate changes the Canonical Skill and Plugin-level `UserPromptSubmit` routing contract. The results below remain historical; WorkBuddy must rerun the new routing corpus and native lifecycle before counting toward `1.2.0`.

This record covers the macOS WorkBuddy Native Evidence required by issue
[#23](https://github.com/springbrand-lab/springbrand-agent-setup/issues/23).
Schema validation is recorded separately and is not treated as runtime success.

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 18, 2026 |
| macOS | 14.1.2 (23B92) |
| WorkBuddy AI | 5.3.13 (`CFBundleVersion` 5.3.13) |
| Marketplace source | `https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/heads/tony/multi-host-planning-docs.zip` |
| Final repository revision | `1d76bcf` (`tony/multi-host-planning-docs`) |
| Package version | `1.2.0-beta.2` |
| Final local state | SpringBrand Marketplace retained; Plugin reinstalled, enabled, and connected |

## Native installation surface

The tested WorkBuddy build did not expose the generic third-party Marketplace
entry described by the earlier capability research. Its native **Plugin URL**
entry accepted the branch archive URL above, read
`.codebuddy-plugin/marketplace.json`, discovered exactly one SpringBrand Plugin,
and installed `springbrand@springbrand`.

Installation and enablement were the observed native trust boundary for the
Plugin-level executable Hook. No separate per-Hook approval UI appeared.

## Acceptance evidence

| Required evidence | Result | Record |
| --- | --- | --- |
| WorkBuddy 5.3.13 or newer | **Pass** | WorkBuddy AI 5.3.13 on macOS 14.1.2. |
| Exactly one SpringBrand Plugin | **Pass** | The Plugin URL source exposed and installed only `springbrand@springbrand`, version `1.2.0-beta.2`. |
| Skill, MCP, and Hook installation | **Pass** | Native logs loaded one `springbrand-plugin-discovery` Skill, one MCP server, and the SpringBrand Hook configuration. |
| Native Hook trust boundary | **Pass** | Installing and enabling the Plugin activated its local `UserPromptSubmit` Hook; no additional Hook-specific consent surface was presented. |
| Fresh production OAuth | **Pass** | Native browser OAuth completed against `https://connector.springbrand.ai/mcp` without API keys or packaged credentials. The server exposed `springbrand_search_capabilities` and `springbrand_execute_capability`. |
| Full-restart loading | **Pass** | A full application quit and restart reloaded the Plugin, Skill, Hook, and MCP connection. |
| Eligible routing before work | **Pass** | `UserPromptSubmit` and `springbrand-plugin-discovery` ran before website planning or production. WorkBuddy searched `springbrand.plugins.list`, executed the full `platform:springbrand@0:springbrand.plugins.list` reference through `execute_capability`, used `view=marketplace`, and evaluated all 23 Plugins before beginning the requested dessert-brand website. |
| Original-task preservation | **Pass** | No suitable commercial dessert-brand website Plugin existed in the complete catalog. WorkBuddy reported the no-match result and completed the original website task instead of stopping at discovery. |
| Ineligible behavior | **Pass** | A fresh `2+2` task returned `4` without loading the SpringBrand Skill or calling the MCP. |
| Update behavior | **Pass** | Marketplace refresh and Plugin update replaced the installed Distribution Mirror without creating a duplicate; a full restart loaded the updated Skill. |
| Disable and enable | **Pass** | Disable plus full restart removed the active SpringBrand components; enable plus full restart restored the Skill, Hook, and MCP while preserving authorization and unrelated configuration. |
| Uninstall and reinstall | **Pass** | Uninstall plus full restart removed the installed Plugin and active components. Reinstallation from the retained Marketplace restored one enabled Plugin without duplicating it. |
| Marketplace and authorization cleanup | **Pass** | Marketplace removal/re-add and SpringBrand-specific authorization cleanup behavior were exercised. Uninstall did not require deletion of unrelated credentials or configuration; the final reinstall retained the SpringBrand Marketplace and working authorization state. |
| Unrelated configuration preservation | **Pass** | The five pre-existing WorkBuddy built-in Plugins remained installed and enabled after the complete lifecycle run. |

## Routing defects found and fixed

The native run exposed two P1 instruction ambiguities:

1. WorkBuddy initially used the bare action identifier instead of the full
   capability reference. Commit `188cde8` now requires copying the exact returned
   capability `name` and using JSON-integer pagination values.
2. WorkBuddy then treated the capability reference as a deferred tool name.
   Commit `1d76bcf` now states that capability references are data and must be
   passed as the `name` argument to SpringBrand's `execute_capability` tool.

The Marketplace and installed Plugin were refreshed after both fixes. All
repository validators passed, and a post-restart direct check returned the
complete 23-Plugin catalog through the corrected execution path.

## Observed host behavior

WorkBuddy sometimes serialized nested numeric pagination fields as strings.
The Gateway correctly rejected those calls. WorkBuddy recovered by omitting the
defaulted pagination fields; because the complete catalog contained 23 items,
the default page contained the entire catalog. It also made unnecessary extra
keyword queries after the complete-catalog result. These calls were inefficient
but did not alter routing-before-work, complete-catalog coverage, Plugin
selection, or original-task completion.

The first OAuth attempt was also blocked by the local VPN TUN/DNS path, which
produced `getaddrinfo ENOTFOUND`; WorkBuddy's legacy SSE fallback then received
the expected HTTP 405 from the POST-only Streamable HTTP endpoint. Correcting
the local VPN TUN/DNS configuration restored native Streamable HTTP. This was an
environment issue, not a Plugin or production MCP failure.

## Final state

After lifecycle testing, SpringBrand was reinstalled and enabled. The
SpringBrand Marketplace remains configured for later updates, the Plugin MCP is
usable, and unrelated built-in Plugins remain unchanged.
