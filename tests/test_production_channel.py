#!/usr/bin/env python3
"""Exercise the production-channel workflow guard across GitHub event types."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]


def main():
    workflow = (ROOT / ".github/workflows/validate-plugin.yml").read_text()
    step = workflow.split("      - name: Reject development packages on the production channel\n", 1)[1]
    step = step.split("      - name:", 1)[0]
    assert "        if:" not in step, "The channel guard must run for fork PRs too"
    script = textwrap.dedent(step.split("        run: |\n", 1)[1])
    code = script.split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    cases = (
        ("push", "refs/heads/main", "", True),
        ("pull_request", "refs/pull/93/merge", "main", True),
        ("workflow_dispatch", "refs/heads/main", "", True),
        ("pull_request", "refs/pull/94/merge", "development", False),
        ("push", "refs/tags/v1.2.0-beta.11-dev.3", "", False),
        ("workflow_dispatch", "refs/heads/development", "", False),
    )
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for version in ("1.2.0-beta.11", "1.2.0-beta.11-dev.3"):
            (root / "VERSION").write_text(version + "\n")
            for event, ref, base, production in cases:
                # Repository ownership must never exempt a main-targeted PR.
                for head_repo in ("springbrand-lab/springbrand-agent-setup", "contributor/fork"):
                    env = {**os.environ, "CHANNEL_EVENT": event, "CHANNEL_REF": ref,
                           "CHANNEL_BASE": base, "GITHUB_HEAD_REPOSITORY": head_repo}
                    result = subprocess.run([sys.executable, "-c", code], cwd=root,
                                            env=env, capture_output=True, text=True)
                    rejected = production and "-dev." in version
                    assert (result.returncode != 0) == rejected, (version, event, ref, base, result.stderr)
                    if rejected:
                        assert "must not be merged into main" in result.stderr
    print("Production channel guard: main, same-repo/fork PRs, dev tags and manual branches passed")


if __name__ == "__main__":
    main()
