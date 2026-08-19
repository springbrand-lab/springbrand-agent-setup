# Claude 原生集成能力核实：CLI 与桌面 Code

- **核实日期**：2026-08-17
- **资料边界**：仅使用 Anthropic 官方文档、官方帮助中心、官方 GitHub 项目；不采用第三方教程或推测。
- **目标**：判断 SpringBrand 能否通过 Claude 的原生 Plugin、Marketplace、MCP、OAuth、Skill/Command、Hook 与权限机制，同时接入 Claude Code CLI 和用户可能称为“Claude Code desktop”的桌面产品。
- **状态词**：
  - **supported**：官方资料明确支持。
  - **unsupported**：官方资料明确不支持，或现有原生入口明确只支持另一种制品/传输。
  - **unknown**：截至核实日期，官方资料没有给出足够明确的行为保证，需要原生实测。

## 1. 结论摘要

1. **“Claude Code desktop”不是另一套独立 CLI 产品。** Anthropic 当前把桌面安装包称为 **Claude Desktop app / Claude desktop app**；应用内有 **Chat、Cowork、Code** 三个 tab。Claude Code 文档把 Code tab 称为 **Claude Code Desktop** 或 **Claude Code on desktop**。本研究的“桌面 Code”专指 Claude Desktop app 的 **Code tab**，不把 Chat、Cowork、Claude Code on the web、Claude in Chrome 混入。[A01][A02][A03]
2. **Claude Code CLI 与桌面本地 Code session 使用同一 Claude Code 引擎，并共享核心本地配置。** `CLAUDE.md`、`~/.claude.json`、`~/.claude/settings.json`、项目 `.mcp.json`、Hooks、Skills、权限规则和本地 Plugin 安装可在两者间复用；会话历史仍然分开。[A03]
3. **一个 Claude Code Plugin 可以原生同时覆盖 CLI 与桌面本地 Code session。** Plugin 可打包 Skills、Commands、Agents、Hooks、MCP servers 和 LSP 配置；桌面 Code 提供 Plugin 浏览、安装、启用、禁用、卸载 UI。[A03][A06][A07][A09]
4. **SpringBrand 的生产远程 MCP 可直接使用 Streamable HTTP。** Claude Code 推荐远程服务器使用 HTTP；JSON 中 `type: "http"` 为规范写法，同时接受 MCP 规范名称 `streamable-http` 作为别名。SSE 已弃用。[A11]
5. **Claude Code 原生支持远程 HTTP MCP 的 OAuth 2.0。** 支持自动发现、Dynamic Client Registration、Client ID Metadata Document、预注册 client ID/secret、token 刷新，以及 `/mcp` 和 `claude mcp login/logout` 流程。[A11]
6. **满足“每次用户提交前运行”的原生 Hook 是 `UserPromptSubmit`。** 它在 Claude 处理 prompt 前触发，可注入 `additionalContext` 或阻止 prompt；同一 Hook 生命周期适用于 terminal、IDE、Desktop 和 web 的 Claude Code 引擎。[A13]
7. **Plugin 安装本身是主要信任边界，但不是 Hook 的逐次执行确认。** Plugin 详情可列出将安装的 Skills、Hooks、MCP 等组件，官方明确警告 Plugin/Marketplace 可用当前用户权限执行任意代码；启用后 Hook 自动运行，命令 Hook 具有完整用户权限。[A06][A13]
8. **持久安装支持“仓库作为 Marketplace”，但不支持把任意裸 Plugin 仓库 URL 直接交给 `claude plugin install`。** 原生持久路径是：先添加含 `.claude-plugin/marketplace.json` 的 GitHub/Git 仓库，再按 `plugin@marketplace` 安装。`--plugin-url` 只接受 Plugin `.zip` URL，并且只对当前 session 生效。[A06][A08][A09][A10]
9. **不要把 MCPB/Desktop Extensions 当作 Claude Code Plugin。** MCPB（旧称 DXT/Desktop Extensions）是面向 macOS/Windows Claude Desktop 的“一键安装本地 MCP server”压缩包，主要是本地 MCP 分发；它不是远程 Streamable HTTP Plugin、Skill 或 Hook 的替代品。[A16]
10. **Chat/Cowork 的账号级 Customize/Plugin/Connector 是另一配置平面。** Cowork 从 claude.ai 账号同步 Skills、Plugins、Connectors，而不是读取 CLI 的 `~/.claude`；因此“安装到 Claude Desktop 的 Customize”不等于“安装到桌面 Code 的本地 Claude Code Plugin”。[A03][A17][A18]

