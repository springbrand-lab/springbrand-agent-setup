# Cursor CLI / 桌面应用原生集成能力核实

- **基准日**：2026-08-17
- **访问日期**：本文所有在线来源均于 2026-08-17 访问
- **范围**：Cursor 桌面 IDE、Cursor CLI、Cursor Plugins、Agent Plugins、VS Code 扩展、MCP、OAuth、Rules、Skills、commands、Hooks、权限/信任、安装/启用/更新/卸载、配置边界、仓库 URL 分发
- **证据规则**：只采用 Cursor 官方文档、Cursor 官方仓库/源码和 Cursor 官方 changelog/公告。资料未明确说明的能力一律标记为 **UNKNOWN**，不作推断。

## 状态定义

| 状态 | 含义 |
| --- | --- |
| **SUPPORTED** | 官方一手资料明确支持。 |
| **PARTIAL** | 只明确支持一部分，不能扩大到完整场景。 |
| **UNKNOWN** | 官方资料不足，不能按支持处理。 |
| **UNSUPPORTED** | 当前官方规范明确不提供或不适用。 |

## 关键结论

| 能力 | 桌面 IDE | Cursor CLI | 结论 |
| --- | --- | --- | --- |
| 原生 Plugin / Marketplace | **SUPPORTED**。支持 Cursor Plugins 与 Agent Plugins，可从 Customize / Marketplace 安装，并选择 user 或 project scope。[S1][S2][S5] | **PARTIAL**。CLI 有 `/plugin [subcommand]` 管理 plugins/marketplaces；但 Plugin 参考只明确称完整 bundle 在 Cursor IDE 工作。[S2][S11] | 桌面可做原生 Plugin；CLI 必须逐组件验证。 |
| VS Code 扩展 | **SUPPORTED**。Cursor 基于 VS Code，可导入 VS Code extensions；官方公告说明扩展目录使用 OpenVSX，并支持 VSIX。[S15][S16] | **UNSUPPORTED / 不适用**。官方资料未说明 VS Code extension host 在 CLI 运行。 | VS Code extension 与 Cursor Agent Plugin 是两套机制。 |
| Remote MCP：Streamable HTTP | **SUPPORTED**。官方 transport 表明确列出 Streamable HTTP，并以 `url` 配置远端 server。[S7] | **SUPPORTED（配置/协议层）**。官方文档明确 Team MCP 可用于 Agent Window、IDE、CLI；CLI permissions 也支持 `Mcp(server:tool)`。[S1][S7][S13] | SpringBrand 的 remote Streamable HTTP 形态可表达；真实端点仍需互操作测试。 |
| MCP OAuth | **SUPPORTED**。远端 HTTP/SSE 支持 OAuth；桌面 callback 为 `http://localhost:8787/callback`。[S7] | **UNKNOWN（交互流程）**。当前官方页面未明确 CLI 的 OAuth 登录命令、callback、token 存储和注销流程。 | 不得把桌面 OAuth 步骤直接写成 CLI 步骤。 |
| Rules | **SUPPORTED**。支持 Project/User/Team Rules 与 `AGENTS.md`。[S8] | **SUPPORTED / 边界不完整**。CLI 使用 Cursor rules，但 Team/User 合并细节未在本研究来源中完整说明。[S8][S20] | 仓库级 Rules 可复用。 |
| Agent Skills | **SUPPORTED**。自动发现或 `/skill-name` 手动调用。[S9] | **SUPPORTED**。2.4 公告明确 Skills 同时支持 editor 与 CLI。[S9][S19] | SpringBrand Skill 可复用 Agent Skills 格式。 |
| Plugin commands | **SUPPORTED**。Cursor Plugin 正式支持 `commands/`。[S1][S2] | **UNKNOWN**。CLI 有内置 slash commands，但官方资料未保证 Plugin `commands/` 与 IDE 完全同构。[S2][S11] | 不得宣称 custom command CLI parity。 |
| Hooks | **SUPPORTED**。Cursor Plugin 可打包 Hooks；也支持 project/user/team/enterprise 配置。[S1][S2][S10] | **PARTIAL**。`workspaceOpen` 明确支持 desktop 与 CLI；没有完整的逐事件 CLI 支持矩阵。[S10][S19] | `beforeSubmitPrompt` 在 CLI 的可用性必须实测。 |
| 权限 / 信任 | **SUPPORTED**。Project Hooks 只在 trusted workspace 运行；MCP 默认请求批准；CLI 有 allow/deny、approval mode 和 sandbox；Marketplace 插件人工审核。[S3][S7][S10][S12][S13] | **SUPPORTED**，但信任 UX 与桌面不应互相推定。 | 应使用 Cursor 自身的 workspace trust 与 permissions 术语。 |
| 仓库 URL 原生分发 | **PARTIAL**。公开 Marketplace 接受公开 Git repo 提交；Team Marketplace 明确支持从 GitHub repo 导入；Rules/Skills 另有 GitHub URL 导入。[S1][S2][S8][S9] | **UNKNOWN（个人直接 repo 安装）**。CLI 有 plugin manager，但官方参考未给出任意 repo URL 的完整安装/更新/卸载合同。[S11] | 正式路径是公开 Marketplace 或 Team Marketplace；个人 repo URL 不应作为已核实的稳定发布路径。 |

