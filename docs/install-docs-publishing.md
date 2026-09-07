# Installation document distribution

## Scope and ownership

Canonical documents remain in this repository. R2 holds byte-identical
Distribution Mirrors, not separately maintained content. The only published
files are `INSTALL.md`, `INSTALL.claude.md`, `INSTALL.cursor.md`,
`INSTALL.workbuddy.md`, and generated `manifest.json` (commit SHA and SHA-256
hashes). Development instructions remain in `INSTALL.dev.md` and are not
published. Native Plugin installation and updates still require GitHub.

- Public origin: `https://plugin.springbrand.ai`
- Bucket: `springbrand-plugin-distribution` (Standard)
- Account: `a046b52313a86ecd2ce47e418d8b0f28`
- S3 endpoint: `https://a046b52313a86ecd2ce47e418d8b0f28.r2.cloudflarestorage.com`

The bucket may later hold versioned release packages. This publisher only
writes the five named keys; it never deletes objects or synchronizes the
whole bucket. Release-package installation is outside this implementation.

## One-time activation

1. Confirm the R2 custom domain has active ownership and TLS status.
2. Create dedicated R2 S3 credentials with Object Read & Write permission
   scoped only to this bucket. Do not reuse personal Wrangler OAuth or an
   account administrator credential.
3. Set repository Actions Secrets `R2_ACCESS_KEY_ID` and
   `R2_SECRET_ACCESS_KEY`. Never commit their values or paste them into a task.
4. Merge the tested workflow to `main`. Leave repository variable
   `INSTALL_DOCS_AUTO_PUBLISH` unset (automatic uploads are disabled).
5. Manually run **Publish installation documents** against `main`.
   This is a real production upload; absent credentials cause an explicit
   failure. The workflow requires AWS CLI (provided by its Ubuntu runner).
6. Verify the workflow's public-content checks pass and all four documents
   can be fetched without login. Only then change product installation links.
7. Set repository variable `INSTALL_DOCS_AUTO_PUBLISH` to `true` to enable
   relevant `main` pushes. PRs and tags never publish. Manual dispatch from
   another branch does not publish either.

## Local validation

Run from the repository root:

```sh
python3 tests/test_install_guidance.py
python3 tests/test_release_identity.py
python3 tests/test_publish_install_docs.py
python3 scripts/publish_install_docs.py
```

The last command builds in a temporary directory and prints provenance; it
performs no upload. Use `--output /absolute/empty/directory` to retain output.
The script's `--publish` path is reserved for Actions on `main` with a clean
tracked checkout and a source commit that is still the remote `main` HEAD.

## Updates, failures, and recovery

Production uploads are serialized and an old queued run is rejected if its
commit is no longer `main` HEAD. Documents use `Cache-Control: no-store`;
do not configure a CDN rule that overrides it. Child documents are uploaded
before the entry document, and provenance is uploaded last. Every public
file is read back with bounded retries and compared byte-for-byte.

Multiple R2 objects are not an atomic transaction: an interrupted run can
leave a partial update. A failed job must not be treated as a successful
release. Rerun the workflow against current `main` to repair it. To restore
older content, revert it through a new `main` commit and publish that commit;
do not rerun a historical workflow. Check Actions failure notifications.
Setting `INSTALL_DOCS_AUTO_PUBLISH` to `false` disables automatic uploads,
not explicitly requested manual runs.

The publishing job depends on its production package/document validation
job. The existing broader Plugin validation workflow remains separate.
Require applicable PR checks in branch protection before merging changes.
