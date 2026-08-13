# Plan: Language-Agnostic Review Failure Modes

**Spec**: `_work/shipped/review-failure-modes/spec.md`
**Branch**: review-failure-modes
**Work type**: change-to code-review
**Feature doc**: code-review

## Context

Two failure modes draw no finding from any reviewer today, in any language: an error rethrown in a way
that discards where it came from, and a log call that folds its values into the message text instead of
passing them as separate fields. Both are language-agnostic, so they belong in core. A third — long-running
work the caller cannot cancel — was in the original framing and turned out to be **already owned** by the
performance reviewer, so this increment states that ownership rather than duplicating it.

The work extends `skills/core/reference/reviewer-discipline/`: the two checks join the quality reviewer's
existing "Input validation and error handling" list, which already carries technology-neutral entries like
"Swallowed exceptions and empty catch blocks". The ownership statement joins the shared contract, which
already delineates reviewer domains in its severity section.

**Unit of work**: one review check, plus the written-down manual check that proves it. There is no test
harness for a review, so per the `tdd-principles` skill the RED→GREEN signal is a recorded before/after,
not an automated assertion.

---

## Key Decisions

- **The two checks go in the agent; the ownership statement goes in the shared contract.** This answers
  the spec's second open question. The checks are domain findings, so they belong with the reviewer whose
  domain they are — `agents/code-reviewer.md`, focus area 2. The cancellation-ownership fact is *about the
  boundary between reviewers*, which no single agent can own, so it goes in `reviewer-discipline/SKILL.md`
  beside the existing sentence that already maps each reviewer to its domain. The spec was right that
  these might not live in the same place.
- **`change-to code-review` stands, and `/feature` will seed the doc.** No `_features/code-review.md`
  exists. The workflow spine is explicit that classification must not depend on whether documentation
  exists, and that naming at area level makes the `new-capability` path converge on the same artifact
  `change-to` would produce. So the doc gets seeded thin, at area level, by the final step — not created
  by an implementation step, and not used as a reason to reclassify.
- **The gate is not the whole rule for technology names.** Check 8's pattern would not catch `ILogger`,
  `CancellationToken`, or `Serilog` — none are in it. They would still violate the layer contract, which
  forbids L0 naming a technology regardless of what the regex matches. Write the failure and its
  consequence; name no interface, library, or keyword belonging to one language.
- **Two languages, not one, for the lost-origin check.** The spec flags the error-return case as where the
  wording is most likely to read badly. A language that throws and a language that returns errors exercise
  genuinely different shapes of the same defect, and the wording has to cover both without naming either
  mechanism.
- **Cancellation ownership has no natural RED, so it gets an induced one.** The merged report already shows
  the finding once, because the quality reviewer never mentioned cancellation. Per `tdd-principles`, a
  check that has never failed proves only that it runs — so the honest signal is to *break* it
  deliberately, observe the doubled finding, then revert and add the statement that prevents it.
- **Commands, all inferred — the `stack.md` slots are empty because this repo has no `.agents/config/`.**
  Gate: `scripts/check-contract.sh`, also enforced by `.githooks/pre-commit`. Fixture regression:
  `tests/run.sh`. There is no build command; the deliverable is markdown. Same inference as the
  `dotnet-pack` plan recorded — worth a `stack.md` slot if this repo ever grows one.
- **No fixture under `tests/install-check/`.** That harness tests `check-install.sh`, and nothing here
  changes what it reports. Running it is regression only.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — The lost-origin check

> **Prompt**: Implement Step 1 of `_work/shipped/review-failure-modes/plan.md`. Add one bullet to the "Input
> validation and error handling" focus area (section 2) of
> `skills/core/reference/reviewer-discipline/agents/code-reviewer.md`, covering an error rethrown or
> replaced in a way that discards its original origin. State the failure and what it costs a reader
> debugging later; name no language's mechanism — not `throw`, not a specific exception type, not an
> interface. It must read correctly both for a language that throws and one that returns errors. Before
> editing, write down and run the manual check described below and record the RED result. Distinguish it
> from the existing "Swallowed exceptions and empty catch blocks" bullet so one handler cannot produce two
> findings. Finish with `scripts/check-contract.sh` green.