## 2. 产品名称与边界

| 用户可能使用的名称 | 官方可核实产品/表面 | 本研究是否作为目标 | 配置边界 |
|---|---|---:|---|
| Claude Code CLI | 终端中的 `claude` | 是 | 本机 `~/.claude*`、项目 `.claude/`、`.mcp.json`。[A01][A05] |
| “Claude Code desktop” | Claude Desktop app 的 **Code tab**；官方也称 Claude Code Desktop | 是 | 本地 Code session 与 CLI 共享核心配置；桌面 app 自己还有额外配置。[A02][A03] |
| Claude Desktop | 包含 Chat、Cowork、Code 三个 tab 的桌面应用 | 仅用于辨识 | 不是单一 agent surface。[A02][A03] |
| Claude Chat | Desktop/claude.ai 的通用对话表面 | 否 | 账号级 Customize；无本地代码目录访问。[A02][A17] |
| Cowork | Desktop 中的后台 agent 表面 | 否 | 账号同步 Skills/Plugins/Connectors，不读取 CLI `~/.claude`。[A03][A17] |
| Claude Code on the web / cloud session | 浏览器或云端 Code session | 否，本研究不把它当 desktop | 不读取本机 user Plugin；需仓库声明或账号同步的能力。[A03][A12] |
| Claude in Chrome | 浏览器扩展 | 否 | 浏览器会话与页面控制，不是 Claude Code Plugin host。[A03] |
| MCPB / Desktop Extensions | 本地 MCP server bundle 格式 | 否，不作为 SpringBrand 远程 MCP 主路径 | `.mcpb` 本地压缩包；macOS/Windows Claude Desktop 可单击安装。[A16] |

### 精确结论

- **目标桌面 host 应命名为“Claude Desktop app 的本地 Code tab（Claude Code Desktop）”。** 不应在规格中写成一个独立的“Claude Code Desktop 应用”。[A02][A03]
- **CLI 与桌面 Code 可以共用一个 Claude Code Plugin adapter。** 目前没有官方证据要求再造一套桌面专用 manifest。[A03][A09]
- **Chat/Cowork 若未来也要接入，应单独建模。** 它们可使用 Claude 的账号级 Plugin/Connector，但安装状态和配置来源与本地 CLI/Code 不相同。[A03][A17][A18]

## 3. 版本与平台基线

### 3.1 Claude Code CLI

- 截至 **2026-08-17**，官方 changelog 顶部最新公开版本为 **Claude Code 2.1.233，发布日期 2026-08-14**。[A04]
- 原生安装支持 macOS 13+、Windows 10 1809+/Windows Server 2019+、Ubuntu 20.04+、Debian 10+、Alpine 3.19+，x64 或 ARM64。[A05]
- 官方推荐 native installer；native 安装后台自动更新。Homebrew、WinGet 和 Linux package manager 默认由各自包管理器更新。[A05]
- 对 SpringBrand adapter，**建议验证基线锁定为 2.1.233 或更新版本**，不是因为 Plugin/MCP/Hook 只在该版本存在，而是因为相关安全、Marketplace、OAuth 和 Desktop 兼容修复持续落在 2.1.x。[A04]

### 3.2 相关功能的已知最低版本

| 功能 | 官方最低版本/变更点 | 结论 |
|---|---:|---|
| `claude mcp login/logout` | `mcp login` 从 2.1.186；无本地浏览器的 URL/paste 流程从 2.1.191 | supported。[A11] |
| 未认证 MCP 启动提醒 | 2.1.193 | supported。[A11] |
| 外部来源 Plugin 不再因项目 `enabledPlugins` 自动安装 | 2.1.195 | 安装仍需用户明确执行；适合作为供应链信任边界。[A06] |
| `streamable-http` 作为 `http` 别名 | 当前文档明确支持；未给出引入版本 | supported，最低版本 unknown。[A11] |
| MCP tool `anthropic/requiresUserInteraction` | 2.1.199 | supported。[A11] |
| Marketplace `archive` Plugin source | 2.1.224 | supported；仅当采用 HTTPS zip 分发时需要。[A08] |
| 固定 OAuth callback 的 `localhost` 修复 | 2.1.231；2.1.229 曾使用 `127.0.0.1` | 需要固定 redirect URI 时应避开 2.1.229。[A11] |
| 当前最新公开 CLI | 2.1.233，2026-08-14 | 核实日期内 latest。[A04] |

### 3.3 Claude Desktop app / Code tab

