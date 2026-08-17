# Codex Desktop Beta Security-Flow Evidence

**Status: INCOMPLETE — not a beta release pass**

This record is intentionally separate from the automated CLI evidence in
[#11](https://github.com/springbrand-lab/springbrand-agent-setup/issues/11).
It records the native Codex desktop check required by [#12](https://github.com/springbrand-lab/springbrand-agent-setup/issues/12),
without treating CLI or static-file checks as proof of native desktop behavior.

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 17, 2026 |
| Verified host | macOS Codex desktop `26.810.52044` |
| Repository revision | `95145ea` (`codex/plan-codex-plugin-distribution`) |
| Result | **Incomplete** |
| Reason | Codex desktop was verified at the required version, but native UI control was unavailable in this execution, so its security flows could not be run or observed. |

## Acceptance evidence

| Required evidence | Result | Record |
| --- | --- | --- |
| Codex desktop `26.810.52044` on macOS | **Not run** | The required version was verified from `/Applications/ChatGPT.app/Contents/Info.plist`, but the manual desktop check did not run. |
| Marketplace bootstrap, then install from Plugins Directory or `/plugins` | **Not run** | Native Marketplace UI was not observed. |
| Plugin enablement | **Not run** | No native Plugin-enabled state was observed. |
| Skill visibility | **Not run** | No native Skill visibility state was observed. |
| Native browser OAuth completes and production MCP reports connected | **Not run** | No OAuth or MCP connection state was observed; no token was collected or recorded. |
| Exact `UserPromptSubmit` Hook reviewed and trusted through native Hook flow | **Not run** | The shipped Hook source is present at `hooks/user-prompt-submit`, but direct file inspection is not evidence of native Hook review or trust. |
| New eligible session shows SpringBrand preflight before the first production action | **Not run** | No new desktop session was available for the smoke task. |
| Incomplete OAuth, Hook review, Plugin enablement, Skill visibility, or smoke result recorded as incomplete | **Pass** | All unavailable native checks above are explicitly marked **Not run**; this document must not be used as a success claim. |
| Desktop evidence remains distinct from automated CLI evidence | **Pass** | CLI/package evidence remains in issue #11 and its workflow; this file contains only the desktop check record. |

## Re-run procedure

On a macOS host with Codex desktop `26.810.52044` installed:

1. Add this repository as the `springbrand` Marketplace in the native Codex UI.
2. Install `springbrand` from the Plugins Directory or `/plugins`.
3. Capture the native Plugin-enabled state and the bundled production MCP state after browser OAuth reports connected.
4. Open the native Hook review flow, inspect the exact `UserPromptSubmit` Hook, and explicitly trust it there. Do not edit trust state directly in a file.
5. Start a new session with an eligible smoke task and capture SpringBrand preflight before the first production action.
6. Replace each applicable **Not run** result with **Pass** or **Fail**, attach screenshots or native UI export references, and change the document status only if every required flow passes.

Until that rerun is completed, the Codex desktop beta check remains incomplete.