## 1. VS Code 扩展与 Cursor Agent Plugin 的边界

Cursor 官方文档说明 Cursor 基于 VS Code，并可一键导入 VS Code 的 extensions、themes、settings 和 keybindings。[S15] 官方公告说明 Cursor 的扩展目录使用 OpenVSX，并支持手工安装 VSIX。[S16]

Cursor Agent Plugin 则使用另一套清单和组件模型：[S1][S2]

- **Agent Plugin**：根目录 `plugin.json`；当前 Cursor 文档列出的组件是 Skills、MCP Servers。
- **Cursor Plugin**：`.cursor-plugin/plugin.json`；可包含 Rules、Skills、Agents、commands、MCP Servers、Hooks、variables。

因此：

- 安装 VS Code extension **不等于**安装 Cursor Plugin。
- VS Code extension 可通过 `vscode.cursor.mcp.registerServer()` 动态注册 MCP，但官方资料没有说明该注册会传播到 Cursor CLI，故该点为 **UNKNOWN**。[S7]
- 若目标是同时提供 Skill、remote MCP 和 Hook，应优先评估 Cursor Plugin，而不是用 VS Code extension 代替 Agent Plugin 机制。

## 2. Plugin 格式、安装和 Marketplace

### 2.1 包格式

Cursor 当前支持两种 Plugin 格式：[S1][S2]

| 格式 | Manifest | 官方列出的组件 |
| --- | --- | --- |
| Agent Plugin | 根 `plugin.json` | Skills、MCP Servers |
| Cursor Plugin | `.cursor-plugin/plugin.json` | Skills、MCP、Rules、Agents、commands、Hooks、variables |

Cursor 官方 `cursor/plugin-template` 仓库提供了 `.cursor-plugin/marketplace.json`、单插件 manifest、`mcp.json`、`hooks/hooks.json` 和校验脚本示例。本次读取的 commit 为 `46216072ac5750f782f95bb325b4d12b7c3ae9c9`。[S4]

### 2.2 安装与 scope

桌面正式安装流程：[S1]

1. 打开 Customize。
2. 找到 Plugin。
3. 点击 Install。
4. 选择 project 或 user scope。

本地开发可把 Plugin 复制或 symlink 到 `~/.cursor/plugins/local/<plugin>`，然后重启 Cursor 或运行 `Developer: Reload Window`。[S1]

CLI 当前 slash command 参考列出 `/plugin [subcommand]`，但没有在该页列出完整子命令和生命周期语义。[S11]

### 2.3 启用与配置

官方明确的管理粒度包括：[S1][S2][S7][S9]