- macOS、Windows 有官方安装包；Linux Desktop 于当前文档中为 beta，要求 Ubuntu 22.04+ 或 Debian 12+，x86_64/arm64。[A02][A15]
- macOS/Windows app 启动时自动检查/安装更新；Linux 通过 apt 更新。[A03][A15]
- Desktop app 自带 Claude Code 引擎，**不需要另外安装 CLI**；只有想在终端运行 `claude` 时才单独装 CLI。[A02]
- **unknown：官方公开文档未给出“Desktop app build number ↔ 内嵌 Claude Code engine 版本”的稳定映射，也未给出 Plugin/MCP/Hook 的最低 Desktop app build。** 因而桌面验收应记录 About Claude 的 app version，并在 session 内记录可见的 Claude Code engine/version 证据，而不能仅写“最新版”。[A03][A04]

## 4. 能力矩阵

| 能力 | CLI | Desktop 本地 Code tab | 结论 |
|---|---|---|---|
| Claude Code Plugin | `/plugin` 与 `claude plugin ...` | `+` → Plugins / Plugin browser / Manage plugins | 两者 supported，共用本地安装和配置。[A03][A06][A09] |
| Marketplace | GitHub、任意 Git URL、本地路径、远程 `marketplace.json` | 从已配置 Marketplace 浏览和安装 | 共享配置；Desktop GUI 直接录入任意 repo URL 是否支持为 unknown。[A03][A06] |
| Skill | `~/.claude/skills`、项目 `.claude/skills`、Plugin `skills/` | 本地 session 同样加载；UI 可浏览 Slash commands | supported。[A03][A12] |
| Legacy custom command | `.claude/commands/*.md` | 同一引擎可用 | supported，但官方已将 custom commands 合并到 Skills；新制品应优先 Skill。[A12] |
| Remote MCP Streamable HTTP | `type: "http"` 或 `streamable-http` | 共享 `.mcp.json`/`~/.claude.json`；也有 Connectors UI | supported。[A03][A11] |
| MCP OAuth 2.0 | `/mcp`、`claude mcp login/logout` | 引擎能力可用；专用 Desktop Plugin-MCP OAuth GUI 流程未明确记录 | CLI supported；纯 GUI 流程 unknown。[A03][A11] |
| Hook | settings 或 Plugin `hooks/hooks.json` | 同样触发 Hook lifecycle | supported。[A13] |
| `UserPromptSubmit` | 提交 prompt 后、模型处理前 | 同样 | supported，可注入 context 或 block。[A13] |
| 权限模式 | 全部模式；含 `dontAsk` | Manual、Accept edits、Plan、Auto、受控的 Bypass；不含 `dontAsk` | supported，但 UI/模式集合不完全相同。[A03][A14] |
| Workspace trust | 交互式 trust dialog、项目 MCP approval、Plugin trust warning | 同一引擎规则适用于本地 Code session | supported；headless `-p` 有更弱的提示边界，见第 9 节。[A10][A13][A14] |
| 直接仓库 URL 持久安装 | 先 add Marketplace repo，再 install Plugin | 从已配置 Marketplace 安装 | supported 作为“两步 Marketplace”；裸 repo URL 直接 `plugin install` unsupported。[A06][A08][A10] |
| `.zip` URL 临时加载 | `--plugin-url`，当前 session | Desktop 文档未给 UI 等价入口 | CLI supported、非持久；Desktop unknown。[A09][A10] |

## 5. 原生 Plugin 与 Marketplace

### 5.1 Plugin 制品

Claude Code Plugin 是一个自包含目录，可原生贡献以下组件：[A07][A09]

- `skills/<name>/SKILL.md`
- `commands/*.md`（兼容旧 custom command）
- `agents/`
- `hooks/hooks.json`
- `.mcp.json` 或 `plugin.json` 内联 MCP
- `.lsp.json`
- 可选 `.claude-plugin/plugin.json` manifest

Manifest 是可选的，但分发版应使用 `.claude-plugin/plugin.json` 来声明稳定名称、版本、描述、仓库和组件路径。Plugin 根目录的 `CLAUDE.md` 不作为 Plugin context 加载；要提供 agent 指令，应放在 Skill、Agent 或 Hook 中。[A09]

**SpringBrand 最小原生制品边界可由现有需求直接得到：**

```text
springbrand-claude-plugin/
├── .claude-plugin/plugin.json
├── .mcp.json
├── hooks/hooks.json
└── skills/springbrand-plugin-discovery/SKILL.md
```

这只是官方能力允许的最小边界，不是本研究阶段的实现提交。

### 5.2 安装、启用、更新、卸载

