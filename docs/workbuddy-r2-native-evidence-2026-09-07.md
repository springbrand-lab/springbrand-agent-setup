# WorkBuddy R2 Native Evidence — September 7, 2026

Status: **CLI distribution lifecycle passed; authenticated business call passed per user-supplied WorkBuddy evidence; Hook acceptance waived by user; isolated GitHub-source migration passed; live migrated OAuth remains unverified.**
This supplements, and does not replace, the historical runtime evidence.

## Environment and source

- macOS WorkBuddy 5.4.3; bundled native CLI 2.132.0.
- CLI discovered under `Contents/Resources/app.asar.unpacked/cli/bin/codebuddy`
  (older guidance only searched `Contents/Plugins/...`).
- Existing production tag: `v1.2.0-beta.10`.
- Tagged commit: `855398a1fe0e4f5ac7385890ac9f83f6983d1ec0`.
- Immutable ZIP: `https://plugin.springbrand.ai/releases/v1.2.0-beta.10/workbuddy/springbrand-workbuddy.zip`.
- ZIP SHA-256: `b8891b6c43869e2662cd69e1936de4683ba45de7ffa9ed248717ea49bb6e7536`.
- Size: 101071 bytes. Public read-back matched byte-for-byte.
- Package uses production identity and production MCP; no tag was changed.

## Passed evidence

1. Native ZIP installation in an isolated config produced one enabled
   `springbrand@springbrand`, version `1.2.0-beta.10`.
2. All installed Plugin files matched the tagged package's per-file SHA-256;
   Hook retained executable permission.
3. Under an OS outbound-network sandbox, GitHub/raw/API/codeload failed while
   the native R2 install succeeded. A test-only HTTPS Agent routes the native
   ZIP downloader through a local allowlisted CONNECT proxy because that
   downloader ignores HTTPS_PROXY. End-to-end TLS verification stays enabled.
   The allowlist includes R2 and WorkBuddy's own bootstrap host, not GitHub.
   This is controlled network-fault evidence, not a claim that the unmodified
   downloader honors a user's proxy or that every user network is reachable.
4. A final clean sequence used the non-production validation ZIP URL:
   - Publish beta.9 bytes; native install listed beta.9.
   - Publish beta.10 bytes to the **same validation URL**, not an immutable key.
   - Native marketplace update then plugin list showed beta.10, enabled.
   - File hashes and executable Hook verified against beta.10.
   - Native disable, uninstall, and marketplace remove succeeded.
   - Plugin list and marketplace list both returned `[]`.
5. Real user WorkBuddy config was preflighted: no existing SpringBrand Plugin,
   Marketplace, manual SpringBrand Skill, or global MCP conflict.
6. The real WorkBuddy was installed and enabled through native CLI using the
   immutable R2 ZIP URL, **without** the test-only HTTPS bridge or sandbox.
   Registry showed exactly one enabled SpringBrand beta.10. All Plugin file
   hashes and Hook executable bit passed. Existing unrelated plugin records,
   market records, enabled flags, other settings, global MCP, and MCP approval
   fingerprints were unchanged immediately after installation.

## Findings incorporated into the probe

- CLI success exit code is insufficient: some failed operations exit zero.
  The probe checks failure text, actual registry version, and installed bytes.
- Marketplace refresh can itself upgrade an enabled plugin. Immediately
  calling `plugin update` again can fail with `Cannot replace plugin cache in
  use`. Query the actual version first, and update explicitly only if needed.
- A local **directory** probe returned success text but an empty installed
  list in this build. It was not accepted as evidence; native ZIP was selected.
- Early network-test harness attempts failed because the sandbox blocked
  native loopback services or the downloader ignored proxy environment vars.
  These were harness failures, not proof of an R2 production outage. One
  isolated startup also returned empty stdout with a loopback EPERM; no retry
  is silently treated as success. The final full lifecycle ran successfully.

## Remaining acceptance — do not promote yet

- WorkBuddy desktop reload/new-task Skill and Hook loading.
- Native user OAuth and a real domain-prefixed MCP tool call.
- Covered task discovery/routing behavior and ordinary-task non-routing.
- GitHub-origin legacy migration, preserving unrelated config and authorization;
  a fresh real-user install does not establish this.
- Production-channel promotion, automatic release publication, and public
  installation-document switch remain disabled/pending.