- MCP server 可在 Customize 中逐个启用/禁用。
- Rules 可在 Always、Agent Decides、Manual 间切换。
- Skills 可由 Agent 自动选择，或用 `/skill-name` 手动调用。
- Team Marketplace 支持 Default Off、Default On、Required；Required 不可卸载。
- Plugin variables 只声明 schema；secret value 不应进入仓库，而由 Dashboard 的 Plugins → Configure 提供。

**UNKNOWN**：当前官方页面没有定义统一的“整包 Plugin enable/disable”行为。

### 2.4 更新与卸载

- 公开 Marketplace 的每次 Plugin 更新都要经过 Cursor 人工审核；不会仅因源仓库变化就自动发布。[S3]
- Team Marketplace 从 GitHub repo 导入后，可启用 Auto Refresh，也可手工 Refresh。完整 repo import 会重新读取 manifest；逐个添加 Plugin 的 Marketplace 需要重新导入 repo URL 才能发现新 Plugin。[S1]
- Team Required Plugin 不可卸载；Default On 可由开发者 opt out。[S1]
- **UNKNOWN**：个人/项目 Plugin 的完整卸载步骤、CLI uninstall 子命令、公开 Marketplace 客户端何时取得已审核更新。

## 3. MCP：Streamable HTTP、OAuth 和配置边界

### 3.1 Transport

Cursor 正式支持 stdio、SSE、Streamable HTTP。SSE 与 Streamable HTTP 都可连接远端 server，并列为支持 OAuth。[S7]

可表达 SpringBrand endpoint 的最小配置为：

```json
{
  "mcpServers": {
    "springbrand": {
      "url": "https://connector.springbrand.ai/mcp"
    }
  }
}
```

该配置只证明 Cursor 能表达此 remote transport；本文没有使用 Cursor 客户端验证该生产 endpoint，互操作结果为 **UNKNOWN until tested**。[S7]

### 3.2 OAuth

官方 MCP 文档明确：[S7]

- Cursor 支持 MCP OAuth。
- 不支持 Dynamic Client Registration 的 provider 可在 `mcp.json` 中配置固定 `CLIENT_ID`、可选 `CLIENT_SECRET` 和 scopes。
- scopes 未填写时可从 `/.well-known/oauth-authorization-server` 发现。
- Desktop callback：`http://localhost:8787/callback`。
- Web/Cursor Agents callback：`https://www.cursor.com/agents/mcp/oauth/callback`。
- Client secret 应通过环境变量 interpolation 提供，不应硬编码。

**UNKNOWN**：CLI 专属 OAuth 命令、callback、浏览器交互、token 存储与 logout 流程。

### 3.3 配置位置

| 配置 | Project | Global / User | Team / Enterprise |
| --- | --- | --- | --- |
| MCP | `.cursor/mcp.json` | `~/.cursor/mcp.json` | Team Marketplace 分发；Enterprise MCP allowlist、URL pattern、tool allowlist。[S7] |
| Plugin | 安装时选择 project scope | 安装时选择 user scope；开发目录 `~/.cursor/plugins/local` | Default Off / Default On / Required。[S1] |
| CLI config | `<project>/.cursor/cli.json`，当前只允许 permissions | `~/.cursor/cli-config.json` | 管理策略另由团队/企业配置。[S12] |

### 3.4 MCP 权限

- MCP tool 默认执行前请求批准。[S7]
- Enterprise 可按 command 或 remote URL pattern allowlist server，并按 tool allowlist。[S7]
- CLI permissions 支持 `Mcp(server:tool)`；deny 优先于 allow。[S13]
- MCP 分发和 MCP policy 是两件分开的事情；允许一个 server 不等于安装它。[S7]

## 4. Rules、Skills 和 commands

### 4.1 Rules

Cursor 正式支持：[S8]

- Project Rules：`.cursor/rules/*.mdc`。
- User Rules：Customize → Rules。
- Team Rules：Dashboard 管理，可 enforce。
- `AGENTS.md`：支持项目根目录与嵌套目录。