CLI 原生生命周期：[A06][A09]

```bash
claude plugin install springbrand@springbrand --scope user
claude plugin disable springbrand@springbrand
claude plugin enable springbrand@springbrand
claude plugin update springbrand@springbrand
claude plugin uninstall springbrand@springbrand
```

- 安装 scope：`user`、`project`、`local`；managed Plugin 由管理员控制。[A06][A09]
- `project` scope 写入 `.claude/settings.json` 的 `enabledPlugins`，可与仓库协作者共享声明。[A09]
- Desktop 本地 Code tab 提供 Add plugin、Manage plugins、enable、disable、uninstall UI。[A03]
- Desktop 与 CLI 共享安装状态和配置，因此 CLI 更新的 Plugin 会供 Desktop 后续 session 使用。[A03][A06]
- `/reload-plugins` 可在部分情况下无需重启加载新版本；Hooks、MCP、LSP 路径更新需要 reload/restart 才完全切换。[A06][A09]
- Marketplace 可后台自动更新；官方 Marketplace 默认启用，第三方/本地 Marketplace 默认关闭。运行中的 session 继续用启动时版本，更新后 reload 或下次启动生效。[A06]
- **unknown：Desktop Code Plugin manager 是否提供独立的“立即更新单个 Plugin”按钮。** 官方桌面文档明确安装/启用/禁用/卸载，但没有明确描述手动 update UI；可依赖 Marketplace auto-update 或 CLI `claude plugin update`。[A03][A06][A09]

### 5.3 安装前可见性与信任

- Plugin 详情可显示 **Will install**，列出 Commands、Agents、Skills、Hooks、MCP/LSP servers；自定义 Marketplace 元数据不完整时，可能只显示“安装时发现组件”。[A06]
- 官方警告 Plugin 和 Marketplace 是高信任组件，可用当前用户权限执行任意代码；只应安装可信来源。[A06]
- 命令 Hook 启用后以用户完整权限执行，可访问、修改或删除该用户可访问的文件。[A13]
- `claude plugin details` 可列出组件 inventory 和预计 context cost；`/hooks` 可查看已配置 Hook 来源和完整 handler，但 `/hooks` 是只读浏览器。[A09][A13]
- **不存在官方记录的“每次 Plugin Hook 执行前重新弹窗批准”机制。** 原生信任动作是添加可信 Marketplace、审查并安装/启用 Plugin；此后 Hook 自动执行。需要逐次确认的行为应落在 MCP tool 权限或 `requiresUserInteraction`，不能依赖 Hook 自身弹窗。[A06][A11][A13]

## 6. 从仓库 URL 安装

### 6.1 持久安装：supported，但必须通过 Marketplace

Claude Code 可原生添加以下 Marketplace 来源：[A06]

- GitHub `owner/repo`
- 任意 HTTPS/SSH Git URL
- 本地目录或 `marketplace.json`
- 远程 `marketplace.json` URL

Git 仓库根需要包含 `.claude-plugin/marketplace.json`。典型持久安装为：[A06][A08]

```text
/plugin marketplace add springbrand-lab/springbrand-agent-setup
/plugin install springbrand@<marketplace-name>
```

Marketplace 条目本身又可以把 Plugin source 指向：[A08]

- Marketplace 仓库内相对目录
- GitHub repository
- 通用 Git URL
- Git repository 子目录
- npm package
- HTTPS zip archive
- 受控 command source

因此，**“从仓库 URL 原生安装”应定义为“从仓库添加 Marketplace，再从 Marketplace 安装 Plugin”**，而不是自造 installer。

### 6.2 裸 Plugin URL

- `claude plugin install` 的参数是 Marketplace 中的 Plugin 名称，不接受任意裸 Git repo URL。[A09]
- `claude --plugin-url https://.../plugin.zip` 支持从 URL 获取 `.zip`，但只加载当前 session，不产生持久安装记录。[A09][A10]
- `claude --plugin-dir` 可临时加载本地目录或 `.zip`，也只对当前 session 生效。[A09][A10]
- **unsupported：把一个不含 Marketplace catalog 的裸 Git repository URL 直接持久安装为 Plugin。**
- **unknown：Desktop Code 的 Plugin browser 是否允许直接输入任意 Marketplace Git URL。** 官方只保证它从“configured marketplaces”展示和安装；可靠路径是先用 CLI 添加 Marketplace，或通过 `extraKnownMarketplaces`/managed settings 配置，再在 Desktop 安装。[A03][A06]

## 7. MCP：Remote Streamable HTTP 与 OAuth

