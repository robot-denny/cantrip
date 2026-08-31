# Plan: Token-Reading Styleguide Page

**Spec**: `_work/styleguide/spec.md`
**Branch**: `feature/styleguide`
**Work type**: `change-to editor-guides` — copied verbatim from the spec's `**Work type**:` line;
this decides how the final step records behavior
**Feature doc**: `_features/editor-guides.md` — copied from the spec; the final step targets this,
not the increment slug

## Context

The editor-facing guides capability shipped on 2026-08-29 with the guides section, the guide page
type, the derived index, the `/guide` spell and its script, and the shared
`umbraco-17-guide-scaffolding` reference. This increment ships story 1 of discovery's four — the
styleguide — as **one new unit** in the `umbraco-17` pack (the `/styleguide` spell and its script),
plus **amendments to two shipped units**: the scaffolding reference gains the showcase element types
and two slot rows, and `guide.py`'s inventory determiner gains one exclusion.

The unit of work in this repo is **a shipped unit plus its fixtures**, established by the
`install-verification` increment and followed by the guides increment. The test harness is
`tests/run.sh` with one suite per subject; this increment adds a `styleguide-check` suite and two
cases to the existing `guide-check` suite.

**This plan resolves seven of the spec's eight open questions.** Each resolution is a Key Decision
below with its reasoning, so no step re-derives it. The one left open is named there as left open.

---

## Key Decisions

### Resolved from the spec's Open Questions

- **A design token, for this capability's purposes, is a value that survives to the browser.**
  That is not a definition of the term in general — it is the only definition under which the
  headline acceptance criterion ("reads the project's design tokens live... without regeneration")
  can be true. In practice that means **CSS custom properties**. A preprocessor variable is a real
  design token by any normal usage and is still outside this capability, because no markup can read
  it at render time.

- **A build-time-only token layer is a stop, not a baked snapshot.** The spec left this undecided
  between "say so and stop" (honest, useless to that project) and "offer clearly-labelled baked
  values" (useful, stale). **Chosen: stop, and name the remedy** — a custom-property layer that the
  preprocessor variables feed, which is an afternoon of front-end work and after which every scenario
  here becomes true. A baked snapshot would fail the headline criterion while looking like it passes,
  which is the silent-staleness failure the whole capability refuses. Reversible additively if a
  project ever argues for it; the reverse is not.

- **Detection is a slot with a recipe, exactly like `## Schema serialization`.**
  `.agents/config/stack.md` → `## Design tokens`. Declared in `umbraco-17-guide-scaffolding` and
  **nowhere else**, for the reason that file already gives about its two existing slots: one slot has
  one point of authority, and a second declaration has to reproduce the fallback word for word and
  diverges the first time one copy is edited.

- **Detection reports every layer it finds and names which is authoritative**, rather than stopping
  at the first — the same rule the schema-serialization recipe already states, and for the same
  reason: stopping early reads a fallback as the whole answer. A project holding preprocessor
  variables *and* custom properties is read from the custom properties.

- **A project design-system skill is the spell's rung, not the script's.** Such a skill "names the
  files where conventions actually live — the stylesheet holding the token definitions"
  (`design-system-authoring`, Step 2), but it names them in **prose**. There is nothing machine-
  readable to parse, so the script detects from the filesystem and the spell reads the pointer. This
  is the same script-computes / spell-writes split the guides increment settled, applied to a new
  input.

- **A showcase element needs no theme property of its own, but a styleguide may still have several
  themes to show, and how to show them is the generating agent's call.** Two halves, and only the
  first is settled.

  **Settled:** a swatch that carries a *token name* rather than a value follows a theme with nothing
  configured, because re-theming a region is the project's own CSS re-pointing what that name means.
  A swatch carrying a value would need a per-theme property; one carrying a name does not. And the
  themed region itself is supplied by whatever mechanism the project already uses to theme a block —
  a setting on the block, a wrapper, a section class — which the showcase inherits by copying the
  closest existing block, exactly as it inherits spacing and visibility. That is `/block` Step 5's
  rule applied to settings rather than to markup.

  **Not settled, and deliberately not decided here:** a project with several themes is under-served
  by a showcase that renders one of them and implies there are no others. **How** to present that —
  one section repeated per theme, a theme switcher, a single representative with the set named
  alongside — depends on how the project themes things, and projects do this differently enough that
  a rule written now would be fitted to one example. **So the spell instructs the generating agent to
  ask whether the project has themes and to decide the presentation from the project's own
  mechanism**, the same deferral this capability already makes for markup. A measured project carries
  nine themes selected per block from a dropdown, re-pointing role tokens that alias a fixed brand
  palette; that is one shape, not the shape.

  **Revisit** when more worked examples are available across projects. If they converge, this becomes
  a rule; if they do not, the deferral was correct. Recorded because the spec called the property
  shape cheaper to decide now than to add later — and the answer is that no property is needed either
  way, so deferring the presentation costs nothing later.

