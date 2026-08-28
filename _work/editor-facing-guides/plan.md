# Plan: Editor-Facing Guides

**Spec**: `_work/editor-facing-guides/spec.md`
**Branch**: `editor-facing-guides`
**Work type**: `new-capability` — copied verbatim from the spec's `**Work type**:` line; this decides
how the final step records behavior
**Feature doc**: `_features/editor-guides.md` — copied from the spec; the final step targets this,
not the increment slug

## Context

The toolkit generates no editor-facing reference today. This increment ships stories 2–4 of
discovery's four — a derived index, one guide page per component, and an audit — as two new units in
the `umbraco-17` pack: a script owning the deterministic half (extraction, the dossier, the
inventory determiner, the audit's arithmetic, the change plan) and a spell owning the
model-dependent half (prose, the diff-and-approve conversation, rendering decisions read from the
project's exemplars, and every CMS write). A third unit — a reference describing the shared guide
scaffolding — is cited by the spell and by the deferred styleguide increment.

The unit of work in this repo is **a shipped unit plus its fixtures**, established by the
`install-verification` increment. Extraction guidance already exists and is verified against real
projects in both on-disk formats: `skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md`
carries the field-by-field mapping, the two asymmetries (kind flag, version declaration), and the
uSync tab/group resolution rule. **This plan implements that guidance; it does not re-derive it.**
Every extraction step should read it first.

---

## Key Decisions

- **Python 3, standard library only.** The two on-disk formats are JSON (`.uda`) and XML
  (`.config`); bash cannot parse XML robustly, and a dependency would break a pack that must run
  anywhere. `scripts/check-preserved.py` is the repo's prior art for a stdlib Python tool, and
  `codebase-audit` is the prior art for a pack shipping executables at all.
- **The script lives inside the spell's own directory**, at
  `skills/umbraco-17/spellbook/guide/scripts/`. ADR 0002 rejected putting *shared* assets in one
  spell's directory because selective install would silently break the other consumer. This asset is
  not shared: `/guide` cannot function without it, and nothing else calls it. The scaffolding
  reference is the genuinely shared piece, so it is a unit of its own.
- **Module layout**: `scripts/guide.py` is the only public surface (CLI dispatch plus report
  rendering); `scripts/guidelib/` holds `dossier.py`, `deploy.py`, `usync.py`, `models.py`,
  `inventory.py`, `audit.py`, `changeplan.py`. Running `python3 …/scripts/guide.py` puts `scripts/`
  on `sys.path`, so no packaging is needed. One module per step keeps each step's diff small; tests
  only ever exercise the CLI, so the split is internal and no test couples to it.
- **Subcommands**: `extract <alias>`, `signature <alias>`, `inventory`, `audit --guides <file>`,
  `plan <alias> --page <file>`. Each accepts its input either from the project on disk or from a
  JSON file (`--dossier`, `--inventory`) the spell supplies.
- **Rung 3 — the running instance's management API — stays with the spell, and the `--dossier`
  seam is why that costs nothing.** The script implements the three file-reading rungs (Deploy
  artifacts, uSync configuration, generated models). A live read needs a base URL and credentials,
  which the spell already reaches through MCP; handing the result back as a dossier JSON means every
  downstream stage — signature, inventory, audit, change plan — is shared rather than duplicated,
  and the ladder stays complete.
- **The script computes; the spell writes.** This settles the spec's open plan-time question. `plan`
  emits a change plan naming machine-owned updates, seeded-once fields left alone, never-touched
  fields, seeds to create, and whether the run is a no-op. Every CMS write happens in the spell,
  after approval, because approval is a conversation.
- **The audit takes the guide set as an input file** (`--guides`), produced by the spell from the
  CMS. That keeps the arithmetic deterministic and fixture-testable while the CMS read stays where
  the connection is. The spec's testing guideline for audit arithmetic — "given a known inventory
  and a known set of guides" — is written for exactly this shape.
- **Verified against a real uSync project on 2026-08-26** — 174 content types, 150 data types, no
  Deploy artifacts. Recorded so no step re-derives it. All 174 extract at exit 0; 125 carry
  `<IsElement>true</IsElement>` and 49 do not, matching the spec's 125-of-174 figure; 1022
  properties of which 623 are inherited and 100 required; zero unresolved editors. Tab references
  are 235 path-form and 164 bare, of which 114 resolve to a group and 50 to a tab — and **zero are
  ambiguous**, so the ambiguous-reference refusal is a guard that never fires on real data.
  ContentTypes filenames are the lowercased alias 174/174; **DataTypes filenames follow a different
  rule entirely** — 0 of 150 match the lowercased alias, because the filename is the alias with
  spaces and punctuation stripped and its *original casing kept* (`"Dropdown - Blank Settings"` →
  `DropdownBlankSettings.config`). Resolve a data type by its `Key`, never by constructing a
  filename. The extraction reference did not say this and now does. A DataType element carries `Info` with
  `Name`, `EditorAlias`, `EditorUIAlias` (capital UI), plus `Config`, and often `Folder` (91/150) —
  it carries no `DatabaseType` and no `SortOrder`. **A DataType's `Alias` attribute is a display name
  with spaces** in 143 of 150 cases.
- **The option-default marker is dropped: `options` is a list of plain strings.** Two projects in two
  formats agree that no dropdown carries a default — Deploy had 11 configs with `items[]` and none
  with `default`; uSync had 26 with `items[]` and none with `default`, and the only two `default`
  keys anywhere sat on `Umbraco.TrueFalse` toggles. A field that can never be true is worse than an
  absent one: it would appear in every guide's property table as noise and invite a reader to trust
  it. A **toggle's** default is a real value with nowhere to live in the dossier today; that is a
  known gap, not this increment's work. If a source for option defaults ever appears, restoring the
  marker is a `dossierVersion` bump.
- **The property table is stored as structured rows, not as markup in a rich-text field.** Decided
  2026-08-27 after reading two reference guide pages from a shipped implementation. Each row is one
  element type with six fields: `alias`, `label`, `required`, `tab`, `group`, and `information` (rich
  text). Rows are flat and carry their tab and group as fields; **the project's template does the
  grouping**, so a property moving between tabs is a field change rather than a row migrating
  between nested containers. Three reasons, in order of weight:
  - **Ownership works per column rather than per field.** `alias`/`label`/`required`/`tab`/`group`
    carry no human writing, so they are machine-owned and update freely. `information` is a person's
    prose from the moment it is seeded, so it is **seeded-once**: written at creation, never touched
    again, reported when the property's shape changed so the note may be stale. No divergence
    detection and no stored hash are needed, because nothing ever wants to overwrite the prose.
  - **The caster gets a summary instead of a diff of markup.** Row identity is the alias, so the
    comparison is a set operation: added, removed, unchanged. A whole-field comparison put rendered
    markup beside structured rows and asked a person to diff them by eye — on a real page type that
    is roughly sixty lines of markup against nineteen rows, which makes approval theatre.
  - **A design change is one template edit, not forty page edits.** This is the spec's own
    "standardize where it does not show" rule applied to the table.
- **Option lists and recommendations live inside the seeded `information` prose, not in structured
  sub-fields.** The reference pages annotate an option list with `(Default)`, and Step 6 verified
  that **no dropdown data type records a default** on either measured project — that annotation came
  from a model reading the project's design-system knowledge, not from the schema. A structured
  option field could never carry it. So options stay in the prose, one fewer field, and the dossier
  is right not to invent a default.
- **A vanished variation axis is reported as a hedge, and the hedge is the whole truth available.**
  A page arranged when the component had an option list, read after that list is gone, is the one
  transition the seeding section exists for — and the first implementation was silent on exactly it,
  because "no variation axis now" was read as "nothing could have changed". Nothing records the shape
  a page was seeded against, only a hash of it, so "the axis was removed" cannot be told from "the
  axis never existed and something else moved". Both are worth a look and neither is worth a write,
  so the plan prints the hedge wherever an arranged page meets no axis and a differing signature. The
  accepted cost is a paragraph a reader sometimes does not need; `plan-ownership`'s golden carries
  that case and its fixture comment says so.
- **Option lists are matched exactly, never case-folded.** An option's text IS the value written to
  the property, so two options differing only in case are two variants. Folding them drops a variant
  from a guide page silently; keeping both puts a near-duplicate in front of a person who can delete
  one. Visible over silent, the same line the rest of the module holds.
- **The purpose sentence is seeded-once, not regenerated.** Decided 2026-08-27: the intro text block
  that displays first on a guide page is written once and thereafter a person's. `REGISTER` shipped it
  as machine-owned with an `owed` proposal — regenerated and offered as a diff on every signature
  change — which is the wrong class for prose somebody edits. Step 14c makes the register agree.
  Consequences, all of them Step 14c's or Step 15's: the field leaves the model-owed count so a
  regeneration needs a model for one field fewer; a page already carrying it is left alone rather than
  offered; and the write moves to page creation, so **Step 15's creation path must write it** — a
  seeded-once field absent from a created page is never offered again, the same trap the seeding
  section already documents for `guideExamples`.
- **The when-to-use section is seeded-once too, so no prose on a guide page is ever regenerated.**
  Decided 2026-08-28, completing the decision above. Step 14c moved the intro and left the
  when-to-use block machine-owned, which put two adjacent prose blocks on one page in two classes:
  a run protected an editor's rewritten intro byte-for-byte while offering model-written words over
  their rewritten when-to-use text. The approval gate still held, but what an approver was saying
  yes to was a replacement for something a person wrote — the exact thing the intro was moved out
  of, and the report gave them no way to tell the two apart, because the per-field reasoning is
  carried in the document and deliberately not printed. **The accepted cost:** after a schema
  change, when-to-use guidance can go stale and nothing offers to refresh it. That is the same
  trade the class makes everywhere else, and it is reported rather than silent.
- **Seeded-then-flag is a deferred enhancement, not this increment's rule.** Storing a hash of the
  seeded prose would let the tool offer a fresh note *as a diff* where nobody has edited one. That
  buys a convenience; the per-column split above already buys the safety property, so it is recorded
  here rather than built.
- **The source signature is a sha256 over the canonical schema-bearing subset of the dossier**
  (alias, kind, tabs, groups, sort order, properties, mandatory flags, option lists), excluding
  `rung` and `dossierVersion`. This is what makes format-blindness assertable without hardcoding a
  hash into a test: the same component read through two adapters must print the same signature.
- **Two new slots, each declared in exactly one file — the scaffolding reference.**
  `.agents/config/stack.md` → `## Schema serialization` holds which adapter runs, with a `**Detect:**`
  recipe (ADR 0014). `.agents/config/conventions.md` → `## Editor guides` holds the guides node's key
  and which document type aliases were used. The spell and the script **defer** to the reference
  rather than re-declaring either slot: check 9 compares the whole `**If empty:**`-to-blank-line
  window, a `**Detect:**` line lands inside it, and a second declarer would have to reproduce both
  word for word. Where a unit needs *locations* rather than the adapter choice, reuse the existing
  `.agents/config/paths.md` → `## Umbraco` slot with its fallback paragraph **copied verbatim** from
  `umbraco-17-planning`.
- **Document type aliases, each a slot with a default** (spec: two types cannot share an alias):
  guide page `editorGuide`, kind container `editorGuideGroup` (carrying a `guideKind` value), index
  page `editorGuideIndex`, stored reference property `guideSource` (alias, kind, source signature,
  rung), optional index blurb `guideBlurb`.
- **What the inventory determiner is actually worth, measured on the demo project 2026-08-26.**
  The raw artifact count is not the guide count, and Step 8 should start from these numbers
  rather than re-derive them. Of 68 document types: 34 carry the element flag, but only **23**
  are offered as content blocks in one of the 7 block-editor palettes; **8** are the settings
  half of a block, and **3** appear in no palette and are used as compositions. Of the 34
  non-element types, **16** carry a template and are page-type candidates while 18 do not. So
  the theoretical guide count is **39**, against a naive 68 or a flag-based 34. The spec
  recorded 125-of-174 flagged versus 52 real blocks on the client project — a 2.4x over-count
  there against 1.5x here, so the ratio varies but the direction holds on a second project.
  **One caveat**: these counts came from inferring palette entry roles by key naming (a key
  containing "settings" versus a content-element key). Step 8 must read the real palette
  schema rather than inherit that heuristic.
- **Live inspection of the demo project, 2026-08-25** — recorded so no step re-derives it. 68
  `document-type__*.uda` artifacts; 34 carry `Permissions.IsElementType`; three `__version` values
  side by side (`17.1.0` ×47, `17.2.0` ×16, `17.2.1` ×5), which confirms the mixed-version case is
  the normal case rather than a hypothetical; 7 data types carry a `blocks[]` palette. Root-level
  `PropertyTypes` exists in the artifact schema but was empty on all 68 — read it anyway and merge it
  as an ungrouped bucket, because the key is real.
- **Build and test commands, inferred because the `stack.md → ## Build` slot is empty**: there is no
  build system. The gates are `./scripts/check-contract.sh` (run by `.githooks/pre-commit`),
  `bash -n <script>`, `python3 -m py_compile <script>`, and `tests/run.sh`.
- **The pack must not be symlinked into `.claude/skills/`.** Contract check 11 is scoped to
  `skills/core` deliberately — this repo is not a CMS project. Do not add links for these units.

### Planning gotchas — observed, not invented (the `conventions.md → ## Planning gotchas` slot is empty)

- **Contract check 1 forbids several names this work would naturally reach for** — including the
  obvious guide-section and guide-TOC element type names, the natural name for a solution directory,
  and two bare English words that appear in a client's domain vocabulary. The aliases chosen above
  were checked against the list and are clear. Before committing any new alias, fixture directory, or
  path, grep it against `CLIENT_PATTERN` in `scripts/check-contract.sh`:
  `grep -inE "$(sed -n 's/^CLIENT_PATTERN[+]*=//p' scripts/check-contract.sh | tr -d "'" | paste -sd'|' -)" <file>`
  — or simply run the gate, which is cheaper. Fixture trees must not reproduce the demo project's
  real solution or project directory names.
- **The client project granted as a read-only working directory must never be named** in any
  committed file, including this plan and every fixture. "The client project" is the only permitted
  reference (AGENTS.md). The demo project may be named directly.
- **Check 1's scan is an extension allow-list with a hole exactly where this increment's fixtures
  land.** It reads `.md .json .sh .py .txt .diff`; Deploy fixtures are `.uda` and uSync fixtures are
  `.config`, so a leaked alias in either would pass silently. Step 2 extends both lists in
  `scripts/check-contract.sh` before the first fixture is committed.
- **Two registries no gate covers.** `ROSTER_PACK` in `scripts/check-install.sh` *is* gated (check
  13) and will fail the build until the two new units are listed — and it fails at the *commit* that
  adds a unit, not at Step 17, because the pre-commit hook runs the gate. So each unit registers
  itself in `ROSTER_PACK` and `PACK_SOURCE` as it lands (`umbraco-17-guide-scaffolding` did so on
  2026-08-28); Step 17 keeps `PACK_SLOTS`, the README, the changelog and the roadmap. `PACK_SLOTS` in the same file is
  **not** gated — a new slot absent from it is surveyed nowhere and reported to no consumer. Both are
  handled in Step 17. Worth recording in the empty slot afterwards.
- **Frontmatter rules that fail the gate**: a spell needs `disable-model-invocation: true`, a
  reference must not have it (check 5); `name:` must equal the directory name and `description:` must
  exceed 40 characters (check 6).
- **An exemplar instruction needs its absence clause within 18 lines** (check 10). The spell's
  "copy the closest existing" steps must carry the greenfield refusal beside them, which the spec
  requires anyway.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Parameterize the test harness

> **Prompt**: Implement Step 1 of `_work/editor-facing-guides/plan.md`. `tests/run.sh` hardcodes one
> subject (`scripts/check-install.sh`) and one cases directory (`tests/install-check`). Generalize it
> to suites: a suite is a directory under `tests/` containing a `subject` file (one line, a
> repo-relative path to an executable) plus one directory per case. Usage becomes
> `tests/run.sh [suite [case ...]]` — no args runs every suite. Create
> `tests/install-check/subject` holding `scripts/check-install.sh`. Add two directives to the
> `expect` grammar: `args:` (a single line of arguments passed to the subject, default none) and
> `same_stdout_as: <case>` (the case's stdout must byte-match that other case's stdout in the same
> suite — needed because the format-blindness claim in Step 4 cannot be expressed as a substring).
> Resolve the subject to an absolute path before `cd`-ing into a case, exactly as the current
> `CHECK="$PWD/…"` line does. Update `tests/README.md` to document suites, `subject`, and the two new
> directives. Confirm `tests/run.sh install-check` runs the 17 existing cases and all still pass.

**What to build**: `tests/run.sh` (suite discovery, `subject` resolution, `args:`,
`same_stdout_as:`), `tests/install-check/subject`, `tests/README.md`.

**Test first**:
- The RED signal already exists: run `tests/run.sh install-check` **now**. Today the argument is
  read as a case name, so it fails with "no expect file" — that is this step's behavior missing.
- GREEN is the same command running all 17 install-check cases and passing.

**Validation**:
- [Automated]: `bash -n tests/run.sh`; `tests/run.sh` (no args) reports 17/17; `tests/run.sh
  install-check` reports the same 17; `tests/run.sh install-check no-config` runs exactly one case.
- [Automated]: `./scripts/check-contract.sh` passes.
- [Manual]: confirm the one-case and one-suite invocations are distinguishable in the output, so a
  mistyped suite name does not silently report success.

---

### Step 2 — The guide-check suite: fixtures and the RED apparatus

> **Prompt**: Implement Step 2 of `_work/editor-facing-guides/plan.md`. First, extend contract check
> 1's scanned-extension allow-list in `scripts/check-contract.sh` — both the `git ls-files` branch
> and the `find` branch — to include `uda` and `config`, since this increment's fixtures use those
> extensions and would otherwise be unscanned for client-identifying content. Then create
> `tests/make-guide-fixtures.sh`, following `tests/make-fixtures.sh`'s conventions (generated not
> hand-built, minimal fake project trees, one `expect` file per case), and
> `tests/guide-check/subject` holding
> `skills/umbraco-17/spellbook/guide/scripts/guide.py`. Generate the first two cases only:
> `deploy-dossier` (a fake project with a Deploy revision directory holding an `alertBanner` element
> type — a Content tab with a required `alertHeading` and an optional `alertDismissible` toggle, a
> Settings tab with an `alertSeverity` dropdown offering Info/Warning/Critical defaulting to Info,
> and a `baseSettings` composition contributing `metaDescription`) and `usync-dossier` (the same
> component serialized as uSync XML, including `usync.config` declaring a recognized `format`).
> Read `skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md` for the exact element and
> attribute shapes of both formats — it is verified against real projects; do not invent field names.
> Both cases invoke `extract alertBanner` via `args:` and assert the same dossier content. Do **not**
> create the script yet. Run `tests/run.sh guide-check` and confirm both cases fail because the
> subject is absent.

**What to build**: `scripts/check-contract.sh` (extension allow-list, both branches),
`tests/make-guide-fixtures.sh`, `tests/guide-check/subject`, `tests/guide-check/deploy-dossier/`,
`tests/guide-check/usync-dossier/`.

**Test first**: this step *is* the test apparatus. RED is both cases failing because the script does
not exist — read one failure and confirm it names a missing subject rather than a malformed fixture.

**Validation**:
- [Automated]: `bash -n tests/make-guide-fixtures.sh`; `tests/make-guide-fixtures.sh` regenerates
  cleanly and is idempotent; `tests/run.sh guide-check` reports 2 cases, both failing;
  `tests/run.sh install-check` still 17/17.
- [Automated]: `./scripts/check-contract.sh` passes, and confirm the new extensions are actually
  scanned — add a temporary forbidden token to a fixture `.uda`, see check 1 fail, remove it.
- [Manual]: no fixture path or alias reproduces a forbidden token from the Key Decisions list.

---

### Step 3 — The dossier and the Deploy adapter (rung 1)

> **Prompt**: Implement Step 3 of `_work/editor-facing-guides/plan.md`. Create
> `skills/umbraco-17/spellbook/guide/scripts/guide.py` (executable, `#!/usr/bin/env python3`, stdlib
> only) with an `extract <alias>` subcommand, plus `guidelib/dossier.py` and `guidelib/deploy.py`.
> The dossier is JSON on stdout: `dossierVersion`, `rung`, `alias`, `name`, `kind`
> (`element`/`document`), `icon`, `description`, `tabs[]` → `groups[]` → `properties[]` (each with
> `alias`, `name`, `description`, `editor`, `mandatory`, `sortOrder`, `options[]` with a `default`
> marker, and `inheritedFrom`), `compositions[]` as aliases, `structureAvailable`, and
> `sourceSignature` — a sha256 over the canonical schema-bearing subset only, excluding `rung` and
> `dossierVersion`. Everything is normalized on the alias. Follow
> `skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md` for the Deploy mapping: groups
> with `"Type": 1` are tabs, `Permissions.IsElementType` is emitted only when true so it must be
> read as a truthiness test, compositions resolve recursively via their UDIs to aliases, and
> `SortOrder` governs both groups and properties. Read root-level `PropertyTypes` as well as
> `PropertyGroups[].PropertyTypes[]`, merging the former as an ungrouped bucket. Accept `--adapter
> deploy` and a project-root argument; hardcode no path. Make the `deploy-dossier` case pass, and
> leave `usync-dossier` failing.

**What to build**: `scripts/guide.py` (CLI dispatch, `extract`), `guidelib/dossier.py` (the format,
canonicalization, signature), `guidelib/deploy.py` (the rung-1 adapter).

**Test first**: `deploy-dossier` is already RED from Step 2. Its assertions come from the fixture's
declared intent — tab order, the required flag, the default-marked option, the inherited property —
not from the implementation's output. Do not add assertions by running the script and copying what
it printed.

**Validation**:
- [Automated]: `python3 -m py_compile` on every new file; `tests/run.sh guide-check` — `deploy-dossier`
  passes, `usync-dossier` still fails; `./scripts/check-contract.sh` passes.
- [Manual]: run `extract` against the demo project's Deploy revision directory (read-only) for two
  real aliases — one element type, one page type — and confirm tabs, groups, and inherited
  properties look like what the backoffice shows. This is the check that catches a mapping error the
  synthetic fixture is too small to expose.

---

### Step 4 — The uSync adapter (rung 2), and format-blindness

> **Prompt**: Implement Step 4 of `_work/editor-facing-guides/plan.md`. Add `guidelib/usync.py` and a
> `signature <alias>` subcommand to `skills/umbraco-17/spellbook/guide/scripts/guide.py` that prints
> the dossier's `sourceSignature` alone. Follow
> `skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md` exactly for uSync: the alias is
> an attribute on the root `<ContentType>` and not an `<Info>` child; `<IsElement>` is always present
> so it is read as a boolean, the opposite of Deploy's truthiness test; a property's `Tab Alias` may
> be a `tab/group` path *or* a bare alias naming either level, so resolve it against the `<Tabs>`
> list and read that entry's `<Type>` rather than inferring from whether it contains a slash;
> captions repeat and are never keys; filenames are the lowercased alias, so a known-alias read must
> case-fold. Make `usync-dossier` pass with the same assertions the Deploy case uses. Then add two
> fixture cases to `tests/make-guide-fixtures.sh`: `signature-deploy` and `signature-usync`, each
> invoking `signature alertBanner --adapter <format>` against the same fixture project holding both
> serializations, with the second carrying `same_stdout_as: signature-deploy`.

**What to build**: `guidelib/usync.py`, the `signature` subcommand, two new fixture cases.

**Test first**: `usync-dossier` is RED from Step 2 — make it green against the *same* assertion set
as `deploy-dossier`, since equivalence is the claim. Then write `signature-deploy` /
`signature-usync` and confirm the pair goes RED before the adapters agree (if it is green
immediately, check that both cases are really reading different serializations).

**Validation**:
- [Automated]: `tests/run.sh guide-check` — all four cases pass. The signature pair is the
  highest-value test in the suite; a failure here means the adapter seam is not real.
- [Automated]: `./scripts/check-contract.sh` passes.
- [Manual]: no uSync project is available as a read-only working directory, so this rung's
  verification rests on the fixture. Say so in the step's report rather than implying a live check.

---

### Step 5 — A read that finds nothing fails loudly

> **Prompt**: Implement Step 5 of `_work/editor-facing-guides/plan.md`. Add the `deploy-missing-alias`
> case to `tests/make-guide-fixtures.sh`: a serialization folder that exists and is readable but
> holds no artifact for the requested alias. `extract alertBanner` must exit non-zero, name the alias
> and the folder it searched, and say the export is partial — never print a dossier with no
> properties. Then implement it in `skills/umbraco-17/spellbook/guide/scripts/guide.py`. Apply the
> same rule to a component whose artifact exists but yields zero properties.

**What to build**: the loud-failure path in the adapters and the CLI's error handling; one fixture
case.

**Test first**: write `deploy-missing-alias` and confirm it fails RED against the current
implementation — most likely by printing an empty dossier and exiting zero, which is precisely the
silent-empty shape this asserts against.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — five cases pass; the new case asserts a non-zero exit
  **and** that the output does not contain an empty property list.
- [Manual]: read the error message as an operator would and confirm it says what to do next
  (re-export, or point at the right folder).

---

### Step 6 — Version refusal, in the two shapes the formats force

> **Prompt**: Implement Step 6 of `_work/editor-facing-guides/plan.md`. The two on-disk formats
> declare their format version differently, so refusal takes two shapes — this is one rule stated
> twice, and implementing either alone encodes the wrong single rule. Add two fixture cases to
> `tests/make-guide-fixtures.sh`: `usync-format-refused` (a `usync.config` whose `format` attribute
> is not one the adapter recognizes → the entire read is refused up front, the found format is
> named, and no component is read) and `deploy-mixed-versions` (three Deploy artifacts whose
> `__version` values differ, one unrecognized → the unrecognized artifact is named as unread and
> every other component is still read). Implement both in `guidelib/usync.py` and
> `guidelib/deploy.py`. Define the accepted version sets in one place with a comment recording that
> the evidence base is narrow — three projects on one CMS major — and that widening it is a known
> open question from the spec. The demo project's real spread is `17.1.0`, `17.2.0`, `17.2.1`, so the
> accepted Deploy set must include all three or the normal case is refused.

**Also folded into this step, from verifying the uSync adapter against a real project on
2026-08-26** (the adapter was fixture-only until then):

> **Drop the option-default marker.** `options` becomes a list of plain strings in the dossier.
> Update `guidelib/dossier.py`'s `options_from_config`, both adapters if they touch it, the
> hand-authored golden files that carry an option list, and the generator. No dropdown in either
> project carries a default, so the marker could only ever be `false`.
>
> **Correct the uSync DataType fixture to the verified shape.** Restore the spaced `Alias` display
> name (143 of 150 real ones contain spaces — a previous review flagged the spaced alias as an
> inconsistency and it was "corrected" to camelCase, which made the fixture *less* faithful);
> rename `EditorUiAlias` to `EditorUIAlias`; drop the invented `DatabaseType` and `SortOrder`
> elements; add `Folder`, which 91 of 150 carry. Then delete the "confirm this shape against a real
> uSync export" caution from the generator — it is now confirmed.
>
> **Amend `skills/umbraco-17/reference/umbraco-17-feature-backfill/SKILL.md`** with the two things
> the sweep found it lacking: the verified DataType element names, and the fact that its
> lowercased-alias filename rule holds for ContentTypes (174/174) but **not** for DataTypes
> (0/150 — the filename keeps the alias's original casing with spaces and punctuation stripped).
> That file is what other increments read.

**What to build**: the uSync up-front gate, the Deploy per-artifact skip-and-report, a single
declared accepted-version set per format; two fixture cases. Plus the three folded-in items above.

**Test first**: write both cases and confirm each goes RED for the right reason — the uSync case by
reading an unrecognized export as though it were understood, the Deploy case by either refusing the
whole read or reading the stale artifact silently.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — every case passes. `deploy-mixed-versions` must assert
  both halves: the skipped artifact named, and the others still reported.
- [Manual]: run `extract` against the demo project and confirm its three-version spread
  (`17.1.0`, `17.2.0`, `17.2.1`) reads cleanly rather than being refused — 68 of 68 at exit 0.
- [Manual]: run `extract` across the real uSync project's 174 content types and confirm all 174
  still read at exit 0 after the fixture and dossier changes, and that its `format="10.7.0"` passes
  the new gate. Both projects are read-only additional working directories; never write to either,
  and never copy an identifier from either into a committed file.

---

### Step 7 — The generated-models rung, and recording the rung

> **Prompt**: Implement Step 7 of `_work/editor-facing-guides/plan.md`. Add `guidelib/models.py`, the
> lowest rung: read committed `*.generated.cs` model classes for aliases, names, and any XML doc
> comments, producing a dossier with `structureAvailable: false`, no tabs or groups (properties
> flattened into a single unnamed bucket), no required flags, and no option lists — with the gap
> stated in the dossier rather than implied by absence. Record `rung` on every dossier from every
> adapter. Add the `models-only-rung` fixture case: a fake project with no serialization folders and
> one generated model file, asserting the flattened shape, the recorded rung, and the stated gap.
> Note that `signature` must still work at this rung, over whatever structure was available.

**What to build**: `guidelib/models.py`, the `rung` and `structureAvailable` fields honored across
all adapters, one fixture case.

**Test first**: write `models-only-rung` and confirm RED — currently no adapter handles a project
with neither serialization format.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — eight cases pass.
- [Manual]: confirm the dossier at this rung reads as *deliberately thin* rather than broken; a
  reader must be able to tell a missing option list from an empty one.

---

### Step 8 — The inventory determiner

> **Prompt**: Implement Step 8 of `_work/editor-facing-guides/plan.md`. Add `guidelib/inventory.py`
> and an `inventory` subcommand (human text by default, `--json` for machine use). A documentable
> unit is **a component an editor can place from a block editor's palette**, read from the project's
> own block-editor data types — Deploy's `Configuration.blocks[]`, uSync's `<Config>` payload — not
> from the element-type flag. Exclude settings models (an element type named as another palette
> entry's settings half) and compositions (element types appearing in no palette). Page types are
> documentable but folders, containers, and abstract bases are not, and no flag separates them: read
> tree reachability, naming convention, and template presence, then **propose** them for human
> confirmation rather than deciding silently. The report states the counts and the rule that produced
> them. Add two fixture cases: `inventory-palette` (element types split across palette content
> blocks, a palette settings model, and compositions used by neither — the inventory names exactly
> the content blocks) and `inventory-page-types-proposed` (a page type with a template, a folder, and
> an abstract base — page types proposed, the other two not).

**What to build**: `guidelib/inventory.py`, the `inventory` subcommand and its report, two fixture
cases.

**Test first**: write `inventory-palette` first and confirm RED. Its assertion is the determiner's
whole value — a determiner that over-counts by two and a half times makes the audit noise rather
than a backlog.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — ten cases pass.
- [Manual]: run `inventory` against the demo project. 34 of its 68 document types carry the
  element-type flag and 7 data types carry a palette; the palette-derived count must be materially
  lower than 34, and the report must state which rule produced it. If the count comes out at 34, the
  determiner is reading the flag rather than the palette.

---

### Step 9 — The audit's arithmetic and report

> **Prompt**: Implement Step 9 of `_work/editor-facing-guides/plan.md`. Add `guidelib/audit.py` and
> an `audit --guides <file>` subcommand. The guides file is JSON the spell produces from the CMS: one
> entry per published guide page, carrying its stored reference (`alias`, `kind`, `signature`,
> `rung`) or explicitly none. The report has three counted sections, each naming items as
> `alias (Display Name)`: features present in code with no guide page (the primary output), guides
> claiming a source that no longer exists, and machine-owned content whose stored signature no longer
> matches. A guide claiming no source appears in **none** of them. Add fixture cases
> `audit-undocumented` (fourteen palette blocks, thirteen guides → the fourteenth named),
> `audit-orphan-and-sourceless` (one guide for a deleted component, one hand-written guide with no
> stored reference → the first named as an orphan, the second in neither list), and
> `audit-signature-mismatch` (a guide whose stored signature differs from the current shape → named
> as stale, not as undocumented).

**What to build**: `guidelib/audit.py`, the `audit` subcommand, the report renderer, three fixture
cases.

**Test first**: write `audit-undocumented` and confirm RED, then the other two. Each asserts on named
items and counts, which come from the fixture's construction rather than from a run of the script.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — thirteen cases pass.
- [Manual]: read a healthy report (every block documented) and confirm it is genuinely short — one
  line per empty section, not a wall.

---

### Step 10 — Rung-relative completeness, and exit-code discipline

> **Prompt**: Implement Step 10 of `_work/editor-facing-guides/plan.md`. Two behaviors on the audit,
> both one-liners whose absence is expensive. First: completeness is judged relative to the rung the
> dossier was read at, and thinness is reported **once as a report-level statement** naming what is
> missing — never as a finding per guide. Second: **the audit always exits zero**, whatever it found;
> a `--strict` flag is the only thing that makes findings non-zero, and nothing else changes with it.
> Add fixture cases `audit-rung-statement` (a project readable only from generated models, with
> guides for every block → one report-level thinness statement, no per-guide incompleteness
> findings) and `audit-strict-exit` (the same findings asserted twice: exit 0 by default, non-zero
> with `--strict`).

**What to build**: the report-level rung statement, the `--strict` flag, two fixture cases.

**Test first**: write `audit-strict-exit` first. The default-zero assertion is the one most easily
implemented backwards, and getting it wrong fails a build in exactly the projects that wired the
audit in early — confirm it goes RED on the exit code before implementing.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — fifteen cases pass. `audit-strict-exit` asserts exit `0`
  in one case and non-zero in its `--strict` twin.
- [Manual]: confirm the rung statement names the *missing structure* (tabs, required flags, option
  lists), not merely the rung's name.

---

### Step 11 — The change plan: signature no-op and ownership classes

> **Prompt**: Implement Step 11 of `_work/editor-facing-guides/plan.md`. Add `guidelib/changeplan.py`
> and a `plan <alias> --page <file>` subcommand. The page file is JSON the spell reads from the CMS:
> the guide page's stored reference and its current field values. The change plan classifies every
> field the tooling can write as exactly one of machine-owned (regenerate, present as a diff, write
> only after approval), seeded-once (written at creation, never touched again, reported when stale),
> or never-touched (page name, address, visibility settings, and everything not named above). It
> emits the proposed new values for machine-owned fields only, and it writes nothing. When the stored
> signature matches the current shape, the plan is a **no-op**: no proposed change, and nothing for
> the spell to send to a model. Add fixture cases `plan-noop` (matching signature → no changes, and
> the output says explicitly that no model call is needed) and `plan-ownership` (a stale signature
> plus a seeded-once field and a never-touched field carrying known values → machine-owned fields
> proposed, the other two byte-identical in the plan's "left alone" list).

**Amended 2026-08-27, after reading two reference guide pages.** The property table is stored as
structured rows rather than markup in one rich-text field (see Key Decisions), so:

> **`guideProperties` is row-oriented.** The comparison is a set operation on the row alias —
> added, removed, unchanged — and the plan reports that summary rather than putting rendered markup
> beside structured rows. Ownership is **per column inside a row**: `alias`, `label`, `required`,
> `tab`, `group` are machine-owned and update freely; `information` is **seeded-once**, written at
> creation and never touched again. A removed row may carry a person's writing, so removal is
> proposed and says so — never silent.
>
> This replaces the whole-field markup comparison rather than adding to it, so the net effort is
> roughly neutral. The scaffolding fields it reads are Step 14's; where they do not exist yet, leave
> a **named seam** and say so in the report rather than inventing them.

**What to build**: `guidelib/changeplan.py`, the `plan` subcommand, two fixture cases.

**Test first**: write `plan-noop` and confirm RED. It is the cheapest guard against the regeneration
loop that costs a model call on every run.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — seventeen cases pass.
- [Manual]: confirm the plan's shape is something a diff-and-approve conversation can render directly
  — field, current value, proposed value — rather than something the spell must re-derive.

---

### Step 12 — The change plan: provenance decides ownership (the adoption path)

> **Prompt**: Implement Step 12 of `_work/editor-facing-guides/plan.md`. Extend
> `guidelib/changeplan.py`: ownership is a property of the page's **provenance**, not of a field's
> declaration. A page carrying no stored reference has **no** machine-owned fields — every field on
> it is human-owned — so `plan` against it is propose-only: the property tables are offered as a
> diff, the person's prose is untouched, and the stored reference is marked as writable only on
> approval. Add the `plan-adoption` fixture case: a hand-written guide page for `alertBanner` with no
> stored reference and prose in a machine-writable field, asserting that the plan proposes the
> property tables, lists the prose as kept, and marks the stored reference as pending approval rather
> than as a write.

**What to build**: the provenance branch in `guidelib/changeplan.py`, one fixture case.

**Test first**: write `plan-adoption` and confirm RED — a first implementation almost certainly
treats a machine-writable field as machine-owned regardless of provenance, which is the failure this
asserts against.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — eighteen cases pass.
- [Manual]: confirm nothing in the plan output could be mistaken by the spell for an approved write.

---

### Step 13 — The change plan: variant seeding derived, not invented

> **Prompt**: Implement Step 13 of `_work/editor-facing-guides/plan.md`. Extend
> `guidelib/changeplan.py` to derive the live-example seed set from the dossier. Where a variation is
> a value of a variant or style property, the option list already carries the set, so seed one
> instance per option. Where variations are combinations of independent toggles, the set is
> combinatorial and not enumerable: seed **one** instance at the default values and state in the plan
> that curating further combinations is a person's job. Every seeded instance is seeded-once — the
> plan reports a changed variant set, and never proposes replacing an arrangement. Add fixture cases
> `seed-variants-enumerable` (a three-value option list → three seeds, one per value) and
> `seed-variants-toggles` (four independent booleans → one seed at defaults, plus the curation
> statement).

**What to build**: the seed derivation in `guidelib/changeplan.py`, two fixture cases.

**Test first**: write `seed-variants-enumerable` and confirm RED, then the toggle case. Assert on the
number and identity of seeds, which the fixture's option list fixes independently.

**Validation**:
- [Automated]: `tests/run.sh guide-check` — twenty cases pass; `./scripts/check-contract.sh` passes.
- [Manual]: confirm that a changed variant set on an already-seeded page is reported and not
  re-seeded — the arrangement-preserving rule the whole ownership model exists for.

---

### Step 14 — The scaffolding reference: document types and the field register

*Split from a single Step 14 on 2026-08-27. The structured property table added an element type and
a full guide-page field set to what this file had to define, and one step defining an element type,
a page type, two container types, the index, two slots, and the audit's report shape would sprawl.
Step 14 is the schema; Step 14b is the report shape and the slots.*

> **Prompt**: Implement Step 14 of `_work/editor-facing-guides/plan.md`. Create
> `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` — a model-invoked reference
> (no `disable-model-invocation`), `name: umbraco-17-guide-scaffolding`, description over 40
> characters. **This step is the schema half**; Step 14b adds the slots, the index and the report
> shape to the same file. Describe, once, what both `/guide` and the deferred styleguide increment
> need:
>
> - The **single guide document type** serving every guide including hand-authored editorial ones,
>   and its full field set: an intro (seeded-once rich text), a behaviour-or-notes section
>   (seeded-once rich text — the reference implementation renders this as *How It Works* on a block
>   and as a tip callout on a page type), the property row list, screenshots (never-touched), and the
>   optional index blurb (never-touched).
> - The **property row element type** and its six fields — `alias`, `label`, `required`, `tab`,
>   `group`, `information` — with **ownership stated per column**: the first five machine-owned, the
>   `information` rich text seeded-once. Rows are flat and the project's template groups them by tab
>   and group. Say why the table is structured rather than markup in a rich-text field, citing the
>   plan's Key Decisions rather than restating the whole argument.
> - The **`guideSource` stored reference** (alias, kind, source signature, rung) and why every
>   machine-populated field including it is **optional**.
> - The **three ownership classes as consequences of provenance**, and that they apply per column
>   inside a row rather than only per field.
>
> Cite `guidelib/changeplan.py`'s field register as the implementation of this, rather than
> duplicating the list — the register is already the one place the field set is written down. Check
> every alias against the forbidden-token list in this plan's Key Decisions before writing it.

**What to build**: `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md`, its schema
half.

**Test first**: no runnable test — this is a reference. The concrete check is the contract gate plus
a read-back: a fresh reader must be able to answer "what document types does a guides section need,
and which column of which field may the tooling write" from this file alone.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes — specifically check 4 (each `**Slot:**` has its
  `**If empty:**` within three lines, with any `**Detect:**` line *after* the fallback), check 5 (no
  `disable-model-invocation` on a reference), check 6 (name matches directory, description long
  enough), and check 1 (no forbidden aliases).
- [Manual]: confirm no rule in this file is also stated in the spell — the spell must cite, not
  restate.

---

### Step 14b — The scaffolding reference: slots, the index, and the report shape

> **Prompt**: Implement Step 14b of `_work/editor-facing-guides/plan.md`, continuing the reference
> Step 14 started at
> `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md`. Add: the **kind containers**
> (`editorGuideGroup` carrying a `guideKind`, found as children of the one guides pointer, never
> matched by name); the **index page type** whose list is derived at render time and which carries no
> machine-owned fields; the editorial levers that live on the guide page rather than on the index;
> and that guides are located by the **stored key** of the guides node, never by route, with
> detection on document type rather than on name. State what the index's per-guide read is scoped
> to — name, URL, and the blurb-or-purpose line, explicitly **not** the property rows or the live
> examples: a derived index built the obvious way resolves every listed guide's whole content model
> to render a teaser, which on forty guides of twenty rows is eight hundred row objects per render of
> a public page. One sentence there is the difference between an index costing one read per guide and
> one costing a guide's entire shape. Declare the two new slots here and nowhere else:
> `.agents/config/stack.md` → `## Schema serialization` (which adapter runs, with a `**Detect:**`
> recipe after the fallback) and `.agents/config/conventions.md` → `## Editor guides` (the guides
> node key and the document type aliases used). Every alias is a slot with a default, not a constant.
> Include a **self-contained section on the audit's report shape** — three counted sections,
> `alias (Display Name)` items, the report-level rung statement, exit zero with `--strict` as the
> only opt-in, and the three fidelity answers — written so a later extraction to core is a move
> rather than a rewrite.

**What to build**: the second half of
`skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md`.

**Test first**: no runnable test. The concrete check is the contract gate plus a read-back: a fresh
reader must be able to answer "where do guides live, how is the index built, and what does the audit
print" from this file alone.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes — check 4 (each `**Slot:**` has its
  `**If empty:**` within three lines, any `**Detect:**` line *after* the fallback), check 9 (one
  slot, one fallback — these two slots are declared here and nowhere else), check 1 (no forbidden
  aliases).
- [Manual]: confirm the audit section states the report shape the script actually prints, checked
  against a real run rather than from memory.

---

### Step 14c — The register: the purpose sentence is seeded, not regenerated

*Added 2026-08-27, after Step 14's review. `REGISTER` classifies the guide page's intro as
machine-owned with an `owed` proposal; the decision above makes it seeded-once. A docs step is the
wrong place for a behaviour change, so it gets its own.*

> **Prompt**: Implement Step 14c of `_work/editor-facing-guides/plan.md`. In
> `skills/umbraco-17/spellbook/guide/scripts/guidelib/changeplan.py`, move `guidePurpose` from
> `MACHINE_OWNED`/`PROPOSAL_OWED` to `SEEDED_ONCE` with no proposal, and update its `why` to say why
> prose an editor writes is not a value to regenerate. Check every consequence rather than only the
> constant: the `owed` count in the model-call arithmetic, `modelCallNeeded`, the model statement's
> wording and its plural, the left-alone list, and the adoption path — on a hand-authored page the
> intro must now be left alone rather than offered. Two hand-authored goldens carry the old shape
> (`tests/guide-check/plan-ownership/expected-plan.txt` and `plan-adoption/expected-plan.txt`);
> update them **by hand from the constants and the documented render order**, never by capturing a
> run. Add a fixture case proving a page missing the field is not silently skipped, or — if the
> honest answer is that a missing seeded-once field is Step 15's to write at creation — say so in the
> report and state where the plan records it, rather than inventing a proposal for it here.

**What to build**: the register change in `guidelib/changeplan.py`, its consequences, two updated
goldens, and at least one new fixture case in `tests/make-guide-fixtures.sh`.

**Test first**: change a fixture's expectation to the intended behaviour and confirm RED before
touching the register — the two goldens will go RED on their own, which is the signal that the
consequences were found rather than guessed. Then implement, then confirm GREEN. Mutation-check the
new fixture: revert the register change and confirm the case fails.

**Validation**:
- [Automated]: `tests/run.sh` — every case passes; `./scripts/check-contract.sh`; a second run of
  `bash tests/make-guide-fixtures.sh` leaves the fixture tree byte-identical.
- [Manual]: print the `--json` document for an already-written page and for a page missing the field,
  and show that the first leaves the intro alone and the second does not claim to propose it.

---

### Step 14d — The register: no prose on a guide page is regenerated

*Added 2026-08-28. Step 14c moved the intro to seeded-once and left the when-to-use block
machine-owned; the user decided both move. The arithmetic is what makes this a step rather than a
one-line edit — with no owed fields left, a sentence the report has always printed becomes wrong.*

> **Prompt**: Implement Step 14d of `_work/editor-facing-guides/plan.md`. In
> `skills/umbraco-17/spellbook/guide/scripts/guidelib/changeplan.py`, move `guideWhenToUse` from
> `MACHINE_OWNED`/`PROPOSAL_OWED` to `SEEDED_ONCE` with no proposal, beside `guidePurpose`, and
> update its `why`. **Then fix the model-call statement, which is the real work.** The owed count
> drops to zero, and `_model_statement(0, 1)` currently renders "A model call is needed. 0
> machine-owned fields need prose this script cannot write, and 1 carries content…" — a sentence
> that reads as a bug in the tool. Decide between a no-prose-owed form of the statement and
> removing prose from the arithmetic, implement one, and **write down which and why** beside the
> constant. The recommendation, not binding: keep the count and add a form saying a model is needed
> and not for prose — every prose field on the page is seeded once and left alone, and what remains
> is the property table's markup, which comes from the project's own components. Check that
> `STATEMENT_NO_MODEL_NEEDED`'s "unreachable" comment is still true and still describes the register
> it now guards. Verify `PROPOSAL_OWED` is still referenced by something after the move — if nothing
> uses it, say so in the report rather than deleting a constant the spell may read.

**What to build**: the register change and the statement's new form in `guidelib/changeplan.py`,
every golden the wording touches, and a fixture case landing on the new form.

**Test first**: add the fixture case asserting the new sentence and confirm RED before touching the
register — the wording does not exist yet, so it must fail for the right reason. The goldens carrying
the old sentence will go RED on their own once the register moves, which is the signal the
consequences were found rather than guessed. Author every golden by hand from the constants and the
documented render order, never by capturing a run.

**Validation**:
- [Automated]: `tests/run.sh` — every case passes; `./scripts/check-contract.sh`; a second run of
  `bash tests/make-guide-fixtures.sh` leaves the fixture tree byte-identical.
- [Manual]: print the human report and the `--json` document for a page whose signature differs, and
  show that no prose field is proposed, that both prose fields are accounted for, and that the
  model-call sentence is true as printed.
- Mutation-check: revert the register entry and confirm the new fixture fails; separately, revert
  the statement's new form and confirm a case fails rather than the suite passing on wording nobody
  asserts.

---

### Step 15 — The `/guide` spell: the generate path

> **Prompt**: Implement Step 15 of `_work/editor-facing-guides/plan.md`. Create
> `skills/umbraco-17/spellbook/guide/SKILL.md` — a spell, so `disable-model-invocation: true`,
> `name: guide`, `argument-hint` for a component alias, `allowed-tools` in the style of
> `skills/umbraco-17/spellbook/block/SKILL.md`. It takes a component alias — a block or a page type,
> read the same way — and walks: resolve the adapter and locations from the slots (**defer to
> `umbraco-17-guide-scaffolding` for the two new slots rather than re-declaring them**; where the
> `.agents/config/paths.md` → `## Umbraco` slot is needed, copy its fallback paragraph **verbatim**
> from `umbraco-17-planning`, since check 9 compares the wording); run the script's `extract`, or
> supply a dossier read live through MCP via `--dossier` when no on-disk format is present; run
> `plan` against the existing guide page if one exists; present machine-owned changes as a diff and
> write **nothing** until a person approves; generate only the model-dependent content — the purpose
> sentence, when-to-use, and warnings — and leave property tables to the script's deterministic
> transform. Live examples are instances of the block placed in the page's content area and rendered
> by the site; the tooling never generates or writes media, and screenshots are uploaded by a human.
> Where markup is needed, take the shape from the project's existing components by reading them —
> and put the greenfield refusal next to that instruction, within a few lines, since check 10
> requires it and the spec requires the behavior. Never create a public URL without confirmation.
> End with a report block and a `Next:` line, per the house style; spells suggest and never invoke
> each other.

**One contract the change plan imposes on this spell, recorded 2026-08-27 from a review.** A
change plan's `rule` object carries **different keys on its two paths** and they share none:
a regeneration carries `machineOwned`/`seededOnce`/`neverTouched`, an adoption carries
`humanOwned`/`offered`/`kept`. **Branch on `comparison == "noReference"` (or `provenance`) before
touching `rule`, or a hand-written page raises a KeyError.** The asymmetry is deliberate — the
three class rules describe a page that carries a reference, and quoting them at a page that
carries none would state a rule that does not apply to it — and the spell has to render two
different shapes anyway, so the branch is not extra work. Two further keys the adoption path
carries and the regeneration path does not: `proposeOnly` and, on the offered reference,
`consequence`, which says in words that writing that reference is what makes the page's fields
machine-owned from then on. Show it; it is the one approval that is not reversible by editing.

**What to build**: `skills/umbraco-17/spellbook/guide/SKILL.md`, the generate path.

**Test first**: the runnable subject is the script, already covered. The concrete manual check for
this step is a dry read-through against the demo project: resolve the adapter, extract one real
alias, produce a change plan, and confirm the spell's steps are followable without inventing
anything the project does not supply. Do not write to the demo project.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes — check 5 (posture), check 6 (frontmatter), check
  9 (any re-declared slot's fallback matches word for word), check 10 (exemplar instruction has its
  absence clause within 18 lines).
- [Manual]: walk the generate path against the demo project up to but not including the write, and
  confirm every step has a real input.

---

### Step 16 — The `/guide` spell: audit mode, and degradation

> **Prompt**: Implement Step 16 of `_work/editor-facing-guides/plan.md`. Add to
> `skills/umbraco-17/spellbook/guide/SKILL.md`: `--audit` as a **mode on this spell**, not a separate
> spell. It reads the guide set from the CMS, hands it to the script's `audit --guides`, and reports
> what came back — reporting the inventory and the rule that produced it **before** acting on it, so
> a wrong determiner is visible immediately rather than after a hundred guides have been proposed.
> State that the audit warns and never blocks, that it exits zero whatever it found, and that
> `--strict` is the only path to a non-zero exit — with a sentence on why, so nobody "fixes" it. Add
> the degradation order: full generation where a model service and a CMS connection are both
> available; rendering to files where the CMS cannot be written; property tables plus marked gaps
> where no model is available at all, since property tables are a deterministic transform. Add the
> voice-and-tone ladder — project references where discoverable or pointed at, the platform's own AI
> contexts where provided, otherwise a generic descriptor shipped with the spell. Follow the
> artifact-disposition convention for any report or file output: ask whether it is durable or
> temporal, per the `workflow` skill.

**What to build**: the audit mode, the degradation order, the voice-and-tone ladder, artifact
disposition.

**Test first**: no new runnable behavior — the audit's own behavior is covered by Steps 9 and 10. The
check is that the spell's stated exit behavior matches the script's actual behavior; run
`audit --guides` on a fixture and confirm the exit code the spell claims is the one observed.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes; `tests/run.sh` stays green.
- [Manual]: run the audit mode against the demo project read-only, with an empty guide set, and
  confirm the report reads as a backlog rather than as an error — and that it exits zero.

---

### Step 17 — Register the units, and document them

> **Prompt**: Implement Step 17 of `_work/editor-facing-guides/plan.md`. Register the two new units
> so nothing reports a clean install while they are absent. In `scripts/check-install.sh`: add
> `guide` and `umbraco-17-guide-scaffolding` to `ROSTER_PACK` (contract check 13 fails until this is
> done), and add `PACK_SLOTS` entries for the two new slots —
> `stack.md|Schema serialization|umbraco-17-guide-scaffolding` and
> `conventions.md|Editor guides|umbraco-17-guide-scaffolding` — which **no gate covers**, so a
> missing entry means the slot is surveyed for nobody. Add two rows to the pack table in `README.md`
> matching the existing style. Add a `CHANGELOG.md` entry. Update `ROADMAP.md`: the guides item moves
> out of Next, recording that the adapter it claimed was built here, and the three still-open
> questions the spec carries (the accepted format-version set, the audit's output contract now that
> the inventory determiner shares its report, and how voice-and-tone guidance is discovered) go where
> a reader will find them. Do **not** symlink either unit into `.claude/skills/` — check 11 is scoped
> to `skills/core` on purpose. Re-run every gate.

**What to build**: `scripts/check-install.sh` (roster + slots), `README.md`, `CHANGELOG.md`,
`ROADMAP.md`.

**Test first**: the gate is the test. Run `./scripts/check-contract.sh` before editing and confirm
check 13 fails naming both new units — that is the RED signal, and it is the same drift the check was
written to catch.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes; `tests/run.sh` — 17 install-check plus 20
  guide-check cases; `scripts/check-install.sh` run in this repo exits zero.
- [Manual]: confirm the README rows say what a consumer needs to decide *before* installing, and that
  the pack's spell count in any prose that states one is still accurate.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes.

> **Prompt**: Run `/feature update editor-guides` to verify the living behavioral doc reflects the
> actual implementation. Review each scenario against the code and test results. Update any scenario
> where the implementation diverged from the draft. Fill in the test coverage table with real fixture
> paths under `tests/guide-check/`, or mark as target-pending the scenarios that are project-side
> rather than script-side — the derived index, grouping by kind in the tree, and conforming markup
> are verified on a real project, not by this repo's harness, and saying so is more useful than a
> blank. Remove the "Draft" banner. Commit the verified doc.
>
> **Validation**: Every scenario matches observable behavior; the coverage table has no unexpected
> "Not covered" gaps, and every remaining gap is explained rather than left blank.

---

## File Summary

| Action | File |
|--------|------|
| Modify | `tests/run.sh` (suites, `subject`, `args:`, `same_stdout_as:`) |
| Create | `tests/install-check/subject` |
| Modify | `tests/README.md` |
| Create | `tests/make-guide-fixtures.sh` |
| Create | `tests/guide-check/subject` |
| Create | `tests/guide-check/<case>/` × 20 (generated) |
| Modify | `scripts/check-contract.sh` (scan `.uda` and `.config` fixtures) |
| Create | `skills/umbraco-17/spellbook/guide/SKILL.md` |
| Create | `skills/umbraco-17/spellbook/guide/scripts/guide.py` |
| Create | `skills/umbraco-17/spellbook/guide/scripts/guidelib/{__init__,dossier,deploy,usync,models,inventory,audit,changeplan}.py` |
| Create | `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` |
| Modify | `scripts/check-install.sh` (`ROSTER_PACK`, `PACK_SLOTS`) |
| Modify | `README.md` (two pack rows) |
| Modify | `CHANGELOG.md` |
| Modify | `ROADMAP.md` |
| _(work type: `new-capability`)_ Update | `_features/editor-guides.md` (verify scenarios, fill coverage, drop the Draft banner) |