### 7.1 传输

Claude Code 对远程 MCP 的当前官方建议是 HTTP：[A11]

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

- `type: "http"` 是 Claude Code 文档主写法。[A11]
- `type: "streamable-http"` 被接受为 `http` 的别名，方便直接使用 MCP 规范配置。[A11]
- SSE 已弃用；只有服务端仍仅暴露 SSE 时才使用 `type: "sse"`。[A11]
- Plugin 根 `.mcp.json` 使用标准 MCP 配置；Plugin 启用时其 MCP server 自动进入 Claude 工具集。[A09]

### 7.2 OAuth 2.0

Claude Code 对远程 HTTP MCP 原生支持：[A11]

- 401/403 检测和“需要认证”状态
- `/mcp` 浏览器登录
- `claude mcp login <name>` 与 `logout`
- OAuth discovery 和 `WWW-Authenticate`
- Dynamic Client Registration
- Client ID Metadata Document 自动发现
- 预配置 `clientId`、交互式/环境变量 client secret
- 固定 localhost callback port
- 安全存储 token、自动刷新、失败后重新认证

关键限制：[A11]

- OAuth 适用于 HTTP server；WebSocket transport 不支持 OAuth。
- 非交互 `claude -p` 不能自己完成 OAuth UI；必须预先在交互 session 或 `claude mcp login` 中授权。
- 若显式配置 `headers.Authorization` 且被服务器拒绝，Claude Code 报连接失败，不自动回退 OAuth。

### 7.3 Desktop Code

- Desktop 本地 Code session 读取与 CLI 相同的 `~/.claude.json` 和项目 `.mcp.json`，因此上述远程 HTTP 配置可同时工作。[A03]
- Desktop 的 Connectors UI 是 MCP 的图形化安装/连接入口，适合官方目录或账号级 Connector；未列出的集成仍可通过 settings files 添加。[A03][A19]
- Desktop 还会把 `claude_desktop_config.json` 中的 MCP server 注入本地 Code session；但 standalone CLI **不读取**该文件，只能通过 `claude mcp add-from-claude-desktop` 导入。[A03][A11]
- **unknown：安装一个带远程 OAuth MCP 的 Claude Code Plugin 后，Desktop Code 是否提供完整、无 CLI 的 Plugin-MCP OAuth 登录 UI。** 官方资料保证共享配置和 Claude Code OAuth 能力，但 OAuth 操作文档明确写的是 `/mcp`/`claude mcp login`，Desktop 文档没有给出该场景的专用 UI。首个桌面 beta 验收必须原生实测。[A03][A11]
- **unknown：OAuth token 存储是否在 standalone CLI 与 Desktop 内嵌引擎间被官方保证为同一 credential record。** 配置文件共享已明确，OAuth credential store 的跨宿主共享没有同等级明确声明。[A03][A11]

## 8. Skill 与 Command

- Claude Code Skill 是带 YAML frontmatter 的 `SKILL.md`；Claude 可根据 description 自动调用，也可由用户 `/skill-name` 显式调用。[A12]
- Personal Skill：`~/.claude/skills/<name>/SKILL.md`；Project Skill：`.claude/skills/<name>/SKILL.md`；Plugin Skill：`<plugin>/skills/<name>/SKILL.md`。[A12]
- Plugin Skill 始终带 namespace，例如 `/springbrand:springbrand-plugin-discovery`，避免与 personal/project Skill 冲突。[A07][A12]
- `.claude/commands/*.md` 仍兼容，但官方已把 custom commands 合并到 Skills；若同名，Skill 优先。[A12]
- Desktop 本地 Code session 可从 prompt 的 Slash commands UI 浏览 built-in commands、custom Skills、project Skills 和 Plugin Skills。[A03]
- 本地 Code 与 CLI 读取同一 personal/project/plugin Skills。[A03][A12]
- Cowork/cloud 主要读取 claude.ai 账号启用的 synced Skills；Cowork 不读取本机 `~/.claude/skills`。这是另一分发面。[A03][A12]

### 对 SpringBrand 的直接能力结论

现有 `springbrand-plugin-discovery` 可作为 Plugin Skill 复用其指令内容，但需要遵守 Claude Skill frontmatter 和 namespace 规则。为了让 Claude 自动发现，应保留准确 `description`；为了让用户可审计/手动验证，应同时允许显式 `/springbrand:springbrand-plugin-discovery` 调用。[A12]

## 9. Hook

### 9.1 生命周期与打包

