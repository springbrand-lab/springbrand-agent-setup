# Ship the SpringBrand Skill Set as four Canonical Skills with a non-executing router

The Gateway now exposes three isolated Domain Executors (`/mcp/platform`, `/mcp/action-api`, `/mcp/connectors`), while the current single Canonical Skill `springbrand-plugin-discovery` mixes Plugin discovery and API Service Actions in one legacy mixed `springbrand.catalog.match` flow. We will ship four Canonical Skills — `ask-springbrand` (the Ask SpringBrand Capability Guide) plus one Domain Skill per Capability Domain (`springbrand-platform`, `springbrand-action-api`, `springbrand-connector`) — each Domain Skill aligned one-to-one with its MCP Domain Entry.

## Decisions

- **Four Skills, one router.** Ask SpringBrand identifies the user's Capability Domain, reports workflow position, recommends exactly one Domain Skill, and stops. It never calls MCP, executes, acquires, authorizes, uploads, publishes, or activates more than one Domain Skill.
- **Invocation.** All four Skills are user-invocable and model-invocable. Domain Skills never call Ask SpringBrand back (sole exception: the user explicitly asks what else SpringBrand can do). Cross-domain work is an explicit Domain Transition handed directly between Domain Skills, preserving relevant task state and ending the prior domain workflow; never a merged search or auto-forward.
- **Audience.** The Plugin targets ordinary people, not only developers. All user-facing text is plain-language, step-by-step process guidance; technical vocabulary stays inside Agent-facing operational instructions.
- **Position sources.** Ask SpringBrand determines "current position" from conversation context and state records embedded in the user's artifact documents. Reading local files is file access, not execution. The state-tracking design, artifact standard format, and a possible artifact-creation helper Skill are deferred to a dedicated workflow discussion.
- **Retirement.** `springbrand-plugin-discovery` is retired as a name; the Plugin lifecycle workflow it carried moves into the Platform Skill.
- **Supersede scope.** This supersedes ADR-0001's single-Canonical-Skill and single-production-endpoint scope only. ADR-0001's source-of-truth, OAuth, lifecycle, and evidence rules remain binding, and its Distribution Mirror mechanism extends to all four Skills: Cursor and WorkBuddy packages carry generated, byte-equivalent, drift-checked mirrors of every Canonical Skill.
- **Validator contract.** The Canonical Skill Set is validated against an explicit named list (currently four), not a hardcoded count, so the set can grow without re-litigating the package contract.

## Consequences

- Package validation moves from "exactly one `skills/*/SKILL.md`" to the named four-Skill set with three-entry MCP assertions.
- The Routing Notice (Hook/Rule) shrinks to a ≤ ~700-character static domain map that points to Ask SpringBrand; all workflow detail lives in Skill bodies.
- Routing evaluation must score router accuracy, domain selection, tool isolation, workflow completion, and duplicate discovery (amends the corpus behind #25).
