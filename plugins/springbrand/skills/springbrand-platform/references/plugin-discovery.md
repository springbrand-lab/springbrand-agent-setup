# Plugin discovery API reference

Exact MCP input and output contracts for the two Plugin discovery capabilities,
`springbrand.plugins.match` and `springbrand.plugins.list`, plus the boundary
against the mixed `springbrand.catalog.match` capability. Field names, types,
defaults, and bounds below are copied from the Gateway and Platform contracts
(`mcp-gateway/src/springbrand.ts`, `sp-platform/api/src/models/resource/index.ts`);
never guess a field. Read this reference before constructing any Match or List
body.

## Capability references and domain tools

Discovery runs through the two Platform domain tools on the unified MCP entry:

- `platform_list_capabilities` — returns the capability registry with each
  capability's exact reference.
- `platform_execute_capability` — runs one capability. It takes the exact
  reference in `name` and the capability's input object in `body`.

Capability references have the form `platform:springbrand@0:<capabilityId>`.
Resolve the exact reference from `platform_list_capabilities` or a verified
handoff — never infer, construct, edit, or synthesize one. Build `body`
strictly to the schema below: every required field present, no invented
fields. Unknown or extra fields make the whole call fail with
`invalid_arguments` (the input schemas are strict objects).

## `springbrand.plugins.match`

Legacy **Plugin-only** keyword Match. Send it once per user request with the
task-specific business keywords.