- **The showcase element types are excluded from the audit's inventory by palette, and the exclusion
  is declared rather than inferred.** This is the spec's load-bearing open question and it needed a
  change to shipped behavior either way. `inventory.py` reads **every** block-editor palette and
  de-duplicates, so a showcase element registered anywhere becomes a documentable unit the audit
  reports as undocumented — permanently, on every project that runs `/styleguide`.
  - **Excluded by palette, not by element alias**: one name to record instead of N, and a showcase
    element added next year inherits the exclusion for free.
  - **Declared in the `## Editor guides` slot**, which already exists to record what aliases a
    project actually used. `/styleguide` writes the value when it scaffolds.
  - **The unconfigured case fails visibly, not silently**: a project whose slot does not name the
    palette gets its showcases reported as undocumented — a wrong line in a report with a one-line
    fix, rather than a quietly smaller count. That is the same direction the reference chose for its
    guides-node key.
  - The script learns the palette through a flag, `inventory --exclude-palette <name>`, because the
    script does not read `.agents/` — the same seam as the existing `--adapter` and `--dossier`.

- **Adopting a project's pre-existing hand-built styleguide page is a deliberate non-goal.** The
  shipped adoption path is the write of one property on a page that is already an `editorGuide`; a
  project's own styleguide is a different document type, so adoption would be a **retype** —
  destructive, irreversible, and the one thing this capability never does silently. The spell reports
  that such a page exists and stops short of touching it.

- **Left open, and named as left open:** whether a swatch reading a removed token can report itself
  rather than rendering blank. This pack ships no markup, so it is a constraint on what a project's
  own view must do — the same shape as the index's render-as-text-never-as-markup constraint already
  in the reference. It is **stated in the reference and enforced nowhere**, and its scenario is
  expected to land uncovered on purpose.

### Shape of the new unit

- **`/styleguide` is a spell in `skills/umbraco-17/spellbook/styleguide/`**, `disable-model-invocation:
  true` like every other spell in the spellbook. Its script sits at `scripts/styleguide.py` inside
  the spell's own directory — the same ADR 0002 reasoning the guides increment recorded: the asset is
  not shared, `/styleguide` cannot function without it, and nothing else calls it.

- **Two subcommands, and no more**: `tokens` (what token layers the project holds, which is
  authoritative, which are runtime-resolvable, and the custom properties found) and `precheck` (are
  both halves of the precondition met). No `seed` subcommand — the grouping that a seed set would
  need is the person's to make, per the decision below, so a third subcommand would compute
  something nobody should trust.

- **Exit codes match `guide.py`'s vocabulary**: **0** the read completed, **1** the read failed and
  the message says why, **2** the call was malformed. **3** means the read completed and the answer
  is negative — an unmet precondition, or a token layer that cannot be read at render time.
  **Unlike `guide.py`'s 3, this one is not gated behind `--strict`**, and the asymmetry is
  deliberate: the audit's findings are a backlog someone works through, while an unmet precondition
  is a stop. A caller that ignores it produces the invented-conventions output this increment exists
  to refuse.

- **The script classifies colors and nothing else.** A custom property whose declared value is a hex,
  `rgb(`, `hsl(`, `oklch(`, or a named CSS color is a color; everything else is reported as
  **unclassified**, with its declared value, for a person to group. A name-based classifier that
  reads `--space-brand` as a color is exactly the plausible-wrong output this repo refuses
  everywhere, and colors are the one group whose value shape is unambiguous.

- **An alias whose target is itself a declared color is a color.** `--brand-primary:
  var(--blue-500)` classifies as a color because `--blue-500` was collected in the same read and is
  one. **This is a lookup among the properties already collected, not a resolution to a value** — the
  reported value stays `var(--blue-500)` verbatim, and the token is still marked an alias.

  Without this rule the classifier inverts on exactly the projects that theme well. A two-tier system
  — a fixed brand palette, plus role tokens that alias into it and are what a theme re-points —
  would report every fixed palette entry as a color and drop every role token into *unclassified*,
  because a role token's declared value is a `var()`. On a measured project that is 99 fixed entries
  classified and 33 re-pointable ones buried. The buried set is the one a styleguide most needs to
  show, because it is the one that changes.

- **`var()` indirection is reported, never resolved.** The declared value is emitted verbatim and the
  token is marked an alias; the *chain* is never walked to a literal. Resolving it would be a second
  implementation of what the browser already does, and the two would eventually disagree. The
  classification rule above is deliberately one hop and deliberately not a resolution: it answers
  "what kind of thing is this", never "what color is this".

- **"Does this project have exemplar blocks" is answered from block views on disk, not from the
  palette determiner.** `precheck` searches for existing block views (`*.cshtml`) the way `/block`
  Step 5's greenfield guard does. Two reasons: the exemplar you copy is a **view**, and calling
  `guide.py` from `styleguide.py` would couple two spell directories that install separately — under
  a selective install `/guide` may be absent.

