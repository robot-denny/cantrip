# Changelog

All notable changes to Cantrip are documented here. This project follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Consuming projects vendor a copy of this toolkit, so every entry should be readable as
"what will change in my project when I update."

## [Unreleased]

### Public readiness

- **MIT license** — the repository had none, which meant public-with-all-rights-reserved: readable but
  not legally installable, contradicting its own install instructions.
- **Five backfilled ADRs** (0001, 0008–0011) covering decisions settled before this repository existed —
  the three-layer split, vendored-copy distribution, the skills-CLI role split, skills-rather-than-commands
  with posture in frontmatter, and the lifecycle-based file layout. The reasoning now lives with the code
  instead of in a document consumers never see.
- **ADR 0007** — repository ownership stays as-is, with the costs of a later move recorded.
- The spell census is stated explicitly: **eight workflow spells**, held deliberately, plus `/setup` and
  `/update-toolkit` counted separately as configuration and maintenance rather than workflow stages.

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
- **`/check-uda` pack spell** — Umbraco Deploy schema conflict and drift analysis: git-side conflicts,
  Live-side drift via the Deploy Management API, block palette drift, and a risk-rated report. Ships
  its Cloud remediation runbook as a `references/` asset.
- **`/umbraco-edit` pack spell** — edit document properties or invoke a configured AI agent via the
  Management API, with alias and agent lookup rather than hardcoded values.
- **`/block` pack spell** — test-first Umbraco block creation. Discovers the project's view location
  and model binding by exemplar rather than asserting one architecture.
- **`umbraco-17-starter-facts` pack skill** — 41 verified Umbraco 17 platform facts across four topic
  files, each carrying `Type`, `Applies`, `Verified`, and a how-to-apply line. Selected for *silent
  failure*: every one describes something that neither throws nor logs.
- **`umbraco-17-review-rules` pack skill** — what to check in an Umbraco diff, deferring the underlying
  facts to `umbraco-17-starter-facts` rather than duplicating them.
- **`architecture-audit` pack skill** — seven-pillar architectural assessment with lifecycle-aware
  scoring, moved essentially unchanged since it was authored portable. Its report destination now
  follows the `workflow` skill's layout and the durable-or-temporal disposition rule.
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
- **`design-system-authoring` reference skill** — how to write a project's own design-system skill: find
  the mechanism that fails silently and lead with it, write pointer-first so it cannot go stale, derive a
  checkable conformance list from real review findings, and engineer the description to catch casual
  requests. Ships the method and a template; the design system itself stays L2.
- **`memory-discipline` reference skill** — the MEMORY.md index and topic-file layout, the entry
  format, and the three entry types, including the false-positive suppressions that keep a reviewer
  calibrated.

- **Install path** — `npx skills add robot-denny/cantrip/skills/core --all` for the core toolkit, or
  a `skills/<pack>` subpath for a stack pack. Packs are opt-in by construction.
- **ADR 0004** — install layout corrections from verifying the CLI, superseding two claims in
  ADR 0002.
- README now carries the install instructions and the spell catalog.
- **`/setup` spell** — configures the toolkit for a project in three tiers: detect what the repository
  answers, **mine what its guidance files already say**, then ask only for the residue. Places the
  workspace scaffold without overwriting an existing convention, preserves the project's own agents and
  skills, discovers a pack's slots from the pack rather than naming them, and reports what it left empty
  and why.
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

- README documents that installing **shadows** same-named commands, and recommends installing on a
  branch to contain it.
- `memory-discipline` distinguishes the two memory systems a project usually has, notes that backups
  must cover both, and warns that renaming an agent orphans its memory silently.

- The three reviewer agents now ask for stack-pack review guidance, applying the ADR 0003 pattern that
  had been carried to spells but not to agents.
- `/plan` Step 1 now resolves a **bare slug** against the workspace layout — previously it fell through
  to the description branch and re-derived a slug, producing a plan divorced from its spec.
- `/spec` asks before creating a workspace directory beside an established one, and before nesting a
  branch inside another working branch.
