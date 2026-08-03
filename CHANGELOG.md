# Changelog

All notable changes to Cantrip are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Consuming projects vendor a copy of this toolkit, so every entry should be readable as
"what will change in my project when I update."

## [Unreleased]

### Added

- Repository scaffold: layer directories, ADR log, changelog, and contributor guidance.
- **The layer contract** ([docs/contract.md](docs/contract.md), ADR 0001): four L2 slot files,
  the `**Slot:**` / `**If empty:**` reference pattern, graceful degradation as a hard
  requirement, and the rule that editing a vendored file is a divergence rather than a
  workflow.
- **Packaging shape** (ADR 0002): every installable unit is a skill directory, with non-skill
  assets shipping inside one. Reviewer agents stay at repo-root `agents/`.
- **`workflow` reference skill** — the workflow spine and work-types classification, extracted
  from the host projects' `CLAUDE.md` so the toolkit owns its own spine. Carries the spec and
  feature templates as assets.
- **`bdd-principles` reference skill** — BDD guidance, with a trigger-engineered description.
- **`scripts/check-contract.sh`** — seven automated contract checks (client-identifier scrub,
  absolute paths, hostnames, slot/fallback pairing, invocation posture, frontmatter
  completeness, loose files).
- **`/spec` spell** — first extracted spellbook entry: turns a short idea into a saved spec with
  acceptance criteria, draft BDD scenarios, a working branch, and a work-type classification.
- **`/plan` spell** — turns a spec into a phased, TDD-first plan of independently-executable
  steps, each with a paste-ready prompt, and a final step that records durable behavior per the
  work type.
- **`umbraco-17-planning` pack skill** — first L1 content: live-schema inspection via MCP,
  backoffice-extension skill routing, the Umbraco layer vocabulary, and typical step order.
- **ADR 0003** — how L0 reaches an L1 pack: packs contribute model-invoked reference skills with
  trigger-engineered descriptions, and L0 asks for a *kind* of guidance rather than naming any
  technology.
- Gate check 8 — no technology names in L0 core, enforcing ADR 0003.
- **`/feature` spell** — reconciled from both source versions into one command with an implicit
  from-code mode, so a capability that exists in code but was never documented can be backfilled.
  This is what makes adopting the toolkit on an existing project work.
- **`umbraco-17-feature-backfill` pack skill** — where Umbraco keeps the schema artifact, generated
  model, and view, plus the data-type-to-field-kind mapping.
- **`scripts/check-preserved.py`** — whitespace- and emphasis-normalized preservation checking, so
  hard-wrapped output stops producing false "content lost" flags.

### Changed

- Skills organized by invocation taxonomy — `skills/core/spellbook/` and
  `skills/core/reference/` — which lets the contract gate enforce invocation posture by path.
- Templates moved from a root directory into the `workflow` skill, so they install with the
  spine that describes them instead of needing a separate placement step.
- Contract gained the **one slot, one point of authority** rule: a slot is referenced where it
  is owned, and other files defer to that owner rather than repeating it. Toolkit-internal paths
  are not slots.