### Conventions assumed because a slot was empty

This repo has no `.agents/config/` at all — it is the toolkit, not a consuming project — so every
slot the spells reference is empty here. Recorded so no step re-derives them:

- **`## Tests` → `tests/run.sh`**, one suite per subject, established by `install-verification`.
  This increment adds `tests/styleguide-check/` with a `subject` file naming
  `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py`, and a generator
  `tests/make-styleguide-fixtures.sh` following `tests/make-guide-fixtures.sh`'s conventions.
- **`## Build` → there is no build.** The gates are `tests/run.sh`, `./scripts/check-contract.sh`,
  and `./scripts/check-install.sh`. Python is stdlib-only Python 3, per the guides increment.
- **`## Code layout`** → `skills/<pack>/spellbook/<name>/` for spells, `skills/<pack>/reference/<name>/`
  for references.

### Planning gotchas discovered here — the `## Planning gotchas` slot is empty and these belong in it

- **Contract check 13 compares `ROSTER_PACK` in `scripts/check-install.sh` against every `SKILL.md`
  outside `skills/core`.** Adding the `styleguide` unit **fails the contract check** until that array
  gains it. This is a gate, not a nuisance — but it fires in Step 10 for work done in Step 8, so
  expect it.
- **`PACK_SOURCE` and `PACK_SLOTS` in the same file are hand-maintained and nothing gates them.** A
  missing or wrong entry fails silently. The guides increment's commit message records learning this
  the hard way; four `PACK_SLOTS` entries were needed where two were planned, because a spell that
  declares a slot in its own text and installs separately would otherwise survey it for nobody.
- **ADR 0010's ten-spell ceiling is enforced by contract check 16 against `skills/core/spellbook`
  only.** A pack spell is ungated, which is the claim the deferred note made and which the check
  confirms. `/styleguide` costs no core budget.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — The `styleguide-check` suite and the RED apparatus

> **Prompt**: Implement Step 1 of `_work/styleguide/plan.md`. Create `tests/make-styleguide-fixtures.sh`
> following the conventions of the existing `tests/make-guide-fixtures.sh` (generated rather than
> hand-built, minimal fake project trees, one `expect` file per case, idempotent regeneration), and
> `tests/styleguide-check/subject` holding the single line
> `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py`. Generate exactly two cases:
> `tokens-custom-properties` (a fake project with a stylesheet declaring `--brand-primary: #0B5FFF`,
> `--brand-ink: #101828`, and `--space-3: 0.75rem` on `:root`) and `tokens-none` (a fake project with
> a stylesheet that hardcodes every color as a literal and declares no custom property). Both invoke
> `tokens` via `args:`. Read `tests/README.md` for the `expect` grammar — the directives available are
> `exit:`, `args:`, `contains:`, `not_contains:`, `same_stdout_as:`, `stdout_matches:`, and `mask:`.
> Do **not** create the script yet. Run `tests/run.sh styleguide-check` and confirm both cases fail
> because the subject is absent, and that the failure names a missing subject rather than a malformed
> fixture.

**What to build**: `tests/make-styleguide-fixtures.sh`, `tests/styleguide-check/subject`,
`tests/styleguide-check/tokens-custom-properties/`, `tests/styleguide-check/tokens-none/`.

**Test first**: this step *is* the test apparatus. RED is both cases failing because the script does
not exist.

**Validation**:
- [Automated]: `bash -n tests/make-styleguide-fixtures.sh`; the generator regenerates cleanly and is
  idempotent (run twice, `git status` clean the second time); `tests/run.sh styleguide-check` reports
  2 cases, both failing; `tests/run.sh guide-check` and `tests/run.sh install-check` are unchanged.
- [Automated]: `./scripts/check-contract.sh` passes. Check 1 scans by extension — if the fixtures use
  a stylesheet extension not already in the allow-list (both the `git ls-files` branch and the `find`
  branch), add it, then prove it is actually scanned by putting a forbidden token in a fixture,
  seeing check 1 fail, and removing it.
- [Manual]: read one failure and confirm it says the subject is missing.

---

### Step 2 — `tokens`: the runtime-resolvable layer