### Input (strict object)

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `intent` | string | yes | 1–4000 characters after trimming. Translate the complete request into English first, then extract a compact business-keyword phrase: required output, capability, and distinguishing qualifiers. Omit full sentences and unrelated terms. |
| `normalizedIntent` | string | no | 1–1000 characters after trimming. The same core English capability-and-output keywords, without generic padding (see [English keyword construction](#english-keyword-construction)). |
| `locale` | string | no | 2–35 characters after trimming. The detected locale of the request, for example `zh-CN` or `en`. |
| `limit` | integer | no | 1–8, default 5. |

No other fields exist in the Match body. In particular there is no threshold,
no keyword list, and no per-keyword field. Discovery context is never carried
in the body — it rides the separate top-level `observation` argument described
below.

**Valid example** — the QA request `用 springbrand 帮我做电子礼物`:

```json
{
  "intent": "digital gift",
  "normalizedIntent": "digital gift",
  "locale": "zh-CN",
  "limit": 5
}
```

**Invalid examples:**

```json
{
  "intent": "digital gift",
  "normalizedIntent": "电子礼物",
  "locale": "zh-CN"
}
```

Rejected policy-wise: `normalizedIntent` carries untranslated Chinese search
keywords. The Gateway would accept this body, but it reproduces the QA failure
where a non-English query matches nothing and the run reports a false
`no_match`.

```json
{
  "intent": "digital gift",
  "keyword": "gift",
  "limit": 20
}
```

Rejected by the Gateway (`invalid_arguments`): `keyword` is an invented field
(strict object), and `limit` 20 exceeds the maximum of 8.

### Output

Discriminated on `outcome`:

- `matches_found` — `match_id` plus 1–8 ordered `matches[]` items.
- `no_match` — `match_id` plus an empty `matches[]`. A genuine empty result:
  the Marketplace has nothing that fits. It is a success result, not an error.

`match_id` has the form `match_` followed by 32 hexadecimal characters.

Each item of `matches[]`:

| Field | Type | Meaning |
| --- | --- | --- |
| `plugin_id` | string | The Plugin's exact ID. Keep it exact. |
| `title` | string | Display title. |
| `summary` | string | Short summary. |
| `user_state` | string | `not_entitled`, `added`, or `entitled_not_added`. |
| `score` | number | 0–1. The Platform's own relevance score. |
| `matched_on` | string[] | The terms that matched (up to 20). |

The Platform already applies its fixed relevance threshold (0.3) and orders
results by score, then catalogue order, then ID. **Preserve the returned order
exactly** — never rerank, never re-sort, never apply a second threshold of
your own, and never drop or reword an ID.

## Structured requirement context (`observation`)

`platform_execute_capability` accepts an optional top-level `observation`
object — a sibling of `name` and `body`, never a field inside the Match body.
It carries the Agent's **structured requirement context**: a compact,
structured statement of the user's task that travels with the discovery call
and links the discovery to the task it serves. Fill it proactively whenever
the tool's declared input schema exposes `observation`, and build it strictly
to the schema below — it is a strict object, and invented fields fail the
call. The Gateway accepts `observation` for `springbrand.plugins.match`
only; on any other capability it is rejected with `invalid_arguments`.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `schema_version` | integer | yes, when `observation` is sent | Literal `1`. |
| `task_id` | string (UUID) | no | The ID of the user task this discovery serves. |
| `intent_spec` | object | no | The structured task summary (below). Strict object. |

`intent_spec` fields:

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `task_goal` | string | yes | 1–1000 characters after trimming. The user's task goal, faithfully restated. |
| `desired_output` | string | no | Up to 500 characters. What the finished result should be. |
| `inputs` | string[] | no | Up to 10 items, each 1–200 characters. Material **types** only. |
| `constraints` | string[] | no | Up to 10 items, each 1–200 characters. Constraints the user stated explicitly. |
| `ambiguities` | string[] | no | Up to 10 items, each 1–200 characters. What is genuinely undecided yet. |

Writing the fields:

- `task_goal` states what the user wants done — the same goal you would
  restate to them in plain language. It is the task itself, not the search
  keywords: `normalizedIntent` remains the compact English search form,
  while `task_goal` carries the task behind it.
- `desired_output`, `inputs`, `constraints`, and `ambiguities` record only
  what the user expressed or what is genuinely open. Never add preferences
  the user did not state.
- `inputs` names material types only — "chat messages", "photos", a
  "spreadsheet" — never pasted content, chat transcripts, execution inputs
  or outputs, or credentials.

`task_id` lifecycle: generate a UUID for each independent user task and
reuse that same `task_id` for every discovery call serving the task; a new,
independent task gets a new UUID. Never substitute a user identity, an
account, or a session for it.

**Valid example** — the top-level argument, alongside `name` and `body`, for
the QA request `用 springbrand 帮我做电子礼物`:

```json
{
  "observation": {
    "schema_version": 1,
    "task_id": "3f8a1c2e-64b7-4c3a-9a2e-5b1d0f6e8a90",
    "intent_spec": {
      "task_goal": "制作一份电子礼物",
      "ambiguities": ["收礼对象、礼物形式和可用素材尚未明确"]
    }
  }
}
```

**Invalid placement** — `observation` inside the Match body: the body schema
above is unchanged and strict, so an `observation` key there is an invented
field and the call fails with `invalid_arguments`. Discovery context never
enters `intent` or `normalizedIntent`.

### `discovery_id`: keeping the discovery context

A successful Match that carried `observation` returns
`observation.discovery_id` — the discovery's own ID, generated per Match
call. Keep it with the task state: it is the handle for associating later,
supported steps with the discovery they rest on. A genuine `no_match` is
still a successful Match and carries it; an error response keeps the
existing error contract and carries none. A Match sent without
`observation` succeeds as before and returns no discovery metadata.

Plugin discovery has no execution association: `add` and
`get_distribution` are not executions, take no `observation`, and never
claim one.

`observation` is processed separately from the search parameters: it changes
nothing about the one-Match rule, the body contract, the returned order, or
the results, and it never justifies an extra Match or List call. It is
structured requirement context — not a matching or ranking mechanism.

## `springbrand.plugins.list`

Browsing and lookup over real Plugins. Not a substitute for keyword Match.

### Input (strict object)

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `view` | string | no | One of `marketplace`, `featured`, `my`, `usable`. Default `usable`. |
| `query` | string | no | Up to 200 characters after trimming. English words from the title, summary, description, tags, or publisher name; substring-matched. |
| `category` | string | no | Up to 128 characters after trimming. A category ID. |
| `page` | integer | no | ≥ 1, default 1. |
| `pageSize` | integer | no | 1–100, default 30. |

No other fields exist.

**Valid example** — browse the full Plugin catalogue:

```json
{
  "view": "marketplace",
  "page": 1,
  "pageSize": 30
}
```

**Invalid examples:**

```json
{
  "view": "usable"
}
```

Rejected policy-wise for Plugin discovery: `usable` is the default, but it is
a **mixed view** — unlike `marketplace`, `my`, and `featured`, the Platform
does not exclude API-supplier resources from it, so it can return an empty or
mixed inventory. Do not use `view=usable` for Plugin discovery until its
semantics are corrected upstream.

```json
{
  "view": "marketplace",
  "page": 0,
  "pageSize": 500
}
```

Rejected by the Gateway (`invalid_arguments`): `page` must be ≥ 1 and
`pageSize` at most 100.

### Output

| Field | Type | Meaning |
| --- | --- | --- |
| `plugins[]` | array | Ordered items: `id`, `title`, `summary`, `usage_count` (integer), and `user_state` (string, present when the user is signed in). |
| `total` | integer | Total items across pages for this view and query. |
| `page` | integer | The returned page. |
| `page_size` | integer | The page size used. |

Preserve the returned order exactly. An empty `plugins[]` on a valid page is
an empty page, not proof that the catalogue is empty — check `total` and the
view before concluding anything.

### Views

- `marketplace` — the full Plugin catalogue, API-supplier resources excluded.
  Use for browse and pagination.
- `featured` — the curated view (`featured_order` set, catalogue order).
  Use only when the user asks for curated recommendations.
- `my` — the user's own added and entitled Plugins.
- `usable` — mixed with API-supplier resources; not for Plugin discovery
  (see above).

## Legacy Plugin Match vs mixed Catalog Match

Two different capabilities share one input schema; never alias one to the
other:

- **`springbrand.plugins.match`** — the legacy, Plugin-only Match this Skill
  uses. Returns `matches[]` with `plugin_id` and a top-level `user_state`.
- **`springbrand.catalog.match`** — a separate, mixed Catalog capability.
  Returns `candidates[]` where each candidate carries a `kind`:
  - `kind: "plugin"` — `plugin_id`, `title`, `summary`, `access` (with
    `user_state` **nested under `access`**), `score`, `matched_on`. Handle it
    in this Skill: continue the Plugin lifecycle from `plugin_id`.
  - `kind: "api_service"` — `api_service_id`, `supplier_id`, `action_id`,
    `title`, `summary`, `description`, `tool_description`,
    `recommended_prompt`, `access` (`type: "direct"`), `billing`
    (`type: "metered_credits"`), `score`, `matched_on`. An API service is
    Action API territory: perform the explicit Domain Transition to the
    `springbrand-action-api` Skill (announce it, preserve the task state and
    the exact IDs, end this workflow, hand back through Ask SpringBrand).
    Never execute an API-service candidate through Platform tools.

Both capabilities accept the same input object as `springbrand.plugins.match`
(the `intent` / `normalizedIntent` / `locale` / `limit` schema above), so the
English keyword construction contract applies to either. When a discovery
arrives from Catalog Match, route by `kind` as above; when this Skill matches,
it uses the legacy Plugin-only capability.

## English keyword construction

Match is keyword-based: do not assume semantic understanding, negation
handling, or a score calibrated to task success.

1. Translate the complete user request into English before extracting
   keywords. Do this while preparing one call; no separate translation tool
   or search is needed. `locale` stays the user's original locale.
2. Build `intent` as a compact keyword phrase. Prioritize the required output
   and capability, then add material or domain terms only when they distinguish
   the needed capability. For this presentation request, use
   `editable presentation slides`, not a full English instruction sentence.
3. Strip articles and prepositions (such as `a`, `an`, `the`, `to`, `for`,
   `from`), polite requests, environment names, and workflow instructions.
   Remove SpringBrand when it only names the tool. Preserve brands or named
   products when they are the business subject, such as a Shopify store.
   Avoid broad padding such as `product`, `content`, or `generation` when it
   adds no useful distinction; these can remain when central to the task.
4. Use the same core capability-and-output keywords in `normalizedIntent`,
   for example `editable presentation`. Do not expand into synonym lists,
   split into multiple requests, or search again with alternative keywords.
5. Keep full goals, material types, audience, length, language, and other
   stated constraints in `intent_spec`; they may use the user's language.
   Include a constraint in search text only when it distinguishes capabilities.
   Record exclusions there and assess candidates against them: `no video`
   must not become search terms that accidentally match video Plugins.
   Environment selection and "only search" remain workflow controls.
6. Add no unstated format, style, audience, or materials. In particular,
   "editable presentation" does not authorize assuming PPTX or PowerPoint.
   Put genuinely unresolved requirements in `ambiguities` when relevant.

Preserve returned order and exact IDs when presenting results. Explain which
requirements each candidate appears to support or miss based on its actual
description. A high keyword score is not proof of suitability; avoid expressing
it as a probability or claiming support the result does not establish.

### Complete call example

For the request "使用 SpringBrand dev，帮我找一个能把中文产品介绍制作成面向潜在客户、
10 页以内的可编辑演示文稿的 Plugin。这次只查找并展示候选。", select the dev MCP
entry and perform discovery only. After resolving the exact capability
reference from the registry, send the following shape. Generate a fresh task
UUID for an independent task; the UUID below is illustrative.

```json
{
  "name": "platform:springbrand@0:springbrand.plugins.match",
  "body": {
    "intent": "editable presentation slides",
    "normalizedIntent": "editable presentation",
    "locale": "zh-CN",
    "limit": 5
  },
  "observation": {
    "schema_version": 1,
    "task_id": "f48d3c69-5b82-4d91-a470-2ba143659fed",
    "intent_spec": {
      "task_goal": "将中文产品介绍制作成面向潜在客户的演示文稿",
      "desired_output": "10 页以内的可编辑演示文稿",
      "inputs": ["中文产品介绍"],
      "constraints": ["面向潜在客户", "不超过 10 页", "输出可编辑"],
      "ambiguities": ["演示文稿文件格式尚未指定"]
    }
  }
}
```

The English `intent` does not imply English output. Here, Chinese describes
the supplied material; the request does not explicitly choose the output
language or file format. Keep those facts distinct.

## One request per Match

Issue **exactly one** Match request per user request, with task-specific
keywords and structured requirement context when supported. Never split the intent into several Match calls to try different
keywords, and never union, merge, or rerank the results of multiple calls.

Why one request is required:

- Both search fields contribute to one keyword-matching request and one
  returned ordering. The structured requirement context is handled separately.
- Multiple calls add latency and return results under the same fixed threshold
  but different term sets, so their orders are not comparable.
- There are no defined union semantics: nothing specifies how to merge two
  ranked result sets, so any merge is an invented rerank.

A List call never compensates for a malformed Match body either: if the
request is vague, route directly to List per the decision tree in the Skill;
if the body is invalid, fix the body.

## Error semantics

Keep four outcomes distinct; never collapse one into another:

- **`matches_found`** — success with results. Preserve order and IDs.
- **`no_match`** — a successful call whose outcome is `no_match` with an empty
  `matches[]`. It is a valid answer ("nothing fits"), never a transport or
  schema error. Only after a genuine `no_match` may the one-time List
  fallback run.
- **Valid empty List page** — a succeeded List call with an empty `plugins[]`.
  Check `total`, `page`, and the view before interpreting it.
- **Provider failure** — `provider_unavailable`, OAuth or permission errors,
  `invalid_arguments`, or any other `status: "failed"` result. Report the
  actual error to the user as a failure. Never report a failure as "nothing
  fits", and never trigger the List fallback for one.
