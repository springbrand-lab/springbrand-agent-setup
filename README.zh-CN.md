<div align="center">

<img src="./assets/springbrand-icon.png" width="96" alt="SpringBrand logo" />

# SpringBrand

**给 AI 助手用的能力市场**

</div>

[English](./README.md) | 简体中文

SpringBrand 将专业数据、工具和工作流连接到你正在使用的 AI Agent，让它不只回答问题，还能执行任务并交付结果。

## 解决什么问题

要让 AI Agent 完成一项完整的工作，用户往往需要自己寻找工具、注册账号、配置 API，再手动衔接不同的工作流程。SpringBrand 将这些能力集中到一个入口：用户只需要说明想要的结果，AI Agent 就会选择并调用合适的工具，把任务真正完成。

- **一个入口：**无需在不同工具、账号和平台之间反复切换。
- **直接交付：**AI Agent 不只提供建议，还能执行任务并交付结果。
- **按次付费：**工具按需调用、统一付费，无需购买多个长期订阅。
- **支持重复任务：**可以定期执行监控、研究和报告等工作。

## 简单案例

- 输入一个竞品网址，分析它的流量来源、获客页面和用户搜索关键词。
- 持续监控社交媒体上关于你的产品、品牌或竞争对手的真实讨论。
- 根据目标客户画像，寻找可以直接联系的公司和关键联系人。
- 寻找合适的 KOL/KOC，并生成可执行的合作与推广方案。
- 调用不同能力，完成文字、图片、视频和配音内容。

## 已覆盖的能力

SpringBrand 的能力覆盖 **X、TikTok、Instagram、YouTube、Reddit、Pinterest、小红书** 等社媒平台，可以完成：社媒监控、趋势追踪、热门内容分析、用户洞察、竞品研究、网站流量分析、流量来源分析、关键词研究、热门页面分析、SEO 表现分析、潜在客户搜索、公司与联系人发现、创作者搜索、推广方案制定，以及文字、图片、视频和配音生成。

这些能力通常分散在不同的专业付费工具中。SpringBrand 提供类似以下产品的能力：

- **流量与 SEO 研究：**Similarweb、Semrush、Ahrefs、DataForSEO
- **搜索与网页研究：**Exa、Tavily、Perplexity、Firecrawl
- **公司与联系人搜索：**Apollo、People Data Labs
- **创作者发现：**WaveInflu
- **内容生成：**GPT Image、Seedream、Seedance、Nano Banana、ElevenLabs
- **第三方系统操作：**GitHub 等连接器

这些产品名称仅用于说明能力范围，不代表 SpringBrand 与它们存在直接集成或合作关系。

能力分为 Platform、Action API、Connector 三个域；不确定该用哪个时，直接问你的 Agent `$ask-springbrand`，它会推荐唯一合适的域。

## 安装

把下面这段提示词发给你的 AI Agent（Claude Code、Codex、Cursor、Copilot、Devin、Windsurf、WorkBuddy 等均可），Agent 会读取指南并完成安装：

> 按照 https://plugin.springbrand.ai/INSTALL.md 安装或更新 SpringBrand 生产版。识别当前 Agent 并使用对应的 Host 指南，检测是否已安装，更新时就地刷新现有 Marketplace/Plugin，优先使用原生 OAuth，保留现有配置，仅在需要我完成的 UI 或 OAuth 步骤时暂停。

也可以直接添加托管 MCP 服务器：

```sh
npx add-mcp 'https://connector.springbrand.ai/mcp'
```

## 本仓库包含什么

本仓库提供 SpringBrand 安装程序，包括五个 Canonical Skills 和一个 MCP 入口，并分别打包为 Codex、Claude Code、Cursor 和 WorkBuddy 的原生插件。

其他 AI Agent 也可以通过 Skills + MCP 的方式接入。