Rules 可从 GitHub repo 导入：Customize → Rules → Add Rule → Remote Rule (Github)。Cursor 扫描 `.mdc` 并同步到 `.cursor/rules/imported/<repoName>`。[S8]

### 4.2 Agent Skills

Cursor 自动发现以下目录：[S9]

- Project：`.agents/skills/`、`.cursor/skills/`
- User：`~/.agents/skills/`、`~/.cursor/skills/`
- 兼容目录：project/user 的 `.claude/skills/` 与 `.codex/skills/`

Skill 默认由 Agent 按 `description` 判断相关性，也可 `/skill-name` 手动调用；`disable-model-invocation: true` 可限制为仅手动调用。[S9]

2.4 公告明确 Agent Skills 支持 editor 与 CLI。[S19]

官方 Skills 页称 Skills 可通过 GitHub repository links 安装，但没有完整说明 Skill repo 的扫描、更新和卸载语义。因此 GitHub Skill 安装为 **PARTIAL**，不能等同于完整 Plugin lifecycle。[S9]

### 4.3 Commands

Cursor Plugin 的 `commands/` 可包含 `.md`、`.mdc`、`.markdown`、`.txt`，并可用 frontmatter 声明 `name` 和 `description`。[S2]

Cursor CLI 自身提供 `/mcp`、`/plugin`、`/config`、`/sandbox`、`/update` 等内置 slash commands。[S11]

**UNKNOWN**：Plugin `commands/` 是否在 CLI 与 IDE 完全相同地发现和执行。

## 5. Hooks、信任和 CLI 边界

### 5.1 Hook 配置

Hooks 是通过 stdio 交换 JSON 的本地子进程，可观察、阻止或修改 Agent loop 行为。Cursor Plugin 的标准位置是 `hooks/hooks.json`。[S2][S10]

配置优先级为：[S10]

1. Enterprise
2. Team
3. Project：`<project>/.cursor/hooks.json`
4. User：`~/.cursor/hooks.json`

Project Hooks 只在 trusted workspace 中运行。[S10]

### 5.2 `beforeSubmitPrompt`

该事件在用户点击发送后、后端请求前执行。当前输出 schema 只有：[S10]

```json
{
  "continue": true,
  "user_message": "阻止时显示给用户的消息"
}
```

因此：

- allow/block prompt：**SUPPORTED**。
- 改写 prompt 或通过该事件注入额外 instructions：**UNSUPPORTED by current schema**。

### 5.3 CLI Hooks

- `workspaceOpen` 明确运行于 Cursor desktop app 和 CLI，并可返回 `pluginPaths`。[S10]
- 2.4 公告记录了 CLI 的 team/MDM Hooks 支持和 Hook 覆盖扩展。[S19]
- 当前 Hooks 页面没有给出每个事件在 CLI 的完整支持矩阵。

所以：

- CLI Hooks 整体：**PARTIAL**。
- CLI `beforeSubmitPrompt`：**UNKNOWN until tested**。
- Plugin-delivered Hooks 在 CLI 的安装、信任、触发和更新 parity：**UNKNOWN until tested**。

### 5.4 Hook 失败模式

`beforeShellExecution` / `beforeMCPExecution` 在 Hook crash、timeout 或 invalid JSON 时默认 fail-open；安全关键 Hook 应显式设置 `failClosed: true`。[S10]

**UNKNOWN**：Cursor 是否提供逐条 Plugin Hook command 的独立 review/trust 对话框。官方资料只明确 workspace trust，没有说明与其他产品相同的 Hook review UX。

## 6. 权限和 Marketplace 安全

Cursor Marketplace 的公开 Plugin 必须开源并经过人工审核；官方说明不分发 binaries，但 Plugin/Skill 仍可包含 scripts。每次 Marketplace update 也要人工审核。[S3]

CLI permissions 包括：[S12][S13]

- `Shell(commandBase)`
- `Read(pathOrGlob)`
- `Write(pathOrGlob)`
- `WebFetch(domainOrPattern)`
- `Mcp(server:tool)`

