# Plan: Umbraco Block Authoring Reference

**Spec**: `_work/shipped/umbraco-block-authoring-reference/spec.md`
**Branch**: `robot-denny/umbraco-block-authoring-reference`
**Work type**: new-capability
**Feature doc**: `_features/block-authoring.md`

## Context

`/block` holds discipline that a planned block never receives: the test shape that proves a block
exists, the rule to copy the closest existing block and never quietly invent a first one, palette
choice as the project's decision, the rule never to hand-edit `.uda` files, and the definition of
done. A spell is invisible to the model, and `/implement-step` refuses a step that casts one, so the
spec → plan → implement flow on an Umbraco project gets none of it. This increment splits that
discipline into a model-invoked reference, `umbraco-17-block-authoring`, routes block work to it from
`umbraco-17-planning`, and thins `/block` to a standalone cast that follows it. The spell stays,
because `/styleguide` hands view authoring to it and a block too small for a spec needs a home.

The unit of work is a pack unit split, and the plan follows its natural slice: the reference, the
router that reaches it, the caller that defers to it, and the registrations a pack unit owes. Two
premises were verified before the spec was written and shape this plan. A reference loads inside the
worker `/implement-step` dispatches, so the split works by mechanism. And every platform fact the
roadmap listed as missing is already in `umbraco-17-starter-facts`, so the reference carries
discipline and cites facts, and restates none.

The user asked for the roadmap update to be part of this plan. It is Step 4.

---

## Key Decisions

- **Unit of work**: the `## Unit of work` slot is empty in this repo. Inferred from the pack's own
  precedent: `umbraco-17-guide-scaffolding` is a reference that two spells cite rather than restate,
  and the guides increment planned it as reference, router, callers, registrations. This plan follows
  the same slice.
- **The reference declares no slot.** The spec left this open. Decided: no `**Slot:**` marker in the
  reference. `/plan` already reads `paths.md → ## Umbraco` through `umbraco-17-planning` and records
  the view location in Key Decisions, which the worker prompt carries verbatim. The standalone spell
  keeps its own slot declarations. So the reference says where a view location is *found* (the
  plan's Key Decisions, or the project's paths slot, or the greenfield sequence when neither has it)
  without declaring a slot of its own. That means no `PACK_SLOTS` registration and no exposure to
  contract check 9's identical-fallback rule. Revisit if a later caller needs the reference to read a
  slot directly.
- **The test sample moves to the reference.** The TypeScript sample against the Playwright test
  helpers is the one piece of the test shape a worker most needs, and it is stack-specific, which is
  fine inside a pack. The reference carries it; `/block` Step 2 cites the reference instead. The
  three facts under it (`getByName()` returns `false`, properties are a flat array, `isElement: true`)
  are cited to `umbraco-17-starter-facts` by unit name, not restated.
- **Routing lives in a section of its own in `umbraco-17-planning`**, not a row in the companion
  table. That table routes to external plugins and is hedged for their absence; a row for this pack's
  own unit would inherit a hedge it does not need and sit among things it is not. The new section
  goes immediately before "Route backoffice extension work to its authoritative skill", and the
  layer table's **Slice** row gains a pointer. No "where installed" hedge: the guide and styleguide
  spells cite `umbraco-17-guide-scaffolding` plainly, and same-pack citation is the precedent.
- **Block steps are never written as "cast `/block`".** The planning reference says so explicitly,
  because `/implement-step` refuses spell-cast steps and hands them back. Block work is planned as
  ordinary steps, each naming the reference in its prompt, the way the worker envelope already names
  `tdd-principles`.
- **Step numbering in `/block` is preserved.** `/styleguide` Step 9 and its `Next:` line point at
  `/block` "Step 5" by number and meaning (author the view; element types and palette already
  exist). Thinning replaces discipline with citations inside steps; it does not renumber, merge, or
  remove a step.
