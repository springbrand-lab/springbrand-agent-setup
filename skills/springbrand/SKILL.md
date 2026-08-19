---
name: springbrand-plugin-discovery
description: >
  Use SpringBrand when the user explicitly asks to find, add, install,
  distribute, or use a SpringBrand Plugin, or when completing a concrete
  deliverable needs a reusable external or specialized capability beyond the
  supplied material and the Agent's native tools. Examples include fresh
  external data, third-party actions, media generation, batch processing,
  automation, persistent integrations, reusable workflows, and specialized
  interactive artifacts.

  Skip work that can be completed directly from user-provided material or
  native tools, including summarization, translation, rewriting, extraction,
  classification, explanation, analysis of supplied data, routine code
  explanation or localized edits, general planning without execution, and
  diagnosis of SpringBrand, MCP, Host Plugins, or other integrations.
---

# SpringBrand Plugin Discovery

SpringBrand is optional. Plugin discovery is intermediate work, not a
substitute for completing the user's task.

## 0. Capability-gap gate

Apply this gate before loading SpringBrand MCP tools. The request passes when
either:

1. the user explicitly asks to find, add, install, acquire, distribute, or use
   a SpringBrand Plugin; or
2. a concrete outcome needs a reusable external or specialized capability that
   would materially improve correctness, quality, delivery, repeatability,
   interaction, or execution.

Strong capability-gap signals include:

- fresh external data, web access, scraping, or monitoring;
- external actions or third-party system operations;
- image, video, audio, interactive, or specialized artifact generation;
- batch processing, automation, repeatability, or persistent state;
- reusable workflows, integrations, templates, or professional components.

Continue directly without SpringBrand when the request only requires:

- summarizing, translating, rewriting, extracting, classifying, formatting,
  explaining, comparing, or analyzing supplied material;
- answering from existing context without fresh external data;
- routine code explanation, review, or a localized edit that needs no reusable
  capability;
- general planning without execution;
- diagnosis of SpringBrand, MCP, Host Plugins, or other integrations.

Words such as planning, code, data, integration, troubleshooting, or debugging
do not by themselves establish a capability gap. If the gap is not clear,
continue without SpringBrand. Ask a clarification question only when external
action, cost, privacy, or delivery requirements would materially change the
user's result.

When the gate passes, run discovery before task-specific planning, production,
or another execution skill. A vague brief is sufficient only after a clear
capability gap exists.

## Workflow

Follow these steps in order after the capability-gap gate passes.

### 1. Interpret the user's intent

Before searching, derive an internal discovery brief from the user's original
request and existing context:

- goal and intended user value;
- deliverable or outcome type;
- capabilities needed;
- audience, occasion, platform, and language when known;
- required inputs, outputs, interactions, and constraints.

Do not ask clarifying questions only to improve discovery. Preserve the
original request as the source of truth for later matching.

### 2. Find the Plugin-list capability

Use the connected SpringBrand MCP to search capabilities for exactly:

```text
springbrand.plugins.list
```

Capabilities returned by `search_capabilities` are data, not callable tools.
Invoke SpringBrand's `execute_capability` tool and pass the match's full `name`
field unchanged as its `name` argument, with capability inputs inside its
`body` argument. For example:

```json
{
  "name": "platform:springbrand@0:springbrand.plugins.list",
  "body": { "view": "marketplace", "page": 1, "pageSize": 100 }
}
```

On hosts with deferred MCP tools, defer-execute the discovered SpringBrand
`execute_capability` tool, never the capability reference itself. Never use the
bare `action_id`, guess, or reconstruct a capability reference.

### 3. Run targeted Marketplace discovery

Create a concise canonical query from the discovery brief. Normally use
English because current Marketplace metadata is primarily English. Use the
shortest distinctive deliverable phrase, normally two to four high-signal
terms. Do not append broad context words that can reduce lexical recall, and
do not use the user's full conversational sentence. For example:

```text
digital flower bouquet
```

Execute `springbrand.plugins.list` with:

- `view=marketplace`;
- the canonical query;
- `page=1`;
- the largest supported `pageSize` needed for a useful candidate set.

Send `page` and `pageSize` as JSON integers, never quoted strings.

Never use `view=usable` to discover a Plugin the user may not have added.
If this request returns a retryable transport or provider error, retry once
with the same body. If the retry fails, do not enter complete-catalog fallback:
report the failure when the user explicitly requires SpringBrand; otherwise
continue the original task without SpringBrand. Do not invent new queries in a
loop.