> **Prompt**: Implement Step 2 of `_work/styleguide/plan.md`. Create
> `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py` — stdlib-only Python 3, no
> dependencies — with a `tokens` subcommand taking `--project-root` (defaulting to the working
> directory) and emitting JSON on stdout. It scans the project's stylesheets for **CSS custom
> property declarations** and reports each one's name and its declared value verbatim. Classify a
> property as a color when its declared value is a hex literal, `rgb(`/`rgba(`, `hsl(`/`hsla(`,
> `oklch(`/`oklab(`, or a named CSS color; classify **everything else as unclassified** and carry its
> declared value so a person can group it — do not guess a group from the property's name. A value of
> the form `var(--other)` is emitted verbatim and marked as an alias; **do not resolve the chain.**
> But **do classify an alias by one hop**: where `--other` was collected in this same read and is
> itself a color, the aliasing property is a color too. That is a lookup among what you already have,
> not a resolution — the reported value stays `var(--other)` verbatim and the alias marking stays.
> Without it, a project whose themeable role tokens all alias into a fixed palette gets every
> re-pointable token dropped into `unclassified`, which inverts the classifier on exactly the
> projects that theme well. Exit
> **0** when the read completed (including when it found nothing), **1** when the read itself failed
> with a message saying why, **2** on a malformed call. Follow `guide.py`'s structure: `styleguide.py`
> is the only public surface, and **`chmod +x` it** — the runner reports `subject missing or not executable` for a subject that is present but unset, which looks identical to an absent file. Make `tests/run.sh styleguide-check` pass both cases from Step 1 —
> `tokens-none` must exit 0 reporting zero custom properties, which is a completed read, not a
> failure.

**What to build**: `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py` (CLI dispatch, the
`tokens` subcommand, custom-property scanning, color classification by value shape plus the one-hop
alias rule, JSON output).

**Test first**:
- The RED signal exists from Step 1: `tests/run.sh styleguide-check` fails both cases.
- Before implementing, extend `tokens-custom-properties/expect` to assert the *classification*, not
  just the scan: `contains:` the two brand properties as colors, and `contains:` `--space-3` as
  unclassified carrying `0.75rem`. Assert the observable output, never an internal function.
  Re-run and confirm still RED.
- Add a third property to the `tokens-custom-properties` fixture — `--role-primary:
  var(--brand-primary)` — and assert it is classified a **color**, marked an **alias**, and carries
  `var(--brand-primary)` as its reported value. This is the one-hop rule's test, and all three
  assertions are needed: classification alone passes on an implementation that resolved the chain,
  and the verbatim-value assertion is what proves it did not.
- **Add a `stdout_matches:` golden file to `tokens-custom-properties`, and it is required rather than
  optional.** Step 1's review raised this as its one Major: `contains:`/`not_contains:` are presence
  checks, so nothing in that grammar can assert **how many times** a token is reported, and the
  fixture deliberately declares each name and then uses it through `var()`. A classifier that emits a
  token once per occurrence rather than once per declaration therefore passes every `contains:` line
  in the suite. The golden file is the only directive in the grammar that catches it, and it becomes
  writable here because this step is where the report format first exists. Use `mask:` for anything
  environment-dependent, as `guide-check`'s `deploy-dossier` case does for its signature.
- GREEN is `tests/run.sh styleguide-check` at 2/2.

**Validation**:
- [Automated]: `tests/run.sh styleguide-check` 2/2; `tests/run.sh` overall unchanged elsewhere.
- [Automated]: `python3 skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py` with no
  subcommand exits 2; with a nonexistent `--project-root` exits 1 with a message naming the path.
- [Manual]: run `tokens` against this repo (which has no stylesheets) and confirm it exits 0
  reporting nothing found, rather than erroring.
- [Automated]: **record the suite's wall time** — `time tests/run.sh styleguide-check`. Until this
  step the two cases exit through the runner's fast subject-missing path at roughly 39ms; from here
  each execs a Python subprocess against a real fixture tree, which is a different cost profile. The
  plan adds about five more cases to this suite, so the number to watch is per-case cost, not the
  total. Step 1's performance review flagged this as the thing to check here rather than there.

---

### Step 3 — More than one token layer, and which is authoritative

> **Prompt**: Implement Step 3 of `_work/styleguide/plan.md`. Extend `tokens` in
> `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py` so it **records every token layer it
> finds and names which is authoritative**, rather than stopping at the first — the same rule
> `umbraco-17-guide-scaffolding`'s `## Schema serialization` recipe already states, and for the same
> reason. Recognize three layers: CSS custom properties (runtime-resolvable), preprocessor variables
> (`$name:` / `@name:` in `.scss`/`.sass`/`.less`, build-time only), and a utility framework's theme
> configuration (build-time only). Custom properties are authoritative whenever present. Report each
> layer found with a count and whether it is runtime-resolvable. Add one fixture case,
> `tokens-two-layers`, to `tests/make-styleguide-fixtures.sh`: a project holding SCSS variables
> **and** a `:root` block of custom properties that reference them. Its `expect` asserts that both
> layers are reported, that the custom properties are named authoritative, and — via `not_contains:`
> — that no SCSS variable name appears among the reported tokens.

**What to build**: `styleguide.py` (layer discovery, the authoritative-layer rule, the layer report),
`tests/make-styleguide-fixtures.sh` and `tests/styleguide-check/tokens-two-layers/`.