- **Single-holder phrases, used as the RED→GREEN signal in Steps 1 and 3 and again in Step 5.** There
  is no harness for prose, so the plan defines seven phrases that each identify one sentence of
  discipline. Before Step 3, each appears in the spell; after Step 3, each appears in exactly one
  shipped file. The grep, run from the repo root, is:

  ```
  grep -rniE 'toBeNull|flat (properties )?array|closest existing block|first block in a project defines|project decision, not a technical one|hand-edit(ing)? `?\.uda|done when the test' skills/umbraco-17 --include=SKILL.md --include='*.md' -l
  ```

  The starter-facts files may legitimately match `toBeNull` and `flat array`, because they hold the
  facts. The rule is about discipline: the sentence stating the *rule* lives once, and the fact it
  rests on is cited.
- **Frontmatter description uses em dashes, never a colon followed by a space.** An unquoted YAML
  scalar with `: ` opens a nested mapping, the installer's parser throws, and the unit is silently
  dropped from the install. Commit 742fa2d fixed exactly this in `prose-discipline` and contract
  check 6b now gates it, but the rule belongs here so the author does not meet it as a failure.
- **Build and test commands** (the `## Build` slot is empty; inferred from the repo root):
  `bash scripts/check-contract.sh` is the gate and currently reports 22 checks passed;
  `bash tests/run.sh` is the suite and currently reports 110 of 110 cases across three suites.
- **A new pack unit is registered in five places, and check 13 and check 18 gate two of them.**
  `ROSTER_PACK` and `PACK_SOURCE` in `scripts/check-install.sh`, the `umbraco-17` pack table in
  `README.md`, a card in `docs/spell-cards.md` with its count line, and a `CHANGELOG.md` entry. The
  install checker's `pack-installed` fixture does not need a new case, because the new unit reads no
  slot and its presence is verified by the roster like any other. This is a planning gotcha worth
  recording in `AGENTS.md`'s authoring conventions if it is not already there in this form.
- **The roadmap entry moves rather than being corrected in place.** Its "not in any reference" claim
  is wrong for every fact it names, but the entry leaves the Next section when this ships. The
  Recently shipped entry states the corrected premise in one sentence.
- **Hand verification is recorded, not attested.** Step 5 writes a validation log under the
  increment's `assets/`, predictions first, following the convention in `AGENTS.md` and the shape of
  `_work/shipped/owasp-security-review-rules/assets/step5-validation-log.md`.
- **The demo project cast is conditional.** The demo project at the sibling path has an older
  install of the pack with no `/block` and no `umbraco-17-block-authoring`. AC7 and AC8 are checked
  by a structural walk of the thinned spell and the styleguide handoff in Step 5, and by a live cast
  only if the pack is reinstalled there from this branch first. The log records which happened.
- **Core is untouched.** `git diff --stat main -- skills/core` must be empty at every validation.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Create the reference and register it

> **Prompt**: Implement Step 1 of `_work/shipped/umbraco-block-authoring-reference/plan.md`. Create
> `skills/umbraco-17/reference/umbraco-17-block-authoring/SKILL.md`, a model-invoked reference that
> holds the block discipline `skills/umbraco-17/spellbook/block/SKILL.md` currently carries, written
> so that every platform fact is cited to `umbraco-17-starter-facts` by unit name and none is
> restated. Model its shape on `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md`.
> Then register the unit: add `umbraco-17-block-authoring` to `ROSTER_PACK` and
> `"umbraco-17-block-authoring|umbraco-17"` to `PACK_SOURCE` in `scripts/check-install.sh`, and add a
> row to the `umbraco-17` pack table in `README.md`. Run `bash scripts/check-contract.sh` after
> creating the file and before registering, expect checks 13 and 18 to fail naming the unit, then
> register and expect 22 checks passed. Run `bash tests/run.sh` and expect 110 of 110. Do not edit
> the spell in this step.

**What to build**:

- `skills/umbraco-17/reference/umbraco-17-block-authoring/SKILL.md` with frontmatter `name:
  umbraco-17-block-authoring` and a description over 40 characters, em dashes and no `: ` inside it,
  that triggers on planning, implementing, or reviewing work that adds a block or element type to an
  Umbraco 17 project, and names what the reference holds: the test that proves a block exists, the
  copy-the-closest-block rule and what to do when there is none, palette choice, schema files, and
  the definition of done. No `disable-model-invocation` line (check 5 fails a reference that sets it).
- Sections, in this order, each stating the rule once and citing facts rather than restating them:
  1. **What this reference is, and what it is not.** Discipline for one block, whether planned or
     cast. The platform facts it rests on live in `umbraco-17-starter-facts` (the Management API and
     content-model topic files); this file cites them. Procedure lives in the plan or in `/block`.
  2. **A block is proved to exist before it is built.** The test shape: assert the element type is
     present and is an element, and that each expected property alias is on it. Carry the TypeScript
     sample from `/block` Step 2 verbatim. Under it, one sentence per fact pointing at the
     starter-facts unit: presence is asserted with truthiness because of what `getByName()` returns
     on a miss, properties are read as a flat array, `isElement: true` is what makes it a block. Run
     to RED before creating anything; a test that passes first is testing nothing.
  3. **A new block copies the closest existing block.** What to carry over verbatim in shape: the
     model or inherits directive, settings handling, the styling convention, the filename
     convention. The existing blocks are the specification. Two common valid shapes named without a
     verdict (flat editor-agnostic folder bound to `IBlockReference<IPublishedElement,
     IPublishedElement>`; per-block folder in a class library bound to the generated model). Where
     the location is found: the plan's Key Decisions, else the project's paths slot, else the next
     section. **Within 18 lines of the phrase "closest existing block", the greenfield sequence**
     (contract check 10 requires the absence clause in that window): when the project has no blocks,
     ask whether another codebase is the reference; otherwise establish the convention explicitly
     and minimally and say so; record it in Key Decisions and propose it for the paths slot so the
     second block copies. "The first block in a project defines its conventions whether or not
     anyone decided to."
  4. **Which palette a block joins is the project's decision.** Identify candidates by the data
     types whose configuration has a top-level `blocks[]`; pick by where the block is meant to
     appear; confirm before adding to only one palette in a project that keeps parity. Compare only
     palettes that already share a block. Point at the starter fact on palette membership, and at
     the Deploy drift check where installed, for the current state.
  5. **Schema files are never hand-edited.** `.uda` under Deploy and uSync `.config` are authored
     through the backoffice or Management API. Point at the starter fact on generated models.
  6. **A block is done when its test passes.** Not when it compiles. Diagnose and fix rather than
     adjust the test to what was built.
  7. **Alias hygiene is a set of facts, not a rule of this file.** One paragraph pointing at the
     starter facts for the reserved `level` alias, unprefixed generic collisions, and the dropdown
     editor alias, with the one rule that is discipline: prefix aliases with the element name.
  8. **How a plan uses this.** The step that writes the test, creates the element type, registers
     the palette entry, or authors the view names this reference in its prompt. A block is planned
     as ordinary steps, never as a step that casts `/block`. The worker records the exemplar it
     copied and the palette it chose in its report.
- `scripts/check-install.sh`: `umbraco-17-block-authoring` appended to the `ROSTER_PACK` array on
  the line with the other `umbraco-17` references, and `"umbraco-17-block-authoring|umbraco-17"`
  added to `PACK_SOURCE` after the `umbraco-17-guide-scaffolding` entry.
- `README.md`: a row in the `umbraco-17` pack table after `umbraco-17-guide-scaffolding`, linking
  `skills/umbraco-17/reference/umbraco-17-block-authoring/SKILL.md`, kind `reference`, one sentence.

**Test first**:
- Run `bash scripts/check-contract.sh` before touching anything; confirm 22 checks passed.
- Create the `SKILL.md`, run the gate again, and confirm RED: check 13 reports the unit missing from
  `ROSTER_PACK`, and check 18 reports it unlinked from the README. If neither fails, the gate is not
  covering what this plan believes it covers, and that is the more important finding; stop and say so.