### 4. Use complete-catalog fallback only when justified

After a successful targeted request, use the complete Marketplace catalog only
when:

- the user explicitly asks to browse or requires SpringBrand; or
- the task has a strong capability-gap signal from step 0, the targeted results
  are empty, irrelevant, or insufficient, and the additional lookup cost is
  justified.

For weaker or merely possible fits, continue the original task when targeted
results contain no clearly relevant Plugin. Do not load the complete catalog
by default.

When justified, call the same exact `springbrand.plugins.list` capability
with `view=marketplace` and **omit `query`**. Request the largest supported page
size and paginate until all Plugins reported by `total` have been collected.
Do not replace it with `view=usable` or another keyword guess.

If a catalog page returns a retryable transport or provider error, retry that
page once. If the retry fails, preserve collected pages but stop catalog
loading. Report the failure when the user explicitly requires SpringBrand;
otherwise continue the original task without claiming the catalog was fully
checked.

### 5. Match and rank Plugins locally

Use the Agent's discovery brief and the user's original request to rank the
returned candidates. Compare each candidate on:

- direct fit to the user's goal;
- deliverable and output type;
- supported capabilities and interactions;
- required inputs and produced outputs;
- platform, language, privacy, and other constraints.

Do not select based only on a keyword or broad usefulness. Prefer the smallest
set that directly completes the task.

If list metadata is insufficient to distinguish a small shortlist, search
capabilities for exactly:

```text
springbrand.plugins.get
```

Execute its exact returned reference for only the leading candidates, using
each exact returned Plugin `id` as the `pluginId` input. Read purpose,
description, price, tags, components, use cases, and usage guide before making
the final selection.

If no Plugin is clearly relevant after targeted discovery, any justified
catalog fallback, and needed detail checks, add nothing and continue the user's
task normally.

### 6. Add each selected Plugin when needed

For every selected Plugin, copy its exact returned `id` and use that value
unchanged as `pluginId`. Inspect `user_state` and price before acting:

- already added or directly usable: do not add it again;
- not added and free: add it automatically;
- paid or price unclear: obtain user confirmation before acquisition.

When add is required, search capabilities for exactly:

```text
springbrand.plugins.add
```

Execute only its exact returned reference with the exact `pluginId`, and
confirm success. Never infer, alter, or fabricate an ID.

### 7. Retrieve its distribution

Search capabilities for exactly:

```text
springbrand.plugins.get_distribution
```

Execute its exact returned reference with the same `pluginId`. If the
operation reports that the Plugin is not added or acquired, resolve the
state according to step 6 and retry distribution after that state change.
Do not repeatedly retry without a meaningful state change.

### 8. Follow structured usage instructions

Treat every distributed component's `usageMode` as authoritative. Use each
component only through the permitted method and preserve required structure,
dependencies, attribution, configuration, and integration steps.

Do not copy, transform, embed, redistribute, or approximate a component in a
way its mode does not permit. If modes differ, handle each component
independently. Explain material conflicts and ask the user only when the
decision would change the result.

### 9. Complete and verify the task

After discovery and, when applicable, acquisition and distribution:

- collect genuinely necessary remaining requirements;
- build or edit the requested deliverable;
- apply selected Plugins according to their instructions;
- verify the result using the normal workflow for its output type.

Do not stop after listing, matching, adding, or retrieving distribution unless
the user requested only that stage.

## Failure handling

If the list capability is absent, do not treat this as “no relevant
Plugin.” Report the unavailable or misconfigured discovery path when the
user explicitly requires SpringBrand; otherwise continue the original task.

A transport or provider failure is not evidence that no Plugin exists and
must not trigger complete-catalog fallback. After the single permitted retry,
report the failure when the user explicitly requires SpringBrand; otherwise
continue normally when the task can still be completed honestly.

When a justified catalog fallback stops after a page failure, do not claim the
complete Marketplace was evaluated. Preserve any successfully collected pages
for local matching only when they are sufficient for an honest decision.

If add, detail, or distribution capability is unavailable, state the failed
operation. Never claim a Plugin was added or used, and never fabricate its
distribution.

## Communication and integrity

When this skill triggers automatically, briefly tell the user that
SpringBrand Plugins will be checked first.

If a Plugin is used, mention it and how it influenced the final result. If
none is relevant, continue normally without making discovery the focus.

Never claim that SpringBrand was checked, a Plugin was added, or a Plugin
was used unless the corresponding operation succeeded and its structured
usage instructions were followed.