CLI 还支持 `approvalMode`（allowlist、auto-review、unrestricted）以及 sandbox mode / network access。Project CLI config 当前只允许 permissions，其他 CLI settings 必须放在 global config。[S12]

## 7. 安装、启用、更新、卸载总表

| 对象 | 安装 | 启用/禁用 | 更新 | 卸载 |
| --- | --- | --- | --- | --- |
| Cursor CLI 本体 | 官方 curl / PowerShell installer。[S14] | 运行 `agent` | 默认自动更新；`agent update` 或 `/update`。[S11][S14] | **UNKNOWN**：安装页未记录卸载命令。 |
| 公开 Cursor Plugin | Marketplace / Customize；user 或 project scope。[S1] | 组件级管理；整包开关 **UNKNOWN** | 更新先经 Cursor 审核。[S3] | **UNKNOWN**：当前规范未给完整个人卸载步骤。 |
| Team Marketplace Plugin | GitHub repo Import from Repo。[S1] | Default Off / On / Required。[S1] | Auto Refresh 或手工 Refresh。[S1] | Required 不可卸载；Default On 可 opt out。[S1] |
| Local Plugin | `~/.cursor/plugins/local` + reload。[S1] | 取决于组件 | 改本地文件并 reload | **UNKNOWN**：文档未定义正式卸载流程。 |
| MCP server | Marketplace、install link 或 `mcp.json`。[S7] | Customize toggle。[S7] | npm server：移除、清 cache、重加；custom server：更新文件并重启。[S7] | Customize 可移除；完整 remote OAuth credential cleanup **UNKNOWN**。 |
| Rule | 文件、Customize、Team Dashboard、GitHub Remote Rule。[S8] | activation mode / enforce。[S8] | Remote Rule 称为 sync，但触发细节 **UNKNOWN** | **UNKNOWN**。 |
| Skill | 文件发现、Plugin、GitHub link。[S9] | 自动或手动 slash。[S9] | GitHub update 语义 **UNKNOWN** | **UNKNOWN**。 |
| VS Code extension | VS Code import、OpenVSX、VSIX。[S15][S16] | extension host 管理 | OpenVSX 可提供自动更新。[S16] | Cursor 官方来源未在本研究中单独定义，**UNKNOWN**。 |

## 8. 仓库 URL 原生分发判定

### 正式支持

1. **公开 Marketplace submission**：Plugin 托管在公开 Git repository，并把 repository link 提交给 Cursor 审核。[S2]
2. **Team Marketplace**：Dashboard → Plugins → Add Marketplace → Import from Repo；当前正式文档明确写 GitHub，并支持 branch refresh。[S1]
3. **Rules**：Remote Rule (Github) 接受 GitHub repository URL。[S8]
4. **Skills**：官方页称可从 GitHub repository links 安装，但 lifecycle 说明不完整。[S9]
5. **本地开发**：filesystem copy/symlink，不是 repo URL 安装。[S1]

### 未被正式资料完整支持

- 个人任意 GitHub repo URL 的稳定 Plugin 安装命令：**UNKNOWN**。
- 个人 repo URL Plugin 的 update/uninstall 语义：**UNKNOWN**。
- CLI 通过 repo URL 完成 install/update/uninstall 的正式子命令：**UNKNOWN**。
- VS Code extension 从源码 repository URL 直接安装：**UNKNOWN**；已核实路径只有 OpenVSX、VSIX、VS Code profile import。[S15][S16]

因此，SpringBrand 的正式分发主路径应是：

- 公共用户：Cursor Marketplace。
- 团队/企业：Team Marketplace Import from Repo。
- 开发测试：`~/.cursor/plugins/local`。

## 9. 对 SpringBrand Cursor Adapter 的最小结论

### 桌面 IDE

官方能力足以承载一个 Cursor Plugin：[S1][S2][S4]

- `skills/springbrand-resource-discovery/SKILL.md`
- 根 `mcp.json`，远端 URL 为 `https://connector.springbrand.ai/mcp`
- 如确有必要，`hooks/hooks.json`
- `.cursor-plugin/plugin.json`

