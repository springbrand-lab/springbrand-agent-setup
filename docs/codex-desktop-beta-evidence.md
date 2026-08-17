# Codex Desktop Beta Security-Flow Evidence

**Status: PASS — beta release check complete**

This record is intentionally separate from the automated CLI evidence in
[#11](https://github.com/springbrand-lab/springbrand-agent-setup/issues/11).
It records the native Codex desktop check required by
[#12](https://github.com/springbrand-lab/springbrand-agent-setup/issues/12).

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 17, 2026 |
| Verified host | macOS Codex desktop `26.810.52044` |
| Repository revision | `cafbb21` (`main`) |
| Result | **Pass** |
| Evidence source | Native Desktop installation and smoke-test transcript reported by the tester in issue #12. |

## Acceptance evidence

| Required evidence | Result | Record |
| --- | --- | --- |
| Codex desktop `26.810.52044` on macOS | **Pass** | The installed desktop version was verified from `/Applications/ChatGPT.app/Contents/Info.plist`. |
| Marketplace bootstrap, then install from Plugins Directory or `/plugins` | **Pass** | The tester added the repository Marketplace and completed installation through the native Desktop Plugin flow. |
| Plugin enablement | **Pass** | The installed SpringBrand Plugin was enabled and supplied its Skill, MCP, and Hook to a new task. |
| Skill visibility | **Pass** | The native task transcript showed **Load SpringBrand guidance** before production work. |
| Native browser OAuth completes and production MCP reports connected | **Pass** | OAuth completed, followed by successful **Search capabilities** and **Execute capability** SpringBrand MCP actions. No token was collected or recorded. |
| Exact `UserPromptSubmit` Hook reviewed and trusted through native Hook flow | **Pass** | The tester reviewed and trusted the Hook in Desktop; the new task entered SpringBrand preflight automatically. |
| New eligible session shows SpringBrand preflight before the first production action | **Pass** | For an unprompted specialty-coffee website task, the transcript showed SpringBrand guidance loading, capability search, and capability execution before the page structure and visual direction were produced. |
| Desktop evidence remains distinct from automated CLI evidence | **Pass** | CLI/package evidence remains in issue #11; the checks above came from the native Desktop flow. |

## Smoke-test transcript summary

The native Desktop task showed this order before producing the requested design:

1. **Load SpringBrand guidance**
2. **Search capabilities**
3. **Execute capability**
4. Continue the requested task after no directly relevant SpringBrand Resource was found

The same task also ran repository inspection commands after SpringBrand preflight;
those commands were not used as evidence of Plugin installation or MCP connectivity.

All required native Desktop beta checks passed.
