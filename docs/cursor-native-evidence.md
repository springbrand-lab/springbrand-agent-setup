# Cursor GitHub Import Native Evidence

**Status: PASS**

This record covers the Cursor desktop Native Evidence required by issue
[#22](https://github.com/springbrand-lab/springbrand-agent-setup/issues/22).
It records native application behavior separately from repository schema checks.

## Run metadata

| Field | Value |
| --- | --- |
| Check date | August 18, 2026 |
| macOS | 14.1.2 (23B92) |
| Cursor | 3.16.17 (`CFBundleVersion` 3.16.17) |
| Marketplace source | `springbrand-lab/springbrand-agent-setup@tony/multi-host-planning-docs` |
| Imported revision | `4eaedf6995359d8f0c98d55eb2d1431cb154b7b7` |
| Package version | `1.2.0-beta.2` |
| Test profile | Existing local Cursor profile; unrelated configuration was retained and checked before and after the lifecycle run |

The Cursor Distribution Mirror is unchanged between the imported revision and
repository revision `c8a7e030e4b1024b01e100d94b3b6695d90bcd2b`.

## Acceptance evidence

| Required evidence | Result | Record |
| --- | --- | --- |
| Exact macOS and Cursor builds | **Pass** | macOS 14.1.2 (23B92), Cursor 3.16.17. |
| GitHub Marketplace import indexes exactly one SpringBrand Plugin | **Pass** | **Customize → Browse Marketplace → Add Marketplace → Import from GitHub** accepted the branch-qualified repository source and exposed one `springbrand` Plugin. |
| Canonical Skill, always-applied Rule, and MCP server visible | **Pass** | The installed Plugin exposed the mirrored Canonical Skill, `springbrand-preflight.mdc`, and the namespaced SpringBrand MCP server. Cursor logs recorded one enabled Plugin with zero load failures. |
| Fresh production OAuth without static credentials | **Pass** | The Plugin MCP entered `needsAuth`; native browser OAuth completed and the same namespaced server transitioned to `connected`. No API key or packaged credential was used. |
| Eligible routing before work and original-task preservation | **Pass** | The operator observed the always-applied preflight invoking SpringBrand discovery before production work, followed by completion of the original eligible task. |
| Ineligible behavior and bounded false triggers | **Pass** | The ineligible arithmetic control returned `4` without a SpringBrand Skill or MCP call. |
| Refresh/update behavior | **Pass** | Native Marketplace refresh completed without duplicating the Plugin or changing unrelated configuration. Because the package version remained `1.2.0-beta.2`, Cursor retained the existing imported revision as the current cached package. |
| Plugin removal and preservation | **Pass** | Uninstall removed the installed Plugin, active Skill, Rule, and MCP registration. Cursor's persisted installed-ID list was empty after removal. Unrelated Plugins and configuration remained available. |
| Full-restart behavior | **Pass** | Installation and OAuth became usable without an additional full restart. After uninstall, a full Cursor restart retained the uninstalled state. |

## Lifecycle cleanup result

Cursor intentionally retained the imported SpringBrand Marketplace and an
inactive local package cache after Plugin uninstall. The Marketplace therefore
continued to offer SpringBrand for one-click reinstallation without requiring
the GitHub URL again. This is Marketplace retention, not an installed or active
Plugin: after restart Cursor loaded zero SpringBrand Plugins and no active
SpringBrand MCP server.

OAuth credentials were not explicitly revoked during this Plugin-removal test.
No claim is made that uninstall deletes shared OAuth state.

## Observed non-blocking limitation

The SpringBrand Marketplace card did not display the packaged logo in Cursor
3.16.17. The Plugin manifest declares `logo: assets/springbrand-icon.svg`, and
Cursor copied that SVG into both its Marketplace checkout and Plugin cache, so
this did not indicate a missing package asset. Installation, component loading,
OAuth, routing, and removal were unaffected. Logo rendering is therefore
recorded as a host UI limitation rather than runtime failure.

## Supporting native observations

Cursor's local logs recorded the following lifecycle transitions:

1. One Marketplace Plugin loaded with zero failures.
2. `plugin-springbrand-springbrand` transitioned from `needsAuth` to `connected`.
3. Uninstall reloaded the Marketplace source with zero enabled Plugins and zero
   failures.
4. A later full application restart still had no installed SpringBrand Plugin.

Repository validators remain package checks only and are not used as substitutes
for the native evidence above.
