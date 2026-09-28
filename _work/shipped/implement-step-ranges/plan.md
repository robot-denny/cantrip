# Plan: Implement-Step Ranges

**Spec**: `_work/shipped/implement-step-ranges/spec.md`
**Branch**: `robot-denny/implement-step-ranges`
**Work type**: `new-capability` — copied verbatim from the spec's `**Work type**:` line; this decides
how the final step records behavior
**Feature doc**: `plan-execution` (`_features/plan-execution.md`) — copied from the spec; the final
step targets this, not the increment slug

## Context

`/implement-step` runs one plan step per cast. This increment lets a cast name a range, `1-3` or
`3-`, so the steps run in order with one fresh worker each, every report relayed as it lands, and the
run stopping at the end of the range or at the first BLOCKED. Review stays a cast the person makes at
the pause, and `/plan`'s closing report gains a mark on every step that ends in a manual check so the
developer can pick a range without opening the file. Discovery and the spec settled the shape;
nothing here re-opens it.

The unit of work in this repo is **a shipped unit plus its registration**. This increment amends two
core spells, `skills/core/spellbook/implement-step/SKILL.md` and `skills/core/spellbook/plan/SKILL.md`,
and updates every surface that says "one step per cast": the `workflow` skill, the README's spellbook
row, `docs/layout.md`, and two spell cards. It ships no script. Core has never shipped an executable,
and a spell's behavior is prose the model follows, so `tests/run.sh` gains no suite. The RED and GREEN
signals are `./scripts/check-contract.sh` plus written-down manual checks against a fixture plan,
evidenced in validation logs under `_work/shipped/implement-step-ranges/assets/`.

---

## Key Decisions

- **No harness, so every step is proved two ways.** `./scripts/check-contract.sh` is the automated
  gate. The behavioral check is a dry run of the edited spell against a fixture plan, with the expected
  output written into the step's validation log *before* the edit, per `tdd-principles`. A dispatched
  worker cannot cast a spell, so its dry run is a **stand-in**: it reads the edited `SKILL.md` and
  walks it against the fixture, labelling the log as a stand-in. The real cast is the person's, listed
  as a Manual validation on every spell-editing step. Skills hot-reload, so a cast made after the edit
  runs the new text; this is not the reviewer-agent trap recorded in `AGENTS.md`.

- **The fixture plan lives with the increment and is invoked by path.** `/implement-step` accepts a
  plan as a slug or a path. A fixture under `_work/accordion-block/` would read as a real increment,
  so it lives at `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md` and is cast by
  path. Its six steps each create one small file under `_scratch/accordion-block/`, which is
  git-ignored, and validate with `test -f`. Steps 4 and 6 carry a `[Manual]` line. Step 2 has a
  variant, `accordion-block-blocking-plan.md`, whose step 2 instructs the worker to report BLOCKED.

- **Range grammar.** The step argument matches `^(\d+)(?:-(\d+)?)?$`. One number is a single step;
  `N-M` is a closed range; `N-` is open and resolves to the highest `### Step N` heading in the plan.
  `N-N` is a single step and produces the single-step output with no run wrapper. Bounds are checked
  against the step numbers actually found, and a reversed, zero, or out-of-range bound aborts before
  any worker starts with the message the single-step form already uses, listing the steps found. A
  closed range never clamps; `3-` is how a developer says "to the end".

- **Relay shape.** Each step's report block is surfaced verbatim as it lands, exactly as today. The
  `Next:` line appears once, after the last step of the run. It points at review, then at the next
  single step by number; the developer chooses whether to type a range.

- **Earlier reports travel forward as whole blocks, uncapped.** From the second step of a run the
  worker prompt carries a section headed `## Earlier in this run`, placed after *Key decisions already
  made* and before *Your step*, holding the full `## Step N — DONE` block of every step finished in
  this run, in order. Only this run's reports, never those of earlier casts. No cap: a plan is bounded
  and a block is a few dozen lines. The spec records the cap as the first thing to add if a consumer
  reports a prompt too long to be useful.