- Hook 可定义在 user/project/local settings、managed settings、Plugin `hooks/hooks.json`、Skill 或 Subagent frontmatter。[A13]
- Plugin 启用后，其 Hooks 与 user/project Hooks 合并。[A13]
- Hook handler 可为 `command`、`http`、`mcp_tool`、`prompt` 或 `agent`。[A09][A13]
- Hook 在 terminal、IDE、Desktop app 和 Claude Code web 使用相同事件模型。[A13]

### 9.2 `UserPromptSubmit`

`UserPromptSubmit` 在用户提交 prompt 后、Claude 处理前触发，能够：[A13]

- 读取原始 `prompt`
- 输出纯文本或 JSON `additionalContext` 注入模型 context
- 返回 `decision: "block"` 阻止 prompt
- 设置 session title

这就是 SpringBrand “eligible task 必须先执行 Plugin discovery，再进入规划、追问或产出”的最接近原生 pre-prompt seam。[A13]

但有一个必须纳入验收的行为：[A13]

- `UserPromptSubmit` 的 command/http/mcp_tool Hook 默认 timeout 为 30 秒。
- timeout 时 Hook 被取消，输出和 `additionalContext` 被丢弃，原 prompt 仍继续进入 Claude，即 **fail open**。
- 因此 Hook 不应直接承担长耗时研究或不受限网络调用；它更适合快速注入“先调用 SpringBrand Skill/MCP”的约束，实际 discovery 由 agent 在本轮执行。

### 9.3 权限与信任

- 命令 Hook 以用户完整权限运行，不受普通 Bash tool sandbox/permission prompt 的逐次保护。[A13]
- 交互 session 会在 workspace trust 前暂缓 settings-file Hooks；但 `claude -p`/SDK 不显示 trust dialog，并将目录视为可运行这些 settings Hooks。[A13][A14]
- 项目 `.mcp.json` 在交互 session 需要用户批准；仓库自身提交的 approval 不能批准自己的 server。[A11][A14]
- **重要风险**：官方的“what runs before trust”表明确显示，一些仓库内容在 `-p`/SDK 中仍可运行；自动化不能把交互式 workspace trust 当作完整供应链隔离。[A14]
- 对用户安装的 Marketplace Plugin，显式安装/启用是主要信任动作；之后 Hook 自动执行。[A06][A13]

## 10. 权限与信任模型

### 10.1 Plugin

- 安装前应审查 Marketplace 来源、Plugin homepage/repository、组件 inventory，特别是 Hooks、MCP、command source 和可执行文件。[A06][A09]
- 第三方 Marketplace 默认不自动更新；用户可显式启用，组织可用 `strictKnownMarketplaces`、`blockedMarketplaces`、`disableSideloadFlags` 等 managed settings 限制来源。[A06][A14]
- 从 2.1.195 起，项目配置仅“enable”一个外部来源 Plugin 不足以自动安装它；用户仍需执行安装。[A06]

### 10.2 MCP

- 项目 `.mcp.json` server 在交互 session 中需要 approval；`claude mcp list/get` 会显示 pending/rejected 状态。[A11]
- MCP tool 默认经过 Claude Code permission flow；服务端可用 `_meta["anthropic/requiresUserInteraction"] = true` 强制每次人工批准，该能力要求 2.1.199+。[A11]
- SpringBrand 若有必须每次由真人确认的高风险工具，应在 MCP tool metadata 标记 `requiresUserInteraction`，而不是依赖 Skill 文案或 Hook。[A11]

### 10.3 Desktop

- Desktop 本地 Code 使用同一权限规则；UI 暴露 Manual、Accept edits、Plan、Auto 和受控 Bypass。[A03][A14]
- `dontAsk` 仅 CLI 有，不在 Desktop。[A03]
- Desktop 的 Bypass 仍不能跳过组织强制 ask、`requiresUserInteraction`、部分高风险 desktop action 等硬限制。[A03][A11]

## 11. CLI 与 Desktop 配置是否共享

### 11.1 明确共享

Desktop 本地 Code 与 CLI 共享：[A03]

- 项目 `CLAUDE.md` / `CLAUDE.local.md`
- `~/.claude.json`
- `~/.claude/settings.json`
- 项目 `.claude/settings.json` / `.claude/settings.local.json`
- `.mcp.json`
- Hooks
- Skills
- Permission rules
- 本地 Marketplace/Plugin 安装与启用状态

因此，**SpringBrand 不需要一个“CLI manifest”加一个“Desktop Code manifest”**；一个 Claude Code Plugin package 即可覆盖两者的本地 session。[A03][A09]

### 11.2 不完全共享与例外