- Register, run again, confirm GREEN.

**Validation**:
- [Automated]: `bash scripts/check-contract.sh` → `22 checks passed`.
- [Automated]: `bash tests/run.sh` → `110/110 cases passed`.
- [Automated]: the single-holder grep from Key Decisions lists the new reference and the spell both;
  that is expected at this point, since the spell is thinned in Step 3.
- [Automated]: `git diff --stat main -- skills/core` prints nothing.
- [Manual]: read the reference once as a worker would, with no other file open. Every sentence
  either states a rule of block discipline or points at where a fact lives. Nothing in it names a
  client, a hostname, or an absolute path.

---

### Step 2 — Route block work from the planning reference

> **Prompt**: Implement Step 2 of `_work/shipped/umbraco-block-authoring-reference/plan.md`. Edit
> `skills/umbraco-17/reference/umbraco-17-planning/SKILL.md` so that a plan for Umbraco work that adds
> a block or element type consults `umbraco-17-block-authoring` before the plan is written and names
> it in the prompt of every step that writes the block's test, creates its element type, registers
> its palette entry, or authors its view. Add a section titled "Route block work to this pack's
> block-authoring reference" immediately before "Route backoffice extension work to its authoritative
> skill", add a pointer in the layer table's Slice row, and add one sentence to "Step order that
> usually works" saying block steps name the reference and are never written as a step that casts
> `/block`. Confirm RED first with `grep -c 'umbraco-17-block-authoring'` on the planning file
> returning 0. Run `bash scripts/check-contract.sh` and expect 22 checks passed.

**What to build**:

- New section in `umbraco-17-planning/SKILL.md`, before the extension-routing section:
  - When the work adds a block or element type, consult `umbraco-17-block-authoring` before writing
    the plan. It holds the test shape, the exemplar rule with its greenfield sequence, palette
    choice, the schema-file rule, and the definition of done.
  - Record in Key Decisions that it was consulted, and record what it needs the worker to know: the
    view location and model binding found through the paths slot or by search, the closest existing
    block by name, and the candidate palettes.
  - Every step that writes the test, creates the element type, registers the palette entry, or
    authors the view names `umbraco-17-block-authoring` in its prompt, so the worker loads it. This
    is the same mechanism the worker envelope uses for `tdd-principles`.
  - Block work is planned as ordinary steps. A step that reads "cast `/block`" is refused by
    `/implement-step` and handed back; do not write one. `/block` is for a block cast without a plan.
- Layer table, **Slice** row: after "the first slice sets the convention", add that for a block the
  exemplar rule and the greenfield sequence are stated in `umbraco-17-block-authoring`.
- "Step order that usually works": one sentence after the numbered list, before the backoffice
  extension note, saying steps 1, 2, and 5 name the block-authoring reference when the slice is a
  block.
- Do not add a row to the companion routing table, and do not add a `**Companion:**` declaration:
  the reference is a unit of this pack, not an external plugin.

**Test first**:
- `grep -c 'umbraco-17-block-authoring' skills/umbraco-17/reference/umbraco-17-planning/SKILL.md`
  → `0` (RED).
- After the edit, the same grep → at least `3` (GREEN: the section, the Slice row, the step-order
  sentence).

**Validation**:
- [Automated]: `bash scripts/check-contract.sh` → `22 checks passed`.
- [Automated]: `git diff --stat main -- skills/core` prints nothing.
- [Manual]: read `/plan` Step 2, "Stack-specific planning guidance", then the new section. It answers
  the three things `/plan` looks for: live state (unchanged, above it), sub-type routing (the new
  section), and step order (the new sentence). A planner following `/plan` finds it without being
  told it exists.

---

### Step 3 — Thin `/block` to a cast that follows the reference

