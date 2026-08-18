# SpringBrand WorkBuddy Plugin

This guide installs the self-contained SpringBrand Host Adapter through WorkBuddy's native Plugin URL flow. Package validation is not Native Evidence; the verified runtime record is `docs/workbuddy-native-evidence.md`.

## Before installing

Check WorkBuddy for an existing global `springbrand` MCP entry or SpringBrand Skill. Report duplicates before continuing. Do not delete or replace a legacy SpringBrand entry, OAuth state, or unrelated configuration without explicit user approval.

## Install

1. In WorkBuddy, open **Plugins**, choose **Plugin URL**, and enter the GitHub archive URL for the release tag or branch being installed. The issue #23 development run used `https://github.com/springbrand-lab/springbrand-agent-setup/archive/refs/heads/tony/multi-host-planning-docs.zip`.
2. Install the single **SpringBrand** Plugin discovered from that source and enable it.
3. Authenticate the bundled `springbrand` entry instead of registering a second global MCP server. Complete WorkBuddy's native OAuth flow when prompted.
4. Start a fresh task and confirm a covered request routes through `springbrand-resource-discovery` before planning or production work.

Do not add a local MCP bridge, token, authorization header, client secret, or API key. The Plugin declares only `https://connector.springbrand.ai/mcp` and relies on WorkBuddy's native MCP OAuth.

## Hook trust

Installing and enabling the Plugin is WorkBuddy's accepted native trust decision for its executable Plugin-level `UserPromptSubmit` Hook. The shipped Hook is a static local script: it is deterministic, network-free, prompt-stateless, writes no prompt data, and only injects the instruction to follow the Canonical Skill when eligible.

## Update or remove

Use WorkBuddy's Plugins UI to update, disable, or uninstall SpringBrand, and to remove the Marketplace when it is no longer needed. Confirm the SpringBrand Skill, bundled MCP entry, and Hook update or disappear together while unrelated configuration remains unchanged. Do not remove legacy SpringBrand entries or OAuth state without explicit user approval.
