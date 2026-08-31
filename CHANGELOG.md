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
- The spell census is stated explicitly: **eight workflow spells** against a working ceiling of ten, plus
  `/setup` and `/update-toolkit` counted separately as configuration and maintenance rather than
  workflow stages.

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

- **`dotnet` stack pack** — two opt-in reference units and no spells: `dotnet-conventions` (what should
  be true of the `.cs` or `.csproj` file you are about to write — naming by code element, async and
  `CancellationToken` discipline, structured logging with `ILogger`, `System.Text.Json` and camelCase
  DTOs, nullable reference types, and the modern syntax that is now the default) and
  `dotnet-review-rules` (what to check in a C# diff, at what severity, on the shared
  Blocker/Major/Minor/Nit scale). It is a **peer of `umbraco-17`, not part of it** — C# and .NET apply
  to every .NET project, CMS or not, so folding it into the CMS pack would have hidden it from the
  majority case and put language-lifetime content behind a CMS-version release cadence. An Umbraco
  project installs both. See [ADR 0014](adr/0014-dotnet-pack-and-the-detection-line.md).
  **Nothing about this arrives by update** — a pack is a separate install, so an existing project sees
  none of it until someone runs the command the README now carries.
- **The pack asserts platform defaults and refuses to answer what the project owns.**
  `dotnet-conventions` names the genuinely contested choices — `var` versus an explicit type, `sealed`
  by default, member ordering and `using` placement, the validation library, an `s_` prefix on static
  fields, when repetition earns a helper — and answers **none** of them, so installing the pack cannot
  start an argument with a codebase that already decided. Each resolves in a stated order:
  `.editorconfig` where it speaks, then a decision the project recorded in the slot
  `.agents/config/conventions.md` → `## .NET style decisions`, then the pack's default, then the
  dominant style of the surrounding file. Correctness never participates in that order — an
  interpolated log message still loses its fields whatever a configuration file says.
- **`**Detect:**`, an optional third line on a slot declaration**
  ([ADR 0014](adr/0014-dotnet-pack-and-the-detection-line.md)). A pack can now tell `/setup` how a
  project's own answer may be **read out of the repository** — which files to look at, and what in them
  counts as an answer — so a question the repo already answers is proposed rather than asked. The
  contract's existing `**If empty:**` governs *use* time, when a spell needs the fact and finds the slot
  blank; nothing governed *configuration* time. Core never writes a recipe, because check 8 forbids an
  L0 file from naming a technology: **the pack owns the recipe, core owns the instruction to honour
  one.** Optional by design, so nothing pairs with it and no gate enforces it —
  [docs/contract.md](docs/contract.md) states the five rules it must follow instead, including that it
  goes *after* the fallback so check 4's three-line pairing window stays intact.

- **`umbraco-cloud` stack pack** — a third pack, holding Umbraco Deploy knowledge that had been living
  inside the CMS pack: `/check-uda`, moved, plus a new `umbraco-deploy-facts` reference merging the Deploy
  schema facts and the Cloud remediation runbook into one unit. Two files where there were three, and the
  facts stay model-discoverable rather than being reachable only by casting the spell. **Versionless on
  purpose** — Deploy behaves the same across CMS majors, so releases are annotated per feature, which is
  [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md) §3's *majors add* branch. Its description
  is written about **Deploy the product, not Cloud the host**: Deploy is licensed standalone for
  on-premise, so a Cloud-scoped trigger would refuse to fire for a licensee who has the artifacts, the
  drift, and no Cloud subscription. **Nothing about this arrives by update** — a pack is a separate
  install: `npx skills add robot-denny/cantrip/skills/umbraco-cloud --all`.
- **`umbraco-17-audit-patterns` pack skill** — the Umbraco half of the architecture audit, staying in the
  CMS pack as assessment criteria: composition and service registration, schema-as-code discipline,
  content and block patterns, and how ready a site is to serve a decoupled frontend. It is judgement
  criteria rather than a defect list and says so, so it does not compete with `umbraco-17-review-rules`
  over a diff.
