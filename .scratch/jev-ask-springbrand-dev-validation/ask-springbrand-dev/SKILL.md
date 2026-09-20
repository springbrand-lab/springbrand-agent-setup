---
name: ask-springbrand-dev
description: >
  Development-only Ask SpringBrand router that uses the Gateway dev
  recommend_springbrand_domain experiment before handing off to one existing
  Domain Skill. Use only when the development SpringBrand package is selected.
metadata:
  version: "1.2.2-dev.1"
  environment: development
  gateway_tool: recommend_springbrand_domain
---

# Ask SpringBrand Dev

This is an experiment path for evaluating Jev-assisted Domain selection. It
keeps the production Ask SpringBrand guide unchanged. The Gateway dev
experiment owns the recommendation; the existing Domain Skills still own
discovery, current contract lookup, connection management, execution, and
result reads.

## Route one request

1. Read the current request and any in-flight state from the conversation. Keep
   the user's wording, execution IDs, connection names, artifact paths, and
   State Document location available for the handoff.
2. Call the development MCP tool `recommend_springbrand_domain` with exactly
   `{ "query": "<the user's current request>" }`. Send only the request text;
   do not send credentials, identity, grants, Provider data, or secrets.
3. Validate the response before using it. A usable response has `domain` set
   to exactly one of `platform`, `action_api`, `connector`, or `none`, a finite
   `confidence` from 0 through 1, and a boolean `no_match`.
4. For `platform`, hand off to `springbrand-platform`; for `action_api`, hand
   off to `springbrand-action-api`; for `connector`, hand off to
   `springbrand-connector`.
5. Preserve the request and state pointers in the handoff. State the selected
   Domain, why it fits, the unchanged task, and the pointers that can be
   reused. Then stop.

## Safe outcomes

- `domain=none` or `no_match=true` means there is no safe SpringBrand Domain
  basis. Continue ordinary work without a Domain Skill and do not call a
  business capability.
- A `jev_unavailable` or `jev_invalid_response` error is an experiment
  failure, not `none`. Use the production guide's local Domain table as the
  reversible fallback, label the result as a Jev fallback in the evaluation
  record, and follow its one-domain handoff and stop behavior.
- Treat confidence below `0.70` as low confidence. Do not silently authorize
  a Domain from a low-confidence result: ask the one allowed goal-level
  clarifying question when the request is not already settled by in-flight
  state; otherwise present the three-domain map and let the user choose.
- An explicit cross-Domain request still starts at the earliest required
  Domain according to the existing handoff rules. Record whether Jev agreed;
  never activate two Domain Skills in one turn.
- A response that fails validation is `jev_invalid_response`; never coerce it
  to `none`, infer a Domain from a Tool ID, or call discovery to compensate.

## Boundaries

This Skill calls only the development recommendation experiment. It does not
call `search_tools`, `get_tool_schemas`, `manage_connections`,
`execute_tools`, or `get_execution`, and it does not create Tool IDs or make
authorization decisions. The selected existing Domain Skill performs those
steps after handoff. The production `ask-springbrand` Skill, production MCP
entry, Gateway, and `sp-platform` remain outside this experiment.

## Evaluation record

For each labeled request, record the legacy/local Domain result, Jev Domain,
confidence, no-match flag, Gateway/Jev/end-to-end latency, handoff result, and
whether any discovery, schema lookup, connection operation, or execution
occurred before handoff. A `shadow` advisory field is evidence for comparison,
not permission to change production behavior.
