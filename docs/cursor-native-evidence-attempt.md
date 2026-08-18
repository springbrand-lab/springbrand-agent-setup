# Cursor GitHub Import Evidence Attempt

**Status: PENDING — awaiting operator native run**

This record is separate from automated package validation. It is the evidence
record for issue [#22](https://github.com/springbrand-lab/springbrand-agent-setup/issues/22).
It deliberately does not treat manifest validation as runtime success.

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 17, 2026 |
| Verified operating system | macOS 14.1.2 (23B92) |
| Verified host build | Cursor 1.7.39 (`arm64`) |
| Repository revision | `bf2a166` (`tony/multi-host-planning-docs`) |
| Package revision | `1.2.0-beta.2` |
| Result | **Pending** |
| Evidence source | Local machine inspection and repository validation only; no native Cursor UI transcript was captured. |

## Pending conditions

1. The installed Cursor build is `1.7.39`; this run did not establish that it
   exposes the required native Plugin Marketplace flow.
2. The available local UI automation service could not start, so the required
   clean-profile install, OAuth, routing, update, and removal actions could not
   be performed through Cursor's own UI.
3. No claim is made for a clean installation, production OAuth, routing-before-
   work, lifecycle cleanup, or preservation of unrelated configuration.

## Acceptance evidence

| Required evidence | Result | Record |
| --- | --- | --- |
| Exact macOS and Cursor builds | **Recorded** | macOS 14.1.2 (23B92), Cursor 1.7.39 arm64. |
| GitHub Marketplace import indexes exactly one SpringBrand Plugin | **Not run** | Requires Cursor desktop Marketplace UI on a clean profile. |
| Canonical Skill mirror, always-applied Rule, and MCP server visible | **Not run** | Requires post-install Cursor inspection. |
| Fresh native OAuth reaches production without static credentials | **Not run** | Requires native Cursor OAuth flow; no credentials are recorded here. |
| Eligible/ineligible routing-before-work behavior | **Not run** | Requires fresh Cursor tasks and transcript evidence. |
| Marketplace refresh/update and Plugin removal preserve unrelated configuration | **Not run** | Requires before/after snapshots from a disposable Cursor profile. |
| Full-restart requirement identified; schema validation not treated as runtime success | **Not run** | Repository validation is explicitly separated from runtime evidence, but restart behavior requires a native lifecycle run. |

## Static package checks (not native evidence)

The repository contains the expected self-contained Cursor Distribution Mirror:

- `.cursor-plugin/marketplace.json` registers one `springbrand` Plugin.
- `plugins/springbrand/.cursor-plugin/plugin.json` declares the SpringBrand Plugin.
- `plugins/springbrand/skills/springbrand/SKILL.md` mirrors the Canonical Skill.
- `plugins/springbrand/rules/springbrand-preflight.mdc` is the always-applied routing Rule.
- `plugins/springbrand/mcp.json` declares only `https://connector.springbrand.ai/mcp`.

These facts are package checks only and do not satisfy issue #22's Native
Evidence gate.

## Operator verification run

Repeat on a disposable macOS Cursor profile with a current Cursor build:

1. Record the exact macOS and Cursor builds.
2. Check for existing global SpringBrand Skills or MCP entries and report duplicates; do not remove them or their OAuth state without explicit user approval.
3. Use **Customize → Browse Marketplace → Add Marketplace → Import from GitHub**
   with this repository.
4. Capture the indexed Plugin count, installed components, OAuth browser flow,
   and refresh/update/removal behavior.
5. For an eligible task, prove preflight occurs before production work and the
   original task still completes. For ineligible tasks, prove preflight does not
   falsely trigger beyond the Rule's documented bounds and the original tasks
   remain unchanged.
6. Record whether a full Cursor restart is required at each lifecycle boundary.
7. Replace this record's pending status with **PASS** or **FAIL** after all rows
   above have native UI evidence.
