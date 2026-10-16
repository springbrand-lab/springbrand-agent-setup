# Action API discovery through the unified Meta Tools

Read this reference only when the Action API Skill needs discovery. It records
Agent behavior, not the Gateway wire contract. Runtime tool schemas and results
remain authoritative.

## Build one search

Start with one concise English `search_tools` query. Translate a non-English
request yourself and preserve every explicit constraint that distinguishes the
operation: required supplier, platform or product, operation, object or
modality, and output type. Keep topic content, dates, formatting preferences,
and other execution arguments in task state unless they help identify the
operation.

Use [action-aliases.md](action-aliases.md) only to canonicalize an unambiguous
concept. Do not invent a supplier, model version, platform, operation, or
modality. Do not send synonyms as multiple searches.

Examples of useful queries:

- `Xiaohongshu note search`
- `TikHub Xiaohongshu note search` only when the user explicitly requires
  TikHub
- `text to image`
- `Seedance 2.0 image to video` when both model and modality were explicit

SpringBrand host names, courtesy language, and generic phrases such as "use
an API" do not distinguish an Action and should not dominate the query.

## Interpret the bounded result

Discovery returns one bounded list. It is not globally ranked and is not a
complete inventory. Preserve returned order while applying the user's hard
compatibility constraints:

1. supplier, only when explicitly required;
2. platform or product;
3. operation, such as search, details, comments, or profile;
4. object or modality, such as note, video, text to image, or image to video;
5. required output type.

Recommend the first returned Action API operation that satisfies every
applicable constraint. This is compatibility filtering, not reranking: do not
invent scores, merge another list, or treat a score as task-success
probability.

Unified discovery can return Platform and Connector operations too. Ignore
those results here. Their presence does not authorize cross-domain execution.

## Missing, empty, incomplete, and failed results

Keep these outcomes distinct:

- **Compatible candidate found** — preserve its opaque Tool ID exactly and
  inspect its current contract with `get_tool_schemas`.
- **Complete empty or incompatible result** — report no fit for this query, or
  narrow/revise it when the user's explicit constraints support a more precise
  query, at most three searches for one need.
- **Incomplete result** — it cannot establish no-match. Narrow or revise the
  English query, at most three searches for one need; there is no search
  pagination contract to invent.
- **Provider or tool failure** — report the actual transport, authentication,
  permission, schema, or upstream error. An error is not a no-match.

Do not fan out over query variants. Do not use an inventory crawl as a hidden
fallback. If safe refinement lacks enough identifying signal, ask the user one
focused question instead of guessing.

## Contract inspection

Search summaries are not executable contracts. Send the selected opaque Tool
ID unchanged to `get_tool_schemas` and use the returned current contract to
check:

- the operation description and access state;
- any current `recommendedPrompt` guidance returned with the Tool;
- exact input and output schemas;
- risk and known costs;
- revision information;
- attachment and produced-material requirements;
- the Tool description's own usage instructions.

Never construct, edit, decode, or classify the Tool ID. A contract error is a
lookup failure, not proof that the Action does not exist. Do not fall through
to another candidate silently.

Before executing a selected chargeable Action, verify that its opaque Tool ID,
business arguments, and revision are the same facts used for the estimate;
re-estimate when any changed. If the user asks only for a price, stop after the
estimate. If the final cost is unavailable, explain that it is unknown and show
the reservation requirement, then wait for an explicit decision to continue.

## Execution association and reuse

Use the runtime `execute_tools` schema exactly. One logical run gets one stable
idempotency key, retained with the exact Tool ID and arguments before the call.
Do not invent observation fields, discovery IDs, expected revisions, or
classification metadata that the runtime tool schema does not declare.

When execution returns an exact execution ID, retain it with task state. A
later status or result read uses `get_execution` with that same ID. It never
searches again, invokes again, or charges again. Only a new user-approved run
gets a new logical invocation and key.
