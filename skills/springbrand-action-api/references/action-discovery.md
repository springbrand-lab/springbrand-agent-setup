# Action discovery API reference

Exact MCP input and output contracts for Action discovery, plus discovery-intent
construction, candidate compatibility, and recovery semantics. Field names,
types, and bounds below are copied from the Gateway contract; never guess a
field. Read this reference before constructing any discovery request.

## Field-name trap: `normalized_intent`, not `normalizedIntent`

The Action match takes **snake_case** `normalized_intent`. The Platform
Plugin match takes **camelCase** `normalizedIntent`. Both skills share one
MCP entry, and the wrong casing for either is an invented field that a strict
object rejects or ignores. Never carry the field name across domains.

## `action_match_capabilities`

Send it once per user request with English capability keywords. Match is
keyword-based; it does not semantically interpret the complete user task.

### Input (strict object)

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `intent` | string | yes | 1–4000 characters after trimming. English capability keywords after translating the task and resolving aliases (see [Discovery intent construction](#discovery-intent-construction)). |
| `normalized_intent` | string | no | 1–1000 characters after trimming. The compact English catalogue label (see [Discovery intent construction](#discovery-intent-construction)). |
| `locale` | string | no | 2–35 characters after trimming. The detected locale of the request, for example `zh-CN` or `en`. |
| `observation` | object | no | Optional structured requirement context at the top level of the tool input, a sibling of the match fields (see [Structured requirement context](#structured-requirement-context-observation)). |

No other fields exist beyond the optional `observation`. In particular there
is no threshold, no keyword list, and no per-keyword field.

**Representative valid example** — the request `SpringBrand 用xhs有关的api给我查查人机恋最近一个月比较火的在讨论什么，总结`:

```json
{
  "intent": "Xiaohongshu note search",
  "normalized_intent": "Xiaohongshu Note Search",
  "locale": "zh-CN"
}
```

Both search fields identify the canonical platform, operation, and object.
The topic, time range, popularity requirement, and final summary remain in
`intent_spec` and task state. These search fields are not the eventual Action
input: inspect its exact contract before deciding how to supply or satisfy
those requirements. Do not claim that the Action supports date/popularity
filters merely because the discovery keywords match.

**Valid example** — the QA request `用 springbrand 帮我生成土豆番茄大战的漫画` after
removing the invocation wrapper and orchestration phrase:

```json
{
  "intent": "comic text to image",
  "normalized_intent": "Text to Image",
  "locale": "zh-CN"
}
```

**Invalid example 1** — a legacy Chinese request body without `normalized_intent`:

```json
{
  "intent": "生成土豆番茄大战的漫画",
  "locale": "zh-CN"
}
```

The Gateway accepts this body, but it reproduces the QA failure: the Chinese
intent alone matches nothing, the call returns a well-formed empty result,
and the run reports a false no-match. A body without an English
`normalized_intent` is **malformed for matching purposes** whenever the
intent is not English (see [Empty results](#empty-results)).

**Invalid example 2** — the brand word in the search form:

```json
{
  "intent": "生成土豆番茄大战的漫画",
  "normalized_intent": "springbrand comic image",
  "locale": "zh-CN"
}
```

Rejected policy-wise: `springbrand` occurs in nearly every catalogue entry,
so it inflates irrelevant candidates and buries the right one. Omit
SpringBrand when it merely names the invoking tool; business brands, explicit
suppliers, platforms, and model names remain meaningful constraints.

### Output

Discriminated on `outcome`. Unlike the snake_case input, the output fields
are camelCase:

- `matches_found` — `matchId` plus ordered `candidates[]` items.
- `no_match` — `matchId` plus an empty `candidates[]`. A valid answer for
  that phrasing — never a transport or schema error by itself.

Top-level `complete` says whether this query's retrieval pass ran to
completion. `complete: false` comes with a `sourceLimitation` (for example
`code: "upstream_mixed_result_truncated"`): the match limit was reached and
later candidates may exist — report the result as possibly incomplete.
`complete: true` says nothing about what a differently phrased query would
find; it is not proof that the catalogue lacks the capability.

Each item of `candidates[]`:

| Field | Type | Meaning |
| --- | --- | --- |
| `kind` | string | Always `api_service` on this path. |
| `apiServiceId` | string | The API service's exact ID. Keep it exact. |
| `actionId` | string | The executable Action's exact ID. Keep it exact. |
| `supplierId` | string | The supplier's exact ID. |
| `title` | string | Display title. |
| `summary` | string | Short summary. |
| `description` | string | Longer description. |
| `toolDescription` | string | What the service does, in the supplier's words. |
| `recommendedPrompt` | string | Example input showing the expected shape. |
| `access` | object | Access type, for example `{"type": "direct"}`. |
| `billing` | object | Billing type, for example `{"type": "metered_credits"}`. |
| `score` | number | 0–1. The service-returned relevance score. |
| `matchedOn` | string[] | The terms that matched. |

## Structured requirement context (`observation`)

`observation` is the Agent's **structured requirement context**: a compact,
structured statement of the user's task that travels with the discovery call
and links the discovery to the task it serves. Fill it whenever the tool's
declared input schema exposes `observation`, and build it strictly to the
schema below — it is a strict object, and invented fields fail the call.

On `action_match_capabilities`, `observation` sits at the top level of the
tool input, a sibling of `intent`, `normalized_intent`, and `locale`. On
`action_execute_capability`, `observation` is likewise a top-level tool
argument — a sibling of `name` and `body` — and never enters the Action
input `body`.

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

- `task_goal` states what the user wants done — the same task-level goal
  Step 1 restates — not the shortened search keywords. `normalized_intent` remains the
  compact catalogue label; `task_goal` carries the task behind it.
- `desired_output`, `inputs`, `constraints`, and `ambiguities` record only
  what the user expressed or what is genuinely open. Never add preferences
  the user did not state.
- `inputs` names material types only — "a text file", "a topic", "a date
  range" — never pasted content, chat transcripts, execution inputs or
  outputs, or credentials.

`task_id` lifecycle: generate a UUID for each independent user task and
reuse that same `task_id` for every discovery call serving the task; a new,
independent task gets a new UUID. Never substitute a user identity, an
account, or a session for it.

**Valid example** — the top-level `observation` argument for the XHS request
(the match fields themselves are unchanged from the example above):

```json
{
  "observation": {
    "schema_version": 1,
    "task_id": "3f8a1c2e-64b7-4c3a-9a2e-5b1d0f6e8a90",
    "intent_spec": {
      "task_goal": "搜索小红书最近一个月关于人机恋的热门笔记",
      "desired_output": "热门笔记列表及其讨论要点",
      "inputs": ["主题关键词"],
      "constraints": ["平台限定小红书", "时间范围最近一个月"],
      "ambiguities": ["热门的具体衡量标准未说明"]
    }
  }
}
```

### `discovery_id`: associating execution with its discovery

A successful Match that carried `observation` returns
`observation.discovery_id` — the discovery's own ID, generated per Match
call. Keep it with the task state. A genuine `no_match` is still a
successful Match and carries it; an error response keeps the existing error
contract and carries none. A Match sent without `observation` succeeds as
before and returns no discovery metadata.

When you later execute an Action that this discovery produced, pass the
discovery context on the execute call — top level, never inside the Action
input `body`:

```json
{
  "observation": {
    "schema_version": 1,
    "discovery_id": "9c2e5f40-1a83-4b6d-8e72-0c4f9a1d3b52",
    "api_service_id": "apiServiceId from the matched candidate"
  }
}
```

- `discovery_id` is required and must be the exact ID the Match returned.
  Without a discovery ID in hand, send no `observation` — never guess,
  reuse another task's, or invent one.
- `api_service_id` is the matched candidate's exact `apiServiceId`, when
  applicable.
- One discovery can precede several executions; each execution carries the
  same `discovery_id`.
- Status lookups (`action_get_execution`) take no `observation`, and a
  retry of the same execution reuses the same association.

## Candidate compatibility

The Match response already orders candidates by the service's own scoring.
Preserve that returned order when inspecting and presenting candidates.
Derive the user's explicit hard constraints, then validate every candidate
against:

1. supplier, only when explicitly requested;
2. platform/product;
3. operation, such as `search`, `comments`, `details`, or `profile`;
4. object or modality, such as `note`, `video`, `text to image`, or
   `image to video`.

Recommend the first candidate in the returned order that satisfies every
applicable hard constraint. This is compatibility filtering, not a new
ranking: do not invent a second score, recompute service-returned scores,
re-sort candidates, or merge another result set into the Match ranking.

For the representative XHS request, TikTok Search, X Search, generic keyword
tools, Xiaohongshu Profile, Comments, and Details violate at least one hard
constraint. `action.tikhub.xhs-search-notes` is the compatible Xiaohongshu
Note Search Action even if an incompatible candidate has a higher rank or
score. The same distinction applies to modalities: generating an image needs
text-to-image, editing an existing image needs image-to-image, and finding an
existing image needs search.

The following fixture pins the returned order and compatibility decision used
by the routing evaluation:

```json
{
  "fixture": "xhs_candidate_compatibility",
  "constraints": {"platform": "Xiaohongshu", "operation": "search", "object": "note"},
  "ordered_candidates": [
    {"title": "TikHub TikTok Search", "compatible": false},
    {"title": "TikHub Xiaohongshu Note Search", "actionId": "action.tikhub.xhs-search-notes", "compatible": true},
    {"title": "TikHub X Search", "compatible": false},
    {"title": "Apify Keyword Search Volume", "compatible": false},
    {"title": "TikHub Xiaohongshu User Profile", "compatible": false},
    {"title": "TikHub Xiaohongshu Note Comments", "compatible": false},
    {"title": "TikHub Xiaohongshu Note Details", "compatible": false}
  ]
}
```

## `action_list_capabilities`

List is the complete Action Inventory path. Use it directly for explicit
inventory browsing, or as the single bounded recovery described below.

### Input (strict object)

| Field | Type | Rules |
| --- | --- | --- |
| optional `cursor` | string | 1–2048 characters; use only the exact `next_cursor` from the preceding page. |
| optional `limit` | integer | 1–100; default 20. |

### Output

The response contains `capabilities[]`, integer `total`, boolean `complete`,
and nullable `next_cursor`. Each inventory entry carries the exact API
Service, Supplier, and Action IDs as `apiServiceId`, `supplierId`, and
`actionId`, plus these public catalogue text and order fields: `title`,
`summary`, `description`, `recommendedPrompt`, `supplierDisplayOrder`, and
`displayOrder`. Preserve every ID exactly.

### Bounded inventory recovery

Enter recovery only after a well-formed Match returns `no_match`, or after
none of its candidates satisfies every applicable hard constraint, and only
when the request gives enough supplier, platform, operation, or object signal
to inspect the inventory safely.

1. Call `action_list_capabilities({ limit: 100 })` once.
2. If `complete: false`, continue with `next_cursor` page by page, passing the
   same limit, until a compatible candidate is found or the inventory is
   complete.
3. Apply the same hard constraints to inventory entries. Preserve inventory
   order, do not invent relevance scores, and do not merge List entries into
   the Match ranking.
4. When an entry is compatible, call `action_get_capability` with the entry's
   exact `actionId` and verify the current full contract before proposing
   execution.
5. If complete traversal finds no compatible Action, report that honestly.

This is one recovery traversal, not a second keyword Match, and it does not
authorize execution. Never enter it for a malformed non-English Match body;
repair normalization and rematch once instead. A transport, OAuth, permission,
schema, or provider error is reported as the actual failure. A compatible
Match candidate, even in a `complete: false` result, continues directly to
exact Get. An existing exact Action or execution pointer is reused without
discovery.

## Discovery intent construction

1. Translate the complete user task into English, preserving its meaning.
   Resolve aliases, abbreviations, and non-English names using
   [action-aliases.md](action-aliases.md) before constructing either search
   field. The map defines canonical forms and ambiguity guards; it is a
   curated aid, not live catalogue metadata. Do not invent a supplier, model
   version, platform, operation, or input modality from an ambiguous alias.
2. Build `intent` from English capability keywords: explicit supplier when
   required, canonical platform/model, operation, and object/modality. Remove
   host/environment names, generic API-selection requests, articles,
   prepositions, and courtesy phrases that do not distinguish a capability.
   Preserve words inside canonical names: `Text to Image` and `Image to Video`
   keep `to`, and explicit model variants such as `Fast` or `Mini` stay intact.
3. Build `normalized_intent` as a compact catalogue label, preferably
   `[explicit supplier] + [canonical platform] + [object/modality] + [operation]`.
   Examples: `Xiaohongshu Note Search`, `X User Profile`, `Text to Image`,
   `Image to Video`. `TikHub Xiaohongshu Note Search` is appropriate only when
   TikHub is explicitly required. Emit one canonical form, not a list of
   synonyms or alternative queries. Both fields must use English keywords.
4. Keep the full task goal, user topic, time range, desired summary, material
   types, and explicit constraints in `intent_spec` and task state. Include
   a qualifier in search text only when it distinguishes the needed capability.
   Negations such as "not TikTok" are constraints for candidate evaluation,
   not search text that should accidentally match TikTok. Workflow directions
   such as "only search" still control the Agent, outside capability keywords.
5. Set `locale` to the user's original locale. English discovery keywords
   neither translate the requested output nor authorize a different output
   language. Keep unresolved requirements explicit instead of filling guesses.
6. Preserve hard compatibility checks and exact Get before execution. Keyword
   scores are not probabilities and cannot prove support for all task constraints.
   Build execution inputs from the selected Action's actual schema and full
   user task, never from the shortened discovery keyword string alone.

For the comic request, `comic text to image` identifies the capability; the
potato-and-tomato story stays in the task summary and later generation prompt.
The absence of an input image must not be rewritten as an image-to-image task.

## Empty results

Keep three outcomes distinct; never collapse one into another:

- **Malformed body** — an empty `candidates[]` from a body whose
  `normalized_intent` is missing or not English. This is a false negative
  waiting to be reported: fix the body per [Discovery intent
  construction](#discovery-intent-construction) and rematch **once**. Never
  tell the user nothing fits from a malformed body.
- **Genuine no-match** — an empty `candidates[]` from a well-formed body
  (English capability-keyword `intent`, canonical English `normalized_intent`, `locale`). It is a
  valid Match answer for that phrasing: proceed to bounded inventory recovery
  when the request carries enough hard-constraint signal. Report no fit only
  after that traversal is complete; otherwise explain that safe recovery lacks
  enough identifying signal.
- **Provider failure** — transport, OAuth, permission, or schema errors, or
  any failed call. Report the actual error as a failure. Never report a
  failure as "nothing fits", and never rematch a schema error with the same
  invalid body.

A rematch fixes the body; it never fans out over keyword variants. Exactly
one well-formed rematch is the ceiling for a suspicious empty result.