**Test first**:
- Write the `tokens-two-layers` case and its `expect` first. Run `tests/run.sh styleguide-check
  tokens-two-layers` and confirm RED — today the layer report does not exist.
- The assertion that carries the behavior is the `not_contains:` one: a reader that merges layers
  would put SCSS names in the token list and pass every `contains:` line.

**Validation**:
- [Automated]: `tests/run.sh styleguide-check` 3/3; the generator still idempotent.
- [Manual]: confirm the report names the authoritative layer explicitly rather than leaving it to be
  inferred from ordering.

---

### Step 4 — A layer that cannot be read at render time is refused, not baked

> **Prompt**: Implement Step 4 of `_work/styleguide/plan.md`. Make `tokens` in
> `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py` **exit 3** when the project holds
> token layers but **none of them is runtime-resolvable** — preprocessor variables or a utility theme
> config with no custom-property layer. The report says the palette cannot be read at render time,
> names the layers it did find, and names the remedy: a custom-property layer the existing variables
> feed. It must emit **no token values** in that case — no color literal may appear anywhere in the
> output, because a baked value presented beside a live-reading promise is the staleness this
> increment exists to prevent. Exit 3 is unconditional here and is deliberately not gated behind a
> `--strict` flag the way `guide.py`'s is; the plan's Key Decisions say why. Add fixture case
> `tokens-build-time-only`: a project with SCSS variables holding real hex colors and no `:root`
> block. Its `expect` asserts `exit: 3` and, critically, `not_contains:` each of the fixture's hex
> values.

**What to build**: `styleguide.py` (the runtime-resolvable gate, exit 3, the remedy message),
`tests/make-styleguide-fixtures.sh` and `tests/styleguide-check/tokens-build-time-only/`.

**Test first**:
- Write the case first, with the `not_contains:` hex assertions. Run it and confirm RED — today the
  layer is reported and its values would come through.
- The `not_contains:` lines are the test. `exit: 3` alone would pass on an implementation that
  refused *and* printed the values.

**Validation**:
- [Automated]: `tests/run.sh styleguide-check` 4/4; `tokens-two-layers` still exits 0, proving the
  gate fires on the absence of a runtime layer rather than on the presence of a build-time one.
- [Manual]: read the refusal message and confirm it names the remedy concretely enough to act on.

---

### Step 5 — `precheck`: both halves of the precondition, named separately

> **Prompt**: Implement Step 5 of `_work/styleguide/plan.md`. Add a `precheck` subcommand to
> `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py`. It answers the spell's precondition
> in two independent halves: **is there a runtime-resolvable token layer** (reusing `tokens`, not
> reimplementing it) and **are there exemplar block views to copy conventions from** — the latter
> answered by searching for existing block views (`*.cshtml`) the way `/block` Step 5's greenfield
> guard does, **not** by calling `guide.py`, which installs separately and may be absent. The report
> states each half as met or unmet **by name**, so a project meeting one half is told which. Exit
> **0** when both halves are met, **3** when either is unmet, **1** on a failed read. Add three
> fixture cases to `tests/make-styleguide-fixtures.sh`: `precheck-both` (views and custom properties
> present), `precheck-no-tokens` (twelve block views, colors hardcoded, no custom properties), and
> `precheck-greenfield` (custom properties present, no block views at all). Each `expect` asserts the
> exit code and that the report names the met half as well as the unmet one.

**What to build**: `styleguide.py` (`precheck`, the exemplar-view search, the two-halves report),
`tests/make-styleguide-fixtures.sh`, and the three new `tests/styleguide-check/precheck-*/` cases.

**Test first**:
- Write all three cases first, then run `tests/run.sh styleguide-check` and confirm the three new
  ones are RED while the four existing ones stay GREEN.
- Each case asserts the **met** half is named too. A report that only lists failures passes a naive
  assertion and leaves the caster unable to tell "no tokens" from "nothing here at all".

**Validation**:
- [Automated]: `tests/run.sh` fully green, and `styleguide-check` gained exactly the three
  `precheck-*` cases this step names — no more and no less.

  <!-- Stated as a condition rather than a count on purpose. Steps 2, 3 and 4 each named a
       number (2/2, 3/3, 4/4) and every one of them was stale by the time the step ran,
       because review kept adding fixtures the plan did not anticipate — the suite was 6 when
       Step 4 expected 4. A count is a claim about the whole suite; what a step can actually
       promise is what IT added. Steps 6 onward already read this way. -->
- [Manual]: run `precheck` against one of the read-only source repos in
  `.claude/settings.local.json` and confirm the answer matches what is actually there. Report the
  outcome in the step's notes; **do not commit anything derived from it** — per `AGENTS.md`, nothing
  client-identifying enters a committed file.

---

### Step 6 — The scaffolding reference: showcase element types, and two slot rows

