# Remove Tool-specific behavior from Canonical Skills

**Status:** resolved

## Scope

- Keep the five Meta Tool names and generic execution rules.
- Require reading the selected Tool description before execution.
- Remove attachment-specific, image-specific, provider-specific and
  operation-specific workflow instructions from the Action API Skill.
- Update the canonical Skill references and generated mirrors.
- Add regression checks that the generic Skill does not contain those
  Tool-specific workflows.

## Checklist

- [x] Rewrite the canonical Action API Skill around the generic framework.
- [x] Remove Tool-specific instructions from Action API discovery reference.
- [x] Regenerate production mirrors.
- [x] Update relevant tests.
- [x] Run setup validation checks available in this checkout.

## 答案

The canonical Action API Skill now requires reading the selected Tool's
description and current schema while leaving Tool-specific usage and follow-up
behavior to the Gateway contract. Attachment preparation, image presentation,
provider alias maps and other operation-specific instructions were removed
from the Skill and its mirrors.

Verification under Python 3.12: `tests/test_action_discovery.py`,
`tests/test_routing_policy.py`, `tests/test_production_skill_sync.py`,
`tests/test_install_guidance.py`, `tests/test_release_identity.py` and
`tests/validate_plugin.py` passed. `git diff --check` passed.
