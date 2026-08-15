# Canary sync #4 — the completed friction log, and three more fixes

**Date:** 2026-08-04. Source: the canary's `CANTRIP-TRIAL.md` — 22 dated entries spanning the whole
trial, read in full on its branch.

## The finding that matters most: a command that succeeds and does nothing

Their `stack.md → ## Tests` slot recorded a test invocation that **discovered zero tests and exited 0**.
It was scoped into the host project, which is not a test project — so it reported success having run
nothing, and every downstream step would have trusted it.

**Detection cannot catch this.** A command that exits 0 is indistinguishable from a command that works,
and `/setup` was designed to infer commands and record them. So `/setup` now **runs a detected build or
test command and reads its output rather than its status**: a test command must report a non-zero test
count, a build must actually compile the thing in question, and a root invocation is preferred over
changing into a subdirectory, since a narrowed scope is the usual cause of a command that succeeds and
covers nothing. Where verification is impossible, record the command **as unverified** rather than as
confirmed.

This is the one place in setup worth doing more than detecting, because **every downstream spell inherits
these commands** — a silently-empty one propagates into every plan and every review.

It is also the sharpest instance yet of the criterion I used to select starter facts: *does it fail
silently?* Zero tests passing is not passing, and nothing in the pipeline would have said otherwise.

## How it was caught is the story

Their **tailored reviewer found it, as a Blocker, by running the command** rather than reading it. Not by
inspecting the slot — by executing `dotnet test`, grepping the project files, and noticing the count.

That is the clearest payoff yet for the collision guidance's "keep yours." A generic reviewer had no
reason to verify a config value against the repo; theirs did, because its calibrated rules told it to. And
it landed on the config *I* had used as the design input for `/setup` — so the answer key I built the
skill from contained the bug the skill now checks for.

## Two more, both real

**The commit envelope contradicted an explicit step.** `/implement-step`'s envelope says "do not commit,"
but a plan delivering a migration as a sequence of pull requests legitimately commits per step. Now
explicit: the default holds, **an explicit step instruction wins**, and the worker reports that it
committed. What must not happen is the two quietly disagreeing so nobody can tell whether a commit was
expected.

**Removal is not symmetric with addition.** Removing "dead" CSS broke a test asserting that rule's
*presence* — green locally, red in CI, because the local run covered the code touched rather than the
suite referencing what was deleted.

Added in two places, because it is both an implementation and a review concern: the worker now **greps the
test suite for anything it removes** before declaring done, and `reviewer-discipline` gains a
removals-deserve-a-second-look section. Plus the corollary, which is a finding in its own right: **a test
asserting the mere presence of a style rule is fragile by construction**, so the removal may be right and
the test may be the defect. Report both readings rather than assuming the deletion was wrong.

## What the completed log establishes

Twenty-two entries, every phase exercised, and the two positives worth banking:

- **The Phase 0–7 guards fire correctly.** `/spec`'s branch-nesting guard — added in response to sync #1 —
  behaved as designed on a later cast. Fixes are holding, not just landing.
- **`/code-review` discovered the reviewer by identity**, used the tailored one, handled scope, and
  reported coverage honestly, stating which dimensions were not applicable rather than silently dropping
  them.

## Tally across four syncs

**Twelve defects**, and the classification held from the first sync to the last. Every one was either:

- **a mechanism present in one component and absent from its sibling** — pack guidance in spells but not
  agents, branch-scoped diff in `/retrofit` but not `/code-review`, ADR 0005's fix in `workflow` but not
  `/feature`'s Guard, pack slot names in `/setup` instead of read from the pack; or
- **a silent failure returning a confident nothing** — a by-eye check answered "looks good", an
  uncommitted-only diff reviewing a fraction and reporting clean, a classifier falling through on missing
  docs, a test command passing zero tests.

Neither class is visible to a gate that checks whether a file is well-formed. Neither is visible to
reading one file, because both concern relationships — between files, or between an instruction and what
happens when it runs.

**Twelve defects, zero found by me reading my own work.** That is the case for the canary, and the reason
the greenfield pilot matters more than another review pass here.