- CLI 与 Desktop 会话历史分开。[A03]
- Desktop 会额外读取 `claude_desktop_config.json` 到本地 Code；standalone CLI 不读取它。[A03]
- 若同名 server 同时在 `claude_desktop_config.json` 与 Claude Code config 中存在，Desktop Code 采用前者；这与 standalone CLI 的正常 MCP scope precedence 不完全一致。[A03]
- Desktop 的 Cowork/Chat 使用账号级 Customize，不读取 CLI `~/.claude`。[A03]
- Cloud Code session 不继承本机 user Plugin；需要在仓库 `.claude/settings.json` 声明，或使用云端支持的账号级能力。[A03][A12]
- Desktop WSL session 当前明确 **不支持 Plugins**；本研究的“共享 Plugin”结论只覆盖本地和官方明确支持的 SSH Code session，不覆盖 WSL。[A03]

## 12. 不应混用的其他官方机制

### 12.1 MCPB / Desktop Extensions

MCPB（旧称 DXT/Desktop Extensions）是 `.mcpb` zip bundle，包含本地 MCP server 和 `manifest.json`；Claude for macOS/Windows 可单击安装，并提供本地配置、自动更新和目录体验。[A16]

对 SpringBrand 当前目标：

- **unsupported 作为远程 Streamable HTTP 主分发制品**：MCPB 的官方定位是本地 MCP server bundle，不是远程 MCP URL 声明。[A16]
- **unsupported 作为 Skill/Hook/Claude Code Plugin 替代品**：MCPB 不提供 Claude Code Plugin 的 Skill、Hook、Agent package 边界。[A09][A16]
- SpringBrand 已有生产 remote MCP endpoint，因此没有理由为此目标引入本地 server bundle。

### 12.2 Claude Chat/Cowork 的账号级 Plugin/Connector

Claude 的通用 Chat/Cowork 也有 Marketplace/Plugin/Connector，并能从 GitHub Marketplace repository URL 添加自定义 Marketplace；它们在账号级 Customize 中管理。[A17][A18]

但：[A03][A17][A18]

- 账号级安装状态不等于 CLI/Desktop 本地 Code Plugin 安装状态。
- 通用 Claude Plugin 的跨表面文档重点是 Skills + remote MCP Connector；不能据此假定 Claude Code-only Hook/Agent 在 Chat/Cowork 可运行。
- 若未来要求“Claude Chat/Cowork 也接入”，应另做一轮表面能力与发布审核，不应把本次 Code adapter 宣称为全 Claude 产品覆盖。

## 13. Unknown / Unsupported 清单

| 项目 | 状态 | 原因/后续验证 |
|---|---|---|
| CLI 原生 Plugin + Marketplace + Skill + Hook + remote HTTP MCP | supported | 官方文档完整覆盖。[A06][A09][A11][A12][A13] |
| Desktop 本地 Code 复用同一 Plugin | supported | 官方明确同引擎、共享配置，并有 Plugin manager。[A03] |
| Desktop Code 中 Plugin-bundled remote HTTP MCP | supported | Plugin MCP 标准配置 + Desktop 共享 `.mcp.json`。[A03][A09][A11] |
| Desktop Code 中完全无 CLI 的 Plugin-MCP OAuth 登录 | unknown | 官方未描述该精确 UI 流程；需 native beta evidence。[A03][A11] |
| Desktop Code Plugin manager 输入任意 Git repo Marketplace URL | unknown | 文档只写“configured marketplaces”；CLI 路径明确。[A03][A06] |
| Desktop Plugin manager 手动 update 单个 Plugin | unknown | enable/disable/uninstall 明确，手动 update UI 未明确。[A03][A09] |
| Desktop app build 与内嵌 engine 版本映射 | unknown | 官方只公开 app About version 和 CLI changelog，无稳定映射。[A03][A04] |
| OAuth credential 是否被 CLI 与 Desktop 内嵌 engine 明确保证共享 | unknown | 配置共享明确，credential record 共享未明确。[A03][A11] |
| 裸 Git repo URL 直接持久 `plugin install` | unsupported | 必须先是 Marketplace，或只用 session-only zip sideload。[A06][A09][A10] |
| Desktop WSL session 使用 Plugin | unsupported | 官方明确 Plugins unavailable in WSL sessions。[A03] |
| 用户在 Desktop 安装的本地 Plugin自动进入 cloud Code session | unsupported | cloud 需 repo declaration；本地安装不带过去。[A03] |
| MCPB 安装 SpringBrand remote Streamable HTTP + Skill + Hook | unsupported | MCPB 是本地 MCP bundle，不是 Claude Code Plugin。[A16] |
| 把 Chat/Cowork Customize 安装当成 CLI/Code 安装 | unsupported | 配置平面不同。[A03][A17] |

