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
- **`/implement-step` spell** — dispatches one plan step to a fresh context with just Context, Key
  Decisions, and that step, then relays a structured DONE/BLOCKED report.
- **`/code-review` spell** — three reviewers in parallel, merged into one de-duplicated report with
  an ordered action plan; applies nothing without approval.
- **`/commit-message` spell** — proposes a message explaining why, following the project's own
  commit convention inferred from history rather than an imposed one.
- **Three reviewer agents** — `accessibility-reviewer`, `code-reviewer`, `perf-reviewer`, as domain
  skeletons carrying their own checklists and deferring shared behavior to two new references.
- **`reviewer-discipline` reference skill** — the diff-only scope rule, the single severity scale,
  the evidence standard, and the report structure every reviewer shares.
- **`/explore` spell** — interview-driven discovery that widens the option space before a decision,
  writing its summary as the increment's `discovery.md`.
- **`/retrofit` spell** — reconciles an out-of-flow change against its actual diff, reviews it,
  surfaces edge cases, and proposes the tests and docs the flow would have produced, applying only
  what is confirmed.
- Gate check 9 — the same slot always gets the same fallback, so behavior cannot diverge silently
  when a slot is empty.
- Toolkit assets are referenced by skill and asset name rather than install path, which varies by
  agent tool and CLI version.
- The reviewer agents moved from repo-root `agents/` into the `reviewer-discipline` skill, so they
  install and are hash-tracked. Registering them as subagents is one documented command; until then
  review runs inline instead of in parallel.
- Dropped the planned `toolkit-lock.json` — the CLI's own `skills-lock.json` already records source,
  path, and content hash per skill.
- **`memory-discipline` reference skill** — the MEMORY.md index and topic-file layout, the entry
  format, and the three entry types, including the false-positive suppressions that keep a reviewer
  calibrated.

- **Install path** — `npx skills add robot-denny/cantrip/skills/core --all` for the core toolkit, or
  a `skills/<pack>` subpath for a stack pack. Packs are opt-in by construction.
- **ADR 0004** — install layout corrections from verifying the CLI, superseding two claims in
  ADR 0002.
- README now carries the install instructions and the spell catalog.
- **`/update-toolkit` spell** — wraps the installer's update behind a git guard, because the bare
  update silently overwrites local modifications and reports success. Verified empirically.
- **`.githooks/pre-commit`** — runs the contract gate before every commit. Enable with
  `git config core.hooksPath .githooks`.
- **`scripts/check-install.sh`** — consumer-facing install verification. Distinguishes wired,
  degraded, and broken, names the fix for each, and exits non-zero only when genuinely broken.
- **`_features/install-verification.md`** — the repo's first behavioral doc, produced by casting the
  toolkit's own chain on itself.
- **`tests/`** — the repo's first test harness: a dependency-free runner, ten generated fixtures
  covering all three install layouts, and `make-fixtures.sh` to regenerate them.
- The technology-name check accepts scoped inline exemptions
  (`<!-- contract-allow: <pattern> — <reason> -->`) for dual-use patterns like the toolkit's own
  installer.

### Changed

- Skills organized by invocation taxonomy — `skills/core/spellbook/` and
  `skills/core/reference/` — which lets the contract gate enforce invocation posture by path.
- Templates moved from a root directory into the `workflow` skill, so they install with the
  spine that describes them instead of needing a separate placement step.
- The quality reviewer is named `code-reviewer`, not after any technology, so a stack pack adds
  rules to it rather than shipping a second quality reviewer.
- All three reviewers share one severity scale (Blocker/Major/Minor/Nit) so merged findings sort
  into a single ranking, with higher-severity-wins on disagreement. The sources carried four
  different scales across files meant to merge into one report.
- Gate check 8 also covers `agents/`, which ship as core and are equally technology-agnostic.
- The one-slot rule now governs the *fact*, not the reference: several spells may read one slot, but
  they must give it identical fallbacks.
- Contract gained the **one slot, one point of authority** rule: a slot is referenced where it
  is owned, and other files defer to that owner rather than repeating it. Toolkit-internal paths
  are not slots.
