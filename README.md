<div align="center">

<img src="./assets/springbrand-icon.png" width="96" alt="SpringBrand logo" />

# SpringBrand

**The AI agent capability marketplace — everything your AI agent needs to take action, all in one place.**

</div>

SpringBrand connects professional data sources, tools, and ready-made task workflows to the AI assistant you already use. You describe the outcome you want; your agent discovers and calls the right services through a single MCP entry — no extra accounts, API keys, or subscriptions to manage. Multiple providers, pay per call, one bill.

This repository ships the SpringBrand installer: five Canonical Skills plus one MCP entry per environment, packaged as native Plugins for Codex, Claude Code, Cursor, and WorkBuddy, with a Skill-plus-MCP fallback for any other agent.

## The problem it solves

Getting an agent to complete a real task today usually means finding separate tools, opening multiple accounts, paying for several subscriptions, configuring different APIs, and manually stitching data and workflow together. The tools exist, but they are scattered — the agent cannot reach the right capability at the right moment.

SpringBrand brings those capabilities into one place. The agent discovers, chooses, and combines what the task needs; you just say what you want done.

## What your agent can do

One MCP entry, three capability domains:

- **Platform** — create and publish artifacts, manage Plugins, and browse the Marketplace.
- **Action API** — call dynamic API services for tasks, for example:
  - **Market and SEO research** — Similarweb, Semrush, Ahrefs, DataForSEO for traffic, keywords, and search performance; Exa, Tavily, Perplexity, Firecrawl for source gathering.
  - **Social listening** — collect discussions and trending content from X, YouTube, TikTok, Instagram, Reddit, Pinterest, and 小红书.
  - **Creator discovery** — find KOL/KOC on Instagram, TikTok, and YouTube with WaveInflu, and draft outreach.
  - **Prospecting** — build company and contact lists with Apollo and People Data Labs.
  - **Content generation** — copy plus images and video via GPT Image, Seedream, Seedance, and Nano Banana, with ElevenLabs voiceover.
- **Connector** — work with third-party systems such as GitHub, within your authorized scope.

Not sure which domain fits? Ask `$ask-springbrand` — it recommends exactly one Domain Skill and stops.

**Example — SEO research without a four-figure tool stack.** Ahrefs- and Semrush-class subscriptions cost $1,000+/month and take time to learn. On SpringBrand the agent queries professional traffic databases per call — top tier $79 — comparing traffic, growth, and audience sources across products in one prompt. No SEO background required.

## Why teams pick it

- **Professional capabilities on demand** — single services or complete workflows, inside the assistant you already use.
- **Pay per call, one bill** — no per-vendor subscriptions or prepaids for occasional use; try and combine services cheaply.
- **Connected apps** — the agent works with data and features of the apps you authorize, so less switching and manual hand-off.
- **Scheduled recurring tasks** — define the task, frequency, and expected output once; the agent runs it and reports on schedule.
- **Learns your context** — the agent combines capabilities per task and applies your confirmed requirements and feedback to later work.

## Install in one prompt

Paste the matching prompt into your Agent (Claude Code, Codex, Cursor, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent). The Agent reads the guide and performs the installation.

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

### Requirements

Your Agent must support:

- Reading a remote URL and writing files to your user-level Skill directory.
- Remote **Streamable HTTP** MCP servers with the selected release credential
  contract, including a safe Bearer credential mechanism for development.

If either is missing, `INSTALL.md` tells the Agent to stop and report the limitation. Some desktop Agents can only add MCP servers through their UI; in that case the Agent will give you the exact values to enter by hand.

## What gets installed