- Gate check 1 broadened well beyond client names to assembly names, component names, block aliases,
  project config values, branch slugs, and test-artifact filenames — each of which identifies a source
  project as surely as its name. Both scrub checks now share one auditable exemption mechanism.

- **ADR 0005** — work-type classification must not depend on documentation coverage. Adds a naming
  tell, area-level naming for undocumented areas, and a bias toward amending over creating.
- Specs now carry a **`Feature doc:`** field naming the capability doc by area, threaded through
  `/plan` and `/feature`, since that name routinely differs from the increment slug.
- `check-install.sh` detects redundant install copies from `--all` and prints the safe cleanup command.

- **ADR 0006** — no instruction may assume its precondition exists, with a five-rung response ladder
  (infer, borrow from a named reference, seed thin and mark it to grow, proceed and say so, ask) and a
  hard prohibition on fabricating a convention.
- Gate check 10 — an exemplar-dependent instruction must handle having no exemplar, the forcing function
  the principle needs.
- `/feature`, `/block`, `umbraco-17-planning`, and `design-system-authoring` now handle the greenfield
  case explicitly rather than assuming an exemplar, a doc, or an established mechanism exists.

- `/code-review` takes a **scope** — `uncommitted` (default) or `branch`, the latter covering committed,
  uncommitted, and untracked work against the upstream base, for increments built commit-per-step.
- `/code-review` **discovers** registered reviewers and maps them to roles rather than assuming canonical
  names, preferring a project's tailored reviewer, and reports which roles ran inline.
- `/implement-step` requires **evidence rather than attestation** for any validation it cannot
  mechanically verify, and declines to dispatch a step that is a spell-cast.
- `/plan` authors manual checkpoints as artifacts to produce, and leaves the behavior-recording step
  unnumbered so it is cast rather than dispatched.

- `/feature`'s from-code path is now **a technique as well as a mode** — update mode compares the doc
  against the code, not only against the artifacts, and backfills whatever the code does that the doc
  does not describe. This is the brownfield adoption path.
- `/feature` gained a third coverage state, **`Not covered (code-derived)`**, so a backfilled doc
  distinguishes verified behavior from inferred behavior instead of presenting both with equal confidence.
- `/feature`'s `Open Issues` hook now names dead styling, comments contradicting code, unreachable
  branches, and unreachable defaults — defects that surface because reading schema, model, and view
  together compares what each layer claims against what the others do.

- `/setup` **verifies** a detected build or test command by running it and reading its output, not its
  exit code — a test invocation that discovers zero tests exits 0 and is otherwise indistinguishable from
  a passing suite. Unverifiable commands are recorded as unverified.
- `/implement-step`'s "do not commit" is now explicitly the default rather than absolute: an explicit step
  instruction wins, and the worker reports that it committed.
- `/implement-step` and `reviewer-discipline` both handle **removal**, which is not symmetric with
  addition — a deleted symbol, rule, or file breaks tests asserting its presence, and those tests live
  nowhere near the code they guard.

- **`tdd-principles` reference skill** — the missing home for test *design*. TDD sequencing was already
  enforced in three spells, but nothing said what a test should assert, so a test could be written first,
  go red, go green, and still be fragile by construction. Covers observable behavior over implementation
  artifacts, the presence-assertion anti-pattern, expected values from an independent source, one behavior
  per cycle, what stands in for RED→GREEN when a project has no harness, and evidence over attestation.
  Brings a core install to **16 skills**. Adapted from an externally published skill — see
  [ADR 0013](adr/0013-attribution-for-adapted-external-work.md).
- **Pack companions are declarable** ([ADR 0012](adr/0012-pack-companions-are-recommended-not-required.md)).
  A pack may route work to external skill sets it does not own, and now says so: a `**Companion:**` line
  in the same self-describing style as `**Slot:**`, which `/setup` reads and reports on without core ever
  naming the technology. **Recommended, never required** — the pack plans without them. `/setup` also
  reports *where* a companion is enabled from, because an entry in your own user settings works for you
  and silently does not for a teammate cloning the repo.
