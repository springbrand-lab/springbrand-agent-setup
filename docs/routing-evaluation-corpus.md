# Cross-Host Routing Evaluation Corpus

Use this corpus against the same immutable development Plugin version on every
Surface. Record every run, including failures. Do not score MCP transport or
provider failures as routing false positives.

## Scoring

- **Notice recall:** eligible prompts that load the Canonical Skill.
- **Notice precision:** Skill loads that were eligible.
- **Match precision:** Match results that satisfy the prompt's hard constraints.
- **First-action ordering:** eligible prompts that load the Skill before
  task-specific planning or production.
- **Duplicate Match rate:** follow-ups that incorrectly run Match again.
- **Match latency:** P50/P95 for the Match call, recorded separately from routing.
- **Original-task completion:** requested outcomes completed after routing.

Establish a cross-Host baseline before setting thresholds. Keep routing,
transport, Match quality, and task completion as separate verdicts.

## FIT: Match once

1. `帮我做一份可以分享的电子礼物。`
2. `帮我制作一个人机恋主题的 DIY 互动体验。`
3. `帮我生成一组专业产品宣传图片。`
4. `制作一个可部署的互动品牌网站。`
5. `把这些跨服务步骤做成一个长期运行的自动化。`
6. `找一个 SpringBrand Plugin 完成这个任务。`

Expected: the Notice loads the Skill before planning or production. The Skill
runs `springbrand.catalog.match` once with the faithful intent and `limit: 5`,
then preserves Platform order and branches on `kind`: `plugin` candidates use
the Plugin lifecycle, `api_service` candidates bypass it and go directly to
exact `action_id` → `action:springbrand@0:<actionId>` lookup →
`execute_capability`.

## NO_FIT: successful no_match

Use plausible Plugin-shaped creation or execution tasks for which the current
dev Marketplace has no matching supply.

Expected: Match runs once, returns `no_match`, and the Agent continues natively.
It must not call List, scan the catalogue, add a Plugin, or report an error.

## SKIP: no SpringBrand calls

1. `总结这份文档。`
2. `把我提供的内容翻译成英文。`
3. `分析这些现有数据并列出三个结论。`
4. `解释这段已有代码。`
5. `修复这个函数里的小语法错误。`
6. `帮我写一个普通 Python 排序函数。`
7. `规划一个网站，但现在不要制作。`
8. `只使用 GitHub 完成这个操作。`
9. `2+2。`

Expected: no Skill load, no capability search, no Marketplace call, and the
original task completes directly.

## DIRECT: explicit Plugin

1. `使用 Plugin ID res-example 完成这个任务。`
2. `查看并使用刚才给你的 SpringBrand Plugin。`

Expected: inspect the resolvable Plugin directly. Do not Match first.

## REUSE: follow-up state

After one successful Match, continue with:

1. `就用第一个。`
2. `继续添加它。`
3. `完成授权后继续。`
4. `查看刚才的执行状态。`
5. `继续刚才那个 Action。`

Expected: load the Skill and reuse the existing `match_id`, Plugin ID,
distribution, authorization, idempotency, or execution state. Do not Match
again unless the desired outcome changed or the user requested refresh.

## BROWSE: List only

1. `打开 SpringBrand Marketplace。`
2. `查看 Featured Plugins。`
3. `显示下一页。`
4. `浏览图片分类。`
5. `按标题查找这个 Plugin。`

Expected: use `springbrand.plugins.list`; do not Match.

## FAILURE: distinct from no_match

For an eligible prompt, exercise Match capability missing, OAuth failure,
retryable transport failure, and service failure:

1. retry the same Match once only when explicitly retryable;
2. never enter a List fallback;
3. report the actual failure when SpringBrand was explicitly requested;
4. for automatic discovery, state briefly that discovery is unavailable and
   continue the original task after the bounded retry;
5. record the failure separately from `no_match` and routing verdicts.

## Gateway Action continuation

For a matched Plugin whose Distribution contains `kind: action` with
`usageMode: gateway_action`, verify:

- exact Action capability reference and schemas are used;
- `risk: high` is disclosed and Host policy is followed;
- retries preserve the original reference, body, and idempotency key;
- `running` polls `get_execution` before completion is claimed;
- `outcome_unknown` never retries automatically;
- `insufficient_credits` reports `recovery.action: add_credits` and requires a
  new Action invocation after Credits are added;
- incomplete Action sources and lookup Tool Errors are not forged into terminal
  execution states.

## Required evidence fields

- Surface and application build;
- Plugin version and Git ref;
- clean/update install state and OAuth state;
- prompt and expected route: FIT, NO_FIT, SKIP, DIRECT, REUSE, BROWSE, FAILURE;
- first loaded Skill or first production action;
- SpringBrand tool calls and arguments;
- Match ID, outcome, Platform order, and duplicate-Match verdict;
- original-task completion;
- routing, transport, Match quality, and Action execution verdicts recorded
  separately.