- **BLOCKED and a missing report are the same stop.** A worker that returns no `## Step N —` block is
  treated as BLOCKED and the relay says so, because the run cannot tell an unfinished step from a
  finished one without it. The closing line points at re-invoking from the blocked step to the range's
  original end.

- **The review scope rule.** After a run the closing line names `uncommitted` unless any step's report
  in the run says it committed, in which case it names `branch`. The reason travels in one clause.

- **The dirty-tree prompt fires once**, before the first step of a run. Between steps the tree is
  dirty by design.

- **A numbered spell-cast step ends the run before it.** The single-step refusal already exists in
  the spell's Step 2. A run reaching such a step stops before dispatching it, relays what finished, and
  hands it back with the same message.

- **The manual-check mark in `/plan`'s report** is derived from a `[Manual]` line under the step's
  Validation block. The closing report lists every numbered step as `  N  <title>` and appends
  `(manual check)` to a marked step. Path, step count, branch, and `Next:` are unchanged.

- **Slots in this repo are empty.** There is no `.agents/config/`, so the build and test commands are
  inferred: `./scripts/check-contract.sh` and `tests/run.sh`. No test-location convention is
  established because no test file is written.

- **Documentation surfaces, enumerated so none is missed.** `skills/core/reference/workflow/SKILL.md`
  line 25; `README.md` line 148; `docs/layout.md` line 89; `docs/spell-cards.md` cards for
  `/implement-step` and `/plan`; `CHANGELOG.md` under *Unreleased*; `ROADMAP.md`. The testify spell's
  reasoning at line 425 still holds with ranges and is left alone.

- **The roadmap's *Now* section names this increment while it is in flight.** That section has been
  wrong before by describing the present, so the sentence names the branch and nothing else. Closing
  the increment moves it to `CHANGELOG.md`.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — The fixture plan, the range grammar, and an ordered run

> **Prompt**: Implement Step 1 of `_work/shipped/implement-step-ranges/plan.md`. First create the fixture plan
> `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md`: a plan in the format
> `skills/core/spellbook/plan/SKILL.md` produces, with a Context section, a Key Decisions section, and
> six numbered steps titled "Element type", "View", "Palette registration", "Open and close behavior",
> "Nested content", and "Styling". Each step's prompt has the worker create one file
> `_scratch/accordion-block/step-N.txt` containing the step title, and its Validation has
> `[Automated]: test -f _scratch/accordion-block/step-N.txt`. Steps 4 and 6 also carry a `[Manual]`
> line ("open the file and confirm it names the step"). Leave the behavior-recording step unnumbered.
> Then write `_work/shipped/implement-step-ranges/assets/step1-validation-log.md` with the expected output
> for casts `1-3`, `3-`, `4-4`, `3-9`, `4-2`, `0-2`, and `-3` *before* editing the spell. Then edit
> `skills/core/spellbook/implement-step/SKILL.md`: the description and `argument-hint` name the three
> forms; Step 1 parses `^(\d+)(?:-(\d+)?)?$`, resolves an open end to the highest `### Step N` heading,
> treats `N-N` as `N`, and aborts on a reversed, zero, or out-of-range bound with the existing
> one-line message listing the steps found; Steps 2, 4, and 5 run once per step in the range in
> order, each with its own composed prompt and worker; Step 6 relays each report block verbatim as
> it lands and prints one `Next:` line after the last step. Rewrite the *Rules of thumb* bullet that
> says the spell executes one step. Do not change the dirty-tree check, the BLOCKED handling, or the
> worker envelope in this step. Run `./scripts/check-contract.sh` and record the stand-in dry run in
> the log, labelled as a stand-in.

**What to build**: `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md`;
`_work/shipped/implement-step-ranges/assets/step1-validation-log.md`;
`skills/core/spellbook/implement-step/SKILL.md` (frontmatter `description` and `argument-hint`,
Step 1 parsing, the run loop across Steps 2, 4, 5, and 6, the *Rules of thumb* bullet).

