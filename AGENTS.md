## Agent skills

### Issue tracker

Issues are tracked in this repository's GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

Use the single-context domain documentation layout. See `docs/agents/domain.md`.

### Release identity: dev vs production

The MCP environment is determined by the version tag, never by the branch a
build happens to run on:

- Version tags containing a dev marker (`-dev.N`, e.g. `v1.2.0-beta.8-dev.1`)
  MUST carry the development identity: Plugin name `springbrand-dev`, display
  name "SpringBrand Dev", and the MCP entry `springbrand-dev` pointing at
  `https://devconnector.springbrand.ai/mcp`.
- Normal release tags (no dev marker, e.g. `v1.2.0-beta.8`) MUST carry the
  production identity: Plugin name `springbrand`, display name "SpringBrand",
  and the MCP entry `springbrand` pointing at
  `https://connector.springbrand.ai/mcp`.

`main` is the rolling production channel, so the manifests on `main`
(`.mcp.json`, `plugins/springbrand/mcp.json`, `plugins/springbrand-workbuddy/.mcp.json`,
`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.codebuddy-plugin/`,
`.agents/plugins/`, `hooks/user-prompt-submit`, and the WorkBuddy equivalents)
MUST always carry the production identity.

To build a dev variant, run `scripts/build_dev_variant.py` on a release branch
only — it rewrites the manifests to the development identity in place. NEVER
merge those rewritten files back into `main`; publish the branch as an
immutable dev tag instead. `tests/test_release_identity.py` guards this rule.
