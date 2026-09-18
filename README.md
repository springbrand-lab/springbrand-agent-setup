# SpringBrand Agent Setup

Install SpringBrand Production through the matching native Host guide: WorkBuddy uses a published R2 release; Codex, Claude Code and Cursor retain GitHub `main`. Other Agents use the documented Skill-plus-MCP fallback.

This source tree ships five Canonical Skills and one MCP entry per environment.
The published WorkBuddy v1.2.1 package includes the same five Skills. The MCP
entry exposes five shared Meta Tools; the Domain Skills preserve business
boundaries through discovered operation contracts rather than registered tool
name prefixes:

| Skill | Role | MCP use |
| --- | --- | --- |
| `springbrand-gtm` | Substantive GTM business entry; hands off to one Domain Skill | none (never calls MCP) |
| `ask-springbrand` | Ask SpringBrand — non-executing Capability Guide | none (never calls MCP) |
| `springbrand-platform` | Platform — create/publish artifacts, Plugin lifecycle | shared discovery, schema, execution, and result tools |
| `springbrand-action-api` | Action API — dynamic API service execution | shared discovery, schema, execution, and result tools |
| `springbrand-connector` | Connector — authorized third-party systems | shared tools plus connection management |

## Quick start

SpringBrand has two environments. Pick the one you need and paste the matching prompt into your Agent (Cursor, Claude Code, Codex, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent).

### Production

> Install or update SpringBrand Production by following https://plugin.springbrand.ai/INSTALL.md. Identify this Agent, use the matching Host guide, detect whether SpringBrand is already installed, refresh the existing Marketplace/Plugin in place when updating, prefer native OAuth, preserve existing configuration, and pause only for UI or OAuth steps I must complete.

[`INSTALL.md`](./INSTALL.md) is the universal production protocol. It routes WorkBuddy to the published R2 release and other Hosts to their existing GitHub paths. Do not use the legacy `stable` branch or guess an unpublished version. The production MCP entry requires Host-native OAuth — one consent per Surface (a single authorization covers all three domains).

### Development

> Follow the official SpringBrand development installation guide to complete setup:
> https://github.com/springbrand-lab/springbrand-agent-setup/blob/v1.2.1-dev.2/INSTALL.dev.md
> Identify the target environment and Host first. Provide the development API key only at runtime through the Host's secure credential flow. Configure exactly one `springbrand-dev` entry, preserve unrelated configuration, run the authoritative identity check and configured MCP service health check, and report whether a restart or new session is required. Do not launch OAuth when the API key is valid; use the manual UI instructions and stop if the Host cannot represent Bearer credentials safely.