> **Prompt**: Implement Step 6 of `_work/styleguide/plan.md`. Amend
> `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` — the shipped authority on this
> section's schema — rather than creating a new reference unit. Add: (a) a **showcase element types**
> section naming the types a styleguide page's sections are built from, each carrying a **token name**
> rather than a value, and stating that this pack ships no view for them; (b) the consequence that
> **themes need no property**, because a view rendering a token resolves per theme already; (c) the
> constraint that a project's own showcase view **must name a token it cannot resolve** rather than
> rendering an unexplained blank — written as a constraint on what a project's component may do,
> alongside the existing render-as-text-never-as-markup constraint on the index, and explicitly not
> something this pack enforces; (d) two new rows in the `## Editor guides` slot table — the showcase
> element aliases, and **the styleguide's showcase palette**, whose purpose is the inventory exclusion
> in Step 7; (e) a new slot declaration, **`.agents/config/stack.md` → `## Design tokens`**, with its
> empty-slot fallback being the detection recipe Steps 2–4 implement, including that every layer found
> is recorded and custom properties are authoritative. The file's "Four types, and the two that are
> absent are absent on purpose" line now undercounts — correct it rather than leaving it to disagree.
> Every `**Slot:**` needs a fallback beside it or contract check 4 fails.

**What to build**: `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` (five
amendments), and its `description:` frontmatter if the added scope is not covered by it.

**Test first**: no executable behavior. The check is contract-level and by eye — see Validation.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes — in particular check 4 (a `**Slot:**` needs a
  fallback), check 1 (no client-identifying content), and check 1b (no authoring-org name in a
  shipped skill).
- [Manual]: confirm the `## Design tokens` slot is declared **only** here, and that the styleguide
  spell in Step 8 cites it rather than restating it — the file's own one-point-of-authority rule.
- [Manual]: confirm the corrected type-roster sentence agrees with the table beneath it.

---

### Step 7 — The inventory exclusion, and the audit's silence on a styleguide

> **Prompt**: Implement Step 7 of `_work/styleguide/plan.md`. This is a change to **shipped**
> behavior. Add an `--exclude-palette <name>` flag to the `inventory` subcommand of
> `skills/umbraco-17/spellbook/guide/scripts/guide.py`, threaded into
> `scripts/guidelib/inventory.py`: a block-editor palette named by the flag contributes **no**
> components to the documentable-unit count. Without the flag, behavior is exactly as today. The
> inventory report must **state that a palette was excluded and name it**, beside the determiner's
> rule it already prints — an exclusion that changes a count silently is the one thing the audit's
> report shape refuses. Add two `guide-check` cases via `tests/make-guide-fixtures.sh`:
> `inventory-excluded-palette` (a project whose palettes include a styleguide showcase palette,
> asserting the count drops by exactly the showcase entries and that the report names the exclusion)
> and `audit-styleguide-silent` (a guides section holding one styleguide page carrying **no**
> `guideSource` alongside N component guides, asserting all three audit counts are unaffected and
> the styleguide is named in none of the three sections). Read
> `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` → *The audit's report shape*
> first; do not invent captions.

**What to build**: `skills/umbraco-17/spellbook/guide/scripts/guide.py` (flag),
`scripts/guidelib/inventory.py` (exclusion, report line), `tests/make-guide-fixtures.sh`, and the two
new `tests/guide-check/` cases.

**Test first**:
- Write both cases first. Run `tests/run.sh guide-check` and confirm the two new ones are RED and
  **all existing cases stay GREEN** — an unflagged run must be byte-identical to today, and the
  existing suite is the assertion that proves it.
- `audit-styleguide-silent` is expected to pass **without any code change**: a guide claiming no
  source is already excluded from all three sections. That is the point of the case — it verifies an
  inherited property rather than assuming it. If it goes GREEN immediately, say so; do not
  manufacture a change to make it look earned.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — every prior case still passing, plus the two new ones.
- [Automated]: `tests/run.sh` overall green; `./scripts/check-contract.sh` passes.
- [Manual]: run `inventory` on a fixture with and without the flag and confirm the two reports differ
  only in the excluded entries and the added exclusion line.

---

### Step 8 — The `/styleguide` spell: the generate path