Desktop control could not start (`Sky Computer Use service startup request
failed`). The installed CLI's `mcp --help` exposes add/remove/list/get/add-json,
not OAuth login. No authorization was simulated and no token/header/global MCP
was added. User must currently reload and complete native OAuth in WorkBuddy.

The real-user install is pinned to the immutable beta.10 URL for acceptance;
it will not automatically follow future production versions. After acceptance,
migrate its source deliberately to the validated production-channel URL.

## Local raw evidence (not committed)

- `/private/tmp/springbrand-r2-workbuddy-artifacts/v1.2.0-beta.9-final-evidence.json`
- `/private/tmp/springbrand-r2-workbuddy-artifacts/v1.2.0-beta.10-final-evidence.json`
- `/private/tmp/springbrand-workbuddy-real-install-20260907/commands.json`
- `/private/tmp/springbrand-workbuddy-real-install-20260907/before-hashes.json`
- `/private/tmp/springbrand-workbuddy-real-install-20260907/after-hashes.json`

Only fingerprints, not copied OAuth values, were used for config preservation
checks. Raw evidence stays local; this document contains no secrets.

## OAuth follow-up — September 7, 2026

User reports completing native OAuth after the initial acceptance report.
Read-only local log verification found:

- Session process 30539 reports `springbrand:connected`, present in the connected
  server cache at 17:30:28 and again at 17:38:27 (session log
  `2026-09-07-17-22-05__a331f083fe4e10de818eb85a23e6cade.log`, lines
  22289 and 22443). This corroborates a connected session after authorization.
- Existing CLI host process 30571 still reports `springbrand:unauthorized` at
  17:38:27 (host log
  `__workbuddy_cli_host__-0-63810d60__ca2ad55ab0295c36575225eb8578de5c.log`,
  line 2431). Do not treat all processes as refreshed or infer the cause.
- The session's original loader entries independently confirm 4 Skills,
  2 Hooks, and 1 MCP server (lines 498 and 980).

An authenticated read-only business-tool success remains unverified. The user's
previous anonymous discovery successes do not establish authenticated access.
Hook dispatch/execution also remains unverified. No credentials were read and
no user configuration was changed during this follow-up. Production promotion
remains gated on the remaining acceptance checks above.


## Authenticated business call — user-supplied acceptance evidence

After restarting WorkBuddy and using a new session, the user supplied a successful
read-only call report on September 7, 2026:

- Tool: `mcp__springbrand__platform_execute_capability`.
- Name: `platform:springbrand@0:springbrand.plugins.list`.
- Body: `{"view":"marketplace","page":1,"pageSize":30}`.
- Execution ID: `de9b1ddf-ac67-4263-b619-d3478105dc8c`.
- Status: `succeeded`; total 26; page/page_size 1/30; risk `none`.
- User reports no reinstall, reauthorization, config edits, or manual OAuth.

This supersedes the pending authenticated-call finding above, based on the
user-supplied runtime evidence; it is not an independently retrieved server trace.
The same report records an initial request with an extra `idempotency_key`
rejected as `invalid_arguments`, with the explicit message
`idempotency_key is supported only for Creation upload`. Do not attribute that
rejection to session expiration. The earlier failures' complete causes remain
unconfirmed; restart and corrected arguments are not isolated experiments.

Hook actual dispatch/execution, routing acceptance, legacy GitHub-source migration,
and production promotion remain pending. No production alias or public installation
instructions were changed by recording this result.


## User acceptance scope amendment — September 7, 2026

User explicitly directed that Hook installation/execution is non-blocking because
Skills are sufficient for the intended workflow. Hook runtime remains unverified,
not failed or passed, and is removed from the production acceptance gate. Earlier
pending-Hook gate statements in this chronological record are superseded by this
amendment. Existing Hook files and package integrity tests are retained; no user
plugin configuration was changed. Legacy migration and the other release gates
are not waived. No production promotion was performed by this amendment.

## GitHub-origin native migration — September 7, 2026

**Passed for enabled and disabled user-scope installations on this macOS host.**
Reproducible probe: `scripts/smoke_workbuddy_migration.py`; safety regression:
`tests/test_workbuddy_migration.py`.

Both independent runs:

1. Used the unmodified native CLI to add the real GitHub repository source and
   install `springbrand@springbrand`. Verified source type `github`, repository
   `springbrand-lab/springbrand-agent-setup`, installed beta.10 and Git commit
   `578b19615b972415e6b5997d9981404ff4a7273f`. The second run disabled it.
