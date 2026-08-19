# WorkBuddy 原生集成能力核实

- **核实日期**：2026-08-17
- **目标产品**：腾讯 CodeBuddy 产品线中的 **WorkBuddy 桌面应用**
- **资料边界**：腾讯/CodeBuddy 官方文档、官方更新日志、官方站点；同名候选只用其自身一手资料做排除。
- **状态词**：
  - **supported**：WorkBuddy 官方资料明确支持。
  - **engine-supported**：CodeBuddy 官方共享引擎规范明确支持，且规范原生识别 `.workbuddy-plugin`，但 WorkBuddy GUI 文档没有逐项重述。
  - **unsupported**：官方明确不支持。
  - **unknown**：官方资料不足，必须原生实测。

## 1. 产品辨识与消歧

本研究将用户所称 **WorkBuddy** 判定为腾讯出品、由 CodeBuddy 官方文档维护的 **WorkBuddy AI 桌面应用**。

判别证据：

1. 官方概览将 WorkBuddy 定义为“腾讯出品的全场景 AI 办公工作台”，具备自主规划、文件操作、代码生成和终端执行等 agent 能力。[W01][W02]
2. 官方为它单独提供 Plugin、Marketplace、MCP、Skill、Hook、权限和沙箱资料，直接匹配“让 SpringBrand plugin 接入 app”的目标。[W04][W05][W06][W07][W08]
3. 官方更新日志明确使用 **WorkBuddy Desktop**，并持续发布插件市场、MCP OAuth、SkillHub 和插件 Hook。[W02]
4. 截至 2026-08-17，最新公开版本是 **5.3.13，发布于 2026-08-13**。[W02][W03]

同名候选处理：

| 候选 | 判定 | 证据 |
|---|---|---|
| 腾讯 CodeBuddy 文档中的 WorkBuddy | **选定** | 官方桌面 agent，且具备本研究要求的原生扩展面。[W01][W02][W04] |
| `Lincyaw/workbuddy` | 排除 | 候选自身 README 将其描述为开源 coding-agent framework/Claude 插件实验，不是腾讯 WorkBuddy 桌面产品。[X01] |
| 其他同名企业工单、现场服务、人力软件 | 排除 | 产品类别与 coding/agent/desktop plugin host 不符，不进入能力矩阵。 |

**无法消歧之处：无实质歧义。** 在“Claude Code CLI/Desktop、Cursor、WorkBuddy”这一 host 组合中，腾讯 WorkBuddy 是唯一同时具备官方桌面产品和 Plugin/MCP/Skill/Hook 证据的候选。

## 2. 版本与平台基线

- 最新公开版本：**5.3.13（2026-08-13）**。[W02][W03]
- 桌面安装要求：**Windows 10+**；**macOS 12 Monterey+**，提供 Apple Silicon 与 Intel 包。[W03]
- 4.6.0（2026-03-19）：插件市场上线；4.7.3（2026-03-28）：MCP 标准 OAuth；4.8.0（2026-03-31）：WorkBuddy Desktop Skills/SkillHub/Marketplace，并修复插件 MCP `type: http` 的 OAuth；5.3.5（2026-07-25）：扩展插件 Hook。[W02]
- 因 SpringBrand 需要 Plugin + remote MCP OAuth + pre-prompt Hook，建议首个支持基线为 **WorkBuddy 5.3.5+**，首轮验收固定在 **5.3.13**。这是由公开变更推导的工程基线，不是腾讯发布的最低兼容承诺。[W02]
- **unknown**：官方未公开 WorkBuddy Desktop 内嵌 CodeBuddy agent engine 的精确版本映射。

## 3. 能力矩阵

