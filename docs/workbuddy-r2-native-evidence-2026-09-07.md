# WorkBuddy R2 Native Evidence — September 7, 2026

Status: **CLI distribution lifecycle passed; desktop runtime/OAuth pending.**
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
