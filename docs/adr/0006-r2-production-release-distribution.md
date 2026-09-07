# ADR 0006: R2 production release distribution

- Date: 2026-09-07
- Status: Accepted direction; WorkBuddy implementation under Native Evidence gate
- Supersedes: ADR 0001's rolling-main **user distribution channel** decision once
  each Host Adapter's R2 route has passed acceptance. Native lifecycle, OAuth,
  trust boundaries, production identity on main, and migration consent remain.

## Decision

Ordinary users install and update immutable production releases through
`plugin.springbrand.ai`, not GitHub. GitHub remains the development, test, and
CI source. Version tags, not branches or GitHub's prerelease flag, determine
production versus development identity. Tags with dev markers cannot publish
or promote a production package.

Release ZIPs are deterministic Distribution Mirrors of a tagged Host Adapter.
They contain all its Skills, references, MCP declaration, and Routing Notice.
They never contain credentials. Each Host Adapter must prove its own native
installation mechanism; ZIP support in WorkBuddy implies nothing about other
Hosts. No cross-host configuration writer is introduced.

For WorkBuddy, the installed 5.4.3 bundled CLI exposes native ZIP Marketplace
support. Prefer an R2 ZIP source over a bespoke extraction/registration tool.
The eventual mutable native source is `channels/production/workbuddy.zip`;
versioned ZIPs and per-host manifests remain under `releases/<tag>/workbuddy/`.
The ZIP is a single-object native update unit. Channel JSON is informational,
not an atomic transaction with the ZIP. Other Hosts will receive independently
verified adapters before their installation instructions change.

## Rollout boundary

Do not change public INSTALL documents or enable the production channel until
WorkBuddy desktop OAuth, Skill/Hook runtime behavior, update, uninstall, and
legacy source migration have Native Evidence. Initial delivery permits immutable
release publication and isolated CLI tests only. Production promotion requires
an explicit Actions dispatch on main and the repository variable
`WORKBUDDY_R2_PRODUCTION_ENABLED=true`. The variable stays unset during testing.

Existing GitHub installations are not silently rewritten. Ask before replacing
an existing SpringBrand Marketplace or removing a conflicting legacy entry.
Unrelated configuration and OAuth state must remain intact. No extra global MCP
is introduced. Dev builds never change main's production identity.