> **Prompt**: Implement Step 8 of `_work/styleguide/plan.md`. Create
> `skills/umbraco-17/spellbook/styleguide/SKILL.md`, with frontmatter matching the pack's other
> spells: `disable-model-invocation: true`, an `argument-hint`, and an `allowed-tools` list. Follow
> `skills/umbraco-17/spellbook/guide/SKILL.md`'s shape — a *What this spell does not decide* section
> citing `umbraco-17-guide-scaffolding` as the authority on the schema, the slots, and the showcase
> element types, and **restating none of it**; a *script's surface* table for `tokens` and `precheck`
> with their exit codes; then numbered steps. The generate path: run `precheck` and stop on a
> non-zero exit; resolve the guides node from the `## Editor guides` slot by its **recorded key**,
> never by route or name, per the reference; find or create the styleguide's kind container (a kind
> with no container is a container to create, never a similarly-named node to fall back on); run
> `tokens` and present the colors and the unclassified properties for a person to group; scaffold the
> showcase element types and their palette, recording the palette name in the slot so Step 7's
> exclusion applies; **delegate view authoring to `/block`** by suggestion only — this spell never
> invokes another. Add one instruction about **the styles an editor can apply**: the
> common-elements showcase should cover them, and where the CMS exposes a menu of named styles to
> editors, that menu is how the agent knows which ones matter — they are the system's styles shown
> to the people who apply them, not a separate set earning a section of their own. Say that a
> literal value in an editor-facing stylesheet which does not trace back to a token is **drift to
> report, not a style to showcase**, and that reporting it is a later increment rather than this
> spell's job. **State this without naming a CMS mechanism, a file, or a property editor** — the
> shape differs between versions and this is an L1 file. Add one instruction about **themes**: ask whether the project themes its blocks,
> and where it does, decide from the project's own mechanism how the showcase should demonstrate the
> theme set — one section per theme, a switcher, or a representative with the set named alongside.
> **Do not prescribe one.** State that the showcase element itself needs no theme property, because a
> swatch carrying a token name is re-pointed by whatever the project already uses to theme a region,
> which the showcase inherits by copying the closest existing block. Say plainly that this is the
> agent's judgement at generation time, the same deferral the spell already makes for markup, and
> that it is expected to be refined once more worked examples exist. Write nothing before a person says yes, and a yes to one section is not a yes to
> another. End with a report block and a `Next:` line.

**What to build**: `skills/umbraco-17/spellbook/styleguide/SKILL.md`.

**Test first**: no executable behavior. The manual checks in Validation are the signal.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes — check 4 (slots carry fallbacks), and check 8 /
  its pack-level sibling for L1 content (no project facts, no hardcoded absolute paths, no tool
  versions).
- [Manual]: confirm the spell **cites** the two slots rather than declaring them — the reference is
  the single point of authority, and a second declaration is the divergence that file warns about.
- [Manual]: confirm no markup, CSS class, or front-end pattern appears anywhere in the file. This is
  the capability's organizing principle and the spell is where it is easiest to break.
- [Manual]: confirm the `Next:` line suggests and does not invoke, per `AGENTS.md`.

---

### Step 9 — The `/styleguide` spell: the refusal paths, and where output lands

> **Prompt**: Implement Step 9 of `_work/styleguide/plan.md`. Extend
> `skills/umbraco-17/spellbook/styleguide/SKILL.md` with the paths that do not generate. **Greenfield
> refusal**: with no block views to copy conventions from, the work stops, having created nothing —
> and the refusal names the same two escape hatches `/block` Step 5 offers (point at another codebase
> to take conventions from, or establish the convention explicitly and say plainly that you are
> establishing rather than following it). State the hazard this guards, verbatim from the spec: a
> styleguide scaffolded at project setup makes a color-swatch view the exemplar every real block is
> later copied from. **Build-time-only refusal**: relay the script's exit 3 and its remedy; do not
> re-derive it or soften it into a baked snapshot. **A pre-existing hand-built styleguide page of
> another document type**: report that it exists and stop — adoption would be a retype, which is
> destructive and irreversible, and this capability never does that silently. **An unrecorded guides
> node**: not an absent one; say the key is the one fact only the project can supply and ask for it,
> exactly as `/guide` Step 1 does. Finally add a *Where a report or a rendered file lands* section
> following `/guide`'s: print first, write only when asked, and ask the durable-or-temporal question
> rather than choosing.

**What to build**: `skills/umbraco-17/spellbook/styleguide/SKILL.md` (the refusal paths, the
artifact-disposition section, the Conventions list).

**Test first**: no executable behavior.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes.
- [Manual]: walk each of the four refusal paths against the matching Step 5 fixture and confirm the
  spell's instruction matches what the script actually exits with — a spell that describes an exit
  code the script does not produce is the drift this pairing exists to prevent.
- [Manual]: confirm no refusal path leaves a partially-scaffolded section behind.

---

### Step 10 — Register the unit, and document it

> **Prompt**: Implement Step 10 of `_work/styleguide/plan.md`. Register the new unit everywhere it
> must be visible, and expect `./scripts/check-contract.sh` to be **failing** when you start —
> check 13 compares `ROSTER_PACK` against every `SKILL.md` outside `skills/core`, and Step 8 added
> one. In `scripts/check-install.sh`: add `styleguide` to `ROSTER_PACK`; add
> `"styleguide|umbraco-17"` to `PACK_SOURCE`; and add the `PACK_SLOTS` entries for the new
> `## Design tokens` slot — one per **reader**, which is both `umbraco-17-guide-scaffolding` (it
> declares the slot) and `styleguide` (it reads it), because the two install separately and a
> scaffolding-less install would otherwise survey the slot for nobody. That is the correction the
> guides increment had to make after the fact; do not repeat it. In `README.md`: add a `/styleguide`
> row to the `umbraco-17` pack table. In `CHANGELOG.md`: describe what shipped, user-visibly. In
> `ROADMAP.md`: move the styleguide item out of **Next** into **Recently shipped**, and carry forward
> the one question this increment leaves open (whether a project's showcase view can report an
> unresolvable token) rather than dropping it. Then run every gate.