| 能力 | 结论 | 边界 |
|---|---|---|
| 原生 Plugin / Marketplace | **supported** | WorkBuddy UI 可浏览、安装、启用、禁用、更新、卸载插件，并可添加第三方插件市场地址。[W04][W05] |
| Plugin 组件 | **supported** | 可包含 Skill、MCP、Slash Command、Hook、Agent。[W04] |
| Plugin manifest/目录 | **engine-supported** | 官方共享引擎接受 `.workbuddy-plugin/plugin.json`，并定义 `skills/`、`commands/`、`hooks/hooks.json`、`.mcp.json`。[W10] |
| Remote MCP HTTP | **supported** | WorkBuddy 更新日志明确支持插件 MCP `type: http`；共享引擎称其为面向远程服务的 HTTP 流式传输。[W02][W12] |
| “Streamable HTTP”精确措辞 | **supported with caveat** | WorkBuddy 文档使用 `HTTP`/`HTTP 流式传输`，没有在 WorkBuddy 页面逐字承诺“Streamable HTTP”；配置名为 `type: "http"`。[W02][W12] |
| MCP OAuth | **supported** | 标准 MCP OAuth、插件 HTTP MCP OAuth、token 主动刷新和自动重连均有发布记录。[W02] |
| OAuth DCR/PKCE/token 存储 | **unknown** | WorkBuddy 官方资料没有公开完整契约。 |
| Skill / Slash Command | **supported** | Plugin 可带两者；SkillHub、项目级 Skill/Command 与 `/` 菜单有官方记录。[W02][W04][W07][W14] |
| Plugin Hook | **supported** | WorkBuddy Plugin 文档列出 Hook，5.3.5 明确“扩展插件 Hook”。[W02][W04] |
| `UserPromptSubmit` | **engine-supported；需实测** | 共享引擎定义其在 AI 处理前触发；WorkBuddy 页面未列出完整事件表。[W10][W13] |
| Hook 独立信任/逐 Hook 审核 | **unknown / 未见支持** | 共享引擎说明 plugin-level Hook 在插件启用后直接生效，不受 frontmatter Hook 闸门约束。[W10] |
| 权限、审批、沙箱 | **supported** | WorkBuddy 有权限模式、安全沙箱、Skill 安全扫描和 MCP 安装信任引导。[W02][W08] |
| 仓库 URL 原生分发 | **engine-supported；GUI 语法需实测** | WorkBuddy 可添加市场地址；共享引擎支持 GitHub、Git URL 和远程 `marketplace.json`。[W05][W11] |

## 4. Plugin、Marketplace 与包结构

WorkBuddy 官方 Plugin 页面明确，一个插件可以统一打包 Skills、MCP、Slash Commands、Hooks 和 Agents。[W04]

原生生命周期包括：

1. Marketplace 浏览和一键安装；
2. 已安装列表中启用/禁用；
3. 获取最新版本；
4. 管理页卸载；
5. 添加第三方 Marketplace 地址。[W04][W05]

更新日志还记录了市场版本号、增量缓存更新、更新提示、企业自建 Skill/插件市场和卸载清理修复，因此 Marketplace 是版本化的原生分发面，不是一次性复制文件。[W02]

CodeBuddy 官方共享引擎给出的 WorkBuddy-compatible 布局是：[W10]

```text
plugin-root/
├── .workbuddy-plugin/
│   └── plugin.json
├── skills/
│   └── springbrand/
│       └── SKILL.md
├── commands/
├── hooks/
│   └── hooks.json
└── .mcp.json
```

关键事实：

- `plugin.json` 可位于 `.codebuddy-plugin/`、`.workbuddy-plugin/` 或 `.claude-plugin/`；WorkBuddy adapter 应优先实测 `.workbuddy-plugin/plugin.json`。[W10]
- Plugin 安装时自动发现 Skills/Commands；Skill 使用含 `SKILL.md` 的目录，Command 使用 Markdown 文件。[W10]
- Plugin MCP 位于根 `.mcp.json` 或 `plugin.json#mcpServers`；Hook 位于 `hooks/hooks.json` 或 `plugin.json#hooks`。[W10]

**unknown**：WorkBuddy GUI 文档没有发布独立、版本化的 Plugin JSON Schema，也没有承诺 CodeBuddy CLI 的所有 plugin 字段在 WorkBuddy 5.3.13 中完全等价。实现前应做最小原生安装实验，不应预先创建自定义安装器。

## 5. MCP 与 OAuth

### 5.1 配置边界

WorkBuddy MCP 支持两个明确作用域：[W06]

- 用户级：`~/.workbuddy/mcp.json`；
- 项目级：`<项目目录>/.workbuddy/mcp.json`。

