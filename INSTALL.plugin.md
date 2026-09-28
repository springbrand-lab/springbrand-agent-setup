# SpringBrand Plugin installation fallback — production

Use this document only after the preferred CLI in [`INSTALL.md`](./INSTALL.md)
cannot run or reports a failed client installation. Preserve successful CLI
registrations and configure only the failed client. The Plugin fallback uses
native OAuth; one consent covers the `springbrand` MCP entry.

## Initial installation response

Before any Plugin command or OAuth handoff, determine whether this is a first
installation or an update. At the first result report or request for user
action, state the actual setup status and next step, then show this Welcome
message once. Do not repeat it during the same installation conversation.

### Welcome message

**Everything your agent needs for go-to-market.**

GTM workflow Plugins and research, social-data, and media APIs—all through
SpringBrand, in the Agent you already use.

Try a task with free credits—copy a prompt below.

- **Research your market**
  “Use SpringBrand to research my product's competitors, compare their
  positioning, and identify opportunities to stand out. Include sources.”
- **Find customer signals**
  “Use SpringBrand to find public discussions about the problem my product
  solves. Summarize recurring pain points and buying signals, with links.”
- **Find creators**
  “Use SpringBrand to find creators who reach my target audience, explain why
  they fit my product, and draft personalized outreach.”
- **Create campaign assets**
  “Use SpringBrand to develop three creative directions for my next campaign,
  then turn my chosen direction into copy and visuals for the target channel.”

## Host guides

- [Codex CLI and Desktop](./INSTALL.cli.codex.md)
- [Claude Code and Desktop Code](./INSTALL.claude.md)
- [Cursor](./INSTALL.cursor.md)
- [WorkBuddy](./INSTALL.workbuddy.md)

Follow the matching guide's Plugin installation and verification steps. If no listed Host guide applies, report that the Plugin fallback is unsupported for this Agent instead of guessing a configuration path. Do not
run another CLI install command from this document. Do not install the dev
Plugin or add a second MCP entry.

## Required Plugin identity

- Plugin: `springbrand`
- MCP entry: `springbrand`
- URL: `https://connector.springbrand.ai/mcp`
- Transport: native remote HTTP / Streamable HTTP
- Authentication: Host-native OAuth
- Skills: the five Canonical production Skills from the selected Host source

Use the Host's native OAuth flow after the Plugin is installed. Never collect,
store, print, proxy, or write OAuth tokens or authorization codes. Preserve
unrelated Plugins, Skills, Rules, Hooks, MCP servers, and configuration.

Close the report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.

## Verification

Do not report success until the selected Host confirms the production identity,
the MCP service health check, the exact URL and native transport, the five
Skills, and the absence of duplicate `springbrand` entries. If the Host asks
for a restart or new session, report that as the next step and stop.