> **Prompt**: Implement Step 3 of `_work/shipped/umbraco-block-authoring-reference/plan.md`. Edit
> `skills/umbraco-17/spellbook/block/SKILL.md` so that every sentence of block discipline it carries is
> replaced by a citation of `umbraco-17-block-authoring`, while its eight steps, their numbering, its
> slot declarations, its argument hint, its report block, and its `Next:` line are kept. Before
> editing, run the single-holder grep from the plan's Key Decisions and confirm the spell is listed
> (RED). After editing, the spell must not be listed for any phrase, and the reference must be
> (GREEN). Keep an absence clause within 18 lines of any "closest existing" phrase that remains,
> because contract check 10 requires it. Run `bash scripts/check-contract.sh` and expect 22 checks
> passed.

**What to build**:

- Frontmatter: keep `name`, `disable-model-invocation: true`, `argument-hint`, `allowed-tools`.
  Description may shorten; it still says test-first, element type, palette, view, and green.
- Opening paragraph: after the workflow-layout sentence, one sentence saying this spell follows
  `umbraco-17-block-authoring` for one block, and that a block built from a plan gets the same
  discipline through its steps.
- **Step 1**: keep the derivation and the editor table. Replace the three alias-hygiene bullets with
  one sentence citing the reference's alias-hygiene paragraph, which cites the starter facts.
- **Step 2**: keep the test slot declaration and its `If empty:` text verbatim, and the Key
  Decisions paragraph. Replace the three-fact list and the TypeScript sample with a citation: write
  the test the reference's "proved to exist" section shows, run it, confirm RED. Keep the build slot
  and its fallback verbatim.
- **Step 3**: unchanged.
- **Step 4**: keep the first two sentences (a block offered nowhere renders nowhere; find the data
  type). Replace the project-decision paragraph and the reading-palettes paragraph with a citation of
  the reference's palette section. Keep the `/check-uda` "where installed" mention, since it is a
  cross-pack reference.