4.8.0 更新记录明确提到“插件 MCP `type` 为 `http` 时 OAuth 授权”，证明 remote HTTP MCP 可以由 Plugin 携带，而不只限手工配置。[W02]

共享引擎 MCP 文档定义 `stdio | sse | http`，其中 HTTP 是“通过 HTTP 流式传输与远程服务通信”，示例为 `{"type":"http","url":"https://example.com/mcp"}`。[W12]

SpringBrand 的最小声明应为：

```json
{
  "mcpServers": {
    "springbrand": {
      "type": "http",
      "url": "https://connector.springbrand.ai/mcp"
    }
  }
}
```

这是基于官方 schema 的适配建议，不是已完成的 WorkBuddy 实测。

### 5.2 OAuth

官方已确认：[W02]

- 4.7.3：MCP 标准 OAuth；
- 4.8.0：插件 HTTP MCP 可触发 OAuth；
- 4.9.1：token 主动刷新和自动重连；
- 后续版本持续修复 token、授权参数和重连问题。

因此 Plugin 不应打包 access token、refresh token、静态 `Authorization` header 或 client secret；应让 WorkBuddy 对 SpringBrand endpoint 走原生 OAuth。

**unknown**：官方没有证明 WorkBuddy 客户端一定支持 SpringBrand 服务端采用的全部 discovery、Dynamic Client Registration、PKCE 和回调细节，也没有公开 token 的精确存储位置。安装验收必须实际覆盖授权、刷新和新会话重连。

## 6. Skill 与 Command

- WorkBuddy 原生提供 Skill 推荐、SkillHub、自定义 Skill 创建/安装、启用/禁用、更新和卸载。[W02][W07]
- Plugin 可携带 Skill 与 Slash Command；输入框 `/` 菜单能够发现 Skill，Plugin 内 Skill 也会被识别。[W02][W04]
- 5.0.0 增加项目级技能、专家、连接器和指令配置，并按角色控制编辑；5.1.0 增加企业自建 Skill/插件市场端到端能力。[W02]
- 共享引擎当前 Plugin Skill 格式为 `skills/<name>/SKILL.md`，支持 description 自动匹配和 `/name` 调用。[W10][W14]

对 SpringBrand 的含义：现有 `skills/springbrand/SKILL.md` 应继续作为唯一 authoritative Skill；不需要复制一份 WorkBuddy 业务流程，只增加最薄 host adapter。

**unknown**：WorkBuddy UI 安装的第三方 Plugin 默认是账号级、设备级还是项目级。项目级/企业级能力已存在，但其 Plugin scope 是否与共享引擎的 `user/project/local/managed` 一一映射，官方未说明。[W02][W10]

## 7. Hook 生命周期与信任

已证实：

- WorkBuddy Plugin 可包含 Hooks；5.3.5 明确扩展插件 Hook。[W02][W04]
- 共享引擎定义 `UserPromptSubmit` 在用户提交 prompt 后、AI 处理前触发，也支持 `SessionStart`、`PreToolUse`、`PermissionRequest`、`PostToolUse` 等事件。[W10][W13]
- Plugin Hook 可为 `command`、`http`、`prompt` 或 `agent`。[W10][W13]

SpringBrand 应优先尝试 Plugin-level `UserPromptSubmit`，只注入一条短 preflight 指令；Hook 不联网、不读取/保存 prompt，也不复制 Skill 的 Marketplace 流程。

但这仍是 **engine-supported**。WorkBuddy 5.3.13 验收必须证明：

1. 原生安装后 Hook 被加载；
2. 新任务首轮在计划、追问、代码或产物前得到 Hook context；
3. 更新、禁用、卸载后 Hook 状态正确变化；
4. 无关 Plugin、Skill、MCP 和用户配置不受影响。

共享引擎明确区分：[W10]

- `hooks/hooks.json`：插件启用后对整个会话生效，**不受** `allowUntrustedFrontmatterHooks` 约束；
- Skill/Agent frontmatter Hook：默认受安全闸门限制，需要显式开启。

因此，**未找到 WorkBuddy 对 executable plugin Hook 的独立 review/hash trust 流程**。当前可证明的信任边界是“用户安装/启用高信任 Plugin”，不是“每个 Hook 单独批准”。若验收要求原生逐 Hook 审核，应暂记 **unknown/未满足**，不能用自写 consent helper 冒充原生能力。

