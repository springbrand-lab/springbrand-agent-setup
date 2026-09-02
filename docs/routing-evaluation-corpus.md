# Cross-Host Routing Evaluation Corpus (four-Skill model)

Use this corpus against the same immutable development Plugin version on every
Surface. Record every run, including failures. Do not score MCP transport or
provider failures as routing false positives.

This corpus evaluates the four-Skill routing model: **Ask SpringBrand** (the
non-executing Capability Guide) plus the three Domain Skills —
**Platform**, **Action API**, **Connector** — each bound to its own MCP Domain
Entry (`springbrand-platform`, `springbrand-action-api`,
`springbrand-connector`). It amends the scoring dimensions of #25; the retired
mixed MATCH / REUSE / BROWSE classes are absorbed into DOMAIN_SELECT,
TOOL_ISOLATION, and TRANSITION below.

## Surfaces

Run the same prompts verbatim on each Surface. Only the routing mechanism
differs; the expected route does not.

| Surface | Routing Notice | Skill invocation |
| --- | --- | --- |
| Claude CLI / Desktop | Hook (`user-prompt-submit`) | `/springbrand:ask-springbrand` and the Domain Skills |
| Codex | Hook (`user-prompt-submit`) | `$ask-springbrand` and the Domain Skills |
| Cursor | Rule (`alwaysApply: true`) | Skill list from the imported Plugin |
| WorkBuddy | Rule mirror | Skill list from the Marketplace mirror |

Per Surface, record: application build, Plugin version and Git ref, clean or
update install state, and OAuth state (per entry — up to three consents).

## Scoring (amends #25)

Seven dimensions. Keep routing, transport, discovery quality, and workflow
completion as separate verdicts, and establish the Skill-plus-MCP baseline
before setting thresholds.