- **`umbraco-cms-backoffice-testing-skills` is named** in the pack's routing and the README. It was
  enabled in practice and cited in no file, which mattered because `/plan` is TDD-first and that is the
  skill set covering extension test setup.
- **Acknowledgements in the README**, plus [ADR 0013](adr/0013-attribution-for-adapted-external-work.md):
  credit for the two units adapted from published skills, and a three-tier rule for when a license notice
  must ship with a skill rather than merely be recorded. The contract now separates our own authorship —
  which never belongs in a shipped skill — from a third party's notice, which may be required to travel
  with the copy.
- **Gate checks 12 and 13.** 12 fails when a declared companion is absent from the README, stripping
  fenced code blocks first, because a name shown in a config example is demonstrated rather than
  documented. 13 compares `check-install.sh`'s hardcoded roster against `skills/core`.

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

- **`/plan`, `/implement-step`, `/retrofit`, and `reviewer-discipline` now point at `tdd-principles`**
  for what a test asserts, each keeping its own framing — `/plan` still owns ordering, the review skill
  still owns the review-time reading.
- **`/plan` gained a breadth constraint on test steps.** Splitting a test from its implementation across
  two steps stays allowed, because a step has to fit a fresh context; batching several behaviors into one
  test-writing step does not, because that tests imagined rather than observed behavior.
- **`bdd-principles` said TDD "tests implementation"** — which, read literally, licenses the exact
  anti-pattern the new reference forbids, and would have had the two references contradicting each other.
  Now "tests units of behavior at the code level", with the ambiguity named explicitly.
- **The pack's absence clause names the remedy**, not just the absence. A note saying which skill set
  would improve the plan is actionable; one recording that something was unavailable is a shrug.

### Fixed

- **The documented core skill count was two short.** The README advertised 13 skills in both install
  shapes; a core install has installed 15 since `design-system-authoring` and `/setup` were extracted.
  Nothing about the install changes — the number describing it was stale.
- **`/setup` and `design-system-authoring` were not self-hosted**, so the two newest core skills could
  not be cast in the repository that authors them — including the spell whose whole job is configuring
  a fresh install. **Gate check 11** now fails on a core skill with no `.claude/skills/` symlink, and on
  any dangling one, because adding a skill takes three unlinked steps and steps 2 and 3 were both missed
  twice running. Scoped to core: a pack must not be linked, since this repo is not an Umbraco project.
- **The consumer-facing install checker verified a different set of skills than the toolkit ships.**
  `check-install.sh`'s roster was a hardcoded 13 that omitted `/setup` and `design-system-authoring`, so a
  project could install core, receive no `/setup` at all, and be told *"13 of 13 — no problems found."*
  Shipped that way since those skills were extracted. The roster is now 16, and **check 13** compares it
  against `skills/core`. This is check 11's missing sibling: 11 guards the self-hosting symlinks, 13 guards
  the install roster, and both lists are maintained by hand — check 11's own note names the two skills that
  were still absent here, so the gate that catches this shape had the shape.
- **Contract check 4 over-matched.** It searched for `**Slot:**` unanchored, so prose *about* the mechanism
  was read as a declaration and demanded a fallback for a slot it never referenced. Now anchored to line
  start with indentation allowed, verified still to catch an indented declaration missing its fallback.
- **`/explore` wrote a document `/spec` had never heard of.** The discovery doc carries a section
  addressed to `/spec` by name, and `/explore` ends by pointing there — but `/spec` built from whatever
  you retyped and re-derived its own slug, so the discovery was either sitting unread beside the new spec
  or orphaned in a second increment directory. It also could not run at all immediately after `/explore`:
  the discovery doc lands untracked, and `/spec` aborts on any untracked file, so the suggested next step
  failed on a clean-tree guard before reaching the part that ignored the file. `/spec` now reads an
  existing increment's `discovery.md` when given its slug and carries the framing, options, and open
  questions forward; `/explore` says to commit the doc first and why. Fifth instance of one mechanism
  present in a spell and absent from its sibling.
