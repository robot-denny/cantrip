# Canary friction sync #2 — the chain validated, four more defects

**Date:** 2026-08-04. Source: the demo-site consumer, having run the **complete chain** end to end on a
real increment, including `/update-toolkit` mid-stream to pull sync-#1's fixes.

**Milestone:** every mechanism I could only ever run inline is now proven on a real repo — fresh-context
dispatch, three reviewers in parallel, a real update flow, and `/feature update` against a shipped
implementation.

## What their run confirmed that I could not

- **`/update-toolkit` pulled 15 skills with 0 tailorings reverted.** The reason is the part worth
  banking: *every tailoring lived in an L2 slot*, so there was nothing to reconcile. The
  "tailor in slots, never edit vendored" premise held under a real update rather than in principle.
- **Both sync-#1 fixes verified in place** — the bare slug resolves to the existing spec, and the
  `Feature doc:` line threads spec → plan header → final step. The manual workarounds their first cast
  needed are gone.
- **Fresh-context dispatch works, and the worker stayed in scope.** More than that: facing a missing
  prerequisite it self-authored a fixture following the repo's own resilient pattern and cleaned up,
  rather than hardcoding. That is the behavior the envelope asks for, produced without being told the
  specific pattern.
- **Tailored reviewers beat generic ones, measurably.** Their project reviewer caught that a new test
  duplicated a contract another spec already owned, and cited a config detail. A generic reviewer had no
  way to know either. Strong validation of the collision guidance's "keep yours."
- **`/feature`'s test-is-truth precedence caught a real spec↔implementation conflict** — the draft
  scenario described one visual treatment, the shipped mark was another. Corrected to reality, which is
  exactly what that precedence rule exists for.

## Four new defects, three of them incoherences between my own components

**1. A by-eye validation cannot be self-attested.** A step whose check was "verify by eye" got dispatched
to a worker with no eyes, which answers "looks good" — an unverifiable claim that **reads exactly like a
real result.** Their mitigation was right and is now the rule: for any check it cannot mechanically
verify, the worker **produces an artifact** (screenshot, captured output, actual values) rather than
attesting, creating and cleaning up a fixture if evidence needs one. And `/plan` now authors manual
checkpoints as *artifacts to produce* rather than judgments to make.

This is the silent-failure criterion again, one layer up: the check did not fail, it returned a
confident nothing.

**2. `/code-review` scoped only to uncommitted work.** Their increment was built through
`/implement-step` with a commit per step, so an uncommitted-only diff saw almost none of it — and would
have reported a clean review of a fraction of the change. Now takes a scope, with `branch` computing
committed-plus-uncommitted-plus-untracked against the **upstream** base.

`/retrofit` already had exactly this logic, correct, since 2.5. I did not carry it across. **Second time
this session a mechanism existed in one spell and not its sibling** — the first being the ADR 0003 pack
ask, present in spells and absent from agents.

**3. `/code-review` assumed its reviewers' names.** It named `code-reviewer`; the project had kept its
tailored reviewer under a stack-prefixed name — *because my own install checker told them to.* So the
recommended path led directly to a spell that could not find its reviewer. It now **discovers registered
reviewers and maps them to roles**, prefers a tailored reviewer over the canonical one, and reports which
roles were dispatched versus run inline, because a review missing a dimension looks identical to one that
found nothing there.

**4. The plan's final step was numbered like an implementation step.** It is a spell-cast, so
`/implement-step <plan> 5` would dispatch a code worker to run a spell. Now unnumbered in `/plan`'s
template, and `/implement-step` recognizes a cast step and hands it back rather than dispatching.

## Their open question, answered

Scatter detection could not be exercised on the update path, since update is add-only and does not
re-scatter. **Verified separately on a fresh `--all` install into a project with a pre-existing bare
`skills/` directory:** both redundant locations reported, with the safe cleanup command. Fixtured.

## The pattern that keeps recurring

Every defect in both syncs falls into one of two classes:

- **A mechanism present in one component and absent from its sibling** — pack-guidance in spells but not
  agents; branch-scoped diff in `/retrofit` but not `/code-review`; the ADR 0005 fix in the `workflow`
  skill but not `/feature`'s local Guard.
- **A silent failure that returns a confident nothing** — a by-eye check answered "looks good"; an
  uncommitted-only diff reviewing a fraction and reporting clean; a classifier falling through on missing
  docs.

Both classes are invisible to the gate, because the gate checks whether a *file* is well-formed. Neither
is visible to a careful read of a single file, because both are about the relationship between files or
between an instruction and its runtime. **Only a real cast finds them**, which is the strongest argument
yet for the canary existing at all.
