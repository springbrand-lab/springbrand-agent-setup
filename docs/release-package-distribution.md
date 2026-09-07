# R2 release-package distribution — WorkBuddy first

## Current scope

This implementation adds immutable tagged WorkBuddy ZIP publication, a gated
production promotion command, and an isolated macOS native lifecycle probe.
It does **not** switch the public install documents, claim desktop OAuth/runtime
acceptance, or claim R2 installation for Codex/Claude/Cursor. It does not alter
existing version tags. See ADR 0006 for the channel decision.

The previous document publisher keeps ownership of its five root keys.
This publisher only writes `releases/<production-tag>/workbuddy/` and, after
explicit acceptance/promotion, `channels/production/workbuddy.zip` plus the
informational `workbuddy.json`. It never deletes or syncs the bucket.

## Build and validation

```sh
python3 tests/test_release_package.py
python3 scripts/build_release_package.py --tag v1.2.0-beta.10 --output /tmp/empty-release-dir
```

Source is read by `git archive refs/tags/<tag>`, never the working tree. Packages
have reproducible ZIP timestamps/permissions and include the complete nested
WorkBuddy Host Adapter and relative Marketplace entry. Build checks reject dev
identity, tag/version disagreement, non-local plugin sources, extra MCP/auth
configuration, missing Skills/references, drift from Canonical Skills/Hook,
and a Hook missing its executable bit. Per-file and package SHA-256 hashes are
recorded with the tag's resolved commit. SHA-256 detects corruption; it is not a
separate signature/trust root. Native ZIP downloads use HTTPS/native host trust.

## Publication

After merge, dispatch **Publish WorkBuddy release package** on main with an
existing prod `tag` and `promote=false`. Credentials reuse the dedicated
bucket-scoped Actions Secrets described in `install-docs-publishing.md`.

The publisher refuses to overwrite an immutable key with different bytes,
uses conditional object creation, and reads every object back through the
public domain. A failed/partial publication is not a release success; identical
reruns are safe. Never replace an existing tag to repair a release. Release
identity follows the tag even when GitHub labels that release a prerelease.

Initial bootstrap may publish an already-existing tag locally using the same
script and ignored bucket-scoped credential file, without promotion. Never
print credentials. Do not set fake Actions environment variables for promotion.

Production promotion is deliberately manual and gated in this first delivery.
Do not enable `WORKBUDDY_R2_PRODUCTION_ENABLED` or set `promote=true` until the
native acceptance checklist is complete. Dispatches are serialized. Select the
intended tag explicitly; there is no automatic “largest semver” selection and
no automatic release-triggered promotion yet. A rollback also needs an explicit
operator choice and tested host behavior; changing a channel does not prove the
host will automatically downgrade an installed plugin.

Promotion verifies immutable objects first, then uploads the complete ZIP with
`Cache-Control: no-store`, verifies it, and writes informational channel JSON.
If upload succeeds but verification fails, the public channel may already have
changed: inspect and repair deliberately, never report success. There is no
cross-object atomicity. The ZIP itself contains the authoritative version.
Do not add CDN rules that override channel no-store semantics.

## Native macOS test

```sh
python3 scripts/smoke_workbuddy_r2.py \
  --config /private/tmp/springbrand-r2-clean-test \
  --url https://plugin.springbrand.ai/releases/v1.2.0-beta.10/workbuddy/springbrand-workbuddy.zip \
  --manifest /tmp/empty-release-dir/manifest.json
```

The config directory must be new or owned by this probe. The script never uses
`~/.workbuddy-ai`. `sandbox-exec` denies direct Internet networking; a local
CONNECT proxy allows only `plugin.springbrand.ai:443` and the native WorkBuddy
bootstrap service `www.workbuddy.ai:443`. The test-only Node HTTPS transport
bridge in `tests/fixtures/r2_proxy.cjs` routes the native ZIP downloader through
that proxy because the downloader ignores HTTPS_PROXY. TLS remains end-to-end
with certificate verification enabled. This fixture is not part of user packages. Negative controls verify
GitHub/raw/API/codeload and direct public-IP connections fail. The native CLI
then adds/updates the ZIP Marketplace, installs/enables the Plugin, and checks
its registry entry and every installed asset hash, including Hook executable
permission. Add `--remove` to test disable/uninstall/marketplace removal.
`r2-smoke-evidence.json` records commands/results and allowed/denied proxy hosts.
No prompts, credentials, OAuth state, or model requests are part of this probe.

