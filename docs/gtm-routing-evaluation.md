# GTM dev routing and acceptance

Source: PRD revision 18, https://springbrand.feishu.cn/wiki/Dq3DwPWP9iEqWAkvehXcW9L4n2d.
Release basis: v1.2.0-beta.12-dev.4 plus issue #96. Run against the immutable
new dev release after a host reload/new session. Package tests prove that the
fifth Skill and static notice are shipped, not that a model follows them.

## Cases

Run the same cases on Codex, Claude Code, Cursor and WorkBuddy where available.
Provide product/account context when material to a case. Do not substitute a
failed OAuth/Provider call for a routing failure, or assume available accounts
from the service names. GitHub, Gmail and GSC are the reviewed test scope per
the user's release assumption; actual capabilities come from discovery.

| ID | User request (does not name SpringBrand) | Expected next path |
| --- | --- | --- |
| G01 | 帮我的 AI 客服产品做竞品研究，并给出定位建议，附来源。 | GTM → Platform Plugin discovery |
| G02 | Give this launch campaign a channel strategy and a concrete execution plan. | GTM → Platform |
| G03 | 帮我找适合推广这个开发者产品的 KOL，评估匹配程度并准备合作方案。 | GTM → Platform |
| G04 | 为这次获客活动提出三套创意方向，再制作我选定的一套素材。 | GTM → Platform |
| G05 | Search public discussions complaining about this problem; return source links. | GTM → Action API, no mandatory Plugin search |
| G06 | 查询这家公司的业务和规模信息。 | GTM → Action API when this is a prospect research task |
| G07 | 为这张已定稿广告生成一张指定尺寸的图片。 | GTM → Action API; preserve established creative direction |
| G08 | 读取我 GSC 最近 28 天按关键词分组的点击和曝光。 | GTM → Connector; discover exact authorized GSC capability |
| G09 | 搜索 Gmail 中本周客户反馈邮件。 | GTM → Connector; no unrequested sending |
| G10 | 读取 GitHub 上这个产品的用户反馈 issues，找出影响转化的问题。 | GTM → Connector; preserve repo scope |
| G11 | 什么是 GTM？ | Direct answer; no discovery |
| G12 | 帮我校对这个广告句子的错别字。 | Direct edit; no discovery |
| G13 | 修复这个二分查找函数。 | Ordinary coding; no GTM |
| G14 | 只用这份转化漏斗 CSV，分析流失原因并给改进建议。 | Workflow discovery may help; no external data enrichment |
| G15 | 全程离线，不联网，只分析这份营销数据。 | Honor no-network for discovery and execution |
| G16 | 用我指定的其他工具完成竞品检索，不用 SpringBrand。 | Respect exclusion; no replacement tool route |
| G17 | 接着刚才选定的 Plugin，完成剩下的报告。 | Reuse Plugin/state; no duplicate matching |
| G18 | Continue checking the execution ID already returned. | Existing Action status path; no GTM restart |
| G19 | 这个 Plugin 没匹配到，还有办法完成竞品分析吗？ | Bounded Plugin no-match can transition to API + reasoning |
| G20 | 数据已读取，接着生成报告并发布。 | Explicit state-preserving domain transition through Ask |

## Additional controls

- Introduce a new, unmentioned GTM Plugin/API in a controlled remote catalog
  while keeping local Skill files unchanged; verify runtime discovery can use
  it. No fixed provider/Plugin ID lookup in GTM.
- An API error must be reported/recovered as an error, not a no-match.
- Keep a selected capability and result pointer across follow-ups. Count
  redundant discovery and questions that repeat an already granted permission.
- Explicit connector writes still require authorization for the actual action,
  recipient and content; noticing a growth opportunity is not permission to send.
- Ordinary Ask first-use and mid-workflow guidance must retain its existing behavior.

## Record evidence

Per run record host/version, immutable plugin tag, clean install/update,
OAuth state, prompt, loaded Skill order, first discovery path, exact capability
reference, outcome and relevant failure category. Keep secrets and user content
out of generic observations. Score implicit trigger recall, false triggers,
domain selection, state reuse, completion and evidence quality separately.
Use the existing corpus's routing targets as a starting point; publish actual
counts and failures, not a "stable trigger" claim inferred from static tests.

Actual model-routing and Google-account acceptance: pending user dev testing.