2. Added explicitly synthetic preservation fixtures for an unrelated plugin
   registry/cache/marketplace, settings, empty global MCP, approval file and
   credentials file. No real user credential or config was copied.
3. Blocked GitHub/raw/API/codeload and direct Internet bypass using the existing
   OS sandbox and allowlisted test proxy. Negative controls failed as required;
   the R2 destination was reachable. Native vendor bootstrap remained allowed.
4. Through native CLI only: disable if needed, uninstall SpringBrand, remove its
   GitHub marketplace, add immutable R2 ZIP, install, restore prior enabled state.
5. Verified exactly one SpringBrand plugin at beta.10, the marketplace type `zip`
   with the exact immutable R2 URL, all installed package hashes, and original
   enabled/disabled state. Unrelated fixture registry/settings/market entries,
   control plugin files, approval and credential file fingerprints were unchanged.

Evidence directories (local, not committed):

- `/private/tmp/springbrand-r2-migration-enabled-final/`
- `/private/tmp/springbrand-r2-migration-disabled-final/`

Each contains `migration-before.json`, `migration-after.json`, and
`migration-evidence.json` (`passed: true`, commands, exit codes, proxy events).
The first exploratory native GitHub install remains separately under
`/private/tmp/springbrand-r2-migration-20260907/`; it is not counted as a completed
migration run. No live user WorkBuddy config was modified.

### Scope and limitations

- This is same-version source migration, not an additional upgrade claim. The
  prior beta.9 -> beta.10 native upgrade evidence remains separate.
- Credential **file preservation** uses synthetic sentinels, not a real OAuth
  session. Post-migration OAuth usability/refresh in a real user installation is
  not established; the user's separately accepted R2 installation and real
  authenticated call do not establish that property for a migrated installation.
- Migration is a non-atomic native uninstall/reinstall sequence. Obtain explicit
  user consent and preserve recoverable pre-migration state before doing it on a
  real installation. Stop on failure; do not silently fall back to GitHub or
  modify credentials. Do not begin a new task until prior enabled state is restored.
- Only the documented user-scope GitHub source on this WorkBuddy/macOS version
  was tested. Other scopes, custom marketplace names, older aggregate-MCP releases,
  Windows and other Hosts are not covered by these two runs.
- Hook gate is waived by user. Remaining routing acceptance and real migrated
  OAuth acceptance are not marked passed. PR submission does not enable production.


## beta.11 release verification and guide selection (2026-09-07)

- Production tag: `v1.2.0-beta.11`, source commit
  `86fa8a013e8d094b7cdf18e773c8b43d22af67ac` (PR #90).
- R2 publish workflow run: `34132782157`, successful, `promote=false`.
- Immutable package:
  `https://plugin.springbrand.ai/releases/v1.2.0-beta.11/workbuddy/springbrand-workbuddy.zip`.
- Package size: 101071 bytes; SHA-256:
  `a0ce515ddba6f84480cd52f27d7b059b0d512c90c9070dd801de430eec9fe9a9`.
- Public manifest and ZIP matched the locally built tagged artifacts byte for
  byte. The beta.10 objects were not overwritten.
- The isolated native WorkBuddy/macOS lifecycle passed: fresh install, enable,
  installed version and asset-hash verification, disable, uninstall, and
  marketplace removal. Final plugin and marketplace lists were empty.
- The existing test-only sandbox/proxy harness blocked GitHub, raw, API,
  codeload and direct outbound bypass; only R2 and required WorkBuddy vendor
  bootstrap were allowlisted. This harness is not part of the shipped plugin.
- Local evidence: `/private/tmp/springbrand-beta11-native-release/r2-smoke-evidence.json`.

Following this successful check, the universal and WorkBuddy installation guides
select the pinned beta.11 R2 package for new WorkBuddy installs. Other Hosts
retain their existing GitHub routing. No moving production channel or automatic
Release-to-R2 trigger is enabled by this guide change.

The real user's WorkBuddy installation and OAuth credentials were not modified.
This run does not establish beta.11 desktop OAuth, authenticated business calls,
or beta.10-to-beta.11 upgrade behavior; earlier beta.10 user acceptance remains
separate. Existing pinned installations do not automatically switch versions.
Hook runtime remains non-blocking by user decision.