### Cursor CLI

只能确认：[S1][S7][S11][S19]

- Skills：**SUPPORTED**。
- MCP：**SUPPORTED（协议/配置层）**；SpringBrand OAuth 流程需实测。
- `/plugin` 管理入口：**SUPPORTED**。
- `beforeSubmitPrompt`：**UNKNOWN**。
- Plugin custom commands / agents / 全部 Hooks parity：**UNKNOWN**。

因此桌面与 CLI 必须分别做安装、Skill 可见性、MCP OAuth、Hook、更新和卸载证据，不能用桌面成功替代 CLI 验收。

## 10. 明确保留的 UNKNOWN / UNSUPPORTED

1. **UNKNOWN**：个人/项目 Cursor Plugin 的完整卸载步骤和 CLI uninstall 子命令。
2. **UNKNOWN**：公开 Marketplace 已安装 Plugin 的客户端更新触发时机。
3. **UNKNOWN**：CLI OAuth 命令、callback、token storage 和 logout。
4. **UNKNOWN**：Plugin 提供的 `beforeSubmitPrompt` 是否在 CLI 运行。
5. **UNKNOWN**：Plugin commands、custom agents、全部 Hooks 的 CLI parity。
6. **UNKNOWN**：VS Code extension API 注册的 MCP 是否传播到 CLI。
7. **UNKNOWN**：逐条 Plugin Hook command 的独立 review/trust UX。
8. **UNSUPPORTED by current schema**：`beforeSubmitPrompt` 改写 prompt。
9. **UNSUPPORTED / 不适用**：把 VS Code extension 安装成功当作 Cursor Agent Plugin 或 CLI 集成成功。
10. **UNKNOWN**：个人任意 repository URL 的稳定 Plugin install/update/uninstall 合同。

## 官方来源

所有来源访问日期均为 **2026-08-17**。

| ID | 来源 | URL |
| --- | --- | --- |
| S1 | Cursor Docs — Plugins | https://cursor.com/docs/plugins |
| S2 | Cursor Docs — Plugins reference | https://cursor.com/docs/reference/plugins |
| S3 | Cursor Help — Marketplace security | https://cursor.com/help/security-and-privacy/marketplace-security |
| S4 | Cursor 官方仓库 — plugin-template，commit `46216072ac5750f782f95bb325b4d12b7c3ae9c9` | https://github.com/cursor/plugin-template/tree/46216072ac5750f782f95bb325b4d12b7c3ae9c9 |
| S5 | Cursor Changelog 2.5 — Plugins, Sandbox Access Controls, and Async Subagents，发布 2026-02-17 | https://cursor.com/changelog/2-5 |
| S7 | Cursor Docs — Model Context Protocol (MCP) | https://cursor.com/docs/mcp |
| S8 | Cursor Docs — Rules | https://cursor.com/docs/rules |
| S9 | Cursor Docs — Agent Skills | https://cursor.com/docs/skills |
| S10 | Cursor Docs — Hooks | https://cursor.com/docs/hooks |
| S11 | Cursor Docs — CLI Slash commands | https://cursor.com/docs/cli/reference/slash-commands |
| S12 | Cursor Docs — CLI Configuration | https://cursor.com/docs/cli/reference/configuration |
| S13 | Cursor Docs — CLI Permissions | https://cursor.com/docs/cli/reference/permissions |
| S14 | Cursor Docs — CLI Installation | https://cursor.com/docs/cli/installation |
| S15 | Cursor Docs — VS Code Migration | https://cursor.com/docs/configuration/migrations/vscode |
| S16 | Cursor 官方公告 — Cursor is switching to Open VSX，发布 2025-06-25 | https://forum.cursor.com/t/cursor-is-switching-to-open-vsx/108193 |
| S19 | Cursor Changelog 2.4 — Subagents, Skills, and Image Generation，发布 2026-01-22 | https://cursor.com/changelog/2-4 |
| S20 | Cursor Docs — Use Agent in CLI | https://cursor.com/docs/cli/using |