**Test first**:
- Write the fixture plan and the validation log's *Expected* section first. For `1-3` the expectation
  is three report blocks in order, three files under `_scratch/accordion-block/`, and one `Next:` line
  after the third block. For `3-` it is steps 3 through 6 and no dispatch of the unnumbered final
  step. For `4-4` it is byte-for-byte the single-step output. For `3-9`, `4-2`, `0-2`, and `-3` it is
  no worker started and a message naming steps 1 through 6.
- RED is the unedited spell: `1-3` is rejected as malformed by today's Step 1. Record that.
- Then edit the spell and record the stand-in walk-through against each cast.
- Assert on what the developer sees, the relay and the files, not on the spell's wording.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 22 checks pass.
- [Automated]: `tests/run.sh` — every suite unchanged and green.
- [Manual]: cast `/implement-step _work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md 1-3`
  in your own session. Confirm three report blocks in order, `ls _scratch/accordion-block/` shows
  `step-1.txt` through `step-3.txt`, and exactly one `Next:` line. Then cast `4-4` and `3-9` and
  confirm they match the log's expectations. Clear `_scratch/accordion-block/` between casts.

---

### Step 2 — A blocked step ends the run and says where to resume

> **Prompt**: Implement Step 2 of `_work/shipped/implement-step-ranges/plan.md`. Create
> `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`, a copy of the
> six-step fixture whose step 2 prompt tells the worker to stop and report `## Step 2 — BLOCKED` with
> the note "fixture: deliberate block". Write
> `_work/shipped/implement-step-ranges/assets/step2-validation-log.md` with the expected output for a `1-4`
> cast on it *before* editing: step 1 DONE relayed, step 2 BLOCKED relayed, no worker started for
> steps 3 or 4, `_scratch/accordion-block/step-1.txt` present and `step-3.txt` absent, and a `Next:`
> line saying to resolve the blocker and re-invoke `/implement-step <plan> 2-4`. Also write the
> expectation for a worker that returns no report block: the run stops after that step and the relay
> says the step is treated as BLOCKED because no report arrived. Then edit
> `skills/core/spellbook/implement-step/SKILL.md` Step 6 so a BLOCKED report, or a report with no
> `## Step N —` block, ends the run there, keeps finished steps in place, and prints the resume
> pointer to the range's original end. Run `./scripts/check-contract.sh` and record the stand-in dry
> run.

**What to build**: `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`;
`_work/shipped/implement-step-ranges/assets/step2-validation-log.md`;
`skills/core/spellbook/implement-step/SKILL.md` (Step 6, the BLOCKED and missing-report branches of
the run, the resume pointer).

**Test first**:
- Write both expectations in the log before editing.
- RED is the Step 1 spell: it has no rule for BLOCKED mid-run, so a walk-through either continues past
  the block or has nothing to say. Record which.
- Then edit and record the stand-in walk-through for both cases.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 22 checks pass.
- [Manual]: cast `/implement-step _work/shipped/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md 1-4`
  in your own session. Confirm the relay shows step 1 DONE then step 2 BLOCKED, `step-3.txt` does not
  exist, and the `Next:` line names `2-4`.

---

### Step 3 — Earlier reports travel forward

> **Prompt**: Implement Step 3 of `_work/shipped/implement-step-ranges/plan.md`. Write
> `_work/shipped/implement-step-ranges/assets/step3-validation-log.md` with the expected composed prompts for
> a `3-4` cast on `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md` *before*
> editing: step 3's prompt has no `## Earlier in this run` section; step 4's prompt has one, placed
> after `## Key decisions already made (do not re-derive)` and before `## Your step`, holding step 3's
> full `## Step 3 — DONE` report block verbatim. Then edit
> `skills/core/spellbook/implement-step/SKILL.md` Step 4 so the composed prompt gains that section from
> the second step of a run onward, holding every report block from this run in order, and carrying
> nothing from earlier casts. State in the spell that the section is uncapped and why. Run
> `./scripts/check-contract.sh`. For evidence, have the stand-in write both composed prompts into the
> log in full.

**What to build**: `_work/shipped/implement-step-ranges/assets/step3-validation-log.md`;
`skills/core/spellbook/implement-step/SKILL.md` (Step 4, the `## Earlier in this run` section of the
worker prompt template).

