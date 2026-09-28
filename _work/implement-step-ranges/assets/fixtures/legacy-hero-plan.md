# Plan: Hero Block (legacy numbering)

> **Fixture.** This plan exists so `/implement-step` can be cast against an older plan that numbers
> its behavior-recording step. Steps 1 to 4 each write one file under `_scratch/`, which is
> git-ignored, so a run leaves nothing in the tree. Step 5 is a spell-cast, numbered the way plans
> were written before the final step was left unnumbered. Cast it by path. Clear
> `_scratch/legacy-hero/` between casts.

**Spec**: none (fixture)
**Branch**: whichever branch is checked out; the fixture touches no tracked file
**Work type**: `new-capability`
**Feature doc**: none (fixture)

## Context

A hero block is the large banner at the top of a page, with a heading, a line of copy, and a call to
action. This plan builds one in four tiny steps and then, as a fifth numbered step, records the
behavior with a spell. Each implementation step creates a single text file named after the step
under `_scratch/legacy-hero/`, and nothing else.

---

## Key Decisions

- **Every implementation step writes exactly one file.** Step N creates
  `_scratch/legacy-hero/step-N.txt` containing the step's title on one line. Nothing else is
  created or modified. The directory is git-ignored, so no step dirties the working tree.
- **Step 5 is a spell-cast.** It is numbered on purpose, so a run that reaches it has to stop before
  it. A worker must never be dispatched for it.
- **No test harness.** The automated check for each implementation step is `test -f` on the file it
  created.
- **The worker does not commit.** Changes stay in place for the developer to inspect.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Element type

> **Prompt**: Implement Step 1 of `_work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md`.
> Run `mkdir -p _scratch/legacy-hero`, then create `_scratch/legacy-hero/step-1.txt`
> containing the single line `Element type`. Create nothing else and modify nothing else.

**What to build**: `_scratch/legacy-hero/step-1.txt`, one line: `Element type`.

**Validation**:
- [Automated]: `test -f _scratch/legacy-hero/step-1.txt` — exits 0.

---

### Step 2 — View

> **Prompt**: Implement Step 2 of `_work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md`.
> Run `mkdir -p _scratch/legacy-hero`, then create `_scratch/legacy-hero/step-2.txt`
> containing the single line `View`. Create nothing else and modify nothing else.

**What to build**: `_scratch/legacy-hero/step-2.txt`, one line: `View`.

**Validation**:
- [Automated]: `test -f _scratch/legacy-hero/step-2.txt` — exits 0.

---

### Step 3 — Call to action

> **Prompt**: Implement Step 3 of `_work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md`.
> Run `mkdir -p _scratch/legacy-hero`, then create `_scratch/legacy-hero/step-3.txt`
> containing the single line `Call to action`. Create nothing else and modify nothing else.

**What to build**: `_scratch/legacy-hero/step-3.txt`, one line: `Call to action`.

**Validation**:
- [Automated]: `test -f _scratch/legacy-hero/step-3.txt` — exits 0.

---

### Step 4 — Styling

> **Prompt**: Implement Step 4 of `_work/implement-step-ranges/assets/fixtures/legacy-hero-plan.md`.
> Run `mkdir -p _scratch/legacy-hero`, then create `_scratch/legacy-hero/step-4.txt`
> containing the single line `Styling`. Create nothing else and modify nothing else.

**What to build**: `_scratch/legacy-hero/step-4.txt`, one line: `Styling`.

**Validation**:
- [Automated]: `test -f _scratch/legacy-hero/step-4.txt` — exits 0.

---

### Step 5 — Record the durable behavior

> **Prompt**: Run `/feature update hero`. Nothing here needs recording; the step exists so a run
> across it meets a numbered spell-cast.

**What to build**: nothing. This is a spell you cast, not implementation work.

**Validation**: none.

---

## File Summary

| Action | File |
|--------|------|
| Create | `_scratch/legacy-hero/step-1.txt` |
| Create | `_scratch/legacy-hero/step-2.txt` |
| Create | `_scratch/legacy-hero/step-3.txt` |
| Create | `_scratch/legacy-hero/step-4.txt` |
| _(work type: `new-capability`)_ Update | none (fixture) |
