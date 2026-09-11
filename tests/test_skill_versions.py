#!/usr/bin/env python3
"""Check VERSION stamping in both channels without modifying the checkout."""

from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
from sync_skill_versions import MIRRORS, stamp_version, sync


def main():
    original = '---\nname: example\ndescription: >\n  Keep this description.\nmetadata:\n  author: "SpringBrand"\n  version: "0.1.0"\nlicense: MIT\n---\n\n# Body\nDo not edit me.\n'
    updated = stamp_version(original, "1.2.3-dev.4")
    assert updated == original.replace('version: "0.1.0"', 'version: "1.2.3-dev.4"')
    assert stamp_version(updated, "1.2.3-dev.4") == updated
    missing = original.replace('  version: "0.1.0"\n', '')
    assert 'metadata:\n  version: "1.2.3"\n  author:' in stamp_version(missing, "1.2.3")
    missing_metadata = '---\nname: example\ndescription: example\n---\n\n# Body\n'
    assert 'metadata:\n  version: "1.2.3"\n---' in stamp_version(missing_metadata, "1.2.3")
    for invalid in (
        'no frontmatter',
        original.replace('metadata:', 'metadata: {}'),
        original.replace('  version: "0.1.0"', '  version: "0.1.0"\n  version: "0.2.0"'),
    ):
        try:
            stamp_version(invalid, "1.2.3")
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid frontmatter was silently rewritten")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for rel in ("skills", *MIRRORS):
            shutil.copytree(ROOT / rel, root / rel)
        # Keep the starting fixture independent of the checkout's release.
        for path in root.rglob("SKILL.md"):
            path.write_text(stamp_version(path.read_text(), "0.0.0"))
        for version in ("1.2.0-beta.12", "1.2.0-beta.12-dev.1", "1.2.0-beta.13"):
            (root / "VERSION").write_text(version + "\n")
            before = {p: p.read_bytes() for p in root.rglob("SKILL.md")}
            assert len(sync(root, check=True)) == len(before)
            assert before == {p: p.read_bytes() for p in root.rglob("SKILL.md")}, "check mode must not write"
            assert len(sync(root)) == len(before)
            assert sync(root, check=True) == []
            assert sync(root) == [], "stamp must be idempotent"
            for path in (root / "skills").glob("*/SKILL.md"):
                text = path.read_text()
                assert f'  version: "{version}"' in text.split("\n---\n", 1)[0]
                for mirror in MIRRORS:
                    assert (root / mirror / path.parent.name / "SKILL.md").read_text() == text
        mirror = root / MIRRORS[0] / "ask-springbrand/SKILL.md"
        mirror.write_text(mirror.read_text() + "\nMirror drift.\n")
        assert sync(root, check=True) == [str(mirror.relative_to(root))]
        sync(root)
        assert sync(root, check=True) == []
    print("Skill versions: production/dev switching, mirrors, preservation and check mode passed")


if __name__ == "__main__":
    main()