## 8. 权限、安全与配置边界

已证实：

- WorkBuddy 有默认、规划、完全访问等权限模式；默认模式在文件写入、命令执行等高风险操作前请求确认。[W08]
- 安全沙箱限制命令的文件系统访问，并提供黑白名单和系统权限管理。[W02][W08]
- 自定义 Skill 安装前有安全检测；非高风险 Skill 可配置自动安装，高风险项仍需人工确认。[W02][W07]
- 更新日志记录 MCP Session 安装信任引导，以及卸载套件/删除市场时清理关联 MCP 和授权信息。[W02]
- 官方 Marketplace 文档将 Plugin/Marketplace 视为高信任组件，并警告其可能以当前用户权限执行代码，只应安装可信来源。[W11]

仍为 **unknown**：

- Plugin command Hook 是否始终受 WorkBuddy OS sandbox 约束；
- Hook 安装时是否展示完整命令、hash 或差异；
- OAuth token 的存储与加密位置；
- 企业管理员能否强制批准/禁止指定第三方 Marketplace/Plugin；
- Plugin 用户/项目/企业 scope 的完整优先级和冲突规则。

## 9. 安装、更新与卸载

| 生命周期 | 原生路径 | 结论 |
|---|---|---|
| 添加来源 | 插件页添加第三方 Marketplace 地址。[W05] | supported |
| 安装 | Marketplace 一键安装。[W04][W05] | supported |
| 启用/禁用 | 已安装 Plugin 卡片切换。[W04] | supported |
| 更新 | 已安装 Plugin 获取最新版；市场有版本号和增量更新机制。[W02][W04] | supported |
| 卸载 | Plugin 管理页卸载。[W05] | supported |
| 删除 Marketplace | 更新日志证明该操作存在，并记录关联清理/提示修复。[W02] | supported；策略需实测 |
| 版本固定/回滚 | GUI 文档未公开 pin、rollback 或安装指定 tag 的流程。 | unknown |
| 无人值守安装 | WorkBuddy GUI 文档未公开稳定 CLI/API。 | unknown |

不应在原生生命周期之外创建 SpringBrand 自定义安装器。

## 10. 仓库 URL 原生分发

可证明的部分：

- WorkBuddy UI 支持添加第三方“插件市场地址”。[W05]
- 共享引擎 Marketplace 原生支持 GitHub `owner/repo`、HTTPS/SSH Git URL（可带 branch/tag）、本地目录/manifest、远程 HTTP(S) `marketplace.json`。[W11]
- Marketplace 是两步流程：先添加 Marketplace，再安装 `plugin@marketplace`；不是把任意裸 Plugin repo URL 直接视为已安装 Plugin。[W11]
- 官方插件规范直接接受 `.workbuddy-plugin/plugin.json`，因此不是把无关 CLI 格式生搬到 WorkBuddy。

结论：

- **仓库作为 Marketplace 来源：engine-supported，是最可能的 WorkBuddy 原生分发路径。**
- **实测结果：** WorkBuddy 5.3.13 的 Add Marketplace 接受 `owner/repo` 和完整 GitHub URL；`owner/repo@tag` 不接受。生产使用裸仓库默认 `main`，开发 tag 使用 ZIP Marketplace source。
- **直接安装裸 Plugin repo：未被 WorkBuddy 文档证明。**
- 当前 Marketplace 文档要求仓库含 `.codebuddy-plugin/marketplace.json`；Plugin 自身可用 `.workbuddy-plugin/plugin.json`。[W10][W11]

## 11. SpringBrand WorkBuddy adapter 最小建议

