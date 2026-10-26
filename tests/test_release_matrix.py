#!/usr/bin/env python3
"""Check that the release matrix guards version pins and the generated page."""

from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
from release_matrix import (  # noqa: E402
    MatrixError,
    check,
    dev_doc_pins,
    load_matrix,
    render,
    validate_matrix,
    workbuddy_pins,
)

FIXTURE = (
    "VERSION",
    "release-matrix.json",
    "INSTALL.md",
    "INSTALL.dev.md",
    "INSTALL.cli.dev.claude.md",
    "INSTALL.workbuddy.md",
    "docs/release-channels.md",
)


def fixture() -> Path:
    root = Path(tempfile.mkdtemp(prefix="release-matrix-"))
    for rel in FIXTURE:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, root / rel)
    return root


def expect_error(root: Path, needle: str) -> None:
    errors = check(root)
    assert any(needle in error for error in errors), (needle, errors)


def main() -> None:
    matrix = load_matrix()
    validate_matrix(matrix)
    page = render(matrix)
    assert "Stable" in page and "Development (pinned)" in page and "WorkBuddy" in page
    assert check(ROOT) == [], check(ROOT)

    assert dev_doc_pins(ROOT) == {"v1.2.1-dev.2"}
    version, source = workbuddy_pins(ROOT)
    assert version == "1.2.3"
    assert source.endswith("/releases/v1.2.3/workbuddy/springbrand-workbuddy.zip")

    root = fixture()
    try:
        (root / "VERSION").write_text("9.9.9\n")
        expect_error(root, "VERSION")
    finally:
        shutil.rmtree(root)

    root = fixture()
    try:
        doc = root / "INSTALL.dev.md"
        doc.write_text(doc.read_text().replace("v1.2.1-dev.2", "v9.9.9-dev.1"))
        expect_error(root, "development docs pin")
    finally:
        shutil.rmtree(root)

    root = fixture()
    try:
        doc = root / "INSTALL.workbuddy.md"
        doc.write_text(doc.read_text().replace('WORKBUDDY_VERSION="1.2.3"', 'WORKBUDDY_VERSION="9.9.9"'))
        expect_error(root, "WORKBUDDY_VERSION")
    finally:
        shutil.rmtree(root)

    root = fixture()
    try:
        (root / "docs/release-channels.md").write_text("stale\n")
        expect_error(root, "is stale")
    finally:
        shutil.rmtree(root)

    broken = dict(matrix)
    broken["channels"] = {**matrix["channels"], "stable": {**matrix["channels"]["stable"], "pluginVersion": "0.0.1"}}
    try:
        validate_matrix(broken)
    except MatrixError as error:
        assert "pluginTag" in str(error)
    else:
        raise AssertionError("Mismatched tag and version were accepted")

    print("Release matrix: VERSION, dev pin, WorkBuddy pin, page and schema checks passed")


if __name__ == "__main__":
    main()
