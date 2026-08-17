#!/usr/bin/env python3
"""Check that package contract failures identify the broken artifact."""

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_plugin", ROOT / "tests/validate_plugin.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def copy_package(destination: Path) -> None:
    for name in ("VERSION", ".codex-plugin", ".agents", ".mcp.json", "assets", "hooks", "skills"):
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def expect_failure(change, message: str) -> None:
    with tempfile.TemporaryDirectory() as directory:
        package = Path(directory)
        copy_package(package)
        change(package)
        try:
            VALIDATOR.validate_package(package)
        except AssertionError as exc:
            assert message in str(exc), exc
        else:
            raise AssertionError(f"expected validation failure containing: {message}")


def edit_json(path: Path, edit) -> None:
    value = json.loads(path.read_text())
    edit(value)
    path.write_text(json.dumps(value))


def main() -> None:
    expect_failure(
        lambda root: (root / "VERSION").write_text("01.2.3\n"),
        "invalid repository version",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".mcp.json",
            lambda value: value["mcpServers"]["springbrand"].update(url="https://example.com/mcp"),
        ),
        "production MCP endpoint",
    )
    expect_failure(
        lambda root: (root / ".env").write_text("SPRINGBRAND_TOKEN=secret\n"),
        "forbidden credential file",
    )
    expect_failure(
        lambda root: edit_json(
            root / ".codex-plugin/plugin.json",
            lambda value: value.update(skills="./missing-skills/"),
        ),
        "Codex skills component must reference ./skills/",
    )
    expect_failure(
        lambda root: (root / "hooks/user-prompt-submit").chmod(0o644),
        "Codex Hook is not executable",
    )


if __name__ == "__main__":
    main()
