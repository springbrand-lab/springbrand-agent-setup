# `ask-springbrand-dev` Step 2 fixture

This directory is the reversible development-only setup path for the Jev
Domain-routing experiment. It is intentionally outside the production Skill
and mirror directories. The fixture is loaded directly by the validation
test; a release build must use the existing dev-variant release process on a
release branch.

The MCP dependency is the dev endpoint configured by the host. The experiment
tool is enabled only when the Gateway dev feature flag exposes
`recommend_springbrand_domain`. No API key is stored here.

Run the comparison locally with:

```sh
python3 .scratch/jev-ask-springbrand-dev-validation/evaluate_corpus.py
python3 -m unittest tests/test_jev_dev_skill.py
```
