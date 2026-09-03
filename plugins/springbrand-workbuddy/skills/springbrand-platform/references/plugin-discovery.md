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

Legacy **Plugin-only** semantic Match. Send it once per user request with the
complete task intent.

### Input (strict object)

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `intent` | string | yes | 1–4000 characters after trimming. The user's request, faithful and unchanged — never paraphrased, translated, or embellished. |
| `normalizedIntent` | string | no | 1–1000 characters after trimming. The English semantic search form of the intent (see [English keyword construction](#english-keyword-construction)). |
| `locale` | string | no | 2–35 characters after trimming. The detected locale of the request, for example `zh-CN` or `en`. |
| `limit` | integer | no | 1–8, default 5. |

No other fields exist. In particular there is no threshold, no keyword list,
and no per-keyword field.

**Valid example** — the QA request `用 springbrand 帮我做电子礼物`:

```json
{
  "intent": "用springbrand帮我做电子礼物",
  "normalizedIntent": "digital gift",
  "locale": "zh-CN",
  "limit": 5
}
```

**Invalid examples:**

```json
{
  "intent": "用springbrand帮我做电子礼物",
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

## `springbrand.plugins.list`

Browsing and lookup over real Plugins. Not a substitute for semantic Match.

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

For the semantic Match path:

- Keep `intent` faithful to the user's original request — that is the Gateway
  contract, and the Platform reads it as the phrase-level signal.
- Put the search representation in `normalizedIntent`: translate the intent to
  English and reduce it to one short English phrase or 1–3 English keywords
  (for example `digital gift`). The scorer weights title and tags highest, so
  a compact noun phrase matches best.
- Never include `springbrand` in `normalizedIntent`. The brand word occurs in
  nearly every title and creates false positives.
- Never send Chinese or other non-English search keywords in
  `normalizedIntent`. Unsupported languages are translated before matching;
  the scorer's term extraction cannot rely on them.
- Detect the request locale and send it in `locale`.

## One request per Match

Issue **exactly one** Match request per user request, with the complete task
intent. Never split the intent into several Match calls to try different
keywords, and never union, merge, or rerank the results of multiple calls.

Why one complete request wins:

- The scorer evaluates the combined fields of one body — the phrase signal
  from `intent` plus the term signals from `normalizedIntent` — in a single
  pass with one threshold and one ordering.
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
