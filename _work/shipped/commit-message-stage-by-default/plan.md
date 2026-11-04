# Plan: Commit Message Stages Related Files by Default

**Spec**: `_work/shipped/commit-message-stage-by-default/spec.md`
**Branch**: `robot-denny/commit-message-stage-by-default`
**Work type**: `change-to commit-message` — copied verbatim from the spec's `**Work type**:` line;
this decides how the final step records behavior
**Feature doc**: `commit-message` (`_features/commit-message.md`, not yet written) — copied from the
spec; the final step targets this, not the increment slug

## Context

`/commit-message` stops when nothing is staged and is not allowed to stage files, so developers
append "staging any files necessary" to every cast. This increment removes that limitation and
nothing more: the spell considers unstaged and new files too, proposes which to include alongside
the message, and stages them only when the developer approves. Which files are related is left to
the agent's own judgment; the spec rules out adding heuristics for it.

The unit of work in this repo is **a shipped unit plus its registration**: here, one spell file
(`skills/core/spellbook/commit-message/SKILL.md`) plus the surfaces that describe it to people. A
spell's behavior is prose the model follows, so there is no automated test of the behavior itself.
`./scripts/check-contract.sh` is the automated gate, and the behavioral signal is expected outcomes
written into a validation log *before* the edit, then checked by a stand-in walk-through and real
casts.

---

## Key Decisions

- **Lean edit, four touches to the spell.** (1) Add `Bash(git add:*)` to `allowed-tools`, which is
  what makes staging run without a permission prompt (spec decision). (2) Add the unstaged diff to the
  spell's **Context** block beside the staged diff, so the agent sees what it is judging; `git status`
  already lists new files. (3) Replace "If nothing is staged, say so and stop" with a stop only when
  there is nothing to commit at all, plus one short paragraph saying the agent decides which unstaged
  or new files belong, whole files only, and that a plain-language request to commit only what is
  staged is honored. (4) In **Output**, show the files it would add alongside the message, and stage
  them only on approval, immediately before committing. Update the frontmatter `description` to match.
  No relatedness rules, file-pattern lists, or grouping heuristics: the spec's Decisions section
  rules them out.

- **Declining changes nothing.** Staging and committing happen together after approval. A declined
  proposal leaves the index exactly as the developer left it, so there is no "still staged"
  report to make.

- **No harness, so the spell step is proved two ways.** As in the shipped `implement-step-ranges`
  increment: expected outcomes are written into `assets/step1-validation-log.md` before the edit, per
  `tdd-principles`, asserting on what the developer sees (the proposal, which files it lists, the
  state of `git status` afterwards), never on the spell's wording. A dispatched worker cannot cast a
  spell, so its check is a labelled **stand-in**: it reads the edited `SKILL.md` and walks each
  scenario against it. The real casts are the developer's, listed as Manual validation. Skills
  hot-reload, so a cast after the edit runs the new text.

- **Real casts dogfood on this branch.** Step 2's own doc edits are the natural test material: leave
  them unstaged and cast `/commit-message` against them. No scratch repository is needed.

- **Final step uses `/feature`'s from-code mode.** `_features/commit-message.md` does not exist, so
  `/feature update commit-message` has nothing to update. The spell is small enough that from-code mode
  documents all of it, including this change, in one pass. That replaces the spec's note about
  documenting only this increment and backfilling the rest later.

- **Commands.** No `.agents/config/` exists in this repo; the gate is `./scripts/check-contract.sh`
  (also run by the pre-commit hook), and `./tests/run.sh` runs the fixture suites, none of which
  covers this spell.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Let the spell stage related files on approval

> **Prompt**: Implement Step 1 of `_work/shipped/commit-message-stage-by-default/plan.md`. First write
> `_work/shipped/commit-message-stage-by-default/assets/step1-validation-log.md` with the expected outcome of
> each of the spec's four draft scenarios plus the old "staging any files necessary" phrasing,
> asserting on what the developer sees, not on spell wording. Then edit
> `skills/core/spellbook/commit-message/SKILL.md` exactly as the plan's first Key Decision describes:
> add `Bash(git add:*)` to `allowed-tools`, add the unstaged diff to the Context block, replace the
> "nothing is staged" stop with a nothing-to-commit stop plus one short paragraph leaving relatedness to
> the agent's judgment (whole files only, plain-language opt-out), update **Output** so staging happens
> only on approval just before the commit, and update the frontmatter `description`. Add nothing else.
> Then walk each expectation against the edited file as a labelled stand-in, record the results in the
> log, and run `./scripts/check-contract.sh`.