1. 目标 WorkBuddy **5.3.5+**，首轮证据固定在 **5.3.13**。
2. 复用现有 `skills/springbrand/SKILL.md` 和 `https://connector.springbrand.ai/mcp`。
3. 只增加 WorkBuddy manifest/Marketplace metadata 与经实测需要的 Hook/MCP 路径差异；不要先建共享多 host abstraction。
4. MCP 使用 `type: "http"` + URL，不携带静态 token/header/client secret，走 WorkBuddy 原生 OAuth。
5. Hook 尝试 Plugin-level `UserPromptSubmit`；实测前保持 `engine-supported`。
6. 把 Plugin 安装/启用视为当前可证明的信任边界；独立 Hook review 是 blocker/unknown。
7. 优先使用 GitHub/Git Marketplace repository；先验证 GUI 地址语法、tag/version 更新和卸载清理。
8. 不得把 `.codebuddy/` 用户配置路径直接写进 WorkBuddy 安装说明；WorkBuddy 使用自己的 `.workbuddy/` 边界。[W06]
9. 验收记录 Plugin、Skill、remote MCP OAuth、Hook、权限提示、更新、禁用、卸载、市场删除，以及无关配置保留的桌面证据。

## 12. 必须通过原生实测关闭的 unknown

- WorkBuddy 5.3.13 是否完整接受 `.workbuddy-plugin/plugin.json` 与 `.codebuddy-plugin/marketplace.json` 组合；
- GUI 接受哪些 Marketplace URL 格式，是否支持 Git tag/ref；
- remote `type: "http"` 是否与 SpringBrand 完成 OAuth discovery、授权、刷新和重连；
- `UserPromptSubmit` 是否在新任务首轮、恢复会话和子任务中稳定触发；
- Plugin Hook 是否有安装时展示、单独信任或变更复审；
- Plugin install scope、企业 policy 和项目角色权限的精确优先级；
- update pin/rollback、离线安装、无人值守安装是否存在稳定原生接口。

## 13. 来源清单

所有来源访问日期均为 **2026-08-17**。

| ID | 官方一手来源 | 用途 |
|---|---|---|
| W01 | https://www.codebuddy.cn/docs/workbuddy/Overview | WorkBuddy 身份、定位、agent 能力 |
| W02 | https://www.codebuddy.cn/docs/workbuddy/Changelog | 最新版本及 Plugin、MCP OAuth、Skill、Hook、安全、企业能力变更 |
| W03 | https://www.codebuddy.cn/docs/workbuddy/Download-History | 桌面版本与平台；安装要求见同站 Windows/macOS 指南 |
| W04 | https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Plug-In | Plugin 组成、安装、启用、禁用、更新 |
| W05 | https://www.codebuddy.cn/docs/workbuddy/Plugins | 添加 Marketplace、安装与卸载 |
| W06 | https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide | MCP 用户/项目作用域与配置路径 |
| W07 | https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market | Skill 市场、自定义 Skill、安全设置 |
| W08 | https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes | 默认权限、审批与安全沙箱 |
| W10 | https://www.codebuddy.cn/docs/cli/plugins-reference | 共享引擎 manifest、目录、Hook 事件与安全闸门 |
| W11 | https://www.codebuddy.cn/docs/cli/plugin-marketplaces | GitHub/Git/HTTP Marketplace、更新和高信任警告 |
| W12 | https://www.codebuddy.cn/docs/cli/mcp | HTTP 流式 remote MCP 与 `type: http` |
| W13 | https://www.codebuddy.cn/docs/cli/hooks | Hook 生命周期与 `UserPromptSubmit` |
| W14 | https://www.codebuddy.cn/docs/cli/skills | `SKILL.md`、发现、斜杠调用、权限 |
| X01 | https://github.com/Lincyaw/workbuddy | 同名候选自身说明，仅用于排除 |

## 14. 最终判断

**腾讯 WorkBuddy 是可行的 SpringBrand 原生 Plugin host 候选。** Plugin/Marketplace、remote HTTP MCP、标准 OAuth、Skill/Command、Hook 和桌面生命周期都有一手资料支持；最短路径是复用现有 Skill 和远程 MCP，只增加 WorkBuddy-specific package adapter。[W02][W04][W06][W10]

目前不能声称完整验收通过的核心缺口：

1. WorkBuddy 自身文档没有逐项保证共享引擎 `UserPromptSubmit` 的桌面行为；
2. 没有找到 executable plugin Hook 的独立原生 trust/review 流程。

两项都必须用 WorkBuddy 5.3.13 原生安装实验关闭；无法关闭时应在后续规格中保留为 `unknown`/`unsupported`，而不是用自定义安装器或 consent helper 掩盖。