- **Step 5**: keep the heading text exactly ("Author the view by copying the closest existing
  block"), because `/styleguide` names this step. Keep the paths slot declaration and its `If empty:`
  text verbatim. Replace the two-shapes list, the greenfield numbered list, the "follow it exactly"
  paragraph, the carry-over list, and the rich-text gotcha with: one sentence citing the reference's
  exemplar section for what to carry over, and one sentence, within 18 lines of the heading, saying
  that if the project has no blocks yet the reference's greenfield sequence applies and this spell
  stops to ask rather than picking a shape. Keep "Do not assume where views live" and the two
  sentences after it.
- **Step 6**: unchanged, including the planning-gotchas slot and fallback.
- **Step 7**: keep the RED→GREEN check; the "do not adjust the test" sentence becomes a citation of
  the reference's definition of done.
- **Step 8**: unchanged. The `Next:` line is unchanged.
- **Conventions**: reduce to items that are procedure of this spell, or remove the section if nothing
  procedural remains. The `.uda` rule, the exemplar rule, and the definition of done are the
  reference's.

**Test first**:
- Run the single-holder grep. The spell's path appears (RED).
- After editing, run it again. The spell's path does not appear; the reference's does (GREEN). Also
  run `grep -n 'closest existing' skills/umbraco-17/spellbook/block/SKILL.md` and confirm that for
  every hit the absence sentence is within 18 lines, or the gate's check 10 will say so.

**Validation**:
- [Automated]: `bash scripts/check-contract.sh` → `22 checks passed`.
- [Automated]: `bash tests/run.sh` → `110/110 cases passed`.
- [Automated]: `grep -c '^## Step' skills/umbraco-17/spellbook/block/SKILL.md` → `8`, and
  `grep -n '^## Step 5' ...` shows the unchanged heading text.
- [Automated]: `git diff --stat main -- skills/umbraco-17/spellbook/styleguide` prints nothing.
- [Automated]: `git diff --stat main -- skills/core` prints nothing.
- [Manual]: read the thinned spell top to bottom as a person casting it with a one-line description.
  Each step still says what to do; where it says why, it names the reference. Then read `/styleguide`
  Step 9 and its `Next:` line and confirm they still describe what `/block` Step 5 does.

---

### Step 4 — Card, changelog, and the roadmap

> **Prompt**: Implement Step 4 of `_work/shipped/umbraco-block-authoring-reference/plan.md`. Add a card for
> `umbraco-17-block-authoring` to `docs/spell-cards.md` after the `umbraco-17-guide-scaffolding` card,
> in the deck's card format, and update the deck's count line under "When to regenerate the deck" to
> 16 spells and 19 references, 35 in all. Add an entry under `## [Unreleased]` → `### Added` in
> `CHANGELOG.md` describing what changes in a consuming project on update. In `ROADMAP.md`, remove the
> entry beginning "**`/block` holds discipline that `/plan` and `/implement-step` cannot see.**" from
> the Next section, and add a dated entry at the top of `## Recently shipped` in that section's
> format, stating the corrected premise in one sentence. Confirm RED first by counting `SKILL.md`
> files under `skills/` against `###` headings in the deck. Run `bash scripts/check-contract.sh` and
> expect 22 checks passed.

**What to build**:

- `docs/spell-cards.md`: a `### umbraco-17-block-authoring` card with Type Reference, Group
  umbraco-17, Triggers (planning or implementing a step that adds a block, or casting `/block`),
  Holds (the test shape, the exemplar rule and greenfield sequence, palette as the project's
  decision, the schema-file rule, the definition of done), Does (one sentence), Watch for (it cites
  facts to the starter facts; it holds no procedure), Pairs with (`/block`, `umbraco-17-planning`).
  Update the count line: 19 references, 35 in all. Update the `/block` card's Pairs-with line to name
  the reference.
- `CHANGELOG.md`, Unreleased → Added: a bold lead saying a block planned through the normal flow now
  gets the discipline `/block` carried, because the discipline moved to a reference the plan routes to
  and a worker loads. Sub-bullets: `/block` still works alone and follows the same reference; nothing
  to configure; the reference cites the starter facts rather than restating them.
- `ROADMAP.md`: remove the Next-section entry (from its bold lead through the line ending "names
  `tdd-principles`.", and the blank line before it). Add at the top of Recently shipped, dated the
  day it ships:
  `- **YYYY-MM-DD** — **Block discipline reachable from the plan.** A model-invoked
  `umbraco-17-block-authoring` reference holds what `/block` alone carried, `umbraco-17-planning`
  routes block steps to it, and `/block` follows it as a standalone cast. The roadmap entry had
  said several platform facts lived in no reference; they were already in the starter facts, so the
  reference carries discipline and cites facts. Full detail in `CHANGELOG.md`
  (`_work/shipped/umbraco-block-authoring-reference/spec.md`, `_features/block-authoring.md`).`
  Write the `_work/shipped/` path, since the entry describes the increment after archiving.

**Test first**:
- `find skills -name SKILL.md | wc -l` → `35`; `grep -c '^### ' docs/spell-cards.md` → `34` (RED).
- After the card, both → `35` (GREEN).

**Validation**:
- [Automated]: `bash scripts/check-contract.sh` → `22 checks passed`.
- [Automated]: `grep -c 'umbraco-17-block-authoring' ROADMAP.md CHANGELOG.md docs/spell-cards.md`
  → non-zero for each, and `grep -c 'cannot see' ROADMAP.md` → `0`.
- [Automated]: `git diff --stat main -- skills/core` prints nothing.
- [Manual]: read the new Recently shipped entry beside the one above it. Same shape, same length
  band, same closing parenthetical.

---

### Step 5 — Verify by hand and record it

> **Prompt**: Implement Step 5 of `_work/shipped/umbraco-block-authoring-reference/plan.md`. Write
> `_work/shipped/umbraco-block-authoring-reference/assets/verification-log.md`, predictions first, then run
> three checks and record their results verbatim. First, dispatch a fresh general-purpose worker
> with a synthetic plan step for a "Testimonial" block (quote as rich text, author name as text) whose
> prompt names `umbraco-17-block-authoring`, and ask it to report the test it would write and the
> exemplar and palette questions it would ask, without editing any file. Second, walk the thinned
> `/block` and `/styleguide` Step 9 structurally for acceptance criteria AC7 and AC8. Third, run the
> single-holder grep and `git diff --stat main -- skills/core`. If the demo project at the sibling
> path has the pack reinstalled from this branch, also cast `/block` there and record the result;
> otherwise record that the live cast was not run and why.

**What to build**:

- `_work/shipped/umbraco-block-authoring-reference/assets/verification-log.md` with: the working tree state
  and gate baseline; a **Predictions** section written before anything runs; then one section per
  check with the exact prompt or command and the exact output.
  - **Worker probe.** Prediction: the worker lists `umbraco-17-block-authoring` among its skills,
    loads it, and its reported test asserts presence with `toBeTruthy()` and reads
    `properties ?? []`; it says it would ask which existing block to copy and which palette the block
    belongs in. Record the worker's full report block. A worker that asserts `toBeNull()` or reads
    `groups.flatMap` is a FAIL and means the reference is not being reached or not being followed;
    say which.
  - **Structural walk for AC7 and AC8.** Prediction: `/block` has eight steps, Step 5's heading is
    unchanged, its `Next:` line is unchanged, and `/styleguide` Step 9 and its report's `Next:` line
    still describe authoring a view for element types that already exist. Record the grep output.
  - **Single holder and core untouched.** Prediction: the grep lists the reference and, for the
    two fact phrases, the starter-facts topic files, and not the spell; the core diff is empty.
  - **Live cast on the demo project**, conditional. Record whether it ran.

**Test first**: this step is verification; its predictions are its test. They are written before the
runs, and a prediction that fails is recorded as a failure, not rewritten.

**Validation**:
- [Automated]: the log file exists and its Predictions section precedes every result.
- [Automated]: `bash scripts/check-contract.sh` → `22 checks passed`; `bash tests/run.sh` →
  `110/110 cases passed`.
- [Manual]: every prediction has a recorded outcome, and any FAIL has a sentence saying what it
  means for the increment.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes.

> **Prompt**: Run `/feature update block-authoring` to verify the living behavioral doc reflects the
> actual implementation. Review each scenario against the code and test results. Update any scenario
> where the implementation diverged from the draft. Fill in the test coverage table with real test
> paths and line numbers, or mark target tests pending if no harness exists yet; for scenarios proved
> only by the verification log, point the Test File column at
> `_work/shipped/umbraco-block-authoring-reference/assets/verification-log.md`. Remove the "Draft" banner.
> Commit the verified doc.
>
> **Validation**: Every scenario matches observable behavior; the coverage table has no unexpected
> "Not covered" gaps, and the parking-lot item to backfill `/block`'s pre-existing behavior from code
> is still listed under Increments.

---

## File Summary

| Action | File |
|--------|------|
| Create | `skills/umbraco-17/reference/umbraco-17-block-authoring/SKILL.md` |
| Modify | `scripts/check-install.sh` (`ROSTER_PACK`, `PACK_SOURCE`) |
| Modify | `README.md` (`umbraco-17` pack table row) |
| Modify | `skills/umbraco-17/reference/umbraco-17-planning/SKILL.md` (routing section, Slice row, step-order sentence) |
| Modify | `skills/umbraco-17/spellbook/block/SKILL.md` (thinned; steps and numbering kept) |
| Modify | `docs/spell-cards.md` (new card, `/block` card, count line) |
| Modify | `CHANGELOG.md` (Unreleased → Added) |
| Modify | `ROADMAP.md` (entry removed from Next; dated entry added to Recently shipped) |
| Create | `_work/shipped/umbraco-block-authoring-reference/assets/verification-log.md` |
| _(work type: `new-capability`)_ Update | `_features/block-authoring.md` (verified by the final step) |