1. **Router accuracy** — eligible or ambiguous prompts where Ask SpringBrand
   selects the correct domain, or spends its one clarifying question / presents
   the three-domain map instead of guessing. Gate: at least 90%, and at least
   25 percentage points above the baseline (carries #25's eligible-recall gate).
2. **Domain selection precision / recall** — recall: explicit-domain prompts
   that enter the correct Domain Skill directly. Precision: Domain Skill
   activations that were justified by the prompt. Gate: at least 90% each,
   in the style of #25's recall gate.
3. **Tool-isolation violations** — target **zero**: any call to another
   domain's entry tools, any cross-domain reference executed without
   `capability_domain_mismatch` handling, any merged search across entries, any
   automatic forwarding, any tool picked by name alone without naming the MCP
   entry.
4. **Workflow completion** — requested outcomes completed after routing, with
   no material regression against the baseline (carries #25's gate).
5. **Duplicate-discovery rate** — follow-ups that rematch, re-list, or
   re-search when a usable pointer (match, plugin, artifact, execution, or
   connection reference) was already in hand and still applies. Reuse beats
   rediscovery; rematch only when the intended outcome materially changes or
   the user asks to start fresh.
6. **First-action ordering** — eligible prompts where the correct Skill is
   loaded before task-specific planning or production. Gate: at least 90%.
7. **False-trigger rate** — SKIP-class prompts that load a Skill or touch an
   MCP entry. Gate: at most 10%.

The competing-domain inventory requirement carries over: the corpus must
include representative competing-domain prompt sets of at least 10 and at
least 50 (prompts where two or three domains plausibly compete — see
DOMAIN_SELECT and the inventory note there). Installation and OAuth success
(at least 95%) remains gated by #25 itself, not by this corpus.

## ROUTER: Ask SpringBrand picks the domain — or asks

The Routing Notice only makes the Skills visible; it does not determine fit or
call MCP. These prompts exercise Ask SpringBrand as the first responder.

First use (Scenario A):

1. `SpringBrand 能帮我做什么？`
2. `我是新用户，这个 Plugin 怎么用？`
3. `我想做点东西发布出去，该从哪里开始？`
4. `帮我看看有什么可用的服务能完成任务。`

Expected: Ask introduces the Plugin, presents the three-domain map in plain
language (**Platform** — create and publish artifacts, manage Plugins, and
browse the Marketplace; **Action API** — use dynamic API services for tasks;
**Connector** — work with third-party systems such as GitHub), recommends
exactly one Domain Skill, and stops. It never calls an MCP tool, never
discovers or executes a capability, and never activates more than one Domain
Skill.

Mid-workflow (Scenario B): after a Platform upload has succeeded but not been
published, continue with:

5. `我刚才做到哪一步了？下一步是什么？`

Expected: Ask reads the conversation and the State Document
(`springbrand-state.md`) as plain file access — never MCP — reports the
position ("uploaded but not published") and the next step, then hands off to
`springbrand-platform` and stops.

Ambiguous (clarifying budget):

6. `帮我把这个弄到线上去。`

Expected: the domain cannot be selected safely. Ask asks at most **one**
clarifying question about the goal ("publish something you have made, or have
a service do a task for you?"); if the answer still does not settle it, Ask
presents the three-domain map and lets the user choose. It never guesses its
way into execution.

Handoff contract (scored on every ROUTER case): the handoff names **the
selected domain**, gives **a one-line reason**, restates **the task**, and
lists **known state pointers** (or "none yet") — then names exactly one Domain
Skill and stops.

## DOMAIN_SELECT: explicit domain requests enter the correct Skill

The prompt names the domain or unambiguously matches one domain's triggers.
The correct Domain Skill is entered directly — no Ask detour, no wrong Skill.

Platform (artifact and Plugin lifecycle):

1. `帮我把这份笔记做成页面并发布。`
2. `把我的作品上传到 SpringBrand。`
3. `找一个能画图表的 SpringBrand Plugin。`
4. `打开 SpringBrand Marketplace 看看 Featured Plugins。`
5. `把我账号里已经有的 Creation 发布出去。`
6. `给我看看我的 Platform 能力列表。`
7. `把这个 Plugin 添加进来。` (after case 3, with the candidate's
   `user_state` set by the fixture: run once each with `added`,
   `entitled_not_added`, and `not_entitled`)
8. `这个 Creation 要更新一版内容。`

Expected: `springbrand-platform` is entered directly, and everything runs on
the `springbrand-platform` MCP entry only, with Platform order preserved
exactly. Two distinct browsing paths must not be confused: Marketplace
browsing uses `springbrand.plugins.list` (views `usable` / `marketplace` /
`my` / `featured`) without a match, while case 6 asks for the capability
registry and is answered by `list_capabilities` — not by `plugins.list`.
Case 5 goes through `springbrand.creations.list` (strict empty object) →
confirm → `springbrand.creations.publish`. Case 7 exercises the `get` →
`add` trunk with its `user_state` branches (`added` → use;
`entitled_not_added` → ask, then add; `not_entitled` → the user completes
acquisition on the Platform's own site, re-`get` verifies the flip, ask,
add) behind the explicit `add` confirmation gate — the Agent never pays or
acquires on the user's behalf. Case 8 is create-only: new content → upload
as a new Creation (new `idempotency_key`) → publish the new Creation, with
the previous public link staying live and the update never presented as an
in-place revision.

Action API (dynamic API intent):

9. `用一个可用的 API 服务帮我总结这个文件。`
10. `有没有 API 服务能把这个数据转成报表？`
11. `继续刚才那个 Action 执行。`
12. `查看刚才那次执行的状态。`

Expected: `springbrand-action-api` is entered directly. Cases 11–12 reuse the
existing execution state: verify with `get_execution` on the
`springbrand-action-api` entry and continue — no rematch, no re-execution.

Connector (named third-party system):

13. `列出我 GitHub 仓库里还没关闭的 issue。`
14. `在 GitHub 上给我的项目建一个新 release。`

Expected: `springbrand-connector` is entered directly. Search and execute run
on the `springbrand-connector` MCP entry only; pagination continues until
`complete` is true.

Competing-domain inventory: build the ≥10 and ≥50 prompt sets from prompts
where two or three domains compete, for example `把这份报告发布到 GitHub 上`
(Platform publish vs Connector GitHub), `用一个 API 服务往 GitHub 提交内容`
(Action API vs Connector), `帮我做一张图并发布` (Platform vs Action API image
services). Score each with domain selection precision/recall; a wrong-domain
entry is a recall miss, and an unjustified activation is a precision miss.

## TOOL_ISOLATION: one domain, one entry — cross-domain reference → mismatch + deliberate switch

Target: **zero** violations. A Domain Skill uses only its own MCP entry's
tools, always names the entry in instructions, and never infers a tool by
name alone (other entries expose similarly named tools — the known Cursor
duplicate-tool-name risk makes this a scored check on every Surface).

Cross-domain reference sent to the wrong entry (inject or simulate; on real
Surfaces, induce by handing a foreign reference into the domain workflow):

1. An `action:springbrand@0:<actionId>` reference submitted to the
   `springbrand-platform` entry.
2. A `platform:springbrand@0:<capabilityId>` reference submitted to the
   `springbrand-action-api` entry.
3. A `connector:...` reference submitted to the `springbrand-action-api`
   entry.
4. A `connector:...` reference submitted to the `springbrand-platform`
   entry.

Expected: the entry rejects it with `capability_domain_mismatch`; the Skill
surfaces the error's `recovery.domain` to the user, announces the switch in
plain language, preserves the task state, and hands over to that domain's
Skill as an explicit Domain Transition (`recovery.domain: action-api` →
`springbrand-action-api`; `recovery.domain: connectors` →
`springbrand-connector`; `recovery.domain: platform` →
`springbrand-platform`). Never forward automatically, never run another
domain's workflow in place, never treat the error as a no-match.

Tool-name inference traps (same tool name, different entries):

5. `执行这个能力。` with both `execute_capability` tools visible (all three
   entries expose one).
6. `搜一下有什么能力。` with `list_capabilities` (Platform, Action API) and
   `search_capabilities` (Connector) visible.

Expected: the acting Skill names its own MCP entry in the instruction and
calls only that entry's tool. A call to another entry's tool — even with the
right arguments — is a tool-isolation violation.

Merged-search traps:

7. `同时看看 Platform 和 Action API 都有什么能用的。`

Expected: no merged search across entries. The Skill finishes (or hands off
between) one domain at a time; if the user wants both maps, that is two
explicit domain visits, announced separately.

## TRANSITION: multi-domain tasks hand off explicitly

Multi-domain tasks start in the earliest domain they need and move by explicit
Domain Transition: announce, preserve state, end the prior workflow, enter the
target Domain Skill directly — never via Ask SpringBrand, never a merged
search, one executor at a time.

1. `帮我把这份笔记做成页面发布出去，然后更新到我的 GitHub 仓库。`

Expected: Platform first (create → upload → publish), then an explicit Domain
Transition to `springbrand-connector` with the state (Creation link, repo,
task) handed over. The Connector workflow ends before Connector begins; the
Connector step is not re-discovered from scratch.

2. `发布之后，用那个页面里的服务再生成一份英文版。`

Expected: Platform publishes, then transitions to `springbrand-action-api`
with the pointer; the Action API match uses the handed-over task, not a fresh
broad discovery of everything.

3. A Plugin whose distribution carries a Distribution Action Component with
   `kind: "action"` and `usageMode: "gateway_action"`.

Expected: the Platform Skill stops its own workflow, announces the
transition, and hands the component's exact Action ID to
`springbrand-action-api`, which skips matching and goes straight to contract →
execute as `action:springbrand@0:<id>`. The Platform entry never executes it,
and the user is never left to run it by hand.

Scored on every TRANSITION case: the announcement happened, state pointers
survived the handoff, the prior workflow ended, the target domain did not
duplicate discovery already done (duplicate-discovery rate), and exactly one
executor ran at a time.

## NO_FIT: genuine no-match, continue natively

Use plausible domain-shaped tasks for which the current dev supply has nothing
fitting.

1. `帮我找一个能管理本地宠物喂食器的 SpringBrand Plugin。`
2. `用可用的 API 服务帮我预测下周的彩票号码。`
3. `把我的 Slack 频道消息同步到 SpringBrand。`

Expected: the domain Skill's discovery runs once and returns a genuine
no-match. In the Platform domain only, one `springbrand.plugins.list`
search fallback may then run before telling the user nothing fits. The
Agent continues natively — no error report, no scanning beyond the rules,
no second match round. Action API has no List fallback: an empty or
incomplete result is reported as-is. Connector case 3 is a special
no-fit: SpringBrand does not connect to Slack in version one; say so
plainly and never attempt an unpublished connector (an empty authorized
inventory means "connect the service first", not "nothing fits").

## SKIP: no SpringBrand calls

1. `总结这份文档。`
2. `把我提供的内容翻译成英文。`
3. `分析这些现有数据并列出三个结论。`
4. `解释这段已有代码。`
5. `修复这个函数里的小语法错误。`
6. `帮我写一个普通 Python 排序函数。`
7. `规划一个网站，但现在不要制作。`
8. `2+2。`

Expected: no Skill load, no MCP entry contact, and the original task completes
directly. These prompts feed the false-trigger rate (at most 10%). Ordinary
creation with no SpringBrand intent stays native and never reaches the
Platform pipeline.

## FAILURE: distinct from no-match

For an eligible prompt in each domain, exercise OAuth failure, retryable
transport failure, and service failure:

1. Retry the same call once only when explicitly retryable, preserving the
   same reference, input body, and idempotency key where the domain uses one
   (Action API: yes; Connector: never sends one; Platform upload: the same
   `idempotency_key`).
2. Never enter a List/search fallback after an error — the fallback runs only
   after a genuine no-match.
3. Report the actual failure when SpringBrand was explicitly requested.
4. For automatic discovery, state briefly that discovery is unavailable and
   continue the original task after the bounded retry.
5. Record the failure separately from no-match and from routing verdicts.
   An error is never a no-match; a `get_execution` lookup error is never an
   execution status; `outcome_unknown` is never auto-retried.

## Required evidence fields

- Surface, application build, Plugin version, Git ref;
- install state (clean/update) and OAuth state per MCP entry;
- prompt and expected route: ROUTER, DOMAIN_SELECT, TOOL_ISOLATION,
  TRANSITION, NO_FIT, SKIP, FAILURE — with the expected domain and expected
  first action;
- first loaded Skill (Ask SpringBrand vs the Domain Skill) and whether the
  handoff carried the four elements (selected domain, one-line reason, task
  restated, known state pointers);
- MCP entry named in instructions, and every tool call mapped to its entry;
- pointers reused vs re-discovered (duplicate-discovery verdict);
- mismatch events with the surfaced `recovery.domain` and the switch that
  followed (tool-isolation verdict);
- transition announcements and per-domain workflow boundaries;
- original-task completion;
- routing, transport, discovery quality, and workflow-completion verdicts
  recorded separately.