**Test first**:
- Write the expected prompt shapes in the log before editing.
- RED is the Step 2 spell: step 4's composed prompt carries no earlier report, so a convention chosen
  in step 3's notes is invisible to step 4. Record the prompt as composed today.
- Then edit and record both composed prompts.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 22 checks pass.
- [Manual]: in your own session, cast `3-4` on the fixture with a temporary edit to fixture step 3's
  prompt asking the worker to add the note "fixture: convention chosen here" to its report. Confirm
  step 4's worker mentions that note in its own report, which it can only do if it received it. Revert
  the fixture edit.

---

### Step 4 — The run envelope: dirty tree once, review scope named, spell-cast step ends the run

> **Prompt**: Implement Step 4 of `_work/shipped/implement-step-ranges/plan.md`. Three behaviors, taken one at
> a time, each with its expectation written into
> `_work/shipped/implement-step-ranges/assets/step4-validation-log.md` before its edit. First, the dirty-tree
> prompt: edit `skills/core/spellbook/implement-step/SKILL.md` Step 3 so the check runs once before
> the first step of a run and not between steps, and declining it runs nothing. Second, the closing
> line: edit Step 6 so the `Next:` line after a run says to review the diff and cast `/code-review`
> with scope `uncommitted`, or `branch` when any step's report in the run says it committed, with a
> one-clause reason in either case; after a run that reached the last numbered step, continue with
> `/commit-message` and archiving as today. Third, an older plan's numbered spell-cast step: create
> `_work/shipped/implement-step-ranges/assets/fixtures/legacy-hero-plan.md`, five numbered steps whose step 5
> reads "Run `/feature update hero`", and edit Step 2 so a run reaching such a step stops before it,
> relays what finished, and hands it back with the existing spell-cast message rather than aborting.
> Run `./scripts/check-contract.sh` after each behavior and record each stand-in walk-through.

**What to build**: `_work/shipped/implement-step-ranges/assets/step4-validation-log.md`;
`_work/shipped/implement-step-ranges/assets/fixtures/legacy-hero-plan.md`;
`skills/core/spellbook/implement-step/SKILL.md` (Step 3 once-per-run; Step 6 closing line and scope
rule; Step 2 spell-cast step inside a run).

**Test first**, one cycle per behavior, in order, never all three expectations before the first edit:
- Dirty tree: expectation is one prompt on a dirty tree before step 1 and none before steps 2 and 3;
  answering "no" runs nothing. RED is the Step 3 spell, which describes the check without saying it
  fires once.
- Review scope: expectation for a `1-3` cast on the six-step fixture is a closing line naming
  `uncommitted` with its reason; for the same cast with fixture step 2 temporarily told to commit, a
  closing line naming `branch` with its reason. RED is today's closing line, which names no scope.
- Spell-cast step: expectation for `3-` on `legacy-hero-plan.md` is steps 3 and 4 run, the run stops
  before 5, and the relay says step 5 is a spell-cast to be cast directly. RED is the Step 3 spell,
  where the refusal exists only for a single cast.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 22 checks pass.
- [Manual]: with one uncommitted change in the tree, cast `1-3` on the six-step fixture and confirm
  the prompt appears once. Cast `3-` on `legacy-hero-plan.md` and confirm the run stops before step 5
  with the spell-cast message. Read the closing line of each run and confirm it names a scope and a
  reason.

---

### Step 5 — The plan report marks the steps that end in a manual check

> **Prompt**: Implement Step 5 of `_work/shipped/implement-step-ranges/plan.md`. Write
> `_work/shipped/implement-step-ranges/assets/step5-validation-log.md` with the expected closing report for
> the six-step fixture `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md` *before*
> editing: after `Steps: 6`, six lines of the form `  N  <title>`, with `(manual check)` appended to
> steps 4 and 6 only, then the existing `Branch:` and `Next:` lines. Also write the expectation for a
> plan with no `[Manual]` lines: every step listed, no marks. Then edit
> `skills/core/spellbook/plan/SKILL.md` Step 7 so the report lists every numbered step by number and
> title and marks each whose Validation block carries a `[Manual]` line. Say in the spell that the
> mark is derived, so a plan author adds nothing. Run `./scripts/check-contract.sh`. For evidence,
> have the stand-in produce the report for both fixtures into the log.

