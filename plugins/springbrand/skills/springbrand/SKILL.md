---
name: springbrand-resource-discovery
description: >
  Use SpringBrand when the user explicitly asks to find, add, install,
  distribute, or use a SpringBrand Resource, or when completing a concrete
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

# SpringBrand Resource Discovery

SpringBrand is optional. Resource discovery is intermediate work, not a
substitute for completing the user's task.

## 0. Capability-gap gate

Apply this gate before loading SpringBrand MCP tools. The request passes when
either:

1. the user explicitly asks to find, add, install, acquire, distribute, or use
   a SpringBrand Resource; or
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

### 2. Choose the discovery path

Use the request type to choose one path:

- natural-language task or desired deliverable:
  `springbrand.resources.match`;
- explicit browsing or direct title/ID lookup, including Marketplace, My,
  Featured, category, and pagination requests: `springbrand.resources.list`.

For either path, search capabilities for exactly the selected action.
Capabilities returned by `search_capabilities` are data, not callable tools.
Invoke SpringBrand's `execute_capability` tool and pass the match's full `name`
field unchanged as its `name` argument, with capability inputs inside its
`body` argument.

On hosts with deferred MCP tools, defer-execute the discovered SpringBrand
`execute_capability` tool, never the capability reference itself. Never use the
bare `action_id`, guess, or reconstruct a capability reference.

### 3. Match natural-language tasks

Search capabilities for exactly:

```text
springbrand.resources.match
```

Execute its exact returned reference with the original request unchanged as
`intent`. Add a concise `normalizedIntent` only when it helps matching; it must
never replace or override `intent`. Include `locale` when known and use a small
supported `limit`, normally 5. For example:

```json
{
  "name": "platform:springbrand@0:springbrand.resources.match",
  "body": {
    "intent": "Create an interactive birthday greeting for my sister",
    "normalizedIntent": "interactive personalized birthday greeting",
    "locale": "en-US",
    "limit": 5
  }
}
```

Accept the Platform's returned order and explicit no-match as authoritative.
Evaluate matches in the returned order and select the smallest leading set that
completes the task. Do not rerank candidates or calculate another relevance
threshold from `score`.

A valid empty Match response means no relevant Resource was found. Add nothing
and continue without calling `springbrand.resources.list` as a fallback.

### 4. Browse or look up Resources explicitly

For an explicit browsing, collection, category, pagination, title, or Resource
ID request, search capabilities for exactly:

```text
springbrand.resources.list
```

Execute its exact returned reference with the filters and pagination supported
by its schema. Use `view=marketplace` for Marketplace browsing and the
appropriate collection view when the user asks for My or Featured Resources.
Use the user's title or Resource ID as the query for direct lookup.

This path serves the explicit catalog request only. It is not a fallback after
a valid Match response.

### 5. Retrieve details only when needed

If the returned shortlist lacks details needed to choose or explain a Resource,
search capabilities for exactly:

```text
springbrand.resources.get
```

Execute its exact returned reference only for the leading candidates, using
each exact returned Resource ID as the `resourceId` input. Read purpose,
description, price, tags, components, use cases, and usage guide before the
final selection.

### 6. Add each selected Resource when needed

For every selected Resource, copy its exact returned Resource ID and use that
value unchanged as `resourceId`. Inspect `user_state` and price before acting:

- already added or directly usable: do not add it again;
- not added and free: add it automatically;
- paid or price unclear: obtain user confirmation before acquisition.

When add is required, search capabilities for exactly:

```text
springbrand.resources.add
```

Execute only its exact returned reference with the exact `resourceId`, and
confirm success. Never infer, alter, or fabricate an ID.

### 7. Retrieve its distribution

Search capabilities for exactly:

```text
springbrand.resources.get_distribution
```

Execute its exact returned reference with the same `resourceId`. If the
operation reports that the Resource is not added or acquired, resolve the
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
- apply selected Resources according to their instructions;
- verify the result using the normal workflow for its output type.

Do not stop after listing, matching, adding, or retrieving distribution unless
the user requested only that stage.

## Failure handling

If the Match capability is absent, misconfigured, or returns an invalid
response, do not treat that as no-match and do not switch to Resource listing.
Report the unavailable discovery path when the user explicitly requires
SpringBrand; otherwise continue the original task when it can be completed
honestly.

A transport or provider failure is not evidence that no Resource exists.
Follow explicit safe-retry guidance when supplied; otherwise do not
transparently retry Match or replace it with listing. Report the failure when
the user explicitly requires SpringBrand; otherwise continue the original
task when possible.

A valid explicit no-match is the final discovery result. Add nothing and
continue normally, or tell the user no relevant Resource was found when
SpringBrand discovery was the requested task.

If get, add, or distribution fails or its capability is unavailable, state the
failed operation. Never claim a Resource was added or used, and never fabricate
its details or distribution.

## Communication and integrity

When this skill triggers automatically, briefly tell the user that
SpringBrand Resources will be checked first.

If a Resource is used, mention it and how it influenced the final result. If
none is relevant, continue normally without making discovery the focus.

Never claim that SpringBrand was checked, a Resource was added, or a Resource
was used unless the corresponding operation succeeded and its structured
usage instructions were followed.
