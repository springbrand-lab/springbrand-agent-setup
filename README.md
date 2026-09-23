<div align="center">

<img src="./assets/springbrand-icon.png" width="96" alt="SpringBrand logo" />

# SpringBrand

**The AI agent capability marketplace — everything your AI agent needs to take action, all in one place.**

</div>

English | [简体中文](./README.zh-CN.md)

SpringBrand connects professional data sources, tools, and ready-made workflows to the AI assistant you already use — so it doesn't just answer questions, it executes tasks and delivers results.

## The problem it solves

Completing one real task with an AI agent usually means finding tools, registering accounts, configuring APIs, and stitching workflows together by hand. SpringBrand puts those capabilities behind one entry: describe the outcome you want, and your agent chooses and calls the right tools to get it done.

- **One entry** — no switching between tools, accounts, and platforms.
- **Direct delivery** — the agent executes tasks and delivers results, not just advice.
- **Pay per call** — unified billing across tools; no stack of long-term subscriptions.
- **Recurring tasks** — schedule monitoring, research, and reporting to run on repeat.

## Examples

- Given a competitor's URL, analyze its traffic sources, acquisition pages, and search keywords.
- Monitor social media for real discussions about your product, brand, or competitors.
- Find companies and key contacts matching your ideal customer profile.
- Find fitting KOL/KOC and draft actionable collaboration and promotion plans.
- Combine capabilities to produce copy, images, video, and voiceover.

## Covered capabilities

SpringBrand covers social platforms including **X, TikTok, Instagram, YouTube, Reddit, Pinterest, and 小红书**, and can perform: social monitoring, trend tracking, content analysis, audience insight, competitor research, website traffic analysis, traffic source analysis, keyword research, top-page analysis, SEO analysis, prospecting, company and contact discovery, creator discovery, promotion planning, and copy, image, video, and voiceover generation.

These capabilities usually live in separate paid tools. SpringBrand provides capabilities similar to:

- **Traffic & SEO research:** Similarweb, Semrush, Ahrefs, DataForSEO
- **Search & web research:** Exa, Tavily, Perplexity, Firecrawl
- **Company & contact search:** Apollo, People Data Labs
- **Creator discovery:** WaveInflu
- **Content generation:** GPT Image, Seedream, Seedance, Nano Banana, ElevenLabs
- **Third-party systems:** GitHub and other connectors

These product names only illustrate capability scope; they do not imply direct integrations or partnerships.

Capabilities are organized into three domains — **Platform**, **Action API**, and **Connector**. When unsure which applies, ask `$ask-springbrand`; it recommends exactly one Domain Skill and stops.

## Install in one prompt

Paste this prompt into your AI Agent (Claude Code, Codex, Cursor, Copilot, Devin, Windsurf, WorkBuddy, or any compatible Agent); it reads the guide and performs the installation:

> Install or update SpringBrand Production by following https://plugin.springbrand.ai/INSTALL.md. Identify this Agent, use the matching Host guide, detect whether SpringBrand is already installed, refresh the existing Marketplace/Plugin in place when updating, prefer native OAuth, preserve existing configuration, and pause only for UI or OAuth steps I must complete.

Or add the hosted MCP server directly:

```sh
npx add-mcp 'https://connector.springbrand.ai/mcp'
```

### Development (testing only)

> Follow the official SpringBrand development installation guide to complete setup:
> https://plugin.springbrand.ai/INSTALL.dev.md
> Identify the target environment and Host first. Provide the development API key only at runtime through the Host's secure credential flow. Configure exactly one `springbrand-dev` entry, preserve unrelated configuration, run the authoritative identity check and configured MCP service health check, and report whether a restart or new session is required. Do not launch OAuth when the API key is valid; use the manual UI instructions and stop if the Host cannot represent Bearer credentials safely.

| | Production | Development |
| --- | --- | --- |
| Install guide | [`INSTALL.md`](./INSTALL.md) | [`INSTALL.dev.md`](./INSTALL.dev.md) |
| MCP entry name | `springbrand` | `springbrand-dev` |
| MCP URL | `https://connector.springbrand.ai/mcp` | `https://devconnector.springbrand.ai/mcp` |
| Authentication | Host-native OAuth | Runtime API key through the selected descriptor |
| Purpose | Everyday use | Testing only |

Install one coherent release rather than mixing Skill versions. Development is for testing only and should not be used as a production configuration.

## What this repository contains

The SpringBrand installer: five Canonical Skills and one MCP entry per environment, packaged as native Plugins for Codex, Claude Code, Cursor, and WorkBuddy. Other AI Agents connect through the documented Skill-plus-MCP fallback.

`INSTALL.md` and `INSTALL.dev.md` are written to be read and executed by an Agent. For maintainers: `VERSION` is the source of truth for releases; synchronize Skill versions with `python3 scripts/sync_skill_versions.py [--check]` and validate packages with `python3 tests/validate_plugin.py`.