**What to build**:
- `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` — one bullet in section 2. Phrase it
  around *losing where the error came from*, which covers both a rethrow that resets the trace and a
  replacement that drops the original.

**Test first**:
- No automated harness exists for a review, so the signal is a recorded before/after. **Write the expected
  results down before editing.**
- Prepare two small diffs: one in a language that **throws** (a handler rethrowing the caught error by
  name), one in a language that **returns** errors (a handler replacing an error without carrying the
  original). Neither should be C# — the claim justifying core ownership is that this is not C#-shaped.
- Prepare two negative diffs: a handler that wraps an error **while carrying the original**, and a handler
  that logs and continues (already covered by the swallowed-exception bullet).
- Expected before: no lost-origin finding on any of the four. Expected after: a finding on the first two,
  nothing new on the second two.
- Run the review and capture the actual output for the RED half. Per `tdd-principles`, produce the
  artifact, not the claim.

**Validation**:
- [Automated]: `scripts/check-contract.sh` — 14 checks pass. Check 8 must stay green; it will not catch a
  library name, so re-read the bullet for one by eye
- [Manual]: the recorded before/after across all four diffs, output captured
- [Manual]: confirm the log-and-continue diff yields **one** finding, not both a swallowed-exception and a
  lost-origin finding

---

### Step 2 — The interpolated-log check

> **Prompt**: Implement Step 2 of `_work/shipped/review-failure-modes/plan.md`. Add one bullet to the "Input
> validation and error handling" focus area (section 2) of
> `skills/core/reference/reviewer-discipline/agents/code-reviewer.md`, covering a log call that builds its
> message as one interpolated string instead of passing its values as separate fields. Say what is lost —
> the values can no longer be filtered or aggregated afterwards — and name no logging library or
> interface. Before editing, write down and run the manual check below and record the RED result. Make
> sure a log line with no values in it cannot trip the check. Finish with `scripts/check-contract.sh`
> green.

**What to build**:
- `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` — one bullet in section 2, phrased
  around *values folded into the message text* rather than around any library's API shape.

**What not to build**: do not touch the eager-formatting cost angle. That is a performance concern and the
performance reviewer owns cost; adding it here would repeat the mistake this increment exists to correct.

**Test first**:
- Prepare a positive diff in a **non-.NET** project: a log call embedding an order number and a retry count
  in a built-up message string.
- Prepare a negative diff: a log call with a fixed message and no values.
- Expected before: neither draws a finding. Expected after: the first does, naming what can no longer be
  filtered on; the second still draws nothing.
- Record the RED result before editing.

**Validation**:
- [Automated]: `scripts/check-contract.sh` — green
- [Manual]: the recorded before/after on both diffs
- [Manual]: confirm the finding says what is *lost*, not merely that interpolation was used — a finding a
  reader cannot act on is one they learn to skip

---

### Step 3 — Write down who owns cancellation

> **Prompt**: Implement Step 3 of `_work/shipped/review-failure-modes/plan.md`. In
> `skills/core/reference/reviewer-discipline/SKILL.md`, add a short statement near the existing sentence
> that maps each reviewer to its domain, recording that cancellation and timeout concerns on long-running
> work belong to the performance reviewer, and that the quality reviewer defers rather than reporting them
> too. Explain the reason — three reviewers merge into one ranked report, so a rule in two reviewers
> reaches the reader twice. Before editing, induce the RED described below: temporarily add a cancellation
> bullet to `agents/code-reviewer.md`, run all three reviewers over a change with uncancellable
> long-running work, and confirm the merged report shows the finding **twice**. Then revert that temporary
> bullet and add the ownership statement. Finish with `scripts/check-contract.sh` green.

