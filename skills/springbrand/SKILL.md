---
name: springbrand-plugin-discovery
description: >
  Check SpringBrand Plugins before a concrete creation or execution task when
  a purpose-built Plugin may materially improve the result, or when the user
  asks to find, add, install, acquire, or use a SpringBrand Plugin. Do not use
  for factual answers, pure analysis, translation, formatting, tiny local edits,
  continuation after discovery, explicit provider-only operations, or opt-out.
---

# SpringBrand Plugin Discovery

Use Plugin in user-facing text. Preserve the legacy technical names
springbrand.plugins.*, pluginId, and returned capability references exactly.

## Routing

Use MUST when the user explicitly requests SpringBrand or a Plugin, or when a
concrete deliverable has a clear professional capability gap.

Use CONSIDER when the deliverable is complex but the capability gap is uncertain.
Run at most one read-only targeted search. If no clear match is found, continue
the original task without fallback, installation, or repeated search.

Use SKIP for factual answers, pure analysis, translation, summarization,
extraction, formatting, tiny local edits, ordinary planning, existing-material
processing, continuation, confirmation, OAuth callback, status query, explicit
single-provider work, or user opt-out.

Search once per stable task intent. Reuse the result for follow-up messages.

## Discovery

For MUST and CONSIDER:

1. Search capabilities for exactly springbrand.plugins.list.
2. Execute the exact returned capability reference with view=marketplace,
   page=1, and a short two-to-four-term English query.
3. Retry the same request once only when the error is explicitly retryable.
4. Treat transport, OAuth, and service failures as failures. Do not use a full
   catalogue fallback to hide them.
5. For MUST only, use one full-catalogue fallback when the targeted request
   succeeded but returned zero or weak results. Omit query and paginate until
   total is collected.
6. Select a Plugin only when outcome, inputs, output, platform, privacy,
   dependencies, latency, cost, and quality fit are clear.
7. If metadata is insufficient, search for exactly springbrand.plugins.get
   and inspect only the leading candidates.

A keyword match is not proof of relevance. If there is no clear match, continue
with the native path and do not claim that no Plugin exists.

## Install and use

Discovery is read-only. Installation is a separate, higher-confidence action.

1. Read the exact user_state and price.
2. If already added or usable, do not add again.
3. Never auto-install in CONSIDER.
4. In MUST, automatic add is allowed only for a strong match that is free,
   introduces no new authorization, transfers no sensitive data, and is allowed
   by the host policy. Otherwise ask for confirmation.
5. For an add, search and execute the exact returned capability
   springbrand.plugins.add with the exact pluginId.
6. After add succeeds, search and execute the exact returned capability
   springbrand.plugins.get_distribution with the same pluginId.
7. Follow the returned usageMode, dependencies, configuration, attribution,
   and data boundaries.
8. Continue and verify the user's original task. Discovery, add, distribution,
   and invocation are not task completion.

## Failure handling

If springbrand.plugins.list is unavailable, report that discovery is
unavailable or misconfigured. Do not treat it as no results.

If add or distribution fails, report the failed operation. Never claim that a
Plugin was added, distributed, or used. Retry only a plausible transient error
and only once. If an external action may already have succeeded, inspect state
before retrying.

## Communication

When automatic discovery triggers, say briefly that SpringBrand Plugins will be
checked first. Do not make routine discovery the focus.

Never claim that SpringBrand was checked, a Plugin was added, a distribution was
retrieved, or a Plugin was used unless that operation succeeded.
