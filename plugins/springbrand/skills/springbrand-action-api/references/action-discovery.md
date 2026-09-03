# Action discovery API reference

Exact MCP input and output contract for `action_match_capabilities`, plus the
English normalized-intent construction and the empty-result semantics. Field
names, types, and bounds below are copied from the Gateway contract; never
guess a field. Read this reference before constructing any match body.

## Field-name trap: `normalized_intent`, not `normalizedIntent`

The Action match takes **snake_case** `normalized_intent`. The Platform
Plugin match takes **camelCase** `normalizedIntent`. Both skills share one
MCP entry, and the wrong casing for either is an invented field that a strict
object rejects or ignores. Never carry the field name across domains.

## `action_match_capabilities`

Send it once per user request with the complete task intent.

### Input (strict object)

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `intent` | string | yes | 1–4000 characters after trimming. The user's request, faithful and unchanged — never paraphrased, translated, or embellished. |
| `normalized_intent` | string | no | 1–1000 characters after trimming. The English search form of the intent (see [English intent construction](#english-intent-construction)). |
| `locale` | string | no | 2–35 characters after trimming. The detected locale of the request, for example `zh-CN` or `en`. |

No other fields exist. In particular there is no threshold, no keyword list,
and no per-keyword field.

**Valid example** — the QA request `用 springbrand 帮我生成土豆番茄大战的漫画`:

```json
{
  "intent": "用springbrand帮我生成土豆番茄大战的漫画",
  "normalized_intent": "generate comic image from text",
  "locale": "zh-CN"
}
```

**Invalid example 1** — the same request without `normalized_intent`:

```json
{
  "intent": "用springbrand帮我生成土豆番茄大战的漫画",
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
  "intent": "用springbrand帮我生成土豆番茄大战的漫画",
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
| `score` | number | 0–1. The Platform's own relevance score. |
| `matchedOn` | string[] | The terms that matched. |

The Platform already orders results by its own scoring. **Preserve the
returned order exactly** — never rerank, never re-sort, never apply a second
threshold of your own. Before recommending the top candidate, check that its
action verb fits the user's goal: generating an image needs a text-to-image
service, editing an existing image needs image-to-image, and finding an
existing image needs a search service. A candidate whose `matchedOn` is only
the brand word or a generic noun (`image`, `text`) often fails this check —
say plainly why you recommend the one you do. This is presentation, not
reranking: the order stays as returned.

## English intent construction

For the match path:

- Keep `intent` faithful to the user's original request — that is the
  Gateway contract, and the scorer reads it as the phrase-level signal.
- Put the search representation in `normalized_intent`: translate the intent
  to English and reduce it to one verb-first English phrase or 1–3 English
  keywords naming the action and the object (for example
  `generate comic image from text`). Lead with what happens — generate,
  edit, transform, search, transcribe — not with the theme alone.
- Never include `springbrand` in `normalized_intent`. The brand word occurs
  in nearly every catalogue entry and creates false positives.
- Never send Chinese or other non-English search keywords in
  `normalized_intent`. The scorer's term extraction cannot rely on them.
- Detect the request locale and send it in `locale`.

## Empty results

Keep three outcomes distinct; never collapse one into another:

- **Malformed body** — an empty `candidates[]` from a body whose
  `normalized_intent` is missing or not English. This is a false negative
  waiting to be reported: fix the body per [English intent
  construction](#english-intent-construction) and rematch **once**. Never
  tell the user nothing fits from a malformed body.
- **Genuine no-match** — an empty `candidates[]` from a well-formed body
  (faithful `intent`, English `normalized_intent`, `locale`). It is a valid
  answer for that phrasing: report it honestly. `action_list_capabilities`
  stays browse-only; it does not become a fallback.
- **Provider failure** — transport, OAuth, permission, or schema errors, or
  any failed call. Report the actual error as a failure. Never report a
  failure as "nothing fits", and never rematch a schema error with the same
  invalid body.

A rematch fixes the body; it never fans out over keyword variants. Exactly
one well-formed rematch is the ceiling for a suspicious empty result.