**What to build**:
- `skills/core/reference/reviewer-discipline/SKILL.md` — a short ownership statement adjacent to the
  existing per-reviewer domain sentence in the severity section.

**Test first**:
- **This behavior already holds**, because the quality reviewer never mentioned cancellation. A check that
  has never failed proves only that it runs, so induce the failure rather than assert the current state.
- Temporarily add a cancellation bullet to `agents/code-reviewer.md`. Run all three reviewers over one
  change with a long-running uncancellable call and merge their findings. Expect the finding **twice** —
  that is the RED, and it is what the statement prevents a future author from shipping.
- Revert the temporary bullet. Confirm the merged report shows it once again, attributed to the
  performance reviewer.
- **Do not leave the temporary bullet in.** Verify it is gone with
  `grep -rn "cancel" skills/core/reference/reviewer-discipline/agents/code-reviewer.md` returning nothing.

**Validation**:
- [Automated]: `scripts/check-contract.sh` — green
- [Automated]: the grep above returns no match, proving the induced-RED edit was reverted
- [Manual]: the recorded twice-then-once result from the merged report

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes. Numbering it would invite `/implement-step <plan> N`, which dispatches a code worker to run a
spell — the wrong mechanism, and it blurs the boundary between building and recording.

> **Prompt**: Run `/feature update code-review`. Fold **only** the user- or operator-observable behavior
> changes from this work into the existing capability doc — do not create a new feature doc. Leave
> architecture and migration acceptance criteria in the shipped spec; they are point-in-time and must not
> appear as Rules. Add a revision note dated today describing what changed.
>
> **Validation**: The capability doc describes current behavior with no transition-style ("goes from… to…")
> Rules; no new feature doc was added.

Three specifics for this increment:

- **`_features/code-review.md` does not exist yet.** It gets seeded at **area level** — the review
  capability, not this increment — covering only what this work establishes, with the rest of review
  behavior flagged for `/feature`'s from-code mode to backfill. A thin area doc is visible debt with a
  known remedy; a doc named after this increment would be permanent pollution.
- **The cancellation statement is not a Rule.** Nothing observable changed — it prevents a future
  regression. It belongs in the shipped spec, not as standing behavior in the capability doc. Writing it in
  as a Rule is exactly the transition-style entry the workflow spine warns against.
- **Coverage cites evidence, not test files.** Every scenario here is proven by a recorded manual check.
  Cite the step whose captured output covers it rather than inventing a test path, and leave anything
  unevidenced marked as not covered.

---

## File Summary

| Action | File |
|--------|------|
| Modify | `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` (two bullets in section 2) |
| Modify | `skills/core/reference/reviewer-discipline/SKILL.md` (cancellation ownership) |
| _(work type: `change-to code-review`)_ Update | `_features/code-review.md` — seeded thin at area level by `/feature`, since the area has no doc yet. **No implementation step creates it** |

---

## Sequencing notes

**Steps 1 and 2 are independent** and can run in either order. Both touch the same file and the same
section, so running them in parallel would conflict — run them sequentially even though neither depends on
the other's result.

**Step 3 last.** Its induced RED temporarily edits `agents/code-reviewer.md`, the same file Steps 1 and 2
modify. Doing it after they have landed keeps the temporary edit from being confused with their work, and
makes the revert unambiguous.

**Every step touches L0.** These changes reach every install, including projects with no pack and no
configuration. That is the point — but it also means the blast radius is wider than the diff looks, and the
manual checks are the only evidence anything works.

**This increment unblocks `dotnet-pack`.** That branch carries a blocker note saying its plan was written
against three failure modes rather than two. Once this lands, reconcile it against what this plan actually
produced: the two checks' final wording, and where each lives. Its cancellation content and eval cases are
already correct and should not be reopened — all three reviewers consult stack-pack guidance, so the pack
supplies the idiom and the performance reviewer picks it up.