## 14. 对下一阶段规格的约束

以下是研究结论直接施加的边界，不是实现方案扩张：

1. **只需要一个 Claude Code Plugin adapter 覆盖 CLI + Desktop 本地 Code。** 不创建第二套 desktop manifest，除非原生实测发现 Desktop 额外要求。[A03][A09]
2. **使用 Claude 原生 Marketplace lifecycle。** Repository 根提供 `.claude-plugin/marketplace.json`，用户 add Marketplace 后 install Plugin；不写自定义安装器。[A06][A08]
3. **Plugin 最少只打包现有 SpringBrand Skill、production remote MCP 和一个 `UserPromptSubmit` Hook。** 不因“将来可能需要”引入 MCPB、本地 proxy、额外 agent 或共享多 host abstraction。[A09][A11][A13]
4. **MCP 声明使用 `type: "http"` + `https://connector.springbrand.ai/mcp`。** 不使用已弃用 SSE，不在仓库放 bearer token。[A11]
5. **OAuth 由 Claude Code 原生流程承担。** CLI 以 `claude mcp login`/`/mcp` 验收；Desktop 必须单独记录是否可从 UI 完成，不能用 CLI 成功代替 Desktop 成功。[A03][A11]
6. **Hook 只做快速 gate/context 注入。** `UserPromptSubmit` timeout 会 fail open，不把长耗时 discovery 直接塞进 Hook 进程。[A13]
7. **安装证据必须包含信任审查。** 记录 Marketplace 来源、Plugin component inventory、Hook 来源、MCP approval/OAuth、fresh session 行为。[A06][A11][A13]
8. **Chat/Cowork 与 MCPB 暂不纳入本 adapter 的成功声明。** 若产品目标扩展到这些表面，另开 adapter/验收范围。[A03][A16][A17]

## 15. 官方来源

所有来源访问日期均为 **2026-08-17**。

- **[A01] Claude Code overview** — https://code.claude.com/docs/en/overview — 访问：2026-08-17
- **[A02] Get started with the desktop app** — https://code.claude.com/docs/en/desktop-quickstart — 访问：2026-08-17
- **[A03] Desktop application / Claude Code Desktop reference** — https://code.claude.com/docs/en/desktop — 访问：2026-08-17
- **[A04] Claude Code changelog** — https://code.claude.com/docs/en/changelog — 访问：2026-08-17
- **[A05] Advanced setup** — https://code.claude.com/docs/en/setup — 访问：2026-08-17
- **[A06] Discover and install plugins through marketplaces** — https://code.claude.com/docs/en/discover-plugins — 访问：2026-08-17
- **[A07] Create plugins** — https://code.claude.com/docs/en/plugins — 访问：2026-08-17
- **[A08] Create and distribute a plugin marketplace** — https://code.claude.com/docs/en/plugin-marketplaces — 访问：2026-08-17
- **[A09] Plugins reference** — https://code.claude.com/docs/en/plugins-reference — 访问：2026-08-17
- **[A10] CLI reference** — https://code.claude.com/docs/en/cli-reference — 访问：2026-08-17
- **[A11] Connect Claude Code to tools via MCP** — https://code.claude.com/docs/en/mcp — 访问：2026-08-17
- **[A12] Extend Claude with skills** — https://code.claude.com/docs/en/skills — 访问：2026-08-17
- **[A13] Hooks reference** — https://code.claude.com/docs/en/hooks — 访问：2026-08-17
- **[A14] Configure permissions** — https://code.claude.com/docs/en/permissions — 访问：2026-08-17
- **[A15] Claude Desktop on Linux (beta)** — https://code.claude.com/docs/en/desktop-linux — 访问：2026-08-17
- **[A16] MCP Bundles (MCPB; formerly Desktop Extensions/DXT)** — https://github.com/anthropics/mcpb — 访问：2026-08-17（官方 URL 当前重定向至 Model Context Protocol organization）
- **[A17] Use plugins in Claude** — https://support.claude.com/en/articles/13837440-use-plugins-in-claude — 访问：2026-08-17
- **[A18] Connector building: What to build — plugin, MCP, or both** — https://claude.com/docs/connectors/building/what-to-build — 访问：2026-08-17
- **[A19] Getting started with custom connectors using remote MCP** — https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp — 访问：2026-08-17
