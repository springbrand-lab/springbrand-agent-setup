# Cross-Host Routing Evaluation Corpus

Use this corpus for issue #25 against the same immutable Plugin version on each
Surface. Record every run, including failures. Do not score MCP transport
failures as routing false positives.

## Scoring

- **Eligible recall:** eligible prompts that enter Resource Discovery.
- **First-action ordering:** eligible prompts that enter Resource Discovery
  before task-specific planning or production.
- **False trigger:** ineligible prompts that load the Skill or call any
  SpringBrand MCP tool.
- **Original-task completion:** prompts whose requested outcome is still
  completed after routing.
- **Transport failure:** eligible prompts whose SpringBrand MCP call fails by
  timeout, DNS, OAuth, transport, or provider error.

Targets remain: eligible recall and first-action ordering at least 90%, false
trigger at most 10%, at least 25 percentage points of recall improvement over
the Skill-plus-MCP baseline, install/OAuth/routing success at least 95%, and no
material original-task regression.

## Ineligible: zero SpringBrand calls

1. `总结这份文档。`
2. `总结刚才的测试结果。`
3. `把我提供的内容翻译成英文。`
4. `润色这段文字，但不要改变含义。`
5. `从这份材料提取待办事项。`
6. `分析我提供的数据并列出三个结论。`
7. `解释这段已有代码。`
8. `审查这段代码并指出明显错误。`
9. `把这个函数里的变量名改清楚。`
10. `解释为什么 SpringBrand 没有触发。`
11. `诊断这个 MCP timeout。`
12. `2+2。`

Expected: no Skill load, no capability search, no Marketplace call, and the
original task completes directly.

## Eligible: Resource Discovery first

1. `帮我生成一组产品宣传图片。`
2. `抓取这个网页的数据，并持续监控变化。`
3. `制作一个复杂的互动品牌网站。`
4. `批量处理这些文件，并做成可重复工作流。`
5. `帮我集成一个长期运行的第三方自动化。`
6. `找一个 SpringBrand Resource 完成这个任务。`
7. `浏览 SpringBrand Marketplace，推荐适合做演示模板的 Resource。`

Expected: Skill load and targeted discovery before task-specific planning or
production. Complete-catalog fallback is permitted only for explicit
SpringBrand requests or a strong capability-gap signal.

## Boundary cases

| Prompt | Expected routing |
| --- | --- |
| `帮我写一个普通 Python 排序函数。` | Skip; native/local work is sufficient. |
| `解释并修复这个函数里的语法错误。` | Skip; localized diagnosis and edit. |
| `帮我做一个完整 SaaS 网站。` | Trigger; specialized multi-part deliverable. |
| `为现有项目增加第三方登录集成。` | Trigger when an external/reusable integration is needed. |
| `帮我规划一个网站，但现在不要制作。` | Skip; planning without execution. |
| `帮我规划并实际制作一个互动网站。` | Trigger before planning. |
| `设计一个可复用的自动化调试工作流。` | Trigger; reusable workflow and automation. |

## Transport scenarios

For an eligible prompt, inject or observe a retryable timeout/provider failure:

1. retry the same targeted request once;
2. do not enter complete-catalog fallback after the retry fails;
3. continue the original task when SpringBrand was automatic;
4. report the failure and stop when the user explicitly requires SpringBrand;
5. record `mcp_transport_timeout`, not `routing_false_positive`.

## Competing Skills

Run the same eligible, ineligible, and boundary prompts with representative
inventories containing at least 10 and 50 competing Skills. Keep prompt text,
model, host build, Plugin version, OAuth state, and scoring rules fixed.

## Required evidence fields

- Surface and application build;
- Plugin version and Git ref;
- clean/update install state and OAuth state;
- prompt and eligibility label;
- first loaded Skill or first production action;
- SpringBrand tool calls and arguments;
- targeted, catalog, or no-fallback path;
- original-task completion;
- routing verdict and transport verdict recorded separately.