**What to build**: `_work/shipped/implement-step-ranges/assets/step5-validation-log.md`;
`skills/core/spellbook/plan/SKILL.md` (Step 7, the report format).

**Test first**:
- Write both expected reports in the log before editing.
- RED is today's Step 7, whose report has no step list at all.
- Then edit and record the stand-in's two reports.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 22 checks pass.
- [Manual]: cast `/plan` on a throwaway description with two steps, one verified by a command and one
  by eye, into a scratch increment. Confirm the closing report lists both steps and marks only the
  second. Delete the scratch increment.

---

### Step 6 — Every surface describes the range, and the changelog and roadmap record it

> **Prompt**: Implement Step 6 of `_work/shipped/implement-step-ranges/plan.md`. Update every surface that
> describes `/implement-step` as one step per cast so it describes the range as an ordinary form:
> `skills/core/reference/workflow/SKILL.md` line 25; the `/implement-step` row in `README.md`'s
> spellbook table; `docs/layout.md`'s chain diagram line; and in `docs/spell-cards.md` the
> `/implement-step` card's Cast, Does, Watch for, and Then lines plus the `/plan` card's Watch for line
> for the marked report. Keep the single-step cast as the form each surface leads with. Add a
> `CHANGELOG.md` entry under *Unreleased → Added* for the range and the marked plan report, written
> as "what will change in my project when I update". In `ROADMAP.md`, name this increment's branch in
> *Now* as in flight, and add a *Later* entry: a plan long enough to be tedious is usually a spec
> holding several increments, seen once at fourteen steps, and nothing says so at plan time. Follow
> the `prose-discipline` skill for every sentence you write. Run `./scripts/check-contract.sh` and
> `grep -rn -i 'one step' README.md docs skills/core/reference/workflow` to confirm each surviving
> mention describes the single step as one form of three.

**What to build**: `skills/core/reference/workflow/SKILL.md`; `README.md`; `docs/layout.md`;
`docs/spell-cards.md`; `CHANGELOG.md`; `ROADMAP.md`.

**Test first**:
- The manual check, written before editing: the grep above lists the four one-step mentions found
  during planning. After the edit each surviving hit describes the range or the single-step form as
  one of three, and no hit says "one step per cast" as a limit.
- RED is the grep as it stands.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 22 checks pass, including the README-link check.
- [Manual]: read the `/implement-step` spell card as a developer who has never used a range and
  confirm the three forms are shown and the single step still comes first.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes.

> **Prompt**: Run `/feature update plan-execution` to verify the living behavioral doc reflects the
> actual implementation. Review each scenario against the edited spells and the validation logs under
> `_work/shipped/implement-step-ranges/assets/`. Update any scenario where the implementation diverged from
> the draft. Fill in the test coverage table: this repo has no harness for spells, so each row points
> at the validation log that evidenced it, or stays `Not covered` where no evidence was captured.
> Remove the "Draft" banner. Commit the verified doc.
>
> **Validation**: Every scenario matches observable behavior; the coverage table has no unexpected
> "Not covered" gaps.

---

## File Summary

| Action | File |
|--------|------|
| Create | `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-plan.md` |
| Create | `_work/shipped/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md` |
| Create | `_work/shipped/implement-step-ranges/assets/fixtures/legacy-hero-plan.md` |
| Create | `_work/shipped/implement-step-ranges/assets/step1-validation-log.md` through `step5-validation-log.md` |
| Modify | `skills/core/spellbook/implement-step/SKILL.md` |
| Modify | `skills/core/spellbook/plan/SKILL.md` |
| Modify | `skills/core/reference/workflow/SKILL.md` |
| Modify | `README.md` |
| Modify | `docs/layout.md` |
| Modify | `docs/spell-cards.md` |
| Modify | `CHANGELOG.md` |
| Modify | `ROADMAP.md` |
| _(work type: `new-capability`)_ Update | `_features/plan-execution.md` |