- **Codex Plugin** — the five Canonical Skills, the single production MCP declaration, and a static preflight Hook for supported macOS Codex hosts.
- **Claude Code Plugin** — the same five Skills, one native OAuth-backed production MCP entry, and a static preflight Hook for Claude Code CLI and the Claude Desktop Code tab; see [`INSTALL.claude.md`](./INSTALL.claude.md).
- **Cursor Plugin** — generated, verified Distribution Mirrors of all five Skills with one native OAuth-backed production MCP entry and an always-applied preflight Rule for Cursor desktop; see [`INSTALL.cursor.md`](./INSTALL.cursor.md).
- **WorkBuddy Plugin** — installed through the bundled WorkBuddy CLI from an immutable published R2 release; **Add Marketplace** remains the manual fallback; see [`INSTALL.workbuddy.md`](./INSTALL.workbuddy.md).
- **SpringBrand Dev Plugin (prerelease)** — the five Skills and a single `springbrand-dev` MCP entry for internal testing against `https://devconnector.springbrand.ai/mcp`; see [`INSTALL.dev.md`](./INSTALL.dev.md).
- **Skill-plus-MCP fallback** — the five user-level Skills and the single remote MCP entry for unsupported hosts.

Each Plugin ships the same five Canonical Skills:

| Skill | Role |
| --- | --- |
| `springbrand-gtm` | GTM business entry; hands off to one Domain Skill |
| `ask-springbrand` | Ask SpringBrand — non-executing Capability Guide |
| `springbrand-platform` | Platform — create/publish artifacts, Plugin lifecycle |
| `springbrand-action-api` | Action API — dynamic API service execution |
| `springbrand-connector` | Connector — authorized third-party systems |

## Safety

- The installer never stores or prints API keys, OAuth tokens, Authorization
  headers, Provider Credentials, or raw upstream responses. No credentials or
  tokens are placed in Skill files, repository content, URLs, logs, errors, or
  final reports.
- The production MCP URL is fixed at `https://connector.springbrand.ai/mcp`; the development MCP URL is fixed at `https://devconnector.springbrand.ai/mcp`.
- Existing MCP configuration is preserved. The manual dev fallback merges only the `springbrand-dev` entry; native Plugin lifecycle operations remove only their own bundled components.
- The installer does not execute any external third-party scripts.

## Updating

Use each host's native Marketplace update flow for Plugins. For the manual fallback, send the same prompt again; `INSTALL.md` / `INSTALL.dev.md` updates the existing entries rather than adding duplicates.

## For maintainers

`INSTALL.md` and `INSTALL.dev.md` are the core product: they are written to be
read and executed by an Agent. Skill sources live in `skills/<machine-name>/SKILL.md`
and are fetched by the Agent during installation.

```
springbrand-agent-setup/
├── README.md                          # this file
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

Each Canonical Skill declares the package release in YAML `metadata.version`.
`VERSION` is the source of truth: production versions have no `-dev.N` marker;
development releases include it. Keep `name` lowercase and stable across both
channels. This identifies the installed Skill release, not the MCP server version.

Production synchronization runs automatically on same-repository pull requests
targeting `main`. After the release author updates `VERSION` and the package
manifests, CI stamps the Canonical Skills, updates Cursor/WorkBuddy Distribution
Mirrors, and commits generated changes to the PR branch, then dispatches
validation for that commit. Merge the reviewed PR and create the production tag
from the synchronized commit. The workflow never pushes to protected `main`
directly or rewrites existing tags. Development releases synchronize in
`build_dev_variant.py --version ...`; for local previews or forks:

```sh
python3 scripts/sync_skill_versions.py [--check]
python3 tests/validate_plugin.py
```

CI rejects mismatched versions or mirrors on main, tags, and validation dispatches.
Version metadata does not itself check remote releases or update an installed
Skill; upgrades use the documented installation flow for the intended channel.

### Migration from a Legacy Plugin Release

A Legacy Plugin Release — an already-installed SpringBrand Plugin version that uses a single `springbrand` MCP entry at `https://connector.springbrand.ai/mcp` with the Gateway's legacy mixed contract (unprefixed tool names) — continues to work until the owner's production release switches the `/mcp` slot to the unified endpoint (Gateway ADR-0014; retirement is Gateway Issue 12, owner-controlled). Upgrading to the current single-entry Plugin with domain-prefixed tools is voluntary — there is no automatic sunset.

### Future: deterministic installer

A programmatic installer (`npx @springbrand/setup@latest`) is planned as a deterministic alternative for environments where prompt-based installation is unreliable. It is not required for the current flow.