The native development Plugin is the immutable prerelease [`v1.2.1-dev.2`](https://github.com/springbrand-lab/springbrand-agent-setup/releases/tag/v1.2.1-dev.2). It is identified as `springbrand-dev`, displays as **SpringBrand Dev**, and bundles a single `springbrand-dev` MCP entry at `https://devconnector.springbrand.ai/mcp`. The selected development descriptor owns its native HTTP transport and runtime API-key credential representation.

Keep the full production and development Plugins enabled together only when the
Host can distinguish their entries and routing. Preserve the production entry
and all unrelated configuration during development installation or migration.
The manual fallback shares the same five Canonical Skills and adds or updates
only the separately named `springbrand-dev` MCP entry.

### Production vs Development

| | Production | Development |
| --- | --- | --- |
| Install guide | [`INSTALL.md`](./INSTALL.md) | [`INSTALL.dev.md`](./INSTALL.dev.md) |
| MCP entry name | `springbrand` | `springbrand-dev` |
| MCP URL | `https://connector.springbrand.ai/mcp` | `https://devconnector.springbrand.ai/mcp` |
| Authentication | Host-native OAuth | Runtime API key through the selected descriptor |
| Purpose | Everyday use | Testing only |
| Full Plugins can coexist | Host-dependent; routing must remain unambiguous | Host-dependent; routing must remain unambiguous |
| Manual Skill-plus-MCP fallback can coexist | Yes | Yes — it shares the same Skills and uses a separate MCP entry name |

The current source and latest dev release include `springbrand-gtm`, `ask-springbrand`, `springbrand-platform`, `springbrand-action-api`, and `springbrand-connector`; install one coherent release rather than mixing Skill versions. Development is for testing only and should not be used as a production configuration.

## What gets installed

- **Codex Plugin** — packages the five Canonical Skills, the single production MCP declaration, and static preflight Hook for supported macOS Codex hosts.
- **Claude Code Plugin** — packages the same five Skills, one native OAuth-backed production MCP entry, and static preflight Hook for Claude Code CLI and the Claude Desktop Code tab; see [`INSTALL.claude.md`](./INSTALL.claude.md).
- **Cursor Plugin** — packages generated, verified Distribution Mirrors of all five Skills with one native OAuth-backed production MCP entry and an always-applied preflight Rule for Cursor desktop; see [`INSTALL.cursor.md`](./INSTALL.cursor.md).
- **WorkBuddy Plugin** — a WorkBuddy Agent installs it through the bundled CLI; **Add Marketplace** remains the manual fallback; see [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md).
- **SpringBrand Dev Plugin (prerelease)** — packages five Skills including `springbrand-gtm` and the single `springbrand-dev` MCP entry for internal testing against `https://devconnector.springbrand.ai/mcp`; see [`INSTALL.dev.md`](./INSTALL.dev.md).
- **Skill-plus-MCP fallback** — the five user-level Skills and the single remote MCP entry for unsupported hosts.

The development API key is requested only at runtime and never stored in
repository files, Skill text, URLs, logs, errors, or reports. Production
authentication remains owned by the production release contract. No Plugin
contains reusable credentials or static authorization headers.

## Distribution channels

| Environment | Installation channel |
| --- | --- |
| Production — WorkBuddy | Published R2 release selected in `INSTALL.workbuddy.md` (currently pinned) |
| Production — other Hosts | `https://github.com/springbrand-lab/springbrand-agent-setup` (`main`) |
| Development | `springbrand-lab/springbrand-agent-setup@v1.2.1-dev.2` |

WorkBuddy installs an immutable production-tag package from R2, not a live mirror
of `main`; the current URL does not automatically advance. Other Hosts still
follow `main`. Release-to-R2 publication is currently manually triggered.
Development Plugins remain immutable dev tags and are never merged into `main`.

## Repository layout

Each Canonical Skill declares the package release in YAML `metadata.version`.
`VERSION` is the source of truth: production versions have no `-dev.N` marker;
development releases include it. Keep `name` lowercase and stable across both
channels. This identifies the installed Skill release, not the MCP server version.

Production synchronization runs automatically on same-repository pull requests
targeting `main`. After the release author updates `VERSION` and the package
manifests, CI stamps the Canonical Skills, updates Cursor/WorkBuddy Distribution
Mirrors, and commits generated changes to the PR branch. It then dispatches
validation for that new commit. Merge the reviewed PR and create the production
tag from the synchronized commit; no separate version-sync command is needed.
The workflow never pushes to protected `main` directly or rewrites existing tags.

Development releases synchronize automatically in
`build_dev_variant.py --version ...`. For local previews or fork contributions
(where CI cannot write to the source branch), the same operation is available:

```sh
python3 scripts/sync_skill_versions.py
python3 scripts/sync_skill_versions.py --check
python3 tests/validate_plugin.py
```

CI rejects mismatched versions or mirrors on main, tags, and validation dispatches.
Automatic PR synchronization uses job-scoped `contents: write` and `actions: write`
permissions; validation jobs remain read-only. Version metadata does not itself
check remote releases or update an installed Skill; upgrades still use the
documented installation flow for the intended channel.

```
springbrand-agent-setup/
├── README.md                          # this file — for humans
├── INSTALL.md                         # the production installation protocol — for Agents
├── INSTALL.dev.md                     # the development installation protocol — for Agents
├── VERSION                            # current release version
└── skills/
    ├── ask-springbrand/SKILL.md       # Ask SpringBrand — non-executing Capability Guide
    ├── springbrand-platform/SKILL.md  # Platform Domain Skill
    ├── springbrand-action-api/SKILL.md # Action API Domain Skill
    ├── springbrand-connector/SKILL.md # Connector Domain Skill
    └── springbrand-gtm/SKILL.md       # GTM Scenario Skill
```

`INSTALL.md` and `INSTALL.dev.md` are the core product. They are written to be read and executed by an Agent. The Skill sources live in `skills/<machine-name>/SKILL.md` and are fetched by the Agent during installation; the selected release determines the complete Canonical Skill set.

## Requirements

Your Agent must support:

- Reading a remote URL and writing files to your user-level Skill directory.
- Remote **Streamable HTTP** MCP servers with the selected release credential
  contract, including a safe Bearer credential mechanism for development.

If either is missing, `INSTALL.md` tells the Agent to stop and report the limitation. Some desktop Agents can only add MCP servers through their UI; in that case the Agent will give you the exact values to enter by hand.

## Safety

- The installer never stores or prints API keys, OAuth tokens, Authorization
  headers, Provider Credentials, or raw upstream responses.
- The production MCP URL is fixed at `https://connector.springbrand.ai/mcp`; the development MCP URL is fixed at `https://devconnector.springbrand.ai/mcp`.
- Existing MCP configuration is preserved. The manual dev fallback merges only the `springbrand-dev` entry; native Plugin lifecycle operations remove only their own bundled components.
- The installer does not execute any external third-party scripts.
- No credentials or tokens are placed in Skill files, repository content,
  URLs, logs, errors, or final reports.

## Updating

Use each host's native Marketplace update flow for Plugins. For the manual fallback, send the same prompt again; `INSTALL.md` / `INSTALL.dev.md` updates the existing entries rather than adding duplicates.

## Migration from a Legacy Plugin Release

A Legacy Plugin Release — an already-installed SpringBrand Plugin version that uses a single `springbrand` MCP entry at `https://connector.springbrand.ai/mcp` with the Gateway's legacy mixed contract (unprefixed tool names) — continues to work until the owner's production release switches the `/mcp` slot to the unified endpoint (Gateway ADR-0014; retirement is Gateway Issue 12, owner-controlled). Upgrading to the current single-entry Plugin with domain-prefixed tools is voluntary — there is no automatic sunset.

## Future: deterministic installer

A programmatic installer (`npx @springbrand/setup@latest`) is planned as a deterministic alternative for environments where prompt-based installation is unreliable. It is not required for the current flow.