**What to build**: `scripts/check-install.sh` (`ROSTER_PACK`, `PACK_SOURCE`, `PACK_SLOTS`),
`README.md`, `CHANGELOG.md`, `ROADMAP.md`.

**Test first**:
- The RED signal is real and already present: run `./scripts/check-contract.sh` **before** editing
  and confirm check 13 fails naming `styleguide`. GREEN is that check passing.
- `PACK_SOURCE` and `PACK_SLOTS` are **not** gated by any check. Verify them by running
  `./scripts/check-install.sh --verbose` and reading the output, not by assuming.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — all checks pass, including 13 and 16.
- [Automated]: `./scripts/check-install.sh` runs and reports the new unit and the new slot.
- [Automated]: `tests/run.sh` — every suite green.
- [Manual]: confirm the README row describes what the spell does for a reader deciding whether to
  install it, and states the design-system precondition — it is the one spell in the pack that
  refuses on a project that is otherwise fine.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes. Numbering it would invite `/implement-step <plan> N`, which dispatches a code worker to run
a spell.

> **Prompt**: Run `/feature update editor-guides`. Fold **only** the user- or operator-observable
> behavior changes from this work into the existing capability doc — **do not create a new feature
> doc.** The observable behaviors: a styleguide page whose showcase sections reflect current styles
> without a regeneration; the precondition being stated and unmet meaning stop, named by half; a
> build-time-only token layer being refused rather than baked; a styleguide appearing in the derived
> index like any other guide and being reported by the audit in none of its three sections; and the
> set of tokens shown being a person's to curate. Flip the styleguide entry in the doc's **Increments**
> list from planned to shipped and point it at `_work/styleguide/spec.md`. Update the doc's summary
> sentence, which currently says the styleguide "is the capability's next increment". Fill the Test
> Coverage table with the real fixture paths from `tests/styleguide-check/` and `tests/guide-check/`,
> and mark the live-token scenarios **Not covered** on purpose — they describe CMS-side rendering
> this pack cannot reach, exactly like the three the shipped increment already leaves uncovered; say
> so rather than writing a weaker test and claiming the scenario. Leave the architecture and
> registration criteria in the shipped spec; they are point-in-time and must not appear as Rules.
> **Leave the two Known gap entries in the Increments list intact** — neither is closed by this work,
> and the second (a serialized dropdown default written by a startup composer) is evidence recorded
> specifically so it is not re-derived. Add a revision note dated today.
>
> **Validation**: The capability doc describes current behavior with no transition-style ("goes
> from… to…") Rules; no new feature doc was added; the Increments list and the summary agree with
> what shipped.

---

## File Summary

| Action | File |
|--------|------|
| Create | `skills/umbraco-17/spellbook/styleguide/SKILL.md` |
| Create | `skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py` |
| Create | `tests/make-styleguide-fixtures.sh` |
| Create | `tests/styleguide-check/subject` |
| Create | `tests/styleguide-check/tokens-custom-properties/`, `tokens-none/`, `tokens-two-layers/`, `tokens-preprocessor-only/`, `tokens-string-terminator/`, `tokens-escaped-selector/`, `precheck-both/`, `precheck-no-tokens/`, `precheck-greenfield/` |

<!-- Three of those fixtures were not in the plan when it was written. `tokens-string-terminator`
     and `tokens-escaped-selector` came out of Step 2's review, and `tokens-preprocessor-only`
     out of Step 3's — it is also the case Step 4 describes as `tokens-build-time-only`, which
     was never created because that fixture already existed under the earlier name. Corrected
     here rather than in Step 4's prose: the prose is what was planned, this table is what
     someone reconciles against the tree. -->
| Create | `tests/guide-check/inventory-excluded-palette/`, `tests/guide-check/audit-styleguide-silent/` |
| Modify | `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` |
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guide.py` |
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guidelib/inventory.py` |
| Modify | `tests/make-guide-fixtures.sh` |
| Modify | `scripts/check-install.sh` (`ROSTER_PACK`, `PACK_SOURCE`, `PACK_SLOTS`) |
| Modify | `scripts/check-contract.sh` (check 1 extension allow-list, if a new fixture extension needs scanning) |
| Modify | `README.md`, `CHANGELOG.md`, `ROADMAP.md` |
| _(work type: `change-to editor-guides`)_ Update | `_features/editor-guides.md` — fold observable behavior only; **no new file** |