To test actual upgrade, use a dedicated **non-production** validation ZIP URL:
serve the older immutable package, run the probe, replace that validation
object with the newer package, and rerun with the newer expected manifest in
the same isolated config. After marketplace refresh, query the installed version
first: CLI 2.132.0 may already have upgraded it, and an unnecessary second
`plugin update` can fail with "cache in use". Do not mutate immutable releases or production to
simulate upgrades. A same-version refresh is not upgrade evidence.

## Remaining desktop acceptance / migration

- User's real WorkBuddy loads exactly one enabled SpringBrand Plugin.
- Four Skills load after restart/new task.
- Per user decision on 2026-09-07, Hook installation/runtime success is not a
  release acceptance gate. Preserve existing packaged Hooks and integrity checks;
  unverified runtime behavior must not be reported as passed.
- User completes native browser OAuth; actual domain-prefixed MCP call succeeds.
- Covered task invokes appropriate discovery; ordinary local task does not.
- Existing GitHub-origin installation migrates through the native lifecycle,
  with explicit consent and no duplicate entries, unrelated config changes, or
  unauthorized OAuth removal. A fresh R2 install is not migration evidence.
- Document Mac evidence only; Windows and other Hosts remain unverified.
- Only after acceptance, change INSTALL.workbuddy.md and the unified entry;
  remove GitHub/raw preflight from the ordinary user path, keep developer
  instructions separate, and automate subsequent accepted production releases.


## GitHub-source migration validation

The isolated native probe has passed with both enabled and disabled old
user-scope GitHub installations. See the dated Native Evidence document for
exact results and limitations. Reproduce on macOS with WorkBuddy installed:

```sh
python3 scripts/build_release_package.py --tag v1.2.0-beta.10 --output /tmp/springbrand-migration-release
python3 scripts/smoke_workbuddy_migration.py \
  --config /tmp/springbrand-migration-new \
  --manifest /tmp/springbrand-migration-release/manifest.json \
  --url https://plugin.springbrand.ai/releases/v1.2.0-beta.10/workbuddy/springbrand-workbuddy.zip
```

Use another fresh config directory and add `--disabled` for the disabled case.
The probe refuses existing directories and paths inside the real user config.
It needs GitHub only to create the old installation; the migration itself blocks
GitHub. It installs synthetic unrelated-state/credential fixtures for preservation
checks, never copies real OAuth data, and is **not a user migration installer**.

The verified native sequence is disable (when enabled), uninstall, remove old
marketplace, add R2 ZIP, install, then restore prior enabled state. Real migration
requires explicit consent, recoverable pre-migration state and destination
verification before removal. It is not atomic: on failure, stop and diagnose,
never silently rewrite OAuth or fall back to GitHub. Same-name custom sources,
non-user scopes and legacy aggregate-MCP releases need separate preflight.

Synthetic credential bytes survived both tests; live post-migration OAuth refresh
is still unverified. The production switch remains a separate authorized step.


## Public installation routing — September 7, 2026

By explicit user direction, INSTALL and README now route new WorkBuddy users to
the already-published immutable `v1.2.0-beta.10` R2 ZIP, while Codex, Claude Code,
Cursor and the other-Agent fallback retain GitHub installation. The user reports
no legacy users; old-source migration is not a new-user rollout blocker. Conflict
preflight remains mandatory; no existing installation is silently migrated.

This supersedes earlier statements that the public INSTALL switch is wholly
pending. The production-channel alias and automatic release publication are
still pending. Before selecting a new release in the guides, publish and verify
its immutable R2 package first, then update both INSTALL documents together.
Never point the guide at an unpublished version or pretend a pinned URL updates
itself. README uses the R2-hosted universal guide so WorkBuddy need not open
GitHub just to read the installation instructions.
