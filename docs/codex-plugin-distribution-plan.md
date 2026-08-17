# SpringBrand Agent Plugin distribution plan

**Status:** to-spec

**Primary repository:** `springbrand-agent-setup`

**First supported host:** Codex

**Production MCP:** `https://connector.springbrand.ai/mcp`

**v1 beta version:** `1.2.0-beta.1`

**Required surfaces:** Codex CLI `0.147.0+` and Codex desktop
`26.810.52044+` on macOS

## 1. Goal

Replace the current installation model, where an Agent reads `INSTALL.md` and
manually copies a Skill and edits MCP configuration, with a native Plugin
distribution that installs SpringBrand routing, execution guidance, and the
remote MCP connection as one versioned unit.

The v1 beta targets Codex on macOS and covers the Plugin package and native
installation flow in Phases 1 and 2. It establishes the mechanism expected to
improve SpringBrand Resource discovery recall without claiming the improvement
until the Phase 3 evaluation runs, and without moving host-specific
installation or routing behavior into `mcp-gateway`.

## 2. Why this repository changes

The existing repository distributes two independent items:

1. `skills/springbrand/SKILL.md`;
2. instructions for adding a remote MCP server.

Installation correctness therefore depends on an Agent correctly identifying
its host, locating user-level directories, merging configuration, restarting,
and later repeating the same process for updates. The MCP can be connected but
rarely selected when many Skills compete for attention.

A native Plugin packages three cooperating layers:

```text
UserPromptSubmit Hook
  -> makes the SpringBrand preflight rule visible before Skill routing
SpringBrand Resource Discovery Skill
  -> owns the detailed discovery, acquisition, distribution, and usage workflow
SpringBrand MCP
  -> owns authenticated capability search and execution
```

Plugin packaging improves installation and routing consistency. The Hook is
the part expected to improve first-action recall; the package format alone is
not treated as proof of a recall improvement.

## 3. Module ownership

### `springbrand-agent-setup`

This repository owns the Agent distribution module:

- host Plugin manifests and Marketplace metadata;
- the shared SpringBrand Skill;
- host lifecycle Hooks;
- bundled remote MCP declarations;
- install, update, migration, and uninstall instructions;
- Plugin versioning and release validation;
- client-side recall and ordering evaluation.

### `mcp-gateway`

The Gateway remains the authorization and execution module. It continues to
own OAuth, Connector Connections, Provider Credentials, Catalog, capability
search, execution, validation, and response redaction.

The Gateway must not own:

- Agent detection or Plugin installation;
- Codex or other host Hooks;
- local Agent configuration;
- Skill file distribution or Plugin updates.

No new Gateway tool is required for the Codex Plugin. The existing
`search_capabilities` and `execute_capability` interface remains the supported
MCP interface.

## 4. Codex Plugin v1 structure

The repository root is the Plugin root. This keeps the existing Skill in one
place and lets future host manifests reuse it without copying its content.

```text
springbrand-agent-setup/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .codex-plugin/
│   └── plugin.json
├── .mcp.json
├── hooks/
│   ├── hooks.json
│   └── user-prompt-submit
├── skills/
│   └── springbrand/
│       └── SKILL.md
├── docs/
│   └── codex-plugin-distribution-plan.md
├── INSTALL.md
├── INSTALL.dev.md
├── README.md
└── VERSION
```

Do not rename `skills/springbrand/` in v1. The Skill frontmatter provides its
runtime name, and moving the directory adds migration work without improving
behavior.

The Marketplace follows the proven AgentKey repository topology: the
Marketplace and Plugin share the repository root, and the `springbrand` entry
uses a local source path of `./` with authentication policy `ON_INSTALL`.

## 5. Runtime contract

### Hook

Use a synchronous `UserPromptSubmit` command Hook. It returns a short, static
`additionalContext` message that tells Codex to load and follow
`$springbrand-resource-discovery` first for eligible requests.

The Hook must:

- contain no network call;
- not read or store the user prompt;
- not read credentials or local files;
- not modify files or configuration;
- leave eligibility judgment to the model using conversation context;
- stay short enough not to materially consume context on every turn.

The Hook is a routing layer only. It must not duplicate the Resource search,
purchase, distribution, or usage workflow.

### Skill

`skills/springbrand/SKILL.md` is the single authoritative execution procedure.
Together with the canonical flow below, it is the implementation source of
truth. The internal demo is historical evaluation evidence, not an
implementation dependency. Do not ship a second SpringBrand Skill.

The canonical Resource discovery flow is:

1. resolve `springbrand.resources.list` through `search_capabilities`;
2. execute only the exact returned capability reference;
3. search Marketplace view with a concise, high-signal query;
4. use a bounded complete-catalog fallback when targeted matching is
   insufficient;
5. rank locally against the original user request;
6. add a selected Resource only when required and permitted;
7. retrieve `springbrand.resources.get_distribution`;
8. follow each component's structured `usageMode`;
9. complete and verify the user's original task.

### MCP declaration and OAuth

The Plugin bundles the existing remote MCP endpoint. It must not contain an
access token, refresh token, static `Authorization` header, OAuth client secret,
or Provider Credential.

Codex must use the Gateway's native OAuth discovery and browser authorization
flow. Marketplace authentication policy is `ON_INSTALL`. Installation is not
complete until the MCP is connected.

Keep the declaration at the Plugin root as `.mcp.json`, with only the remote
URL and native OAuth defaults. Do not copy AgentKey's older
`.codex-plugin/mcp.json` placement over the current OpenAI path contract.

### Hook trust

Plugin installation does not automatically trust a command Hook. Users review
and trust the exact Hook definition through the native Codex Hook flow. A
changed Hook hash requires review again.

Do not ship the demo's custom consent helper in v1. It depends on internal Codex
app-server behavior and writes user configuration that Codex already manages.

## 6. Installation and legacy migration

For Codex, `INSTALL.md` stops asking the Agent to copy a Skill or edit MCP
configuration. It becomes a host router whose beta path uses native commands:

```bash
codex plugin marketplace add springbrand-lab/springbrand-agent-setup --ref v1.2.0-beta.1
codex plugin add springbrand@springbrand
```

The first command is also the one-time Marketplace bootstrap for desktop. The
desktop path then installs SpringBrand from the Plugins Directory or `/plugins`.
OAuth completes through the native browser flow, and Hook review completes
through `/hooks`. These user security interactions are part of installation;
"deterministic" does not mean unattended.

Smoke-test the CLI path on Codex CLI `0.147.0` and the desktop path on Codex
desktop `26.810.52044` for macOS. Newer versions are supported; older versions,
the IDE extension, Linux, and Windows are outside the v1 beta compatibility
matrix.

The installation report must verify:

- the `springbrand` Plugin is installed and enabled;
- the bundled Skill is visible;
- the bundled MCP is connected after OAuth;
- the `UserPromptSubmit` Hook is trusted;
- a new test task enters SpringBrand preflight before production work.

Existing users may already have a manually installed
`springbrand-resource-discovery` Skill and a global `springbrand` MCP entry.
Keeping both copies can create duplicate instructions or tools. Migration must:

1. install and verify the Plugin first;
2. detect and report legacy entries;
3. request confirmation before removing or disabling them;
4. never remove unrelated Skills, MCP servers, or OAuth state.

Migration is an explicit, user-confirmed procedure in `INSTALL.md`; v1 beta
does not add a detection or cleanup script.

Update and uninstall also use native commands:

```bash
codex plugin marketplace upgrade springbrand
codex plugin remove springbrand@springbrand
```

Marketplace upgrade refreshes the installed Plugin cache. Do not document a
nonexistent `codex plugin update` command. Legacy migration must not remove
OAuth state; uninstall relies on native Plugin removal and adds no custom
credential cleanup.

Unsupported hosts retain the existing Skill plus MCP fallback until a native
Adapter exists for that host.

## 7. Version and release protocol

Keep `VERSION` as the canonical repository version. The same version must be
present in every versioned Plugin manifest. The first Plugin beta uses
`1.2.0-beta.1`; "Plugin v1" does not reset the repository's semantic version.

CI must perform the minimum release checks:

- parse all JSON files;
- validate the Codex Plugin manifest and Marketplace entry with repository
  invariants and a clean-runner Marketplace discover/install smoke test;
- assert `VERSION` equals `.codex-plugin/plugin.json` version;
- assert the MCP declaration contains only the production endpoint and no
  credential material;
- execute the Hook and validate its JSON output;
- verify the Hook executable bit;
- verify the Skill name referenced by the Hook exists;
- run the CLI smoke test on a clean macOS CI runner;
- record the desktop install, OAuth, Hook trust, and new-session smoke result as
  a manual beta release check.

The prerelease tag must not advance `stable`. After Phase 3 passes, the existing
release tag workflow may move `stable` to the corresponding final release.
Users may then track `stable` or pin a final tag.

Prefer Codex's native Marketplace and Plugin update mechanisms. Do not add a
network version check to every Skill invocation unless measured update failures
show that native updates are insufficient.

## 8. Recall evaluation (deferred from v1 beta)

