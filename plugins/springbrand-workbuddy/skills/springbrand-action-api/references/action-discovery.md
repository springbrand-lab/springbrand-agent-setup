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

Send it once per user request with a faithful, catalogue-facing discovery
intent.

### Input (strict object)

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `intent` | string | yes | 1–4000 characters after trimming. A faithful task-level restatement cleaned for capability discovery (see [Discovery intent construction](#discovery-intent-construction)). |
| `normalized_intent` | string | no | 1–1000 characters after trimming. The compact English catalogue label (see [Discovery intent construction](#discovery-intent-construction)). |
| `locale` | string | no | 2–35 characters after trimming. The detected locale of the request, for example `zh-CN` or `en`. |

No other fields exist. In particular there is no threshold, no keyword list,
and no per-keyword field.

**Representative valid example** — the request `SpringBrand 用xhs有关的api给我查查人机恋最近一个月比较火的在讨论什么，总结`:

```json
{
  "intent": "用XHS搜索最近一个月关于人机恋的热门笔记",
  "normalized_intent": "Xiaohongshu Note Search",
  "locale": "zh-CN"
}
```

The cleaned `intent` keeps the platform, search operation, note object, topic,
time range, and popularity constraint. It removes only invocation scaffolding
and downstream summarization. The compact `normalized_intent` names the
catalogue capability rather than translating the whole task.

**Valid example** — the QA request `用 springbrand 帮我生成土豆番茄大战的漫画` after
removing the invocation wrapper and orchestration phrase:

```json
{
  "intent": "生成土豆番茄大战的漫画",
  "normalized_intent": "Text to Image",
  "locale": "zh-CN"
}
```

**Invalid example 1** — the same request without `normalized_intent`:

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
so it inflates irrelevant candidates and buries the right one. Never include
the brand word in `normalized_intent`.

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

This is one recovery traversal, not a second semantic Match, and it does not
authorize execution. Never enter it for a malformed non-English Match body;
repair normalization and rematch once instead. A transport, OAuth, permission,
schema, or provider error is reported as the actual failure. A compatible
Match candidate, even in a `complete: false` result, continues directly to
exact Get. An existing exact Action or execution pointer is reused without
discovery.

## Discovery intent construction

For the match path:

- Build `intent` as a faithful task-level restatement. Keep the requested
  platform, operation, object, user topic, and business constraints. Remove
  the `SpringBrand` invocation wrapper, generic API/service-selection wording,
  courtesy or orchestration phrases such as `帮我`, `给我`, and `查查`, and
  downstream work such as summarization or report formatting when it does not
  distinguish the external Action. Cleaning scaffolding must not broaden,
  narrow, or otherwise change the requested outcome.
- Build `normalized_intent` as a compact catalogue label, preferably
  `[explicit supplier] + [canonical platform] + [object/modality] + [operation]`.
  Examples include `Xiaohongshu Note Search`, `Xiaohongshu Note Comments`,
  `X User Profile`, `Text to Image`, and `Image to Video`. Include a supplier,
  as in `TikHub Xiaohongshu Note Search`, only when the user explicitly requires
  it.
- Never include `springbrand` in `normalized_intent`. The brand word occurs
  in nearly every catalogue entry and creates false positives.
- Omit the user topic, time range, final summarization, generic `api`, and
  filler such as `by keyword` unless a term genuinely distinguishes the
  capability.
- Never send Chinese or other non-English search keywords in
  `normalized_intent`. The scorer's term extraction cannot rely on them.
- Detect the request locale and send it in `locale`.

When the request uses an alias, abbreviation, alternative spelling, or
non-English name for a supplier, platform/product, model, object, or
operation, read [action-aliases.md](action-aliases.md) before building
`normalized_intent`. That inventory-audited map defines the canonical forms,
ambiguity guards, and maintenance boundary for this temporary Agent-side
fix. Apply one canonical form without adding unstated constraints.

## Empty results

Keep three outcomes distinct; never collapse one into another:

- **Malformed body** — an empty `candidates[]` from a body whose
  `normalized_intent` is missing or not English. This is a false negative
  waiting to be reported: fix the body per [Discovery intent
  construction](#discovery-intent-construction) and rematch **once**. Never
  tell the user nothing fits from a malformed body.
- **Genuine no-match** — an empty `candidates[]` from a well-formed body
  (cleaned faithful `intent`, English `normalized_intent`, `locale`). It is a
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
