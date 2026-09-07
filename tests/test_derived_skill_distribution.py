from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "skills/springbrand-platform/SKILL.md"
ACTION = ROOT / "skills/springbrand-action-api/SKILL.md"
MIRROR_ROOTS = (
    ROOT / "plugins/springbrand/skills",
    ROOT / "plugins/springbrand-workbuddy/skills",
)


def test_platform_uses_platform_rendered_mcp_skill_package() -> None:
    skill = PLATFORM.read_text()
    normalized = " ".join(skill.split())

    for phrase in (
        'target: "mcp"',
        "mcp-skill-package-v1",
        "render_version",
        "distribution.json",
        "Resource ID, Resource version, and render version",
        "bundle-level `instructions`",
        "Skill `entrypoint`",
        "never perform a second marker replacement",
        "return to the packaged business Skill",
    ):
        assert phrase in normalized, phrase

    assert "stop this workflow and hand over" not in skill
    assert "permanently switch the combined task" not in skill


def test_action_get_contract_uses_current_camel_case_fields() -> None:
    skill = ACTION.read_text()

    assert "**`inputSchema`**" in skill
    assert "**`outputSchema`**" in skill
    assert "**`input_schema`**" not in skill
    assert "**`output_schema`**" not in skill


def test_generated_host_mirrors_match_the_canonical_skills() -> None:
    for name in ("springbrand-platform", "springbrand-action-api"):
        canonical = (ROOT / f"skills/{name}/SKILL.md").read_bytes()
        for mirror_root in MIRROR_ROOTS:
            assert (mirror_root / f"{name}/SKILL.md").read_bytes() == canonical


if __name__ == "__main__":
    test_platform_uses_platform_rendered_mcp_skill_package()
    test_action_get_contract_uses_current_camel_case_fields()
    test_generated_host_mirrors_match_the_canonical_skills()