The evaluation runner and JSONL corpora belong to Phase 3 and are not created
for the Phase 1-2 beta. The demo may inform later cases, but it is not their
authoritative source.

Static JSONL cases are test data, not proof. The evaluation runner must execute
real Codex tasks and inspect the event stream or transcript for ordering.

Compare these configurations with the same model, Codex version, prompt set,
and competing Skills:

1. MCP only;
2. current Skill plus MCP;
3. Plugin with Skill, MCP, and Hook.

Run the suite with representative competing-Skill counts, including at least
10 and 50. Add a 100-Skill case only when it reflects a real supported user
environment and does not make CI cost unreasonable.

Measure separately:

- eligible-request recall;
- whether the first task-producing action resolves
  `springbrand.resources.list`;
- negative-request false-trigger rate;
- OAuth and Hook installation success;
- Resource match success after the MCP was invoked;
- completion of the user's original task.

Initial release gates:

- eligible-request recall at least 90%;
- at least 25 percentage points above current Skill plus MCP baseline;
- first-action ordering correctness at least 90%;
- false-trigger rate at most 10%;
- OAuth and Hook installation success at least 95%;
- no material regression in original-task completion.

These thresholds may change only with recorded evaluation evidence.

## 9. Delivery phases

### Phase 1: Codex Plugin package

- add Codex manifest, Marketplace entry, MCP declaration, and static Hook;
- keep the existing Skill and canonical flow as the runtime authority;
- validate local installation, OAuth, Hook trust, and a new-session smoke task;
- keep Gateway tools and data model unchanged.

### Phase 2: deterministic Codex installation

- replace manual Codex construction in `INSTALL.md` with native Plugin commands;
- document update, uninstall, and legacy migration;
- automate only verification that native installation cannot provide;
- do not edit Codex configuration directly.

The native Codex CLI and desktop Plugin UI are the installers for this phase.
OAuth and Hook trust remain native user interactions. No custom wrapper,
detection script, or configuration writer is included in v1 beta.

### Phase 3: evaluation and stable release

- author the evaluation corpora and a real A/B runner;
- establish the current Skill plus MCP baseline;
- tune the Hook and Skill using false-positive and ordering evidence;
- evaluate the beta, then advance `stable` only after release gates pass.

### Phase 4: second native host Adapter (outside current spec)

Claude Code is the preferred next Adapter. It should reuse the same Skill and
remote MCP declaration while maintaining only the manifest and Hook behavior
that genuinely differs for Claude.

Do not add a shared host abstraction before the second Adapter exists.

### Phase 5: multi-host installer and detection (outside current spec)

After at least two native Adapters are working, consider a small installer that
detects supported hosts and invokes each host's native Plugin command. It must
not become a generic MCP configuration writer.

## 10. Gateway dependency

Before the Plugin reaches `stable`, create a separate Gateway change to align
its MCP `initialize.instructions` with the canonical Skill. Current Gateway
instructions and the canonical Skill disagree about query construction and
no-match fallback.

The aligned Gateway instructions should remain a concise compatibility policy
for clients without the Plugin. They must not become a copy of the full Skill.

No Gateway code or deployment is part of the v1 beta specification.

## 11. Explicit non-goals

The v1 beta does not include:

- a new Gateway routing engine or additional top-level MCP tools;
- embedding search without evidence that post-invocation matching is the
  bottleneck;
- Hook-side network classification;
- a custom Hook trust/configuration writer;
- telemetry or transmission of user prompts;
- a public development Plugin installed alongside production;
- all-Agent auto-detection;
- the Codex IDE extension, Linux, or Windows compatibility work;
- the Phase 3 evaluation runner or JSONL corpora;
- Claude or another host Adapter;
- a multi-Agent installer;
- Gateway code or deployment;
- copied AgentKey billing, provider, or discovery behavior;
- public ChatGPT Plugin Directory submission.

## 12. References

- [OpenAI: Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI: Codex Hooks](https://learn.chatgpt.com/docs/hooks)
- [AgentKey Codex Plugin change](https://github.com/chainbase-labs/Agentkey/pull/73)
- [AgentKey Marketplace](https://github.com/chainbase-labs/Agentkey/blob/main/.agents/plugins/marketplace.json)
- [AgentKey Codex manifest](https://github.com/chainbase-labs/Agentkey/blob/main/.codex-plugin/plugin.json)
- [AgentKey Codex MCP declaration](https://github.com/chainbase-labs/Agentkey/blob/main/.codex-plugin/mcp.json)
- SpringBrand Codex Plugin demo v0.1.6 (historical internal evaluation artifact,
  not an implementation dependency)
