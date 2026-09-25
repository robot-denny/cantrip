# Plan: Accordion Block (blocking variant)

> **Fixture.** This plan is the six-step accordion fixture with one change: step 2 blocks by
> design. Cast it by path to watch a run stop at a BLOCKED report, keep step 1's file in place,
> and point at `2-4` as the place to resume. Every other step writes one file under `_scratch/`,
> which is git-ignored, so a run leaves nothing in the tree. Clear `_scratch/accordion-block/`
> between casts.

**Spec**: none (fixture)
**Branch**: whichever branch is checked out; the fixture touches no tracked file
**Work type**: `new-capability`
**Feature doc**: none (fixture)

## Context

An accordion block is a content block with a heading that a reader clicks to open or close a panel
of content underneath. This plan builds one in six steps. Each step is deliberately tiny: the worker
creates a single text file named after the step under `_scratch/accordion-block/`, and nothing else.
The unit of work here is one file per step.

---

## Key Decisions

- **Every step but step 2 writes exactly one file.** Step N creates
  `_scratch/accordion-block/step-N.txt` containing the step's title on one line. Nothing else is
  created or modified. The directory is git-ignored, so no step dirties the working tree.
- **Step 2 blocks on purpose.** Its worker creates nothing and reports `## Step 2 — BLOCKED` with
  the note `fixture: deliberate block`. A run that reaches it must stop there; steps 3 onward exist
  so there is something the run could wrongly continue into.
- **No test harness.** The automated check for each step is `test -f` on the file it created.
  Steps 4 and 6 also carry a manual check, so a run across them exercises the case where a manual
  check sits inside a range.
- **The worker does not commit.** Changes stay in place for the developer to inspect.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Element type

> **Prompt**: Implement Step 1 of `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-1.txt`
> containing the single line `Element type`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-1.txt`, one line: `Element type`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-1.txt` — exits 0.

---

### Step 2 — View

> **Prompt**: Implement Step 2 of `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`.
> This step blocks by design. Create no file and modify nothing. Stop at once and end your response
> with the report block `## Step 2 — BLOCKED`. Under **Files changed** write `none`. Under
> **Validation results** write `none run`. Under **Notes** write the single line
> `fixture: deliberate block`.

**What to build**: nothing. The step exists so a run across it meets a BLOCKED report.

**Validation**:
- none. The step reports BLOCKED before any validation would run.

---

### Step 3 — Palette registration

> **Prompt**: Implement Step 3 of `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-3.txt`
> containing the single line `Palette registration`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-3.txt`, one line: `Palette registration`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-3.txt` — exits 0.

---

### Step 4 — Open and close behavior

> **Prompt**: Implement Step 4 of `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-4.txt`
> containing the single line `Open and close behavior`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-4.txt`, one line: `Open and close behavior`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-4.txt` — exits 0.
- [Manual]: open the file and confirm it names the step.

---

### Step 5 — Nested content

> **Prompt**: Implement Step 5 of `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-5.txt`
> containing the single line `Nested content`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-5.txt`, one line: `Nested content`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-5.txt` — exits 0.

---

### Step 6 — Styling

> **Prompt**: Implement Step 6 of `_work/implement-step-ranges/assets/fixtures/accordion-block-blocking-plan.md`.
> Run `mkdir -p _scratch/accordion-block`, then create `_scratch/accordion-block/step-6.txt`
> containing the single line `Styling`. Create nothing else and modify nothing else.

**What to build**: `_scratch/accordion-block/step-6.txt`, one line: `Styling`.

**Validation**:
- [Automated]: `test -f _scratch/accordion-block/step-6.txt` — exits 0.
- [Manual]: open the file and confirm it names the step.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes. In this fixture there is nothing to record, so the cast is a no-op; the step exists so an
open range such as `3-` has an unnumbered step past its end to stop before.

> **Prompt**: Run `/feature update accordion-block`. Nothing here needs recording.
>
> **Validation**: none.

---

## File Summary

| Action | File |
|--------|------|
| Create | `_scratch/accordion-block/step-1.txt` |
| _(none: step 2 blocks by design)_ | |
| Create | `_scratch/accordion-block/step-3.txt` |
| Create | `_scratch/accordion-block/step-4.txt` |
| Create | `_scratch/accordion-block/step-5.txt` |
| Create | `_scratch/accordion-block/step-6.txt` |
| _(work type: `new-capability`)_ Update | none (fixture) |