**What to build**:
- `_work/shipped/commit-message-stage-by-default/assets/step1-validation-log.md`: expected outcomes first,
  stand-in results after.
- `skills/core/spellbook/commit-message/SKILL.md`: the four touches in Key Decisions, plus the
  `description` line.

**Test first**:
- Write the validation log's **Expected, written before the edit** section, one block each for:
  nothing staged with `README.md` edited; `SKILL.md` staged with a related unstaged `CHANGELOG.md`;
  declining the proposal; "just what's staged"; and casting with "staging any files necessary".
- Each block states the proposal's file list and the `git status` result afterwards.
- RED: walk the expectations against the *unedited* spell and record that the first scenario stops
  with "nothing is staged" and that no scenario can stage a file.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes.
- [Automated]: the stand-in section of the log shows every expectation met by the edited spell, and
  the diff to `SKILL.md` adds no relatedness rules or file-pattern lists.
- [Manual]: in this repo, edit any tracked file, stage nothing, and cast `/commit-message`. It should
  propose committing that file instead of stopping, with no permission prompt for staging. Decline
  it, then confirm with `git status` that nothing was staged, and revert the edit.

---

### Step 2 — Update the docs that describe the spell, and dogfood it

> **Prompt**: Implement Step 2 of `_work/shipped/commit-message-stage-by-default/plan.md`. The
> `/commit-message` spell now considers unstaged and new files and stages related ones on approval.
> Update the surfaces that say otherwise: in `docs/spell-cards.md`, the `/commit-message` card's
> **Cast** line ("reads your staged changes") and **Needs** line ("something staged") should say it
> reads staged and unstaged changes and needs something to commit; add one entry under `### Changed`
> in the `[Unreleased]` section of `CHANGELOG.md`, written as "what will change in my project when I
> update". Check `README.md` line ~152 and `docs/layout.md` line ~93 and change them only if they now
> state something false. Run `./scripts/check-contract.sh`. Leave all edits **unstaged**; the
> developer commits them by casting `/commit-message` as the manual check.

**What to build**:
- `docs/spell-cards.md`: the `/commit-message` card's Cast and Needs lines.
- `CHANGELOG.md`: one `### Changed` entry under `[Unreleased]`.
- `README.md`, `docs/layout.md`: only if a statement is now false.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` passes.
- [Manual]: with this step's edits unstaged, cast `/commit-message`. The proposal should list
  `docs/spell-cards.md` and `CHANGELOG.md` as files to add. Approve it, and confirm with `git status`
  and `git show --stat` that both landed in one commit. Then, on any later commit in this increment,
  cast with "just what's staged" once to check the opt-out. Add these results to the step 1 log under
  **Real casts**.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes.

> **Prompt**: Run `/feature commit-message` in from-code mode to create `_features/commit-message.md`,
> named for the spell's area, from `skills/core/spellbook/commit-message/SKILL.md`. Include the
> observable behavior this increment established: unstaged and new files are considered, related ones
> are proposed alongside the message and staged only on approval, whole files only, a plain-language
> opt-out, and a stop only when there is nothing to commit. Leave point-in-time criteria in the shipped
> spec. Point the coverage table at the step 1 validation log for what the real casts proved. Add a
> revision note dated today.
>
> **Validation**: The doc describes current behavior with no transition-style ("no longer stops…")
> Rules; it is named `commit-message`, not after this increment.

---

## File Summary

| Action | File |
|--------|------|
| Create | `_work/shipped/commit-message-stage-by-default/assets/step1-validation-log.md` |
| Modify | `skills/core/spellbook/commit-message/SKILL.md` |
| Modify | `docs/spell-cards.md` |
| Modify | `CHANGELOG.md` |
| Modify (only if now false) | `README.md`, `docs/layout.md` |
| _(work type: `change-to commit-message`)_ Create | `_features/commit-message.md` via from-code mode: the capability doc did not exist yet (**no doc named after the increment**) |