- **Gate check 14** — the audit's four stack-agnostic references are held to L0's no-technology rule
  while still sitting in a pack, so promoting them to core later is a `git mv` and a roster edit rather
  than a rewrite. The list is by *basename*, so the check follows the files through the very move it
  protects, and a named file that has gone missing fails rather than passing quietly — the failure shape
  checks 11 and 13 were both written to stop.
- **Three install-check fixtures**, taking the suite to 17 cases: `cloud-only` (a pack verifies with no
  sibling pack installed), `cloud-unit-missing` (the reinstall hint names the pack that provides the
  unit), and `shared-slot-two-packs` (one slot, two readers, surveyed once).
- **ADR 0015 amended** with four rules the pack split discovered — the **variant axis** (a pack can be
  wrong for a project by host or product, not only by version), the **replacement operation** (a pack is
  swapped for its successor, with version-carrying reference names, bare spell names, and one platform
  major installed at a time), where **portable criteria end and stack-specific detection recipes begin**,
  and the obligation to register **every** reader of a shared slot. Each is stated as a test an author can
  apply. Three of the four existed only in a shell loop or in review notes before.

- **Editor-facing guides for a CMS project — `/guide` and `umbraco-17-guide-scaffolding`**
  (2026-08-29). A component's schema already says what its properties are called, which are
  required, and what a dropdown offers; until now nothing turned that into a page an editor can
  read. `/guide` writes one guide page per component and audits which components have none.
  **Nothing about this arrives by update if you have not installed the `umbraco-17` pack** — and if
  you have, it arrives with two new slots to fill.
  - **The deterministic half is a script, not prose for a model to follow.**
    `skills/umbraco-17/spellbook/guide/scripts/guide.py` (Python 3, standard library only) owns
    extraction, the dossier, the inventory determiner, the audit's arithmetic, and the change plan.
    The spell owns what needs judgement — the prose, the diff-and-approve conversation, rendering
    read from the project's own exemplars, and **every CMS write**. Property tables are a
    deterministic transform and never depend on a model, which is what lets the whole thing degrade
    to rendered files when no AI service is available.
  - **Schema is read from whatever the project has**, over four rungs: Deploy artifacts, uSync
    configuration, a live instance through MCP, then a degraded read from generated models that
    states its own gaps rather than implying them by absence. The same component read through two
    adapters produces the same source signature, which is the assertion that makes the seam real.
    A read that finds nothing **fails loudly** rather than reporting an empty set.
  - **Provenance decides ownership, not a field's declaration.** A page carrying no stored reference
    has no machine-owned fields, so a run against a hand-written guide proposes and writes nothing.
    No prose on a guide page is ever regenerated: the purpose sentence, the when-to-use block, and
    every property row's note are written once and thereafter a person's. A matching signature is a
    no-op — no model call, no write.
  - **The audit warns and never blocks.** It exits zero whatever it found; `--strict` is the only
    thing that changes that. It reports the inventory and the rule that produced it *before* acting
    on it, because a determiner reading the element-type flag rather than the block palettes
    over-counts by 1.5x to 2.4x on the two projects measured — which turns the primary output from a
    backlog into noise.
  - **Two new slots** — `.agents/config/stack.md` → `## Schema serialization` (which adapter runs,
    with a `**Detect:**` recipe) and `.agents/config/conventions.md` → `## Editor guides` (the guides
    node's key and the document type aliases the project used). Both are declared in
    `umbraco-17-guide-scaffolding` and nowhere else; the spell defers to it. Every alias is a slot
    with a default, so a fresh install works before `/setup` runs.
  - **You create the document types.** The reference describes the guide page, the property row
    element type, the kind containers, and the index; nothing in the toolkit creates them for you,
    and the index's per-guide read is deliberately scoped to name, URL, and one line — resolving each
    listed guide's whole content model to render a teaser is eight hundred row objects per render of
    a public page.
  - **A `guide-check` test suite of 80 cases**, and `tests/run.sh` generalized to suites so a second
    subject was possible at all. Taking the harness to 97 cases across two suites.
- **A spell-card cheatsheet** ([docs/spell-cards.md](docs/spell-cards.md)) — one card's worth of
  content for every unit in the toolkit: 30 cards, 14 spells and 16 references, each with its
  invocation or trigger, its prerequisites, what it leaves behind, and the one thing newcomers get
  wrong about it. Repository documentation rather than an installable unit, written for building a
  printed or on-screen deck, and for reading straight as a cheatsheet. It is a snapshot of the
  spellbook and says so — a new spell means a missing card.

### Changed

- **Schema reading gained a uSync rung, and this changes four pack files you may have vendored.**
  `umbraco-17-feature-backfill`, `umbraco-17-planning`, `/block`, and `/check-uda` all guarded the
  absence of `.uda` files by routing to a live instance via MCP — so a uSync project was sent to an
  API for schema already committed to its own repository. The ladder is now Deploy → uSync → MCP,
  and it routes on a *matching file* rather than a folder's existence, because a uSync folder with
  no file for the type you asked about is a partial export rather than an empty schema.
  `umbraco-17-feature-backfill` also carries a Deploy-to-uSync field mapping, and the rule that
  **compositions normalize on the alias** whichever format was read — Deploy gives UDIs, uSync gives
  aliases, so a reader that keeps whichever it found works on one project and breaks on the other.
  The uSync element names were carried as unverified until 2026-08-25, when a real uSync project was
  available to check them against; see Fixed below for what they got wrong.
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

- **Core's `code-reviewer` gained two failure modes**, and `reviewer-discipline` gained the rule that
  stops them being reported twice. The agent now names an error passed onward with its origin no longer
  recorded anywhere, and a log call that folds its values into the message text instead of passing them
  as named fields. Both carry an exemption, because a response deliberately sanitized for an external
  caller is not the first finding so long as the origin survives internally, and a message carrying no
  values is not the second. `reviewer-discipline` gained **Where two domains abut**: cancellation and
  timeouts on outbound and I/O-bound work belong to the performance reviewer alone, since a rule held by
  two reviewers reaches the reader twice in a merged report — but a reviewer running *alone* raises it
  anyway, because a finding withheld is indistinguishable from a finding absent. This landed in a
  prerequisite increment and was never logged; recorded here.
- **`umbraco-17-review-rules` narrowed its outbound-call bullet**, and this **changes a pack you may
  already be running.** It now states only the form the CMS pack can claim as its own — a form
  submission handler must be async, must take a `CancellationToken` and pass it on, and must carry a
  deadline, because a token alone bounds nothing if nothing ever cancels it — and defers the general
  rule about long-running outbound calls and streams to whatever language guidance is installed,
  applying it itself where none is. Nothing is lost: with both packs installed, the two rules stated at
  the same generality put one defect into the merged report twice.
- **`/setup` treats a formatter or editor configuration as authoritative for whatever it encodes** —
  indentation, ordering, declaration form, whichever slot records it — recording what the file says
  rather than asking, and staying silent where the file is. Where an installed pack supplies a
  narrower detection recipe, that recipe wins, because it knows which evidence counts. Setup also now
  **says when a configuration overrode something**: a file that settles a question you already answered
  differently gets reported alongside your answer rather than quietly preferred, since a configuration
  is authoritative about the rule and not about your intent. **This applies to every install**, pack or
  not — it is a change to a core spell rather than to pack content.

- **`architecture-audit` is now `codebase-audit`, and it ships in the `dotnet` pack.** The audit was
  always a structural assessment of a .NET solution wearing CMS clothing; it now says so, and a .NET
  project with no CMS can install it without bringing Umbraco content along. **Seven pillars became
  five** — Umbraco-idiomatic use and headless suitability went back to the CMS pack, and
  framework-idiomatic use is explicitly *not* a pillar, because it is version- and platform-specific,
  which is what a stack pack is for: where one is installed the audit cites it, and where none is it says
  so in the report rather than guessing. **This changes a path an existing install pinned.** A lockfile
  naming `skills/umbraco-17/reference/architecture-audit/SKILL.md` names nothing now, and neither the
  installer nor `/update-toolkit` distinguishes a move from a deletion, so the fix is manual:
  `npx skills add robot-denny/cantrip/skills/dotnet --skill codebase-audit`.
- **Detection recipes and judgement criteria are split inside the audit.** The criteria stay in the four
  portable references; the greps that find the evidence moved to the pack-side hygiene reference, because
  **a search that names no technology matches everything** — one logging search sanitized down to the
  generic words went from 8 hits to 25 on a real repository, which is noise rather than a signal. The
  audit's guide now says to read both halves for the pillars whose recipes moved.
- **Deploy and `.uda` facts left `umbraco-17-starter-facts`** for the new Cloud pack. An Umbraco Cloud
  project installs both packs and loses nothing; a CMS-only project stops carrying artifact mechanics for
  a product it does not run.
- **`/umbraco-edit` states its version floor.** It works entirely through the Management API, which exists
  from Umbraco 14, and said so nowhere — a project on an earlier major would have followed it into a wall.
  Named as a version rather than as "recent versions", per the annotate-per-feature rule.
- **`/block` hedges its cross-pack deferral.** `/check-uda` now lives in a different pack, so the
  reference is marked *where installed* and is followed by what a reader without it checks by hand. A
  deferral to something absent is a silent loss of guidance, which is worse than no deferral at all.
- **A reinstall hint names the pack that provides the unit.** It used to print the literal
  `skills/<pack>`, which was already unhelpful with one pack and unresolvable with three — nothing in the
  report said where a unit came from. A `PACK_SOURCE` map makes it answerable, so the hint answers it, and
  a unit in no map still falls back to the placeholder rather than confidently naming the wrong pack.
- **The README, `docs/layout.md`, and the layer table carry three packs**, each labelled with the axis it
  is cut on — a CMS major, a product that spans majors, a language that only adds — since which axis a
  pack is cut on is what decides whether its name carries a version.

- **The spell budget is a working ceiling of ten, not a stated aim of 6–8**
  ([ADR 0010](adr/0010-skills-not-commands.md), amended). The workflow set is still eight and the
  principle is unchanged — past the ceiling, merge two stages or add a router rather than append
  another — but a budget sitting at its limit would have made the next genuine stage a documentation
  rewrite, which the aim was never meant to cost. `AGENTS.md` carries the new number and check 16
  holds it, so it cannot drift back. **Nothing here arrives by update** — the budget governs what this
  repository ships, not anything installed.
- **The README describes the toolkit that exists.** `design-system-authoring` is a method for writing
  your project's own design-system skill, not something that learns your conventions as you build; the
  reviewer contract lists all four of its pillars, evidence included; and the packs section says plainly
  that core assumes no stack while the three packs shipped today happen to cover Umbraco and .NET.
  Prose is re-wrapped to the ~100 column convention the other markdown files use. **Documentation only**
  — README and `adr/` are not vendored into a consuming project.

### Fixed

- **`umbraco-17-feature-backfill` looked for element types under a filename that does not exist**, so
  following it would have found none on any Deploy project. It told you to locate
  `element-type__*.uda` and said the kind was in the filename for Deploy. Deploy serializes element
  types as `document-type__*.uda` with the same artifact type; the kind is `Permissions.IsElementType`
  *inside* the file, and it is emitted only when true. Verified against two Deploy projects, one of
  which holds 171 element types and zero `element-type__` files. A reader following the old guidance
  would have reported a project full of blocks as having none — the silent-empty read ADR 0006
  forbids, arriving through the guidance rather than through a missing file.
- **The uSync half of that mapping was unverified, and three parts of it were wrong or too thin.** Now
  checked against a real uSync project. The alias is an attribute on the root `<ContentType>`, not an
  `<Info>` child. `<IsElement>` is always written, `true` or `false` — the *opposite* of Deploy's
  only-when-true flag, so a reader must branch per format rather than assume symmetry. Tabs and groups
  are both `<Tab>` entries told apart by `<Type>Tab</Type>` versus `<Type>Group</Type>`, and a
  property's `<Tab Alias>` is sometimes a `tab/group` path and sometimes a bare alias that may name
  either level — so it must be resolved against the `<Tabs>` list rather than inferred from the
  slash. The file also now answers its own open question: **uSync filenames are the lowercased
  alias**, so a known alias can be read as a single file if the lookup case-folds.
- **Neither format's version marker was documented, and they need opposite handling.** Deploy stamps
  `__version` on every artifact and one project holds a mix of them, because artifacts only
  re-serialize when touched — so a version check belongs per file, and refusing a whole read over one
  stale artifact would reject the normal case. uSync declares one `format` for the entire export in
  `usync.config`, on a numbering line unrelated to its package version or its folder name — so there
  the check is a single gate.
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
- **Every shipped script broke on a Windows checkout.** The repo had no `.gitattributes`, and Git for
  Windows defaults `core.autocrlf=true` — so the ten `.sh` files, `check-preserved.py`, and
  `.githooks/pre-commit` all checked out with CRLF, and bash fails on the trailing carriage return with
  `$'\r': command not found`. Because the hook runs the contract gate, a Windows contributor's *first
  commit* failed with an error that reads like a corrupt repo. In a consuming project the same thing hit
  the pack's four `architecture-audit` scripts, which that skill calls as mandatory steps rather than
  optional ones. Now pinned to `eol=lf`; `core.autocrlf` is per-machine and could never have fixed this
  for anyone but the person who set it.
- **The install-shape guidance buried the property that matters on Windows.** The single-agent shape was
  presented as merely "cleaner if you only use Claude Code" when its load-bearing difference is that it
  creates **no symlinks** — and symlinks are exactly what a Windows checkout without `core.symlinks=true`
  turns into path-shaped text files, leaving a skill directory that looks present and contains no
  `SKILL.md`. The table now states it, the multi-tool case is named as the one needing setup, and the
  reviewer-agent step carries a copy-based alternative — which `check-install.sh` already accepted, since
  it compares content rather than looking for a link.

- **The install checker's pack roster listed two of the eight pack units that existed.** A unit absent
  from `check-install.sh`'s roster is skipped entirely — not verified when it is installed, not reported
  when it is not — so it passes as though absent either way. `umbraco-17-review-rules`,
  `umbraco-17-starter-facts`, `architecture-audit`, `/block`, `/check-uda`, and `/umbraco-edit` were all
  in that state, meaning a project running the full CMS pack could be told everything was fine about six
  units the checker never looked at. **Gate check 13 now covers `ROSTER_PACK` as well as `ROSTER_CORE`**,
  comparing it against every unit outside `skills/core`. It had gated only the core half, which is
  exactly why the core half was caught drifting and the pack half was not — the same defect as the entry
  above, one list over, and the gate that found it had been built with the blind spot in it.

- **A slot read by two packs was surveyed for only one of them.** `.agents/config/paths.md → ## Umbraco`
  is read by `umbraco-17-planning` and by `/check-uda`, and `PACK_SLOTS` listed only the planning unit —
  so a project that installed the Cloud pack alone was never told whether a slot its drift check depends
  on was filled. Registering the second reader then exposed the other half of the defect: the survey
  appends one entry per reader, so the slot was counted **twice** and the reported total was wrong rather
  than merely incomplete, which is the worse failure because a wrong total reads as authoritative. Both
  halves are fixed and the `shared-slot-two-packs` fixture holds them. This is the first slot with readers
  in two packs, and splitting a pack is what produced it.
- **`/check-uda`'s second slot was never verified at all.** It declares
  `.agents/config/conventions.md → ## Block palette parity`, `PACK_SLOTS` did not list it, and an
  unlisted slot is skipped — so the checker reported on one of the spell's two slots and looked
  complete. Present since the slot was declared.
- **A CMS-specific scoring anchor had already crept into the portable half of the audit**, which is all it
  takes for those four references to stop being movable to core. Found by writing check 14 rather than by
  reading them, which is the argument for the check: noticing it by eye costs four long re-reads. The
  same gate then caught the fix overreaching — the pass that relocated the detection recipes wrote the
  pack-side filename into a portable file, and a filename that contains the technology is a technology
  name. A portable file names the *kind* of file it pairs with and lets the unit's own guide route.
